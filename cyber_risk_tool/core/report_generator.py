import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(report_data: dict, output_path: str) -> str:
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = styles['Title']
    heading1 = styles['Heading1']
    heading2 = styles['Heading2']
    normal = styles['Normal']
    
    elements = []
    
    elements.append(Paragraph("Cyber Risk Underwriting Intelligence Report", title_style))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph(f"<b>Company:</b> {report_data.get('company_name', 'N/A')}", normal))
    elements.append(Paragraph(f"<b>Domain:</b> {report_data.get('domain', 'N/A')}", normal))
    elements.append(Paragraph(f"<b>Country:</b> {report_data.get('country', 'N/A')} | <b>Revenue:</b> {report_data.get('revenue_band', 'N/A')}", normal))
    
    gen_time = report_data.get('generated_at_local')
    if not gen_time:
        gen_time = report_data.get('generated_at', 'N/A')
    elements.append(Paragraph(f"<b>Generated At:</b> {gen_time}", normal))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Overall Risk Profile", heading1))
    
    manual_review = "Yes" if report_data.get('manual_review_required', False) else "No"
    placeholder = "Yes" if report_data.get('placeholder_detected', False) else "No"
    is_valid_domain = "Yes" if report_data.get('is_valid_domain', True) else "No"
    
    data = [
        ["Overall Score", f"{report_data.get('overall_score', 0):.2f}"],
        ["Risk Category", report_data.get('overall_risk_category', 'Unknown')],
        ["Confidence", f"{report_data.get('overall_confidence', 0)*100:.0f}%"],
        ["Evidence Quality", report_data.get('evidence_quality', 'N/A')],
        ["Domain Valid", is_valid_domain],
        ["Manual Review Req.", manual_review],
    ]
    if not report_data.get('is_valid_domain', True) and report_data.get('validation_error'):
        data.append(["Validation Error", report_data.get('validation_error')])
        
    if placeholder == "Yes":
        data.append(["Placeholder Detected", placeholder])
        data.append(["Business Validity", report_data.get('business_validity_status', 'N/A')])
        
    data.append(["Category Reason", report_data.get('category_reason', 'N/A')])
    t = Table(data, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("Underwriter Summary", heading2))
    elements.append(Paragraph(report_data.get('underwriter_summary', 'N/A').replace("\n", "<br/>"), normal))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Detailed Findings by Modifier", heading1))
    
    for mod in report_data.get('modifiers', []):
        title = f"<b>{mod.get('modifier_name')}</b>"
        if mod.get('status') == 'not_implemented_phase_2':
            title += " <font color='gray'>(Phase 2 - Excluded)</font>"
        elif mod.get('status') == 'partial_mvp':
            title += " <font color='#92400e'>(Partial MVP)</font>"
            
        elements.append(Paragraph(title, heading2))
        
        mod_data = [
            ["Status", mod.get('status', 'Unknown').replace('_', ' ').upper()],
            ["Score", str(mod.get('score')) if mod.get('status') != 'not_implemented_phase_2' else '-'],
            ["Category", mod.get('risk_category')],
            ["Verified", mod.get('verification_status')]
        ]
        t_mod = Table(mod_data, colWidths=[100, 350])
        t_mod.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(t_mod)
        elements.append(Spacer(1, 10))
        
        if mod.get('description'):
            elements.append(Paragraph(f"<b>Description:</b> {mod.get('description')}", normal))
        if mod.get('target_parameter'):
            elements.append(Paragraph(f"<b>Target Parameter:</b> {mod.get('target_parameter')}", normal))
        if mod.get('research_needed'):
            elements.append(Paragraph(f"<b>Research Needed:</b> {mod.get('research_needed')}", normal))
            
        elements.append(Spacer(1, 5))
        
        if mod.get('reason_for_score'):
            elements.append(Paragraph(f"<b>Scoring Reason:</b> {mod.get('reason_for_score')}", normal))
            elements.append(Spacer(1, 5))
        
        elements.append(Paragraph("<b>Findings:</b>", normal))
        for f in mod.get('findings', []):
            elements.append(Paragraph(f"- {f}", normal))
            
        if mod.get('modifier_name') == "Domain Encryption" and mod.get('raw_data'):
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("<b>Domain Encryption Details:</b>", normal))
            raw = mod.get('raw_data')
            details = [
                f"- Normalized Domain: {raw.get('normalized_domain')}",
                f"- HTTPS Working: {raw.get('https_working')}",
                f"- HTTP Redirects to HTTPS: {raw.get('redirects_to_https')}",
                f"- Final HTTPS URL: {raw.get('final_https_url')}",
                f"- HTTPS Status Code: {raw.get('https_status_code')}"
            ]
            if raw.get('access_restricted'):
                details.append(f"- Access Restricted: Yes")
                details.append(f"- Blocked Status Code: {raw.get('blocked_status_code')}")
                details.append(f"- Manual Verification Required: Yes")
                
            for d in details:
                elements.append(Paragraph(d, normal))
            
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>Recommendation:</b>", normal))
        elements.append(Paragraph(mod.get('recommendation', 'None'), normal))
        elements.append(Spacer(1, 15))

    doc.build(elements)
    return output_path
