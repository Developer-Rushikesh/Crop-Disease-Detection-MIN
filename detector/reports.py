import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable,
)


def generate_pdf_report(prediction_data, image_abs_path=None):
    """
    Generates a professional, print-ready PDF diagnosis report in memory.
    
    Args:
        prediction_data (dict): Prediction dictionary from ml_model.predict_disease.
        image_abs_path (str, optional): Absolute filesystem path to the leaf image.
        
    Returns:
        io.BytesIO: Buffer containing the binary PDF stream.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    primary_color = colors.HexColor("#1b4332")
    accent_green = colors.HexColor("#2d6a4f")
    text_dark = colors.HexColor("#1b262c")
    text_muted = colors.HexColor("#5c6b73")
    bg_subtle = colors.HexColor("#f7faf7")
    border_color = colors.HexColor("#e2ece4")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=text_muted,
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=text_dark,
    )

    body_bold = ParagraphStyle(
        'DocBodyBold',
        parent=body_style,
        fontName='Helvetica-Bold',
    )

    disclaimer_style = ParagraphStyle(
        'DocDisclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#78350f"),
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>FloraScan AI</b><br/><font size=9 color='#2d6a4f'>Plant Pathology Diagnosis Report</font>", title_style),
            Paragraph(
                f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>"
                f"<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}<br/>"
                f"<b>System:</b> MobileNetV2 / PlantVillage",
                subtitle_style
            )
        ]
    ]
    header_table = Table(header_data, colWidths=[340, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_green, spaceAfter=14))

    # 2. Main Diagnosis Summary & Image Grid
    disease_info = prediction_data.get('disease_info', {})
    display_name = prediction_data.get('display_name', 'Unknown')
    plant_name = prediction_data.get('selected_plant', 'Plant')
    confidence = prediction_data.get('confidence', 0.0)
    scientific_name = disease_info.get('scientific_name', 'Solanum species')
    severity = disease_info.get('severity', 'None')
    is_healthy = disease_info.get('is_healthy', False)

    summary_rows = [
        [Paragraph("<b>Target Crop:</b>", body_style), Paragraph(str(plant_name), body_bold)],
        [Paragraph("<b>Predicted Condition:</b>", body_style), Paragraph(f"<b>{display_name}</b>", body_bold)],
        [Paragraph("<b>Scientific Name:</b>", body_style), Paragraph(f"<i>{scientific_name}</i>", body_style)],
        [Paragraph("<b>Condition Status:</b>", body_style), Paragraph("Healthy Foliage" if is_healthy else f"Pathogen Detected ({severity})", body_style)],
        [Paragraph("<b>Model Confidence:</b>", body_style), Paragraph(f"<b>{confidence}%</b>", body_bold)],
    ]

    summary_table = Table(summary_rows, colWidths=[130, 220])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_subtle),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    # Leaf Image Thumbnail
    image_element = None
    if image_abs_path and os.path.exists(image_abs_path):
        try:
            image_element = RLImage(image_abs_path, width=170, height=140)
        except Exception:
            image_element = Paragraph("<font color='#64748b'>[Leaf Image Attached]</font>", body_style)
    else:
        image_element = Paragraph("<font color='#64748b'>[Image Reference Available in App]</font>", body_style)

    overview_data = [[summary_table, image_element]]
    overview_table = Table(overview_data, colWidths=[360, 180])
    overview_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 14))

    # Warning Note if any
    warning_msg = prediction_data.get('warning_message')
    if warning_msg:
        warn_table = Table([[
            Paragraph(f"<b>Notice:</b> {warning_msg}", disclaimer_style)
        ]], colWidths=[540])
        warn_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef3c7")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#fde68a")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(warn_table)
        story.append(Spacer(1, 10))

    # 3. Top Predictions Breakdown Table
    top_3 = prediction_data.get('top_3', [])
    if top_3:
        story.append(Paragraph("<b>Top Machine Learning Predictions</b>", section_heading))
        pred_rows = [
            [
                Paragraph("<b>Rank</b>", body_bold),
                Paragraph("<b>Class Label</b>", body_bold),
                Paragraph("<b>Confidence Score</b>", body_bold)
            ]
        ]
        for rank, item in enumerate(top_3, 1):
            pred_rows.append([
                Paragraph(f"#{rank}", body_style),
                Paragraph(f"{item.get('display_name')} <font color='#64748b' size=7.5>({item.get('raw_name')})</font>", body_style),
                Paragraph(f"<b>{item.get('confidence')}%</b>", body_bold)
            ])
        pred_table = Table(pred_rows, colWidths=[50, 360, 130])
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e9f5ed")),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(pred_table)
        story.append(Spacer(1, 12))

    # 4. Symptoms & Prevention Guidance
    symptoms = disease_info.get('symptoms', [])
    prevention = disease_info.get('prevention', [])
    treatment = disease_info.get('treatment', [])

    guidance_data = []

    # Symptoms Column
    symptoms_text = ""
    for s in symptoms:
        symptoms_text += f"• {s}<br/>"
    if not symptoms_text:
        symptoms_text = "Foliage appears normal."

    # Prevention & Treatment Column
    pt_text = "<b>Prevention:</b><br/>"
    for p in prevention:
        pt_text += f"✓ {p}<br/>"
    pt_text += "<br/><b>Recommended Treatment:</b><br/>"
    for t in treatment:
        pt_text += f"→ {t}<br/>"

    guidance_table = Table([
        [Paragraph("<b>Key Visual Symptoms</b>", section_heading), Paragraph("<b>Care & Management Plan</b>", section_heading)],
        [Paragraph(symptoms_text, body_style), Paragraph(pt_text, body_style)]
    ], colWidths=[260, 280])
    guidance_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 1), (-1, 1), bg_subtle),
        ('BOX', (0, 1), (-1, 1), 1, border_color),
        ('TOPPADDING', (0, 1), (-1, 1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 8),
        ('LEFTPADDING', (0, 1), (-1, 1), 8),
        ('RIGHTPADDING', (0, 1), (-1, 1), 8),
    ]))
    story.append(guidance_table)
    story.append(Spacer(1, 14))

    # 5. Mandatory Academic / AI Disclaimer
    disclaimer_box = Table([[
        Paragraph(
            "<b>Disclaimer:</b> FloraScan AI produces automated predictions based on computer vision models "
            "trained on the PlantVillage research dataset. This report is intended for educational, academic, "
            "and preliminary screening purposes. It does not replace professional laboratory testing or direct "
            "evaluation by a certified agricultural extension officer.",
            disclaimer_style
        )
    ]], colWidths=[540])
    disclaimer_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(KeepTogether(disclaimer_box))

    doc.build(story)
    buffer.seek(0)
    return buffer
