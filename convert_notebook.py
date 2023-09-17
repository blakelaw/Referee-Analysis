import nbformat

# Load the notebook
notebook = nbformat.read('PSM.ipynb', as_version=4)

# Initialize an empty string to store the code
code_script = ""

# Loop through each cell in the notebook
for cell in notebook.cells:
    # If the cell is a code cell, extract the source
    if cell.cell_type == "code":
        code_script += cell.source + "\n\n"

# Save the code to a new .py file
with open('PSM.py', 'w') as f:
    f.write(code_script)
