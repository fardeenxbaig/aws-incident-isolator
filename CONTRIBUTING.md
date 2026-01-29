# Contributing to AWS Incident Isolator

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Issues
- Use GitHub Issues to report bugs
- Include detailed steps to reproduce
- Provide Lambda logs if applicable
- Specify AWS region and Python version

### Suggesting Features
- Open an issue with the "enhancement" label
- Describe the use case
- Explain expected behavior

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small

### Testing
- Test with non-production resources
- Verify all error paths
- Check CloudWatch logs
- Validate SNS notifications

### Security
- Never commit AWS credentials
- Sanitize all inputs
- Log without sensitive data
- Follow least privilege principle

### Documentation
- Update README.md for new features
- Add inline code comments
- Update QUICKSTART.md if deployment changes
- Include examples

## Code Review Process

1. Automated checks must pass
2. At least one maintainer approval required
3. All comments must be addressed
4. Documentation must be updated

## Questions?

Open an issue with the "question" label.

Thank you for contributing! 🎉
