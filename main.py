from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer, util
import PyPDF2
import spacy
import io
import re
from typing import Dict, List
import json

app = FastAPI(title="AI Resume Builder API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

nlp = spacy.load("en_core_web_sm")


def extract_skills(text):
    """Extract skills using a combination of NER and keyword matching"""
    doc = nlp(text)
    skills = []
    
    # Common technical skills keywords
    tech_skills = [
        'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'html', 'css',
        'machine learning', 'data analysis', 'project management', 'leadership',
        'communication', 'teamwork', 'problem solving', 'git', 'docker', 'kubernetes',
        'aws', 'azure', 'gcp', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'fastapi',
        'django', 'flask', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
        'agile', 'scrum', 'devops', 'ci/cd', 'testing', 'debugging', 'api', 'rest',
        'graphql', 'microservices', 'cloud computing', 'data science', 'analytics'
    ]
    
    # Extract entities that might be skills
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "LANGUAGE", "PERSON"]:
            # Filter for technology-related entities
            if any(tech in ent.text.lower() for tech in ['python', 'java', 'react', 'aws', 'google', 'microsoft']):
                skills.append(ent.text)
    
    # Extract skills using keyword matching
    text_lower = text.lower()
    for skill in tech_skills:
        if skill in text_lower:
            skills.append(skill.title())
    
    # Extract noun phrases that might be skills
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) <= 3 and len(chunk.text) > 2:
            # Check if it looks like a technical term
            if any(char.isupper() for char in chunk.text) or any(tech in chunk.text.lower() for tech in tech_skills[:10]):
                skills.append(chunk.text)
    
    return list(set(skills))

def parse_resume_sections(text: str) -> Dict[str, str]:
    """Parse resume text into structured sections"""
    sections = {
        'contact': '',
        'summary': '',
        'experience': '',
        'education': '',
        'skills': '',
        'other': ''
    }
    
    # Common section headers
    section_patterns = {
        'contact': r'(contact|personal|info)',
        'summary': r'(summary|objective|profile|about)',
        'experience': r'(experience|work|employment|career|professional)',
        'education': r'(education|academic|qualification|degree)',
        'skills': r'(skills|technical|competenc|abilities)',
        'projects': r'(projects|portfolio)',
        'certifications': r'(certification|certificate|license)',
        'achievements': r'(achievement|award|honor|accomplishment)'
    }
    
    lines = text.split('\n')
    current_section = 'other'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a section header
        line_lower = line.lower()
        section_found = False
        
        for section, pattern in section_patterns.items():
            if re.search(pattern, line_lower) and len(line) < 50:
                current_section = section
                section_found = True
                break
        
        if not section_found:
            # Add content to current section
            if current_section in sections:
                sections[current_section] += line + '\n'
            else:
                sections['other'] += line + '\n'
    
    return sections

