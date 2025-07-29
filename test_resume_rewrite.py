#!/usr/bin/env python3
"""
Test script to demonstrate the AI resume rewriting functionality
"""

from main import generate_improved_resume, extract_skills

# Sample resume text
sample_resume = """
John Doe
john.doe@email.com
(555) 123-4567

Objective
Looking for a software development position

Experience
Software Developer at Tech Corp
- Worked on web applications
- Used Python and JavaScript
- Collaborated with team members

Education
Bachelor of Science in Computer Science
University of Technology, 2020

Skills
Python, JavaScript, HTML, CSS
"""

# Sample job description
job_description = """
We are looking for a Senior Full Stack Developer to join our team.

Requirements:
- 3+ years of experience in web development
- Proficiency in Python, JavaScript, React, Node.js
- Experience with databases (SQL, MongoDB)
- Knowledge of cloud platforms (AWS, Azure)
- Strong problem-solving skills
- Experience with Docker and Kubernetes
- Agile/Scrum methodology experience

Responsibilities:
- Develop and maintain web applications
- Work with cross-functional teams
- Implement best practices for code quality
- Mentor junior developers
"""

def test_resume_rewrite():
    print("🧪 Testing AI Resume Rewriting Functionality")
    print("=" * 50)
    
    # Extract skills
    resume_skills = extract_skills(sample_resume)
    job_skills = extract_skills(job_description)
    
    print(f"📄 Resume Skills Found: {resume_skills}")
    print(f"💼 Job Skills Required: {job_skills}")
    
    # Find missing and matching skills
    missing_skills = [skill for skill in job_skills if skill.lower() not in [rs.lower() for rs in resume_skills]]
    matching_skills = [skill for skill in job_skills if skill.lower() in [rs.lower() for rs in resume_skills]]
    
    print(f"❌ Missing Skills: {missing_skills}")
    print(f"✅ Matching Skills: {matching_skills}")
    
    # Generate improved resume
    print("\n🤖 Generating AI-Enhanced Resume...")
    print("=" * 50)
    
    improved_resume = generate_improved_resume(sample_resume, job_description, missing_skills, matching_skills)
    
    print(improved_resume)
    
    print("\n" + "=" * 50)
    print("✨ Resume enhancement completed!")
    print("Key improvements:")
    print("• Professional formatting with emojis and sections")
    print("• Enhanced contact information display")
    print("• Improved professional summary")
    print("• Categorized skills section")
    print("• Better structured experience section")
    print("• Job-specific optimization suggestions")

if __name__ == "__main__":
    test_resume_rewrite()