from PIL import Image

def convert_to_ico(source="compile.png", dest="app_icon.ico"):
    try:
        img = Image.open(source)
        # Resize/Resample and save as ICO with multiple sizes
        img.save(dest, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print(f"Successfully converted {source} to {dest}")
    except Exception as e:
        print(f"Error converting icon: {e}")

if __name__ == "__main__":
    convert_to_ico()
