"""
ui/visualizer.py

Defines a Tkinter UI to visualize progress of each AI agent with 8-bit avatar animation,
progress bars, status labels, a real-time conversation log, and a right-side control panel
for Accept/Redo (and future) buttons.
"""

import tkinter as tk
from tkinter import ttk
import queue
from ui.avatars import AVATAR_PATTERNS, build_avatar_image


class AgentVisualizer(tk.Tk):
    def __init__(self, agents, pixel_size=16, log_poll_interval=100, anim_interval=1000):
        super().__init__()
        self.title("AI Agents Progress Visualizer")
        self.geometry("800x550")  # wider to accommodate control panel

        # Data structures
        self.progress_bars = {}
        self.status_labels = {}
        self.avatar_labels = {}
        self.anim_frames = {}
        self.current_frame = {}
        self.active_agent = None
        self.log_queue = queue.Queue()

        # Buttons container and controls
        self.control_frame = None
        self.manual_run_button = None
        self.auto_run_button = None
        self.accept_button = None
        self.redo_button = None

        # Build UI: left main + right controls
        self._build_main_ui(agents, pixel_size)
        self._build_control_panel()

        # Start polling and animation
        self.after(log_poll_interval, self._poll_log_queue)
        self.after(anim_interval, self._animate)
        self.log_poll_interval = log_poll_interval
        self.anim_interval = anim_interval

    def _build_main_ui(self, agents, pixel_size):
        # Main frame holds avatars, logs
        main_frame = tk.Frame(self)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header
        header = tk.Label(main_frame, text="AI Agents Progress", font=("Arial", 16, "bold"))
        header.pack(pady=10)

        # Agents frame
        container = tk.Frame(main_frame)
        container.pack(fill=tk.X, padx=20)

        for agent in agents:
            frame = tk.Frame(container)
            frame.pack(fill=tk.X, pady=5)

            patterns = AVATAR_PATTERNS.get(agent, [])
            frames = [build_avatar_image(pat, pixel_size) for pat in patterns]
            self.anim_frames[agent] = frames or [None]
            self.current_frame[agent] = 0

            img = frames[0] if frames else None
            avatar_lbl = tk.Label(frame, image=img)
            avatar_lbl.image = img
            avatar_lbl.pack(side=tk.LEFT, padx=(0, 10))
            self.avatar_labels[agent] = avatar_lbl

            name_lbl = tk.Label(frame, text=agent, width=15, anchor="w")
            name_lbl.pack(side=tk.LEFT)

            progress = ttk.Progressbar(frame, length=200, maximum=100)
            progress.pack(side=tk.LEFT, padx=10)
            self.progress_bars[agent] = progress

            status = tk.Label(frame, text="Pending", width=20, anchor="w")
            status.pack(side=tk.LEFT)
            self.status_labels[agent] = status

        # Separator
        sep = ttk.Separator(main_frame, orient='horizontal')
        sep.pack(fill=tk.X, pady=10)

        # Conversation log
        log_label = tk.Label(main_frame, text="Conversation Log:", font=("Arial", 12, "bold"))
        log_label.pack(anchor='w', padx=20)

        self.log_text = tk.Text(main_frame, height=10, wrap='word', state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def _build_control_panel(self):
        # Control panel on right side for action buttons
        self.control_frame = tk.Frame(self, width=200)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        # Title
        tk.Label(self.control_frame, text="Controls", font=("Arial", 14, "bold")).pack(pady=10)
        # Accept and Redo placeholders; actual buttons will be packed below

    def show_manual_run_button(self, callback):
        """
        Display a Manual Run button in the control panel. Invokes callback when clicked.
        """
        if self.manual_run_button:
            self.manual_run_button.destroy()
        self.manual_run_button = tk.Button(
            self.control_frame, text="Manual Run", command=callback
        )
        # Place at top of control panel under title
        self.manual_run_button.pack(pady=5)

    def disable_manual_run_button(self):
        """
        Remove the Manual Run button after use.
        """
        if self.manual_run_button:
            self.manual_run_button.destroy()
            self.manual_run_button = None

    def show_auto_run_button(self, callback):
        if self.auto_run_button:
            self.auto_run_button.destroy()
        self.auto_run_button = tk.Button(self.control_frame, text="Auto Run", command=callback)
        self.auto_run_button.pack(side=tk.LEFT, pady=5, padx=(5, 5))

    def disable_auto_run_button(self):
        if self.auto_run_button:
            self.auto_run_button.destroy()
            self.auto_run_button = None

    def update_progress(self, agent, percent, status_text, message=None):
        self.active_agent = agent
        if agent in self.progress_bars:
            self.progress_bars[agent]['value'] = percent
            self.status_labels[agent]['text'] = status_text
            self.update_idletasks()
        if message:
            self.log_queue.put((agent, message))

    def _poll_log_queue(self):
        try:
            while True:
                agent, msg = self.log_queue.get_nowait()
                self.log_text.configure(state='normal')
                self.log_text.insert(tk.END, f"[{agent}] {msg}\n")
                self.log_text.see(tk.END)
                self.log_text.configure(state='disabled')
        except queue.Empty:
            pass
        self.after(self.log_poll_interval, self._poll_log_queue)

    def _animate(self):
        if self.active_agent in self.avatar_labels:
            frames = self.anim_frames.get(self.active_agent, [])
            if len(frames) > 1:
                idx = (self.current_frame[self.active_agent] + 1) % len(frames)
                self.current_frame[self.active_agent] = idx
                img = frames[idx]
                lbl = self.avatar_labels[self.active_agent]
                lbl.configure(image=img)
                lbl.image = img
        self.after(self.anim_interval, self._animate)

    def show_accept_button(self, callback):
        # Place Accept in control panel
        if self.accept_button:
            self.accept_button.destroy()
        self.accept_button = tk.Button(self.control_frame, text="Accept Post", command=callback)
        self.accept_button.pack(pady=5)

    def disable_accept_button(self):
        if self.accept_button:
            self.accept_button.destroy()
            self.accept_button = None

    def show_redo_button(self, callback):
        # Place Redo in control panel above Accept
        if self.redo_button:
            self.redo_button.destroy()
        self.redo_button = tk.Button(self.control_frame, text="Redo Post", command=callback)
        self.redo_button.pack(pady=5)

    def disable_redo_button(self):
        if self.redo_button:
            self.redo_button.destroy()
            self.redo_button = None
