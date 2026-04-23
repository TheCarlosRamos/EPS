
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import hashlib, json

def gerar_pdf(data):
    path=f"dossie_{data['id']}.pdf"
    doc=SimpleDocTemplate(path,pagesize=A4)
    styles=getSampleStyleSheet()
    story=[]
    story.append(Paragraph('POLÍCIA CIVIL DO DISTRITO FEDERAL', styles['Title']))
    story.append(Paragraph('Dossiê OSINT', styles['Heading2']))
    story.append(PageBreak())
    story.append(Paragraph('1. Dados da Investigação', styles['Heading2']))
    for k,v in data.items():
        story.append(Paragraph(f"<b>{k}</b>: {v}", styles['Normal']))
    h=hashlib.sha256(json.dumps(data).encode()).hexdigest()
    story.append(PageBreak())
    story.append(Paragraph(f"Hash de Integridade: {h}", styles['Normal']))
    doc.build(story)
    return path
