"""
ui/visualizer.py

Defines a Tkinter UI to visualize progress of each AI agent with 8-bit animated avatars,
progress bars, status labels, and a real-time conversation log textbox.
Each avatar has two frames that alternate when the agent is active.
"""

import tkinter as tk
from tkinter import ttk
import queue
from ui.avatars import AVATAR_PATTERNS, build_avatar_image


class AgentVisualizer(tk.Tk):
    def __init__(self, agents, pixel_size=16, log_poll_interval=100, anim_interval=1000):
        super().__init__()
        self.title("AI Agents Progress Visualizer")
        self.geometry("600x450")

        # Data structures
        self.progress_bars = {}
        self.status_labels = {}
        self.avatar_labels = {}
        self.anim_frames = {}          # holds [frame1, frame2] per agent
        self.current_frame = {}        # current index (0 or 1) per agent
        self.active_agent = None       # name of agent currently animating
        self.log_queue = queue.Queue() # Thread-safe queue for log messages

        # Accept button (hidden until needed)
        self.button_frame = None
        self.accept_button = None
        self.redo_button = None

        # Build UI and start loops
        self._build_ui(agents, pixel_size)
        self.after(log_poll_interval, self._poll_log_queue)
        self.after(anim_interval, self._animate)
        self.log_poll_interval = log_poll_interval
        self.anim_interval = anim_interval

    def _build_ui(self, agents, pixel_size):
        # Header
        header = tk.Label(self, text="AI Agents Progress", font=("Arial", 16, "bold"))
        header.pack(pady=10)

        # Agents frame
        container = tk.Frame(self)
        container.pack(fill=tk.X, padx=20)

        for agent in agents:
            frame = tk.Frame(container)
            frame.pack(fill=tk.X, pady=5)

            # Build two animation frames per agent
            patterns = AVATAR_PATTERNS.get(agent, [])
            # expect patterns to be [pattern1, pattern2]
            frames = []
            for pat in patterns:
                frames.append(build_avatar_image(pat, pixel_size))
            if not frames:
                frames = [None]
            self.anim_frames[agent] = frames
            self.current_frame[agent] = 0

            # Avatar label, start with first frame
            img = frames[0]
            avatar_lbl = tk.Label(frame, image=img)
            avatar_lbl.image = img
            avatar_lbl.pack(side=tk.LEFT, padx=(0, 10))
            self.avatar_labels[agent] = avatar_lbl

            # Agent name label
            name_lbl = tk.Label(frame, text=agent, width=15, anchor="w")
            name_lbl.pack(side=tk.LEFT)

            # Progress bar
            progress = ttk.Progressbar(frame, length=200, maximum=100)
            progress.pack(side=tk.LEFT, padx=10)
            self.progress_bars[agent] = progress

            # Status label
            status = tk.Label(frame, text="Pending", width=20, anchor="w")
            status.pack(side=tk.LEFT)
            self.status_labels[agent] = status

        # Separator
        sep = ttk.Separator(self, orient='horizontal')
        sep.pack(fill=tk.X, pady=10)

        # Conversation log label & box
        log_label = tk.Label(self, text="Conversation Log:", font=("Arial", 12, "bold"))
        log_label.pack(anchor='w', padx=20)
        self.log_text = tk.Text(self, height=10, wrap='word', state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def update_progress(self, agent, percent, status_text, message=None):
        """
        Update progress bar/status, enqueue a log message, and mark agent as active.
        """
        # Activate agent for animation
        self.active_agent = agent

        # Update progress bar and status label
        if agent in self.progress_bars:
            self.progress_bars[agent]['value'] = percent
            self.status_labels[agent]['text'] = status_text
            self.update_idletasks()

        # Enqueue log message
        if message:
            self.log_queue.put((agent, message))

    def _poll_log_queue(self):
        """Poll and render log messages."""
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
        """
        Toggle avatar frame for the active agent at a fixed interval.
        """
        if self.active_agent and self.active_agent in self.avatar_labels:
            agent = self.active_agent
            frames = self.anim_frames.get(agent, [])
            if len(frames) > 1:
                # compute next frame index
                idx = (self.current_frame[agent] + 1) % len(frames)
                self.current_frame[agent] = idx
                img = frames[idx]
                lbl = self.avatar_labels[agent]
                lbl.configure(image=img)
                lbl.image = img
        # schedule next animation tick
        self.after(self.anim_interval, self._animate)

    def _ensure_button_frame(self):
        """
        Create a container frame for Accept and Redo buttons if not existing.
        """
        if self.button_frame is None:
            self.button_frame = tk.Frame(self)
            self.button_frame.pack(pady=(0, 10))

    def show_accept_button(self, callback):
        """
        Display an Accept button. Invokes callback when clicked.
        """
        self._ensure_button_frame()
        # Remove existing, to ensure fresh pack
        if self.accept_button:
            self.accept_button.destroy()
        self.accept_button = tk.Button(
            self.button_frame, text="Accept Post", command=callback
        )
        # pack to the right
        self.accept_button.pack(side=tk.RIGHT, padx=(5, 0))

    def disable_accept_button(self):
        """
        Disable and hide the Accept button after user click.
        """
        if self.accept_button:
            self.accept_button.destroy()
            self.accept_button = None

    def show_redo_button(self, callback):
        """
        Display a Redo button to the left of Accept. Invokes callback when clicked.
        """
        self._ensure_button_frame()
        # Remove existing, to ensure fresh pack
        if self.redo_button:
            self.redo_button.destroy()
        self.redo_button = tk.Button(
            self.button_frame, text="Redo Post", command=callback
        )
        # pack to the left
        self.redo_button.pack(side=tk.LEFT, padx=(0, 5))

    def disable_redo_button(self):
        """
        Disable and hide the Redo button after use.
        """
        if self.redo_button:
            self.redo_button.destroy()
            self.redo_button = None
