# Contributing to Compilation Process Simulator

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to this project. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## 🛠️ How to Contribute

### Reporting Bugs
This section guides you through submitting a bug report.
*   **Search existing issues** to see if the problem has already been reported.
*   **Create a new issue** and provide as much detail as possible:
    *   **Steps to reproduce**: How can we see the bug ourselves?
    *   **Expected behavior**: What did you expect to happen?
    *   **Actual behavior**: What actually happened?
    *   **Screenshots/Logs**: Any visual proof or error messages.

### Suggesting Enhancements
*   Open an issue with the tag **enhancement**.
*   Explain why this enhancement would be useful.

### Pull Requests
1.  **Fork the repo** and create your branch from `main`.
2.  **Clone the repository** to your local machine.
3.  **Install dependencies**: `pip install -r requirements.txt`.
4.  **Make your changes**. 
    *   Ensure "Strict Mode" checks inside `backend.py` are preserved.
    *   Follow PEP 8 coding standards for Python.
5.  **Test your changes**. Run the simulator and verify all steps (C and Java lanes) work as expected.
6.  **Push** to your fork.
7.  **Submit a Pull Request**!

---

## 💻 specific Development Guidelines

### Python Environment
*   We target **Python 3.10+**.
*   We use **CustomTkinter** for the UI. Please don't introduce new heavy dependencies without discussion.

### Adding New Languages
If you want to add support for a new language (e.g., Rust, Go):
1.  Update `backend.py` to handle the new compiler tools.
2.  Update `main.py` to add the visualisation steps.
3.  See `TECHNICAL_MANUAL.md` for architectural details.

---

## 📜 License
By contributing, you agree that your contributions will be licensed under its MIT License.
