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

### fake-js-undeclared/
- **Purpose**: **NEW** - Undeclared imports in JavaScript source code
- **Expected Result**: Should detect packages imported in code but not declared in package.json
- **Contains**: 
  - **Declared in package.json**: express, lodash, jest (real packages)
  - **Undeclared imports in source**: company-internal-utils, undeclared-helpers, another-missing-package, dynamic-missing-lib, @company/secret-config, internal-api-client, custom-validator-lib

### fake-python-undeclared/
- **Purpose**: **NEW** - Undeclared imports in Python source code  
- **Expected Result**: Should detect packages imported in code but not in requirements.txt
- **Contains**:
  - **Declared in requirements.txt**: requests, flask, pandas (real packages)
  - **Undeclared imports in source**: company_internal_tools, missing_data_processor, undeclared_auth, secret_config, proprietary_ml_lib, custom_analytics, internal_db_client, runtime_import_missing_pkg

### fake-mixed-undeclared/
- **Purpose**: **NEW** - Mixed-language project with undeclared imports
- **Expected Result**: Should detect undeclared imports in both JavaScript and Python files
- **Contains**:
  - **JavaScript undeclared**: @company/auth-service, metrics-collector
  - **Python undeclared**: company_data_tools, secret_algorithm

## Usage

These test projects are used to verify that VibeHat correctly:
1. Parses dependency files (`package.json`, `requirements.txt`)
2. **Parses source code files** for import statements (`.js`, `.py`, etc.)
3. Checks package registries
4. Identifies non-existent packages
5. **Detects dependency confusion from undeclared imports**
6. Filters out relative imports and built-in modules

## Key Security Scenarios

The **undeclared import** test cases simulate real-world dependency confusion vulnerabilities where:
- Developers import packages that aren't declared in dependency files
- Internal/private package names leak into source code
- Attackers can publish malicious packages with these names to public registries

## Testing the Scanner

Scan this repository with VibeHat:
```
Repository URL: https://github.com/your-username/vibehat
```

Expected results:
- Should find multiple fake dependencies across npm and PyPI ecosystems
- **Should detect undeclared imports from source code analysis**
- Should demonstrate comprehensive dependency confusion vulnerability detection 