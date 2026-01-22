import customtkinter as ctk
import tkinter as tk
from pygments import lex
from pygments.lexers import CLexer, GasLexer

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, step_callback, save_callback, break_callback, reset_callback, lang_callback):
        super().__init__(master, width=204, corner_radius=0)
        self.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.grid_rowconfigure(20, weight=1)

        # Logo
        self.logo = ctk.CTkLabel(self, text="CompSim", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Language Selector
        self.lang_menu = ctk.CTkOptionMenu(self, values=["C", "Java"], command=lang_callback)
        self.lang_menu.grid(row=1, column=0, padx=20, pady=10)

        # Headers
        self.header_comp = ctk.CTkLabel(self, text="COMPILATION", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray70")
        self.header_comp.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")

        # Dynamic Buttons (Pool of 12 max buttons)
        self.buttons = []
        for i in range(12):
            btn = ctk.CTkButton(self, text=f"Step {i}", fg_color="transparent", border_width=1, anchor="w", state="disabled")
            self.buttons.append(btn)
        
        # RE Header (Position varies)
        self.header_re = ctk.CTkLabel(self, text="REVERSE ENG.", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray70")
        
        # Controls
        self.btn_next = ctk.CTkButton(self, text="NEXT STEP >", command=step_callback)
        self.btn_save = ctk.CTkButton(self, text="SAVE CODE", command=save_callback, fg_color="#2E7D32", hover_color="#1B5E20")
        self.btn_break = ctk.CTkButton(self, text="BREAK IT! (Error)", command=break_callback, fg_color="#C62828", hover_color="#B71C1C")
        self.btn_restore = ctk.CTkButton(self, text="RESTORE CODE", command=reset_callback, fg_color="#0288D1", hover_color="#0277BD") # Using reset_callback for now (acts as restore)
        self.btn_reset = ctk.CTkButton(self, text="RESET SIM", command=reset_callback, fg_color="transparent", border_width=1, text_color="silver")

        # Initial Grid for controls (Fixed at bottom logic handled by refresh)
        self.current_lang = "C"

    def refresh(self, language, steps):
        self.current_lang = language
        
        # 1. Compilation Header
        self.header_comp.configure(text="JAVA COMPILATION" if language == "Java" else "COMPILATION PROT.")
        
        # 2. Map Buttons
        split_idx = 6 if language == "C" else 3
        
        current_row = 3
        # Compilation Section
        for i in range(split_idx):
            self.buttons[i].configure(text=steps[i])
            self.buttons[i].grid(row=current_row, column=0, padx=20, pady=2, sticky="ew")
            current_row += 1
            
        # RE Header
        self.header_re.configure(text="JAVA REVERSING" if language == "Java" else "REVERSE ENG.")
        self.header_re.grid(row=current_row, column=0, padx=10, pady=(15, 0), sticky="w")
        current_row += 1
        
        # RE Section
        for i in range(split_idx, len(steps)):
            self.buttons[i].configure(text=steps[i])
            self.buttons[i].grid(row=current_row, column=0, padx=20, pady=2, sticky="ew")
            current_row += 1
            
        # Hide unused buttons
        for i in range(len(steps), 12):
            self.buttons[i].grid_forget()
            
        # Controls Placement
        self.btn_next.grid(row=current_row + 1, column=0, padx=20, pady=20)
        self.btn_save.grid(row=current_row + 2, column=0, padx=20, pady=5)
        self.btn_break.grid(row=current_row + 3, column=0, padx=20, pady=5)
        self.btn_restore.grid(row=current_row + 4, column=0, padx=20, pady=5)
        self.btn_reset.grid(row=current_row + 5, column=0, padx=20, pady=20)
    
    def highlight(self, index):
        for i, btn in enumerate(self.buttons):
            if i == index:
                btn.configure(fg_color=("gray75", "gray25"), text_color=("black", "white"))
            else:
                btn.configure(fg_color="transparent", text_color=("gray50", "gray50"))

    def set_next_text(self, text):
        self.btn_next.configure(text=text)
        if text == "DONE": self.btn_next.configure(state="disabled")
        else: self.btn_next.configure(state="normal")
    
    def enable_controls(self, enable=True):
        state = "normal" if enable else "disabled"
        self.btn_save.configure(state=state)
        self.btn_break.configure(state=state)
        self.btn_restore.configure(state=state)


class Console(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=120, corner_radius=0)
        # self.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10)) # Handled by PanedWindow
        
        ctk.CTkLabel(self, text="Terminal Output", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=2)
        
        self.text = ctk.CTkTextbox(self, height=100, font=ctk.CTkFont(family="Consolas", size=12))
        self.text.pack(fill="both", expand=True, padx=5, pady=5)
        self.text.configure(state="disabled")
        
        self.text._textbox.tag_config("error", foreground="#ff5555")
        self.text._textbox.tag_config("info", foreground="white")

    def log(self, message, error=False):
        self.text.configure(state="normal")
        tag = "error" if error else "info"
        self.text.insert("end", f"> {message}\n", tag)
        self.text.see("end")
        self.text.configure(state="disabled")


class EditorArea(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        # self.grid(row=0, column=1, sticky="nsew", padx=10, pady=10) # Handled by PanedWindow
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header = ctk.CTkLabel(self, text="Welcome", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.grid(row=0, column=0, pady=(10, 5), sticky="w", padx=20)

        # Paned Window
        self.paned = tk.PanedWindow(self, orient=tk.VERTICAL, sashwidth=6, bg="#2b2b2b", sashrelief="flat")
        self.paned.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Top: Explanation
        self.top_pane = ctk.CTkFrame(self.paned, fg_color="transparent")
        self.expl_box = ctk.CTkTextbox(self.top_pane, fg_color="transparent", text_color="silver", wrap="word", font=ctk.CTkFont(size=14))
        self.expl_box.pack(fill="both", expand=True, padx=10, pady=5)
        self.paned.add(self.top_pane, minsize=80, sticky="nsew", stretch="always")

        # Bottom: Split View
        self.bottom_pane = ctk.CTkFrame(self.paned, fg_color="transparent")
        self.bottom_pane.grid_columnconfigure(0, weight=1)
        self.bottom_pane.grid_columnconfigure(1, weight=1)
        self.bottom_pane.grid_rowconfigure(1, weight=1)
        
        # Left
        self.lbl_left = ctk.CTkLabel(self.bottom_pane, text="Input")
        self.lbl_left.grid(row=0, column=0, sticky="w", padx=10)
        self.txt_left = ctk.CTkTextbox(self.bottom_pane, width=400, font=ctk.CTkFont(family="Consolas", size=13))
        self.txt_left.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Right
        self.lbl_right = ctk.CTkLabel(self.bottom_pane, text="Output")
        self.lbl_right.grid(row=0, column=1, sticky="w", padx=10)
        self.txt_right = ctk.CTkTextbox(self.bottom_pane, width=400, font=ctk.CTkFont(family="Consolas", size=13))
        self.txt_right.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        self.paned.add(self.bottom_pane, minsize=200, sticky="nsew", stretch="always")
        
        # Setup Highlighting
        self._setup_highlighting_tags()

    def set_header(self, text):
        self.header.configure(text=text)

    def set_explanation(self, text):
        self.expl_box.configure(state="normal")
        self.expl_box.delete("0.0", "end")
        self.expl_box.insert("0.0", text)
        self.expl_box.configure(state="disabled")

    def _setup_highlighting_tags(self):
        for tb in [self.txt_left._textbox, self.txt_right._textbox]:
            tb.tag_config("Token.Keyword", foreground="#ffb86c")        
            tb.tag_config("Token.Keyword.Type", foreground="#8be9fd")   
            tb.tag_config("Token.Name.Function", foreground="#50fa7b")  
            tb.tag_config("Token.Literal.String", foreground="#f1fa8c") 
            tb.tag_config("Token.Comment", foreground="#6272a4")        
            tb.tag_config("Token.Operator", foreground="#ff79c6")       
            tb.tag_config("Token.Punctuation", foreground="#f8f8f2")    
            tb.tag_config("Token.Number", foreground="#bd93f9")         

    def apply_highlighting(self, ctk_textbox, code, lexer):
        ctk_textbox.configure(state="normal")
        ctk_textbox.delete("0.0", "end")
        if not lexer:
            ctk_textbox.insert("0.0", code)
        else:
            tokens = lex(code, lexer)
            for token_type, value in tokens:
                tag = str(token_type)
                # Simple fallback tagging
                while tag and not ctk_textbox._textbox.tag_names().__contains__(tag):
                    if "." in tag: tag = tag.rsplit(".", 1)[0]
                    else: tag = None
                ctk_textbox.insert("end", value, tag if tag else ())
        ctk_textbox.configure(state="disabled")

    def set_content(self, left_text, right_text, left_title="Input", right_title="Output", left_lexer=None, right_lexer=None, left_editable=False):
        self.lbl_left.configure(text=left_title)
        self.apply_highlighting(self.txt_left, left_text, left_lexer)
        if left_editable: self.txt_left.configure(state="normal")
        
        self.lbl_right.configure(text=right_title)
        self.apply_highlighting(self.txt_right, right_text, right_lexer)
