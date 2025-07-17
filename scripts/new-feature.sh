#!/bin/bash

# Create a new feature branch
# Usage: ./scripts/new-feature.sh "feature-name"

set -e  # Exit on any error

if [ $# -eq 0 ]; then
    echo "❌ Error: Please provide a feature name"
    echo "📋 Usage: ./scripts/new-feature.sh \"feature-name\""
    echo "📋 Example: ./scripts/new-feature.sh \"patient-search-optimization\""
    exit 1
fi

FEATURE_NAME="$1"
BRANCH_NAME="feature/$FEATURE_NAME"

echo "🚀 Creating new feature branch: $BRANCH_NAME"

# Make sure we're starting from develop
echo "🔄 Switching to develop branch..."
git checkout develop

# Pull latest changes
echo "⬇️  Pulling latest changes from origin/develop..."
git pull origin develop

# Create and switch to new feature branch
echo "🌿 Creating feature branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

# Push the new branch to origin
echo "⬆️  Pushing new branch to origin..."
git push -u origin "$BRANCH_NAME"

echo ""
echo "✅ Feature branch created successfully!"
echo "📋 Next steps:"
echo "   1. Start developing your feature"
echo "   2. Make commits with clear messages"
echo "   3. Push changes: git push origin $BRANCH_NAME"
echo "   4. Create a Pull Request to develop when ready"
echo ""
echo "💡 Useful commands:"
echo "   - Run tests: ./run_tests.sh"
echo "   - Check status: git status"
echo "   - Commit changes: git add . && git commit -m \"feat: your change description\""
