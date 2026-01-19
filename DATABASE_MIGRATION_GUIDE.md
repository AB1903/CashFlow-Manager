# Production-Ready Database Setup Guide

## Overview
This guide will help you migrate from SQLite to Supabase Postgres for a production-ready application.

## Prerequisites
- Supabase account with your project set up
- Database password from Supabase

## Step 1: Get Your Supabase Database Password

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project: `jvlbxzhqzfaxvneqcyiy`
3. Go to **Settings** → **Database**
4. Under **Connection string**, find the **URI** tab
5. Click "Copy" to get your connection string
6. It will look like: `postgresql://postgres:[YOUR-PASSWORD]@db.jvlbxzhqzfaxvneqcyiy.supabase.co:5432/postgres`

## Step 2: Update .env File

1. Open the `.env` file in your project root
2. Replace `[YOUR-DATABASE-PASSWORD]` in the `SUPABASE_DB_URL` with your actual password:

```env
SUPABASE_DB_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD_HERE@db.jvlbxzhqzfaxvneqcyiy.supabase.co:5432/postgres
```

## Step 3: Create Database Tables in Supabase

1. Go to your Supabase Dashboard
2. Click on **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy the entire contents of `database_setup.sql`
5. Paste it into the SQL Editor
6. Click **Run** to execute the script

This will create:
- ✅ `transactions` table with proper schema
- ✅ Indexes for performance optimization
- ✅ Row Level Security (RLS) policies for data protection
- ✅ Auto-update trigger for `updated_at` column
- ✅ Transaction summary view (optional)

## Step 4: Install Python Dependencies

```bash
cd /Users/ankushbhatt/App
source venv/bin/activate
pip install -r requirements.txt
```

New packages installed:
- `psycopg2-binary` - PostgreSQL database adapter
- `python-dotenv` - Environment variable management
- All existing packages updated to latest versions

## Step 5: Test the Database Connection

Start your backend:

```bash
python main.py
```

You should see:
```
==================================================
🚀 Starting CashFlow Manager API
==================================================
✓ Database connection pool initialized
✓ Database schema initialized successfully
==================================================
```

## Step 6: Test the API

1. Go to your frontend (http://localhost:3000)
2. Sign in with your account
3. Try creating a transaction
4. Verify it appears in your transaction list

## Step 7: Verify Data in Supabase

1. Go to Supabase Dashboard → **Table Editor**
2. Select the `transactions` table
3. You should see your transactions stored there

## Features of the Production Setup

### 1. **Connection Pooling**
- Maintains 1-10 database connections
- Reuses connections for better performance
- Automatically manages connection lifecycle

### 2. **Row Level Security (RLS)**
- Users can only access their own transactions
- Enforced at the database level
- Prevents data leaks even if backend is compromised

### 3. **Proper Data Types**
- `UUID` for user IDs (matches Supabase auth)
- `DECIMAL` for money (no floating-point errors)
- `TIMESTAMP WITH TIME ZONE` for accurate time tracking

### 4. **Performance Optimizations**
- Indexed columns for faster queries
- Query parameter binding (prevents SQL injection)
- Efficient cursor usage with RealDictCursor

### 5. **Environment Variables**
- All secrets stored in `.env` file
- Never hardcoded in source code
- Easy to change for different environments

### 6. **Auto-Updated Timestamps**
- `created_at` automatically set on insert
- `updated_at` automatically updated on changes
- Database triggers handle this automatically

### 7. **Error Handling**
- Try-catch blocks for all database operations
- Automatic transaction rollback on errors
- Descriptive error messages for debugging

## Environment Variables Checklist

Make sure your `.env` file has all these set:

```env
# Backend Configuration
SECRET_KEY=your-secret-key-change-in-production  # Change this!
ENVIRONMENT=development

# Supabase Configuration
SUPABASE_URL=https://jvlbxzhqzfaxvneqcyiy.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=7Dd1bTwfbq3Uem72rUXzP04hhw4uP5dO...
SUPABASE_DB_URL=postgresql://postgres:YOUR_PASSWORD@db.jvlbxzhqzfaxvneqcyiy.supabase.co:5432/postgres

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Troubleshooting

### Connection Error: "could not connect to server"
- Check your database password in SUPABASE_DB_URL
- Verify network connectivity
- Check if your IP is allowed in Supabase (Settings → Database → Connection Pooling)

### Row Level Security Error
- Make sure you ran the complete database_setup.sql
- Verify RLS policies are enabled in Supabase Table Editor

### Import Error: "No module named psycopg2"
- Run: `pip install -r requirements.txt`
- Make sure your virtual environment is activated

### "Database connection pool initialization failed"
- Check SUPABASE_DB_URL format
- Verify password doesn't have special characters that need URL encoding
- Test connection in Supabase SQL Editor first

## Migration from SQLite

Your old SQLite data is still in `cashflow.db`. To migrate:

1. **Export from SQLite:**
   - Use the export feature in your frontend
   - Download as CSV or JSON

2. **Import to Supabase:**
   - Use the import feature in your frontend
   - Upload the exported file

OR manually with SQL:

```python
# Migration script (optional)
import sqlite3
import psycopg2
from datetime import datetime

# Read from SQLite
sqlite_conn = sqlite3.connect('cashflow.db')
cursor = sqlite_conn.cursor()
cursor.execute("SELECT * FROM transactions")
transactions = cursor.fetchall()

# Write to Postgres
pg_conn = psycopg2.connect("your_supabase_db_url")
pg_cursor = pg_conn.cursor()

for tx in transactions:
    pg_cursor.execute("""
        INSERT INTO transactions (user_id, type, amount, category, description, date, payment_method, currency)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (tx[1], tx[2], tx[3], tx[4], tx[5], tx[6], tx[7], tx[8]))

pg_conn.commit()
```

## Next Steps

1. ✅ Database migrated to Postgres
2. ⬜ Deploy backend to production (Railway, Render, or Fly.io)
3. ⬜ Deploy frontend to production (Vercel, Netlify)
4. ⬜ Set up monitoring and logging
5. ⬜ Configure automated backups
6. ⬜ Add analytics and insights features

## Security Checklist for Production

- [ ] Change SECRET_KEY to a strong random value
- [ ] Update ALLOWED_ORIGINS to your production domain
- [ ] Enable HTTPS only in production
- [ ] Set up Supabase backups
- [ ] Configure rate limiting thresholds
- [ ] Review and test RLS policies
- [ ] Set up error monitoring (Sentry)
- [ ] Enable database SSL connections
- [ ] Rotate JWT secrets periodically
- [ ] Set up logging and audit trails
