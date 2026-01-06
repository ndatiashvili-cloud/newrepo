# GitHub Setup Guide - RND Monitoring Platform

## 🎯 სწრაფი გზამკვლევი

### 1️⃣ GitHub Repository-ს შექმნა

1. გადადით: https://github.com/new
2. Repository name: `rnd-monitoring-platform`
3. Description: `RND Research & Development Team Monitoring Platform`
4. აირჩიეთ **Private** (რეკომენდებული) ან Public
5. **არ** მონიშნოთ "Initialize with README" (უკვე გვაქვს)
6. დააჭირეთ **"Create repository"**

### 2️⃣ ლოკალური Setup

პროექტის directory-ში გაუშვით:

```bash
# Script-ის გაშვება (რეკომენდებული)
chmod +x push-to-github.sh
./push-to-github.sh

# შემდეგ დაამატეთ GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/rnd-monitoring-platform.git
git branch -M main
git push -u origin main
```

**ან ხელით:**

```bash
# Git repository-ს ინიციალიზაცია
git init

# ყველა ფაილის დამატება
git add .

# Initial commit
git commit -m "Initial commit: RND Monitoring Platform v3.0.0"

# GitHub-თან დაკავშირება (შეცვალეთ YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/rnd-monitoring-platform.git

# Main branch-ზე push
git branch -M main
git push -u origin main
```

### 3️⃣ Credentials Setup

თუ GitHub password სთხოვს:

```bash
# Personal Access Token-ის გამოყენება
# Settings → Developer settings → Personal access tokens → Generate new token
# Select scopes: repo (full control)

# Token-ით authentication:
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/rnd-monitoring-platform.git
```

### 4️⃣ Repository Structure

```
rnd-monitoring-platform/
├── README.md                  # Main documentation
├── DEPLOYMENT.md             # Deployment guide
├── QUICKSTART.md             # Quick start guide
├── CHANGELOG.md              # Version history
├── docker-compose.yml        # Docker orchestration
├── Dockerfile                # Container configuration
├── main.py                   # FastAPI application
├── requirements.txt          # Python dependencies
├── frontend/                 # React frontend
│   ├── src/
│   ├── package.json
│   └── ...
├── routers/                  # API routers
├── monitoring/               # Monitoring modules
└── scripts/                  # Utility scripts
```

## 🔐 Sensitive Files (.gitignore)

უკვე კონფიგურირებულია `.gitignore` ფაილში:

```
.env
*.db
*.log
__pycache__/
node_modules/
data/
logs/
```

## 📦 Clone & Deploy

სხვა ადგილას deploy-ისთვის:

```bash
# Repository-ს clone
git clone https://github.com/YOUR_USERNAME/rnd-monitoring-platform.git
cd rnd-monitoring-platform

# Setup და გაშვება
chmod +x deploy.sh
./deploy.sh
```

## 🚀 Continuous Deployment

GitHub Actions workflow (optional):

```bash
# შექმენით: .github/workflows/deploy.yml
# Auto-deploy Docker containers on push to main
```

## ℹ️ დამატებითი ინფორმაცია

- **Repository URL**: შეცვალეთ `YOUR_USERNAME` თქვენი GitHub username-ით
- **Branch**: ვიყენებთ `main` branch-ს (არა `master`)
- **License**: MIT License უკვე დამატებულია

## 🆘 პრობლემების გადაჭრა

### "Permission denied"
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Add SSH key to GitHub: Settings → SSH Keys
```

### "Repository not found"
```bash
# Check remote URL
git remote -v

# Update if needed
git remote set-url origin https://github.com/CORRECT_USERNAME/rnd-monitoring-platform.git
```

### "Authentication failed"
Use Personal Access Token instead of password

---

**✅ Done!** თქვენი პროექტი ახლა GitHub-ზეა და მზადაა deployment-ისთვის!
