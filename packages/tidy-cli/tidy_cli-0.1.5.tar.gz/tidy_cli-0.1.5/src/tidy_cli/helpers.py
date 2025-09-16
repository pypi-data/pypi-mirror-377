"""Module aimed at defining helper functions for main CLI program."""

# Import packages and modules

import time
from importlib.metadata import version

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


# Define helper functions
def get_version() -> str:
    """
    Function aimed at retrieving the CLI version from installed package metadata.

    :return: latest version of the CLI
    :rtype: str
    """
    try:
        return version("tidy-cli")
    except Exception:
        return "unknown"


def show_ascii_art() -> None:
    """
    Utility function aimed at printing nicely formatted 90s vibe ASCII art about CLI.

    :return: None
    :rtype: None
    """

    # ASCII art for TIDY with 90s styling
    tidy_art = """
████████╗██╗██████╗ ██╗   ██╗    ██████╗██╗     ██╗
╚══██╔══╝██║██╔══██╗╚██╗ ██╔╝   ██╔════╝██║     ██║
   ██║   ██║██║  ██║ ╚████╔╝    ██║     ██║     ██║
   ██║   ██║██║  ██║  ╚██╔╝     ██║     ██║     ██║
   ██║   ██║██████╔╝   ██║      ╚██████╗███████╗██║
   ╚═╝   ╚═╝╚═════╝    ╚═╝       ╚═════╝╚══════╝╚═╝
"""
    # Animate ASCII art line by line
    console.print("\n\n")
    lines = tidy_art.split("\n")
    colors = ["bold magenta", "bold cyan"]

    for i, line in enumerate(lines):
        if line.strip():  # Skip empty lines
            color = colors[i % len(colors)]
            console.print(Align.center(Text(line, style=color)))
            time.sleep(0.12)

    time.sleep(0.2)

    # Bottom decoration
    console.print()
    decoration = "▀▄▀▄▀▄ ✨ CLEAN CODE COMMAND LINE INTERFACE ✨ ▄▀▄▀▄▀"
    console.print(Align.center(Text(decoration, style="bright_white")))  # dim
    time.sleep(0.2)

    # Retro panel with system info style
    info_panel = Panel(
        Text(
            f"VERSION: {get_version()}\n MODE: DEVELOPMENT",
            style="bright_cyan",
            justify="center",
        ),
        title="[bright_magenta]◆ STATUS ◆[/bright_magenta]",
        border_style="bright_magenta",
        expand=False,
    )
    console.print()
    console.print(Align.center(info_panel))
    console.print()
