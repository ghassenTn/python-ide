import tkinter as tk
from tkinter import scrolledtext, filedialog
from io import StringIO
import sys
import keyword
import re
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class CodeInputWithLineNumbers(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.text_widget = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15, font=("Courier New", 12), undo=True)
        self.text_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(self, width=4, padx=5, takefocus=0, border=0, background='#2b2b2b', foreground='gray', state='disabled', font=("Courier New", 12))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Bind events
        self.text_widget.bind("<KeyRelease>", self.on_key_release)
        self.text_widget.bind("<Return>", self.on_return_key)
        self.text_widget.bind("<BackSpace>", self.on_backspace_key)
        self.text_widget.bind("<MouseWheel>", self.on_mouse_wheel)  # Bind mouse wheel event for scrolling
        self.text_widget.bind("<Configure>", self.update_line_numbers)  # Bind widget configuration event

        # Create a scrollbar that will be used to synchronize scrolling
        self.text_widget.bind_all("<Button-4>", self.on_mouse_wheel)  # For Linux mouse wheel scrolling
        self.text_widget.bind_all("<Button-5>", self.on_mouse_wheel)  # For Linux mouse wheel scrolling

        self.update_line_numbers()

        # Configure a tag for Python keywords (blue)
        self.text_widget.tag_configure("keyword", foreground="blue")

    def on_key_release(self, event=None):
        self.highlight_syntax()
        self.update_line_numbers()

    def on_return_key(self, event=None):
        current_line = self.text_widget.get("insert linestart", "insert lineend")
        leading_spaces = len(current_line) - len(current_line.lstrip())

        if current_line.strip().endswith(':'):
            self.text_widget.insert("insert", "\n" + " " * (leading_spaces + 4))
            return "break"
        else:
            self.text_widget.insert("insert", "\n" + " " * leading_spaces)
            return "break"

    def on_backspace_key(self, event=None):
        current_line = self.text_widget.get("insert linestart", "insert lineend")
        leading_spaces = len(current_line) - len(current_line.lstrip())

        if leading_spaces > 0 and len(current_line.strip()) == 0:
            self.text_widget.delete("insert-1c", "insert")
            return "break"

    def on_mouse_wheel(self, event=None):
        self.sync_scroll()

    def sync_scroll(self):
        # Synchronize the line numbers widget scroll with the text widget
        self.line_numbers.yview_moveto(self.text_widget.yview()[0])

    def highlight_syntax(self):
        code = self.text_widget.get("1.0", tk.END)
        self.text_widget.mark_set("range_start", "1.0")

        # Remove existing tags
        for tag in self.text_widget.tag_names():
            self.text_widget.tag_remove(tag, "1.0", tk.END)

        # Apply new tags
        for match in re.finditer(r'\b(' + '|'.join(keyword.kwlist) + r')\b', code):
            start_index = f"1.0+{match.start()}c"
            end_index = f"1.0+{match.end()}c"
            self.text_widget.tag_add("keyword", start_index, end_index)

    def update_line_numbers(self, event=None):
        self.line_numbers.configure(state='normal')
        self.line_numbers.delete("1.0", tk.END)

        line_count = int(self.text_widget.index('end-1c').split('.')[0])
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))

        self.line_numbers.insert("1.0", line_numbers_string)
        self.line_numbers.configure(state='disabled')

    def get_code(self):
        return self.text_widget.get("1.0", tk.END)

    def clear_code(self):
        self.text_widget.delete("1.0", tk.END)
        self.update_line_numbers()

    def set_font(self, font_name, font_size):
        self.text_widget.config(font=(font_name, font_size))
        self.line_numbers.config(font=(font_name, font_size))

    def load_file(self, file_path):
        with open(file_path, "r") as file:
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, file.read())
            self.highlight_syntax()  # Apply syntax highlighting after loading the file
            self.update_line_numbers()  # Update line numbers after loading the file



class JupyterApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Jupyter-like App")
        self.geometry("900x700")

        self.create_widgets()
        self.create_menu()

    def create_widgets(self):
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

        code_label = ttk.Label(input_frame, text="Code Input", font=("Helvetica", 12, "bold"))
        code_label.pack(anchor=tk.W, pady=(0, 5))

        self.code_input = CodeInputWithLineNumbers(input_frame)
        self.code_input.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.run_button = ttk.Button(button_frame, text="Run", command=self.run_code, bootstyle=SUCCESS)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(button_frame, text="Clear Code", command=self.clear_code, bootstyle=INFO)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.clear_output_button = ttk.Button(button_frame, text="Clear Output", command=self.clear_output, bootstyle=WARNING)
        self.clear_output_button.pack(side=tk.LEFT, padx=5)

        output_label = ttk.Label(self, text="Output", font=("Helvetica", 12, "bold"))
        output_label.pack(anchor=tk.W, padx=10, pady=(10, 5))

        self.output_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15, bg="#2b2b2b", fg="white", font=("Courier New", 12))
        self.output_area.pack(fill=tk.BOTH, padx=10, pady=(0, 10), expand=True)
        self.output_area.configure(state='disabled')

    def create_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        font_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Font", menu=font_menu)

        # Font options
        font_menu.add_command(label="Arial 12", command=lambda: self.change_font("Arial", 12))
        font_menu.add_command(label="Courier New 12", command=lambda: self.change_font("Courier New", 12))
        font_menu.add_command(label="Courier New 16", command=lambda: self.change_font("Courier New", 16))
        font_menu.add_command(label="Times New Roman 12", command=lambda: self.change_font("Times New Roman", 12))

        import_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=import_menu)
        
        # Import file option
        import_menu.add_command(label="Import Python File", command=self.import_file)

    def change_font(self, font_name, font_size):
        self.code_input.set_font(font_name, font_size)
        self.output_area.config(font=(font_name, font_size))

    def import_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if file_path:
            self.code_input.load_file(file_path)

    def run_code(self):
        code = self.code_input.get_code()
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()

        try:
            exec(code)
        except Exception as e:
            print(f"Error: {e}")

        sys.stdout = old_stdout
        output = redirected_output.getvalue()

        self.output_area.configure(state='normal')
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert(tk.END, code)
        self.output_area.insert(tk.END, output)
        self.output_area.configure(state='disabled')

    def clear_code(self):
        self.code_input.clear_code()

    def clear_output(self):
        self.output_area.configure(state='normal')
        self.output_area.delete("1.0", tk.END)
        self.output_area.configure(state='disabled')

if __name__ == "__main__":
    app = JupyterApp()
    app.mainloop()
