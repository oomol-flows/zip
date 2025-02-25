# ZIP

English | [Chinese](./README_zh-CN.md)

## Introduction

ZIP is an OOMOL Block encapsulated based on `adm-zip`, designed to simplify the compression and decompression of files and folders. Through this module, users can easily compress files or folders into ZIP format, or extract ZIP files to a specified location.

## Features

- **Compress files or folders**: Supports packing single files or entire folders into ZIP format compressed files.
- **Extract ZIP files**: Supports extracting files from ZIP archives to a specified directory.
- **Flexible operation options**: Provides multiple configuration options, such as specifying output paths, including or excluding specific files, etc.
- **Easy integration**: As part of OOMOL Block, it can be seamlessly integrated into larger workflows or projects.

## Notes

- When compressing large files or folders, ensure that the system has sufficient disk space.
- Before extraction, confirm whether the target directory is empty to avoid data loss caused by file overwriting.
- Customizable configuration items are supported to meet different scenario requirements; for more details, refer to the `adm-zip` official documentation.

## Reference Links

- [adm-zip Official Documentation](https://github.com/cthackers/adm-zip)