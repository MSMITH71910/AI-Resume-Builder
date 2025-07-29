# 🚀 Deploy AI Resume Builder to Vercel

## 📋 Prerequisites
- GitHub account (✅ You have this)
- Vercel account (free tier available)
- Your repository: https://github.com/MSMITH71910/AI-Resume-Builder.git

## 🎯 Deployment Strategy

**Important**: Vercel is perfect for the frontend (Next.js), but the backend (Python FastAPI) needs a separate service. Here's the complete setup:

### Option 1: Frontend + Backend Separation (Recommended)
- **Frontend**: Deploy to Vercel
- **Backend**: Deploy to Railway, Render, or Heroku

### Option 2: Full-Stack on Single Platform
- Deploy everything to Railway or Render

## 🚀 Method 1: Vercel Frontend + Railway Backend

### Step 1: Deploy Backend to Railway

1. **Go to Railway**: https://railway.app
2. **Sign up** with GitHub
3. **Create New Project** → **Deploy from GitHub repo**
4. **Select**: `MSMITH71910/AI-Resume-Builder`
5. **Configure**:
   - **Root Directory**: Leave empty (uses root)
   - **Build Command**: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. **Environment Variables**:
   ```
   PYTHONPATH=/app
   PORT=8000
   ```
7. **Deploy** and note your backend URL (e.g., `https://your-app.railway.app`)

### Step 2: Deploy Frontend to Vercel

1. **Go to Vercel**: https://vercel.com
2. **Sign up** with GitHub
3. **Import Project** → **Import Git Repository**
4. **Select**: `MSMITH71910/AI-Resume-Builder`
5. **Configure**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `resume-builder`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
6. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-backend-url.railway.app
   ```
7. **Deploy**

## 🚀 Method 2: All-in-One Railway Deployment

1. **Go to Railway**: https://railway.app
2. **Create New Project** → **Deploy from GitHub repo**
3. **Select**: `MSMITH71910/AI-Resume-Builder`
4. **Add Custom Start Command**:
   ```bash
   pip install -r requirements.txt && python -m spacy download en_core_web_sm && cd resume-builder && npm install && npm run build && cd .. && python -c "
   import subprocess
   import threading
   import time
   
   def run_backend():
       subprocess.run(['uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'])
   
   def run_frontend():
       time.sleep(5)  # Wait for backend
       subprocess.run(['npm', 'start'], cwd='resume-builder')
   
   backend_thread = threading.Thread(target=run_backend)
   frontend_thread = threading.Thread(target=run_frontend)
   
   backend_thread.start()
   frontend_thread.start()
   
   backend_thread.join()
   frontend_thread.join()
   "
   ```

## 🔧 Configuration Files for Vercel

Let me create the necessary config files:

### vercel.json (for frontend)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "resume-builder/package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/resume-builder/$1"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url"
  }
}
```

### Railway Configuration
Create `railway.toml`:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"

[env]
PYTHONPATH = "/app"
```

## 🌍 Environment Variables Setup

### For Vercel (Frontend):
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

### For Railway (Backend):
```env
PORT=8000
PYTHONPATH=/app
CORS_ORIGINS=["https://your-vercel-app.vercel.app"]
```

## 🔄 Automatic Deployments

Both platforms support automatic deployments:
- **Push to main branch** → Automatic deployment
- **Pull requests** → Preview deployments
- **Environment-specific branches** → Staging deployments

## 🧪 Testing Your Deployment

1. **Backend Health Check**:
   ```bash
   curl https://your-backend-url.railway.app/health
   ```

2. **Frontend Access**:
   - Visit your Vercel URL
   - Test file upload
   - Test resume analysis

## 💰 Cost Considerations

### Free Tiers:
- **Vercel**: 100GB bandwidth, unlimited personal projects
- **Railway**: $5 credit monthly, pay-as-you-go after
- **Render**: 750 hours/month free tier

### Recommended for Production:
- **Vercel Pro**: $20/month (better performance)
- **Railway**: ~$5-20/month depending on usage

## 🚨 Important Notes

1. **CORS Configuration**: Update backend CORS settings with your Vercel domain
2. **API Limits**: Free tiers have request limits
3. **Cold Starts**: Serverless functions may have cold start delays
4. **File Size**: Vercel has 50MB deployment limit (our app is ~400KB ✅)

## 🔧 Troubleshooting

### Common Issues:
1. **CORS Errors**: Check environment variables
2. **Build Failures**: Verify Node.js version compatibility
3. **API Timeouts**: Backend cold starts on free tiers
4. **Memory Limits**: ML models need sufficient RAM

### Solutions:
- Use Railway for backend (better for Python/ML)
- Set proper environment variables
- Monitor deployment logs
- Test locally first

---

**🎉 Your AI Resume Builder will be live on the internet!**