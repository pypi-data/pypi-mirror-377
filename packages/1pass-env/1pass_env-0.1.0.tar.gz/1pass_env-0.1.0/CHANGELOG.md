# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `import` command to import environment variables from 1Password items
- Support for importing all fields or specific fields using `--fields` filter
- Customizable vault selection with `--vault` option (default: 'tokens')
- Automatic item name detection from current folder name
- Custom output file support with `--file` option (default: '1pass.env')
- Debug mode with `--debug` flag for detailed logging
- File safety with merge/overwrite confirmation prompts
- Integration with 1Password SDK for Python for secure authentication
- Rich terminal output with tables and colored status messages
- Comprehensive test coverage for all functionality

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- Secure handling of environment variables with proper escaping
- Value masking in output for security (unless debug mode is enabled)
- Service account token validation before operations

## [0.1.0] - 2025-09-18

### Added
- Initial release focused on importing environment variables from 1Password
- Single `import` command with full feature set
- 1Password SDK integration for secure operations
- Rich CLI interface with comprehensive help and examples
