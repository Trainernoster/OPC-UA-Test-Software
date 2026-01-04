import subprocess
import os

from pathlib import Path

def main():
    testServer = os.path.join(Path(__file__).parent.parent, "CPP", "build", "TestServer")

    # Arguments to pass
    args = ["Test_arg1", "Test_arg2", "Test_arg3"]

    # Call the executable
    result = subprocess.run([testServer] + args, capture_output=True, text=True)

    # Print output
    print("STDOUT:")
    print(result.stdout)

    print("STDERR:")
    print(result.stderr)

    print("RETURN CODE (int):")
    print(result.returncode)

if __name__ == "__main__":
    main()
