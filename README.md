# AI Resume Builder

An intelligent resume analysis and tailoring tool that uses AI to match your resume against job descriptions and provide actionable recommendations.

## Features

- **PDF Resume Upload**: Upload your resume in PDF format
- **AI-Powered Analysis**: Uses sentence transformers for semantic similarity analysis
- **Skill Extraction**: Automatically extracts skills from both resume and job descriptions
- **Smart Recommendations**: Provides tailored suggestions to improve your resume
- **🆕 AI Resume Rewriting**: Generates an improved, better-structured version of your resume
- **Interactive Resume Comparison**: Toggle between original and AI-enhanced versions
- **Resume Download**: Download the improved resume as a text file
- **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS
- **Dark Mode Support**: Automatic dark/light mode switching

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Sentence Transformers**: For semantic similarity analysis
- **spaCy**: Natural language processing for skill extraction
- **PyPDF2**: PDF text extraction
- **CORS**: Cross-origin resource sharing support

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS v4**: Utility-first CSS framework
- **React Hooks**: Modern React state management

## Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Create and activate virtual environment:**
```bash
cd /home/msmith/AIResumeBuilder
python -m venv resume-env
source resume-env/bin/activate  # On Windows: resume-env\Scripts\activate
```

2. **Install Python dependencies:**
```bash
pip install fastapi uvicorn sentence-transformers PyPDF2 spacy python-multipart
python -m spacy download en_core_web_sm
```

3. **Start the backend server:**
```bash
python run_backend.py
```
The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd resume-builder
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm run dev
```
The frontend will be available at `http://localhost:3000`

## Usage

1. **Start both servers** (backend on port 8000, frontend on port 3000)
2. **Open your browser** to `http://localhost:3000`
3. **Upload your resume** in PDF format
4. **Paste the job description** you're applying for
5. **Click "Tailor My Resume"** to get analysis and recommendations
6. **View the AI-enhanced resume** with improved structure and formatting
7. **Toggle between original and improved versions** to see the differences
8. **Download the improved resume** for your job applications

## API Endpoints

### `POST /tailor-resume`
Analyzes a resume against a job description.

**Parameters:**
- `resume`: PDF file upload
- `job_desc`: Job description text

**Response:**
```json
{
  "similarity_score": 0.75,
  "resume_skills": ["Python", "React", "SQL"],
  "job_skills": ["Python", "JavaScript", "Docker"],
  "missing_skills": ["JavaScript", "Docker"],
  "matching_skills": ["Python"],
  "recommendations": ["Consider adding these skills: JavaScript, Docker"],
  "improved_resume": "============================================================\n  JOHN DOE\n============================================================\n📧 john@email.com | 📱 (555) 123-4567\n\n🎯 PROFESSIONAL SUMMARY\n-------------------------\nResults-driven professional with expertise in Python, React, SQL...",
  "analysis": {
    "total_resume_skills": 3,
    "total_job_skills": 3,
    "skill_match_percentage": 33.3
  }
}
```

### `GET /health`
Health check endpoint.

## Project Structure

```
AIResumeBuilder/
├── main.py                 # FastAPI backend
├── run_backend.py          # Backend startup script
├── resume-env/             # Python virtual environment
├── resume-builder/         # Next.js frontend
│   ├── app/
│   │   ├── globals.css     # Global styles
│   │   ├── layout.tsx      # Root layout
│   │   └── page.tsx        # Main page component
│   ├── package.json        # Frontend dependencies
│   └── tailwind.config.js  # Tailwind configuration
└── README.md              # This file
```

## Development

### Backend Development
- The backend uses FastAPI with automatic API documentation at `http://localhost:8000/docs`
- CORS is configured to allow requests from the frontend
- Error handling includes proper HTTP status codes and error messages

### Frontend Development
- Built with Next.js 15 using the App Router
- TypeScript for type safety
- Tailwind CSS for styling with dark mode support
- Responsive design for mobile and desktop

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Make sure you've activated the virtual environment and installed all dependencies
2. **CORS errors**: Ensure the backend is running on port 8000 and CORS is properly configured
3. **PDF extraction fails**: Make sure the PDF is not password-protected and contains extractable text
4. **spaCy model not found**: Run `python -m spacy download en_core_web_sm`

### Backend Logs
Check the FastAPI logs for detailed error information when requests fail.

### Frontend Logs
Open browser developer tools to see client-side errors and network requests.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.