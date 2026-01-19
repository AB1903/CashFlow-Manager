# Setup Instructions - Supabase Authentication

## Step 1: Add Your Supabase JWT Secret

1. Open the file: `main.py`
2. Find line 38 where it says:
   ```python
   SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "PASTE_YOUR_LEGACY_JWT_SECRET_HERE")
   ```
3. Replace `"PASTE_YOUR_LEGACY_JWT_SECRET_HERE"` with your actual Supabase Legacy JWT Secret
4. It should look like:
   ```python
   SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "your-actual-secret-key-from-supabase")
   ```

## Step 2: Restart Your Backend

In the terminal where your Python backend is running:
1. Stop the server (Ctrl+C)
2. Restart it with:
   ```bash
   python main.py
   ```

## Step 3: Test the Application

1. Your React frontend should already be running
2. Login to your app with your Supabase account
3. Try adding a transaction
4. The transaction should now save successfully!

## What Was Done

✅ Installed PyJWT library for token verification
✅ Added Supabase JWT verification to backend
✅ Updated all transaction endpoints to use Supabase auth
✅ Updated frontend to send JWT token in all API requests
✅ Transactions are now linked to your Supabase user ID

## Troubleshooting

- If you see 401 errors: Check that your JWT secret is correct
- If you see 403 errors: Make sure you're logged in to Supabase
- Check backend terminal for detailed error messages
