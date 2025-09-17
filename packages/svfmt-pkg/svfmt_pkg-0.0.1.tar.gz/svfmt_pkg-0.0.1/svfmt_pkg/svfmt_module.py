import re
import argparse
import os
INDENT_ONE = "    "

def get_if_else_statement_fmt(length: int, always_comb: bool = True, implicit_final_condition: bool = True, case_format: bool = False, unique: bool = False) -> str:
    """
    Generates a formatted string for an if-else or case statement in SystemVerilog.
    Args:
        length (int): The number of conditions to generate.
        always_comb (bool, optional): If True, wraps the statement in an always_comb block. Defaults to True.
        implicit_final_condition (bool, optional): If True, the final else condition is implicit. Defaults to True.
        case_format (bool, optional): If True, generates a case statement instead of if-else. Defaults to False.
    Returns:
        str: A formatted string representing the if-else or case statement.
    """
    
    if always_comb:
        out_fmt = "{indent}always_comb begin\n"
    else:
        out_fmt = ""
        
    if case_format is True:
        
        if unique:
            out_fmt += "{indent}unique case ({val})\n"
        else:
            out_fmt += "{indent}case ({val})\n"
        for i in range(length+1):
            out_fmt += f"{{indent}}\t{{condition{i}}} : {{assign{i}}}"
            
        out_fmt += "{indent}endcase\n"
    else:
        for i in range(length):
            if i == 0:
                out_fmt += f"{{indent}}\tif ({{condition{i}}}) begin\n"
            elif i == length-1 and implicit_final_condition is True:
                out_fmt += "{indent}\tend else begin\n"
            else:
                out_fmt += f"{{indent}}\tend else if ({{condition{i}}}) begin\n"
                
            # out_fmt += f"{{indent}}\t\t{{lhs}} = {{rhs{i}}};\n"
            out_fmt += f"{{assign{i}}}"

        out_fmt += "{indent}\tend\n"
    
    if always_comb:
        out_fmt += "{indent}end\n"
    
    return out_fmt

wrp_fmt = """

module {module_name}_wrp (
{port_def}   
);

{module_name} i_{module_name} (
{portmap_def}  
);

always_comb begin
{assign_def}
end

endmodule
"""

def port_parser(file_path):
    ports = []
    with open(file_path, "r") as f:
        lines = f.readlines()

    in_module = False
    module_name = None
    for line in lines:
        line = line.strip()
        if not in_module:
            if line.startswith("module "):
                in_module = True
                # Extract module name
                m = re.match(r'module\s+(\w+)', line)
                if m:
                    module_name = m.group(1)
            continue
        if line.startswith(");"):
            break
        if line == "" or line.startswith("//"):
            continue
        # Remove trailing commas and comments
        line = line.split("//")[0].strip().rstrip(",")
        if not line:
            continue
        parts = line.split()
        # Handle interface: <if_type>.<direction> <name>
        # Match interface: <if_type>.<direction> <name>
        m_interface = re.match(r'(\w+)\.(\w+)\s+(\w+)', line)
        if m_interface:
            if_type, direction, name = m_interface.groups()
            ports.append({
                "kind": "interface",
                "if_type": if_type,
                "direction": direction,
                "name": name
            })
            continue

        # Match port: <verse> <type> <name>
        # Handles types with spaces and brackets, e.g., 'var logic', 'var smb_msel_dtype[NUM_STACK_PER_CXR-1:0][NUM_SUBSTACK_PER_STACK-1:0]'
        m_port = re.match(r'(\w+)\s+([\w\[\]\-\:\s]+)\s+(\w+)', line)
        if m_port:
            verse, port_type, name = m_port.groups()
            ports.append({
            "kind": "port",
            "verse": verse,
            "type": port_type.strip(),
            "name": name
            })
    return ports, module_name

