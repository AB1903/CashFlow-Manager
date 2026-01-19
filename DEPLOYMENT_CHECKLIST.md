# Quick Deployment Checklist

## Before Deployment

### 1. Environment Setup
- [ ] `.env` file configured with real values
- [ ] `.env` added to `.gitignore`
- [ ] SECRET_KEY generated (`openssl rand -hex 32`)
- [ ] All Supabase credentials copied from dashboard

### 2. Code Repository
- [ ] Code pushed to GitHub
- [ ] Repository is public (required for free Render)
- [ ] No secrets in repository (check with `git log -p | grep -i password`)

### 3. Database
- [ ] Supabase project created
- [ ] Database tables created (users, transactions, refresh_tokens)
- [ ] Row Level Security enabled
- [ ] Connection tested locally

## Deployment Steps

### Backend (Render.com)
- [ ] Account created on Render
- [ ] New Web Service created
- [ ] GitHub repository connected
- [ ] Environment variables set (12 variables)
- [ ] Deploy triggered
- [ ] Health check passed: `/health`
- [ ] Backend URL noted: `https://______.onrender.com`

### Frontend (Vercel)
- [ ] Account created on Vercel
- [ ] New Project created
- [ ] GitHub repository connected
- [ ] Root directory set to `frontend`
- [ ] Environment variables set (3 variables)
- [ ] Deploy triggered
- [ ] Frontend URL noted: `https://______.vercel.app`

### Final Configuration
- [ ] Backend CORS updated with frontend URL
- [ ] Frontend tested with registration
- [ ] Login tested
- [ ] Transaction creation tested
- [ ] Backend redeployed after CORS update

## Free Tier Monitoring

### Weekly Checks
- [ ] Check Render usage (750 hrs/month limit)
- [ ] Check Vercel bandwidth (100 GB/month)
- [ ] Check Supabase storage (<500 MB)
- [ ] Review error logs

### Monthly Checks
- [ ] Verify all services still free
- [ ] Check for unused resources
- [ ] Review security logs in Supabase
- [ ] Update dependencies if needed

## Troubleshooting

### Backend Issues
- Check: Render logs
- Verify: All env variables set
- Test: Database connection
- Confirm: `requirements.txt` is complete

### Frontend Issues
- Check: Vercel deployment logs
- Verify: `REACT_APP_API_URL` is correct
- Test: Browser console (F12)
- Confirm: CORS allows your domain

### Database Issues
- Check: Supabase logs
- Verify: RLS policies allow access
- Test: Direct database connection
- Confirm: Password is URL-encoded

## URLs & Credentials

### Production URLs
- Frontend: `https://_______________.vercel.app`
- Backend: `https://_______________.onrender.com`
- Database: Supabase Dashboard

### Important Dashboards
- Render: https://dashboard.render.com
- Vercel: https://vercel.com/dashboard
- Supabase: https://app.supabase.com

### GitHub Repository
- URL: `https://github.com/___________/cashflow-manager`

---

**Deployment Status**: ⬜ Not Started | 🟨 In Progress | ✅ Complete

**Last Updated**: _______________
