# Glaemscribe-py

A Python implementation of Glaemscribe for transcribing Tolkien's Elvish languages (Quenya and Sindarin) to Tengwar script using **Unicode**.

Glaemscribe-py is a Python port of the original [Glaemscribe](https://github.com/BenTalagan/glaemscribe). It focuses on Elvish → Tengwar transcription and outputs Unicode Private Use Area (PUA) characters instead of font-specific codes, so you can use modern Unicode Tengwar fonts.

## Key features

- **Quenya transcription** – Classical Quenya → Tengwar
- **Sindarin transcription** – General Sindarin → Tengwar
- **Font flexibility** – Works with any Unicode Tengwar TTF or OTF font
- **PNG rendering helpers** – Example scripts for image output

## Installation

```bash
 pip install glaemscribe
```

## Fonts

This library outputs Unicode Tengwar (PUA) and can be used with any Unicode Tengwar font. The repository includes a small, curated set of Unicode Tengwar fonts, all under the SIL Open Font License (OFL):

- **FreeMonoTengwar** – [baseline font](https://freetengwar.sourceforge.net/freemonotengwar.html) used during development
- **AlcarinTengwar-Regular** – Unicode Tengwar font by [Toshi Omagari](https://github.com/Tosche/Alcarin-Tengwar)
- **AlcarinTengwar-Bold** – Bold companion font by [Toshi Omagari](https://github.com/Tosche/Alcarin-Tengwar)

These fonts live under `src/glaemscribe/fonts/` and are suitable for most uses. See the respective licence files alongside the fonts for details. There are many Tengwar fonts available online, an example of how to use a custom font is shown in the [Quick start](#quick-start) section.


## Quick start

### Simple API (recommended)

The easiest way to use Glaemscribe is with the high-level `transcribe()` function:

```python
from glaemscribe import transcribe, list_modes

# Simple Quenya transcription
quenya_text = transcribe("Elen síla lúmenn' omentielvo", mode="quenya")
renderer = TengwarRenderer()
renderer.render_to_file(quenya_text, "quenya_text.png")
print(quenya_text)

# Sindarin transcription
sindarin_text = transcribe("Ai na vedui Dúnadan !", mode="sindarin")
# For other tengwar fonts simply pass in the path to the ttf or otf file
renderer_alcarin = TengwarRenderer(font_name='alcarin-bold', font_size=36)
renderer_alcarin.render_to_file(sindarin_text, "sindarin_text.png")

# List available modes
modes = list_modes()
print(modes)  # ['quenya', 'sindarin', 'english', ...]
```

Rendered outputs using the default fonts look like this:
Quenya example text rendered to Tengwar
![Quenya example text rendered to Tengwar](docs/images/quenya_text.png)
Sindarin example text rendered to Tengwar
![Sindarin example text rendered to Tengwar](docs/images/sindarin_text.png)

**Mode aliases** for convenience:
- `"quenya"` → Quenya Classical Tengwar
- `"sindarin"` → Sindarin General Use
- `"sindarin-beleriand"` → Sindarin Beleriand mode
- `"english"` → English Tengwar (experimental)

See `scripts/simple_usage.py` for more examples.

### Advanced usage (custom modes/options)

For advanced use cases, you can use the lower-level API:

```python
from glaemscribe.parsers.mode_parser import ModeParser
from glaemscribe.resources import get_mode_path

parser = ModeParser()
mode = parser.parse(str(get_mode_path('quenya-tengwar-classical')))
mode.processor.finalize({})

success, result, debug = mode.transcribe("Elen síla lúmenn' omentielvo")
if success:
    print(result)
```


### Example Scripts

The `scripts/` directory contains several useful examples:

- **`simple_usage.py`** - Simple API examples for common use cases
- **`render_text.py`** - Render Tengwar text to PNG images, also accepts custom fonts
- **`validate_unicode.py`** - Validate Unicode transcriptions
- **`render_poem.py`** - Render the Namárië poem with multiple fonts

Example:
```bash
uv run scripts/simple_usage.py
uv run scripts/render_text.py "Elen síla" --mode quenya --output output.png
```

## Contributing

Contributions are welcome! When contributing:

1. **Maintain compatibility** with original Glaemscribe behavior
2. **Add tests** for new features
3. **Follow existing** code style and patterns
4. **Update documentation** as needed

## TO DO

The core architecture supports all transcription modes from the original Glaemscribe.

Examples of modes that can be added this way:

- English Tengwar (phonemic, via eSpeak NG)
- Other Tengwar modes from the original Glaemscribe
- Cirth (runes), Sarati, and other scripts

## License

This port follows the same license as the original Glaemscribe project (GNU Affero General Public License v3.0).

## Acknowledgments

- **Benjamin Babut (Talagan)** - Original creator of Glaemscribe
- **The Tengwar and Quenya community** - For supporting the creation of the original Glaemscribe  

---
