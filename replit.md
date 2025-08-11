# Overview

This is a comprehensive web-based PDF converter application that transforms web pages into PDF documents while preserving layout and replacing video elements with clickable thumbnails. The application features both a Flask web interface and a command-line interface for converting web pages, with support for authentication, custom headers, viewport settings, and various PDF formatting options.

## Recent Updates (August 2025)
- ✅ **Scheduling System**: Added complete scheduling functionality for automatic conversions
- ✅ **Database Integration**: Integrated SQLAlchemy with SQLite for persistent storage
- ✅ **Background Processing**: Implemented background scheduler with threading
- ✅ **Web Interface**: Added scheduler management pages with full CRUD operations
- ✅ **Browser Compatibility**: Fixed Chromium dependency issues with software rendering

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Application Structure
The application follows a hybrid architecture combining a Flask web application with a standalone command-line tool:

- **Flask Web App**: Provides a user-friendly interface for web-based conversions with real-time progress tracking
- **CLI Module**: Offers command-line access to conversion functionality for automation and scripting
- **Background Processing**: Uses threading for non-blocking conversions with status tracking
- **Scheduling System**: Automatic conversion scheduling with configurable frequencies (once, daily, weekly, monthly)
- **Database Layer**: SQLAlchemy with SQLite for persistent storage of scheduled conversions and results

## Frontend Architecture
- **Template Engine**: Jinja2 templates with a base layout system
- **UI Framework**: Bootstrap 5 with dark theme for responsive design
- **Icons**: Feather icons for consistent iconography
- **Real-time Updates**: JavaScript polling for conversion progress tracking
- **Form Handling**: Progressive enhancement with client-side validation

## Backend Architecture
- **Web Framework**: Flask with modular route organization and database integration
- **Browser Automation**: Playwright with Chromium for web scraping and PDF generation (with fallback browser support)
- **Database**: SQLAlchemy ORM with SQLite for scheduled conversions, settings, and execution history
- **Scheduling Engine**: Multi-threaded background scheduler with automatic retry and error handling
- **Configuration Management**: Dataclass-based settings with multiple source support (CLI args, config files, environment variables)
- **File Management**: Automatic output directory creation with sanitized filenames based on page titles

## PDF Conversion Engine
- **Video Processing**: Automatic detection and replacement of video elements (YouTube, Vimeo, etc.) with clickable thumbnails
- **Authentication Support**: Form-based login handling for protected content
- **Customization Options**: Viewport dimensions, PDF margins, orientation, and scaling
- **Output Formats**: Generates both PDF and HTML snapshot files

## Configuration System
The application uses a layered configuration approach:
- Environment variables (lowest priority)
- YAML/JSON configuration files
- Command-line arguments (highest priority)

This allows flexible deployment scenarios while maintaining secure credential management.

## Error Handling and Logging
- Comprehensive error handling with user-friendly messages
- Debug-level logging for troubleshooting
- Graceful fallbacks for missing dependencies or network issues

# External Dependencies

## Core Dependencies
- **Playwright**: Browser automation and PDF generation engine
- **Flask**: Web application framework for the user interface
- **python-dotenv**: Environment variable management for configuration
- **PyYAML**: YAML configuration file parsing

## Browser Requirements
- **Chromium**: Headless browser engine installed via Playwright for consistent rendering across environments

## Frontend Dependencies
- **Bootstrap 5**: CSS framework loaded from CDN for responsive design
- **Feather Icons**: Icon library loaded from CDN for UI consistency

## File System
- **Output Directory**: Local `output/` directory for generated PDF and HTML files
- **Template System**: Jinja2 templates for web interface rendering
- **Static Assets**: CSS and JavaScript files for frontend functionality

## Network Dependencies
- **CDN Resources**: Bootstrap CSS/JS and Feather Icons loaded from external CDNs
- **Target Websites**: The web pages being converted (user-provided URLs)
- **Authentication Endpoints**: Optional login URLs for protected content access