import os
import subprocess
import shutil

# Constants
SOURCE_FILE_C = "source_code/hello.c"
SOURCE_FILE_JAVA = "source_code/Hello.java"
GCC_CMD = "gcc"

# Setup PATH for MSYS2 and Java
os.environ["PATH"] += r";C:\msys64\mingw64\bin"
os.environ["PATH"] += r";C:\Program Files\Microsoft\jdk-17.0.17.10-hotspot\bin"

if os.path.exists(r"C:\msys64\mingw64\bin\gcc.exe"):
    GCC_CMD = r"C:\msys64\mingw64\bin\gcc.exe"

class CompilerBackend:
    def __init__(self):
        self.has_gcc = self.check_gcc()
        self.has_java = self.check_java()

    def check_gcc(self):
        try:
            subprocess.check_call([GCC_CMD, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False

    def check_java(self):
        try:
            subprocess.check_call(["javac", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False

    def clean_artifacts(self):
        # Clean paths in source_code/ directory
        base = "source_code"
        if not os.path.exists(base): return
        
        for f in ["hello.i", "hello.s", "hello.o", "hello.exe", "Hello.class", "HelloWorld.class", "Add.class"]:
             path = os.path.join(base, f)
             if os.path.exists(path): 
                 try: os.remove(path)
                 except: pass

    def extract_strings(self, filename):
        if not os.path.exists(filename): return "File not found."
        import re
        try:
            with open(filename, "rb") as f:
                data = f.read()
            # Find ASCII strings > 4 chars
            # Regex: 4 or more printable chars (from space to tilde)
            strings = re.findall(b"[ -~]{4,}", data)
            return "\n".join([s.decode("utf-8", errors="ignore") for s in strings])
        except Exception as e:
            return f"Error extracting strings: {e}"

    def run_cmd(self, cmd, mock_preview=None, binary=False, filename=None):
        tool = cmd.split()[0].lower()
        
        # Determine native vs mock
        use_real = False
        if "gcc" in tool: use_real = self.has_gcc
        elif "hello.exe" in tool: use_real = self.has_gcc
        elif "java" in tool: use_real = self.has_java
        elif "objdump" in tool: use_real = self.has_gcc # objdump comes with gcc usually
        
        # Intercept strings command regardless of OS support (fallback to python)
        if tool == "strings":
            # Extract filename from cmd "strings <filename>"
            parts = cmd.split()
            if len(parts) > 1:
                target_file = parts[-1]
                return True, self.extract_strings(target_file)
            else:
                return False, "Usage: strings <file>"
        
        # Execute Real
        if use_real:
            try:
                # Capture Output
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                return True, output.decode() if not binary else "Binary Output"
            except subprocess.CalledProcessError as e:
                # Failure
                err_msg = e.output.decode() if e.output else "Command Failed"
                return False, err_msg
        
        # Execute Mock
        else:
            if filename and mock_preview:
                mode = 'wb' if binary else 'w'
                with open(filename, mode) as f:
                    content = mock_preview.encode() if binary and isinstance(mock_preview, str) else mock_preview
                    f.write(content)
            return True, "[MOCKED] Command success! (Simulation)"
