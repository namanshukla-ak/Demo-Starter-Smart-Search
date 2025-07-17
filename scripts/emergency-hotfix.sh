#!/bin/bash

# Create emergency hotfix branch
# Usage: ./scripts/emergency-hotfix.sh "issue-description"

set -e  # Exit on any error

if [ $# -eq 0 ]; then
    echo "❌ Error: Please provide a hotfix description"
    echo "📋 Usage: ./scripts/emergency-hotfix.sh \"issue-description\""
    echo "📋 Example: ./scripts/emergency-hotfix.sh \"database-connection-timeout\""
    exit 1
fi

ISSUE_DESCRIPTION="$1"
BRANCH_NAME="hotfix/$ISSUE_DESCRIPTION"

echo "🚨 Creating emergency hotfix branch: $BRANCH_NAME"

# Make sure we're starting from main (production)
echo "🔄 Switching to main branch..."
git checkout main

# Pull latest changes from main
echo "⬇️  Pulling latest changes from origin/main..."
git pull origin main

# Create and switch to new hotfix branch
echo "🌿 Creating hotfix branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

# Push the new branch to origin
echo "⬆️  Pushing new branch to origin..."
git push -u origin "$BRANCH_NAME"

echo ""
echo "🚨 Emergency hotfix branch created successfully!"
echo "⚠️  HOTFIX WORKFLOW - FOLLOW CAREFULLY:"
echo ""
echo "📋 Immediate steps:"
echo "   1. Fix the critical issue quickly"
echo "   2. Test the fix thoroughly: ./run_tests.sh"
echo "   3. Commit with clear message: git commit -m \"fix: resolve $ISSUE_DESCRIPTION\""
echo "   4. Push changes: git push origin $BRANCH_NAME"
echo ""
echo "📋 Deployment steps:"
echo "   5. Merge to main: git checkout main && git merge $BRANCH_NAME"
echo "   6. Deploy to production immediately"
echo "   7. Merge to develop: git checkout develop && git merge $BRANCH_NAME"
echo "   8. Tag the hotfix: git tag -a v1.0.1 -m \"Hotfix: $ISSUE_DESCRIPTION\""
echo ""
echo "⚠️  Remember:"
echo "   - This is for CRITICAL production issues only"
echo "   - Keep changes minimal and focused"
echo "   - Test thoroughly before merging"
echo "   - Communicate with team immediately"
echo ""
echo "🔥 Quick commands:"
echo "   Test: ./run_tests.sh -t unit"
echo "   Status: git status"
echo "   Diff: git diff"
