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

## Installation

### Option 1: Standalone Executable
Download the latest `CompilationSimulator.exe` from this repository. No Python or dependencies required.

### Option 2: Run from Source
1. Install Python 3.10+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. Launch the application.
2. Select a language (C or Java) from the sidebar.
3. Advance through the steps using "NEXT STEP".
4. Explore each stage's output and explanation.
5. Try modifying the source code and saving to see how it affects the result!

## Requirements for Full Functionality

The simulator works in "Mock Mode" by default. For real compilation, ensure you have:
- **GCC** (MinGW) for C compilation.
- **JDK** (Java Development Kit) for Java compilation.
