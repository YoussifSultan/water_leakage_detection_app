from tkinter import messagebox
import tkinter as tk


class Pipe:
    def __init__(self, canvas, x1, y1, x2, y2, pipe_id, delete_callback=None,moisture=0):
        self.canvas = canvas
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.id = pipe_id
        self.moisture = moisture  # Add this
        self.delete_callback = delete_callback  # <-- this line is important
        self.line = canvas.create_line(
            x1, y1, x2, y2,
            fill=self.get_gradient_color(),  # white pipe
            width=6,
            capstyle=tk.ROUND
        )
        self.start_circle = canvas.create_oval(
            x1-4, y1-4, x1+4, y1+4,
            fill=self.get_gradient_color(), outline=""
        )
        self.end_circle = canvas.create_oval(
            x2-4, y2-4, x2+4, y2+4,
            fill=self.get_gradient_color(), outline=""
        )
        self.label = self.canvas.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2 - 10,
            text=f"{self.moisture}%",
            font=("Segoe UI", 10, "bold"),
            fill="gray"
        )
        # self.line = canvas.create_line(x1, y1, x2, y2, fill="#ffffff", width=8, arrow=tk.LAST, capstyle=tk.ROUND)

        canvas.tag_bind(self.line, "<Button-1>", self.show_info)

    def get_gradient_color(self):
        # """Fade from blue (0%) to red (100%) with no purple"""
        moisture = max(0, min(100, self.moisture))  # Clamp value
        red = int(255 * (moisture / 100))
        green =  int(255 * (1 - (moisture / 100)))
        blue =0
        return f"#{red:02x}{green:02x}{blue:02x}"

    def update_moisture(self, new_value):
       self.moisture = new_value
       self.canvas.itemconfig(self.label, text=f"{self.moisture}%")
       self.canvas.itemconfig(self.start_circle, fill=self.get_gradient_color())
       self.canvas.itemconfig(self.end_circle, fill=self.get_gradient_color())
       self.canvas.itemconfig(self.line, fill=self.get_gradient_color())

    def show_info(self, event=None):
        # Create a dialog window
        info_win = tk.Toplevel()
        info_win.title(f"Pipe #{self.id}")
        info_win.geometry("280x180")
        info_win.configure(bg="#f9fafb")
        info_win.resizable(False, False)

        # Info labels
        tk.Label(info_win, text=f"🆔 Pipe ID: {self.id}", font=("Segoe UI", 11, "bold"), bg="#f9fafb").pack(pady=(15, 5))
        tk.Label(info_win, text=f"Start: ({self.x1}, {self.y1})", font=("Segoe UI", 10), bg="#f9fafb").pack()
        tk.Label(info_win, text=f"End:   ({self.x2}, {self.y2})", font=("Segoe UI", 10), bg="#f9fafb").pack()

        # Delete button
        delete_btn = tk.Button(
            info_win,
            text="🗑️ Delete Pipe",
            bg="#dc2626",
            fg="white",
            font=("Segoe UI", 10),
            relief="flat",
            activebackground="#b91c1c",
            activeforeground="white",
            command=lambda: self.delete(info_win)
        )
        delete_btn.pack(pady=20)

    def delete(self, window):
        self.canvas.delete(self.line)
        window.destroy()
