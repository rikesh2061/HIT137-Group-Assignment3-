import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor - OOP, Tkinter & OpenCV")
        
        # Original imaga
        self.image = None
        self.processed_image = None  # Image modifications
        self.start_x = self.start_y = self.end_x = self.end_y = None
        
        self.canvas = tk.Canvas(root, width=600, height=400, bg='gray')
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        
        btn_frame = tk.Frame(root)
        btn_frame.pack()
        
        self.load_btn = tk.Button(btn_frame, text="Load Image", command=self.load_image)
        self.load_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.save_btn = tk.Button(btn_frame, text="Save Image", command=self.save_image)
        self.save_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.quality_slider = tk.Scale(btn_frame, from_=0, to=50, orient=tk.HORIZONTAL, label="Degrade Quality", command=self.degrade_quality)
        self.quality_slider.grid(row=0, column=2, padx=5, pady=5)
        
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
        if not file_path:
            return
        
        self.image = cv2.imread(file_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        
        self.processed_image = self.image.copy()
        self.display_image(self.image)
        
    def display_image(self, img):
        img = Image.fromarray(img)
        img.thumbnail((600, 400))
        img_tk = ImageTk.PhotoImage(img)
        self.canvas.image = img_tk
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        
    def on_mouse_press(self, event):
        self.start_x, self.start_y = event.x, event.y
    
    def on_mouse_drag(self, event):
        self.end_x, self.end_y = event.x, event.y
        self.canvas.delete("crop_rect")
        self.canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="red", width=2, tags="crop_rect")
    
    def on_mouse_release(self, event):
        if self.image is None:
            return
        
        self.end_x, self.end_y = event.x, event.y
        self.crop_and_invert()
    
    def crop_and_invert(self):
        if not self.image.any():
            return
        
        x1, y1, x2, y2 = sorted([self.start_x, self.end_x]), sorted([self.start_y, self.end_y])
        mask = np.ones(self.image.shape, dtype=np.uint8) * 255
        mask[y1[0]:y1[1], x1[0]:x1[1]] = 0  # Invert the cropped area
        
        self.processed_image = cv2.bitwise_and(self.image, mask)
        self.display_image(self.processed_image)
    
    def degrade_quality(self, value):
        if self.processed_image is None:
            return
        
        quality = int(value)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100 - quality]
        _, enc_img = cv2.imencode(".jpg", cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR), encode_param)
        degraded_img = cv2.imdecode(enc_img, cv2.IMREAD_COLOR)
        degraded_img = cv2.cvtColor(degraded_img, cv2.COLOR_BGR2RGB)
        
        self.display_image(degraded_img)
    
    def save_image(self):
        if self.processed_image is None:
            messagebox.showerror("Error", "No processed image to save!")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if file_path:
            cv2.imwrite(file_path, cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR))
            messagebox.showinfo("Success", "Image saved successfully!")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()
