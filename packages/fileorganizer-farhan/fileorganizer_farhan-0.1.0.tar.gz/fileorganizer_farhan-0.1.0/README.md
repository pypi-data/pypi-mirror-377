# FileOrganizer

A Python package that organizes messy files in a folder into categorized subfolders.

## Features

- 📁 Automatically categorizes files based on extension
- 🏷️ Supports common file types: images, videos, documents, audio, code, archives
- 🔄 Creates subfolders automatically if they don't exist
- 🔄 Handles duplicate filenames by adding a suffix (_1, _2, etc.)
- 📝 Logs all actions (old path → new path) into a log file
- ↩️ Undo functionality to revert the last organization operation
- 🧰 Simple command-line interface

## Installation

### From PyPI

```bash
pip install fileorganizer
```

### From Source

```bash
git clone https://github.com/yourusername/fileorganizer.git
cd fileorganizer
pip install -e .
```

## Usage

### Command Line Interface

Organize files in a directory:

```bash
fileorganizer organize /path/to/messy/directory
```

Add the `-v` or `--verbose` flag for detailed output:

```bash
fileorganizer organize /path/to/messy/directory --verbose
```

Undo the last organization operation:

```bash
fileorganizer undo /path/to/organized/directory
```

### As a Python Package

You can also use FileOrganizer in your Python scripts:

```python
from fileorganizer import FileOrganizer

# Initialize the organizer with the target directory
organizer = FileOrganizer("/path/to/messy/directory")

# Organize files
moved_files = organizer.organize()

# Undo the last operation
undone_files = organizer.undo_last_operation()
```

## File Categories

FileOrganizer sorts files into the following categories:

- **images**: .jpg, .jpeg, .png, .gif, .bmp, .svg, .tiff, .webp
- **documents**: .doc, .docx, .pdf, .txt, .rtf, .odt, .md, .csv, .xls, .xlsx, .ppt, .pptx
- **audio**: .mp3, .wav, .flac, .aac, .ogg, .wma, .m4a
- **video**: .mp4, .avi, .mov, .wmv, .mkv, .flv, .webm, .m4v
- **code**: .py, .js, .html, .css, .java, .c, .cpp, .h, .php, .rb, .go, .rs, .ts, .json, .xml
- **archives**: .zip, .rar, .7z, .tar, .gz, .bz2, .xz
- **others**: Any file type not listed above

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.