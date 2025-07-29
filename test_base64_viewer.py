#!/usr/bin/env python3
"""
Test script for Base64 Image Viewer
Creates a sample base64 image for testing
"""

import base64
import io
from PIL import Image, ImageDraw


def create_sample_base64_image():
    """Create a simple test image and return it as base64"""
    # Create a 200x200 test image
    img = Image.new('RGB', (200, 200), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw some shapes
    draw.rectangle([50, 50, 150, 150], fill='red', outline='black', width=2)
    draw.ellipse([25, 25, 75, 75], fill='green')
    draw.ellipse([125, 125, 175, 175], fill='yellow')
    
    # Add some text
    draw.text((60, 90), "Test Image", fill='white')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


if __name__ == "__main__":
    # Generate sample base64 image
    base64_image = create_sample_base64_image()
    
    print("Sample Base64 Image (copy and paste into the viewer):")
    print("-" * 50)
    print(base64_image)
    print("-" * 50)
    print(f"Length: {len(base64_image)} characters")
    
    # Save to file for easy testing
    with open('sample_base64_image.txt', 'w') as f:
        f.write(base64_image)
    
    print("Sample image saved to 'sample_base64_image.txt'")
    print("Run: python base64_image_viewer.py --file sample_base64_image.txt")