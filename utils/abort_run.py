import tkinter as tk
from tkinter import messagebox
from langsmith import Client
import os

def abort_run():
    run_id = run_id_entry.get().strip()
    api_key = api_key_entry.get().strip()

    if not run_id:
        messagebox.showerror("Error", "Please enter a Run ID.")
        return

    if api_key:
        os.environ["LANGCHAIN_API_KEY"] = api_key

    try:
        client = Client()
        client.update_run(run_id=run_id, status="aborted")
        messagebox.showinfo("Success", f"Run {run_id} has been aborted.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to abort run:\n{e}")

root = tk.Tk()
root.title("Stop LangSmith Run")

tk.Label(root, text="LangChain API Key (optional if set in env):").pack(pady=(10, 0))
api_key_entry = tk.Entry(root, show="*", width=50)
api_key_entry.pack(padx=10, pady=5)

tk.Label(root, text="Run ID:").pack(pady=(10, 0))
run_id_entry = tk.Entry(root, width=50)
run_id_entry.pack(padx=10, pady=5)

abort_button = tk.Button(root, text="Abort Run", command=abort_run, bg="red", fg="white")
abort_button.pack(pady=15)

root.mainloop()
