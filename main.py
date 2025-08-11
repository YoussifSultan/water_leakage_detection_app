import tkinter as tk
from Homepage.canvas import PipeCanvas

from tkinter import  font

from threading import Thread
from Homepage.esp32_connection import create_server
import queue

# Create a global queue to share with Flask
update_queue = queue.Queue()


app = create_server(update_queue)
flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000), daemon=True)
flask_thread.start()


class App:
    def check_updates(self):
        while not update_queue.empty():
            pipe_id, moisture = update_queue.get()
            self.pipe_canvas.update_pipe(pipe_id, moisture)
        self.root.after(100, self.check_updates)  # Keep polling

    def __init__(self, root):
        self.root = root
        self.root.title("🚰 Pipe Layout Designer")
        self.root.geometry("1000x650")
        self.root.configure(bg="#0f172a")

        self.custom_font = font.Font(family="Segoe UI", size=11)

        self.canvas_frame = tk.Frame(self.root, bg="#0f172a", padx=15, pady=15)
        self.canvas_frame.pack()

        self.pipe_canvas = PipeCanvas(
            self.canvas_frame,
            bg="#0a2540",
            width=850,
            height=500,
            bd=0,
            highlightthickness=3,
            highlightbackground="#38bdf8"
        )
        self.pipe_canvas.pack()
        self.root.bind("<Control-z>", lambda e: self.pipe_canvas.undo())
        self.root.bind("<Control-y>", lambda e: self.pipe_canvas.redo())
        self.toggle_btn = tk.Button(
            self.root,
            text="➕ Add Pipe",
            command=self.toggle_mode,
            bg="#0ea5e9",
            fg="white",
            font=self.custom_font,
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        self.toggle_btn.place(relx=1.0, rely=1.0, x=-30, y=-30, anchor="se")
        btn_frame = tk.Frame(self.root, bg="#0f172a")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="↩ Undo", command=self.pipe_canvas.undo,
                  bg="#334155", fg="white", font=self.custom_font).pack(side="left", padx=5)
        tk.Button(btn_frame, text="↪ Redo", command=self.pipe_canvas.redo,
          bg="#334155", fg="white", font=self.custom_font).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🔄 Reset View", command=self.pipe_canvas.reset_view,
          bg="#334155", fg="white", font=self.custom_font).pack(side="left", padx=5)


        self.status = tk.Label(
            self.root,
            text="Mode: Normal",
            bg="#1e293b",
            fg="white",
            font=("Segoe UI", 10),
            anchor="w",
            relief="flat"
        )
        self.status.pack(fill="x", side="bottom")

        self.pipe_canvas.set_status_label(self.status)
        self.root.after(100, self.check_updates)

    def toggle_mode(self):
        mode_on = self.pipe_canvas.toggle_vertex_mode()
        if mode_on:
            self.toggle_btn.config(text="✅ Drawing Mode", bg="#16a34a")
            self.pipe_canvas.config(cursor="crosshair")
            self.status.config(text="Mode: Add Pipe (click start and end points)")
        else:
            self.toggle_btn.config(text="➕ Add Pipe", bg="#0ea5e9")
            self.pipe_canvas.config(cursor="")
            self.status.config(text="Mode: Normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()