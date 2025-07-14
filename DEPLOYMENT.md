# Portfolio Website Deployment Guide

This guide covers multiple deployment options for your Flask portfolio website using GitHub.

## 🚀 Deployment Options

### 1. **Render (Recommended - Free)**
- ✅ Free tier available
- ✅ Easy Flask deployment
- ✅ Automatic deployments from GitHub
- ✅ Custom domain support

### 2. **Vercel**
- ✅ Excellent for Python apps
- ✅ Easy GitHub integration
- ✅ Fast CDN
- ✅ Free tier

### 3. **Heroku**
- ✅ Classic choice for Flask apps
- ✅ Easy deployment
- ⚠️ Free tier discontinued (paid only)

### 4. **Railway**
- ✅ Modern platform
- ✅ Good free tier
- ✅ Simple deployment

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- [x] Updated `.gitignore` file
- [x] `requirements.txt` with all dependencies
- [x] `Procfile` for Heroku compatibility
- [x] `runtime.txt` specifying Python version
- [x] Data validation implemented
- [x] GitHub Actions for CI/CD testing

---

## 🔧 Step-by-Step Deployment

### **Step 1: Commit Your Changes**

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "feat: restructure templates and add deployment configs

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push origin main
```

### **Step 2: Choose Your Hosting Platform**

#### **Option A: Deploy to Render (Recommended)**

1. **Sign up at [render.com](https://render.com)**
2. **Connect your GitHub account**
3. **Create a new Web Service**
   - Repository: `Guu-2/portfolio-website`
   - Branch: `main`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. **Deploy!**

#### **Option B: Deploy to Vercel**

1. **Sign up at [vercel.com](https://vercel.com)**
2. **Import your GitHub repository**
3. **Vercel will auto-detect the `vercel.json` configuration**
4. **Deploy!**

#### **Option C: Deploy to Railway**

1. **Sign up at [railway.app](https://railway.app)**
2. **Connect GitHub and select your repository**
3. **Railway will auto-detect it's a Python app**
4. **Deploy!**

#### **Option D: Deploy to Heroku**

1. **Sign up at [heroku.com](https://heroku.com)**
2. **Install Heroku CLI**
3. **Create a new app**:
   ```bash
   heroku create your-portfolio-name
   ```
4. **Connect to GitHub**:
   ```bash
   git remote add heroku https://git.heroku.com/your-portfolio-name.git
   ```
5. **Deploy**:
   ```bash
   git push heroku main
   ```

---

## 🔄 Continuous Deployment

Once deployed, your site will automatically update when you:

1. **Edit JSON data files locally**
2. **Commit changes to GitHub**
3. **Push to main branch**
4. **Hosting platform automatically redeploys**

---

## 🧪 Testing Before Deploy

The GitHub Actions workflow will automatically:

- ✅ Validate all JSON data files
- ✅ Test Flask app routes
- ✅ Ensure no validation errors
- ✅ Verify templates render correctly

Check the **Actions** tab in your GitHub repository to see test results.

---

## 🌐 Custom Domain Setup

After deployment, you can add a custom domain:

### **Render:**
1. Go to your service dashboard
2. Settings → Custom Domains
3. Add your domain and configure DNS

### **Vercel:**
1. Go to your project dashboard
2. Settings → Domains
3. Add your domain

### **Railway:**
1. Go to your project
2. Settings → Domains
3. Add custom domain

---

## 📊 Monitoring & Maintenance

### **Data Updates Workflow:**
1. Edit JSON files locally
2. Test changes: `python app.py`
3. Commit and push to GitHub
4. Automatic deployment begins
5. Site updates in 1-2 minutes

### **Logs & Debugging:**
- **Render**: Dashboard → Logs
- **Vercel**: Dashboard → Functions → Logs
- **Railway**: Dashboard → Deployments → Logs

---

## 🔐 Environment Variables

If you need environment variables:

### **Render:**
```
Environment → Add environment variable
```

### **Vercel:**
```
Settings → Environment Variables
```

### **Railway:**
```
Variables tab in project
```

---

## 🚨 Troubleshooting

### **Common Issues:**

1. **Build fails**: Check `requirements.txt` has all dependencies
2. **App won't start**: Ensure `app.py` has `if __name__ == '__main__':`
3. **Static files missing**: Verify `static/` folder is committed
4. **JSON validation errors**: Check GitHub Actions logs

### **Quick Fixes:**

```bash
# Test locally first
python app.py

# Check requirements
pip freeze > requirements.txt

# Test data validation
python -c "from app import load_and_validate_data; load_and_validate_data()"
```

---

## 🎯 Next Steps

After deployment:

1. **Test your live site thoroughly**
2. **Set up custom domain (optional)**
3. **Configure analytics (Google Analytics)**
4. **Set up monitoring (UptimeRobot)**
5. **Share your portfolio!**

---

## 📚 Additional Resources

- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Render Python Documentation](https://render.com/docs/python)
- [Vercel Python Documentation](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)

---

**Happy Deploying! 🚀**