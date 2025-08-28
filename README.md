# Zip

A modern file compression and archiving tool built with TypeScript and Python, designed for efficient file compression with cross-platform support.

## Features

- **Cross-Platform Compatibility**: Works seamlessly on Windows, macOS, and Linux
- **Multiple Format Support**: Supports ZIP, TAR, GZIP, and other popular archive formats
- **High Performance**: Optimized compression algorithms for fast processing
- **Modern Interface**: Clean, intuitive command-line interface
- **Batch Processing**: Compress multiple files and directories efficiently
- **Metadata Preservation**: Maintains file permissions and metadata during compression

## Installation

### Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- npm or yarn package manager

### Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
# Compress files to ZIP
npm run compress --input ./files --output archive.zip

# Extract ZIP files
npm run extract --input archive.zip --output ./extracted

# Batch compress multiple directories
npm run batch-compress --config ./config.json
```

### Python API

```python
from newzip import Compressor

# Create a new compressor instance
compressor = Compressor()

# Compress a directory
compressor.compress_directory('./source', './archive.zip')

# Extract an archive
compressor.extract_archive('./archive.zip', './destination')
```

## Project Structure

```
newzip/
├── src/
│   ├── typescript/          # TypeScript source code
│   └── python/             # Python modules
├── flows/                  # Workflow definitions
├── tasks/                  # Build and automation tasks
├── tests/                  # Unit and integration tests
├── package.json            # Node.js dependencies
├── pyproject.toml          # Python project configuration
└── README.md
```

## Development

### Setting Up Development Environment

1. Clone the repository
2. Install dependencies (see Installation section)
3. Run tests to ensure everything works

### Running Tests

```bash
# Run TypeScript tests
npm test

# Run Python tests
pytest

# Run all tests
npm run test:all
```

### Building

```bash
# Build TypeScript
npm run build

# Build Python package
python setup.py build
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## Support

- **Documentation**: [docs.newzip.dev](https://docs.newzip.dev)
- **Issues**: [GitHub Issues](https://github.com/your-org/newzip/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/newzip/discussions)

## Roadmap

- [ ] Support for additional archive formats (7z, RAR)
- [ ] GUI application using Electron
- [ ] Cloud storage integration
- [ ] Compression optimization profiles
- [ ] Batch processing with progress tracking

---

**Made with ❤️ by the NewZip team**