"""
Publish Markdown files to Confluence wiki.

Copyright 2022-2025, Levente Hunyadi

:see: https://github.com/hunyadi/md2conf
"""

_EMOJI_TO_EMOTICON = {
    "grinning": "laugh",
    "heart": "heart",
    "slight_frown": "sad",
    "slight_smile": "smile",
    "stuck_out_tongue": "cheeky",
    "thumbsdown": "thumbs-down",
    "thumbsup": "thumbs-up",
    "wink": "wink",
}


def emoji_to_emoticon(shortname: str) -> str:
    return _EMOJI_TO_EMOTICON.get(shortname) or "blue-star"
