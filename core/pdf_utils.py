from fpdf import FPDF

def generate_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    
    # Handle Unicode characters gracefully
    safe_text = text_content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=safe_text)
    
    return bytes(pdf.output())
