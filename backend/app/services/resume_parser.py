from fastapi import UploadFile
import time
from typing import Dict, Any
import PyPDF2
import docx
import re
from datetime import datetime

async def parse_resume(file: UploadFile) -> Dict[str, Any]:
    """
    Parse a resume file and extract relevant information.
    Returns a dictionary containing the parsed information.
    """
    start_time = time.time()
    
    # Read file content based on file type
    content = await read_file_content(file)
    
    # Extract information
    analysis = {
        "skills": extract_skills(content),
        "experience": extract_experience(content),
        "education": extract_education(content),
        "summary": generate_summary(content),
        "recommendations": generate_recommendations(content),
        "job_titles": extract_job_titles(content),
        "years_of_experience": calculate_years_of_experience(content),
        "confidence_score": calculate_confidence_score(content),
        "processing_time": time.time() - start_time
    }
    
    return analysis

async def read_file_content(file: UploadFile) -> str:
    """Read content from different file types."""
    content = ""
    
    if file.content_type == "application/pdf":
        # Read PDF
        pdf_reader = PyPDF2.PdfReader(file.file)
        for page in pdf_reader.pages:
            content += page.extract_text()
    elif file.content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        # Read DOCX/DOC
        doc = docx.Document(file.file)
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
    else:
        # Read text file
        content = await file.read()
        content = content.decode("utf-8")
    
    return content

def extract_skills(content: str) -> list:
    """Extract skills from resume content."""
    # This is a placeholder implementation
    # In a real implementation, you would use NLP or ML to extract skills
    common_skills = [
        "Python", "Java", "JavaScript", "SQL", "React", "Node.js",
        "AWS", "Docker", "Kubernetes", "Git", "Agile", "Scrum"
    ]
    
    found_skills = []
    for skill in common_skills:
        if re.search(rf"\b{skill}\b", content, re.IGNORECASE):
            found_skills.append(skill)
    
    return found_skills

def extract_experience(content: str) -> list:
    """Extract work experience from resume content."""
    # This is a placeholder implementation
    # In a real implementation, you would use NLP to extract structured experience data
    experience_pattern = r"(?i)(.*?)\s*(\d{4})\s*-\s*(present|\d{4})\s*(.*?)(?=\n\n|\Z)"
    matches = re.finditer(experience_pattern, content)
    
    experiences = []
    for match in matches:
        experiences.append({
            "company": match.group(1).strip(),
            "start_date": datetime.strptime(match.group(2), "%Y"),
            "end_date": None if match.group(3).lower() == "present" else datetime.strptime(match.group(3), "%Y"),
            "description": match.group(4).strip()
        })
    
    return experiences

def extract_education(content: str) -> list:
    """Extract education information from resume content."""
    # This is a placeholder implementation
    # In a real implementation, you would use NLP to extract structured education data
    education_pattern = r"(?i)(.*?)\s*(\d{4})\s*-\s*(present|\d{4})\s*(.*?)(?=\n\n|\Z)"
    matches = re.finditer(education_pattern, content)
    
    education = []
    for match in matches:
        education.append({
            "institution": match.group(1).strip(),
            "start_date": datetime.strptime(match.group(2), "%Y"),
            "end_date": None if match.group(3).lower() == "present" else datetime.strptime(match.group(3), "%Y"),
            "degree": match.group(4).strip()
        })
    
    return education

def generate_summary(content: str) -> str:
    """Generate a summary of the resume content."""
    # This is a placeholder implementation
    # In a real implementation, you would use NLP to generate a meaningful summary
    sentences = content.split(".")
    return " ".join(sentences[:3]) + "."

def generate_recommendations(content: str) -> list:
    """Generate recommendations for improving the resume."""
    # This is a placeholder implementation
    # In a real implementation, you would use ML to generate personalized recommendations
    return [
        "Add more quantifiable achievements",
        "Include relevant certifications",
        "Highlight key projects"
    ]

def extract_job_titles(content: str) -> list:
    """Extract potential job titles from the resume content."""
    # This is a placeholder implementation
    # In a real implementation, you would use NLP to extract and classify job titles
    common_titles = [
        "Software Engineer", "Full Stack Developer", "Data Scientist",
        "Product Manager", "DevOps Engineer", "System Administrator"
    ]
    
    found_titles = []
    for title in common_titles:
        if re.search(rf"\b{title}\b", content, re.IGNORECASE):
            found_titles.append(title)
    
    return found_titles

def calculate_years_of_experience(content: str) -> float:
    """Calculate total years of experience from the resume content."""
    # This is a placeholder implementation
    # In a real implementation, you would use NLP to accurately calculate experience
    experience_pattern = r"(?i)(\d{4})\s*-\s*(present|\d{4})"
    matches = re.finditer(experience_pattern, content)
    
    total_years = 0
    for match in matches:
        start_year = int(match.group(1))
        end_year = datetime.now().year if match.group(2).lower() == "present" else int(match.group(2))
        total_years += end_year - start_year
    
    return total_years

def calculate_confidence_score(content: str) -> float:
    """Calculate confidence score for the extracted information."""
    # This is a placeholder implementation
    # In a real implementation, you would use ML to calculate confidence scores
    score = 0.0
    
    # Check for presence of key sections
    if re.search(r"(?i)experience|work history", content):
        score += 0.2
    if re.search(r"(?i)education|academic", content):
        score += 0.2
    if re.search(r"(?i)skills|technologies", content):
        score += 0.2
    if re.search(r"(?i)projects|portfolio", content):
        score += 0.2
    if re.search(r"(?i)summary|objective", content):
        score += 0.2
    
    return min(score, 1.0) 