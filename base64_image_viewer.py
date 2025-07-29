#!/usr/bin/env python3
"""
Base64 Image Viewer

A simple Python application to decode and display base64 encoded images.
Supports PNG, JPEG, and WebP formats.
"""

import base64
import io
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from PIL import Image, ImageTk
import argparse
import sys
import re


class Base64ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Base64 Image Viewer")
        self.root.geometry("800x600")
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        ttk.Label(main_frame, text="Paste Base64 Image Data:").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        self.text_area = scrolledtext.ScrolledText(main_frame, height=8, wrap=tk.WORD)
        self.text_area.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Button(button_frame, text="View Image", command=self.view_image).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Clear", command=self.clear_text).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Save Image", command=self.save_image).grid(row=0, column=2)
        
        self.image_frame = ttk.LabelFrame(main_frame, text="Image Preview", padding="10")
        self.image_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        main_frame.rowconfigure(3, weight=1)
        
        self.image_label = ttk.Label(self.image_frame, text="No image loaded")
        self.image_label.pack(expand=True)
        
        self.current_image = None
        
    def extract_base64_data(self, input_text):
        input_text = input_text.strip()
        
        if input_text.startswith('data:image/'):
            match = re.match(r'data:image/[^;]+;base64,(.+)', input_text)
            if match:
                return match.group(1)
        
        input_text = re.sub(r'\s+', '', input_text)
        return input_text
        
    def view_image(self):
        base64_data = self.text_area.get("1.0", tk.END).strip()
        
        if not base64_data:
            messagebox.showwarning("Warning", "Please paste base64 image data first.")
            return
            
        try:
            clean_data = self.extract_base64_data(base64_data)
            
            image_data = base64.b64decode(clean_data)
            
            image = Image.open(io.BytesIO(image_data))
            self.current_image = image.copy()
            
            display_image = self.resize_image_for_display(image)
            
            photo = ImageTk.PhotoImage(display_image)
            
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo
            
            self.image_frame.configure(text=f"Image Preview ({image.format} - {image.size[0]}x{image.size[1]})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decode/display image: {str(e)}")
            
    def resize_image_for_display(self, image, max_width=600, max_height=400):
        width, height = image.size
        
        if width <= max_width and height <= max_height:
            return image
            
        ratio = min(max_width/width, max_height/height)
        new_size = (int(width * ratio), int(height * ratio))
        
        return image.resize(new_size, Image.Resampling.LANCZOS)
        
    def clear_text(self):
        self.text_area.delete("1.0", tk.END)
        self.image_label.configure(image="", text="No image loaded")
        self.image_label.image = None
        self.image_frame.configure(text="Image Preview")
        self.current_image = None
        
    def save_image(self):
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to save. Please load an image first.")
            return
            
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("WebP files", "*.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_image.save(file_path)
                messagebox.showinfo("Success", f"Image saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Base64 Image Viewer")
    parser.add_argument("--file", "-f", help="File containing base64 image data")
    parser.add_argument("--data", "-d", help="Base64 image data string")
    
    args = parser.parse_args()
    
    root = tk.Tk()
    app = Base64ImageViewer(root)
    
    if args.file:
        try:
            with open(args.file, 'r') as f:
                data = f.read()
            app.text_area.insert("1.0", data)
            app.view_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    elif args.data:
        app.text_area.insert("1.0", args.data)
        app.view_image()
    
    root.mainloop()


if __name__ == "__main__":
    main()