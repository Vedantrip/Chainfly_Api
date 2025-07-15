from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Color scheme
PRIMARY_COLOR = colors.HexColor("#2E86AB")
SECONDARY_COLOR = colors.HexColor("#F18F01")
LIGHT_BG = colors.HexColor("#F7F9FC")
DARK_TEXT = colors.HexColor("#2B2D42")

def fmt_currency(value):
    """Format currency with proper handling"""
    try:
        return f"₹{int(value):,}" if value else "₹0"
    except:
        return "₹---"

def create_savings_chart(savings, output_path="generated_pdfs/savings_chart.png"):
    """Generate savings projection chart"""
    months = list(range(1, 26 * 12 + 1, 12))
    monthly_savings = savings.get('monthly_savings', 0) or 0
    cumulative = [monthly_savings * m for m in months]
    
    plt.style.use('seaborn')
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(months, cumulative, color=SECONDARY_COLOR, linewidth=2.5)
    ax.fill_between(months, cumulative, color=SECONDARY_COLOR, alpha=0.1)
    ax.set_title("25-Year Savings Projection", pad=20, fontsize=12, fontweight='bold')
    ax.set_xlabel("Months", fontsize=10)
    ax.set_ylabel("Cumulative Savings (₹)", fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches='tight')
    plt.close()

def generate_proposal_pdf(data: dict, savings: dict, output_dir="generated_pdfs"):
    """Generate professional solar proposal PDF"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create filename
    customer_name = data.get("customer_name", "proposal").replace(" ", "_")
    file_name = f"{customer_name}_solar_proposal_{datetime.now().strftime('%Y%m%d')}.pdf"
    file_path = os.path.join(output_dir, file_name)

    # Initialize canvas
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    styles = getSampleStyleSheet()
    
    # Custom styles
    heading_style = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=PRIMARY_COLOR,
        spaceAfter=6
    )
    
    # --- Header ---
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(PRIMARY_COLOR)
    c.drawCentredString(width/2, height-50, "SOLAR FEASIBILITY PROPOSAL")
    
    # --- Key Metrics Bar ---
    c.setFillColor(LIGHT_BG)
    c.rect(30, height-100, width-60, 40, fill=True, stroke=False)
    
    metrics = [
        ("System Size", f"{data.get('system_size_kw', 'N/A')} kW"),
        ("CAPEX", fmt_currency(savings.get('capex'))),
        ("Net Cost", fmt_currency(savings.get('net_capex'))),
        ("Monthly Savings", fmt_currency(savings.get('monthly_savings'))),
        ("ROI", f"{savings.get('roi_percent_25yr', 'N/A')}%"),
        ("Payback", f"{int(savings.get('payback_years', 0)*12)} months")
    ]
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK_TEXT)
    col_width = (width-60)/len(metrics)
    for i, (label, value) in enumerate(metrics):
        x_pos = 35 + (i * col_width)
        c.drawString(x_pos, height-85, label)
        c.drawString(x_pos, height-100, value)
    
    y = height - 130  # Current y position
    
    # --- Customer Details ---
    p = Paragraph("<b>1. CUSTOMER DETAILS</b>", heading_style)
    p.wrapOn(c, width, height)
    p.drawOn(c, 40, y)
    y -= 30
    
    customer_data = [
        ["Customer:", data.get("customer_name", "N/A")],
        ["Location:", f"{data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}"],
        ["Rooftop Area:", f"{data.get('rooftop_area_m2', 'N/A')} m²"],
        ["Monthly Bill:", fmt_currency(data.get('monthly_bill'))]
    ]
    
    t = Table(customer_data, colWidths=[100, 200])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TEXTCOLOR', (0,0), (0,-1), DARK_TEXT),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
    ]))
    t.wrapOn(c, width, height)
    t.drawOn(c, 40, y-80)
    y -= 100
    
    # --- System Design ---
    p = Paragraph("<b>2. SYSTEM DESIGN</b>", heading_style)
    p.wrapOn(c, width, height)
    p.drawOn(c, 40, y)
    y -= 30
    
    system_data = [
        ["System Size:", f"{data.get('system_size_kw', 'N/A')} kW"],
        ["Shadow Risk:", data.get('shadow_risk', 'Unknown')],
        ["Orientation:", "Optimal" if data.get('orientation_ok') else "Suboptimal"],
        ["Feasibility:", "Suitable" if data.get('suitable') else "Not Recommended"]
    ]
    
    t = Table(system_data, colWidths=[100, 200])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TEXTCOLOR', (0,0), (0,-1), DARK_TEXT),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,3), (-1,3), 
         colors.green if data.get('suitable') else colors.red),
        ('TEXTCOLOR', (0,3), (-1,3), colors.white)
    ]))
    t.wrapOn(c, width, height)
    t.drawOn(c, 40, y-80)
    y -= 100
    
    # --- Financial Summary ---
    p = Paragraph("<b>3. FINANCIAL SUMMARY</b>", heading_style)
    p.wrapOn(c, width, height)
    p.drawOn(c, 40, y)
    y -= 30
    
    financial_data = [
        ["Monthly Generation:", f"{savings.get('monthly_generation_kwh', 'N/A')} kWh"],
        ["Monthly Savings:", fmt_currency(savings.get('monthly_savings'))],
        ["Total System Cost:", fmt_currency(savings.get('capex'))],
        ["Available Subsidy:", fmt_currency(savings.get('subsidy'))],
        ["Net Investment:", fmt_currency(savings.get('net_capex'))],
        ["Annual Maintenance:", fmt_currency(savings.get('o_and_m'))],
        ["Payback Period:", f"{int(savings.get('payback_years', 0)*12)} months"],
        ["25-Year ROI:", f"{savings.get('roi_percent_25yr', 'N/A')}%"]
    ]
    
    t = Table(financial_data, colWidths=[120, 180])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TEXTCOLOR', (0,0), (0,-1), DARK_TEXT),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('BACKGROUND', (0,2), (-1,2), LIGHT_BG),
        ('BACKGROUND', (0,4), (-1,4), LIGHT_BG),
        ('BACKGROUND', (0,6), (-1,6), LIGHT_BG),
    ]))
    t.wrapOn(c, width, height)
    t.drawOn(c, 40, y-160)
    y -= 180
    
    # --- Savings Chart ---
    p = Paragraph("<b>4. SAVINGS PROJECTION</b>", heading_style)
    p.wrapOn(c, width, height)
    p.drawOn(c, 40, y)
    y -= 30
    
    chart_path = os.path.join(output_dir, "savings_chart.png")
    create_savings_chart(savings, chart_path)
    try:
        c.drawImage(chart_path, 40, y-150, width=500, height=120)
    except:
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.red)
        c.drawString(40, y-20, "Savings projection chart not available")
    y -= 170
    
    # --- Footer ---
    c.setFont("Helvetica", 8)
    c.setFillColor(DARK_TEXT)
    c.drawString(40, 40, "ChainFly Energy Pvt. Ltd.")
    c.drawString(40, 30, "Phone: +91 70155 71891 | Email: contact@chainfly.co")
    c.drawCentredString(width/2, 20, "This proposal was auto-generated by ChainFly API , kindly contact us for further details")
    
    c.save()
    return file_path
