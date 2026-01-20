# 💰 CashFlow Manager

A modern, secure personal finance management application built with React and FastAPI.

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com)

**Live Demo**: [https://spendbase-vert.vercel.app](https://spendbase-vert.vercel.app)  
**Backend API**: [https://cashflow-manager-m1od.onrender.com](https://cashflow-manager-m1od.onrender.com)  
**Total Cost**: $0/month (Free Tier Deployment)

---

## ✨ Features

### 💳 Transaction Management
- ✅ Add, view, and delete income/expense transactions
- ✅ Categorize transactions
- ✅ Track payment methods
- ✅ Date-based filtering
- ✅ Real-time summaries

### 🔐 Security
- ✅ JWT authentication with Supabase
- ✅ 12+ character password requirements
- ✅ Rate limiting (prevents abuse)
- ✅ Input sanitization (XSS/SQL injection protection)
- ✅ Security headers (CSP, HSTS, X-Frame-Options)
- ✅ Audit logging
- ✅ HTTPS encryption

### 📊 Dashboard
- ✅ Total income/expense summary
- ✅ Current balance tracking
- ✅ Category-wise breakdown
- ✅ Responsive mobile design

---

## 🚀 Tech Stack

| Layer | Technology | Why? |
|-------|------------|------|
| **Frontend** | React + Tailwind CSS | Modern UI, fast development |
| **Backend** | FastAPI (Python) | High performance, auto docs |
| **Database** | Supabase (Postgres) | Scalable, realtime, free tier |
| **Auth** | Supabase Auth + JWT | Secure, industry standard |
| **Hosting** | Vercel + Render | Free, reliable, auto-deploy |

---

## 📦 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- Supabase account (free)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/cashflow-manager.git
cd cashflow-manager
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

3. **Start the backend**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend runs at: http://localhost:8000

4. **Start the frontend** (new terminal)
```bash
cd frontend
npm install
npm start
```

Frontend runs at: http://localhost:3000

5. **Open your browser**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## 🌐 Deploy to Production (FREE)

**Total deployment time: ~25 minutes**

### Option 1: Automatic Deployment

1. Fork this repository
2. Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
3. Deploy backend to Render.com
4. Deploy frontend to Vercel
5. Done! 🎉

### Option 2: One-Click Deploy

**Backend (Render):**
1. Click [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)
2. Set environment variables
3. Deploy!

**Frontend (Vercel):**
1. Click [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com)
2. Set root directory to `frontend`
3. Set environment variables
4. Deploy!

**Detailed instructions**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Complete deployment walkthrough |
| [DEPLOYMENT_QUICK_START.md](DEPLOYMENT_QUICK_START.md) | Quick reference guide |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Deployment progress tracker |
| [SECURITY.md](SECURITY.md) | Security features & best practices |
| [DATABASE_MIGRATION_GUIDE.md](DATABASE_MIGRATION_GUIDE.md) | Database setup instructions |
| [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) | Local development setup |

---

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```bash
ENVIRONMENT=development
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_DB_URL=postgresql://...
SECRET_KEY=generate-with-openssl-rand-hex-32
ALLOWED_ORIGINS=http://localhost:3000
TRUSTED_HOSTS=localhost,127.0.0.1
```

**Frontend (.env)**
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
```

See `.env.example` files for complete templates.

---

## 🛡️ Security Features

- **Authentication**: JWT tokens with Supabase
- **Password Policy**: Minimum 12 characters with complexity requirements
- **Rate Limiting**: 
  - Login: 5 attempts per 5 minutes
  - Registration: 3 per hour
  - Transactions: 100 per minute
- **Input Validation**: Pydantic models + sanitization
- **Security Headers**: CSP, HSTS, X-Frame-Options, etc.
- **Database**: Row Level Security enabled
- **Audit Logging**: All auth events tracked

See [SECURITY.md](SECURITY.md) for details.

---

## 🧪 Testing

### Run Security Tests
```bash
python test_security.py
```

Tests include:
- ✅ Security headers validation
- ✅ Password strength enforcement
- ✅ Rate limiting
- ✅ Input sanitization
- ✅ SQL injection prevention
- ✅ Authentication/authorization

---

## 📁 Project Structure

```
cashflow-manager/
├── main.py                      # FastAPI backend
├── requirements.txt             # Python dependencies
├── Procfile                     # Deployment config
├── render.yaml                  # Render.com config
├── .env.example                 # Environment template
├── DEPLOYMENT_GUIDE.md          # Deployment instructions
├── SECURITY.md                  # Security documentation
├── test_security.py             # Security test suite
│
└── frontend/                    # React application
    ├── src/
    │   ├── App.js              # Main component
    │   ├── supabaseClient.js   # Supabase config
    │   └── config.js           # API configuration
    ├── public/
    ├── package.json
    ├── vercel.json             # Vercel config
    └── .env.example            # Frontend env template
```

---

## 🎯 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user
- `POST /auth/logout` - Logout user
- `POST /auth/change-password` - Change password

### Transactions
- `GET /transactions` - List all transactions
- `POST /transactions` - Create transaction
- `DELETE /transactions/{id}` - Delete transaction
- `GET /summary` - Get financial summary
- `GET /categories` - List categories

### Health
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger UI)

---

## 💰 Free Tier Limits

| Service | Free Tier |
|---------|-----------|
| **Render** | 750 hours/month, 100GB bandwidth |
| **Vercel** | Unlimited projects, 100GB bandwidth |
| **Supabase** | 500MB storage, 50K users |

**Note**: Render free tier spins down after 15 minutes of inactivity. First request after spin-down takes ~30-60 seconds.

---

## 🐛 Troubleshooting

### Backend won't start?
- Check logs: `python main.py`
- Verify `.env` file exists and is filled in
- Ensure all Supabase credentials are correct

### Frontend can't connect?
- Verify `REACT_APP_API_URL` in `.env`
- Check CORS settings in backend
- Open browser console (F12) for errors

### Database connection failed?
- Check Supabase dashboard is accessible
- Verify database URL (special characters must be URL-encoded)
- Ensure Row Level Security policies are set

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

ISC License - feel free to use this project however you like!

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS
- [Supabase](https://supabase.com/) - Open source Firebase alternative
- [Render](https://render.com/) - Free hosting platform
- [Vercel](https://vercel.com/) - Frontend hosting

---

## 📞 Support

- 📖 [Documentation](DEPLOYMENT_GUIDE.md)
- 🔒 [Security Guide](SECURITY.md)
- ⚙️ [Setup Instructions](SETUP_INSTRUCTIONS.md)

---

## 🎉 Status

- ✅ Backend API - Production Ready
- ✅ Frontend UI - Production Ready
- ✅ Database - Configured & Migrated
- ✅ Security - Hardened & Tested
- ✅ Deployment - Ready for Free Hosting
- ✅ Monitoring - 24/7 uptime with cron-job

**Total Development Time**: Complete  
**Total Cost**: $0/month  
**Production Ready**: Yes ✅

---

## 📊 Monitoring & Uptime

- **Keep-Alive**: Cron job pings backend every 10 minutes via [cron-job.org](https://cron-job.org)
- **Backend Logs**: Available in [Render Dashboard](https://dashboard.render.com)
- **Frontend Analytics**: Available in [Vercel Dashboard](https://vercel.com/dashboard)
- **Health Endpoint**: https://cashflow-manager-m1od.onrender.com/health

---

**Built with ❤️ | Deployed for Free 🆓 | Secure by Design 🔒**
