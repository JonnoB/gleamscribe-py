# Glaemscribe-py

A Python implementation of Glaemscribe for transcribing Tolkien's Elvish languages (Quenya and Sindarin) to Tengwar script using **Unicode**.

Glaemscribe-py is a Python port of the original [Glaemscribe](https://github.com/BenTalagan/glaemscribe). It focuses on Elvish → Tengwar transcription and outputs Unicode Private Use Area (PUA) characters instead of font-specific codes, so you can use modern Unicode Tengwar fonts.

## Key features

- **Quenya transcription** – Classical Quenya → Tengwar
- **Sindarin transcription** – General Sindarin → Tengwar
- **Font flexibility** – Works with several Unicode Tengwar fonts
- **PNG rendering helpers** – Example scripts for image output

## Fonts

This library outputs Unicode Tengwar (PUA) and can be used with any Unicode Tengwar font.

### Bundled fonts (OFL)

The repository includes a small, curated set of Unicode Tengwar fonts, all under the SIL Open Font License (OFL):

- **FreeMonoTengwar** – baseline font used during development
- **AlcarinTengwar-Regular** – Unicode Tengwar font
- **AlcarinTengwar-Bold** – bold companion font

These fonts live under `src/glaemscribe/fonts/` and are suitable for most uses. See the respective licence files alongside the fonts for details.

### Other fonts

You can also use any other Unicode Tengwar font (for example, Unicode-mapped versions of classic fonts such as Tengwar Annatar). These fonts are **not** bundled with `glaemscribe-py`; you must obtain them from their original sources and follow their licences.

## Supported languages & modes

### ✅ Implemented

- **Quenya (Classical)** – `quenya-tengwar-classical.glaem`
- **Sindarin (General)** – `sindarin-general.glaem`

### 🚧 Architecture ready, implementation needed

The core architecture supports all transcription modes from the original Glaemscribe.

Examples of modes that can be added this way:

- English Tengwar (phonemic, via eSpeak NG)
- Other Tengwar modes from the original Glaemscribe
- Cirth (runes), Sarati, and other scripts

## Installation

```bash
# Clone the repository
git clone https://github.com/JonnoB/glaemscribe-py.git
cd glaemscribe-py

# Install library (runtime only)
pip install -e .

# For development (tests, formatting, etc.)
pip install -e .[dev]
```

## Quick start

### Basic transcription (Quenya → Tengwar)

```python
from glaemscribe.parsers.mode_parser import ModeParser
from glaemscribe.resources import get_mode_path

parser = ModeParser()
mode = parser.parse(str(get_mode_path('quenya-tengwar-classical')))
mode.processor.finalize({})

success, result, debug = mode.transcribe("Elen síla lúmenn' omentielvo")
if success:
    print(result)  # Unicode Tengwar (PUA, U+E000+)
```

### Rendering a line to PNG

```python
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("src/glaemscribe/fonts/FreeMonoTengwar.ttf", 48)
img = Image.new("RGB", (800, 100), color="white")
draw = ImageDraw.Draw(img)
draw.text((20, 20), result, font=font, fill="black")
img.save("output.png")
```

## Contributing

Contributions are welcome! When contributing:

1. **Maintain compatibility** with original Glaemscribe behavior
2. **Add tests** for new features
3. **Follow existing** code style and patterns
4. **Update documentation** as needed

### Adding New Modes

To add a new transcription mode:
1. Convert the charset file from font-specific encoding to Unicode (FreeMonoTengwar)
2. Update the mode file to reference the Unicode charset
3. Add tests to verify transcription accuracy
4. For phonemic modes, integrate required preprocessing tools (e.g., eSpeak NG)

## License

This port follows the same license as the original Glaemscribe project (GNU Affero General Public License v3.0).

## Acknowledgments

- **Benjamin Babut (Talagan)** - Original creator of Glaemscribe
- **The Tengwar and Quenya community** - For supporting the creation of the original Glaemscribe  

---

**Original Implementation**: [Ruby/JavaScript](https://github.com/BenTalagan/glaemscribe)  
