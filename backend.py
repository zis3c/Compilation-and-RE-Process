import os
import subprocess
import shutil

# Constants
# Constants
SOURCE_FILE_C = "source_code/hello.c"
SOURCE_FILE_JAVA = "source_code/Hello.java"
GCC_CMD = "gcc"

class CompilerBackend:
    def __init__(self):
        # Check specific common paths FIRST to help user, then fallback to PATH
        self._add_common_paths()
        
        self.gcc_path = shutil.which("gcc")
        self.java_path = shutil.which("javac")
        self.java_runtime = shutil.which("java")
        
        self.has_gcc = self.gcc_path is not None
        self.has_java = self.java_path is not None

    def _add_common_paths(self):
        # Add common installation paths to env just in case
        paths = [
            r"C:\msys64\mingw64\bin",
            r"C:\Program Files\Java\jdk-17\bin" 
        ]
        # Dynamically find likely JDKs? For now just keep the user's specific one as a fallback hint
        known_jdk = r"C:\Program Files\Microsoft\jdk-17.0.17.10-hotspot\bin"
        if os.path.exists(known_jdk): paths.append(known_jdk)
        
        current_path = os.environ["PATH"]
        for p in paths:
             if os.path.exists(p) and p not in current_path:
                 os.environ["PATH"] += ";" + p

    def check_gcc(self):
        return self.has_gcc

    def check_java(self):
        return self.has_java

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
            strings = re.findall(b"[ -~]{4,}", data)
            return "\n".join([s.decode("utf-8", errors="ignore") for s in strings])
        except Exception as e:
            return f"Error extracting strings: {e}"

    def run_cmd(self, cmd, mock_preview=None, binary=False, filename=None):
        tool = cmd.split()[0].lower()
        
        # STRICT MODE: Check availability before running
        if "gcc" in tool or "objdump" in tool:
            if not self.has_gcc:
                return False, "ERROR: GCC (MinGW) is not installed or not found in PATH.\nPlease install MinGW to run this step."
        
        if "javac" in tool or "java " in tool: # space to avoid matching javac in java
             if not self.has_java:
                return False, "ERROR: Java Development Kit (JDK) is not installed or not found in PATH.\nPlease install JDK to run this step."
        
        # Intercept strings command 
        if tool == "strings":
            parts = cmd.split()
            if len(parts) > 1:
                target_file = parts[-1]
                return True, self.extract_strings(target_file)
            else:
                return False, "Usage: strings <file>"
        
        # Always try to execute REAL command now
        try:
            # For Windows GUI apps, we need to hide the console window when spawning subprocesses
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, startupinfo=startupinfo)
            return True, output.decode() if not binary else "Binary Output Generated"
        except subprocess.CalledProcessError as e:
            err_msg = e.output.decode() if e.output else "Command Failed"
            return False, f"Command Execution Failed:\n{err_msg}"
        except Exception as e:
            return False, f"System Error: {e}"
