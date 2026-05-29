from PIL import Image

# Create 1x1 transparent image
img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))

assets_dir = "/Users/Nada/nada/GRAD/Grad-Project/SW/frontend/src/assets/"
img.save(assets_dir + "house_rock.png", "PNG")
img.save(assets_dir + "house_moai.png", "PNG")
img.save(assets_dir + "house_krusty.png", "PNG")
print("Dummy PNGs created successfully.")
