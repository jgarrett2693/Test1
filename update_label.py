"""Replace 'Josh G.' with 'James M.' on FreshDirect delivery label image."""

from pillow_heif import register_heif_opener
register_heif_opener()

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

INPUT_IMAGE = Path("/workspace/template_receipt.heic")
OUTPUT_IMAGE = Path("/workspace/updated_label.png")


def find_font(size: int) -> ImageFont.FreeTypeFont:
    """Try to load a bold sans-serif font at the given size."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
    ]
    for fp in font_paths:
        if Path(fp).exists():
            return ImageFont.truetype(fp, size)
    # Fallback
    return ImageFont.load_default()


def main() -> None:
    img = Image.open(str(INPUT_IMAGE)).convert("RGB")

    draw = ImageDraw.Draw(img)

    # --- Top label: "Josh G." text region ---
    # "Josh G." occupies roughly x=100..720, y=1300..1420 in the 3024x4032 image.
    # Background color sampled: ~(227, 227, 230)
    bg_color = (227, 227, 230)

    # Cover "Josh G." with background rectangle (leave "FD – UBER" untouched).
    cover_box_top = (85, 1295, 725, 1430)
    draw.rectangle(cover_box_top, fill=bg_color)

    # Draw "James M." in similar style/position.
    font_size = 95
    font = find_font(font_size)

    text_color = (55, 50, 50)  # dark gray/black matching original
    text_x = 90
    text_y = 1302
    draw.text((text_x, text_y), "James M.", fill=text_color, font=font)

    # Save result.
    img.save(str(OUTPUT_IMAGE), "PNG")
    print(f"Updated label saved to {OUTPUT_IMAGE}")


if __name__ == "__main__":
    main()