def text_gen(port_list, py_struct_file_path):
    """
    Generate text representation of the port list.
    """
    import importlib.util

    error_msg = []
    port_def = []
    assign_def = []
    portmap_def = []

    # Dynamically load the py_struct_file as a module
    spec = importlib.util.spec_from_file_location("py_struct_module", py_struct_file_path)
    py_struct_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(py_struct_module)

    struct_definitions = getattr(py_struct_module, "struct_definitions", [])

    for port in port_list:
        port_name = port.get("name")
        
        direction = port.get("direction")
        
        if direction == "slv":
            dir = "input"
        elif direction == "mst":
            dir = "output"
            
        portmap_def.append(f"{INDENT_ONE}.{port_name}({port_name})")
        
        struct = next((s for s in struct_definitions if s.get("struct_name") == f"{port_name}_pkt_dtype"), None)
        if not struct:
            error_msg.append(f"\033[91m{port_name}: <no struct found>\033[0m")
            continue
        
        for field in struct.get("field_defs", []):
            field_name = field.get("name")
            field_type = field.get("dtype")
            
            if field_type == "logic":
                dtype = "logic"
            else:
                dtype = f"logic[$bits({field_type})-1:0]"
            
            port_def.append(f"{INDENT_ONE}{dir} var {dtype} {port_name}_{field_name}")
            if dir == "input":
                lhs = f"{port_name}.packet.{field_name}"
                rhs = f"{port_name}_{field_name}"
            else:
                lhs = f"{port_name}_{field_name}"
                rhs = f"{port_name}.packet.{field_name}"
                
            assign_def.append(f"{INDENT_ONE}{lhs} = {rhs}")
            
    return ",\n".join(port_def), ";\n".join(assign_def), ",\n".join(portmap_def), error_msg

def module_instance_gen(module_name, port_list):
    """
    Generate module instance text.
    """
    instance_lines = [f"{module_name} {module_name}_inst ("]
    for port in port_list:
        port_name = port.get("name")
        if port.get("direction") == "slv":
            direction = "input"
        elif port.get("direction") == "mst":
            direction = "output"
        else:
            direction = "inout"
        
        instance_lines.append(f"    .{port_name}({port_name}),  // {direction}")
    
    instance_lines.append(");")
    return "\n".join(instance_lines)

# Provide the path to a .sv top module file, the port declaration of the file is analyzed
# The structure of the file is:
# - interface
# -- packet, type, direction
# --- field -> type name
# The autogen struct is analyzed and the wrapper is generated and the interfaces connected\

def wrapperizer():

    parser = argparse.ArgumentParser(description="Analyze .sv top module file and generate wrapper.")
    parser.add_argument("-top", dest="top_module_path", required=True, help="Path to the top module .sv file")
    parser.add_argument("-struct", dest="struct_path", required=True, help="Path to the Python struct definition file")
    args = parser.parse_args()

    if not os.path.exists(args.top_module_path):
        print(f"Error: The file {args.top_module_path} does not exist.")
        exit(1)
        
    port_list, module_name = port_parser(args.top_module_path)
    
    print(f"Analyzed Ports of module {module_name}:")
    for port in port_list:
        print(port)
        
    # struct_path = os.path.join(
    #     os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    #     "autogen", "definitions_files", "cxr_autogen", "structs.py"
    # )
    port_def, assign_def, portmap_def, error_msg = text_gen(port_list, args.struct_path)
    
    print("\nErrors:")
    for msg in error_msg:
        print(msg)
    
    # print("\nGenerated Port Definition:")
    # print(port_def)
    # print("\nGenerated Assign:")
    # print(assign_def)
    # print("\nPortmap Def:")
    # print(portmap_def)
    
    formatted_wrp = wrp_fmt.format(
        module_name=module_name,
        port_def=port_def,
        portmap_def=portmap_def,
        assign_def=assign_def
    )
    
    print("\nFormatted Wrapper Code:")
    print(formatted_wrp)

    # Here you would implement the logic to parse the .sv file and generate the wrapper code.
    # This is a placeholder for the actual implementation.
    print(f"Generating wrapper for {args.top_module_path}...")