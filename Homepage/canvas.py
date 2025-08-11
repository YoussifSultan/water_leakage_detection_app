import tkinter as tk
from Homepage.pipe import Pipe


class PipeCanvas(tk.Canvas):
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pipes = []
        self.pipe_id_counter = 1
        self.vertex_mode = False
        self.first_click = None
        self.bind("<Button-1>", self.on_click)
        self.status_label = None  # Will be set by App
        self.undo_stack = []
        self.redo_stack = []
        # self.scale = 1.0  # Zoom level
        self.zoom_level = 1.0  # Initial zoom level
        self.offset_x = 0  # Pan offset
        self.offset_y = 0
        self.bind("<MouseWheel>", self.on_zoom)  # Windows
        self.bind("<Button-4>", self.on_zoom)    # Linux scroll up
        self.bind("<Button-5>", self.on_zoom)    # Linux scroll down


    def set_status_label(self, label):
        self.status_label = label

    def toggle_vertex_mode(self):
        self.vertex_mode = not self.vertex_mode
        self.first_click = None
        return self.vertex_mode

    def on_click(self, event):  
        if not self.vertex_mode:
            return

        x, y = event.x, event.y

        # Snap to nearby endpoint if close
        snapped = self.find_nearest_endpoint(x, y)
        if snapped:
            x, y = snapped
            self.update_status(f"Snapped to ({x}, {y})")

        if self.first_click is None:
            self.first_click = (x, y)
            self.update_status(f"Start point: ({x}, {y}) — now click the end point")
        else:
            x1, y1 = self.first_click
            x2, y2 = x, y
            pipe = Pipe(self, x1, y1, x2, y2, self.pipe_id_counter, moisture= 0,delete_callback=self.remove_pipe)
            self.pipes.append(pipe)
            self.undo_stack.append(pipe)
            self.redo_stack.clear()
            self.pipe_id_counter += 1

            self.first_click = None
            self.update_status("Pipe created. Click to start a new one.")

    def remove_pipe(self, pipe):
        if pipe in self.pipes:
            self.pipes.remove(pipe)
            self.update_status(f"Pipe {pipe.id} deleted.")

    def update_status(self, msg):
        if self.status_label:
            self.status_label.config(text=msg)

    def find_nearest_endpoint(self, x, y, radius=10):
        for pipe in self.pipes:
            for px, py in [(pipe.x1, pipe.y1), (pipe.x2, pipe.y2)]:
                if abs(px - x) <= radius and abs(py - y) <= radius:
                    return (px, py)
        return None

    def on_zoom(self, event):
        factor = 1.1 if event.delta > 0 or getattr(event, 'num', 0) == 4 else 0.9
    
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
    
        self.zoom_level *= factor
        self.zoom_level = max(0.2, min(5, self.zoom_level))  # Clamp zoom
    
        # ✅ This is calling the Canvas.scale method
        super().scale("all", x, y, factor, factor)
        self.configure(scrollregion=self.bbox("all"))

    def start_pan(self, event):
        self.scan_mark(event.x, event.y)

    def do_pan(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    def reset_view(self):
        self.zoom_level = 1.0
        self.zoom_level("all", 0, 0, 1.0, 1.0)
        self.configure(scrollregion=self.bbox("all"))
        self.xview_moveto(0)
        self.yview_moveto(0)

    def update_pipe(self, pipe_id, moisture):
        for pipe in self.pipes:
            if pipe.id == pipe_id:
                pipe.update_moisture(moisture)
                break

    def undo(self):
        if not self.undo_stack:
            self.update_status("Nothing to undo.")
            return

        pipe = self.undo_stack.pop()
        self.delete(pipe.line)
        self.delete(getattr(pipe, 'start_circle', ''))
        self.delete(pipe.label)  # 🧠 Delete the moisture label too

        self.delete(getattr(pipe, 'end_circle', ''))
        self.pipes.remove(pipe)
        self.redo_stack.append(pipe)
        self.update_status(f"Undo: Pipe {pipe.id} removed.")

    def redo(self):
        if not self.redo_stack:
            self.update_status("Nothing to redo.")
            return

        pipe = self.redo_stack.pop()
        pipe.line = self.create_line(
            pipe.x1, pipe.y1,pipe. x2, pipe.y2,
            fill=pipe.get_gradient_color(),  # white pipe
            width=6,
            capstyle=tk.ROUND
        )
        pipe.start_circle = self.create_oval(
            pipe.x1-4, pipe.y1-4, pipe.x1+4, pipe.y1+4,
            fill=pipe.get_gradient_color(), outline=""
        )
        pipe.end_circle = self.create_oval(
            pipe.x2-4, pipe.y2-4, pipe.x2+4, pipe.y2+4,
            fill=pipe.get_gradient_color(), outline=""
        )

        pipe.label = self.create_text(
            (pipe.x1 + pipe.x2) / 2, (pipe.y1 + pipe.y2) / 2 - 10,
            text=f"{pipe.moisture}%",
            font=("Segoe UI", 10, "bold"), fill="gray"
        )
        self.tag_bind(pipe.line, "<Button-1>", pipe.show_info)
        self.pipes.append(pipe)
        self.undo_stack.append(pipe)
        self.update_status(f"Redo: Pipe {pipe.id} restored.")


