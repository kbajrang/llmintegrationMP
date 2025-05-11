# utils/pdf_generator.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors


def generate_pdf(name, analysis):
    folder = "static/reports"
    os.makedirs(folder, exist_ok=True)
    filename = f"{name}_feedback_{int(datetime.now().timestamp())}.pdf"
    file_path = os.path.join(folder, filename)

    doc = SimpleDocTemplate(file_path, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=60, bottomMargin=60)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SectionTitle", fontSize=14, leading=18, textColor=colors.HexColor("#1d4ed8"), spaceAfter=6))
    styles.add(ParagraphStyle(name="Card", fontSize=11, leading=16, backColor=colors.whitesmoke, borderPadding=6,
                              borderColor=colors.HexColor("#d1d5db"), borderWidth=0.5, spaceBefore=6, spaceAfter=10))
    styles.add(ParagraphStyle(name="Label", fontSize=11, textColor=colors.HexColor("#334155"), spaceAfter=4))
    styles.add(ParagraphStyle(name="Heading", fontSize=18, leading=22, spaceAfter=14, textColor=colors.HexColor("#0f172a")))
    styles.add(ParagraphStyle(name="Highlight", fontSize=16, textColor=colors.green, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="FinalScore", fontSize=20, textColor=colors.HexColor("#4338ca"), alignment=TA_CENTER, spaceBefore=20, spaceAfter=12))

    story = []
    story.append(Paragraph("📄 Smart Interview Final Report", styles["Heading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#4f46e5")))
    story.append(Spacer(1, 16))

    scores = []
    if isinstance(analysis, dict) and "questions" in analysis:
        for idx, q in enumerate(analysis["questions"]):
            story.append(Paragraph(f"Q{idx + 1}. {q.get('question', '')}", styles["SectionTitle"]))
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
            story.append(Paragraph(f"Score: {score_str} / 10", styles["Label"]))
            story.append(Paragraph("Suggestion:", styles["Label"]))
            story.append(Paragraph(q.get("suggestion", ""), styles["Card"]))
            story.append(Spacer(1, 12))

    # Summary table
    if "summary_table" in analysis:
        story.append(PageBreak())
        story.append(Paragraph("📊 Summary Table", styles["Heading"]))
        table_data = [["Question", "Score"]] + analysis["summary_table"]
        table = Table(table_data, colWidths=[350, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.gray),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f0f9ff"))
        ]))
        story.append(table)

    # Final Score Section
    if scores:
        total = sum(scores)
        count = len(scores)
        avg = round((total / (count * 10)) * 100)
        grade = "Excellent" if avg >= 85 else "Good" if avg >= 70 else "Needs Improvement"

        story.append(PageBreak())
        story.append(Paragraph("🧠 Final Interview Analysis", styles["Heading"]))
        story.append(Paragraph(f"Total Questions Evaluated: {count}", styles["Label"]))
        story.append(Paragraph(f"Total Score: {total:.1f} / {count * 10}", styles["Label"]))
        story.append(Paragraph(f"<b>Average Score:</b> {avg}%", styles["FinalScore"]))
        story.append(Paragraph(f"💡 <b>Overall Remark:</b> {grade}", styles["Highlight"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(
            "This score reflects the interviewee’s overall performance in communication, confidence, coding, and behavioral questions.",
            styles["Card"]
        ))

    doc.build(story)
    return file_path
