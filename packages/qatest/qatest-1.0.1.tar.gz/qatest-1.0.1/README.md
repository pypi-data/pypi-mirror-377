# QATest CLI

A command-line tool for validating and uploading JSON test cases to the QATest management system.

## Features

- 🔍 **Validate** test case JSON files for correct structure and format
- 📤 **Bulk upload** test cases to QATest API
- 📁 **Recursive scanning** of directories for test case files  
- 🎨 **Rich terminal output** with progress indicators and colored formatting
- ⚙️ **Configurable** via environment variables, config files, or command-line arguments
- 🔄 **GitHub Actions integration** for CI/CD pipelines

## Installation

### From PyPI

```bash
pip install qatest
```

### From Source

```bash
git clone https://github.com/yourusername/qatest-cli.git
cd qatest-cli
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/qatest-cli.git
cd qatest-cli
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .
```

## Quick Start

### Initialize Configuration

Create a configuration file with your project credentials:

```bash
qatest init <project_key>
```

Example:
```bash
qatest init my-project abc123-api-key
```

This will create a `qatest-config.yml` file with your specified API key.

You can overwrite an existing configuration file using:

```bash
qatest init <project_key> --force
```

### Configure API Endpoint

**Important:** You must configure the API endpoint and project key before uploading test cases.

Edit the `qatest-config.yml` file created by `init` command:

```yaml
api_endpoint: http://127.0.0.1:8000  # Update with your API endpoint
project_key: abc123-api-key          # Your API key (provided during init)
batch_size: 50                       # Optional (default: 50)
validate_first: true                 # Optional (default: true)
```

### Validate Test Cases

Check that all test case JSON files in a directory are valid:

```bash
qatest validate ./test_cases
```

### Upload Test Cases

Upload all valid test cases to the QATest API:

```bash
qatest upload ./test_cases
```

## Test Case Format

Test cases must be JSON files with the following structure:

```json
{
  "id": 442,
  "title": "Default view page",
  "description": "Optional description",
  "preconditions": "Optional preconditions",
  "steps": [
    {
      "action": "Tap on Settings tab",
      "expected_result": "Settings tab is opened"
    },
    {
      "action": "Press on the company name", 
      "expected_result": "The Accounts list is displayed"
    }
  ]
}
```

### Required Fields

- `id` (integer): Unique identifier for the test case
- `title` (string): Test case title
- `steps` (array): List of test steps, each with:
  - `action` (string): The action to perform
  - `expected_result` (string): The expected result

### Optional Fields

- `description` (string): Detailed description of the test case
- `preconditions` (string): Prerequisites for running the test

## Configuration

**Important:** API endpoint and project key must be configured before uploading test cases.

QATest CLI is configured through a configuration file.

### Environment Variables

Only these optional settings can be configured via environment variables:

```bash
export QATEST_BATCH_SIZE="50"         # Optional (default: 50)
export QATEST_VALIDATE_FIRST="true"   # Optional (default: true)
```

### Configuration File

Create a `qatest-config.yml` or `qatest-config.yaml` file using the `init` command:

```yaml
api_endpoint: http://127.0.0.1:8000  # Required for upload
project_key: abc123-api-key          # Required for upload (set via init)
batch_size: 50                       # Optional (default: 50)
validate_first: true                 # Optional (default: true)
```


Show all configuration:

```bash
qatest config
```

## CLI Commands

### `qatest init`

Initialize a new configuration file with project credentials.

```bash
qatest init <project_key> [OPTIONS]

Arguments:
  PROJECT_KEY  Your project API key

Options:
  --force  Overwrite existing configuration file
  --help   Show this message and exit.
```

**Examples:**

```bash
# Create a new configuration file
qatest init my-project abc123-api-key

# Overwrite existing configuration file
qatest init my-project abc123-api-key --force
```

### `qatest validate`

Validate test case files in a directory.

```bash
qatest validate <directory> [OPTIONS]

Options:
  --pattern TEXT  File pattern to match (default: *.json)
  --help         Show this message and exit.
```

**Example:**

```bash
qatest validate ./test_cases --pattern "*.json"
```

### `qatest upload`

Upload test cases to the QATest API.

```bash
qatest upload <directory> [OPTIONS]

Options:
  --no-validate      Skip validation before upload
  --batch-size INT   Number of test cases per batch (default: 50)
  --config PATH      Path to configuration file
  --help            Show this message and exit.
```

**Examples:**

```bash
# Upload with validation (requires API endpoint to be configured)
qatest upload ./test_cases

# Skip validation
qatest upload ./test_cases --no-validate

# Custom batch size
qatest upload ./test_cases --batch-size 100
```

### `qatest config`

Manage QATest configuration.

```bash
qatest config [OPTIONS]

Options:
  --show-endpoint     Show the configured API endpoint
  --set-endpoint TEXT Set the default API endpoint
  --config-file PATH  Path to configuration file
  --help             Show this message and exit.
```

## GitHub Actions Integration

Add QATest to your CI/CD pipeline with the provided GitHub Action workflow.

### Basic Setup

1. Add the workflow file to `.github/workflows/qatest-upload.yml`
2. Set the `QATEST_API_ENDPOINT` secret in your repository settings
3. Push test case changes to trigger the workflow

### Example Workflow

```yaml
name: Upload Test Cases

on:
  push:
    paths:
      - 'test_cases/**/*.json'

jobs:
  upload:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - run: pip install qatest
    - run: qatest validate test_cases
    - run: qatest upload test_cases
      env:
        QATEST_API_ENDPOINT: ${{ secrets.QATEST_API_ENDPOINT }}
```

## API Endpoint

The tool uploads test cases to the following endpoint:

```
POST /api/test-cases/bulk
Content-Type: application/json

[
  {
    "id": 1,
    "title": "Test case title",
    "description": null,
    "preconditions": null,
    "steps": [...]
  },
  ...
]
```

## Error Handling

The CLI provides detailed error messages for common issues:

- **No API endpoint configured**: Shows configuration methods and examples
- **Invalid JSON syntax**: Shows the line number and error details
- **Missing required fields**: Lists which fields are missing
- **Connection errors**: Provides troubleshooting suggestions
- **API errors**: Shows HTTP status codes and error messages

## Development

See [CLAUDE.md](CLAUDE.md) for development guidelines and contribution instructions.

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black qatest/
flake8 qatest/
```


**Pre-publish checklist:**
- Update version in `setup.py`, `pyproject.toml`, `qatest/__init__.py`
- Run tests: `pytest`
- Tag release: `git tag -a v0.1.0 -m "Release v0.1.0"`


### Publishing to PyPI

```bash
# Activate virtual environment first
source venv/bin/activate

# Install/upgrade build tools
pip install --upgrade build twine

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build packages
python -m build

# Test with TestPyPI (optional but recommended)
twine upload --repository testpypi dist/*
# Test install: pip install --index-url https://test.pypi.org/simple/ qatest


# Or use API token (more secure)
# Get token from: https://pypi.org/manage/account/token/
twine upload dist/* --username __token__ --password pypi-<your-token>
```