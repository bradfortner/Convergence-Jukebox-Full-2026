import os
import re
import wordsegment
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError

class RenamerApp:
    def __init__(self, master):
        self.master = master
        master.title("File Renamer")
        master.geometry("1024x768")

        self.directory = "rockabilly"
        self.original_suggestions = {}

        wordsegment.load()
        self.create_widgets()
        self.populate_file_list()

    def create_widgets(self):
        self.file_frame = ttk.Frame(self.master)
        self.file_frame.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.file_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_list = ttk.Treeview(self.file_frame, columns=("Approve", "Original", "Suggested", "Artist", "Title", "UseTags"), yscrollcommand=self.scrollbar.set)
        
        self.file_list.heading("#0", text="", anchor=tk.W)
        self.file_list.heading("Approve", text="Approve", anchor=tk.CENTER)
        self.file_list.heading("Original", text="Original Filename", anchor=tk.W)
        self.file_list.heading("Suggested", text="Suggested New Filename", anchor=tk.W)
        self.file_list.heading("Artist", text="Artist", anchor=tk.W)
        self.file_list.heading("Title", text="Title", anchor=tk.W)
        self.file_list.heading("UseTags", text="Use Artist/Title", anchor=tk.CENTER)
        
        self.file_list.column("#0", width=0, stretch=tk.NO)
        self.file_list.column("Approve", width=70, anchor=tk.CENTER)
        self.file_list.column("Original", width=250)
        self.file_list.column("Suggested", width=250)
        self.file_list.column("Artist", width=150)
        self.file_list.column("Title", width=150)
        self.file_list.column("UseTags", width=100, anchor=tk.CENTER)
        
        self.file_list.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.file_list.yview)

        self.file_list.bind("<Double-1>", self.edit_item)
        self.file_list.bind("<ButtonRelease-1>", self.on_list_click)

        self.rename_button = ttk.Button(self.master, text="Rename Approved Files", command=self.rename_files)
        self.rename_button.pack(pady=10)
    
    def sanitize_filename(self, filename_raw):
        """Cleans a string to be a valid filename containing only a-z, A-Z, 0-9, -, and spaces.
        Replaces '&' with 'and'."""
        filename = filename_raw.replace('&', 'and') # Replace & with and first
        filename = re.sub(r'[^a-zA-Z0-9\s-]', '', filename) # Remove disallowed characters
        filename = re.sub(r'\s+', ' ', filename).strip() # Replace multiple spaces with one, strip leading/trailing
        return filename

    def populate_file_list(self):
        for filename in sorted(os.listdir(self.directory)):
            if filename.endswith(".mp3"):
                name, extension = os.path.splitext(filename)
                
                artist, title = "", ""
                try:
                    filepath = os.path.join(self.directory, filename)
                    audio = MP3(filepath)
                    artist = audio.get('TPE1', [''])[0] if audio.get('TPE1') else ""
                    title = audio.get('TIT2', [''])[0] if audio.get('TIT2') else ""
                except (ID3NoHeaderError, Exception):
                    pass

                segments = wordsegment.segment(name)
                new_name_parts = []
                current_pos = 0
                for segment in segments:
                    try:
                        start_index = name.lower().index(segment, current_pos)
                        end_index = start_index + len(segment)
                        new_name_parts.append(name[start_index:end_index])
                        current_pos = end_index
                    except ValueError:
                        new_name_parts.append(segment)

                # Sanitize the wordsegment suggestion
                wordsegment_suggestion = self.sanitize_filename(' '.join(new_name_parts)) + extension

                item_id = self.file_list.insert("", tk.END, values=('[ ]', filename, wordsegment_suggestion, artist, title, '[ ]'))
                self.original_suggestions[item_id] = wordsegment_suggestion

    def on_list_click(self, event):
        item_id = self.file_list.identify_row(event.y)
        column_id = self.file_list.identify_column(event.x)

        if not item_id:
            return

        # Column #1 is "Approve", Column #6 is "UseTags"
        if column_id in ("#1", "#6"):
            current_value = self.file_list.set(item_id, column_id)
            new_value = '[x]' if current_value == '[ ]' else '[ ]'
            self.file_list.set(item_id, column_id, new_value)

            if column_id == "#6": # "UseTags" was clicked
                if new_value == '[x]':
                    values = self.file_list.item(item_id, "values")
                    artist = values[3]
                    title = values[4]
                    if artist and title:
                        _, extension = os.path.splitext(values[1])
                        # Sanitize the generated name from tags
                        new_name = self.sanitize_filename(f"{artist} - {title}") + extension
                        self.file_list.set(item_id, "Suggested", new_name)
                else: # Revert
                    original_suggestion = self.original_suggestions.get(item_id, "")
                    self.file_list.set(item_id, "Suggested", original_suggestion)

    def edit_item(self, event):
        item_id = self.file_list.identify_row(event.y)
        column_id = self.file_list.identify_column(event.x)

        # Allow editing only on "Suggested", "Artist", and "Title" columns
        if not item_id or column_id not in ("#3", "#4", "#5"):
            return

        x, y, width, height = self.file_list.bbox(item_id, column_id)
        
        # Get the column index (0-based) to get the value
        col_index = int(column_id.replace('#', '')) - 2
        current_text = self.file_list.item(item_id, "values")[col_index]
        
        entry = ttk.Entry(self.master)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, current_text)
        entry.focus_force()
        
        entry.bind("<Return>", lambda e, i=item_id, c=column_id, en=entry: self.save_edit(e, i, c, en))
        entry.bind("<FocusOut>", lambda e, i=item_id, c=column_id, en=entry: self.save_edit(e, i, c, en))

    def save_edit(self, event, item_id, column_id, entry):
        new_text = entry.get()
        
        # If the "Suggested" name is being edited, apply full sanitization
        if column_id == "#3":
             _, extension = os.path.splitext(self.file_list.item(item_id, "values")[1]) # Get original extension
             sanitized_text = self.sanitize_filename(os.path.splitext(new_text)[0]) + extension
             self.file_list.set(item_id, column_id, sanitized_text)
        else:
            self.file_list.set(item_id, column_id, new_text)

        entry.destroy()

    def rename_files(self):
        items_to_rename = []
        for item_id in self.file_list.get_children():
            values = self.file_list.item(item_id, "values")
            if values[0] == '[x]':
                items_to_rename.append(item_id)

        if not items_to_rename:
            messagebox.showinfo("No files selected", "Please approve files to rename by clicking the '[ ]' in the 'Approve' column.")
            return

        if messagebox.askyesno("Confirm Rename", f"Are you sure you want to rename {len(items_to_rename)} files?"):
            renamed_count = 0
            errors = []
            for item_id in items_to_rename:
                try:
                    values = self.file_list.item(item_id, "values")
                    original_name = values[1]
                    new_name = values[2]
                    
                    old_path = os.path.join(self.directory, original_name)
                    new_path = os.path.join(self.directory, new_name)

                    if old_path == new_path:
                        continue 
                    
                    if not os.path.exists(old_path):
                        errors.append(f"'{original_name}' not found.")
                        continue
                    
                    if os.path.exists(new_path):
                        errors.append(f"A file named '{new_name}' already exists. Skipping '{original_name}'.")
                        continue

                    os.rename(old_path, new_path)
                    renamed_count += 1
                    self.file_list.delete(item_id)
                except Exception as e:
                    errors.append(f"Could not rename '{original_name}': {e}")
            
            summary_message = f"{renamed_count} files were successfully renamed."
            if errors:
                summary_message += "\n\nThe following errors occurred:\n" + "\n".join(errors)
            
            messagebox.showinfo("Rename Complete", summary_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = RenamerApp(root)
    root.mainloop()