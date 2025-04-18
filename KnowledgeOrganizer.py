import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import datetime
from collections import defaultdict
import random
import webbrowser

class SpacedRepetitionCalculator:
    """Implements a simple spaced repetition algorithm"""
    def __init__(self):
        self.intervals = [1, 3, 7, 14, 30, 60]  # Days between reviews
    
    def next_review_date(self, current_streak):
        if current_streak >= len(self.intervals):
            return datetime.date.today() + datetime.timedelta(days=self.intervals[-1])
        return datetime.date.today() + datetime.timedelta(days=self.intervals[current_streak])

class KnowledgeOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Knowledge Organizer")
        self.root.geometry("1000x700")
        
        # Initialize data structures
        self.notes = []
        self.tags = set()
        self.note_id_counter = 1
        self.spaced_rep = SpacedRepetitionCalculator()
        
        # Load previous data if available
        self.load_data()
        
        # Create GUI
        self.create_widgets()
        
        # Display initial note
        self.display_random_note_for_review()
        
    def create_widgets(self):
        # Main frames
        self.left_frame = ttk.Frame(self.root, width=300)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left frame - Navigation and controls
        ttk.Label(self.left_frame, text="Knowledge Organizer", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Review section
        review_frame = ttk.LabelFrame(self.left_frame, text="Spaced Repetition")
        review_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(review_frame, text="Show Random Note", command=self.display_random_note_for_review).pack(fill=tk.X)
        ttk.Button(review_frame, text="Today's Review Notes", command=self.show_todays_review_notes).pack(fill=tk.X, pady=5)
        
        # Search section
        search_frame = ttk.LabelFrame(self.left_frame, text="Search")
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)
        self.search_entry.bind('<Return>', lambda e: self.search_notes())
        
        ttk.Button(search_frame, text="Search", command=self.search_notes).pack(fill=tk.X)
        
        # Tags filter
        tags_frame = ttk.LabelFrame(self.left_frame, text="Filter by Tags")
        tags_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.tag_filter_var = tk.StringVar()
        self.tag_filter = ttk.Combobox(tags_frame, textvariable=self.tag_filter_var, values=sorted(self.tags))
        self.tag_filter.pack(fill=tk.X, padx=5, pady=5)
        self.tag_filter.bind('<<ComboboxSelected>>', lambda e: self.filter_by_tag())
        
        # Stats section
        stats_frame = ttk.LabelFrame(self.left_frame, text="Statistics")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="")
        self.stats_label.pack()
        self.update_stats()
        
        # Right frame - Note display and editing
        self.note_display_frame = ttk.Frame(self.right_frame)
        self.note_display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Note viewing controls
        control_frame = ttk.Frame(self.right_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="New Note", command=self.new_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Edit Note", command=self.edit_current_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Delete Note", command=self.delete_current_note).pack(side=tk.LEFT, padx=5)
        
        # Review buttons
        review_btn_frame = ttk.Frame(self.right_frame)
        review_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(review_btn_frame, text="Easy", command=lambda: self.review_feedback('easy')).pack(side=tk.LEFT, expand=True)
        ttk.Button(review_btn_frame, text="Good", command=lambda: self.review_feedback('good')).pack(side=tk.LEFT, expand=True)
        ttk.Button(review_btn_frame, text="Hard", command=lambda: self.review_feedback('hard')).pack(side=tk.LEFT, expand=True)
        
        # Menu bar
        self.create_menu_bar()
        
        # Initialize note display
        self.current_note_id = None
        self.init_note_display()
        
    def init_note_display(self):
        for widget in self.note_display_frame.winfo_children():
            widget.destroy()
            
        self.title_label = ttk.Label(self.note_display_frame, text="", font=('Helvetica', 16, 'bold'))
        self.title_label.pack(pady=10)
        
        self.tags_label = ttk.Label(self.note_display_frame, text="", font=('Helvetica', 10))
        self.tags_label.pack()
        
        self.content_text = tk.Text(self.note_display_frame, wrap=tk.WORD, font=('Helvetica', 12), padx=10, pady=10)
        self.content_text.pack(fill=tk.BOTH, expand=True)
        self.content_text.config(state=tk.DISABLED)
        
        self.metadata_label = ttk.Label(self.note_display_frame, text="", font=('Helvetica', 8))
        self.metadata_label.pack()
        
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Note", command=self.new_note)
        file_menu.add_command(label="Export Notes", command=self.export_notes)
        file_menu.add_command(label="Import Notes", command=self.import_notes)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
    def display_note(self, note):
        self.current_note_id = note['id']
        
        self.title_label.config(text=note['title'])
        self.tags_label.config(text="Tags: " + ", ".join(note['tags']))
        
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, note['content'])
        self.content_text.config(state=tk.DISABLED)
        
        metadata = f"Created: {note['created']} | Last Reviewed: {note['last_reviewed']} | Next Review: {note['next_review']} | Strength: {note['streak']}"
        self.metadata_label.config(text=metadata)
        
    def new_note(self):
        self.current_note_id = None
        
        # Create a new window for editing
        edit_window = tk.Toplevel(self.root)
        edit_window.title("New Note")
        edit_window.geometry("800x600")
        
        # Title
        ttk.Label(edit_window, text="Title:").pack(pady=(10, 0))
        title_entry = ttk.Entry(edit_window, width=80)
        title_entry.pack(padx=10)
        
        # Tags
        ttk.Label(edit_window, text="Tags (comma separated):").pack(pady=(10, 0))
        tags_entry = ttk.Entry(edit_window, width=80)
        tags_entry.pack(padx=10)
        
        # Content
        ttk.Label(edit_window, text="Content:").pack(pady=(10, 0))
        content_text = tk.Text(edit_window, wrap=tk.WORD, height=20, padx=10, pady=10)
        content_text.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Save button
        def save_note():
            title = title_entry.get().strip()
            tags = [tag.strip() for tag in tags_entry.get().split(',') if tag.strip()]
            content = content_text.get("1.0", tk.END).strip()
            
            if not title or not content:
                messagebox.showerror("Error", "Title and content cannot be empty")
                return
                
            note_data = {
                'id': self.note_id_counter,
                'title': title,
                'tags': tags,
                'content': content,
                'created': datetime.date.today().isoformat(),
                'last_reviewed': datetime.date.today().isoformat(),
                'next_review': (datetime.date.today() + datetime.timedelta(days=1)).isoformat(),
                'streak': 0
            }
            
            self.notes.append(note_data)
            self.note_id_counter += 1
            self.update_tags()
            self.update_stats()
            edit_window.destroy()
            self.display_note(note_data)
            
        ttk.Button(edit_window, text="Save Note", command=save_note).pack(pady=10)
        
    def edit_current_note(self):
        if not self.current_note_id:
            messagebox.showinfo("Info", "No note selected")
            return
            
        note = next((n for n in self.notes if n['id'] == self.current_note_id), None)
        if not note:
            return
            
        # Create a new window for editing
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Note")
        edit_window.geometry("800x600")
        
        # Title
        ttk.Label(edit_window, text="Title:").pack(pady=(10, 0))
        title_entry = ttk.Entry(edit_window, width=80)
        title_entry.insert(0, note['title'])
        title_entry.pack(padx=10)
        
        # Tags
        ttk.Label(edit_window, text="Tags (comma separated):").pack(pady=(10, 0))
        tags_entry = ttk.Entry(edit_window, width=80)
        tags_entry.insert(0, ", ".join(note['tags']))
        tags_entry.pack(padx=10)
        
        # Content
        ttk.Label(edit_window, text="Content:").pack(pady=(10, 0))
        content_text = tk.Text(edit_window, wrap=tk.WORD, height=20, padx=10, pady=10)
        content_text.insert(tk.END, note['content'])
        content_text.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Save button
        def save_note():
            title = title_entry.get().strip()
            tags = [tag.strip() for tag in tags_entry.get().split(',') if tag.strip()]
            content = content_text.get("1.0", tk.END).strip()
            
            if not title or not content:
                messagebox.showerror("Error", "Title and content cannot be empty")
                return
                
            note['title'] = title
            note['tags'] = tags
            note['content'] = content
            self.update_tags()
            edit_window.destroy()
            self.display_note(note)
            
        ttk.Button(edit_window, text="Save Changes", command=save_note).pack(pady=10)
        
    def delete_current_note(self):
        if not self.current_note_id:
            messagebox.showinfo("Info", "No note selected")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this note?"):
            self.notes = [n for n in self.notes if n['id'] != self.current_note_id]
            self.current_note_id = None
            self.update_tags()
            self.update_stats()
            self.init_note_display()
            messagebox.showinfo("Info", "Note deleted")
            
    def search_notes(self):
        query = self.search_entry.get().lower()
        if not query:
            return
            
        results = []
        for note in self.notes:
            if (query in note['title'].lower() or 
                query in note['content'].lower() or 
                any(query in tag.lower() for tag in note['tags'])):
                results.append(note)
                
        if not results:
            messagebox.showinfo("Search Results", "No notes found matching your search")
            return
            
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Search Results for '{query}'")
        results_window.geometry("800x600")
        
        tree = ttk.Treeview(results_window, columns=('Title', 'Tags'), show='headings')
        tree.heading('Title', text='Title')
        tree.heading('Tags', text='Tags')
        tree.column('Title', width=400)
        tree.column('Tags', width=200)
        
        for note in results:
            tree.insert('', tk.END, values=(note['title'], ", ".join(note['tags'])), tags=(note['id'],))
            
        tree.pack(fill=tk.BOTH, expand=True)
        
        def on_select(event):
            item = tree.focus()
            note_id = int(tree.item(item, 'tags')[0])
            note = next(n for n in self.notes if n['id'] == note_id)
            self.display_note(note)
            results_window.destroy()
            
        tree.bind('<Double-1>', on_select)
        
    def filter_by_tag(self):
        tag = self.tag_filter_var.get()
        if not tag:
            return
            
        filtered_notes = [n for n in self.notes if tag in n['tags']]
        
        if not filtered_notes:
            messagebox.showinfo("Filter Results", f"No notes found with tag '{tag}'")
            return
            
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Notes with tag '{tag}'")
        results_window.geometry("800x600")
        
        tree = ttk.Treeview(results_window, columns=('Title', 'Tags'), show='headings')
        tree.heading('Title', text='Title')
        tree.heading('Tags', text='Tags')
        tree.column('Title', width=400)
        tree.column('Tags', width=200)
        
        for note in filtered_notes:
            tree.insert('', tk.END, values=(note['title'], ", ".join(note['tags'])), tags=(note['id'],))
            
        tree.pack(fill=tk.BOTH, expand=True)
        
        def on_select(event):
            item = tree.focus()
            note_id = int(tree.item(item, 'tags')[0])
            note = next(n for n in self.notes if n['id'] == note_id)
            self.display_note(note)
            results_window.destroy()
            
        tree.bind('<Double-1>', on_select)
        
    def display_random_note_for_review(self):
        if not self.notes:
            messagebox.showinfo("Info", "No notes available for review")
            return
            
        # Filter notes that are due for review
        today = datetime.date.today().isoformat()
        due_notes = [n for n in self.notes if n['next_review'] <= today]
        
        if due_notes:
            note = random.choice(due_notes)
        else:
            note = random.choice(self.notes)
            
        self.display_note(note)
        
    def show_todays_review_notes(self):
        today = datetime.date.today().isoformat()
        due_notes = [n for n in self.notes if n['next_review'] <= today]
        
        if not due_notes:
            messagebox.showinfo("Today's Review", "No notes are due for review today")
            return
            
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title("Today's Review Notes")
        results_window.geometry("800x600")
        
        tree = ttk.Treeview(results_window, columns=('Title', 'Next Review', 'Strength'), show='headings')
        tree.heading('Title', text='Title')
        tree.heading('Next Review', text='Next Review')
        tree.heading('Strength', text='Strength')
        tree.column('Title', width=400)
        tree.column('Next Review', width=150)
        tree.column('Strength', width=100)
        
        for note in sorted(due_notes, key=lambda x: x['next_review']):
            tree.insert('', tk.END, values=(note['title'], note['next_review'], note['streak']), tags=(note['id'],))
            
        tree.pack(fill=tk.BOTH, expand=True)
        
        def on_select(event):
            item = tree.focus()
            note_id = int(tree.item(item, 'tags')[0])
            note = next(n for n in self.notes if n['id'] == note_id)
            self.display_note(note)
            results_window.destroy()
            
        tree.bind('<Double-1>', on_select)
        
    def review_feedback(self, feedback):
        if not self.current_note_id:
            messagebox.showinfo("Info", "No note selected")
            return
            
        note = next((n for n in self.notes if n['id'] == self.current_note_id), None)
        if not note:
            return
            
        today = datetime.date.today()
        
        # Update note based on feedback
        if feedback == 'easy':
            note['streak'] += 2
        elif feedback == 'good':
            note['streak'] += 1
        else:  # hard
            note['streak'] = max(0, note['streak'] - 1)
            
        note['last_reviewed'] = today.isoformat()
        note['next_review'] = self.spaced_rep.next_review_date(note['streak']).isoformat()
        
        self.display_note(note)
        self.update_stats()
        
    def update_tags(self):
        self.tags = set()
        for note in self.notes:
            self.tags.update(note['tags'])
            
        self.tag_filter['values'] = sorted(self.tags)
        
    def update_stats(self):
        total_notes = len(self.notes)
        total_tags = len(self.tags)
        
        today = datetime.date.today().isoformat()
        due_reviews = len([n for n in self.notes if n['next_review'] <= today])
        
        avg_streak = sum(n['streak'] for n in self.notes) / total_notes if total_notes > 0 else 0
        
        stats_text = (f"Total Notes: {total_notes}\n"
                     f"Total Tags: {total_tags}\n"
                     f"Due Reviews: {due_reviews}\n"
                     f"Avg. Strength: {avg_streak:.1f}")
                     
        self.stats_label.config(text=stats_text)
        
    def export_notes(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        data = {
            'notes': self.notes,
            'note_id_counter': self.note_id_counter
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "Notes exported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export notes: {str(e)}")
            
    def import_notes(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            if not all(key in data for key in ['notes', 'note_id_counter']):
                raise ValueError("Invalid data format")
                
            self.notes = data['notes']
            self.note_id_counter = data['note_id_counter']
            self.update_tags()
            self.update_stats()
            self.current_note_id = None
            self.init_note_display()
            messagebox.showinfo("Success", "Notes imported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import notes: {str(e)}")
            
    def load_data(self):
        try:
            with open('knowledge_organizer_data.json', 'r') as f:
                data = json.load(f)
                
            self.notes = data.get('notes', [])
            self.note_id_counter = data.get('note_id_counter', 1)
            self.update_tags()
        except FileNotFoundError:
            self.notes = []
            self.note_id_counter = 1
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.notes = []
            self.note_id_counter = 1
            
    def save_data(self):
        data = {
            'notes': self.notes,
            'note_id_counter': self.note_id_counter
        }
        
        try:
            with open('knowledge_organizer_data.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
            
    def show_about(self):
        about_text = ("Personal Knowledge Organizer\n"
                     "Version 1.0\n\n"
                     "A tool to organize your knowledge and implement\n"
                     "spaced repetition for effective learning.")
        messagebox.showinfo("About", about_text)
        
    def show_documentation(self):
        docs_url = "https://en.wikipedia.org/wiki/Spaced_repetition"
        webbrowser.open_new_tab(docs_url)
        
    def on_closing(self):
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = KnowledgeOrganizer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()