# Security Policy

## Supported Versions

We actively support the following versions of Helios with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Helios seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Report Publicly

Please **do not** report security vulnerabilities through public GitHub issues, discussions, or any other public forum.

### 2. Contact Us Securely

Report security vulnerabilities by emailing us at: **security@helios-project.com**

Include the following information in your report:
- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### 3. Response Timeline

- **Within 24 hours**: We will acknowledge receipt of your vulnerability report
- **Within 7 days**: We will provide a detailed response indicating next steps
- **Within 30 days**: We will provide a resolution or timeline for a fix

## Security Considerations

### Local-First Architecture

Helios is designed with a "Your Code, Your Machine" philosophy, which provides inherent security benefits:

- **No External Data Transmission**: Code never leaves your local environment
- **Local Model Inference**: All AI processing happens on your machine
- **No Cloud Dependencies**: No reliance on external APIs or services

### VS Code Extension Security

Our VS Code extension follows security best practices:

- **Minimal Permissions**: Only requests necessary VS Code API permissions
- **Input Sanitization**: All user inputs are properly sanitized
- **No External Network Calls**: Extension only communicates with local server
- **Secure Configuration**: Sensitive settings are properly handled

### Server Security

The Helios server implements multiple security layers:

- **Local Binding**: Default configuration binds only to localhost
- **Input Validation**: All API inputs are validated using Pydantic models
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Error Handling**: Secure error messages that don't leak sensitive information

### Ollama Integration Security

Our integration with Ollama follows security guidelines:

- **Local Communication**: Only communicates with local Ollama instance
- **Model Verification**: Validates model availability before use
- **Timeout Protection**: Implements timeouts to prevent hanging requests

## Security Features

### 1. Private Code Completion

- All code completion happens locally using Ollama
- No code snippets are transmitted to external servers
- Your intellectual property remains secure

### 2. Secure Configuration

- Configuration files support environment variable substitution
- Sensitive settings can be stored in environment variables
- Default configurations prioritize security

### 3. Network Security

- Server binds to localhost by default
- Optional TLS/SSL support for network communication
- Configurable CORS policies for web interface

### 4. Data Protection

- No persistent storage of user code
- Temporary data is cleared after processing
- No logging of sensitive information

## Known Security Considerations

### 1. Local Server Exposure

**Risk**: If configured to bind to 0.0.0.0, the server may be accessible from the network.

**Mitigation**: 
- Default configuration binds to localhost only
- Use firewall rules to restrict access
- Consider VPN for remote access needs

### 2. Model Security

**Risk**: AI models may generate unexpected or potentially harmful code.

**Mitigation**:
- Review all generated code before use
- Use code scanning tools on generated content
- Keep models updated with latest versions

### 3. Extension Permissions

**Risk**: VS Code extensions run with elevated permissions.

**Mitigation**:
- Minimal permission requests in package.json
- Regular security audits of extension code
- Transparent about what permissions are used

## Security Best Practices for Users

### 1. Environment Security

- Keep your development environment updated
- Use strong authentication for your system
- Regularly update Ollama and models

### 2. Network Configuration

- Use localhost binding for server (default)
- Implement firewall rules if network access is needed
- Consider using VPN for remote development

### 3. Code Review

- Always review AI-generated code
- Use static analysis tools
- Follow your organization's code review processes

### 4. Dependency Management

- Regularly update Helios and its dependencies
- Monitor security advisories for dependencies
- Use dependency scanning tools

## Incident Response

In case of a security incident:

1. **Immediate Action**: Disable the affected component
2. **Assessment**: Evaluate the scope and impact
3. **Containment**: Prevent further exposure
4. **Recovery**: Implement fixes and restore service
5. **Lessons Learned**: Update security measures

## Security Updates

Security updates are distributed through:

- **VS Code Marketplace**: Extension updates
- **Docker Hub**: Server container updates
- **GitHub Releases**: Source code updates
- **Security Advisories**: Critical security notifications

To receive security notifications:
- Watch the GitHub repository
- Subscribe to release notifications
- Follow security mailing list (security-announce@helios-project.com)

## Security Audits

We regularly conduct security audits including:

- **Code Review**: Manual review of security-critical code
- **Dependency Scanning**: Automated scanning for vulnerable dependencies
- **Penetration Testing**: Testing for common vulnerabilities
- **Third-Party Audits**: Independent security assessments

## Compliance

Helios is designed to help organizations maintain compliance with:

- **GDPR**: No personal data transmission or storage
- **HIPAA**: Local processing ensures patient data protection
- **SOX**: Audit trails and secure development practices
- **ISO 27001**: Information security management alignment

## Contact Information

For security-related matters:

- **Security Email**: security@helios-project.com
- **GPG Key**: Available upon request
- **Response Time**: 24-48 hours for critical issues

For general questions:
- **GitHub Issues**: For non-security bugs and features
- **Discussions**: For community questions and support

## Acknowledgments

We appreciate the security research community and welcome responsible disclosure of vulnerabilities. Contributors who report valid security issues will be:

- Credited in our security advisories (with permission)
- Listed in our Hall of Fame
- Eligible for our bug bounty program (when available)

Thank you for helping keep Helios secure!