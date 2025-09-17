<pre>
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║  ███████╗████████╗███████╗ ██████╗ ██╗  ██╗██╗   ██╗██████╗  ║
║  ██╔════╝╚══██╔══╝██╔════╝██╔════╝ ██║  ██║██║   ██║██╔══██╗ ║
║  ███████╗   ██║   █████╗  ██║  ███╗███████║██║   ██║██████╔╝ ║
║  ╚════██║   ██║   ██╔══╝  ██║   ██║██╔══██║██║   ██║██╔══██╗ ║
║  ███████║   ██║   ███████╗╚██████╔╝██║  ██║╚██████╔╝██████╔╝ ║
║  ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ║
║                                                       ║
║           ░▒▓█ STEGANOGRAPHY METAPACKAGE █▓▒░         ║
║                                                       ║
║    ┌─[HIDE]───────────────────────────────[SEEK]─┐    ║
║    │    🔐 Advanced Steganography Toolkit 🔐     │    ║
║    │     ∴ What you see is not what you get ∴    │    ║
║    └─────────────────────────────────────────────┘    ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
</pre>

# StegHub - Advanced Steganography Toolkit

StegHub is a meta-package that installs all steganography tools in one command.

## Installation

```bash
pip install steghub
```

This automatically installs:
- **gradus** - Image steganography using histogram shifting
- **resono** - Audio steganography using phase coding  
- **shadowbits** - Image and Audio steganography using LSB

## Usage

### Use tools directly(Recommended):
```bash
gradus embed --in "secret message" --cover image.png --key mypassword
resono embed --in "secret message" --cover audio.wav --key mypassword
```

### Use through StegHub interface:
```bash
# Get help
steghub --help

# Use specific tools
steghub gradus embed --in "secret" --cover image.png --key mykey
steghub resono extract --stego audio_with_secret.wav --key mykey

# Check installed and update tools
steghub info
steghub list
steghub version
steghub check-update
steghub update
```

## Individual Tools

You can also install tools individually:
```bash
pip install gradus     # Image steganography only
pip install resono     # Audio steganography only
pip install shadowbits # Imgage and Audio steganography both
```
## 🔧 Tool Details

| Tool | Method | Supports | Best For |
|------|--------|----------|----------|
| **gradus** | Histogram shifting | PNG images | High-quality image hiding |
| **resono** | Phase coding | WAV audio | Undetectable audio secrets |
| **shadowbits** | LSB technique | Images & Audio | Any file type hiding |

## ⚡ Features

- **Unified interface** - One command to rule them all
- **Multiple algorithms** - Different techniques for different needs  
- **Password protection** - All tools support encryption keys
- **Cross-format** - Works with images and audio files
- **Easy installation** - Single pip install gets everything

## 🔐 Security Note

All tools use password-based encryption. Always use strong, unique passwords for your hidden data. Without the correct password, hidden content cannot be extracted.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

*"The best place to hide a leaf is in the forest"* 🌲

**Made with ❤️ by kaizoku**

</div>