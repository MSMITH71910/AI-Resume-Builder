from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer, util
import PyPDF2
import spacy
import io
import re
from typing import Dict, List
import json
import openai
import os
from openai import OpenAI
from dotenv import load_dotenv

app = FastAPI(title="AI Resume Builder API", version="1.0.0")

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

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

def extract_name_from_text(text: str) -> str:
    """Extract name from resume text (usually first line)"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        # First non-empty line is usually the name
        first_line = lines[0]
        # Skip if it looks like a header or section
        if not any(word in first_line.lower() for word in ['resume', 'cv', 'curriculum', 'objective', 'summary']):
            return first_line
    return "Professional Candidate"

def extract_experience_entries(text: str) -> List[Dict[str, str]]:
    """Extract work experience entries from resume text"""
    entries = []
    lines = text.split('\n')
    
    # Look for experience section
    in_experience = False
    current_entry = {'title': '', 'company': '', 'dates': '', 'description': []}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if we're entering experience section
        if any(keyword in line.lower() for keyword in ['experience', 'work', 'employment', 'career']):
            if len(line) < 50:  # Likely a section header
                in_experience = True
                continue
        
        # Check if we're leaving experience section
        if in_experience and any(keyword in line.lower() for keyword in ['education', 'skills', 'projects', 'certifications']):
            if len(line) < 50:  # Likely a section header
                if current_entry['title'] or current_entry['company']:
                    entries.append(current_entry.copy())
                break
        
        if in_experience:
            # Try to identify job title, company, dates
            if '|' in line or ' at ' in line or ' - ' in line:
                # Likely a job title/company line
                if current_entry['title'] or current_entry['company']:
                    entries.append(current_entry.copy())
                    current_entry = {'title': '', 'company': '', 'dates': '', 'description': []}
                
                # Parse the line
                parts = re.split(r'\s*[\|\-]\s*', line)
                if len(parts) >= 2:
                    current_entry['title'] = parts[0].strip()
                    current_entry['company'] = parts[1].strip()
                    if len(parts) >= 3:
                        current_entry['dates'] = parts[2].strip()
            elif line.startswith('•') or line.startswith('-'):
                # Achievement/responsibility bullet point
                current_entry['description'].append(line)
            elif current_entry['title'] and not current_entry['dates'] and any(char.isdigit() for char in line):
                # Might be dates
                current_entry['dates'] = line
            elif current_entry['title']:
                # Additional description
                current_entry['description'].append(line)
    
    # Add the last entry
    if current_entry['title'] or current_entry['company']:
        entries.append(current_entry)
    
    return entries

def extract_education_entries(text: str) -> List[str]:
    """Extract education entries from resume text"""
    entries = []
    lines = text.split('\n')
    
    in_education = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if we're entering education section
        if any(keyword in line.lower() for keyword in ['education', 'academic', 'qualification', 'degree']):
            if len(line) < 50:  # Likely a section header
                in_education = True
                continue
        
        # Check if we're leaving education section
        if in_education and any(keyword in line.lower() for keyword in ['experience', 'skills', 'projects', 'certifications']):
            if len(line) < 50:  # Likely a section header
                break
        
        if in_education:
            entries.append(line)
    
    return entries

def extract_actual_skills_from_text(text: str) -> List[str]:
    """Extract actual skills mentioned in the resume text"""
    # Common technical skills to look for
    common_skills = [
        'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
        'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask',
        'HTML', 'CSS', 'SQL', 'MongoDB', 'PostgreSQL', 'MySQL',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git', 'Linux',
        'Machine Learning', 'AI', 'Data Analysis', 'Excel', 'Word', 'PowerPoint'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in common_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills

def is_technical_skill(skill: str) -> bool:
    """Determine if a skill is technical or soft skill"""
    technical_keywords = [
        'python', 'javascript', 'java', 'react', 'node', 'sql', 'html', 'css',
        'aws', 'docker', 'git', 'linux', 'database', 'api', 'framework',
        'programming', 'development', 'software', 'web', 'mobile', 'cloud'
    ]
    
    return any(keyword in skill.lower() for keyword in technical_keywords)

def create_intelligent_summary(experience_entries: List[Dict], actual_skills: List[str], 
                             matching_skills: List[str], missing_skills: List[str], job_desc: str) -> str:
    """Create an intelligent professional summary based on actual experience"""
    
    # Determine years of experience
    years_exp = "experienced"
    if experience_entries:
        if len(experience_entries) >= 3:
            years_exp = "senior"
        elif len(experience_entries) >= 2:
            years_exp = "experienced"
        else:
            years_exp = "motivated"
    
    # Determine primary field
    field = "professional"
    job_lower = job_desc.lower()
    if any(word in job_lower for word in ['developer', 'software', 'programming']):
        field = "software developer"
    elif any(word in job_lower for word in ['analyst', 'data', 'business intelligence']):
        field = "analyst"
    elif any(word in job_lower for word in ['manager', 'management', 'lead']):
        field = "professional"
    
    # Build summary
    summary_parts = []
    summary_parts.append(f"{years_exp.title()} {field}")
    
    if matching_skills:
        top_skills = matching_skills[:3]
        summary_parts.append(f"with expertise in {', '.join(top_skills)}")
    
    if missing_skills:
        priority_missing = missing_skills[:2]
        summary_parts.append(f"Seeking to expand capabilities in {', '.join(priority_missing)}")
    
    summary_parts.append("Committed to delivering high-quality results and continuous professional development")
    
    return ". ".join(summary_parts) + "."

def rewrite_experience_entry(entry: Dict[str, str], job_desc: str, matching_skills: List[str]) -> List[str]:
    """Rewrite a single experience entry with improvements"""
    result = []
    
    # Job title and company
    if entry['title'] and entry['company']:
        title_line = f"{entry['title']} | {entry['company']}"
        if entry['dates']:
            title_line += f" | {entry['dates']}"
        result.append(title_line)
    
    # Enhanced descriptions
    if entry['description']:
        for desc in entry['description']:
            # Enhance bullet points with action verbs and metrics
            enhanced_desc = enhance_bullet_point(desc, matching_skills)
            result.append(enhanced_desc)
    else:
        # Generate generic achievements if none provided
        result.append("• Contributed to team objectives and organizational goals")
        result.append("• Collaborated effectively with cross-functional teams")
    
    return result

def enhance_bullet_point(bullet: str, matching_skills: List[str]) -> str:
    """Enhance a bullet point with better action verbs and structure"""
    
    # Remove existing bullet if present
    clean_bullet = bullet.lstrip('•-').strip()
    
    # Action verbs to replace weak verbs
    action_verbs = {
        'worked': 'collaborated',
        'did': 'executed',
        'made': 'developed',
        'helped': 'assisted',
        'used': 'utilized',
        'was responsible': 'managed'
    }
    
    # Replace weak verbs
    enhanced = clean_bullet
    for weak, strong in action_verbs.items():
        enhanced = re.sub(rf'\b{weak}\b', strong, enhanced, flags=re.IGNORECASE)
    
    # Ensure it starts with capital letter
    if enhanced:
        enhanced = enhanced[0].upper() + enhanced[1:]
    
    return f"• {enhanced}"

def generate_improved_resume_with_ai(resume_text: str, job_desc: str, missing_skills: List[str], 
                                   matching_skills: List[str]) -> str:
    """Generate AI-powered resume rewrite using OpenAI GPT"""
    
    try:
        # Create a comprehensive prompt for AI resume rewriting
        prompt = f"""
