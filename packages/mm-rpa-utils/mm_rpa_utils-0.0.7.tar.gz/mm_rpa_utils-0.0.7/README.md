# mm_rpa_utils

### build version

1. python -m build
2. python -m twine upload dist/*


### build app
1. pyinstaller --onefile --add-data "img;img" --windowed .\main.py