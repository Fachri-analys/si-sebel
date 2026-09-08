# CI/CD Documentation

## Overview

Si Sebel Bot uses GitHub Actions for continuous integration and continuous deployment (CI/CD). This ensures code quality, automated testing, and streamlined deployment.

## CI/CD Pipeline Architecture

```
Push/PR → GitHub Actions → Test → Lint → Security Scan → Build → Deploy
```

## Workflows

### 1. CI - Testing and Linting (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Steps:**
1. **Checkout Code**: Clone repository
2. **Setup Python**: Install Python 3.12
3. **Cache Dependencies**: Cache pip packages for faster builds
4. **Install Dependencies**: Install requirements and dev tools
5. **Lint with Flake8**: Check code quality and style
6. **Format Check with Black**: Verify code formatting
7. **Type Check with MyPy**: Static type checking
8. **Run Tests**: Execute pytest with coverage
9. **Upload Coverage**: Upload coverage reports to Codecov

**Python Versions Tested:**
- Python 3.12 (current minimum requirement)

### 2. CD - Deployment (`.github/workflows/cd.yml`)

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Steps:**
1. **Checkout Code**: Clone repository
2. **Setup Python**: Install Python 3.12
3. **Install Dependencies**: Install requirements
4. **Run Tests**: Pre-deployment testing
5. **Build Package**: Create deployment tarball
6. **Upload Artifact**: Store deployment package
7. **Deploy to Server**: Deploy to production (placeholder)
8. **Notify Status**: Report deployment status

**Environments:**
- `production`: Main production deployment
- `staging`: Staging environment for testing

### 3. Docker Build (`.github/workflows/docker-build.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Manual workflow dispatch

**Steps:**
1. **Checkout Code**: Clone repository
2. **Setup Docker Buildx**: Initialize Docker build environment
3. **Login to Docker Hub**: Authenticate with Docker Hub
4. **Build and Push**: Build and push Docker images
5. **Image Digest**: Output image digest

**Docker Tags:**
- `latest`: Latest stable version
- `{commit_sha}`: Specific commit version
- `buildcache`: Build cache for faster builds

## Setup Instructions

### 1. GitHub Secrets Configuration

Configure the following secrets in your GitHub repository (`Settings → Secrets and variables → Actions`):

**For CI/CD:**
- No additional secrets required for basic CI

**For Docker Build:**
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password or access token

**For Deployment:**
- `SSH_PRIVATE_KEY`: SSH private key for server access
- `SERVER_HOST`: Server hostname/IP
- `SERVER_USER`: Server username
- `DEPLOY_PATH`: Deployment path on server

### 2. Enable Workflows

Workflows are automatically enabled when:
- Files are present in `.github/workflows/`
- Repository is pushed to GitHub

### 3. Configure Branch Protection

Recommended branch protection rules for `main`:
- Require pull request before merging
- Require status checks to pass
- Require branches to be up to date
- Include administrators

## Local Development

### Running CI Checks Locally

**Install dev dependencies:**
```bash
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
```

**Run linting:**
```bash
# Flake8
flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics

# Black check
black --check src/

# MyPy type check
mypy src/ --ignore-missing-imports
```

**Run tests:**
```bash
pytest tests/ -v --cov=src/ --cov-report=html
```

**Format code:**
```bash
black src/
```

### Running Security Checks Locally

**Install security tools:**
```bash
pip install safety bandit
```

**Run safety check:**
```bash
safety check --file requirements.lock
```

**Run bandit:**
```bash
bandit -r src/
```

## Deployment Strategies

### 1. Manual Deployment

Current workflow supports manual deployment via workflow dispatch.

**Steps:**
1. Go to Actions tab in GitHub
2. Select "CD - Deployment" workflow
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow" button

### 2. Automated Deployment

For automated deployment on push to `main`:
- Workflow is already configured to trigger on push
- Customize deployment step in `.github/workflows/cd.yml`

### 3. Docker Deployment

**Build Docker image locally:**
```bash
docker build -t sisebel:latest .
```

**Run with Docker Compose:**
```bash
docker-compose up -d
```

**Deploy Docker image:**
```bash
docker push yourusername/sisebel:latest
```

## Monitoring and Debugging

### View Workflow Runs

1. Go to Actions tab in GitHub
2. Select workflow run
3. View logs for each step
4. Download artifacts if needed

### Common Issues

**Workflow not triggering:**
- Check workflow file syntax
- Verify branch names match configuration
- Check GitHub Actions is enabled for repository

**Tests failing:**
- Run tests locally first
- Check Python version compatibility
- Verify all dependencies are installed

**Deployment failing:**
- Check server connectivity
- Verify SSH credentials
- Check deployment path permissions
- Review deployment logs

## Performance Optimization

### CI/CD Optimization

**Reduce build time:**
- Use dependency caching (already implemented)
- Parallelize test execution
- Use matrix strategy for multiple Python versions (if needed)

**Reduce deployment time:**
- Use Docker layer caching
- Implement incremental deployments
- Use blue-green deployment strategy

## Security Best Practices

1. **Never commit secrets**: Use GitHub Secrets
2. **Rotate credentials regularly**: Update secrets periodically
3. **Limit permissions**: Use least privilege principle
4. **Review logs**: Check for sensitive data in logs
5. **Use dependency scanning**: Safety and Bandit checks
6. **Keep dependencies updated**: Regular dependency updates

## Troubleshooting

### Workflow Permissions Error

**Error**: `Resource not accessible by integration`

**Solution:**
- Go to Settings → Actions → General
- Under "Workflow permissions", select "Read and write permissions"
- Save changes

### Docker Login Failed

**Error**: `unauthorized: incorrect username or password`

**Solution:**
- Verify Docker Hub credentials
- Use access token instead of password
- Check secret name is correct

### SSH Connection Failed

**Error**: `Permission denied (publickey)`

**Solution:**
- Verify SSH private key is correct
- Check SSH key is added to server
- Verify server hostname and user

## Maintenance

### Regular Tasks

1. **Update dependencies**: Monthly dependency updates
2. **Review workflow logs**: Weekly log review
3. **Update GitHub Actions**: Monthly Action version updates
4. **Rotate secrets**: Quarterly secret rotation
5. **Backup artifacts**: Regular artifact backup

### Workflow Updates

When updating workflows:
1. Test changes in a feature branch
2. Create pull request
3. Review CI results
4. Merge after approval

## Documentation Updates

Keep this documentation updated when:
- Adding new workflows
- Modifying existing workflows
- Changing deployment strategy
- Updating security practices

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Codecov Documentation](https://docs.codecov.com/)