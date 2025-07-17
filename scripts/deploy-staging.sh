#!/bin/bash

# Deploy to staging environment
# Usage: ./scripts/deploy-staging.sh

set -e  # Exit on any error

echo "🚀 Deploying to staging environment..."

# Check if we're on develop or a release branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [[ $CURRENT_BRANCH != "develop" && $CURRENT_BRANCH != release/* ]]; then
    echo "⚠️  Warning: You're not on develop or a release branch"
    echo "📍 Current branch: $CURRENT_BRANCH"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Make sure we have the latest changes
echo "⬇️  Pulling latest changes..."
git pull origin "$CURRENT_BRANCH"

# Switch to staging branch
echo "🔄 Switching to staging branch..."
git checkout staging

# Pull latest staging
git pull origin staging

# Merge current branch to staging
echo "🔀 Merging $CURRENT_BRANCH to staging..."
git merge "$CURRENT_BRANCH" --no-ff -m "deploy: merge $CURRENT_BRANCH to staging"

# Push to origin
echo "⬆️  Pushing staging branch..."
git push origin staging

# Run tests in staging context
echo "🧪 Running tests before deployment..."
if ./run_tests.sh -e staging; then
    echo "✅ Tests passed!"
else
    echo "❌ Tests failed! Deployment aborted."
    exit 1
fi

# Build and deploy using Docker
echo "🐳 Building Docker image for staging..."
docker build -t neurologix-staging:latest .

echo "🚀 Starting staging services..."
ENVIRONMENT=staging docker-compose up -d

# Wait for services to be ready
echo "⏱️  Waiting for services to start..."
sleep 30

# Health check
echo "🏥 Performing health check..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Staging deployment successful!"
    echo "🌐 Staging URL: http://localhost:8000"
    echo "📊 Frontend URL: http://localhost:8501"
else
    echo "❌ Health check failed!"
    echo "📋 Check logs: docker-compose logs"
    exit 1
fi

# Switch back to original branch
git checkout "$CURRENT_BRANCH"

echo ""
echo "🎉 Staging deployment completed successfully!"
echo "📋 Next steps:"
echo "   1. Test thoroughly in staging environment"
echo "   2. Run integration tests: ./run_tests.sh -t integration"
echo "   3. If all tests pass, proceed with production deployment"
echo "   4. To rollback: git checkout staging && git reset --hard HEAD~1"
