#!/bin/bash

# Configuration
REPO_DIR="."
COMMIT_MESSAGE="Auto-deploy weather app from multi-agent system"

echo "Starting Git operations..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "Error: Not in a Git repository. Please run 'git init' first."
    exit 1
fi

# Check if index.html exists
if [ ! -f "index.html" ]; then
    echo "Error: index.html not found!"
    exit 1
fi

# Stage the file
echo "Staging index.html..."
git add index.html

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "No changes to commit."
    exit 0
fi

# Commit the changes
echo "Committing changes..."
git commit -m "$COMMIT_MESSAGE"

if [ $? -ne 0 ]; then
    echo "Error: Git commit failed!"
    exit 1
fi

# Push to remote
echo "Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
else
    echo "❌ Failed to push to GitHub. Check your Git credentials and remote configuration."
    exit 1
fi

echo "Git operations completed successfully!"
