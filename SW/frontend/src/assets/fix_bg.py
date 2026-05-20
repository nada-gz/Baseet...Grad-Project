from PIL import Image
import os

files = [
    "/Users/Nada/nada/GRAD/Grad-Project/SW/frontend/src/assets/baseet_run_1.png",
    "/Users/Nada/nada/GRAD/Grad-Project/SW/frontend/src/assets/baseet_run_2.png"
]

for file_path in files:
    if os.path.exists(file_path):
        try:
            img = Image.open(file_path)
            img = img.convert("RGBA")
            datas = img.getdata()
            newData = []
            for item in datas:
                # Tolerance for white background
                if item[0] > 230 and item[1] > 230 and item[2] > 230:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)
            img.putdata(newData)
            img.save(file_path, "PNG")
            print(f"Fixed {file_path}")
        except Exception as e:
            print(f"Error on {file_path}: {e}")
    else:
        print(f"File not found: {file_path}")
