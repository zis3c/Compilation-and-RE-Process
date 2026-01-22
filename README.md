# Compilation & Reverse Engineering Process Simulator

A visual, interactive simulator designed to demonstrate the stages of compilation (C/Java) and the basics of Reverse Engineering.

## Features

- **Multi-Language Support**: Simulate both C and Java compilation workflows.
- **Visual Steps**: specific stages for:
  - Source Code
  - Preprocessing (C) / Bytecode (Java)
  - Compilation
  - Assembly / Disassembly
  - Linking
  - Execution
  - **Reverse Engineering**: Strings, Dynamic Analysis, Static Analysis (Disassembly/Decompilation), and Patching.
- **Interactive**: Edit code, break it to see errors, and visualize the transformation of data.

## 🚀 Application

This is a **Python Application**. You run it directly from source for the best experience.

### Requirements
- **Python 3.10+**
- **Modules**: `customtkinter`, `pygments` (Install via `pip install -r requirements.txt`)
- **Tools**: GCC (MinGW) and Java (JDK) for real compilation.

### 📥 Setup & Run
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **[Important]** Ensure you have GCC and Java installed:
   - **GCC**: Install MinGW-w64 and add `bin` to PATH.
   - **Java**: Install JDK 17+ and add `bin` to PATH.

3. Run the application:
   ```bash
   python main.py
   ```

*(Note: A standalone executable may be available in releases, but running from source is recommended for stability.)*

## Usage

1. Launch `main.py`.
2. Select a language (C or Java) from the sidebar.
3. Advance through the steps using "NEXT STEP".
4. Explore each stage's output and explanation.
5. Try modifying the source code and saving to see how it affects the result!

## Troubleshooting

### "System Error" or Crashes?
Ensure you have the required compilers installed and added to your system PATH. The application runs in **Strict Mode** and expects real tools to be available.

