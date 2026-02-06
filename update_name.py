"""
Edit FreshDirect delivery label image to change 'Josh G.' to 'James M.'
"""
from __future__ import annotations

from pillow_heif import register_heif_opener
from PIL import Image, ImageDraw, ImageFont
import numpy as np

register_heif_opener()

INPUT_IMAGE = "template_receipt.heic"
OUTPUT_IMAGE = "updated_label.png"


def load_helvetica_bold(size: int) -> ImageFont.FreeTypeFont:
    """Load Helvetica Neue Bold specifically."""
    path = "/usr/share/fonts/truetype/macos/Helvetica.ttc"
    for idx in range(20):
        try:
            font = ImageFont.truetype(path, size, index=idx)
            name = font.getname()
            if "Bold" in name[1] and "Italic" not in name[1] and "Condensed" not in name[1]:
                return font
        except (OSError, IOError):
            break
    # Fallback
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size
    )


def gradient_fill_with_noise(
    img: Image.Image,
    box: tuple[int, int, int, int],
    source_img: Image.Image,
    sample_x_range: tuple[int, int],
) -> None:
    """Fill a box region with gradient + noise matching the paper texture."""
    x0, y0, x1, y1 = box
    src_arr = np.array(source_img)
    img_arr = np.array(img)

    for y in range(y0, y1):
        # Sample background color and variance from a clear area at this y
        row_pixels = []
        for x in range(sample_x_range[0], sample_x_range[1]):
            r, g, b = src_arr[y, x]
            if r > 200:
                row_pixels.append((r, g, b))
        if row_pixels:
            px = np.array(row_pixels)
            avg_color = px.mean(axis=0)
            std_color = px.std(axis=0)
        else:
            avg_color = np.array([237.0, 237.0, 241.0])
            std_color = np.array([3.0, 3.0, 3.0])

        # Generate noisy pixels for this row
        width = x1 - x0
        noise = np.random.normal(0, np.maximum(std_color, 2.0), size=(width, 3))
        row_colors = (avg_color + noise).clip(0, 255).astype(np.uint8)
        img_arr[y, x0:x1] = row_colors

    # Write back to image
    result = Image.fromarray(img_arr)
    img.paste(result)


def main() -> None:
    orig = Image.open(INPUT_IMAGE)
    img = orig.copy()
    draw = ImageDraw.Draw(img)

    # --- First label: Cover entire "Josh G. FD – UBER" line ---
    # Text line occupies: y=1290-1430, x=58-1300
    cover_box = (58, 1290, 1300, 1435)

    # Fill with gradient + noise matching the paper background texture
    gradient_fill_with_noise(img, cover_box, orig, sample_x_range=(150, 240))

    # Recreate draw after gradient fill
    draw = ImageDraw.Draw(img)

    # Load bold font - increase size to match original text
    font = load_helvetica_bold(120)
    print(f"Using font: {font.getname()}")

    # Write "James M. FD – UBER" as the full replacement line
    text = "James M. FD \u2013 UBER"
    text_x = 68
    text_y = 1293

    # Match the dark gray/black printed text color
    text_color = (72, 67, 65)
    draw.text((text_x, text_y), text, font=font, fill=text_color)

    # Save the result
    img.save(OUTPUT_IMAGE, "PNG")
    print(f"Updated image saved to {OUTPUT_IMAGE}")


if __name__ == "__main__":
    main()
