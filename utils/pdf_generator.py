import os
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

def generate_pdf(name, analysis):
    folder = "static/reports"
    os.makedirs(folder, exist_ok=True)
    filename = "{}_feedback_{}.pdf".format(name, int(datetime.now().timestamp()))
    file_path = os.path.join(folder, filename)

    doc = SimpleDocTemplate(file_path, pagesize=landscape(A4),
                            rightMargin=30, leftMargin=30,
                            topMargin=40, bottomMargin=30)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CustomTitle", fontSize=24, alignment=TA_CENTER, textColor=colors.HexColor("#1e40af"), spaceAfter=16))
    styles.add(ParagraphStyle(name="Question", fontSize=14, leading=18, textColor=colors.HexColor("#7c3aed"), spaceAfter=8))
    styles.add(ParagraphStyle(name="Card", fontSize=12, leading=18, backColor=colors.HexColor("#e0f7fa"), borderPadding=12,
                              borderColor=colors.HexColor("#60a5fa"), borderWidth=1.2,
                              leftIndent=4, rightIndent=4, spaceBefore=10, spaceAfter=16))
    styles.add(ParagraphStyle(name="Label", fontSize=11, textColor=colors.HexColor("#334155"), spaceAfter=4))
    styles.add(ParagraphStyle(name="Section", fontSize=18, leading=22, spaceAfter=10, textColor=colors.HexColor("#0f172a"), alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="FinalScore", fontSize=18, textColor=colors.HexColor("#16a34a"), alignment=TA_CENTER, spaceBefore=12, spaceAfter=10))

    story = []
    story.append(Paragraph("🚀 Smart Interview AI Analysis Report", styles["CustomTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#7c3aed")))
    story.append(Spacer(1, 16))

    scores = []

    if isinstance(analysis, dict) and "questions" in analysis:
        for idx, q in enumerate(analysis["questions"]):
            story.append(Paragraph("Q{}. {}".format(idx + 1, q.get("question", "")), styles["Question"]))
            story.append(Paragraph("Answer:", styles["Label"]))
            story.append(Paragraph(q.get("answer", ""), styles["Card"]))
            story.append(Paragraph("Feedback:", styles["Label"]))
            story.append(Paragraph(q.get("feedback", ""), styles["Card"]))
            score_str = q.get("score", "0").replace("/10", "").strip()
            try:
                score = float(score_str)
                scores.append(score)
            except:
                pass
            story.append(Paragraph("Score: {} / 10".format(score_str), styles["Label"]))
            story.append(Paragraph("Suggestion:", styles["Label"]))
            story.append(Paragraph(q.get("suggestion", ""), styles["Card"]))
            story.append(Spacer(1, 20))

    if "summary_table" in analysis:
        story.append(PageBreak())
        story.append(Paragraph("📊 Performance Summary", styles["Section"]))
        table_data = [["Question", "Score"]] + analysis["summary_table"]
        table = Table(table_data, colWidths=[400, 120])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#7c3aed")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 1.2, colors.HexColor("#1e3a8a")),
            ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#e0f2fe")),
        ]))
        story.append(table)

    if scores:
        total = sum(scores)
        count = len(scores)
        avg = round((total / (count * 10)) * 100)
        grade = "Excellent" if avg >= 85 else "Good" if avg >= 70 else "Needs Improvement"

        story.append(PageBreak())
        story.append(Paragraph("📌 Final Interview Analysis", styles["Section"]))
        story.append(Paragraph("Total Questions Evaluated: <b>{}</b>".format(count), styles["Card"]))
        story.append(Paragraph("Total Score: <b>{:.1f} / {}</b>".format(total, count * 10), styles["Card"]))
        story.append(Paragraph("<b>Average Score:</b> {}%".format(avg), styles["FinalScore"]))
        story.append(Paragraph("🟢 <b>Overall Remark:</b> {}".format(grade), styles["FinalScore"]))
        story.append(Paragraph(
            "This evaluation covers your communication clarity, technical confidence, code explanations, problem solving, and long-term potential.",
            styles["Card"]
        ))

    doc.build(story)
    return file_path
