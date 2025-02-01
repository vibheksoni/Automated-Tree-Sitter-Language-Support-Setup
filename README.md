# Automated Tree-Sitter Language Support Setup

This script automates the process of downloading, installing, and setting up Tree-Sitter language parsers. It supports a wide range of programming languages, ensuring all necessary dependencies are installed and configuring the environment for both Unix-based systems and Windows.

## Features

- Downloads and installs Tree-Sitter language parsers
- Supports multiple languages including Python, JavaScript, TypeScript, Rust, Go, C, C++, Java, Ruby, PHP, C#, HTML, CSS, Bash, YAML, JSON, TOML, and Regex
- Handles compilation of language parsers
- Maintains a record of installed languages
- Simplifies integration of Tree-Sitter parsers into your projects

## Supported Languages

- Python
- JavaScript
- TypeScript
- Rust
- Go
- C
- C++
- Java
- Ruby
- PHP
- C#
- HTML
- CSS
- Bash
- YAML
- JSON
- TOML
- Regex

## Prerequisites

- Python 3.x
- Git
- C compiler (e.g., GCC, Clang, MSVC)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/vibheksoni/Automated-Tree-Sitter-Language-Support-Setup.git
    cd Automated-Tree-Sitter-Language-Support-Setup
    ```

2. Run the setup script:
    ```sh
    python treesitter_setup.py
    ```

## Usage

The script will automatically download and install the specified Tree-Sitter language parsers. You can modify the [LANGUAGE_CONFIGS](http://_vscodecontentref_/0) dictionary in the [treesitter_setup.py](http://_vscodecontentref_/1) file to add or remove languages as needed.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- [Tree-Sitter](https://github.com/tree-sitter) for providing the language parsing library.

## Author

[Vibhek Soni](https://github.com/vibheksoni)
