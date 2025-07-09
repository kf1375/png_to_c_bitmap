# 🖼️ PNG to C Bitmap Converter

This Python script converts a 24-bit RGB PNG image into a 16-bit RGB565 C bitmap structure, suitable for embedded systems. It's designed for microcontrollers that render bitmaps on LCDs or OLEDs, using RGB565 pixel data arranged in BMP-style format.

## Features

- Converts PNG to 16-bit RGB565 format
- Generates packed C structures compatible with BMP format
- Supports little-endian and big-endian output (`RC()` macro)

## Requirements

- Python 3.6+
- Pillow image library

Install Pillow with:

```bash
pip install pillow
```

# Usage
```bash
python png_to_c_bitmap.py <input.png> <output.c> <var_name> [--reverse16]
```