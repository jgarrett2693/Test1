from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        # Logo placeholder (Using text since we don't have the image file)
        self.set_font("Arial", "B", 30)
        self.cell(40, 15, "B&H", border=1, align="C")

        # Header Text
        self.set_font("Arial", "B", 12)
        self.set_xy(55, 10)
        self.cell(0, 5, "PHOTO - VIDEO - PRO AUDIO", 0, 1)
        self.set_font("Arial", "", 8)
        self.set_xy(55, 16)
        self.cell(0, 4, "The Professional's Source", 0, 1)

        # Address and Contact Info
        self.set_xy(120, 10)
        self.set_font("Arial", "", 7)
        self.multi_cell(
            0,
            3,
            "420 Ninth Avenue, New York, NY 10001\n"
            "Fax: 212.239.7770 - 800.947.2215\n"
            "www.bhphotovideo.com\n"
            "To Inquire About Your Order Tel: 212.239.7765 - 800.221.5743",
            align="R",
        )
        self.ln(10)


def create_receipt():
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- Bill To / Ship To Section ---
    pdf.set_y(40)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(90, 5, "Bill To:", 0, 0)
    pdf.cell(90, 5, "Ship To:", 0, 1)

    pdf.set_font("Arial", "", 9)
    bill_to = (
        "JOSHUA GARRETT\n"
        "JOSHUA GARRETT\n"
        "123 MELROSE ST APT 354\n"
        "BROOKLYN, NY 11206\n"
        "USA"
    )

    ship_to = (
        "GARRETT, JOSHUA\n"
        "123 MELROSE ST APT 354\n"
        "BROOKLYN, NY 11206\n"
        "Bill Phone: (310)408-4111"
    )

    y_start = pdf.get_y()
    pdf.multi_cell(90, 4, bill_to, 0, "L")
    pdf.set_xy(100, y_start)
    pdf.multi_cell(90, 4, ship_to, 0, "L")

    pdf.ln(5)

    # --- Order / Invoice Details Header ---
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", "B", 7)

    headers = [
        "Invoice Date",
        "Terms",
        "Order No:",
        "Order Date",
        "PO NUMBER",
        "Customer Code",
        "Ship Via",
    ]
    widths = [25, 20, 25, 25, 25, 30, 40]

    for i, header in enumerate(headers):
        pdf.cell(widths[i], 5, header, 1, 0, "C", True)
    pdf.ln()

    # Data Row
    pdf.set_font("Arial", "", 7)
    data = ["01/27/26", "", "915726201", "01/27/26", "", "C4158536", "PICKUP IN STORE"]
    for i, value in enumerate(data):
        pdf.cell(widths[i], 5, value, 1, 0, "C")
    pdf.ln(10)

    # --- Line Items Header ---
    pdf.set_font("Arial", "B", 7)
    item_headers = [
        "Qty Ord",
        "Qty Ship",
        "Qty Bko",
        "Item Description",
        "SKU#/MFR#",
        "Item Price",
        "Amount",
    ]
    item_widths = [15, 15, 15, 75, 30, 20, 20]

    for i, header in enumerate(item_headers):
        pdf.cell(item_widths[i], 5, header, "B", 0, "C")  # Bottom border only
    pdf.ln()

    # --- Line Item Data (UPDATED PRODUCT) ---
    # New Product Details
    qty = "1"
    desc = (
        "Axis Communications P3735-PLE 8MP Outdoor Four-Sensor Panoramic "
        "Network Dome Camera with Night Vision"
    )
    sku_line1 = "AXP3735PLE"
    sku_line2 = "(02633-001)"
    price = "$1,599.00"
    amount = "$1,599.00"

    pdf.set_font("Arial", "", 7)

    # We use multi_cell for description to handle wrapping
    y_before_item = pdf.get_y()

    pdf.cell(item_widths[0], 5, qty, 0, 0, "C")
    pdf.cell(item_widths[1], 5, qty, 0, 0, "C")
    pdf.cell(item_widths[2], 5, "", 0, 0, "C")

    # Save x, y for description
    x_desc = pdf.get_x()
    pdf.multi_cell(item_widths[3], 4, desc, 0, "L")
    y_after_desc = pdf.get_y()

    # Reset position for remaining columns
    pdf.set_xy(x_desc + item_widths[3], y_before_item)

    # SKU Column (Multi-line)
    x_sku = pdf.get_x()
    pdf.multi_cell(item_widths[4], 4, f"{sku_line1}\n{sku_line2}", 0, "C")

    # Price and Amount
    pdf.set_xy(x_sku + item_widths[4], y_before_item)
    pdf.cell(item_widths[5], 5, price, 0, 0, "R")
    pdf.cell(item_widths[6], 5, amount, 0, 1, "R")

    pdf.set_y(max(y_after_desc, pdf.get_y()) + 5)

    # --- Footer Totals ---
    # Calculations based on approx 8.875% tax rate from original receipt
    subtotal_val = 1599.00
    tax_val = subtotal_val * 0.08875
    total_val = subtotal_val + tax_val

    pdf.set_x(140)
    pdf.cell(30, 5, "Sub-Total:", 0, 0, "R")
    pdf.cell(20, 5, f"${subtotal_val:,.2f}", 0, 1, "R")

    pdf.set_x(140)
    pdf.cell(30, 5, "Tax:", 0, 0, "R")
    pdf.cell(20, 5, f"${tax_val:,.2f}", 0, 1, "R")

    pdf.set_font("Arial", "B", 8)
    pdf.set_x(140)
    pdf.cell(30, 5, "Total Order:", 0, 0, "R")
    pdf.cell(20, 5, f"${total_val:,.2f}", 0, 1, "R")

    pdf.set_x(140)
    pdf.cell(30, 5, "Total Payment:", 0, 0, "R")
    pdf.cell(20, 5, f"${total_val:,.2f}", 0, 1, "R")

    pdf.set_x(140)
    pdf.cell(30, 5, "Balance:", 0, 0, "R")
    pdf.cell(20, 5, "USD $.00", 0, 1, "R")

    # --- Payment Info ---
    pdf.set_y(y_after_desc + 30)
    pdf.set_font("Arial", "", 7)
    pdf.cell(50, 4, "Payment Type: VISA CARD", 0, 1)
    pdf.cell(50, 4, "Card/Check Number: ************4587", 0, 1)
    pdf.cell(50, 4, f"Amount: {total_val:,.2f}", 0, 1)
    pdf.cell(50, 4, "Ship Phone: (310)408-4111", 0, 1)

    pdf.ln(10)
    pdf.cell(0, 5, "Customer Copy", 0, 1, "C")
    pdf.cell(0, 5, "Page 1 of 1", 0, 1, "C")

    # Output
    pdf.output("updated_bh_receipt.pdf")
    print("PDF generated successfully: updated_bh_receipt.pdf")


if __name__ == "__main__":
    create_receipt()
