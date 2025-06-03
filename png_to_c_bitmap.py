from PIL import Image
import sys

def rgb888_to_rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def format_pixel(value, endian_swap=False):
    if endian_swap:
        value = ((value & 0xFF) << 8) | ((value >> 8) & 0xFF)
    return f"RC(0x{value:04x})"

def convert_png_to_c(filename, var_name="image", endian_swap=False):
    img = Image.open(filename).convert("RGB")
    width, height = img.size
    pixels = list(img.getdata())

    # Flip vertically to match BMP bottom-up storage
    pixels = [pixels[y * width:(y + 1) * width] for y in range(height)]
    pixels.reverse()
    flat_pixels = [px for row in pixels for px in row]

    pixel_data = [format_pixel(rgb888_to_rgb565(r, g, b), endian_swap) for r, g, b in flat_pixels]

    bmp_size = width * height * 2
    offset = 14 + 40  # BITMAPFILEHEADER + BITMAPINFOHEADER

    output = []

    output.append('#include <stdint.h>')
    output.append('#include "lcd.h"')
    output.append('#include "bmp.h"\n')
    output.append(f'#define WIDTH {width}')
    output.append(f'#define HEIGHT {height}\n')
    output.append('#if LCD_REVERSE16 == 0')
    output.append('#define RC(a) a')
    output.append('#endif')
    output.append('#if LCD_REVERSE16 == 1')
    output.append('#define RC(a) ((((a) & 0xFF) << 8) | (((a) & 0xFF00) >> 8))')
    output.append('#endif\n')

    output.append('#ifdef  __GNUC__')
    output.append('#pragma pack(push, 1)')
    output.append('#elif   defined(__CC_ARM)')
    output.append('#pragma push')
    output.append('#pragma pack(1)')
    output.append('#endif\n')

    output.append(f'const BITMAPSTRUCT {var_name}_{width}x{height}_16 __attribute__((aligned)) =')
    output.append('{')
    output.append('  {')
    output.append(f'    0x4d42u,')
    output.append(f'    {bmp_size + offset},')
    output.append(f'    0x0000u,')
    output.append(f'    0x0000u,')
    output.append(f'    {offset}')
    output.append('  },')
    output.append('  {')
    output.append(f'    40,')
    output.append(f'    {width},')
    output.append(f'    {height},')
    output.append(f'    1u,')
    output.append(f'    16,')
    output.append(f'    0x00000003u,')
    output.append(f'    {bmp_size},')
    output.append(f'    0x00000000ul,')
    output.append(f'    0x00000000ul,')
    output.append(f'    0x00000000ul,')
    output.append(f'    0x00000000ul')
    output.append('  },')
    output.append('  {')

    # Insert pixel values, 8 per line
    for i in range(0, len(pixel_data), 8):
        output.append('    ' + ', '.join(pixel_data[i:i+8]) + (',' if i + 8 < len(pixel_data) else ''))

    output.append('  }')
    output.append('};\n')

    output.append('#ifdef  __GNUC__')
    output.append('#pragma pack (pop)')
    output.append('#elif   defined(__CC_ARM)')
    output.append('#pragma pop')
    output.append('#endif')

    return '\n'.join(output)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python png_to_c_bitmap.py <input.png> <output.c> <var_name> [--reverse16]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    var_name = sys.argv[3] if len(sys.argv) > 3 else "image"
    endian_reverse = "--reverse16" in sys.argv

    result = convert_png_to_c(input_file, var_name, endian_swap=endian_reverse)

    with open(output_file, "w") as f:
        f.write(result)

    print(f"Bitmap written to {output_file}")
