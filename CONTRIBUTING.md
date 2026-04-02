# Contributing to OPS Data Standard

Thank you for your interest in contributing to the OPS Data Standard! This document provides guidelines for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Please report unacceptable behavior to opensource@chanzuckerberg.com.

## How to Contribute

### Reporting Issues

If you find a bug, have a question, or want to request a feature:

1. Check if the issue already exists in the [issue tracker](https://github.com/chanzuckerberg/ops-schema/issues)
2. If not, create a new issue with a clear title and description
3. Include as much relevant information as possible
4. For bug reports, include steps to reproduce the issue

### Proposing Schema Changes

The schema is the core of this project, so changes should be carefully considered:

1. Open an issue describing the proposed change and why it's needed
2. Discuss the change with maintainers and community members
3. Once there's consensus, create a pull request with the changes
4. Include updates to documentation, examples, and the validator as needed

### Pull Request Process

1. Fork the repository and create a new branch for your changes
2. Make your changes following the project's style and conventions
3. Update documentation to reflect your changes
4. Ensure your changes don't break existing functionality
5. Submit a pull request with a clear description of the changes
6. Link to any related issues in your pull request description
7. Be responsive to feedback during the review process

### Development Setup

The repository contains both schema documentation and a Python validator package.

**Schema documentation:**

1. Clone the repository
2. Create a new branch for your changes
3. Edit markdown files as needed
4. Preview your changes locally before submitting

**Validator (`validator/`):**

```bash
cd validator
pip install -e ".[dev]"
python -m pytest tests/
```

> Schema field changes (adding, removing, or renaming fields) will typically require a corresponding update to the validator. See `validator/src/ops_validator/` for the relevant model and validator files.

### Schema Versioning

The OPS schema follows [Semantic Versioning](https://semver.org/):

- **Major version**: Incompatible schema changes (renaming/removing fields, changing types)
- **Minor version**: Additive changes (new fields, changed validation)
- **Patch version**: Editorial updates (documentation, examples)

### Documentation Style

When contributing to documentation:

- Use clear, concise language
- Include examples where helpful
- Follow the existing structure and formatting
- Use HTML tables for schema field definitions (matching the existing style)
- Link to relevant external resources

## Getting Help

If you need help with your contribution:

- Ask questions in the issue or pull request
- Reach out to maintainers
- Check existing documentation and examples

## Reporting Security Issues

**Please do not report security issues in public GitHub issues.**

Instead, please responsibly disclose security issues by contacting us at security@chanzuckerberg.com. See [SECURITY.md](SECURITY.md) for more information.

## Recognition

Contributors will be acknowledged in:

- Git commit history
- Release notes for significant contributions
- The project's acknowledgments

Thank you for contributing to the OPS Data Standard!
