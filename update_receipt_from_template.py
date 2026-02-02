from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


TEMPLATE_PDF = Path(
    "/home/ubuntu/.cursor/projects/workspace/uploads/BH_915726201.pdf"
)
OUTPUT_PDF = Path("/workspace/updated_bh_receipt.pdf")


def wrap_text(text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        tentative = f"{current} {word}".strip()
        if stringWidth(tentative, font_name, font_size) <= max_width:
            current = tentative
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def money(value: Decimal) -> str:
    return f"${value:,.2f}"


def generate_overlay() -> BytesIO:
    buffer = BytesIO()
    page_width, page_height = letter
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    # Rectangles to cover old values (keep borders visible).
    def cover_rect(
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        fill_rgb: tuple[float, float, float] = (1, 1, 1),
    ) -> None:
        c.setFillColorRGB(*fill_rgb)
        c.setStrokeColorRGB(*fill_rgb)
        c.rect(x0, y0, x1 - x0, y1 - y0, fill=1, stroke=0)

    # Item row areas (description, SKU, price, amount).
    cover_rect(130.0, 440.0, 367.0, 492.0)  # description cell
    cover_rect(369.0, 440.0, 472.5, 478.0)  # SKU cell
    cover_rect(474.5, 456.0, 531.0, 477.0)  # item price cell
    cover_rect(534.0, 456.0, 586.0, 477.0)  # amount cell

    # Totals values in right box.
    totals_gray = (229 / 255, 229 / 255, 229 / 255)
    cover_rect(520.0, 130.0, 588.0, 142.5)  # Sub-total value (white)
    cover_rect(520.0, 76.5, 588.0, 89.0)  # Tax value (white)
    cover_rect(520.0, 51.0, 588.0, 63.5, fill_rgb=totals_gray)  # Total Order value
    cover_rect(520.0, 39.0, 588.0, 51.5, fill_rgb=totals_gray)  # Total Payment value

    # Payment amount value (within gray payment box).
    payment_gray = (229 / 255, 229 / 255, 229 / 255)
    cover_rect(405.0, 116.0, 445.0, 129.0, fill_rgb=payment_gray)

    # Reset fill color for text.
    c.setFillColorRGB(0, 0, 0)

    # New dates (mask old text with white glyphs, then draw new text).
    date_text = "3/02/2024"
    c.setFont("Times-Roman", 8)
    c.setFillColorRGB(1, 1, 1)
    c.drawString(31.70, 518.05, "01/27/26")  # mask original Invoice Date
    c.drawString(226.10, 518.05, "01/27/26")  # mask original Order Date
    c.setFillColorRGB(0, 0, 0)
    c.drawString(31.70, 518.05, date_text)  # Invoice Date
    c.drawString(226.10, 518.05, date_text)  # Order Date

    # New product details.
    desc = (
        "AXIS COMMUNICATIONS P3735-PLE 8MP OUTDOOR FOUR-SENSOR "
        "PANORAMIC NETWORK DOME CAMERA WITH NIGHT VISION"
    )
    desc_lines = wrap_text(desc, "Helvetica-Bold", 8, 234.9)

    desc_x = 133.2
    desc_start_y = 480.0
    desc_leading = 10.0

    c.setFont("Helvetica-Bold", 8)
    for i, line in enumerate(desc_lines):
        c.drawString(desc_x, desc_start_y - (i * desc_leading), line)

    # Salesperson line (kept, shifted slightly down for extra description line).
    c.setFont("Helvetica-Bold", 7)
    c.drawString(143.44, 450.0, "Salesperson Code:")
    c.drawString(216.0, 450.0, "WB")

    # SKU / MFR.
    c.setFont("Helvetica-Bold", 8)
    c.drawString(370.8, 467.64, "AXP3735PLE")
    c.setFont("Helvetica-Bold", 6)
    c.drawString(370.8, 456.92, "(02633-001)")

    # Pricing calculations.
    subtotal = Decimal("1599.00")
    tax_rate = Decimal("0.08875")
    tax = (subtotal * tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = subtotal + tax

    subtotal_str = money(subtotal)
    tax_str = money(tax)
    total_str = money(total)
    payment_amount_str = f"{total:,.2f}"

    # Item price and amount.
    c.setFont("Times-Bold", 9)
    c.drawRightString(529.2, 468.96, subtotal_str)
    c.drawRightString(586.8, 468.96, subtotal_str)

    # Totals.
    c.drawRightString(586.8, 133.81, subtotal_str)
    c.drawRightString(586.8, 80.52, tax_str)
    c.drawRightString(586.8, 54.60, total_str)
    c.drawRightString(586.8, 42.36, total_str)

    # Payment amount (no currency symbol).
    c.setFont("Times-Roman", 9)
    c.drawRightString(439.2, 120.06, payment_amount_str)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def main() -> None:
    if not TEMPLATE_PDF.exists():
        raise FileNotFoundError(f"Template PDF not found: {TEMPLATE_PDF}")

    overlay_pdf = generate_overlay()
    overlay_reader = PdfReader(overlay_pdf)
    overlay_page = overlay_reader.pages[0]

    reader = PdfReader(str(TEMPLATE_PDF))
    writer = PdfWriter()

    base_page = reader.pages[0]
    base_page.merge_page(overlay_page)
    writer.add_page(base_page)

    with OUTPUT_PDF.open("wb") as output_file:
        writer.write(output_file)

    print(f"Updated receipt saved to {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
