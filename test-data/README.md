# Test Data for VibeHat Scanner

This directory contains test projects with intentionally fake dependencies to verify that the VibeHat scanner correctly identifies missing packages.

## Test Projects

### fake-npm-project/
- **Purpose**: Pure fake npm dependencies
- **Expected Result**: All dependencies should be flagged as missing
- **Contains**: 10 main dependencies + 3 dev dependencies (all fake)

### fake-python-project/
- **Purpose**: Pure fake Python dependencies  
- **Expected Result**: All dependencies should be flagged as missing
- **Contains**: 15 fake Python packages

### fake-mixed-project/
- **Purpose**: Mix of real and fake dependencies
- **Expected Result**: Only fake dependencies should be flagged
- **Contains**: 
  - **Real**: express, requests, numpy (should exist)
  - **Fake**: All others (should be flagged)

## Usage

These test projects are used to verify that VibeHat correctly:
1. Parses dependency files
2. Checks package registries
3. Identifies non-existent packages
4. Reports potential dependency confusion vulnerabilities

## Testing the Scanner

Scan this repository with VibeHat:
```
Repository URL: https://github.com/your-username/vibehat
```

Expected results:
- Should find multiple fake dependencies across npm and PyPI ecosystems
- Should demonstrate the dependency confusion vulnerability detection 