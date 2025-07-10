from functions.run_python import run_python_file

def run_tests():
    print("=== main.py ===")
    print(run_python_file("calculator", "main.py"))
    
    print("\n=== tests.py ===")
    print(run_python_file("calculator", "tests.py"))

    print("\n=== ../main.py (should error) ===")
    print(run_python_file("calculator", "../main.py"))

    print("\n=== nonexistent.py (should error) ===")
    print(run_python_file("calculator", "nonexistent.py"))


if __name__ == "__main__":
    run_tests()
    