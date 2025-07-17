#!/bin/bash

# Create a new release branch
# Usage: ./scripts/new-release.sh "v1.2.0"

set -e  # Exit on any error

if [ $# -eq 0 ]; then
    echo "❌ Error: Please provide a version number"
    echo "📋 Usage: ./scripts/new-release.sh \"v1.2.0\""
    echo "📋 Example: ./scripts/new-release.sh \"v1.1.0\""
    exit 1
fi

VERSION="$1"
BRANCH_NAME="release/$VERSION"

echo "🚀 Creating new release branch: $BRANCH_NAME"

# Make sure we're starting from develop
echo "🔄 Switching to develop branch..."
git checkout develop

# Pull latest changes
echo "⬇️  Pulling latest changes from origin/develop..."
git pull origin develop

# Create and switch to new release branch
echo "🌿 Creating release branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

# Update version in pyproject.toml
echo "📝 Updating version in pyproject.toml..."
sed -i "s/^version = .*/version = \"${VERSION#v}\"/" pyproject.toml

# Commit version update
git add pyproject.toml
git commit -m "chore: bump version to $VERSION"

# Push the new branch to origin
echo "⬆️  Pushing new branch to origin..."
git push -u origin "$BRANCH_NAME"

echo ""
echo "✅ Release branch created successfully!"
echo "📋 Next steps:"
echo "   1. Test the release thoroughly"
echo "   2. Update CHANGELOG.md if needed"
echo "   3. Run full test suite: ./run_tests.sh"
echo "   4. Merge to staging for testing: git checkout staging && git merge $BRANCH_NAME"
echo "   5. After approval, merge to main and develop"
echo ""
echo "🔥 Release workflow:"
echo "   1. staging ← $BRANCH_NAME (for testing)"
echo "   2. main ← $BRANCH_NAME (for production)"
echo "   3. develop ← $BRANCH_NAME (to sync back)"
echo "   4. Create tag: git tag -a $VERSION -m \"Release $VERSION\""
