from PIL import Image
import os

file_path = "/Users/Nada/.gemini/antigravity/brain/e215d3e7-e60a-4b27-bdb7-d6b2e64cee9b/house_pineapple_1776207284312.png"
if os.path.exists(file_path):
    img = Image.open(file_path)
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    # Remove pure white background
    for item in datas:
        if item[0] > 245 and item[1] > 245 and item[2] > 245:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    img.save("/Users/Nada/nada/GRAD/Grad-Project/SW/frontend/src/assets/house_pineapple.png", "PNG")
    print("Pineapple prepared and saved.")
