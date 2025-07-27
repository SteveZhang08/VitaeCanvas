import tkinter as tk
from tkinter import ttk, scrolledtext
import DNA_Generation

class AminoAcidApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GUI DNA_Generation by SteveZhang08")
        self.root.geometry("800x600")
        
        # 设置现代化风格
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#2c3e50')
        self.style.configure('TButton', background='#34495e', foreground='#ecf0f1', 
                            font=('Helvetica', 10), borderwidth=1)
        self.style.map('TButton', background=[('active', '#2c3e50')])
        self.style.configure('TLabel', background='#2c3e50', foreground='#ecf0f1', 
                           font=('Helvetica', 10, 'bold'))
        self.style.configure('TEntry', fieldbackground='#ecf0f1', foreground='#2c3e50')
        self.style.configure('TListbox', background='#ecf0f1', foreground='#2c3e50')
        
        # 主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入部分
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        
        self.sequence_label = ttk.Label(self.input_frame, text="Amino Acid Sequence:")
        self.sequence_label.grid(row=0, column=0, sticky='w')
        
        self.sequence_entry = ttk.Entry(self.input_frame, width=50)
        self.sequence_entry.grid(row=1, column=0, sticky='ew', padx=(0, 10))
        
        self.add_button = ttk.Button(self.input_frame, text="Add", command=self.add_sequence)
        self.add_button.grid(row=1, column=1, sticky='ew')
        self.sequence_entry.bind('<Return>', lambda event: self.add_sequence())
        
        # 序列列表部分
        self.list_frame = ttk.Frame(self.main_frame)
        self.list_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 10))
        
        self.list_label = ttk.Label(self.list_frame, text="Sequence List:")
        self.list_label.grid(row=0, column=0, sticky='w')
        
        self.sequence_list = tk.Listbox(self.list_frame, height=6, selectmode=tk.SINGLE)
        self.sequence_list.grid(row=1, column=0, sticky='nsew', padx=(0, 10))
        
        self.delete_button = ttk.Button(self.list_frame, text="Delete", command=self.delete_sequence)
        self.delete_button.grid(row=1, column=1, sticky='ew')
        
        # 操作按钮
        self.generate_button = ttk.Button(self.main_frame, text="Generate", command=self.generate_sequences)
        self.generate_button.grid(row=2, column=0, sticky='ew', pady=(0, 20))
        
        # 结果显示部分
        self.result_frame = ttk.Frame(self.main_frame)
        self.result_frame.grid(row=3, column=0, sticky='nsew')
        
        # RNA部分
        self.rna_label = ttk.Label(self.result_frame, text="RNA:")
        self.rna_label.grid(row=0, column=0, sticky='w')
        
        # 添加RNA复制按钮
        self.copy_rna_button = ttk.Button(
            self.result_frame, 
            text="Copy RNA", 
            command=lambda: self.copy_to_clipboard(self.rna_text.get(1.0, tk.END))
        )
        self.copy_rna_button.grid(row=0, column=1, sticky='e', padx=(10, 0))
        
        self.rna_text = scrolledtext.ScrolledText(
            self.result_frame, 
            wrap=tk.NONE, 
            width=60, 
            height=8,
            bg='#ecf0f1',
            fg='#2c3e50',
            insertbackground='#2c3e50'
        )
        self.rna_text.grid(row=1, column=0, sticky='nsew', pady=(0, 10))
        
        # DNA部分
        self.dna_label = ttk.Label(self.result_frame, text="DNA:")
        self.dna_label.grid(row=2, column=0, sticky='w')
        
        # 添加DNA复制按钮
        self.copy_dna_button = ttk.Button(
            self.result_frame, 
            text="Copy DNA", 
            command=lambda: self.copy_to_clipboard(self.dna_text.get(1.0, tk.END))
        )
        self.copy_dna_button.grid(row=2, column=1, sticky='e', padx=(10, 0))
        
        self.dna_text = scrolledtext.ScrolledText(
            self.result_frame, 
            wrap=tk.NONE, 
            width=60, 
            height=8,
            bg='#ecf0f1',
            fg='#2c3e50',
            insertbackground='#2c3e50'
        )
        self.dna_text.grid(row=3, column=0, sticky='nsew')
        
        # 配置网格权重
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_columnconfigure(0, weight=1)
        
    def add_sequence(self):
        sequence = self.sequence_entry.get().strip()
        if sequence:
            self.sequence_list.insert(tk.END, sequence)
            self.sequence_entry.delete(0, tk.END)
    
    def delete_sequence(self):
        selection = self.sequence_list.curselection()
        if selection:
            self.sequence_list.delete(selection[0])
    
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text.strip())
    
    def generate_sequences(self):
        sequences = self.sequence_list.get(0, tk.END)
        if sequences:
            result = DNA_Generation.re_translate(sequences)
            self.rna_text.delete(1.0, tk.END)
            self.rna_text.insert(tk.END, result['rna'])
            self.dna_text.delete(1.0, tk.END)
            self.dna_text.insert(tk.END, result['dna'])

if __name__ == "__main__":
    root = tk.Tk()
    app = AminoAcidApp(root)
    root.mainloop()