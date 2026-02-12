"""Logic for building and saving Jupyter notebooks."""
import nbformat
import io


def build_notebook(cells: list) -> nbformat.NotebookNode:
    """Convert list of cell dictionaries into a nbformat Notebook."""
    nb = nbformat.v4.new_notebook()
    nb.cells = []

    for c in cells:
        ctype = c.get("cell_type", "code")
        source = c.get("source", "")
        if ctype == "markdown":
            nb.cells.append(nbformat.v4.new_markdown_cell(source))
        else:
            nb.cells.append(nbformat.v4.new_code_cell(source))

    return nb


def save_notebook(nb: nbformat.NotebookNode, path: str) -> None:
    """Save a notebook object to a file."""
    with open(path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)


def notebook_to_bytes(nb: nbformat.NotebookNode) -> bytes:
    """Convert a notebook object to bytes."""
    buffer = io.StringIO()
    nbformat.write(nb, buffer)
    return buffer.getvalue().encode("utf-8")
