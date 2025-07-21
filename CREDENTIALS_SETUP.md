# VibeHat Publishing Credentials Setup

## Overview
To automatically publish warning packages to npm and PyPI registries, you need to configure authentication tokens.

## Required Credentials

### 1. GitHub Token (GITHUB_TOKEN)
**Purpose:** Repository scanning and access
**Create at:** https://github.com/settings/tokens

**Permissions needed:**
- `public_repo` (for public repositories)
- `repo` (for private repositories - if needed)

```bash
export GITHUB_TOKEN="github_pat_your_token_here"
```

### 2. NPM Token (NPM_TOKEN)  
**Purpose:** Publishing warning packages to npm registry
**Create at:** https://www.npmjs.com/settings/[username]/tokens

**Token type:** Automation (for CI/CD publishing)
**Permissions:** Read and Publish

```bash
export NPM_TOKEN="npm_your_token_here"
```

### 3. PyPI Token (PYPI_TOKEN)
**Purpose:** Publishing warning packages to PyPI registry  
**Create at:** https://pypi.org/manage/account/token/

**Scope:** Entire account (required for creating new packages)
**Note:** Use API tokens, not username/password

```bash
export PYPI_TOKEN="pypi-your_token_here"
```

### 4. Warning Website (Optional)
**Purpose:** Educational URL shown in warning packages
**Default:** https://vibehat.dev/dependency-confusion

```bash
export WARNING_WEBSITE="https://your-domain.com/dependency-confusion"
```

## Setup Instructions

### Option 1: Environment Variables
```bash
# Set environment variables
export GITHUB_TOKEN="github_pat_..."
export NPM_TOKEN="npm_..."  
export PYPI_TOKEN="pypi-..."
export WARNING_WEBSITE="https://vibehat.dev/dependency-confusion"

# Start containers
docker-compose up --build -d
```

### Option 2: .env File
```bash
# Create .env file in project root
cat > .env << EOF
GITHUB_TOKEN=github_pat_your_token_here
NPM_TOKEN=npm_your_token_here
PYPI_TOKEN=pypi-your_token_here
WARNING_WEBSITE=https://vibehat.dev/dependency-confusion
EOF

# Start containers (docker-compose will load .env automatically)
docker-compose up --build -d
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Token Security**
   - Never commit tokens to version control
   - Use environment variables or secure secret management
   - Rotate tokens regularly

2. **NPM Token Scope**
   - Use automation tokens (not classic tokens)
   - Restrict to necessary permissions only
   - Consider using scoped packages (@yourorg/package-name)

3. **PyPI Token Scope**  
   - Account-level tokens needed for new package creation
   - Consider creating a dedicated PyPI account for security research
   - Monitor published packages regularly

## Testing Setup

```bash
# Test API health
curl http://localhost:8000/health

# Test GitHub access (should not return 404)
curl -H "Content-Type: application/json" \
     -d '{"repository_url": "https://github.com/jvlax/vibehat"}' \
     http://localhost:8000/scan/repository

# Test publishing capabilities (dry run - checks credentials)
curl -H "Content-Type: application/json" \
     -d '{"package_name": "test-package-name", "ecosystem": "npm"}' \
     http://localhost:8000/publish/warning-package
```

## Troubleshooting

### NPM Publishing Issues
- Verify token has publish permissions
- Check package name availability
- Ensure npm CLI is available in container

### PyPI Publishing Issues  
- Verify token scope includes package creation
- Check package name format (no uppercase, use hyphens)
- Ensure twine is installed

### GitHub Scanning Issues
- Verify token has repository read access
- Check rate limiting
- Ensure repository URL format is correct 