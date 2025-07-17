# Branching Strategy - Neurologix Smart Search POV

## Overview
This project follows a **Git Flow** branching strategy to maintain code quality, enable parallel development, and ensure stable releases.

## Branch Structure

### Core Branches

#### 1. `main` (Production)
- **Purpose**: Contains production-ready code
- **Protection**: Protected branch, requires PR reviews
- **Deployment**: Automatically deploys to production
- **Merges from**: `staging` (via release) or `hotfix/*`
- **Never commit directly to this branch**

#### 2. `develop` (Integration)
- **Purpose**: Integration branch for all features
- **Status**: Latest development changes
- **Merges from**: `feature/*` branches
- **Merges to**: `staging` for testing
- **Active development happens here**

#### 3. `staging` (Pre-production)
- **Purpose**: Pre-production testing environment
- **Status**: Release candidate testing
- **Merges from**: `develop` (when ready for testing)
- **Merges to**: `main` (after testing approval)
- **Environment**: Staging server with production-like data

### Supporting Branches

#### 4. `feature/*` (Feature Development)
- **Naming**: `feature/feature-name` or `feature/JIRA-123-description`
- **Purpose**: Individual feature development
- **Branches from**: `develop`
- **Merges to**: `develop`
- **Lifetime**: Short-lived (days to weeks)
- **Examples**: 
  - `feature/nlp-query-improvement`
  - `feature/user-authentication`
  - `feature/advanced-metrics`

#### 5. `hotfix/*` (Emergency Fixes)
- **Naming**: `hotfix/issue-description` or `hotfix/v1.2.1`
- **Purpose**: Critical production bug fixes
- **Branches from**: `main`
- **Merges to**: `main` AND `develop`
- **Lifetime**: Very short (hours to days)
- **Examples**:
  - `hotfix/database-connection-fix`
  - `hotfix/security-vulnerability`

#### 6. `release/*` (Release Preparation)
- **Naming**: `release/v1.2.0`
- **Purpose**: Prepare releases, final testing, version bumps
- **Branches from**: `develop`
- **Merges to**: `main` AND `develop`
- **Lifetime**: Short (days to weeks)

## Workflow Examples

### Feature Development Workflow

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/nlp-enhancement

# 3. Develop and commit
git add .
git commit -m "feat: implement advanced NLP query processing"

# 4. Push feature branch
git push origin feature/nlp-enhancement

# 5. Create Pull Request to develop
# 6. After review and approval, merge to develop
# 7. Delete feature branch
git branch -d feature/nlp-enhancement
```

### Release Workflow

```bash
# 1. Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.1.0

# 2. Final testing, version bumps, documentation
git commit -m "chore: bump version to v1.1.0"

# 3. Merge to staging for testing
git checkout staging
git merge release/v1.1.0

# 4. After staging approval, merge to main
git checkout main
git merge release/v1.1.0

# 5. Merge back to develop
git checkout develop
git merge release/v1.1.0

# 6. Tag the release
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

### Hotfix Workflow

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-fix

# 2. Fix the issue
git commit -m "fix: resolve critical database connection issue"

# 3. Merge to main
git checkout main
git merge hotfix/critical-bug-fix

# 4. Merge to develop
git checkout develop
git merge hotfix/critical-bug-fix

# 5. Tag and deploy
git tag -a v1.0.1 -m "Hotfix version 1.0.1"
```

## Branch Protection Rules

### `main` Branch
- Require pull request reviews (min 1-2 reviewers)
- Require status checks to pass
- Require up-to-date branches before merging
- Restrict pushes to admins only
- Require signed commits

### `develop` Branch
- Require pull request reviews (min 1 reviewer)
- Require status checks to pass
- Allow force pushes by admins

## Environment Mapping

| Branch | Environment | URL | Auto-Deploy |
|--------|-------------|-----|-------------|
| `main` | Production | `https://neurologix.prod.com` | Yes |
| `staging` | Staging | `https://neurologix.staging.com` | Yes |
| `develop` | Development | `https://neurologix.dev.com` | Yes |
| `feature/*` | Local/PR Preview | PR preview URLs | On PR |

## Commit Message Conventions

Use conventional commits for better tracking:

```bash
feat: add new NLP processing capability
fix: resolve database connection timeout
docs: update API documentation
style: format code with prettier
refactor: restructure query processor
test: add unit tests for metrics calculation
chore: update dependencies
```

## Testing Strategy by Branch

### `feature/*` branches
- Unit tests must pass
- Code coverage > 80%
- Linting and formatting checks

### `develop` branch
- All feature tests
- Integration tests
- API contract tests

### `staging` branch
- Full test suite
- End-to-end tests
- Performance tests
- Security scans

### `main` branch
- Production smoke tests
- Health checks
- Monitoring alerts

## Tools and Scripts

### Quick Branch Operations

```bash
# Switch to develop and update
./scripts/switch-to-develop.sh

# Create new feature branch
./scripts/new-feature.sh "feature-name"

# Create release branch
./scripts/new-release.sh "v1.2.0"

# Deploy to staging
./scripts/deploy-staging.sh

# Emergency hotfix
./scripts/emergency-hotfix.sh "issue-description"
```

## Best Practices

1. **Always branch from the correct source**:
   - Features from `develop`
   - Hotfixes from `main`
   - Releases from `develop`

2. **Keep branches up to date**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/my-feature
   git rebase develop  # or merge develop
   ```

3. **Use descriptive branch names**:
   - ✅ `feature/patient-search-optimization`
   - ❌ `feature/fix`

4. **Small, focused commits**:
   - One logical change per commit
   - Clear commit messages
   - Atomic commits that don't break builds

5. **Regular cleanup**:
   ```bash
   # Delete merged branches
   git branch --merged develop | grep -v develop | xargs -n 1 git branch -d
   ```

## Troubleshooting

### Common Issues

1. **Merge Conflicts**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/my-feature
   git rebase develop
   # Resolve conflicts, then:
   git rebase --continue
   ```

2. **Accidental commits to main**:
   ```bash
   # Move commits to correct branch
   git checkout main
   git reset --hard HEAD~1  # Remove commit from main
   git checkout develop
   git cherry-pick <commit-hash>  # Add to develop
   ```

3. **Need to update feature branch**:
   ```bash
   git checkout feature/my-feature
   git rebase develop  # or git merge develop
   ```

## Monitoring and Alerts

- **Branch health**: Monitor build status
- **Merge frequency**: Track development velocity
- **Branch age**: Alert on stale branches (>2 weeks)
- **Test coverage**: Ensure coverage doesn't decrease

---

**Remember**: This strategy ensures code quality, enables parallel development, and provides clear deployment paths. Always communicate with your team before making structural changes!
