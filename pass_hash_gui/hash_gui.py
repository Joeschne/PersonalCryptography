from hash_processing import HashProcessor
import tkinter as tk
from tkinter import messagebox

class HashingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hashing Application")
        self.root.geometry("800x500")  # Set fixed size to avoid resizing
        self.root.configure(bg="#282c34")  # Updated background color

        # Title Label
        self.title_label = tk.Label(
            root, text="Cool Hashing Tool", bg="#282c34", fg="#ffffff", font=("Helvetica", 20, "bold")
        )
        self.title_label.pack(pady=10)

        # Frame for Inputs
        self.input_frame = tk.Frame(root, bg="#282c34")
        self.input_frame.pack(pady=10)

        # Key Input
        self.key_label = tk.Label(self.input_frame, text="Key:", bg="#282c34", fg="#ffffff", font=("Helvetica", 12))
        self.key_label.grid(row=0, column=0, padx=5, pady=5)
        self.key_entry = tk.Entry(self.input_frame, width=40, bg="#e8e8e8", fg="#000000", font=("Helvetica", 12))
        self.key_entry.grid(row=0, column=1, padx=5, pady=5)

        # Input for Custom String
        self.custom_label = tk.Label(self.input_frame, text="Hash Input:", bg="#282c34", fg="#ffffff", font=("Helvetica", 12))
        self.custom_entry = tk.Entry(self.input_frame, width=40, bg="#e8e8e8", fg="#000000", font=("Helvetica", 12))
        self.custom_label.grid(row=2, column=0, padx=5, pady=5)
        self.custom_entry.grid(row=2, column=1, padx=5, pady=5)

        # Output Box
        self.output_label = tk.Label(root, text="Output:", bg="#282c34", fg="#ffffff", font=("Helvetica", 12))
        self.output_label.pack(pady=10)
        self.output_text = tk.Text(root, height=8, width=60, bg="#282c34", fg="#ffffff", font=("Helvetica", 12))
        self.output_text.pack(pady=5)

        # Hash Button
        self.hash_button = tk.Button(
            root,
            text="Generate Hash",
            bg="#4caf50",
            fg="#ffffff",
            font=("Helvetica", 14, "bold"),
            activebackground="#45a049",
            command=self.generate_hash,
        )
        self.hash_button.pack(pady=10)

    def generate_hash(self):
        """Generate the hash based on the inputs."""
        input_data = ""
        key = self.key_entry.get()
        if not key:
            messagebox.showerror("Error", "Key is required!")
            return
        
        input_data = self.custom_entry.get()
        if not input_data:
            messagebox.showerror("Error", "Custom String is required!")
            return
        initial_base = 2951
        try:
            output = HashProcessor.hash_input_data(key, input_data, initial_base, True)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"Hash: {output}")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating hash: {e}")



# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = HashingApp(root)
    root.mainloop()
