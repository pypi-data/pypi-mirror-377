# PyPI Deployment Guide for zymmr-client

## 🚀 Quick Deploy Commands
```bash
# 1. Build the package
uv build

# 2. Test on TestPyPI first  
uv publish --index-url https://test.pypi.org/legacy/

# 3. Deploy to production PyPI
uv publish
```

## 📋 Pre-Deployment Checklist

### 1. Account Setup
- [ ] Create PyPI account at https://pypi.org/account/register/
- [ ] Create TestPyPI account at https://test.pypi.org/account/register/
- [ ] Generate API tokens for both accounts
- [ ] Verify email addresses

### 2. Package Validation
- [ ] Check pyproject.toml has correct metadata
- [ ] Verify package name availability on PyPI
- [ ] Test package builds without errors
- [ ] Ensure all required files are included

## 🔐 Authentication Setup

### Option 1: Environment Variables (Recommended)
```bash
# For TestPyPI
export UV_PUBLISH_USERNAME=__token__
export UV_PUBLISH_PASSWORD=your-testpypi-api-token

# For Production PyPI  
export UV_PUBLISH_USERNAME=__token__
export UV_PUBLISH_PASSWORD=your-pypi-api-token
```

### Option 2: Interactive Authentication
Let `uv publish` prompt for credentials when needed.

## 📦 Step-by-Step Deployment

### Step 1: Build Package
```bash
uv build
```
This creates:
- `dist/zymmr_client-0.1.0.tar.gz` (source distribution)
- `dist/zymmr_client-0.1.0-py3-none-any.whl` (wheel)

### Step 2: Test on TestPyPI
```bash
# Set TestPyPI credentials
export UV_PUBLISH_USERNAME=__token__
export UV_PUBLISH_PASSWORD=your-testpypi-token

# Publish to TestPyPI
uv publish --index-url https://test.pypi.org/legacy/
```

### Step 3: Verify TestPyPI Installation
```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ zymmr-client

# Test import
python -c "import zymmr_client; print(zymmr_client.__version__)"
```

### Step 4: Deploy to Production PyPI
```bash
# Set PyPI credentials  
export UV_PUBLISH_USERNAME=__token__
export UV_PUBLISH_PASSWORD=your-pypi-token

# Publish to PyPI
uv publish
```

### Step 5: Verify Production Installation
```bash
# Install from PyPI
pip install zymmr-client

# Test import
python -c "import zymmr_client; print('Success!')"
```

## 🔍 Package Name Verification

Check if your package name is available:
- PyPI: https://pypi.org/project/zymmr-client/
- TestPyPI: https://test.pypi.org/project/zymmr-client/

If taken, consider alternatives:
- `zymmr-python-client`
- `zymmr-api-client`
- `python-zymmr`

## 🚨 Common Issues & Solutions

### Issue: Package name already exists
**Solution**: Choose a different name in `pyproject.toml`

### Issue: Authentication failed
**Solution**: 
1. Verify API token is correct
2. Check environment variables are set
3. Ensure token has upload permissions

### Issue: Build fails
**Solution**:
1. Check pyproject.toml syntax
2. Verify all dependencies are declared
3. Ensure src/zymmr_client/__init__.py exists

### Issue: Import fails after installation
**Solution**:
1. Check package structure follows src layout
2. Verify __init__.py has proper imports
3. Test locally with `pip install -e .`

## 🎯 Post-Deployment

### 1. Tag the Release
```bash
git tag v0.1.0
git push origin v0.1.0
```

### 2. Create GitHub Release
- Go to GitHub → Releases → Create new release
- Tag: v0.1.0
- Title: "zymmr-client v0.1.0 - Initial Release"
- Description: List key features

### 3. Update Documentation
- Add PyPI badges to README
- Update installation instructions
- Announce on relevant platforms

## 📊 Success Verification

Your package is successfully deployed when:
- [ ] Available on PyPI: https://pypi.org/project/zymmr-client/
- [ ] Installable via: `pip install zymmr-client`
- [ ] Importable in Python: `import zymmr_client`
- [ ] Shows correct version: `zymmr_client.__version__`

## 🔄 Future Updates

For subsequent versions:
1. Update version in pyproject.toml and __init__.py
2. Build: `uv build`  
3. Test on TestPyPI (optional)
4. Deploy: `uv publish`
5. Tag release: `git tag vX.Y.Z`
