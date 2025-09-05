# ZIP Operations for OOMOL Platform

A comprehensive collection of ZIP archive manipulation task blocks for the OOMOL workflow platform. This package provides 15 specialized task blocks covering all aspects of ZIP file operations, from basic compression and extraction to advanced features like encryption, encoding conversion, and archive management.

## 🎯 Overview

This OOMOL package enables users to work with ZIP archives through a visual workflow interface. Each task block is designed to be intuitive, reliable, and feature-rich, supporting both basic file operations and advanced use cases like encrypted archives, batch processing, and cross-platform encoding compatibility.

## ✨ Key Features

- **🔐 Full Encryption Support** - AES 128/192/256-bit encryption for secure archives
- **🌏 Encoding Compatibility** - Auto-detection and conversion for Chinese/Asian filenames
- **📊 Detailed Analytics** - Compression statistics, file counts, and processing summaries
- **🔄 Batch Processing** - Handle multiple files and folders efficiently  
- **🛠️ Advanced Operations** - Merge, split, validate, and selectively extract archives
- **📋 Rich UI Integration** - File pickers, save dialogs, and progress indicators
- **⚡ High Performance** - Optimized for large files and complex operations

## 📦 Task Blocks Overview

### Compression Tasks (5 blocks)

#### `zip-create` - Basic Archive Creation
Create ZIP archives from files or folders with standard compression.
- **Input**: Source path, output path, compression options
- **Output**: ZIP file path, compression statistics
- **Use Case**: General-purpose file archiving

#### `zip-create-encrypted` - Encrypted Archive Creation  
Create password-protected ZIP archives with AES encryption.
- **Input**: Source path, password, encryption strength (128/192/256)
- **Output**: Encrypted ZIP file with compression metrics
- **Use Case**: Secure file storage and transmission

#### `zip-compress-level` - Custom Compression
Create ZIP archives with configurable compression levels and methods.
- **Input**: Compression level (0-9), method (DEFLATED/STORED/BZIP2/LZMA)
- **Output**: ZIP file with detailed compression timing
- **Use Case**: Optimizing file size vs. processing time

#### `zip-add-files` - Append to Archive
Add new files to existing ZIP archives without recreating.
- **Input**: Existing ZIP path, files to add, conflict handling
- **Output**: Modified ZIP with addition summary
- **Use Case**: Incremental archive updates

#### `zip-batch-compress` - Bulk Compression
Compress multiple folders into separate ZIP files in one operation.
- **Input**: List of folders, output directory, naming patterns
- **Output**: Multiple ZIP files with batch processing summary
- **Use Case**: Organizing large collections of folders

### Extraction Tasks (4 blocks)

#### `zip-extract` - Standard Extraction
Extract ZIP archive contents to a specified directory.
- **Input**: ZIP path, output directory, structure options
- **Output**: Extracted files list and statistics
- **Use Case**: General file restoration and access

#### `zip-extract-encrypted` - Decrypt and Extract
Extract password-protected ZIP archives with validation.
- **Input**: ZIP path, password, verification options
- **Output**: Extracted files with password verification status
- **Use Case**: Accessing secure archives

#### `zip-extract-selective` - Partial Extraction
Extract only specific files from ZIP archives.
- **Input**: ZIP path, file selection list, structure preservation
- **Output**: Selected extracted files with skip report
- **Use Case**: Retrieving specific files without full extraction

#### `zip-extract-flat` - Flattened Extraction
Extract files to a flat directory structure, ignoring subdirectories.
- **Input**: ZIP path, file filters, conflict resolution
- **Output**: Flattened file structure with conflict handling
- **Use Case**: Consolidating files from complex directory structures

### Information Tasks (3 blocks)

#### `zip-list-contents` - Archive Inspection
List and analyze ZIP archive contents with detailed metadata.
- **Input**: ZIP path, sorting options, detail level
- **Output**: File listings, statistics, and structured data
- **Use Case**: Archive exploration and content verification

#### `zip-get-info` - Archive Metadata
Extract comprehensive information about ZIP files and their properties.
- **Input**: ZIP path, checksum calculation options
- **Output**: Detailed metadata, compression stats, file analysis
- **Use Case**: Archive analysis and quality assessment

#### `zip-validate` - Integrity Verification
Validate ZIP file integrity, test extraction, and verify checksums.
- **Input**: ZIP path, validation depth, testing options
- **Output**: Validation results, corruption reports, integrity status
- **Use Case**: Quality assurance and archive health checking

