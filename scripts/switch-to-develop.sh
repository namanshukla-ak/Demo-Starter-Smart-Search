#!/bin/bash

# Switch to develop branch and update it
# Usage: ./scripts/switch-to-develop.sh

set -e  # Exit on any error

echo "🔄 Switching to develop branch..."

# Stash any uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "📦 Stashing uncommitted changes..."
    git stash push -m "Auto-stash before switching to develop"
    STASHED=true
else
    STASHED=false
fi

# Switch to develop
git checkout develop

# Pull latest changes
echo "⬇️  Pulling latest changes from origin/develop..."
git pull origin develop

# Show current status
echo "✅ Successfully switched to develop branch"
echo "📊 Current branch status:"
git status --short

# Restore stashed changes if any
if [ "$STASHED" = true ]; then
    echo "📦 Restoring stashed changes..."
    git stash pop
fi

echo ""
echo "🎯 You are now on develop branch and up to date!"
echo "💡 To create a new feature branch, run: ./scripts/new-feature.sh <feature-name>"
