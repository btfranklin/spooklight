import tkinter as tk
from tkinter import filedialog, ttk

class SpooklightApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Spooklight")
        self.root.geometry("600x400")

        self.story_concept = tk.StringVar()
        self.starting_image_path = tk.StringVar()

        self._setup_ui()

    def _setup_ui(self):
        # Configure grid weight
        self.root.columnconfigure(0, weight=1)

        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)

        # Story Concept
        ttk.Label(main_frame, text="Story Concept:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.concept_entry = ttk.Entry(main_frame, textvariable=self.story_concept, width=50)
        self.concept_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

        # Image Selection
        ttk.Label(main_frame, text="Starting Image (Optional):").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        image_frame = ttk.Frame(main_frame)
        image_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(image_frame, text="Choose Image...", command=self._choose_image).pack(side=tk.LEFT, padx=(0, 10))
        self.image_label = ttk.Label(image_frame, textvariable=self.starting_image_path)
        self.image_label.pack(side=tk.LEFT)

        # Start Button (Placeholder)
        ttk.Button(main_frame, text="Start Story", command=self._start_story).grid(row=2, column=0, columnspan=2, pady=(20, 0))

    def _choose_image(self):
        filename = filedialog.askopenfilename(
            title="Select Starting Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.starting_image_path.set(filename)

    def _start_story(self):
        print(f"Starting story with concept: {self.story_concept.get()}")
        print(f"Starting image: {self.starting_image_path.get()}")
