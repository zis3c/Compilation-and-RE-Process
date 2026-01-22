# 📘 Technical Manual & Architecture Guide

This document provides a deep dive into the inner workings of the **Compilation Process Simulator**. It is intended for developers, educators, or anyone curious about the "magic" behind the GUI.

## 🏗️ Architecture

The application follows a simple **Model-View-Controller (MVC)**-like pattern:

### 1. The Frontend (`main.py` & `ui_components.py`)
Built with **CustomTkinter**, the frontend handles:
- **State Management**: Tracks the current `step_index` and `language` (C/Java).
- **Visualization**: Displays the split-screen view (Source Code vs. Output) using `pygments` for syntax highlighting.
- **Thread Management**: All backend operations run in a background thread (`threading.Thread`) to prevent the GUI from freezing during long compilation tasks.

### 2. The Backend (`backend.py`)
The logic engine of the simulator. It exposes a `CompilerBackend` class that:
- **Safe Execution**: Wraps `subprocess` calls to execute system commands (`gcc`, `javac`, etc.).
- **Process Management**: Handles Windows-specific flags (like `STARTF_USESHOWWINDOW`) to ensure console windows don't pop up annoyingly.
- **Artifact Management**: Cleans up temporary files (`.o`, `.class`, `.exe`) to keep the workspace tidy.

---

## 🔒 Strict Mode

The simulator operates in **Strict Mode**. This is a design choice to maximize educational value.

### Implementation
In `backend.py`, the `run_cmd` method performs a pre-flight check before executing any tool:

```python
# Pseudo-code logic
if command.startswith("gcc"):
    if not self.has_gcc:
        raise Error("GCC not found! Please install it.")
```

### Why not include compilers?
1.  **Size**: GCC and JDK are hundreds of megabytes. Bundling them would bloat the application.
2.  **Licensing**: Redistribution of certain JDKs or compiler chains can be legally complex.
3.  **Education**: Forcing the user to install tools teaches them about system PATH and environment variables—crucial skills for any developer.

---

## 🔍 Reverse Engineering Modules

The simulator demonstrates RE concepts using standard CLI tools:

| Concept | Tool Used | Description |
| :--- | :--- | :--- |
| **Reconnaissance** | `strings` | Scans the binary for printable ASCII chains (>4 chars). |
| **Disassembly** | `objdump -d` | Dumps the `.text` section of the binary to show ASM instructions. |
| **Bytecode Analysis** | `javap -c` | Disassembles Java class files to show JVM opcodes. |
| **Patching** | *Python Logic* | The app simulates hex-editing by directly modifying byte arrays in the file API to replace strings (e.g., "Hello" → "HACKD"). |

---

## 🚀 Extending the Simulator

Want to add **C++** or **Rust** support?

1.  **Update `backend.py`**:
    - Add a check for the new compiler (e.g., `rustc`).
    - Add a path variable for the new source file (`hello.rs`).

2.  **Update `main.py`**:
    - In `_define_steps()`, add a new list for the language.
    - In `restore_defaults()`, add the default "Hello World" code for that language.
    - Add a `prepare_rust_step(idx)` function to handle the logic for each stage.

3.  **Update UI**:
    - Add the new language to the Sidebar options in `ui_components.py`.

---

## 🐛 Troubleshooting Common Issues

### "subprocess/STARTWAIT_CAI not found"
**Status**: Fixed.
**Cause**: Used an invalid flag in `backend.py`.
**Fix**: Switched to `subprocess.STARTF_USESHOWWINDOW` for proper window suppression on Windows.

### "ImportError: GCC_CMD"
**Status**: Fixed.
**Cause**: A cleanup refactor accidentally removed a constant import.
**Fix**: The constant strictly points to "gcc" (system path) now.
