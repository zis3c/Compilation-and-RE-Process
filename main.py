import customtkinter as ctk
import os
import re
from backend import CompilerBackend, SOURCE_FILE_C, SOURCE_FILE_JAVA, GCC_CMD
from ui_components import Sidebar, Console, EditorArea
from pygments.lexers import CLexer, GasLexer
import threading
import shutil

class CompilationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Compilation Process Simulator (Refactored)")
        self.geometry("1400x900")
        
        # Ensure workspace exists
        self.workspace_dir = "source_code"
        if not os.path.exists(self.workspace_dir):
            os.makedirs(self.workspace_dir)
        
        # Backend
        self.backend = CompilerBackend()
        
        # State
        self.language = "C"
        self.step_index = 0
        self.steps = [] 
        self.current_java_file = os.path.join(self.workspace_dir, "Hello.java")
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar (Left)
        self.sidebar = Sidebar(self, 
            step_callback=self.next_step, 
            save_callback=self.save_source,
            break_callback=self.break_code,
            reset_callback=self.reset_sim,
            lang_callback=self.change_language
        )
        self.sidebar.btn_restore.configure(command=self.restore_defaults)
        
        # Main Area (Right) - Vertical PanedWindow for Resizable Console
        import tkinter as tk
        
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.main_paned = tk.PanedWindow(self.right_frame, orient=tk.VERTICAL, sashwidth=8, bg="#333333", sashrelief="flat")
        self.main_paned.grid(row=0, column=0, sticky="nsew")
        
        # Top: Editor
        self.editor = EditorArea(self.main_paned) 
        self.main_paned.add(self.editor, minsize=400, stretch="always")
        
        # Bottom: Console
        self.console = Console(self.main_paned)
        self.main_paned.add(self.console, minsize=100, stretch="never")

        # Zoom State
        self.current_scale = 1.0
        self._zoom_job = None
        
        # Bindings
        self.bind("<Control-plus>", self.zoom_in)
        self.bind("<Control-equal>", self.zoom_in)
        self.bind("<Control-minus>", self.zoom_out)

        # Initial Render
        self._define_steps()
        self.reset_sim()

    def zoom_in(self, event=None):
        if self.current_scale < 2.0:
            self.current_scale += 0.1
            self._schedule_zoom()

    def zoom_out(self, event=None):
        if self.current_scale > 0.5:
            self.current_scale -= 0.1
            self._schedule_zoom()

    def _schedule_zoom(self):
        if self._zoom_job:
            self.after_cancel(self._zoom_job)
        self._zoom_job = self.after(100, self._apply_zoom)

    def _apply_zoom(self):
        try:
            ctk.set_window_scaling(self.current_scale)
            self.console.log(f"Zoom Applied: {int(self.current_scale * 100)}%")
        except Exception as e:
            self.console.log(f"Zoom Error: {e}", error=True)
        self._zoom_job = None

    def _define_steps(self):
        if self.language == "C":
            self.steps = [
                "Source Code", "Preprocessing", "Compilation", "Assembling", "Linking", "Execution",
                "RE: Recon (Strings)", "RE: Dynamic Analysis", "RE: Static (Disasm)", "RE: Static (Decomp)",
                "RE: Solve (Patching)"
            ]
        else:
            self.steps = [
                "Source Code", "Compilation", "Execution",
                "RE: Recon (Strings)", "RE: Dynamic Analysis", "RE: Static (Disasm)", "RE: Static (Decomp)",
                "RE: Solve (Patching)"
            ]

    # --- Step Control ---
    def change_language(self, choice):
        self.language = choice
        self.console.log(f"Switched to {self.language}")
        self._define_steps() # Recalculate steps
        self.current_java_file = os.path.join(self.workspace_dir, "Hello.java")
        self.reset_sim()

    def restore_defaults(self):
        # Determine correct filename based on context or default
        if self.language == "C":
            fname = SOURCE_FILE_C
            code = '#include <stdio.h>\n\nint main() {\n    printf("Hello from C!\\n");\n    return 0;\n}'
        else:
            # For Java, try to preserve class name if valid, else default
            current_content = self.editor.txt_left.get("0.0", "end-1c")
            current_name = self._get_java_filename(current_content)
            
            # If current content is garbage, fallback to Hello
            if not current_name or current_name == "Hello.java": 
                 fname = os.path.join(self.workspace_dir, "Hello.java")
                 class_name = "Hello"
            else:
                 fname = current_name
                 # Ensure full path
                 if not os.path.dirname(fname): fname = os.path.join(self.workspace_dir, fname)
                 class_name = os.path.splitext(os.path.basename(fname))[0]

            code = f'public class {class_name} {{\n    public static void main(String[] args) {{\n        System.out.println("Hello from Java!");\n    }}\n}}'
            
            # Update tracking
            self.current_java_file = fname

        with open(fname, "w") as f: f.write(code)
        self.console.log(f"Restored code to {fname}")
        self.reset_sim(preload_content=code)

    def refresh_ui(self):
        # Sidebar Sync Update
        self.sidebar.refresh(self.language, self.steps)
        self.sidebar.highlight(self.step_index)
        
        # Async Content Update
        self.sidebar.set_next_text("Processing...")
        self.sidebar.btn_next.configure(state="disabled")
        
        # Trigger Step 0
        threading.Thread(target=self._run_step_thread, daemon=True).start()

    def next_step(self):
        # Auto-save current content if it's the source step
        if self.step_index == 0:
            self.save_source(reset=False)

        self.step_index += 1
        if self.step_index >= len(self.steps):
            self.step_index = len(self.steps) - 1
            self.sidebar.set_next_text("DONE")
            return
            
        self.sidebar.highlight(self.step_index)
        self.sidebar.set_next_text("Processing...")
        self.sidebar.enable_controls(False) # Disable all during processing
        self.sidebar.btn_next.configure(state="disabled")
        
        # Run logic in thread
        threading.Thread(target=self._run_step_thread, daemon=True).start()

    def _run_step_thread(self):
        # This runs in background
        idx = self.step_index
        lang = self.language
        
        try:
            if lang == "C":
                result = self.prepare_c_step(idx)
            else:
                result = self.prepare_java_step(idx)
            
            # Schedule UI update
            self.after(0, self._apply_step_result, result)
        except Exception as e:
            self.after(0, self.console.log, f"Thread Error: {e}", True)

    def _apply_step_result(self, result):
        # Back on Main Thread
        self.sidebar.set_next_text("NEXT STEP >")
        self.sidebar.btn_next.configure(state="normal")
        
        # Header
        self.editor.set_header(f"Step {self.step_index}: {self.steps[self.step_index]}")
        
        # Logs
        if "log" in result: self.console.log(result["log"])
        if "error" in result: self.console.log(result["error"], error=True)
            
        # Explanation
        if "explanation" in result: self.editor.set_explanation(result["explanation"])
            
        # Error Rewind Logic
        if "success" in result and not result["success"]:
            self.editor.set_explanation("ERROR: The step failed. Check console.")
            self.step_index -= 1 
            self.sidebar.highlight(self.step_index)
            # Re-enable controls if we rewound to 0? Logic complex here.
            # Simpler: Just exit. User needs to fix via Reset or Back?
            # Existing logic was just rewind.
            return

        # Content Updates
        if "content" in result:
            c = result["content"]
            self.editor.set_content(
                c["left_text"], c["right_text"], 
                c.get("left_title", "Input"), c.get("right_title", "Output"),
                c.get("left_lexer"), c.get("right_lexer"),
                c.get("left_editable", False)
            )

        # Controls
        is_step_0 = (self.step_index == 0)
        self.sidebar.enable_controls(is_step_0)

    # --- Logic Generators (Background Safe) ---
    # These return dicts: { "success": bool, "log": str, "explanation": str, "content": {...} }

    def _log_file_saved(self, fname):
        if os.path.exists(fname):
            size = os.path.getsize(fname)
            return f"[SUCCESS] Generated {fname} ({size} bytes)"
        return ""

    def prepare_c_step(self, idx):
        bk = self.backend
        res = {"success": True, "log": ""}
        
        # Define paths within workspace
        f_src = SOURCE_FILE_C # Already source_code/hello.c
        f_pre = os.path.join(self.workspace_dir, "hello.i")
        f_asm = os.path.join(self.workspace_dir, "hello.s")
        f_obj = os.path.join(self.workspace_dir, "hello.o")
        f_exe = os.path.join(self.workspace_dir, "hello.exe")
        
        if idx == 0: # Source
            # Ensure code exists and is not empty
            default_c = '#include <stdio.h>\n\nint main() {\n    printf("Hello from C!\\n");\n    return 0;\n}'
            if not os.path.exists(f_src) or os.path.getsize(f_src) == 0:
                with open(f_src, "w") as f: f.write(default_c)
                res["log"] = f"Created default {f_src}\n"
            
            content = self.read_file(f_src)
            res["explanation"] = "Source Code: Human-Readable C.\n\nThis is where it starts. Programming languages like C are designed for humans to read and write. The computer cannot run this directly; it needs to be translated into machine code."
            res["log"] += f"Loaded {f_src}\nReady for Preprocessing."
            res["content"] = {
                "left_text": content, "right_text": "", 
                "left_title": "Source Code (Editable)", "right_title": "Output",
                "left_lexer": CLexer(), "left_editable": True
            }
            
        elif idx == 1: # Preprocessing
            res["explanation"] = "Preprocessing: Expansion & Cleanup.\n\nBefore compilation, the Preprocessor handles directives like '#include'.\n\nWhy?\nIt basically 'copy-pastes' the contents of header files (like stdio.h) into your file. This is why the output (right) is so huge compared to your source code."
            cmd = f"{GCC_CMD} -E {f_src} -o {f_pre}"
            res["log"] += f"Running: {cmd}\n"
            bk.run_cmd(cmd, "# Mock Pre", filename=f_pre)
            res["log"] += self._log_file_saved(f_pre)
            
            res["content"] = {
                "left_text": self.read_file(f_src), "right_text": self.read_file(f_pre),
                "left_title": "Source", "right_title": "Preprocessed (Expanded)",
                "left_lexer": CLexer(), "right_lexer": CLexer()
            }
            
        elif idx == 2: # Compilation
            res["explanation"] = "Compilation: C to Assembly.\n\nThe Compiler translates the messy preprocessed C code into Assembly Language.\n\nWhat is Assembly?\nIt's a low-level, human-readable representation of CPU instructions. It's specific to the processor architecture (like x86-64)."
            cmd = f"{GCC_CMD} -S {f_pre} -o {f_asm}"
            res["log"] += f"Running: {cmd}\n"
            success, out = bk.run_cmd(cmd, "Mock Asm", filename=f_asm)
            
            res["success"] = success
            if not success: res["error"] = out
            else: 
                res["log"] += self._log_file_saved(f_asm)
                res["content"] = {
                    "left_text": self.read_file(f_pre), "right_text": self.read_file(f_asm),
                    "left_title": "Preprocessed", "right_title": "Assembly (Instructions)",
                    "left_lexer": CLexer(), "right_lexer": GasLexer()
                }

        elif idx == 3: # Assembling
            res["explanation"] = "Assembling: Assembly to Machine Code.\n\nThe Assembler converts the text instructions (like 'mov', 'call') into raw binary opcodes (Machine Code).\n\nResult?\nAn 'Object File' (.o). It contains machine code, but it's incomplete. It has 'holes' where external functions like 'printf' should be."
            cmd = f"{GCC_CMD} -c {f_asm} -o {f_obj}"
            res["log"] += f"Running: {cmd}\n"
            success, out = bk.run_cmd(cmd, "Mock Bin", binary=True, filename=f_obj)
            
            res["success"] = success
            if not success: res["error"] = out
            else:
                res["log"] += self._log_file_saved(f_obj)
                res["content"] = {
                    "left_text": self.read_file(f_asm), "right_text": self.read_file(f_obj),
                    "left_title": "Assembly", "right_title": "Object File (Machine Code)",
                    "left_lexer": GasLexer()
                }

        elif idx == 4: # Linking
            res["explanation"] = "Linking: Creating the Executable.\n\nThe Linker combines your Object File with System Libraries to create the final .exe.\n\nWhy does it get bigger?\nThe Linker adds:\n1. C Runtime (Startup code to initialize the app).\n2. Import Tables (telling Windows where to find 'printf').\n3. PE Headers (Metadata for the OS)."
            cmd = f"{GCC_CMD} {f_obj} -o {f_exe}"
            res["log"] += f"Running: {cmd}\n"
            success, out = bk.run_cmd(cmd, "Mock Exe", binary=True, filename=f_exe)
            
            res["success"] = success
            if not success: res["error"] = out
            else:
                res["log"] += self._log_file_saved(f_exe)
                res["content"] = {
                    "left_text": self.read_file(f_obj), "right_text": self.read_file(f_exe),
                    "left_title": "Object File", "right_title": "Executable (Complete)"
                }

        elif idx == 5: # Execution - NEW
            res["explanation"] = "Execution (User Mode).\n\nThis is how a normal user interacts with the program. They run it, provide input, and expect an output.\n\nKey Difference:\nThe user cares about the *Result* (Did it work?), not *How* it worked."
            res["log"] += f"Running: {f_exe}\n"
            success, out = bk.run_cmd(f_exe)
            res["log"] += f"Process Finished. Output:\n{out}"
            res["content"] = {
                "left_text": self.read_file(f_exe), "right_text": f"OUTPUT:\n{out}",
                "left_title": "Executable", "right_title": "Run Result"
            }

        elif idx == 6: # RE: Recon (Strings) - OLD idx 5
            res["explanation"] = "RE: Reconnaissance (Strings).\n\nBefore running unknown code, we check it statically. The 'strings' command scans the binary for readable ASCII text.\n\nGoal: identifying passwords, error messages, or hardcoded API keys."
            res["log"] += f"Running: strings {f_exe}"
            success, out = bk.run_cmd(f"strings {f_exe}")
            res["content"] = {
                "left_text": self.read_file(f_exe), "right_text": out,
                "left_title": "Executable", "right_title": "Strings Output"
            }

        elif idx == 7: # RE: Dynamic (Execution) - OLD idx 6
            res["explanation"] = "RE: Dynamic Analysis (Hacker Mode).\n\nWe run the program again, but this time we are *investigating*. We act like a detective.\n\nWe test edge cases:\n- What happens if I enter a looong password? (Buffer Overflow?)\n- What if I enter symbols?\n- We monitor memory and CPU registers (using a Debugger)."
            res["log"] += f"Running: {f_exe}\n"
            success, out = bk.run_cmd(f_exe)
            res["log"] += f"Process Finished. Output:\n{out}"
            res["content"] = {
                "left_text": self.read_file(f_exe), "right_text": f"OUTPUT:\n{out}",
                "left_title": "Executable", "right_title": "Dynamic Analysis (Debugger Attached)"
            }

        elif idx == 8: # RE: Static (Disasm) - OLD idx 7
            res["explanation"] = "RE: Static Analysis (Disassembly).\n\nWe convert raw machine code back into Assembly to understand the logic flow.\n\nAssembly (ASM): The bridge between Code and Hardware. We can see exactly which registers are used and where jumps happen."
            cmd = f"{GCC_CMD.replace('gcc','objdump')} -d {f_exe}"
            res["log"] += f"Running: {cmd}"
            success, out = bk.run_cmd(cmd)
            res["content"] = {
                "left_text": self.read_file(f_exe), "right_text": out,
                "left_title": "Executable", "right_title": "Disassembly",
                "right_lexer": GasLexer()
            }

        elif idx == 9: # RE: Static (Decomp) - OLD idx 8
            res["explanation"] = "RE: Static Analysis (Decompilation).\n\nTools like Ghidra reconstruct high-level C code from ASM.\n\nNote: Variable names are lost (iVar1), and comments are gone. Complexity remains, but it's readable."
            res["log"] += "Simulating Decompiler (Ghidra-style)..."
            
            # Dynamic Decomp
            source_content = self.read_file(SOURCE_FILE_C)
            decomp_code = self._simulate_decompilation(source_content, "C")
            
            exe_file = os.path.join(self.workspace_dir, "hello.exe")
            res["content"] = {
                "left_text": self.read_file(exe_file),
                "right_text": decomp_code,
                "left_title": f"Binary ({os.path.basename(exe_file)})", "right_title": "Decompiled C (Mock)",
                "right_lexer": CLexer()
            }

        elif idx == 10: # RE: Solve (Patching) - OLD idx 9
            res["explanation"] = "RE: The Solve (Patching).\n\nWe don't just watch; we change! We can edit the binary's bytes directly to alter its behavior.\n\nSimulation:\nWe will patch the binary to replace 'Hello' with 'HACKD'. No recompilation needed!"
            
            # Create a patched copy
            f_patched = os.path.join(self.workspace_dir, "hello_patched.exe")
            
            # Simulate Patch logic
            try:
                if os.path.exists(f_exe):
                    with open(f_exe, 'rb') as f: data = f.read()
                    
                    # Pattern match "Hello" -> "HACKD"
                    # Only works if lengths match to avoid corrupting offsets
                    patch_from = b"Hello"
                    patch_to   = b"HACKD"
                    
                    if patch_from in data:
                        new_data = data.replace(patch_from, patch_to, 1) # Replace first occurrence
                        with open(f_patched, 'wb') as f: f.write(new_data)
                        res["log"] += f"Patched 'Hello' -> 'HACKD' in binary.\nSaved to {f_patched}\n"
                    else:
                        res["log"] += "String 'Hello' not found for patching. Using original.\n"
                        shutil.copy(f_exe, f_patched)
                else:
                    res["error"] = "Binary not found to patch."
                    return res
            except Exception as e:
                res["log"] += f"Patching failed: {e}\n"
                shutil.copy(f_exe, f_patched)

            # Run patched
            res["log"] += f"Running: {f_patched}\n"
            success, out = bk.run_cmd(f_patched)
            res["log"] += f"Pwning complete. Output:\n{out}"
            
            res["content"] = {
                "left_text": f"[HEX VIEW]\nOriginal: ... 48 65 6c 6c 6f ... (Hello)\nPatched : ... 48 41 43 4b 44 ... (HACKD)", 
                "right_text": f"OUTPUT:\n{out}",
                "left_title": "Hex Editor Patch", "right_title": "Run Patched Binary"
            }

        return res

    def _get_java_filename(self, content=None):
        default_name = "Hello.java"
        if content is None:
             if hasattr(self, 'editor'): content = self.editor.txt_left.get("0.0", "end-1c")
             else: return default_name

        match = re.search(r'public\s+class\s+(\w+)', content)
        if match: return f"{match.group(1)}.java"
        return default_name

    def _simulate_decompilation(self, source_code, lang="C"):
        # 1. Strip Single Line Comments
        code = re.sub(r'//.*', '', source_code)
        # 2. Strip Multi-line Comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # 3. Clean up empty lines
        lines = []
        for line in code.split('\n'):
            line = line.rstrip() # Remove trailing spaces
            if line.strip(): # Keep non-empty lines
                lines.append(line)
        
        clean_code = "\n".join(lines)
        
        # 4. Add "Decompiler" Header
        header = f"// Decompiled by CompSim (Mock)\n// SOURCE: Recovered from Binary\n// NOTE: Original comments are lost.\n\n"
        
        if lang == "C":
            # Mock variable renaming for simple int declarations (Visual flair)
            # This is a very simple regex to find 'int x =' patterns and replace them
            # We won't do it aggressively to avoid breaking logic display
            pass

        return header + clean_code
        
    def save_source(self, reset=True):
        fname = SOURCE_FILE_C if self.language == "C" else self._get_java_filename()
        
        # Ensure regex result (just filename) is joined with workspace path
        if not os.path.dirname(fname):
            fname = os.path.join(self.workspace_dir, fname)

        if self.language == "Java":
            self.current_java_file = fname
            
        code = self.editor.txt_left.get("0.0", "end-1c")
        
        try:
            with open(fname, "w") as f:
                f.write(code)
                f.flush()
                os.fsync(f.fileno())
            self.console.log(f"Saved {fname}.")
            if reset:
                self.reset_sim(preload_content=code)
        except Exception as e:
            self.console.log(f"Save failed: {e}", error=True)

    def prepare_java_step(self, idx):
        bk = self.backend
        res = {"success": True, "log": ""}
        
        # Use tracked file
        java_file = self.current_java_file
        
        # Ensure tracking is robust
        if not java_file: 
             java_file = os.path.join(self.workspace_dir, "Hello.java")
             self.current_java_file = java_file

        if idx == 0:
            default_code = 'public class Hello {\n    public static void main(String[] args) {\n        System.out.println("Hello from Java!");\n    }\n}'
            
            # Use tracked file if exists, else create default in workspace
            if not os.path.exists(java_file):
                 with open(java_file, "w") as f: f.write(default_code)
            
            content = self.read_file(java_file)
            
            res["explanation"] = "Java Source Code."
            res["log"] += f"Loaded {java_file}"
            res["content"] = {
                "left_text": content, "right_text": "",
                "left_title": f"Source ({os.path.basename(java_file)})", "right_title": "Output",
                "left_lexer": CLexer(), "left_editable": True
            }
            return res

        # For Compilation+, strict use of tracked file
        if not os.path.exists(java_file):
            res["success"] = False
            res["error"] = f"File {java_file} not found. Did you save?"
            return res

        base_name_full = os.path.splitext(java_file)[0] # source_code/Hello
        base_name = os.path.basename(base_name_full) # Hello
        class_file = f"{base_name_full}.class" # source_code/Hello.class

        if idx == 1: # Compilation
            res["explanation"] = "Compilation: Source to Bytecode.\n\nThe 'javac' compiler translates your human-readable Java code into 'Bytecode' (the .class file).\n\nWhat is Bytecode?\nIt's a set of instructions for a 'Virtual Machine' (the JVM), not for your physical CPU. This is why Java can run on any OS that has a JVM."
            
            # javac source_code/Hello.java (outputs .class in same dir by default)
            cmd = f"javac {java_file}"
            res["log"] += f"Running: {cmd}\n"
            success, out = bk.run_cmd(cmd, "Mock Bytecode", binary=True, filename=class_file)
            
            res["success"] = success
            if not success: res["error"] = out
            else:
                res["log"] += self._log_file_saved(class_file)
                res["content"] = {
                    "left_text": self.read_file(java_file), "right_text": self.read_file(class_file),
                    "left_title": "Source Code", "right_title": "Bytecode (.class)",
                    "left_lexer": CLexer()
                }

        elif idx == 2: # Execution - NEW
            res["explanation"] = "Execution (User Mode).\n\nThe JVM loads the class file and runs it. This is standard usage.\n\nFrom a user's perspective, they just want to see 'Hello from Java!'."
            # java -cp source_code Hello
            cmd = f"java -cp {self.workspace_dir} {base_name}"
            res["log"] += f"Running: {cmd}\n"
            success, out = bk.run_cmd(cmd)
            res["log"] += f"JVM Output:\n{out}"
            res["content"] = {
                "left_text": self.read_file(class_file), "right_text": out,
                "left_title": "Bytecode", "right_title": "Console Output"
            }

        elif idx == 3: # RE: Recon (Strings) - OLD idx 2
            res["explanation"] = "RE: Reconnaissance (Strings).\n\nWe scan the .class file for readable text. This often reveals constant values, class names, and error messages."
            res["log"] += f"Running: strings {class_file}"
            success, out = bk.run_cmd(f"strings {class_file}")
            res["content"] = {
                "left_text": self.read_file(class_file), "right_text": out,
                "left_title": "Bytecode", "right_title": "Strings Found"
            }

        elif idx == 4: # RE: Dynamic (Execution) - OLD idx 3
            res["explanation"] = "RE: Dynamic Analysis (Hacker Mode).\n\nWe run the Java program again, but this time we attach a Debugger (JDB) or monitor the JVM memory.\n\nWe look for side effects:\n- Does it write to a file?\n- Does it open a network connection?\n- We pause execution to inspect variables."
            # java -cp source_code Hello
            cmd = f"java -cp {self.workspace_dir} {base_name}"
            res["log"] += f"Running: {cmd}\n"
            success, out = bk.run_cmd(cmd)
            res["log"] += f"JVM Output:\n{out}"
            res["content"] = {
                "left_text": self.read_file(class_file), "right_text": out,
                "left_title": "Bytecode", "right_title": "Dynamic Run (Monitored)"
            }

        elif idx == 5: # RE: Static (Disasm) - OLD idx 4
            res["explanation"] = "RE: Static Analysis (javap).\n\nWe use 'javap' to disassemble Bytecode. This shows us the stack operations (push, pop, invoke) that the JVM performs."
            # javap -c -cp source_code Hello
            cmd = f"javap -c -cp {self.workspace_dir} {base_name}"
            res["log"] += f"Running: {cmd}"
            success, out = bk.run_cmd(cmd)
            res["content"] = {
                "left_text": self.read_file(class_file), "right_text": out,
                "left_title": "Bytecode", "right_title": "JVM Opcodes",
                "right_lexer": GasLexer()
            }

        elif idx == 6: # RE: Static (Decomp) - OLD idx 5
            res["explanation"] = "RE: Static Analysis (Decompilation).\n\nJava decompilation is extremely effective because the .class file preserves so much metadata.\n\nSimulation:\nWe simulate a tool like JD-GUI reconstructing the source."
            res["log"] += "Simulating Java Decompiler..."
            
            # Dynamic Decomp
            source_content = self.read_file(java_file)
            decomp_code = self._simulate_decompilation(source_content, "Java")
            
            res["content"] = {
                "left_text": self.read_file(class_file), "right_text": decomp_code,
                "left_title": "Bytecode", "right_title": "Decompiled Source (Mock)",
                "right_lexer": CLexer()
            }

        elif idx == 7: # RE: Solve (Patching) - OLD idx 6
            res["explanation"] = "RE: The Solve (Patching Class Files).\n\nJava Bytecode can be edited too! Tools like 'Recaf' allow us to change instructions or constants.\n\nSimulation:\nWe will patch the 'Hello' string in the .class file to 'PWNED'."
            
            # Create a patched copy
            f_patched = os.path.join(self.workspace_dir, f"{base_name}Patched.class")
            
            try:
                if os.path.exists(class_file):
                    with open(class_file, 'rb') as f: data = f.read()
                    
                    patch_from = b"Hello"
                    patch_to   = b"PWNED"
                    
                    if patch_from in data:
                        new_data = data.replace(patch_from, patch_to, 1)
                        with open(f_patched, 'wb') as f: f.write(new_data)
                        res["log"] += f"Patched 'Hello' -> 'PWNED' in class file.\nSaved to {f_patched}\n"
                    else:
                        res["log"] += "String 'Hello' not found. Copying original.\n"
                        shutil.copy(class_file, f_patched)
                else:
                     res["error"] = "Class file not found."
                     return res
            except Exception as e:
                res["log"] += f"Patch failed: {e}\n"
                shutil.copy(class_file, f_patched)

            # We can't easily run the patched class without renaming it properly in Java structure
            # But for simulation, we just show the HEX difference
            res["log"] += "Patching complete. Ready for injection."
            
            res["content"] = {
                 "left_text": f"[HEX VIEW]\nOriginal: ... Hello ...\nPatched : ... PWNED ...",
                 "right_text": "Visual Confirmation:\nThe string constant has been modified in the Bytecode Pool.",
                 "left_title": "Bytecode Patch", "right_title": "Result"
            }
        
        return res

    def reset_sim(self, preload_content=None):
        self.step_index = 0
        self.backend.clean_artifacts()
        self.console.log("Simulation Reset.")
        self.sidebar.set_next_text("NEXT STEP >")
        self.refresh_ui()

    def break_code(self):
        code = ""
        if self.language == "C":
            code = '#include <stdio.h>\nint main() {\n    printf("Error") // Missing semi\n    return 0;\n}'
            fname = SOURCE_FILE_C
        else:
            # Check editor content for class name first (handle unsaved changes)
            current_content = self.editor.txt_left.get("0.0", "end-1c")
            fname = self._get_java_filename(current_content)
            
            # Update tracked file
            self.current_java_file = fname
            
            # Extract class name from filename
            class_name = os.path.splitext(fname)[0]
            
            code = f'public class {class_name} {{\n    public static void main(String[] a) {{\n        System.out.print("Err") // Missing semi\n    }}\n}}'
            
        with open(fname, "w") as f: f.write(code)
        self.console.log(f"Injected Error into {fname}")
        self.reset_sim(preload_content=code)

    def read_file(self, fname):
        if not os.path.exists(fname): return "[File Not Found]"
        if fname.endswith((".o", ".exe", ".class")):
             return f"[Binary File: {os.path.getsize(fname)} bytes]"
        try:
            with open(fname, "r") as f: return f.read()
        except: return "[Error Reading]"

if __name__ == "__main__":
    app = CompilationApp()
    app.mainloop()
