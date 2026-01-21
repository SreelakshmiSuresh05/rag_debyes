# GitHub Setup Guide - Step by Step

## Prerequisites

Before we start, you need:
1. ✅ The other person's GitHub username
2. ✅ Access to push to their repository (they need to add you as a collaborator OR you'll fork their repo)
3. ✅ Git installed on your machine

## Option 1: Push to Their Existing Repository (Recommended)

### Step 1: Get Repository Access

**The repository owner needs to:**
1. Go to their GitHub repository
2. Click **Settings** → **Collaborators**
3. Click **Add people**
4. Add your GitHub username
5. You'll receive an email invitation - accept it

### Step 2: Initialize Git in Your Project

```bash
cd /Users/adarshravindran/Desktop/rag_debyes

# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Agentic RAG System with Groq integration"
```

### Step 3: Connect to Their Repository

```bash
# Replace USERNAME and REPO_NAME with actual values
git remote add origin https://github.com/USERNAME/REPO_NAME.git

# Verify remote is set
git remote -v
```

### Step 4: Push to GitHub

```bash
# Push to main branch
git push -u origin main

# If they use 'master' instead of 'main':
# git branch -M master
# git push -u origin master
```

---

## Option 2: Create a New Repository Under Their Account

### Step 1: Repository Owner Creates New Repo

**The repository owner needs to:**
1. Go to https://github.com/new
2. Repository name: `agentic-rag-system` (or any name)
3. Description: "Local-LLM-based agentic document QA system with Groq integration"
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**
7. Share the repository URL with you

### Step 2: Initialize and Push

```bash
cd /Users/adarshravindran/Desktop/rag_debyes

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Agentic RAG System with Groq integration"

# Add their repository as remote (replace with actual URL)
git remote add origin https://github.com/USERNAME/REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Option 3: Fork Their Repository (If They Have One)

### Step 1: Fork the Repository

1. Go to their repository on GitHub
2. Click **Fork** button (top right)
3. Select your account as the destination
4. Wait for fork to complete

### Step 2: Clone Your Fork and Add Your Code

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# Copy your code into this directory
cp -r /Users/adarshravindran/Desktop/rag_debyes/* .

# Add and commit
git add .
git commit -m "Add agentic RAG system implementation"

# Push to your fork
git push origin main
```

### Step 3: Create Pull Request

1. Go to your fork on GitHub
2. Click **Pull requests** → **New pull request**
3. Base repository: their repo, Base branch: main
4. Head repository: your fork, Compare branch: main
5. Click **Create pull request**
6. Add description and submit

---

## Important: Before Pushing

### 1. Check .gitignore

Make sure sensitive files are ignored:
```bash
cat .gitignore
```

Should include:
- `.env` (your actual API keys)
- `__pycache__/`
- `*.pyc`
- `uploads/`

### 2. Remove Sensitive Data

```bash
# Make sure .env is not tracked
git rm --cached .env 2>/dev/null || true

# Verify no sensitive files will be committed
git status
```

### 3. Create .env from .env.example

Add a note in README that users need to:
```bash
cp .env.example .env
# Then edit .env and add GROQ_API_KEY
```

---

## Troubleshooting

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/USERNAME/REPO_NAME.git
```

### Error: "failed to push some refs"
```bash
# Pull first, then push
git pull origin main --allow-unrelated-histories
git push origin main
```

### Error: "Permission denied"
- Make sure you're added as a collaborator
- Or use SSH instead of HTTPS
- Or check your GitHub authentication

### Using SSH Instead of HTTPS

```bash
# Add SSH remote instead
git remote add origin git@github.com:USERNAME/REPO_NAME.git

# Make sure you have SSH key set up
ssh -T git@github.com
```

---

## Next Steps After Pushing

1. ✅ Verify files on GitHub
2. ✅ Check that .env is NOT in the repository
3. ✅ Add repository description and topics
4. ✅ Enable GitHub Actions (optional)
5. ✅ Add repository badges to README (optional)

---

## Quick Reference Commands

```bash
# Check status
git status

# View commit history
git log --oneline

# View remote
git remote -v

# Pull latest changes
git pull origin main

# Push changes
git push origin main

# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main
```

---

## What Information Do I Need?

Please provide:
1. **GitHub username** of the repository owner
2. **Repository name** (if it exists) or preferred name for new repo
3. **Which option** you want to use (1, 2, or 3)
