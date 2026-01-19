# 🎯 FREE Deployment - Quick Reference

## Your Free Stack (Total: $0/month)

| Service | What For | Free Tier Limits |
|---------|----------|------------------|
| **Render.com** | Backend API | 750 hrs/month, 100GB bandwidth |
| **Vercel** | Frontend | Unlimited, 100GB bandwidth |
| **Supabase** | Database | 500MB storage, 50K users |

---

## 🚀 Deploy in 3 Commands

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/YOUR_USERNAME/cashflow-manager.git
git push -u origin main

# 2. Deploy Backend (do this in Render dashboard)
# - Connect GitHub repo
# - Set environment variables
# - Deploy

# 3. Deploy Frontend (do this in Vercel dashboard)
# - Connect GitHub repo
# - Set root to 'frontend'
# - Set environment variables
# - Deploy
```

---

## 🔑 Required Environment Variables

### Backend (Render.com) - 12 variables
```bash
ENVIRONMENT=production
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_JWT_SECRET=xxx
SUPABASE_DB_URL=postgresql://...
SECRET_KEY=generate-with-openssl-rand-hex-32
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=https://your-app.vercel.app
TRUSTED_HOSTS=your-backend.onrender.com
```

### Frontend (Vercel) - 3 variables
```bash
REACT_APP_API_URL=https://your-backend.onrender.com
REACT_APP_SUPABASE_URL=https://xxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJ...
```

---

## 📝 Configuration Files Created

✅ `render.yaml` - Backend deployment config  
✅ `vercel.json` - Frontend deployment config  
✅ `Procfile` - How to start the app  
✅ `runtime.txt` - Python version  
✅ `.env.example` - Template for environment variables  
✅ `DEPLOYMENT_GUIDE.md` - Complete step-by-step guide  
✅ `DEPLOYMENT_CHECKLIST.md` - Deployment checklist  
✅ `deploy-prep.sh` - Preparation script  

---

## ⚡ Quick Commands

### Generate Secret Key
```bash
openssl rand -hex 32
```

### Test Backend Locally
```bash
python main.py
# Visit: http://localhost:8000/health
```

### Test Frontend Locally
```bash
cd frontend
npm start
# Visit: http://localhost:3000
```

### Check Git Status
```bash
git status
```

### Run Deployment Prep Script
```bash
./deploy-prep.sh
```

---

## 🌐 Your URLs (Fill in after deployment)

- **Frontend**: `https://________________.vercel.app`
- **Backend**: `https://________________.onrender.com`
- **GitHub**: `https://github.com/________/cashflow-manager`

---

## 🐛 Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| Backend won't start | Check Render logs, verify env vars |
| Frontend can't connect | Update CORS in backend env vars |
| Database error | Check Supabase URL, verify password encoding |
| Cold start slow | Normal for free tier (30-60 sec first request) |

---

## 📊 Free Tier Limits

**Render Backend:**
- ⚠️ Spins down after 15 min inactivity
- First request after = slow (~30 sec)
- 750 hours/month (enough for 24/7!)

**Vercel Frontend:**
- ✅ Always fast (CDN cached)
- ✅ No sleep/spin down
- ✅ Unlimited projects

**Supabase Database:**
- ⚠️ Pauses after 7 days inactivity
- Automatically resumes on connection
- 500 MB storage limit

---

## 🔒 Security Checklist

- [x] Security headers enabled
- [x] Rate limiting active
- [x] Password strength validation (12+ chars)
- [x] Input sanitization
- [x] SQL injection protection
- [x] XSS prevention
- [x] CORS configured
- [x] HTTPS enabled (automatic)
- [ ] `.env` NOT in git (verify!)
- [ ] Strong SECRET_KEY generated

---

## 📚 Resources

- **Full Guide**: `DEPLOYMENT_GUIDE.md`
- **Checklist**: `DEPLOYMENT_CHECKLIST.md`
- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Supabase Docs**: https://supabase.com/docs

---

## 🆘 Need Help?

1. Check `DEPLOYMENT_GUIDE.md` for detailed steps
2. Review error logs in Render/Vercel dashboards
3. Verify environment variables are correct
4. Test locally first: `./deploy-prep.sh`

---

**Total Deployment Time**: ~20 minutes  
**Total Cost**: $0/month  
**Global Availability**: ✅  
**SSL/HTTPS**: ✅ (Automatic)  
**Auto-deploy on Git push**: ✅  

🎉 **Your production-ready app awaits!**
