# Provide the path to a .sv top module file, the port declaration of the file is analyzed
# The structure of the file is:
# - interface
# -- packet, type, direction
# --- field -> type name
# The autogen struct is analyzed and the wrapper is generated and the interfaces connected\

# svfmt_pkg/wrapperizer.py
from .svfmt_module import wrapperizer

def main():
    wrapperizer()

if __name__ == "__main__":
    main()
 