You are an expert resume writer and career coach. Your task is to completely rewrite and optimize a resume to perfectly match a specific job description.

ORIGINAL RESUME:
{resume_text}

TARGET JOB DESCRIPTION:
{job_desc}

ANALYSIS RESULTS:
- Matching Skills: {', '.join(matching_skills) if matching_skills else 'None identified'}
- Missing Skills: {', '.join(missing_skills) if missing_skills else 'None identified'}

INSTRUCTIONS:
1. COMPLETELY REWRITE the resume content (don't just suggest changes)
2. Tailor ALL experience descriptions to highlight relevance to the target job
3. Rewrite bullet points using strong action verbs and quantifiable achievements
4. Enhance job titles and descriptions to show relevance to target role
5. Create a compelling professional summary that speaks directly to the job requirements
6. Reorganize and enhance skills section to prioritize job-relevant abilities
7. Add missing skills as "developing" or "familiar with" where appropriate
8. Use professional formatting with clear sections and bullet points
9. Ensure the rewritten resume tells a story of progression toward the target role
10. Make every word count - remove fluff and add substance

FORMATTING REQUIREMENTS:
- Use clear section headers with emojis (🎯 PROFESSIONAL SUMMARY, 💼 EXPERIENCE, 🛠️ SKILLS, 🎓 EDUCATION)
- Use bullet points (•) for all lists
- Include contact information at the top
- Professional, ATS-friendly formatting
- Quantify achievements wherever possible

OUTPUT: Provide ONLY the complete rewritten resume, no explanations or comments.
"""

        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert resume writer who creates compelling, job-tailored resumes that get interviews."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        ai_resume = response.choices[0].message.content.strip()
        
        # Add optimization suggestions at the end
        ai_resume += "\n\n💡 AI OPTIMIZATION NOTES\n" + "-" * 25
        ai_resume += "\nThis resume has been AI-optimized for maximum job relevance:"
        
        if missing_skills:
            ai_resume += f"\n• Added focus on: {', '.join(missing_skills[:3])}"
        if matching_skills:
            ai_resume += f"\n• Emphasized your strengths in: {', '.join(matching_skills[:3])}"
        
        ai_resume += "\n• Enhanced with industry-specific keywords and phrases"
        ai_resume += "\n• Optimized for Applicant Tracking Systems (ATS)"
        ai_resume += "\n• Quantified achievements and used strong action verbs"
        
        return ai_resume
        
    except Exception as e:
        print(f"AI resume generation failed: {e}")
        # Fallback to original method if AI fails
        return generate_improved_resume_fallback(resume_text, job_desc, missing_skills, matching_skills)

def generate_improved_resume_fallback(resume_text: str, job_desc: str, missing_skills: List[str], 
                                    matching_skills: List[str]) -> str:
    """Fallback resume generation if AI fails"""
    
    # Extract contact information
    contact_info = extract_contact_info(resume_text)
    name = contact_info['name'] or extract_name_from_text(resume_text)
    email = contact_info['email']
    phone = contact_info['phone']
    
    # Extract experience and education
    experience_entries = extract_experience_entries(resume_text)
    education_entries = extract_education_entries(resume_text)
    actual_skills = extract_actual_skills_from_text(resume_text)
    
    # Generate improved resume
    improved_resume = []
    
    # Professional Header
    improved_resume.append("=" * 60)
    improved_resume.append(f"  {name.upper()}")
    improved_resume.append("=" * 60)
    
    contact_line = []
    if email:
        contact_line.append(f"📧 {email}")
    if phone:
        contact_line.append(f"📱 {phone}")
    
    if contact_line:
        improved_resume.append(" | ".join(contact_line))
    improved_resume.append("")
    
    # Professional Summary
    improved_resume.append("🎯 PROFESSIONAL SUMMARY")
    improved_resume.append("-" * 25)
    summary = create_intelligent_summary(experience_entries, actual_skills, matching_skills, missing_skills, job_desc)
    improved_resume.append(summary)
    improved_resume.append("")
    
    # Skills Section
    improved_resume.append("🛠️ TECHNICAL SKILLS")
    improved_resume.append("-" * 20)
    
    all_skills = list(set(actual_skills + matching_skills))
    priority_missing = [skill for skill in missing_skills[:4] if skill.lower() not in [s.lower() for s in all_skills]]
    
    if all_skills:
        tech_skills = [s for s in all_skills if is_technical_skill(s)]
        soft_skills = [s for s in all_skills if not is_technical_skill(s)]
        
        if tech_skills:
            improved_resume.append(f"• Technical: {', '.join(tech_skills)}")
        if priority_missing:
            improved_resume.append(f"• Developing: {', '.join(priority_missing)}")
        if soft_skills:
            improved_resume.append(f"• Additional: {', '.join(soft_skills)}")
    
    improved_resume.append("")
    
    # Experience Section
    if experience_entries:
        improved_resume.append("💼 PROFESSIONAL EXPERIENCE")
        improved_resume.append("-" * 28)
        
        for entry in experience_entries:
            improved_entry = rewrite_experience_entry(entry, job_desc, matching_skills)
            improved_resume.extend(improved_entry)
            improved_resume.append("")
    
    # Education Section
    if education_entries:
        improved_resume.append("🎓 EDUCATION")
        improved_resume.append("-" * 12)
        
        for entry in education_entries:
            improved_resume.append(f"• {entry}")
        improved_resume.append("")
    
    return '\n'.join(improved_resume)

def generate_improved_resume(resume_text: str, job_desc: str, missing_skills: List[str], 
                           matching_skills: List[str]) -> str:
    """Generate a completely rewritten and improved version of the resume"""
    
    # Extract contact information
    contact_info = extract_contact_info(resume_text)
    
    # Parse resume into structured sections
    lines = resume_text.split('\n')
    
    # Extract actual content from resume
    name = contact_info['name'] or extract_name_from_text(resume_text)
    email = contact_info['email']
    phone = contact_info['phone']
    
    # Extract experience entries
    experience_entries = extract_experience_entries(resume_text)
    
    # Extract education entries  
    education_entries = extract_education_entries(resume_text)
    
    # Extract actual skills from resume text
    actual_skills = extract_actual_skills_from_text(resume_text)
    
    # Generate improved resume
    improved_resume = []
    
    # Professional Header
    improved_resume.append("=" * 60)
    improved_resume.append(f"  {name.upper()}")
    improved_resume.append("=" * 60)
    
    contact_line = []
    if email:
        contact_line.append(f"📧 {email}")
    if phone:
        contact_line.append(f"📱 {phone}")
    
    if contact_line:
        improved_resume.append(" | ".join(contact_line))
    improved_resume.append("")
    
    # Professional Summary (Rewritten based on actual content)
    improved_resume.append("🎯 PROFESSIONAL SUMMARY")
    improved_resume.append("-" * 25)
    
    # Create intelligent summary based on actual experience
    summary = create_intelligent_summary(experience_entries, actual_skills, matching_skills, missing_skills, job_desc)
    improved_resume.append(summary)
    improved_resume.append("")
    
    # Technical Skills (Enhanced with actual skills)
    improved_resume.append("🛠️ TECHNICAL SKILLS")
    improved_resume.append("-" * 20)
    
    # Combine actual skills with job-relevant skills
    all_skills = list(set(actual_skills + matching_skills))
    
    # Add high-priority missing skills as "developing" or "familiar"
    priority_missing = [skill for skill in missing_skills[:4] if skill.lower() not in [s.lower() for s in all_skills]]
    
    if all_skills:
        # Categorize skills intelligently
        tech_skills = [s for s in all_skills if is_technical_skill(s)]
        soft_skills = [s for s in all_skills if not is_technical_skill(s)]
        
        if tech_skills:
            improved_resume.append(f"• Technical: {', '.join(tech_skills)}")
        if priority_missing:
            improved_resume.append(f"• Developing: {', '.join(priority_missing)}")
        if soft_skills:
            improved_resume.append(f"• Additional: {', '.join(soft_skills)}")
    
    improved_resume.append("")
    
    # Professional Experience (Completely rewritten)
    if experience_entries:
        improved_resume.append("💼 PROFESSIONAL EXPERIENCE")
        improved_resume.append("-" * 28)
        
        for entry in experience_entries:
            # Rewrite each experience entry
            improved_entry = rewrite_experience_entry(entry, job_desc, matching_skills)
            improved_resume.extend(improved_entry)
            improved_resume.append("")
    
    # Education (Reformatted)
    if education_entries:
        improved_resume.append("🎓 EDUCATION")
        improved_resume.append("-" * 12)
        
        for entry in education_entries:
            improved_resume.append(f"• {entry}")
        improved_resume.append("")
    
    # Optimization suggestions
    improved_resume.append("💡 OPTIMIZATION SUGGESTIONS")
    improved_resume.append("-" * 28)
    improved_resume.append("Based on the job description analysis:")
    
    if missing_skills:
        improved_resume.append(f"• Consider highlighting experience with: {', '.join(missing_skills[:5])}")
    if matching_skills:
        improved_resume.append(f"• Emphasize your expertise in: {', '.join(matching_skills[:3])}")
    
    improved_resume.append("• Quantify achievements with specific metrics and results")
    improved_resume.append("• Use action verbs and job-specific keywords")
    improved_resume.append("• Tailor your summary to match the job requirements")
    
    return '\n'.join(improved_resume)

def extract_text_from_pdf(file):
    """Extract text from PDF with enhanced error handling and multiple methods"""
    try:
        # Method 1: Try PyPDF2 with strict=False
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file), strict=False)
            text = ""
            for page in reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception:
                    continue
            
            if text.strip():
                return text.strip()
        except Exception:
            pass
        
        # Method 2: Try with different PyPDF2 settings
        try:
            file_obj = io.BytesIO(file)
            reader = PyPDF2.PdfReader(file_obj)
            text = ""
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception:
                    # Skip problematic pages
                    continue
            
            if text.strip():
                return text.strip()
        except Exception:
            pass
        
        # If all methods fail, provide helpful error message
        raise ValueError("Unable to extract text from this PDF. The file may be corrupted, password-protected, or contain only images. Please try a different PDF or convert it to text format.")
        
    except Exception as e:
        if "EOF marker not found" in str(e):
            raise HTTPException(
                status_code=400, 
                detail="PDF file appears to be corrupted or incomplete. Please try re-saving or re-exporting your PDF and upload again."
            )
        elif "password" in str(e).lower():
            raise HTTPException(
                status_code=400, 
                detail="This PDF is password-protected. Please remove the password and try again."
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Error processing PDF: {str(e)}. Please try a different PDF file or paste your resume text directly."
            )

@app.post("/tailor-resume")
async def tailor_resume(
    resume: UploadFile = File(...),
    job_desc: str = Form(...)
):
    """Analyze PDF resume against job description and provide tailoring suggestions"""
    
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
        
        # Generate AI-powered improved resume
        improved_resume = generate_improved_resume_with_ai(resume_text, job_desc, missing_skills, matching_skills)
        
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@app.post("/tailor-resume-text")
async def tailor_resume_text(
    resume_text: str = Form(...),
    job_desc: str = Form(...)
):
    """Analyze resume text against job description and provide tailoring suggestions"""
    
    # Validate inputs
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty")
    
    if not job_desc.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
    
    try:
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
        
        # Generate AI-powered improved resume
        improved_resume = generate_improved_resume_with_ai(resume_text, job_desc, missing_skills, matching_skills)
        
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

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