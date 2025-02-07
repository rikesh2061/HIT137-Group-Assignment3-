import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageEnhance

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        
        self.image = None
        self.cropped_image = None
        self.original_image = None
        self.history = []
        self.redo_stack = []
        self.pan_offset = [0, 0]
        self.crop_coords = None
        
        self.setup_ui()
    
    def setup_ui(self):
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.frame, bg='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.update_crop)
        self.canvas.bind("<ButtonRelease-1>", self.perform_crop)
        
        self.controls = ttk.Frame(self.root)
        self.controls.pack(fill=tk.X)
        
        self.load_btn = ttk.Button(self.controls, text="Load Image", command=self.load_image)
        self.load_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.save_btn = ttk.Button(self.controls, text="Save Image", command=self.save_image)
        self.save_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.undo_btn = ttk.Button(self.controls, text="Undo", command=self.undo)
        self.undo_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.redo_btn = ttk.Button(self.controls, text="Redo", command=self.redo)
        self.redo_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.center_btn = ttk.Button(self.controls, text="Center Image", command=self.center_image)
        self.center_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.brightness_slider = ttk.Scale(self.controls, from_=0.5, to=2.0, orient=tk.HORIZONTAL, command=self.adjust_brightness)
        self.brightness_slider.pack(side=tk.LEFT, padx=5, pady=5)
        
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not file_path:
            return
        self.image = Image.open(file_path)
        self.original_image = self.image.copy()
        self.history.append(self.image.copy())
        self.display_image()
    
    def display_image(self):
        if self.image is None:
            return
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(self.pan_offset[0], self.pan_offset[1], anchor=tk.CENTER, image=self.tk_image)
    
    def save_image(self):
        if self.image is None:
            messagebox.showerror("Error", "No image to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG file", "*.png"), ("JPEG file", "*.jpg")])
        if file_path:
            self.image.save(file_path)
    
    def start_crop(self, event):
        self.crop_coords = (event.x, event.y)
    
    def update_crop(self, event):
        self.crop_coords = (self.crop_coords[0], self.crop_coords[1], event.x, event.y)
    
    def perform_crop(self, event):
        if self.image is None or not self.crop_coords:
            return
        x1, y1, x2, y2 = self.crop_coords
        self.image = self.image.crop((x1, y1, x2, y2))
        self.history.append(self.image.copy())
        self.display_image()
    
    def adjust_brightness(self, value):
        if self.image is None:
            return
        enhancer = ImageEnhance.Brightness(self.original_image)
        self.image = enhancer.enhance(float(value))
        self.display_image()
    
    def undo(self):
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.image = self.history[-1].copy()
            self.display_image()
    
    def redo(self):
        if self.redo_stack:
            self.image = self.redo_stack.pop()
            self.history.append(self.image.copy())
            self.display_image()
    
    def center_image(self):
        self.pan_offset = [self.canvas.winfo_width()//2, self.canvas.winfo_height()//2]
        self.display_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()
