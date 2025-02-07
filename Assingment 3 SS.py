import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np

class ImageProcessorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HIT137 Group Assignment 3 - Image Processor")
        self.geometry("1000x700")
        self.configure(bg="lightgray")

        # Let's get the images sorted, eh?
        self.image = None  # Original image
        self.processed_image = None  # This is what we're messing with
        self.display_image = None # For showing on the GUI
        self.history = []  # Keeping track of changes
        self.history_index = -1  # Where we are in history
        self.crop_start = None  # Where the crop starts
        self.crop_end = None  # Where the crop ends
        self.cropping = False  # Are we cropping?
        self.crop_rectangle = None # The outline

        self.initUI()
        self.bind_shortcuts()

    def initUI(self):
        # Frame for the controls - buttons and stuff
        self.control_frame = tk.Frame(self, bg="lightgray")
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Load Image Button
        self.load_button = tk.Button(self.control_frame, text="Load Image (Ctrl+O)", bg="#4CAF50", fg="white",
                                     font=("Arial", 12), command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Crop Image Button
        self.crop_button = tk.Button(self.control_frame, text="Crop Image (Ctrl+X)", bg="#FF9800", fg="white",
                                     font=("Arial", 12), command=self.enable_cropping)
        self.crop_button.pack(side=tk.LEFT, padx=5)

        # Resize Slider - because why not?
        self.resize_slider = tk.Scale(self.control_frame, from_=10, to=200, orient=tk.HORIZONTAL,
                                      label="Resize (%)", font=("Arial", 12), command=self.resize_image)
        self.resize_slider.set(100)
        self.resize_slider.pack(side=tk.LEFT, padx=5)

        # Rotate Button - for fun
        self.rotate_button = tk.Button(self.control_frame, text="Rotate 90° (Ctrl+R)", bg="#9C27B0", fg="white",
                                       font=("Arial", 12), command=self.rotate_image)
        self.rotate_button.pack(side=tk.LEFT, padx=5)

        # Flip Button - another fun one
        self.flip_button = tk.Button(self.control_frame, text="Flip Horizontal (Ctrl+F)", bg="#795548", fg="white",
                                     font=("Arial", 12), command=self.flip_image)
        self.flip_button.pack(side=tk.LEFT, padx=5)

        # Save Image Button - gotta save our masterpieces!
        self.save_button = tk.Button(self.control_frame, text="Save Image (Ctrl+S)", bg="#2196F3", fg="white",
                                     font=("Arial", 12), command=self.save_image)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Undo/Redo Buttons - for when we mess up (and we will!)
        self.undo_button = tk.Button(self.control_frame, text="Undo (Ctrl+Z)", bg="#9E9E9E", fg="white",
                                     font=("Arial", 12), command=self.undo_action, state=tk.DISABLED)
        self.undo_button.pack(side=tk.LEFT, padx=5)

        self.redo_button = tk.Button(self.control_frame, text="Redo (Ctrl+Y)", bg="#9E9E9E", fg="white",
                                     font=("Arial", 12), command=self.redo_action, state=tk.DISABLED)
        self.redo_button.pack(side=tk.LEFT, padx=5)

        # Image Frame - where the magic happens
        self.image_frame = tk.Frame(self, bg="white")
        self.image_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas - for drawing the image and crop outline
        self.canvas = tk.Canvas(self.image_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind some mouse events
        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.draw_crop_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)

    def bind_shortcuts(self):
        # Bind some handy shortcuts
        self.bind("<Control-o>", lambda event: self.load_image())
        self.bind("<Control-x>", lambda event: self.enable_cropping())
        self.bind("<Control-r>", lambda event: self.rotate_image())
        self.bind("<Control-f>", lambda event: self.flip_image())
        self.bind("<Control-s>", lambda event: self.save_image())
        self.bind("<Control-z>", lambda event: self.undo_action())
        self.bind("<Control-y>", lambda event: self.redo_action())

    def load_image(self):
        # Load an image from a file
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if file_path:
            try:
                self.image = cv2.imread(file_path)
                if self.image is None:
                    raise ValueError("Could not read image")
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                self.processed_image = self.image.copy()
                self.add_to_history(self.processed_image)
                self.show_image()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def show_image(self):
        # Display the image on the canvas
        if self.processed_image is not None:
            img = Image.fromarray(self.processed_image)
            img.thumbnail((800, 500), Image.LANCZOS)
            self.display_image = img # keep a reference
            self.photo = ImageTk.PhotoImage(img)
            self.canvas.config(width=img.width, height=img.height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def enable_cropping(self):
        # Enable cropping mode
        self.cropping = True
        self.crop_start = None
        self.crop_end = None

    def start_crop(self, event):
        # Start the cropping rectangle
        if self.cropping:
            self.crop_start = (event.x, event.y)
            if self.crop_rectangle:
                self.canvas.delete(self.crop_rectangle)

    def draw_crop_rectangle(self, event):
        # Draw the cropping rectangle as the mouse moves
        if self.cropping and self.crop_start:
            self.crop_end = (event.x, event.y)
            if self.crop_rectangle:
                self.canvas.delete(self.crop_rectangle)
            self.crop_rectangle = self.canvas.create_rectangle(
                self.crop_start[0], self.crop_start[1], 
                self.crop_end[0], self.crop_end[1], 
                outline="red", width=2
            )

    def end_crop(self, event):
        # Finish the cropping action
        if self.cropping and self.crop_start:
            self.crop_end = (event.x, event.y)
            x1, y1 = self.crop_start
            x2, y2 = self.crop_end
            x1, x2 = sorted((x1, x2))
            y1, y2 = sorted((y1, y2))

            # Calculate the scale factor
            display_width, display_height = self.display_image.size
            original_height, original_width = self.processed_image.shape[:2]
            width_ratio = original_width / display_width
            height_ratio = original_height / display_height

            # Apply the scale factor to get correct coords
            x1, x2 = int(x1 * width_ratio), int(x2 * width_ratio)
            y1, y2 = int(y1 * height_ratio), int(y2 * height_ratio)

            # Let's crop this thing!
            if x2 > x1 and y2 > y1:
                self.processed_image = self.processed_image[y1:y2, x1:x2]
                self.add_to_history(self.processed_image)
                self.show_image()

            self.cropping = False
            if self.crop_rectangle:
                self.canvas.delete(self.crop_rectangle)
                self.crop_rectangle = None

    def resize_image(self, value):
        # Resize the image
        if self.processed_image is not None:
            scale_factor = int(value) / 100
            new_width = int(self.image.shape[1] * scale_factor)
            new_height = int(self.image.shape[0] * scale_factor)
            self.processed_image = cv2.resize(self.image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            self.add_to_history(self.processed_image)
            self.show_image()

    def rotate_image(self):
        # Rotate the image 90 degrees clockwise
        if self.processed_image is not None:
            self.processed_image = cv2.rotate(self.processed_image, cv2.ROTATE_90_CLOCKWISE)
            self.add_to_history(self.processed_image)
            self.show_image()

    def flip_image(self):
        # Flip the image horizontally
        if self.processed_image is not None:
            self.processed_image = cv2.flip(self.processed_image, 1)
            self.add_to_history(self.processed_image)
            self.show_image()

    def save_image(self):
        # Save the processed image to a file
        if self.processed_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                     filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
            if file_path:
                try:
                    save_image = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(file_path, save_image)
                    messagebox.showinfo("Saved", f"Image saved as {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image: {e}")

    def add_to_history(self, img):
        # Add the current state of the image to the history
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        self.history.append(img.copy())
        self.history_index += 1
        self.update_undo_redo_buttons()

    def update_undo_redo_buttons(self):
        # Enable or disable the undo/redo buttons based on history
        self.undo_button.config(state=tk.NORMAL if self.history_index > 0 else tk.DISABLED)
        self.redo_button.config(state=tk.NORMAL if self.history_index < len(self.history) - 1 else tk.DISABLED)

    def undo_action(self):
        # Undo the last action
        if self.history_index > 0:
            self.history_index -= 1
            self.processed_image = self.history[self.history_index].copy()
            self.show_image()
            self.update_undo_redo_buttons()

    def redo_action(self):
        # Redo the last undone action
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.processed_image = self.history[self.history_index].copy()
            self.show_image()
            self.update_undo_redo_buttons()

if __name__ == "__main__":
    app = ImageProcessorApp()
    app.mainloop()
