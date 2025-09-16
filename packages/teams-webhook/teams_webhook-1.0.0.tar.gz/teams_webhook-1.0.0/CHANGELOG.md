# Changelog

All notable changes to the teams-webhook package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- Initial release of teams-webhook package
- `TeamsWebhook` class for sending messages to Microsoft Teams
- `send_teams_message()` convenience function
- Support for rich message cards with titles, subtitles, and images
- Customizable theme colors for message cards
- Comprehensive error handling and response validation
- Support for activity images in message cards
- Type hints for better IDE support
- Detailed documentation and examples

### Features
- **Class-based API**: `TeamsWebhook` class for object-oriented usage
- **Function-based API**: `send_teams_message()` for simple function calls
- **Rich Messages**: Support for Microsoft Teams MessageCard format
- **Error Handling**: Comprehensive error handling for network and API issues
- **Customization**: Theme colors and activity images
- **Response Validation**: Detailed response information including success status

### Technical Details
- Python 3.7+ support
- Dependencies: requests library
- MIT License
- Full type hints support
- Comprehensive error handling

### Documentation
- Complete README with examples
- Inline code documentation
- Usage examples for different scenarios
- Error handling documentation
