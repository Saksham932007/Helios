# Helios Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously and appreciate your help in keeping Helios secure.

### How to Report

If you discover a security vulnerability, please report it by:

1. **Email**: Send details to security@helios-project.org (if available)
2. **GitHub**: Create a private security advisory on GitHub
3. **Direct Contact**: Contact the maintainers directly

### What to Include

Please include the following information:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fixes (if any)
- Your contact information

### Response Timeline

- **Initial Response**: Within 24 hours
- **Assessment**: Within 72 hours
- **Fix Development**: Depends on severity
- **Public Disclosure**: After fix is available

### Security Considerations

Since Helios runs locally, the attack surface is limited, but we still consider:

1. **Model Security**: Ensuring models can't be used maliciously
2. **Server Security**: Protecting the local inference server
3. **Extension Security**: VS Code extension security best practices
4. **Data Privacy**: Ensuring no data leaves the local environment

### Known Security Features

- **Local-Only Operation**: No external data transmission
- **Sandboxed Execution**: Code runs in controlled environment
- **Input Validation**: All inputs are validated
- **Error Handling**: Secure error messages

### Security Best Practices for Users

1. **Keep Updated**: Use the latest version
2. **Secure Environment**: Run on trusted systems
3. **Monitor Usage**: Watch for unusual behavior
4. **Limited Access**: Don't expose server externally
5. **Safe Models**: Only use trusted model sources

### Vulnerability Disclosure Policy

We follow responsible disclosure:
1. Report received and acknowledged
2. Vulnerability assessed and validated
3. Fix developed and tested
4. Security advisory prepared
5. Fix released to users
6. Public disclosure after users can update

Thank you for helping keep Helios secure!