def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract contact information from resume text"""
    contact_info = {
        'name': '',
        'email': '',
        'phone': '',
        'location': '',
        'linkedin': '',
        'github': ''
    }
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info['email'] = email_match.group()
    
    # Phone pattern
    phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        contact_info['phone'] = phone_match.group()
    
    # LinkedIn pattern
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        contact_info['linkedin'] = linkedin_match.group()
    
    # GitHub pattern
    github_pattern = r'github\.com/[\w-]+'
    github_match = re.search(github_pattern, text, re.IGNORECASE)
    if github_match:
        contact_info['github'] = github_match.group()
    
    # Extract name (first few words that look like a name)
    lines = text.split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if line and len(line.split()) <= 4 and not any(char.isdigit() for char in line):
            if '@' not in line and 'http' not in line.lower():
                contact_info['name'] = line
                break
    
    return contact_info

def generate_improved_resume(resume_text: str, job_desc: str, missing_skills: List[str], 
                           matching_skills: List[str]) -> str:
    """Generate an improved version of the resume"""
    
    # Parse the original resume
    sections = parse_resume_sections(resume_text)
    contact_info = extract_contact_info(resume_text)
    
    # Generate improved resume
    improved_resume = []
    
    # Header with contact info
    improved_resume.append("=" * 60)
    improved_resume.append(f"  {contact_info['name'].upper() or 'YOUR NAME'}")
    improved_resume.append("=" * 60)
    
    contact_line = []
    if contact_info['email']:
        contact_line.append(f"📧 {contact_info['email']}")
    if contact_info['phone']:
        contact_line.append(f"📱 {contact_info['phone']}")
    if contact_info['linkedin']:
        contact_line.append(f"💼 {contact_info['linkedin']}")
    if contact_info['github']:
        contact_line.append(f"💻 {contact_info['github']}")
    
    if contact_line:
        improved_resume.append(" | ".join(contact_line))
    improved_resume.append("")
    
    # Professional Summary
    improved_resume.append("🎯 PROFESSIONAL SUMMARY")
    improved_resume.append("-" * 25)
    
    if sections['summary'].strip():
        # Enhance existing summary with job-relevant keywords
        summary = sections['summary'].strip()
        # Add missing skills context
        if missing_skills:
            summary += f" Seeking to leverage expertise and develop skills in {', '.join(missing_skills[:3])}."
    else:
        # Generate a basic summary
        summary = f"Results-driven professional with expertise in {', '.join(matching_skills[:3]) if matching_skills else 'various technologies'}. "
        summary += f"Passionate about delivering high-quality solutions and continuously learning new technologies including {', '.join(missing_skills[:2]) if missing_skills else 'emerging tools'}."
    
    improved_resume.append(summary)
    improved_resume.append("")
    
    # Skills Section (Enhanced)
    improved_resume.append("🛠️ TECHNICAL SKILLS")
    improved_resume.append("-" * 20)
    
    all_skills = matching_skills.copy()
    # Add some missing skills as "learning" or "familiar with"
    if missing_skills:
        learning_skills = missing_skills[:3]
        all_skills.extend([f"{skill} (Learning)" for skill in learning_skills])
    
    if all_skills:
        # Group skills by category (basic categorization)
        tech_skills = [s for s in all_skills if any(tech in s.lower() for tech in 
                      ['python', 'java', 'javascript', 'react', 'node', 'sql', 'html', 'css', 'git'])]
        other_skills = [s for s in all_skills if s not in tech_skills]
        
        if tech_skills:
            improved_resume.append(f"• Programming & Technologies: {', '.join(tech_skills)}")
        if other_skills:
            improved_resume.append(f"• Additional Skills: {', '.join(other_skills)}")
    else:
        improved_resume.append("• [Add your technical skills here]")
    
    improved_resume.append("")
    
    # Experience Section
    if sections['experience'].strip():
        improved_resume.append("💼 PROFESSIONAL EXPERIENCE")
        improved_resume.append("-" * 28)
        
        # Clean up and format experience
        experience_text = sections['experience'].strip()
        # Add bullet points if missing
        experience_lines = experience_text.split('\n')
        for line in experience_lines:
            line = line.strip()
            if line:
                if not line.startswith('•') and not line.startswith('-'):
                    if any(word in line.lower() for word in ['company', 'inc', 'corp', 'llc']) or len(line.split()) <= 6:
                        improved_resume.append(f"\n{line}")  # Company/title line
                    else:
                        improved_resume.append(f"• {line}")  # Achievement line
                else:
                    improved_resume.append(line)
        improved_resume.append("")
    
    # Education Section
    if sections['education'].strip():
        improved_resume.append("🎓 EDUCATION")
        improved_resume.append("-" * 12)
        improved_resume.append(sections['education'].strip())
        improved_resume.append("")
    
    # Additional sections
    for section_name, content in sections.items():
        if section_name not in ['contact', 'summary', 'experience', 'education', 'skills'] and content.strip():
            improved_resume.append(f"📋 {section_name.upper()}")
            improved_resume.append("-" * (len(section_name) + 4))
            improved_resume.append(content.strip())
            improved_resume.append("")
    
    # Job Match Optimization Tips
    improved_resume.append("💡 OPTIMIZATION SUGGESTIONS")
    improved_resume.append("-" * 28)
    improved_resume.append("Based on the job description analysis:")
    
    if missing_skills:
        improved_resume.append(f"• Consider highlighting experience with: {', '.join(missing_skills[:5])}")
    
    if matching_skills:
        improved_resume.append(f"• Emphasize your expertise in: {', '.join(matching_skills[:5])}")
    
    improved_resume.append("• Quantify achievements with specific metrics and results")
    improved_resume.append("• Use action verbs and job-specific keywords")
    improved_resume.append("• Tailor your summary to match the job requirements")
    
    return '\n'.join(improved_resume)

def extract_text_from_pdf(file):
    """Extract text from PDF with error handling"""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
        
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

@app.post("/tailor-resume")
async def tailor_resume(
    resume: UploadFile = File(...),
    job_desc: str = Form(...)
):
    """Analyze resume against job description and provide tailoring suggestions"""
    
    # Validate inputs
    if not resume.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    if not job_desc.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
    
    try:
        # Extract text from PDF resume
        resume_bytes = await resume.read()
        resume_text = extract_text_from_pdf(resume_bytes)
        
        # Extract skills from resume and job description
        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_desc)
        
        # Find missing and matching skills
        missing_skills = [skill for skill in job_skills if skill.lower() not in [rs.lower() for rs in resume_skills]]
        matching_skills = [skill for skill in job_skills if skill.lower() in [rs.lower() for rs in resume_skills]]
        
        # Calculate similarity
        embeddings = model.encode([resume_text, job_desc])
        similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
        
        # Generate recommendations
        recommendations = []
        if similarity < 0.7:
            recommendations.append("Consider adding more relevant keywords from the job description")
            recommendations.append("Highlight experiences that match the job requirements")
        if missing_skills:
            recommendations.append(f"Consider adding these skills: {', '.join(missing_skills[:5])}")
        if similarity >= 0.85:
            recommendations.append("Excellent match! Your resume aligns well with the job requirements")
        
        # Generate improved resume
        improved_resume = generate_improved_resume(resume_text, job_desc, missing_skills, matching_skills)
        
        # Return comprehensive results
        return {
            "similarity_score": similarity,
            "resume_text": resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text,
            "job_desc": job_desc,
            "resume_skills": resume_skills,
            "job_skills": job_skills,
            "missing_skills": missing_skills,
            "matching_skills": matching_skills,
            "recommendations": recommendations,
            "improved_resume": improved_resume,
            "analysis": {
                "total_resume_skills": len(resume_skills),
                "total_job_skills": len(job_skills),
                "skill_match_percentage": (len(matching_skills) / len(job_skills) * 100) if job_skills else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI Resume Builder API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "nlp_loaded": nlp is not None
    }