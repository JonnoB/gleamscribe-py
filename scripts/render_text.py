#!/usr/bin/env python3
"""Render arbitrary text as Tengwar using Glaemscribe.

This script transcribes plain text to Tengwar script and renders it as a PNG
image using Unicode Tengwar fonts. It supports multiple fonts and customizable
rendering options.

Typical usage examples:
    python render_tengwar.py "Elen síla lúmenn' omentielvo"
    python render_tengwar.py "Namárië" --font src/glaemscribe/fonts/AlcarinTengwar-Bold.ttf
    python render_tengwar.py "Hello" --mode resources/glaemresources/modes/quenya-tengwar-classical.glaem --output mytext.png
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

from glaemscribe.parsers.mode_parser import ModeParser

try:
    from glaemscribe.fonts import extract_bundled_fonts
except ImportError:  # pragma: no cover - optional dependency
    extract_bundled_fonts = None

DEFAULT_TEXT = "Elen síla lúmenn' omentielvo"
DEFAULT_MODE_NAME = "quenya-tengwar-classical"
DEFAULT_FONT_SIZE = 72
DEFAULT_OUTPUT = Path("tengwar_output.png")

# Available fonts
AVAILABLE_FONTS = {
    "freemono": "src/glaemscribe/fonts/FreeMonoTengwar.ttf",
    "alcarin-reg": "src/glaemscribe/fonts/AlcarinTengwar-Regular.ttf",
    "alcarin-bold": "src/glaemscribe/fonts/AlcarinTengwar-Bold.ttf",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "text",
        nargs="?",
        default=DEFAULT_TEXT,
        help="Plain text to transliterate to Tengwar"
    )
    parser.add_argument(
        "--mode",
        "-m",
        type=str,
        default=DEFAULT_MODE_NAME,
        help="Mode name (default: quenya-tengwar-classical) or path to a .glaem file"
    )
    parser.add_argument(
        "--font",
        "-f",
        help=(
            "Font to use. Either a path to a .ttf file, or one of: "
            "'freemono', 'alcarin-reg', 'alcarin-bold'. "
            "Defaults to a bundled CSUR font or FreeMonoTengwar if available."
        ),
    )
    parser.add_argument(
        "--font-size",
        type=int,
        default=DEFAULT_FONT_SIZE,
        help="Font size in points (default: 72)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output PNG path (default: tengwar_output.png)"
    )
    parser.add_argument(
        "--with-transcription",
        action="store_true",
        help="Include original text and transcription label in the image"
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=20,
        help="Padding around text in pixels (default: 20)"
    )
    parser.add_argument(
        "--bgcolor",
        default="white",
        help="Background color (default: white)"
    )
    parser.add_argument(
        "--textcolor",
        default="black",
        help="Text color (default: black)"
    )
    return parser.parse_args()


def resolve_font(font_arg: Path | str | None) -> Path:
    """Resolve font path from argument, preset name, or bundled fonts."""

    # Named preset or path string from CLI
    if isinstance(font_arg, str):
        key = font_arg.lower()
        # Known preset name
        if key in AVAILABLE_FONTS:
            font_path = Path(AVAILABLE_FONTS[key])
            if font_path.exists():
                return font_path
            print(f"Warning: preset font not found: {font_path}", file=sys.stderr)

        # Otherwise treat as filesystem path
        font_candidate = Path(font_arg)
        if font_candidate.exists():
            return font_candidate
        raise SystemExit(f"Font file not found: {font_candidate}")

    # Explicit Path object (e.g. from internal calls)
    if isinstance(font_arg, Path):
        if font_arg.exists():
            return font_arg
        raise SystemExit(f"Font file not found: {font_arg}")

    # Try bundled fonts
    if extract_bundled_fonts is not None:
        fonts = extract_bundled_fonts()
        if fonts:
            return fonts[0]

    # Fallback to freemono if it exists
    freemono = Path(AVAILABLE_FONTS["freemono"])
    if freemono.exists():
        return freemono

    raise SystemExit(
        "No font found. Install the `tengwar` package or pass --font to point at a CSUR font."
    )


def load_mode(mode_name_or_path: str) -> object:
    """Load and finalize a Glaemscribe mode."""
    from glaemscribe.resources import get_mode_path
    
    # Check if it's a file path or a mode name
    if "/" in mode_name_or_path or mode_name_or_path.endswith(".glaem"):
        # It's a path
        mode_path = Path(mode_name_or_path)
        if not mode_path.exists():
            raise SystemExit(f"Mode file not found: {mode_path}")
    else:
        # It's a mode name - use package resources
        mode_path = get_mode_path(mode_name_or_path)
    
    parser = ModeParser()
    mode = parser.parse(str(mode_path))
    mode.processor.finalize({})
    return mode


def transcribe(text: str, mode_name_or_path: str, charset_name: str | None = None) -> str:
    """Transcribe text to Tengwar using the specified mode."""
    mode = load_mode(mode_name_or_path)
    success, result, _debug = mode.transcribe(text, charset=charset_name)
    if not success:
        raise SystemExit(f"Glaemscribe transcription failed for text: {text}")
    return result


def render(
    text: str,
    mode_name_or_path: str,
    font_file: Path,
    font_size: int,
    output: Path,
    with_transcription: bool = False,
    padding: int = 20,
    bgcolor: str = "white",
    textcolor: str = "black",
) -> None:
    """Render text to Tengwar PNG image."""
    
    # Determine charset based on font name
    if "freemono" in font_file.name.lower():
        charset_name = "tengwar_freemono"
    else:
        charset_name = None
    
    # Transcribe text
    glyphs = transcribe(text, mode_name_or_path, charset_name)
    
    # Load font
    try:
        font = ImageFont.truetype(str(font_file), font_size)
        if with_transcription:
            label_font = ImageFont.truetype(str(font_file), int(font_size * 0.4))
        else:
            label_font = font
    except Exception as e:
        print(f"Warning: Could not load font {font_file}: {e}", file=sys.stderr)
        font = ImageFont.load_default()
        label_font = font
    
    # Estimate canvas size
    tmp_img = Image.new("RGBA", (10, 10), (255, 255, 255, 0))
    tmp_draw = ImageDraw.Draw(tmp_img)
    left, top, right, bottom = tmp_draw.textbbox((0, 0), glyphs, font=font)
    text_width = max(1, right - left)
    text_height = max(1, bottom - top)
    
    # Calculate dimensions with optional header
    width = text_width + padding * 2
    height = text_height + padding * 2
    
    if with_transcription:
        # Add space for original text and label
        label_bbox = tmp_draw.textbbox((0, 0), text, font=label_font)
        label_height = label_bbox[3] - label_bbox[1]
        height += label_height * 2.5  # Original text + spacing
    
    # Create image
    img = Image.new("RGB", (width, height), bgcolor)
    draw = ImageDraw.Draw(img)
    
    if with_transcription:
        # Draw original text
        label_height = tmp_draw.textbbox((0, 0), text, font=label_font)[3] - \
                       tmp_draw.textbbox((0, 0), text, font=label_font)[1]
        draw.text((padding, padding), text, font=label_font, fill=textcolor)
        draw.text((padding, padding + label_height * 1.5), 
                  "↓ Tengwar ↓", font=label_font, fill="gray")
        y_offset = padding + label_height * 2.5
    else:
        y_offset = padding
    
    # Draw Tengwar text
    draw.text((padding, y_offset), glyphs, font=font, fill=textcolor)
    
    # Save image
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output)
    print(f"✓ Rendered '{text}' to {output}")
    print(f"  Font: {font_file.name}")
    print(f"  Mode: {mode_name_or_path}")
    print(f"  Output size: {width}×{height} pixels")


def main() -> None:
    args = parse_args()
    font_file = resolve_font(args.font)
    render(
        args.text,
        args.mode,
        font_file,
        args.font_size,
        args.output,
        with_transcription=args.with_transcription,
        padding=args.padding,
        bgcolor=args.bgcolor,
        textcolor=args.textcolor,
    )


if __name__ == "__main__":
    main()