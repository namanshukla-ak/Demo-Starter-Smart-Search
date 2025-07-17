#!/bin/bash

# Branch status and management utility
# Usage: ./scripts/branch-status.sh

set -e  # Exit on any error

echo "🌿 Git Branch Status - Neurologix Smart Search POV"
echo "=================================================="
echo ""

# Current branch info
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "📍 Current Branch: $CURRENT_BRANCH"
echo ""

# Show all branches with last commit info
echo "📋 All Branches:"
echo "----------------"
git for-each-ref --format='%(refname:short) - %(committerdate:relative) - %(authorname) - %(contents:subject)' refs/heads/ | column -t -s ' - '
echo ""

# Show remote branches
echo "🌐 Remote Branches:"
echo "-------------------"
git for-each-ref --format='%(refname:short) - %(committerdate:relative) - %(authorname) - %(contents:subject)' refs/remotes/ | column -t -s ' - '
echo ""

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Uncommitted Changes:"
    echo "------------------------"
    git status --short
    echo ""
fi

# Check for unpushed commits
UNPUSHED=$(git log @{u}..HEAD --oneline 2>/dev/null | wc -l || echo "0")
if [ "$UNPUSHED" -gt 0 ]; then
    echo "⬆️  Unpushed Commits: $UNPUSHED"
    echo "------------------------"
    git log @{u}..HEAD --oneline
    echo ""
fi

# Show recent commits
echo "📝 Recent Commits (last 5):"
echo "----------------------------"
git log --oneline -5
echo ""

# Branch recommendations
echo "💡 Recommendations:"
echo "-------------------"

# Check if on main/develop
if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "⚠️  You're on main branch - consider switching to develop for development"
    echo "   Command: ./scripts/switch-to-develop.sh"
elif [ "$CURRENT_BRANCH" = "develop" ]; then
    echo "✅ Good! You're on develop branch for development"
    echo "   To create feature: ./scripts/new-feature.sh \"feature-name\""
elif [[ $CURRENT_BRANCH == feature/* ]]; then
    echo "🚀 You're on a feature branch - great for development!"
    echo "   When ready, create PR to develop branch"
elif [[ $CURRENT_BRANCH == release/* ]]; then
    echo "🎯 You're on a release branch - ready for deployment testing"
    echo "   Test thoroughly, then merge to staging and main"
elif [[ $CURRENT_BRANCH == hotfix/* ]]; then
    echo "🚨 You're on a hotfix branch - fix critical issues quickly!"
    echo "   Test and merge to main AND develop ASAP"
else
    echo "❓ Unknown branch type - ensure you're following branch naming conventions"
fi

# Check for stale branches (older than 30 days)
echo ""
echo "🗑️  Stale Branches (older than 30 days):"
echo "----------------------------------------"
git for-each-ref --format='%(refname:short) %(committerdate)' refs/heads/ | while read branch date; do
    if [ "$(date -d "$date" +%s)" -lt "$(date -d '30 days ago' +%s)" ]; then
        echo "$branch - $date"
    fi
done

echo ""
echo "🛠️  Useful Commands:"
echo "--------------------"
echo "  Switch to develop:     ./scripts/switch-to-develop.sh"
echo "  New feature:           ./scripts/new-feature.sh \"name\""
echo "  New release:           ./scripts/new-release.sh \"v1.2.0\""
echo "  Deploy staging:        ./scripts/deploy-staging.sh"
echo "  Emergency hotfix:      ./scripts/emergency-hotfix.sh \"issue\""
echo "  Clean merged branches: git branch --merged develop | grep -v develop | xargs -n 1 git branch -d"
echo ""
