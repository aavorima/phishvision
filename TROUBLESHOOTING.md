# PhishVision - Troubleshooting Guide

## Pre-Flight Checklist

Before starting, verify:
- [ ] Python 3.10+ installed: `python3 --version`
- [ ] Node.js 16+ installed: `node --version`
- [ ] npm installed: `npm --version`
- [ ] Ports 3000 and 5000 are available

## Common Issues & Solutions

### Backend Issues

#### Issue: `ModuleNotFoundError`
```
Error: No module named 'flask'
```
**Solution:**
```bash
cd backend
source venv/bin/activate  # Make sure venv is activated!
pip install -r ../requirements.txt
```

#### Issue: Missing dependencies
**Solution:**
```bash
source venv/bin/activate
pip install -r ../requirements.txt
```

#### Issue: `Port 5000 already in use`
```
Error: Address already in use
```
**Solution:**
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9

# Or change port in backend/app.py (last line):
app.run(debug=True, port=5001)
```

#### Issue: Database errors
```
Error: no such table: campaigns
```
**Solution:**
```bash
# Delete and recreate database
rm phishvision.db
python app.py  # Database will auto-create
```

#### Issue: Import errors in routes
```
Error: cannot import name 'db' from 'app'
```
**Solution:**
This is a circular import issue. Make sure you're running from the backend directory:
```bash
cd backend
python app.py
```

### Frontend Issues

#### Issue: `npm install` fails
```
Error: EACCES permission denied
```
**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Remove old installations
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

#### Issue: Port 3000 already in use
**Solution:**
Create `.env` file in frontend directory:
```bash
echo "PORT=3001" > frontend/.env
```

#### Issue: `Module not found` errors
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

#### Issue: White screen / nothing renders
**Solution:**
1. Check browser console for errors (F12)
2. Verify backend is running on port 5000
3. Check CORS configuration in backend

#### Issue: API calls fail (404 or CORS errors)
**Solution:**
1. Verify backend is running: `curl http://localhost:5000/health`
2. Check proxy in `frontend/package.json`: `"proxy": "http://localhost:5000"`
3. Restart both frontend and backend

### Integration Issues

#### Issue: Frontend can't connect to backend
**Checklist:**
- [ ] Backend running on port 5000?
- [ ] Frontend running on port 3000?
- [ ] CORS enabled in backend? (Flask-CORS installed)
- [ ] Check browser Network tab for actual error

**Solution:**
```bash
# Test backend health
curl http://localhost:5000/health

# Should return: {"status":"healthy"}
```

#### Issue: No data showing in dashboard
**Solution:**
1. Create test data first (campaigns or email analyses)
2. Check browser console for API errors
3. Verify API endpoints are responding:
```bash
curl http://localhost:5000/api/dashboard/stats
```

### Installation Issues

#### Issue: Virtual environment not activating
**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

**Still not working?**
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Issue: Python version too old
```bash
# Check version
python3 --version

# If < 3.10, install newer Python
# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.10

# On Mac:
brew install python@3.10
```

## Debugging Tips

### Backend Debugging

1. **Enable verbose logging:**
Edit `backend/app.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Test individual endpoints:**
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test campaigns list
curl http://localhost:5000/api/campaigns/

# Test dashboard stats
curl http://localhost:5000/api/dashboard/stats
```

3. **Check database:**
```bash
# Install sqlite3
sqlite3 phishvision.db

# List tables
.tables

# Check campaigns
SELECT * FROM campaigns;

# Exit
.quit
```

### Frontend Debugging

1. **Check browser console** (F12 → Console tab)
2. **Check Network tab** for failed API calls
3. **React DevTools** for component debugging

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ECONNREFUSED` | Backend not running | Start backend on port 5000 |
| `CORS policy` | CORS not configured | Install Flask-CORS |
| `404 Not Found` | Wrong API endpoint | Check API routes |
| `500 Internal Server Error` | Backend crash | Check backend terminal for error |
| White screen | JavaScript error | Check browser console |

## Performance Issues

### Backend is slow
1. Check if running in debug mode (normal for development)
2. Verify database isn't too large
3. Consider indexing database tables

### Frontend is slow
1. Clear browser cache
2. Check Network tab for slow API calls
3. Verify backend is responding quickly

## Data Issues

### Reset everything
```bash
# Stop both servers (Ctrl+C)

# Backend reset
cd backend
rm phishvision.db
python app.py  # Will recreate database

# Frontend reset
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Test with sample data
Use the sample emails in `QUICK_START.md` to test the analyzer.

## Still Having Issues?

### Checklist
1. [ ] Both backend and frontend running?
2. [ ] No errors in either terminal?
3. [ ] Browser console clear?
4. [ ] Tested with sample data?
5. [ ] Reviewed error messages above?

### Get Help
1. Check full error message in terminal
2. Review README.md for detailed setup
3. Check SETUP_GUIDE.md for step-by-step instructions
4. Look for similar errors in the troubleshooting sections

### Last Resort - Clean Install
```bash
# Backup any custom changes first!

# Remove everything
cd /home/morpho/Desktop/Hackathon/phishvision
rm -rf backend/venv backend/__pycache__ backend/*.db
rm -rf frontend/node_modules frontend/build

# Reinstall backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python -m spacy download en_core_web_sm

# Reinstall frontend
cd ../frontend
npm install

# Start fresh
# Terminal 1: cd backend && python app.py
# Terminal 2: cd frontend && npm start
```

## Prevention Tips

1. **Always activate venv** before running backend
2. **Keep terminals open** to see errors immediately
3. **Test incrementally** - verify each step works
4. **Check logs** when something doesn't work
5. **Use provided sample data** for testing

---

**Good luck! You've got this!** 🚀
