import modal

app = modal.App("grad-project-ai")

image = (
    modal.Image.debian_slim()
    .pip_install_from_requirements("requirements.txt")
)

model_volume = modal.Volume.from_name(
    "grad-project-models",
    create_if_missing=True
)

@app.function(image=image)
def ping():
    return "modal is working"
