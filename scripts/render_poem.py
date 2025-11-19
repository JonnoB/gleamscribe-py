#!/usr/bin/env python3
"""Render the Namárië poem as PNG images using Tengwar Unicode characters.

This module provides functionality to transcribe and visualize Galadriel's Lament
(Namárië) in Tengwar script using multiple Unicode Tengwar fonts. It generates
PNG images with both the original text and Tengwar transcription, as well as
Tengwar-only versions.

The module uses Glaemscribe for Tengwar transcription and PIL for image
rendering. Output images are saved to the data directory with appropriate
labeling for each font variant used.

Typical usage example:
    python script.py
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont
from glaemscribe.parsers.mode_parser import ModeParser

def load_poem_outputs():
    """Load the poem transcription outputs."""
    import os
    # Load from tests/fixtures relative to repo root
    repo_root = os.path.dirname(os.path.dirname(__file__))
    fixture_path = os.path.join(repo_root, 'tests', 'fixtures', 'poem_transcription_canonical.json')
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _render_with_font(poem_data, font_path, label, base_filename):
    """Render the poem with a given font into labeled PNGs."""
    width = 800
    height = 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(font_path, 20)
        title_font = ImageFont.truetype(font_path, 24)
    except Exception:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()

    draw.text((50, 30), "Namárië (Galadriel's Lament)", font=title_font, fill='black')
    draw.text((50, 60), f"Transcribed using Glaemscribe Python ({label})", font=font, fill='gray')

    y_position = 100
    for i, line_data in enumerate(poem_data):
        line_text = f"{i+1}. {line_data['line']}"
        draw.text((50, y_position), line_text, font=font, fill='black')

        tengwar_text = line_data['output']
        draw.text((50, y_position + 25), tengwar_text, font=font, fill='blue')

        y_position += 60

    draw.text((50, height - 40), f"Unicode Tengwar ({label})", font=font, fill='gray')

    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(output_dir, exist_ok=True)

    out1 = os.path.join(output_dir, f'{base_filename}_transcription.png')
    img.save(out1)
    print(f"Poem rendered as '{out1}'")

    # Tengwar-only version
    img2 = Image.new('RGB', (width, height), color='white')
    draw2 = ImageDraw.Draw(img2)

    draw2.text((50, 30), f"Namárië - Tengwar Transcription ({label})", font=title_font, fill='black')
    y_position = 80
    for i, line_data in enumerate(poem_data):
        tengwar_text = line_data['output']
        draw2.text((50, y_position), tengwar_text, font=font, fill='black')
        y_position += 50

    draw2.text((50, height - 40), label, font=font, fill='gray')
    out2 = os.path.join(output_dir, f'{base_filename}_tengwar_only.png')
    img2.save(out2)
    print(f"Tengwar-only version saved as '{out2}'")


def render_poem():
    """Render the poem as PNG with multiple Tengwar fonts."""
    poem_data = load_poem_outputs()

    freemono_path = 'src/glaemscribe/fonts/FreeMonoTengwar.ttf'
    alcarin_reg_path = 'src/glaemscribe/fonts/AlcarinTengwar-Regular.ttf'
    alcarin_bold_path = 'src/glaemscribe/fonts/AlcarinTengwar-Bold.ttf'

    _render_with_font(poem_data, freemono_path, 'FreeMonoTengwar', 'namarie_poem')
    _render_with_font(poem_data, alcarin_reg_path, 'AlcarinTengwar-Regular', 'namarie_poem_alcarin_reg')
    _render_with_font(poem_data, alcarin_bold_path, 'AlcarinTengwar-Bold', 'namarie_poem_alcarin_bold')

if __name__ == "__main__":
    render_poem()
