# src/your_package_name/cli.py

import sys

def main():
    if len(sys.argv) > 1:
        name = sys.argv[1]
        print(f"Hello, {name}!")
    else:
        print("Hello, world!")

if __name__ == "__main__":
    main()