### Advanced Operations (3 blocks)

#### `zip-merge` - Archive Consolidation
Merge multiple ZIP archives into a single consolidated file.
- **Input**: List of ZIP files, conflict resolution, password handling
- **Output**: Merged archive with operation summary
- **Use Case**: Combining related archives or consolidating backups

#### `zip-split-by-size` - Archive Splitting
Split large ZIP files into smaller chunks based on size limits.
- **Input**: ZIP path, maximum size per chunk, naming patterns
- **Output**: Multiple split files with size distribution
- **Use Case**: Preparing archives for size-limited transfers or storage

#### `zip-convert-encoding` - Filename Encoding Repair
Fix filename encoding issues, especially for Chinese and Asian characters.
- **Input**: ZIP path, source/target encodings, auto-detection options  
- **Output**: Re-encoded archive with conversion statistics
- **Use Case**: Cross-platform compatibility and internationalization

## 🚀 Installation & Setup

### Prerequisites
- OOMOL Platform
- Python 3.10+ 
- Poetry (for dependency management)

### Installation
```bash
# Clone or download this package to your OOMOL workspace
git clone <repository-url> zip-operations

# Install dependencies
cd zip-operations
poetry install --no-root
```

### Dependencies
- `pyzipper` (0.3.6+) - ZIP operations with encryption support
- `pandas` (2.0.0+) - Data processing and analytics
- `chardet` (5.0.0+) - Character encoding detection
- `oocana` - OOMOL platform integration

## 📋 Usage Examples

### Basic Workflow: Compress → Validate → Extract
1. Use `zip-create` to compress project files
2. Use `zip-validate` to verify archive integrity  
3. Use `zip-extract` to restore files when needed

### Security Workflow: Encrypt → Verify → Decrypt
1. Use `zip-create-encrypted` with strong password
2. Use `zip-get-info` to verify encryption status
3. Use `zip-extract-encrypted` with password for access

### Batch Processing Workflow: Batch → Merge → Split
1. Use `zip-batch-compress` for multiple folders
2. Use `zip-merge` to consolidate related archives
3. Use `zip-split-by-size` for distribution-ready chunks

### Cross-Platform Workflow: Convert → Validate → Extract
1. Use `zip-convert-encoding` to fix filename issues
2. Use `zip-validate` to ensure compatibility
3. Use `zip-extract` for clean file restoration

## 🛠️ Technical Details

### Supported ZIP Features
- Standard ZIP compression (DEFLATED, STORED, BZIP2, LZMA)
- AES encryption (128/192/256-bit)
- Unicode filename support
- Large file support (>4GB with ZIP64)
- Directory structures and metadata preservation

### Encoding Support
- UTF-8 (primary)
- GBK/GB2312 (Chinese Simplified)  
- Big5 (Chinese Traditional)
- Shift_JIS (Japanese)
- EUC-KR (Korean)
- CP437 (DOS/Windows legacy)
- Auto-detection for mixed encodings

### Performance Characteristics
- Optimized for both speed and compression ratio
- Memory-efficient processing for large files
- Parallel processing support where applicable
- Progressive feedback for long operations

## 🔧 Configuration Options

Each task block provides extensive configuration through its UI:

- **File Selection**: Directory pickers, file filters, save dialogs
- **Security Options**: Password fields, encryption strength selection
- **Processing Options**: Compression levels, batch settings, naming patterns
- **Output Control**: Detailed logging, progress tracking, error handling

## 📊 Output Data

All task blocks provide structured output data including:

- **Operation Results**: Success/failure status, processed file counts
- **Performance Metrics**: Compression ratios, processing times, file sizes
- **Detailed Reports**: Pandas DataFrames with comprehensive operation data
- **Error Information**: Detailed error messages and troubleshooting guidance

## 🤝 Contributing

This package follows OOMOL development standards:

1. Each task block includes both `task.oo.yaml` configuration and `__init__.py` implementation
2. All inputs/outputs are properly typed with JSON schema definitions
3. Error handling includes user-friendly messages and recovery suggestions
4. UI components use appropriate widgets for file selection and data input
5. Documentation includes comprehensive parameter descriptions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Task block descriptions and parameter details
- **Examples**: Sample workflows and common use cases  
- **Issues**: Report bugs or request features through the OOMOL platform
- **Community**: Share workflows and best practices with other users

---

**Built for the OOMOL Platform** - Empowering visual workflow automation with powerful ZIP archive operations.