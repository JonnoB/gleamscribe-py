# Glaemscribe-py

A Python implementation of Glaemscribe for transcribing Tolkien's Elvish languages (Quenya and Sindarin) to Tengwar script using **Unicode**.

Glaemscribe-py is a Python port of the original [Glaemscribe](https://github.com/BenTalagan/glaemscribe). It focuses on Elvish → Tengwar transcription and outputs Unicode Private Use Area (PUA) characters instead of font-specific codes, so you can use modern Unicode Tengwar fonts.

## Key features

- ✅ **Quenya transcription** – Classical Quenya → Tengwar
- ✅ **Sindarin transcription** – General Sindarin → Tengwar
- ✅ **Unicode output** – Tengwar in the U+E000–U+F8FF range
- ✅ **Font flexibility** – Works with several Unicode Tengwar fonts
- ✅ **PNG rendering helpers** – Example scripts for image output
- ✅ **Extensible modes** – Same mode/charset architecture as original Glaemscribe

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

The library itself is font-agnostic: as long as your font supports the Tengwar code points used in the output, it will render correctly.

## Supported languages & modes

### ✅ Implemented

- **Quenya (Classical)** – `quenya-tengwar-classical.glaem`
- **Sindarin (General)** – `sindarin-general.glaem`

### 🚧 Architecture ready, implementation needed

The core architecture supports all transcription modes from the original Glaemscribe. To add more modes:

- Adapt the mode’s charset to Unicode.
- For phonemic modes (like English), integrate the required preprocessing tools (e.g. eSpeak NG).

Examples of modes that can be added this way:

- English Tengwar (phonemic, via eSpeak NG)
- Other Tengwar modes from the original Glaemscribe
- Cirth (runes), Sarati, and other scripts

## About Glaemscribe

Glaemscribe is the definitive transcription engine for Tolkien's languages and writing systems. Originally created by Benjamin Babut (Talagan), it enables accurate transcription between languages and writing systems.

**Original Project**: [BenTalagan/glaemscribe](https://github.com/BenTalagan/glaemscribe)  
**Official Site**: [Glaemscrafu](https://glaemscrafu.jrrvf.com/english/glaemscribe.html)

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
from src.glaemscribe.parsers.mode_parser import ModeParser

parser = ModeParser()
mode = parser.parse('resources/glaemresources/modes/quenya-tengwar-classical.glaem')
mode.finalize({})

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

## Advanced usage

Most users do not need this section. These examples are for debugging and advanced integrations.

### Using a specific charset

```python
from src.glaemscribe.parsers.charset_parser import CharsetParser

charset_parser = CharsetParser()
charset = charset_parser.parse("resources/glaemresources/charsets/tengwar_ds_sindarin.cst")

success, result, debug = mode.transcribe("text")
```

### Debug mode

```python
from src.glaemscribe.core.mode_debug_context import ModeDebugContext

debug_ctx = ModeDebugContext()
success, result, debug_ctx = mode.transcribe("text")

print("Processor output:", debug_ctx.processor_output)
print("Post-processor output:", debug_ctx.postprocessor_output)
```

## Testing

```bash
# Run all tests
uv run pytest
```

## Developer utilities

Helper scripts live under `scripts/` and are intended to be run as modules from the project root (so imports like `from src.glaemscribe...` work correctly).

### Render Namárië poem

Render the canonical Namárië transcription to PNGs in the `data/` directory:

```bash
uv run python -m scripts.render_poem
```

Outputs:

- `data/namarie_poem_transcription.png` – original lines + Tengwar
- `data/namarie_poem_tengwar_only.png` – Tengwar-only version

### English Ring Verse experiment (phonemic mode)

Experimental English Tengwar transcription of the Ring Verse (requires the phonemic `english-tengwar-espeak` mode; accuracy depends on future eSpeak NG integration):

```bash
uv run python -m scripts.test_english_ring_verse
```

Output:

- `data/ring_verse_english_tengwar.png`

### Debug transcription tree for "Ai ! laurië ..."

Build the Python transcription decision tree for debugging:

```bash
uv run python -m scripts.test_ai_lauri
```

This writes:

- `data/debug_tree_ai_lauri_python.json`

If you also place the JavaScript reference tree as:

- `data/debug_tree_ai_lauri_js.json`

you can compare them with:

```bash
uv run python -m scripts.compare_ai_lauri_trees
```

which produces:

- `data/debug_tree_ai_lauri_diff.txt`

### Unicode / Tengwar validation CLI

Validate a piece of text or a transcription result:

```bash
uv run python -m scripts.validate_unicode "some text"
uv run python -m scripts.validate_unicode --mode quenya-tengwar-classical "Elen síla lúmenn' omentielvo"
```

You can also list available modes:

```bash
uv run python -m scripts.validate_unicode --list-modes "dummy"
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
