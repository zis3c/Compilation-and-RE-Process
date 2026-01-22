from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(filename="app_icon.ico"):
    # Create a 256x256 image with alpha channel
    size = (256, 256)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Draw rounded square (Blue)
    # Since Pillow doesn't have easy rounded rect, we'll draw a circle + rects or just a circle
    # Let's do a Circle for simplicity and modern look
    d.ellipse([(10, 10), (246, 246)], fill="#2196F3", outline="#1976D2", width=5)

    # Draw Text "CS" (Compilation Simulator)
    try:
        # Try to load a font, fallback to default
        font = ImageFont.truetype("arial.ttf", 120)
    except IOError:
        font = ImageFont.load_default()

    # Center text
    text = "CS"
    # loose approximation of centering
    d.text((55, 60), text, fill="white", font=font)

    # Save as ICO
    img.save(filename, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Icon created: {filename}")

if __name__ == "__main__":
    create_icon()
