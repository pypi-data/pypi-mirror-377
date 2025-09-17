# aii - AI Intelligence: Multi-Modal AI Assistant

`aii` (AI Intelligence) is a powerful multi-modal AI assistant that serves as your intelligent companion for translation, explanation, coding, writing, and shell automation - all powered by Google Gemini AI.

> 🚀 **Stay tuned!** We're actively developing new features and capabilities. Follow this project for updates on upcoming enhancements.

## Features

- **Multi-Modal AI**: Supports 5 different AI modes (shell, translate, explain, code, write)
- **Natural Language Interface**: Use intuitive commands like `aii translate "hello" to Spanish`
- **Smart Environment Detection**: Auto-detects your OS (macOS/Linux) and shell (bash, zsh, fish, etc.)
- **Context-Aware**: Provides culturally appropriate translations and OS-specific commands
- **Safe Execution**: Only prompts for execution on shell commands, not explanations or translations
- **High-Quality Output**: Shows confidence levels and provides detailed reasoning
- **Secure**: Uses environment variables for API keys with helpful setup guidance

## AI Modes

### 🐚 Shell Commands (Default)

Generate and execute shell commands with OS and shell-specific optimizations.

```bash
# Auto-detect environment and generate commands
aii install docker
aii list all python files
aii compress this folder

# Override detection
aii --os mac install nginx          # Force macOS
aii --shell fish find large files   # Force fish syntax
aii -m -s zsh copy file             # macOS + zsh combo
```

### 🌐 Translation Mode

Natural, culturally appropriate translations that avoid machine-translate awkwardness.

```bash
# Natural language detection
aii translate "Hello world" to Spanish
aii translate "I'm running late" to French

# Explicit target language
aii translate "Good morning" --to Japanese
aii trans "Bonjour" to English                # Short form
```

### 🎓 Explanation Mode

Clear, comprehensive explanations of complex topics with examples and analogies.

```bash
# Get detailed explanations
aii explain "How does Docker work?"
aii explain "Machine learning algorithms"
aii exp "Why is the sky blue?"              # Short form
```

### 💻 Code Mode

Generate, review, and debug code with best practices and security considerations.

```bash
# Code generation
aii code "Python function to sort a list"
aii code "React component for user login"
aii coding "Fix this JavaScript bug"        # Alternative form
```

### ✍️ Write Mode

Create well-structured, purpose-driven content for various contexts.

```bash
# Content generation
aii write "Professional email declining meeting"
aii write "Blog post intro about AI trends"
aii writing "Cover letter for developer role"  # Alternative form
```

## Quick Start

### Installation

```bash
# Install with uv
uv pip install aii

# Or install from source
git clone <repository-url>
cd aii
uv pip install .
```

### Setup

