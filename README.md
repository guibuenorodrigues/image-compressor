# Image compressor

[![pthon-version](https://img.shields.io/badge/Python-3.9-brightgreen?style=flat-square)](https://www.python.org/) [![pthon-version](https://img.shields.io/github/downloads/guibuenorodrigues/image-compressor/total.svg?style=flat-square)](https://github.com/guibuenorodrigues/image-compressor/releases) [![pthon-version](https://img.shields.io/github/license/guibuenorodrigues/image-compressor.svg?style=flat-square)](https://github.com/guibuenorodrigues/image-compressor/blob/main/LICENSE)

monitor a given folder and compress images to recude its size.

## Create the executable file

To create an executable file for the script you can use `pyinstaller` (available in the development dependencies) using the follow commando:

```bash
pyinstaller --onefile --name compressor --add-data="utils/;." --add-data="services/;." --paths .venv/Lib/site-packages main.py
```

## How it works

The application monitor a given directory looking for all files inside it based in a interval. Once it is time to look all the files the applications perfom a read and evaluate if the file should be or not compressed.

The requirements to be compressed is being a image and has its size higher than the last one saved in the control file. If the image is not in the control file, so the application compress the image and save details about its new size that will be used in the future.

The control file is located in the directory that is being monitored and its named `.compressed.json`.

> if you delete the control file, the application will try to compress all the images in the next time. So the control file help the application to avoid unnecessary wast resources.

## Settings

| **argument** | **short** |                                               **description**                                               | **default** | **Type** | **required** |
|:------------:|:---------:|:-----------------------------------------------------------------------------------------------------------:|:-----------:|:--------:|:------------:|
|  --directory |     -d    | the directory to be monitored                                                                               |      .      |  string  |      No      |
|   --quality  |     -q    | the image quality after compression                                                                         |     100     |  integer |      No      |
|    --debug   |     -D    | Enable or not debug option. This may increase a lot the log file.  Valid values: 1, 0, yes, no, true, false |    false    |    str   |      No      |
|  --interval  |     -I    | the interval between each directory lookup. in seconds                                                      |     180     |    int   |      No      |
