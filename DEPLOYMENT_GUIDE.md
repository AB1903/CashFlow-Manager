# 🚀 FREE Deployment Guide - CashFlow Manager

This guide will help you deploy your CashFlow Manager application **completely free** using:
- **Backend**: Render.com (Free tier)
- **Frontend**: Vercel (Free tier)
- **Database**: Supabase (Free tier - already set up!)

Total Cost: **$0/month** 💰

---

## 📋 Prerequisites

Before you begin, you need:
1. ✅ A GitHub account
2. ✅ Your Supabase project (already created)
3. ✅ Git installed on your computer

---

## 🗂️ Step 1: Push Your Code to GitHub

### 1.1 Create a new GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Name it `cashflow-manager`
3. Keep it **Public** (required for free Render deployment)
4. **DO NOT** initialize with README (you already have one)
5. Click "Create repository"

### 1.2 Push your code

```bash
cd /Users/ankushbhatt/App

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - production ready"

# Add your GitHub repository as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/cashflow-manager.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**⚠️ Important**: Make sure `.env` is in `.gitignore` so your secrets are NOT pushed!

---

## 🖥️ Step 2: Deploy Backend to Render (FREE)

### 2.1 Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest option)
4. Authorize Render to access your GitHub

### 2.2 Deploy the Backend

1. Click "New +" → "Web Service"
2. Connect your `cashflow-manager` repository
3. Configure the service:

   **Basic Settings:**
   - Name: `cashflow-manager-api` (or any name you like)
   - Region: `Oregon (US West)` (or closest to you)
   - Branch: `main`
   - Root Directory: (leave blank)
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

   **Instance Type:**
   - Select **"Free"** ($0/month)
   - Note: Free tier spins down after 15 min of inactivity

4. Click "Advanced" → "Add Environment Variables"

   Add these variables (get values from your `.env` file):

   ```
   ENVIRONMENT=production
   SUPABASE_URL=your-supabase-url
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_JWT_SECRET=your-jwt-secret
   SUPABASE_DB_URL=your-database-url
   SECRET_KEY=generate-new-random-key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

   **IMPORTANT - CORS Settings:**
   ```
   ALLOWED_ORIGINS=http://localhost:3000
   TRUSTED_HOSTS=cashflow-manager-api.onrender.com
   ```
   *(We'll update ALLOWED_ORIGINS after deploying frontend)*

   **Generate SECRET_KEY:**
   ```bash
   # Run this in your terminal to generate a secure key:
   openssl rand -hex 32
   ```

5. Click "Create Web Service"

6. Wait 5-10 minutes for deployment to complete

7. Once deployed, you'll see: **"Your service is live 🎉"**

8. Note your backend URL: `https://cashflow-manager-api.onrender.com`

### 2.3 Test Your Backend

Open: `https://your-service-name.onrender.com/health`

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-18T...",
  "database": "connected"
}
```

✅ **Backend is now live!**

---

## 🌐 Step 3: Deploy Frontend to Vercel (FREE)

### 3.1 Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up"
3. Choose "Continue with GitHub"
4. Authorize Vercel

### 3.2 Deploy the Frontend

1. Click "Add New..." → "Project"
2. Import your `cashflow-manager` repository
3. Configure the project:

   **Framework Preset:** `Create React App`
   
   **Root Directory:** Click "Edit" → Select `frontend`
   
   **Build Settings:**
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `build` (auto-detected)
   - Install Command: `npm install` (auto-detected)

4. **Environment Variables** (click "Add")

   Add these:
   ```
   REACT_APP_API_URL=https://your-backend.onrender.com
   REACT_APP_SUPABASE_URL=https://your-project.supabase.co
   REACT_APP_SUPABASE_ANON_KEY=your-anon-key
   ```

   Replace with your actual:
   - Backend URL from Render (Step 2.3)
   - Supabase URL from your `.env` file
   - Supabase Anon Key from your `.env` file

5. Click "Deploy"

6. Wait 2-3 minutes for deployment

7. Once complete, you'll see: **"Congratulations! 🎉"**

8. Note your frontend URL: `https://your-app.vercel.app`

✅ **Frontend is now live!**

---

## 🔗 Step 4: Connect Frontend & Backend

### 4.1 Update CORS Settings

Now that you have your frontend URL, update backend CORS:

1. Go to Render Dashboard
2. Click on your backend service
3. Go to "Environment"
4. Find `ALLOWED_ORIGINS` variable
5. Click "Edit"
6. Update to:
   ```
   https://your-app.vercel.app,http://localhost:3000
   ```
7. Click "Save Changes"

8. Similarly, update `TRUSTED_HOSTS`:
   ```
   your-backend.onrender.com,your-app.vercel.app
   ```

9. Backend will automatically redeploy (takes 2-3 min)