1. **Get your Google Gemini API key** from [AI Studio](https://aistudio.google.com/apikey)

2. **Set the environment variable:**

```bash
# For Fish shell
set -x GEMINI_API_KEY your_api_key_here

# For Bash/Zsh
export GEMINI_API_KEY=your_api_key_here
```

3. **Make it permanent** by adding to your shell config:

```bash
# Fish
echo "set -x GEMINI_API_KEY your_api_key_here" >> ~/.config/fish/config.fish

# Bash
echo "export GEMINI_API_KEY=your_api_key_here" >> ~/.bashrc

# Zsh
echo "export GEMINI_API_KEY=your_api_key_here" >> ~/.zshrc
```

### Basic Usage

```bash
# Shell commands (default mode)
aii install docker
aii find files larger than 100MB

# Translation (natural syntax)
aii translate "Hello world" to Spanish
aii trans "Bonjour" to English

# Explanations (natural syntax)
aii explain "quantum computing"
aii exp "how does GPS work"

# Code generation (natural syntax)
aii code "Python web scraper"
aii coding "React todo component"

# Content writing (natural syntax)
aii write "resignation letter"
aii writing "product launch announcement"
```

## Advanced Usage

### Command-Line Options

```bash
# Mode selection
aii --mode translate "Hello" --to Spanish
aii --translate "Good morning" --to French    # Shortcut
aii -t "Hola" to English                      # Short form

# Shell-specific options (for shell mode)
aii --os mac install nginx                   # Force macOS
aii --shell fish list files                  # Force fish shell
aii -m -s zsh compress folder                # Combine options

# Get help
aii --help
aii --version
```

### Environment-Specific Features

#### macOS Optimizations

- Uses Homebrew for package management
- Leverages macOS commands: `open`, `pbcopy`, `pbpaste`, `mdfind`
- Accounts for BSD utilities vs GNU versions
- Service management with `launchctl`

#### Linux Optimizations

- Supports multiple package managers (apt, yum, dnf, pacman)
- Uses GNU versions of utilities
- Service management with `systemctl`
- Clipboard operations with `xclip`/`wl-clipboard`

#### Shell-Specific Adaptations

- **Fish**: Uses `set var value` syntax, `and`/`or` logic
- **Zsh**: Enhanced globbing, Oh-My-Zsh compatibility
- **Bash**: POSIX compliance, brace expansion

## Example Interactions

### Smart Translation

```bash
$ aii translate "I'm really excited about this project" to Spanish
🌐 Translation Logic: Converting informal English expression to Spanish, maintaining enthusiasm and colloquial tone...

🌐 Translation:
Estoy muy emocionado/a por este proyecto

🎯 Confidence: 95%
```

### Technical Explanations

```bash
$ aii explain "Docker containers"
🎓 Explanation Structure: I'll explain Docker containers using the shipping analogy, then cover technical details...

🎓 Explanation:
Docker containers are like standardized shipping containers for software applications. Just as shipping containers allow goods to be transported consistently across different ships, trucks, and trains, Docker containers package applications with all their dependencies so they run consistently across different computing environments...

[Detailed explanation continues]

🎯 Confidence: 92%
```

### Code Generation

```bash
$ aii code "Python function to validate email addresses"
💻 Code Planning: I'll create a robust email validation function using regex with proper error handling...

💻 Generated Code:

```python
import re
from typing import bool

def validate_email(email: str) -> bool:
    """
    Validate email address using RFC 5322 compliant regex.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

# Example usage
if __name__ == "__main__":
    test_emails = ["user@example.com", "invalid.email", "test@domain.co.uk"]
    for email in test_emails:
        print(f"{email}: {validate_email(email)}")
```

🎯 Confidence: 88%
```

## Debugging

Enable debug mode to troubleshoot issues:

```bash
# Show detailed debug information
AII_DEBUG=true aii explain "quantum physics"
```

Debug mode shows:

- Mode detection and setup
- AI reasoning process
- Response creation and handling
- Mode verification steps

## Troubleshooting

### API Key Issues

```text
❌ Error: GEMINI_API_KEY environment variable is required.
💡 Setup: export GEMINI_API_KEY=your_api_key_here
🔗 Get key: https://aistudio.google.com/apikey
```

**Solution**: Follow the setup instructions above to configure your API key.

### Mode Detection Issues

If the wrong mode is detected, use explicit mode selection:

```bash
# Instead of: aii explain something
# Use: aii --mode explain something
```

### Shell/OS Detection Issues

Override detection when working on remote systems:

```bash
aii --os linux --shell bash your_command
```

## Command Reference

### Modes and Shortcuts

- `--mode shell` or default - Shell command generation
- `--mode translate` or `-t` - Translation mode
- `--mode explain` or `-e` - Explanation mode
- `--mode code` or `-c` - Code generation mode
- `--mode write` or `-w` - Writing mode

### Natural Language Triggers

- `aii translate ...` - Auto-detected translation
- `aii explain ...` - Auto-detected explanation
- `aii code ...` - Auto-detected code generation
- `aii write ...` - Auto-detected writing

### Shell Options (Shell Mode Only)

- `--os mac` or `-m` - Force macOS mode
- `--os linux` or `-l` - Force Linux mode
- `--shell SHELL` or `-s` - Override shell detection

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Apache License 2.0 - see LICENSE file for details.

## Acknowledgments

- Powered by [Google Gemini AI](https://ai.google.dev/)
- Built with [Pydantic AI](https://ai.pydantic.dev/)
- Inspired by the need for intelligent, multi-modal command-line tools

---

**Made with ❤️ for developers who want AI-powered assistance across all their tasks**