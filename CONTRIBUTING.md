# Contributing to DressUp

Thank you for your interest in contributing to DressUp! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to keep our community approachable and respectable.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed after following the steps
- Explain which behavior you expected to see instead and why
- Include screenshots if possible
- Include the version of the project you're using

### Suggesting Enhancements

If you have a suggestion for a new feature or enhancement, please include as much detail as possible:

- Use a clear and descriptive title
- Provide a detailed description of the proposed functionality
- Explain why this enhancement would be useful
- List any similar features in other applications

### Pull Requests

1. Fork the repo and create your branch from `master`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Development Process

### Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/dressup.git
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Tests

```bash
python -m pytest test_api.py test_outfits.py
```

### Code Style

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused
- Write docstrings for all functions and classes

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Documentation

- Update the README.md with details of changes to the interface
- Update the API documentation for any API changes
- Add comments to the code where necessary
- Update the examples if you change the API

## Project Structure

```
dressup/
├── api.py              # FastAPI application
├── material_specs.py   # Material specifications
├── dress_maker.py      # Outfit generation logic
├── test_api.py         # API tests
├── test_outfits.py     # Outfit generation tests
├── requirements.txt    # Project dependencies
├── docs/              # Documentation
│   ├── api/          # API documentation
│   └── examples/     # Example requests/responses
└── README.md         # Project overview
```

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

- `bug` - Issues that are bugs
- `enhancement` - Issues that are feature requests
- `documentation` - Issues that are documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed

### Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your-username/dressup/tags).

## Questions?

Feel free to open an issue for any questions you might have about contributing to the project. 