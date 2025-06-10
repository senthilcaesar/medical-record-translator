from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

def create_lab_report_pdf():
    filename = "sample_lab_report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph("COMPREHENSIVE METABOLIC PANEL & COMPLETE BLOOD COUNT", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Patient Info
    patient_info = """
    <b>Patient:</b> John Doe<br/>
    <b>Date:</b> 2024-01-15<br/>
    <b>Lab ID:</b> LAB123456<br/>
    """
    story.append(Paragraph(patient_info, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Hematology Section
    hematology = """
    <b>HEMATOLOGY:</b><br/>
    Hemoglobin: 14.0 g/dL (Normal: 13.5-18.0)<br/>
    RBC Count: 6.52 Million/cmm (Normal: 3.5-5.0)<br/>
    Hematocrit (PCV): 56.3% (Normal: 40-65%)<br/>
    MCV: 86.5 fL (Normal: 76-96)<br/>
    MCH: 24.5 pg (Normal: 27-32)<br/>
    MCHC: 28.4 g% (Normal: 30-35)<br/>
    """
    story.append(Paragraph(hematology, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # White Blood Cells Section
    wbc = """
    <b>WHITE BLOOD CELLS:</b><br/>
    Total WBC Count: 8,200 cells/cmm (Normal: 4,500-11,000)<br/>
    Neutrophils: 78.9% (Normal: 40-60%)<br/>
    Lymphocytes: 13.9% (Normal: 20-40%)<br/>
    Eosinophils: 7.2% (Normal: 1-4%)<br/>
    Monocytes: 0% (Normal: 2-8%)<br/>
    Basophils: 0% (Normal: 0.5-1%)<br/>
    """
    story.append(Paragraph(wbc, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Platelets Section
    platelets = """
    <b>PLATELETS:</b><br/>
    Platelet Count: 1.88 Lakhs/cmm (Normal: 1.5-4.5)<br/>
    """
    story.append(Paragraph(platelets, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Chemistry Panel Section
    chemistry = """
    <b>CHEMISTRY PANEL:</b><br/>
    Blood Sugar (Fasting): 110 mg/dL (Normal: 70-110)<br/>
    Urea: 24 mg/dL (Normal: 10-40)<br/>
    Creatinine: 0.7 mg/dL (Normal: 0.9-1.4)<br/>
    Uric Acid: 5.4 mg/dL (Normal: 3.5-7.2)<br/>
    Calcium: 8.9 mg/dL (Normal: 8.7-11.0)<br/>
    """
    story.append(Paragraph(chemistry, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Lipid Profile Section
    lipid = """
    <b>LIPID PROFILE:</b><br/>
    Total Cholesterol: 180 mg/dL (Desirable: &lt;200)<br/>
    Triglycerides: 152 mg/dL (Normal: &lt;150)<br/>
    HDL Cholesterol: 45 mg/dL (Normal: 45-60)<br/>
    LDL Cholesterol: 104.6 mg/dL (Normal: 70-165)<br/>
    VLDL: 30.4 mg/dL (Normal: 15-30)<br/>
    Total Cholesterol/HDL Ratio: 4 (Desirable: &lt;4.5)<br/>
    """
    story.append(Paragraph(lipid, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print(f"Created {filename}")

if __name__ == "__main__":
    create_lab_report_pdf()