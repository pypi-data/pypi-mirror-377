# 🚀 GitIgnore Generator (`gitign`)

A powerful and user-friendly Python script to generate `.gitignore` files with default entries, custom patterns, or templates from [gitignore.io](https://gitignore.io) and to effortlessly create, manage, and clean your `.gitignore` files. Features rich console output and smart duplicate detection.

## ✨ Features

- 🎯 **Smart Generation**: Create `.gitignore` files with sensible defaults
- 🔄 **Template Support**: Fetch templates from gitignore.io for popular frameworks
- 🛡️ **Duplicate Prevention**: Automatically detects and prevents duplicate entries
- 🧹 **Cleanup Tool**: Remove duplicates from existing `.gitignore` files
- 📖 **Syntax Highlighting**: Beautiful syntax-highlighted file reading
- 🎨 **Rich Console Output**: Colorful and informative terminal interface
- ⚡ **Auto-Append Mode**: Intelligently appends to existing files
- 💾 **Backup Support**: Creates backups when cleaning files

## 📋 Requirements

- Python 3.6+
- [Rich](https://pypi.org/project/rich) library (`pip install rich`)
- [licface](https://pypi.org/project/licface) (`pip install licface`)  (*optional*, for enhanced help formatting)

## 🔧 Installation

1. Clone or download the script:
```bash
git clone https://github.com/cumulus13/gitignore.git
cd gitignore
```

2. Install dependencies:
```bash
pip install rich
```

3. Make the script executable (optional):
```bash
chmod +x gitignore.py
```

## 🚀 Quick Start

### Basic Usage

```bash
# Generate .gitignore with default entries
python gitignore.py

# Add custom entries (auto-appends if file exists)
python gitignore.py "*.log" "temp/" "config.local"

# Use templates from gitignore.io
python gitignore.py -t python node react

# Read existing .gitignore with syntax highlighting
python gitignore.py -r
```

## 📖 Usage Examples

### 🎯 Creating New .gitignore Files

```bash
# Basic generation with defaults
gitign

# Generate with custom entries
gitign "*.tmp" "debug.log" "*.cache"

# Generate with templates
gitign -t python django

# Generate without default entries
gitign --no-defaults -t python

# Force overwrite existing file
gitign -f "*.backup"
```

### 📝 Adding to Existing Files

```bash
# Auto-append mode (detects existing file)
gitign "new_pattern" "*.local"

gitign -d "secrets.txt" -d "temp/" -d "*.log"

# Explicit append mode
gitign -a "build/" "dist/"

# Add multiple entries with different separators
gitign "file1,file2;file3|file4"

# Combine Template and Custom Entries
gitign -t node -d ".env" -d "dist_electron/"
```

### 🧹 Cleaning Duplicates

```bash
# Preview duplicates without changes
gitign --clean --preview

# Remove duplicates (creates backup by default)
gitign --clean

# Remove duplicates without backup
gitign --clean --no-backup

# Clean file in specific directory
gitign --clean -p /path/to/project
```

### 📖 Reading Files

```bash
# Read .gitignore with syntax highlighting
gitign -r

# Read from specific directory
gitign -r -p /path/to/project
```

## ⚙️ Command Line Options

### Main Options

| Option | Short | Description |
|--------|-------|-------------|
| `--path` | `-p` | Target directory path (default: current directory) |
| `--data` | `-d` | Additional entries (can be repeated) |
| `--template` | `-t` | Templates from gitignore.io |
| `--append` | `-a` | Append to existing file without overwrite |
| `--force` | `-f` | Skip confirmation prompt |
| `--no-defaults` |  | Don't include default entries |
| `--read` | `-r` | Read and display .gitignore content |
| `--version` | `-v` | Show version information |

### Cleaning Options

| Option | Description |
|--------|-------------|
| `--clean` | Clean duplicate entries |
| `--preview` | Preview changes without applying |
| `--no-backup` | Don't create backup file |

### 🎯 All Options

| Option | Description |
| :--- | :--- |
| `-p PATH`, `--path PATH` | Target directory for the `.gitignore` file. (Default: current directory `.`) |
| `-d DATA`, `--data DATA` | Add a custom entry. Can be used multiple times. |
| `-t TEMPLATE [TEMPLATE ...]`, `--template TEMPLATE [TEMPLATE ...]` | Use one or more templates from [gitignore.io](https://www.toptal.com/developers/gitignore) (e.g., `python`, `node`, `java`). |
| `-a`, `--append` | Add entries to an existing `.gitignore` file instead of overwriting it. |
| `-f`, `--force` | Skip the overwrite confirmation prompt if `.gitignore` already exists. |
| `--no-defaults` | Prevent the script from adding its built-in default entries. |
| `-r`, `--read` | Display the content of the `.gitignore` file in the specified path with syntax highlighting. |
| `--clean` | Remove duplicate entries from the `.gitignore` file. |
| `--preview` | (With `--clean`) Show which duplicates would be removed without changing the file. |
| `--no-backup` | (With `--clean`) Do not create a `.gitignore.bak` backup file. |
| `-h`, `--help` | Show a help message and exit. |
| `-v`, `--version` | Show the script version and exit. |


### 🧾 Positional Arguments (`ENTRIES`)

You can pass entries directly as arguments. The script intelligently splits them based on common delimiters:

*   Comma (`,`): `gitign "*.tmp,*.log"`
*   Semicolon (`;`): `gitign "build/;dist/"`
*   Colon (`:`): `gitign "secrets.txt:config.ini"`
*   Pipe (`|`): `gitign "temp|cache"`
*   Space (` `): `gitign .vscode .idea`
*   Newline (`\n`): Useful when piping input.
*   Brackets: `gitign "[*.bak,*.old]"` or `gitign "{*.tmp,*.temp}"`
*   Quotes: `gitign "'my file.txt'"` or `gitign '"another file.log"'`

> **Note:** Backslashes (`\`) in entries are automatically converted to forward slashes (`/`) for cross-platform compatibility.


## 🎨 Default Entries

The script includes these default entries by default:

```gitignore
*.pyc
*.bak
*.zip
*.rar
*.7z
*.mp3
*.wav
*.sublime-workspace
.hg/
build/
*.hgignore
*.hgtags
*dist/
*.egg-info/
traceback.log
__pycache__/
*.log
```

## 🌟 Advanced Features

### 📝 Multiple Entry Formats

The script supports various entry formats:

```bash
# Comma-separated
python gitignore.py "file1,file2,file3"

# Space-separated (use quotes)
python gitignore.py "file1 file2 file3"

# Semicolon-separated
python gitignore.py "file1;file2;file3"

# Array-like format
python gitignore.py "[file1,file2,file3]"

# Quoted entries
python gitignore.py '"special file.txt"' "'another file.log'"
```

### 🔄 Template Examples

Popular templates available from gitignore.io:

```bash
# Programming languages
python gitignore.py -t python
python gitignore.py -t node javascript
python gitignore.py -t java maven
python gitignore.py -t csharp dotnetcore

# Frameworks
python gitignore.py -t react vue angular
python gitignore.py -t django flask
python gitignore.py -t rails laravel

# IDEs and editors
python gitignore.py -t vscode visualstudio
python gitignore.py -t intellij pycharm
python gitignore.py -t sublime vim

# Operating systems
python gitignore.py -t windows macos linux

# Combined templates
python gitignore.py -t python django vscode
```

### 🛡️ Smart Duplicate Detection

The script automatically:
- ✅ Reads existing `.gitignore` entries
- ✅ Prevents adding duplicate patterns
- ✅ Preserves comments and formatting
- ✅ Shows informative messages about skipped duplicates

## 🔧 Configuration

### Environment Variables

- `TRACEBACK=1`: Enable detailed error tracebacks

## 🎯 Use Cases

### For New Projects

```bash
# Python project
python gitignore.py -t python

# Node.js project
python gitignore.py -t node

# Full-stack project
python gitignore.py -t python node react vscode
```

### For Existing Projects

```bash
# Add build artifacts
python gitignore.py "build/" "dist/" "*.map"

# Add IDE files
python gitignore.py ".vscode/" ".idea/" "*.swp"

# Add OS-specific files
python gitignore.py -t macos windows linux
```

### Maintenance Tasks

```bash
# Clean up duplicated .gitignore
python gitignore.py --clean

# Preview what would be cleaned
python gitignore.py --clean --preview

# Backup and clean
python gitignore.py --clean  # Creates .gitignore.bak automatically
```

## 🐛 Troubleshooting

### Common Issues

**Unicode characters not displaying properly**
- Ensure your terminal supports UTF-8 encoding
- On Windows, try using Windows Terminal or enable UTF-8 support

**Permission errors**
- Make sure you have write permissions in the target directory
- Run with appropriate privileges if needed

**Template fetch failures**
- Check your internet connection
- Verify template names are correct (see gitignore.io)

### Debug Mode

Enable detailed tracebacks:

```bash
export TRACEBACK=1  # Linux/Mac
set TRACEBACK=1     # Windows
python gitignore.py [options]
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/cumulus13/gitignore.git
cd gitignore
pip install rich
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [gitignore.io](https://gitignore.io) for providing the template API
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- The Python community for inspiration and support

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/cumulus13/gitignore/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/cumulus13/gitignore/issues)
- 📧 **Email**: cumulus13@gmail.com

---

## Author
<div align="center">

**Made with ❤️ by [Hadi Cahyadi](https://github.com/cumulus13)**

⭐ **Star this repo if you find it helpful!** ⭐

</div>

## License

MIT License. See [LICENSE](`LICENSE`).

## Coffee

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)

[Support me on Patreon](https://www.patreon.com/cumulus13)

[Medium](https://medium.com/@cumulus13/gitign-the-smart-gitignore-generator-that-every-developer-needs-d9bd9b23a719)