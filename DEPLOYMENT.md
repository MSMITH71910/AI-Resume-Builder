# 🚀 AI Resume Builder - Deployment Guide

## 📋 Quick Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/MSMITH71910/AI-Resume-Builder.git
cd AI-Resume-Builder
```

### 2. Automated Setup (Recommended)
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Start Development Servers
```bash
chmod +x start_dev.sh
./start_dev.sh
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

## 🔧 Manual Setup

### Backend Setup
```bash
# Create virtual environment
python -m venv resume-env
source resume-env/bin/activate  # On Windows: resume-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd resume-builder

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🌐 Production Deployment

### Backend (FastAPI)
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Next.js)
```bash
cd resume-builder

# Build for production
npm run build

# Start production server
npm start
```

## 🐳 Docker Deployment (Optional)

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY resume-builder/package*.json ./
RUN npm ci --only=production

COPY resume-builder/ .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

## 🔒 Environment Variables

Create `.env` files for production:

### Backend `.env`
```env
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### Frontend `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
# For production: NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## 🚀 Cloud Deployment Options

### Vercel (Frontend)
1. Connect your GitHub repository to Vercel
2. Set environment variable: `NEXT_PUBLIC_API_URL`
3. Deploy automatically on push

### Railway/Render (Backend)
1. Connect your GitHub repository
2. Set Python buildpack
3. Add start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### AWS/Google Cloud/Azure
- Use container services (ECS, Cloud Run, Container Instances)
- Set up load balancers and auto-scaling
- Configure environment variables

## 🔍 Testing the Deployment

### Test Backend API
```bash
curl http://localhost:8000/health
```

### Test Frontend
1. Open http://localhost:3000
2. Upload a sample PDF resume
3. Paste a job description
4. Click "Tailor My Resume"
5. Verify AI-enhanced resume generation

## 🛠️ Troubleshooting

### Common Issues

1. **spaCy model not found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **CORS errors**
   - Check CORS_ORIGINS in backend
   - Verify API_URL in frontend

3. **Port conflicts**
   - Change ports in start_dev.sh
   - Update NEXT_PUBLIC_API_URL accordingly

4. **Memory issues**
   - Increase system memory for ML models
   - Consider using smaller transformer models

### Performance Optimization

1. **Backend**
   - Use model caching
   - Implement request queuing
   - Add Redis for session storage

2. **Frontend**
   - Enable Next.js image optimization
   - Implement code splitting
   - Add service worker for caching

## 📊 Monitoring

### Health Checks
- Backend: `GET /health`
- Frontend: Check page load and API connectivity

### Logging
- Backend: FastAPI automatic logging
- Frontend: Next.js built-in logging
- Add custom logging for AI operations

## 🔄 Updates

To update the application:
```bash
git pull origin main
./setup.sh  # Reinstall dependencies if needed
./start_dev.sh
```

## 📞 Support

If you encounter issues:
1. Check the logs in terminal
2. Verify all dependencies are installed
3. Ensure ports 3000 and 8000 are available
4. Check the GitHub repository for updates

---

**🎉 Your AI Resume Builder is now ready to help users create better resumes!**