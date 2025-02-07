from tkinter import *
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np

# Initialize the main window
root = Tk()
root.title("Image Editor")

# Global variables
original_image = None
cropped_image = None
crop_coords = None
history = []
redo_stack = []
current_tool = None

# Function to load the image
def load_image():
    global original_image, cropped_image, history, redo_stack
    filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
    if filepath:
        original_image = cv2.imread(filepath)
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        cropped_image = original_image.copy()
        history.clear()
        redo_stack.clear()
        add_to_history()
        display_images()

# Function to add to history
def add_to_history():
    global cropped_image, history
    if cropped_image is not None:
        history.append(cropped_image.copy())

# Function to display image
def display_images():
    if cropped_image is not None:
        image_pil = Image.fromarray(cropped_image)
        tk_image = ImageTk.PhotoImage(image_pil)
        canvas_cropped.create_image(250, 250, anchor=CENTER, image=tk_image)
        canvas_cropped.image = tk_image

# Function to start cropping
def start_crop(event):
    global crop_coords
    if current_tool == "crop":
        crop_coords = [event.x, event.y]

# Function to show crop area
def show_crop(event):
    if current_tool == "crop" and crop_coords:
        canvas_original.delete("crop_rectangle")
        canvas_original.create_rectangle(
            crop_coords[0], crop_coords[1], event.x, event.y, outline="red", tags="crop_rectangle"
        )

# Function to finalize cropping
def finish_crop(event):
    global cropped_image
    if current_tool == "crop" and crop_coords:
        add_to_history()
        x1, y1 = crop_coords
        x2, y2 = event.x, event.y
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])

        # Crop image
        cropped_image = original_image[y1:y2, x1:x2]
        display_images()

# Function to undo last action
def undo_action():
    global cropped_image
    if history:
        redo_stack.append(cropped_image.copy())
        cropped_image = history.pop()
        display_images()

# Function to redo last undone action
def redo_action():
    global cropped_image
    if redo_stack:
        history.append(cropped_image.copy())
        cropped_image = redo_stack.pop()
        display_images()

# Function to save the cropped image
def save_image():
    if cropped_image is not None:
        filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if filepath:
            cv2.imwrite(filepath, cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR))

# Function to set current tool
def set_tool(tool_name):
    global current_tool
    current_tool = tool_name

# GUI Layout
title = Label(root, text="Brad and Jaafar Assessment 3", font=("Arial", 18, "bold"))
title.pack(pady=5)

canvas_frame = Frame(root)
canvas_frame.pack()

canvas_original = Canvas(canvas_frame, width=500, height=500, bg="gray")
canvas_original.grid(row=0, column=0, padx=10)
canvas_original.bind("<ButtonPress-1>", start_crop)
canvas_original.bind("<B1-Motion>", show_crop)
canvas_original.bind("<ButtonRelease-1>", finish_crop)

canvas_cropped = Canvas(canvas_frame, width=500, height=500, bg="gray")
canvas_cropped.grid(row=0, column=1, padx=10)

button_frame = Frame(root)
button_frame.pack()

Button(button_frame, text="Load Image", command=load_image).grid(row=0, column=0, padx=10)
Button(button_frame, text="Crop Tool", command=lambda: set_tool("crop")).grid(row=0, column=1, padx=10)
Button(button_frame, text="Undo", command=undo_action).grid(row=0, column=2, padx=10)
Button(button_frame, text="Redo", command=redo_action).grid(row=0, column=3, padx=10)
Button(button_frame, text="Save Image", command=save_image).grid(row=0, column=4, padx=10)

# Function to bind standard keyboard shortcuts
def bind_shortcuts():
    root.bind("<Control-o>", lambda event: load_image())  # Ctrl+O to load image
    root.bind("<Control-s>", lambda event: save_image())  # Ctrl+S to save image
    root.bind("<Control-z>", lambda event: undo_action())  # Ctrl+Z to undo
    root.bind("<Control-y>", lambda event: redo_action())  # Ctrl+Y to redo
    root.bind("<Control-c>", lambda event: set_tool("crop"))  # Ctrl+C to activate Crop Tool

bind_shortcuts()

# Run main loop
root.mainloop()
