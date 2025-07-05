from fpdf import FPDF

def generate_summary_pdf(path, total, active, resigned):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="Workforce Summary Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Total Employees: {total}", ln=True)
    pdf.cell(200, 10, txt=f"Active Employees: {active}", ln=True)
    pdf.cell(200, 10, txt=f"Resigned Employees: {resigned}", ln=True)

    pdf.output(path)
