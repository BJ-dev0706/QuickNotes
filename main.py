import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
from database.setup import setup_database  # Import the setup_database function

class NoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Note-taking Application")
        self.root.geometry("600x500")
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.section_var = tk.StringVar()
        self.section_menu = ttk.OptionMenu(main_frame, self.section_var, *self.get_sections())
        self.section_menu.pack(pady=10, fill=tk.X)

        self.title_entry = ttk.Entry(main_frame, width=50)
        self.title_entry.pack(pady=10, fill=tk.X)

        text_frame = ttk.Frame(main_frame)
        text_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.text_area = tk.Text(text_frame, height=15, width=50, wrap=tk.WORD)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(text_frame, command=self.text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill=tk.X)

        self.save_button = ttk.Button(button_frame, text="Save Note", command=self.save_note)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.load_button = ttk.Button(button_frame, text="Load Note", command=self.load_note)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(button_frame, text="Delete Note", command=self.delete_note)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.like_button = ttk.Button(button_frame, text="Like Note", command=self.like_note)
        self.like_button.pack(side=tk.LEFT, padx=5)

    def get_sections(self):
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sections')
        sections = [row[0] for row in cursor.fetchall()]
        conn.close()
        return sections

    def save_note(self):
        title = self.title_entry.get()
        content = self.text_area.get("1.0", tk.END).strip()
        section_name = self.section_var.get()
        if title and content and section_name:
            conn = sqlite3.connect('notes.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM sections WHERE name = ?', (section_name,))
            section_id = cursor.fetchone()[0]
            try:
                cursor.execute('INSERT INTO notes (title, content, section_id) VALUES (?, ?, ?)', (title, content, section_id))
                conn.commit()
                messagebox.showinfo("Success", "Note saved!")
            except sqlite3.IntegrityError:
                messagebox.showwarning("Warning", "Note with this title already exists.")
            conn.close()
        else:
            messagebox.showwarning("Warning", "Please enter a title, content, and select a section.")

    def load_note(self):
        title = simpledialog.askstring("Load Note", "Enter the title of the note:")
        if title:
            conn = sqlite3.connect('notes.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT notes.content, sections.name 
                FROM notes 
                JOIN sections ON notes.section_id = sections.id 
                WHERE notes.title = ?
            ''', (title,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                content, section_name = result
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, title)
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.section_var.set(section_name)
            else:
                messagebox.showwarning("Warning", "Note not found.")
        else:
            messagebox.showwarning("Warning", "Please enter a title.")

    def delete_note(self):
        title = simpledialog.askstring("Delete Note", "Enter the title of the note to delete:")
        if title:
            conn = sqlite3.connect('notes.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM notes WHERE title = ?', (title,))
            conn.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Note deleted!")
            else:
                messagebox.showwarning("Warning", "Note not found.")
            conn.close()
        else:
            messagebox.showwarning("Warning", "Please enter a title.")

    def like_note(self):
        title = simpledialog.askstring("Like Note", "Enter the title of the note to like:")
        if title:
            conn = sqlite3.connect('notes.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE notes SET likes = likes + 1 WHERE title = ?', (title,))
            conn.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Note liked!")
            else:
                messagebox.showwarning("Warning", "Note not found.")
            conn.close()
        else:
            messagebox.showwarning("Warning", "Please enter a title.")

if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = NoteApp(root)
    root.mainloop()
