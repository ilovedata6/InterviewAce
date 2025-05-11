from typing import Dict, Any
import os
import json
from datetime import datetime
import docx
from docx.shared import Inches
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.models.resume import Resume

async def export_to_pdf(resume: Resume, export_path: str) -> str:
    """Export resume to PDF format."""
    file_path = f"{export_path}.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph(resume.title, title_style))
    
    # Summary
    if resume.analysis and "summary" in resume.analysis:
        story.append(Paragraph("Summary", styles["Heading2"]))
        story.append(Paragraph(resume.analysis["summary"], styles["Normal"]))
        story.append(Spacer(1, 20))
    
    # Skills
    if resume.analysis and "skills" in resume.analysis:
        story.append(Paragraph("Skills", styles["Heading2"]))
        skills_text = ", ".join(resume.analysis["skills"])
        story.append(Paragraph(skills_text, styles["Normal"]))
        story.append(Spacer(1, 20))
    
    # Experience
    if resume.analysis and "experience" in resume.analysis:
        story.append(Paragraph("Experience", styles["Heading2"]))
        for exp in resume.analysis["experience"]:
            story.append(Paragraph(exp["company"], styles["Heading3"]))
            story.append(Paragraph(f"{exp['start_date'].year} - {exp['end_date'].year if exp['end_date'] else 'Present'}", styles["Normal"]))
            story.append(Paragraph(exp["description"], styles["Normal"]))
            story.append(Spacer(1, 10))
    
    # Education
    if resume.analysis and "education" in resume.analysis:
        story.append(Paragraph("Education", styles["Heading2"]))
        for edu in resume.analysis["education"]:
            story.append(Paragraph(edu["institution"], styles["Heading3"]))
            story.append(Paragraph(f"{edu['degree']} in {edu['field_of_study']}", styles["Normal"]))
            story.append(Paragraph(f"{edu['start_date'].year} - {edu['end_date'].year if edu['end_date'] else 'Present'}", styles["Normal"]))
            story.append(Spacer(1, 10))
    
    doc.build(story)
    return file_path

async def export_to_docx(resume: Resume, export_path: str) -> str:
    """Export resume to DOCX format."""
    file_path = f"{export_path}.docx"
    doc = docx.Document()
    
    # Title
    doc.add_heading(resume.title, 0)
    
    # Summary
    if resume.analysis and "summary" in resume.analysis:
        doc.add_heading("Summary", level=1)
        doc.add_paragraph(resume.analysis["summary"])
    
    # Skills
    if resume.analysis and "skills" in resume.analysis:
        doc.add_heading("Skills", level=1)
        doc.add_paragraph(", ".join(resume.analysis["skills"]))
    
    # Experience
    if resume.analysis and "experience" in resume.analysis:
        doc.add_heading("Experience", level=1)
        for exp in resume.analysis["experience"]:
            doc.add_heading(exp["company"], level=2)
            doc.add_paragraph(f"{exp['start_date'].year} - {exp['end_date'].year if exp['end_date'] else 'Present'}")
            doc.add_paragraph(exp["description"])
    
    # Education
    if resume.analysis and "education" in resume.analysis:
        doc.add_heading("Education", level=1)
        for edu in resume.analysis["education"]:
            doc.add_heading(edu["institution"], level=2)
            doc.add_paragraph(f"{edu['degree']} in {edu['field_of_study']}")
            doc.add_paragraph(f"{edu['start_date'].year} - {edu['end_date'].year if edu['end_date'] else 'Present'}")
    
    doc.save(file_path)
    return file_path

async def export_to_json(resume: Resume, export_path: str) -> str:
    """Export resume to JSON format."""
    file_path = f"{export_path}.json"
    
    # Create export data
    export_data = {
        "id": str(resume.id),
        "title": resume.title,
        "description": resume.description,
        "created_at": resume.created_at.isoformat(),
        "updated_at": resume.updated_at.isoformat(),
        "version": resume.version,
        "analysis": resume.analysis
    }
    
    # Write to file
    with open(file_path, "w") as f:
        json.dump(export_data, f, indent=2)
    
    return file_path

async def export_to_txt(resume: Resume, export_path: str) -> str:
    """Export resume to TXT format."""
    file_path = f"{export_path}.txt"
    
    with open(file_path, "w") as f:
        # Title
        f.write(f"{resume.title}\n")
        f.write("=" * len(resume.title) + "\n\n")
        
        # Summary
        if resume.analysis and "summary" in resume.analysis:
            f.write("Summary\n")
            f.write("-" * 7 + "\n")
            f.write(f"{resume.analysis['summary']}\n\n")
        
        # Skills
        if resume.analysis and "skills" in resume.analysis:
            f.write("Skills\n")
            f.write("-" * 6 + "\n")
            f.write(", ".join(resume.analysis["skills"]) + "\n\n")
        
        # Experience
        if resume.analysis and "experience" in resume.analysis:
            f.write("Experience\n")
            f.write("-" * 10 + "\n")
            for exp in resume.analysis["experience"]:
                f.write(f"{exp['company']}\n")
                f.write(f"{exp['start_date'].year} - {exp['end_date'].year if exp['end_date'] else 'Present'}\n")
                f.write(f"{exp['description']}\n\n")
        
        # Education
        if resume.analysis and "education" in resume.analysis:
            f.write("Education\n")
            f.write("-" * 9 + "\n")
            for edu in resume.analysis["education"]:
                f.write(f"{edu['institution']}\n")
                f.write(f"{edu['degree']} in {edu['field_of_study']}\n")
                f.write(f"{edu['start_date'].year} - {edu['end_date'].year if edu['end_date'] else 'Present'}\n\n")
    
    return file_path 