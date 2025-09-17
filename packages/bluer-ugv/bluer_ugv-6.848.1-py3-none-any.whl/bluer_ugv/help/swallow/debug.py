from typing import List

from bluer_options.terminal import show_usage


def help_debug(
    tokens: List[str],
    mono: bool,
) -> str:
    args = [
        "[--generate_gif 0]",
        "[--save_images 0]",
    ]

    return show_usage(
        [
            "@swallow",
            "debug",
            "[-|<object-name>]",
        ]
        + args,
        "debug swallow.",
        mono=mono,
    )
