# Image compressor

monitor a given folder and compress images to recude its size.

## Create the executable file

To create an executable file for the script you can use `pyinstaller` (available in the development dependencies) using the follow commando:

```bash
pyinstaller --onefile --name compressor --add-data="utils/;." --paths .venv/Lib/site-packages main.py
```
