#!/usr/bin/env python3
from src.glaemscribe.parsers.mode_parser import ModeParser


def tokens_after_post_ops(mode, tokens):
    ops = getattr(mode.post_processor, 'operators', [])
    out = list(tokens)
    for op in ops:
        out = op.apply(out, mode.default_charset)
    return out


def main():
    parser = ModeParser()
    mode = parser.parse("resources/glaemresources/modes/quenya-tengwar-classical.glaem")
    mode.processor.finalize({})

    text = "Ai ! laurië lantar lassi súrinen ,"
    success, _, debug = mode.transcribe(text)

    # Raw tokens from processor
    raw_tokens = mode.processor.transcribe(text, debug)
    print("Raw tokens (first 80):", raw_tokens[:80])

    # Tokens after post-processor operators (sequences, swaps, virtuals), before mapping to chars
    post_tokens = tokens_after_post_ops(mode, raw_tokens)
    # Drop empties and structural markers
    post_tokens = [t for t in post_tokens if t and t != "\\"]

    print("\nTokens after post ops (count={}):".format(len(post_tokens)))
    for t in post_tokens:
        print(t)

if __name__ == "__main__":
    main()
