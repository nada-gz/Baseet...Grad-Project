import os
files = [f for f in os.listdir("models") if f.endswith(".py") and f != "__init__.py"]

imports = ["from sqlmodel import SQLModel"]
refs = []

for f in sorted(files):
    module = f[:-3]
    # Simple heuristic to extract class names from file
    with open(f"models/{f}", "r") as file:
        content = file.read()
    
    classes = []
    for line in content.split("\n"):
        if line.startswith("class ") and "(SQLModel, table=True)" in line:
            cls = line.split(" ")[1].split("(")[0]
            classes.append(cls)
        elif line.startswith("class ") and "(SQLModel" in line:
            cls = line.split(" ")[1].split("(")[0]
            classes.append(cls)

    if classes:
        imports.append(f"from models.{module} import {', '.join(classes)}")
        for cls in classes:
            refs.append(f"{cls}.update_forward_refs()")

with open("models/__init__.py", "w") as out:
    out.write("\n".join(imports) + "\n\n")
    # out.write("\n".join(refs) + "\n") # Pydantic V2 doesn't always need update_forward_refs or it might be Model.model_rebuild()

