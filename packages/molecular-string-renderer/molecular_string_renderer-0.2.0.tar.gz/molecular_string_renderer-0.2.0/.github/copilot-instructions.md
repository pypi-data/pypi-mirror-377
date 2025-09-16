---
applyTo: "**"
---

# GitHub Copilot Instructions

This is a Python repo for rendering molecular structures from various string formats (e.g., SMILES, InChI) to images using RDKit and Pillow.

- use logging instead of print statements
- write type hints for all functions and methods; use the most modern PEP practices when performing your type hinting (no `List`, `Dict`, etc. from `typing` - use `list`, `dict`, etc. instead)
- no relative imports; always use absolute imports
- write docstrings for all functions and methods using the Google style
- use f-strings for string formatting, but only when you need to embed expressions; otherwise, use regular strings