### 4.2 Test Your App

1. Open: `https://your-app.vercel.app`
2. Try registering a new account
3. Try logging in
4. Try adding a transaction

✅ **Everything should work!**

---

## 🎯 Step 5: Custom Domain (Optional - FREE)

### For Frontend (Vercel):
1. In Vercel project → Settings → Domains
2. Add your domain (e.g., `cashflow.yourdomain.com`)
3. Follow DNS configuration instructions
4. SSL certificate is automatic & free!

### For Backend (Render):
1. Render free tier doesn't support custom domains
2. Upgrade to paid plan ($7/month) if needed
3. Or use the provided `.onrender.com` domain

---

## 📊 Free Tier Limitations

### Render (Backend)
- ✅ 750 hours/month (enough for 24/7)
- ✅ 512 MB RAM
- ✅ SSL certificate included
- ⚠️ Spins down after 15 min inactivity (first request takes ~30 sec)
- ✅ 100 GB bandwidth/month

### Vercel (Frontend)
- ✅ Unlimited websites
- ✅ 100 GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Automatic deployments from Git
- ✅ Global CDN

### Supabase (Database)
- ✅ 500 MB database space
- ✅ 2 GB bandwidth/month
- ✅ 50,000 monthly active users
- ✅ 500,000 Edge Function invocations

---

## 🔄 Automatic Deployments

Both platforms auto-deploy when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Update feature X"
git push origin main

# Render & Vercel will automatically deploy! 🎉
```

---

## 🐛 Troubleshooting

### Backend not starting?
- Check Render logs: Dashboard → your service → Logs
- Verify all environment variables are set
- Check if `requirements.txt` is in root directory

### Frontend can't connect to backend?
- Check `REACT_APP_API_URL` in Vercel environment variables
- Verify CORS settings in Render
- Open browser console (F12) to see errors

### Database connection failed?
- Verify `SUPABASE_DB_URL` is correct
- Check if password has special characters (must be URL-encoded)
- Ensure Row Level Security is configured

### 500 Internal Server Error?
- Check Render logs for Python errors
- Verify all environment variables match `.env.example`
- Ensure database schema is initialized

### Cold starts (slow first request)?
This is normal for free tier:
- Render spins down after 15 min inactivity
- First request wakes it up (~30-60 sec)
- Subsequent requests are fast
- Use a service like [UptimeRobot](https://uptimerobot.com) to ping every 10 min (keeps it warm)

---

## 🎓 Monitoring & Logs

### Backend Logs (Render):
1. Go to Render Dashboard
2. Click your service
3. Click "Logs" tab
4. See real-time logs

### Frontend Logs (Vercel):
1. Go to Vercel Dashboard
2. Click your project
3. Click "Deployments"
4. Click any deployment → "View Function Logs"

### Database (Supabase):
1. Go to Supabase Dashboard
2. Click "Table Editor" to see data
3. Click "Logs" for database logs
4. Click "Reports" for usage analytics

---

## 🔒 Security Checklist

Before going live, verify:

- [ ] `.env` file is in `.gitignore` (NOT pushed to GitHub)
- [ ] `SECRET_KEY` is randomly generated (not the default)
- [ ] `ENVIRONMENT=production` in Render
- [ ] CORS only allows your frontend domain
- [ ] Supabase Row Level Security is enabled
- [ ] SSL certificates are active (automatic on Render & Vercel)
- [ ] All environment variables are set correctly
- [ ] Database password uses URL-encoding for special chars

---

## 📈 Going Beyond Free Tier

When you're ready to scale:

### Render Upgrades:
- **Starter ($7/mo)**: No cold starts, custom domain, 1 GB RAM
- **Standard ($25/mo)**: 2 GB RAM, faster CPU

### Vercel Upgrades:
- **Pro ($20/mo)**: More bandwidth, analytics, team features
- Free tier is usually sufficient for most apps!

### Supabase Upgrades:
- **Pro ($25/mo)**: 8 GB database, daily backups, no daily pause
- Free tier is great for starting!

---

## 🎉 Congratulations!

Your CashFlow Manager is now:
- ✅ Deployed globally
- ✅ Accessible 24/7
- ✅ Using production database
- ✅ Fully secured with HTTPS
- ✅ Costing $0/month!

Share your app: `https://your-app.vercel.app`

---

## 🆘 Need Help?

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Supabase Docs**: [supabase.com/docs](https://supabase.com/docs)

---

## 📝 Quick Reference

### Your URLs:
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-service.onrender.com`
- Database: Supabase Dashboard

### Important Files:
- Backend env: Render Dashboard → Environment
- Frontend env: Vercel Dashboard → Settings → Environment Variables
- Logs: Available in both dashboards

---

**Made with ❤️ | Deployed for Free 🆓**
