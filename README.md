# Compilation & RE Process Simulator

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-green?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

<br/>
<img src="ui.png" alt="Simulator Screenshot" width="800">
<br/>

**A visual, interactive educational tool to demonstrate the Compilation Process and Reverse Engineering concepts.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Technical Docs](TECHNICAL_MANUAL.md)

</div>

---

## 📖 Overview

The **Compilation Process Simulator** bridges the gap between high-level code and machine execution. It visualizes every step of transforming C or Java source code into an executable, and then demonstrates how Reverse Engineers deconstruct that same executable.

Unlike static interactives, this simulator runs **real compilation commands** in the background, providing an authentic learning experience.

## ✨ Features

- **See the Invisible**: Visualize intermediate artifacts usually hidden from developers (`.i`, `.s`, `.o`, `.class`).
- **Dual Language Support**: 
    - **C Lane**: Source → Preprocessing → Compilation → Assembly → Linking → Execution.
    - **Java Lane**: Source → Bytecode → JVM Execution.
- **Reverse Engineering Suite**:
    - **Recon**: Extract ASCII strings from binaries.
    - **Disassembly**: View raw CPU opcodes and mnemonics.
    - **Decompilation**: Simulate recovering source code from binaries.
    - **Patching**: Hex-edit binaries to alter behavior without recompiling.
- **Strict Mode**: Enforces the use of real-world tools (`GCC` and `JDK`) for accurate simulation.

## 🛠️ Prerequisites

To run this application efficiently, ensure your environment is set up:

1.  **Python 3.10+**: [Download Here](https://www.python.org/downloads/)
2.  **GCC (MinGW)**: Required for C compilation steps. [Installation Guide](https://www.msys2.org/)
3.  **Java JDK 17+**: Required for Java compilation steps. [Download Here](https://www.oracle.com/java/technologies/downloads/)

> **Note**: The application will check your system `PATH` for these tools. If missing, "Strict Mode" will prevent execution of compilation steps.

## 📥 Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/zis3c/Compilation-and-RE-Process.git
    cd Compilation-and-RE-Process/simulator
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**:
    ```bash
    python main.py
    ```

## 🖥️ Usage Guide

1.  **Launch**: Run `python main.py` to open the GUI.
2.  **Select Language**: Choose **C** or **Java** from the left sidebar.
3.  **Step-by-Step**: Click **NEXT STEP >** to advance through the lifecycle.
4.  **Interactive**:
    - **Edit**: You can modify the source code in the first step.
    - **Break**: Intentionally write bad code to see compiler errors.
    - **Analyze**: Read the explanations for each step to understand *why* the output looks the way it does.

## 📚 Technical Logic

Curious about how the simulator works under the hood? 
Check out our **[Technical Manual](TECHNICAL_MANUAL.md)** for a deep dive into the `CompilerBackend`, strict mode enforcement, and architecture.

## 🤝 Contributing

Contributions are welcome! Please run the simulator locally and test changes before submitting a Pull Request.

---
<div align="center">
Made with ❤️ for the RE Community
</div>
