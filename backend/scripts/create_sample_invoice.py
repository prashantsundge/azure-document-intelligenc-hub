import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def create_invoice(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(20 * mm, height - 25 * mm, "NORTHSTAR")

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawRightString(width - 20 * mm, height - 25 * mm, "INVOICE")

    pdf.setFont("Helvetica", 11)
    details = [
        "Invoice number: NS-2026-001",
        "Invoice date: 15 August 2026",
        "Supplier: Blue River Consulting",
        "Payment terms: Net 30 days",
    ]

    y = height - 48 * mm
    for detail in details:
        pdf.drawString(20 * mm, y, detail)
        y -= 7 * mm

    table_top = height - 95 * mm
    columns = [20 * mm, 105 * mm, 135 * mm, 165 * mm]
    rows = [
        ["Description", "Quantity", "Rate", "Amount"],
        ["Consulting services", "10 hours", "USD 125.00", "USD 1,250.00"],
    ]

    for row_index, row in enumerate(rows):
        row_y = table_top - (row_index * 12 * mm)
        if row_index == 0:
            pdf.setFillColor(colors.HexColor("#EAF3FA"))
            pdf.rect(20 * mm, row_y - 8 * mm, 170 * mm, 12 * mm, fill=True, stroke=False)
            pdf.setFillColor(colors.black)
            pdf.setFont("Helvetica-Bold", 10)
        else:
            pdf.setFont("Helvetica", 10)

        for column_index, value in enumerate(row):
            pdf.drawString(columns[column_index] + 2 * mm, row_y - 2 * mm, value)

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawRightString(width - 20 * mm, height - 145 * mm, "Total due: USD 1,250.00")

    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(20 * mm, 20 * mm, "Synthetic document created for the Azure Document Intelligence Hub.")
    pdf.save()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    create_invoice(args.output)
    print(f"Created synthetic invoice: {args.output}")


if __name__ == "__main__":
    main()