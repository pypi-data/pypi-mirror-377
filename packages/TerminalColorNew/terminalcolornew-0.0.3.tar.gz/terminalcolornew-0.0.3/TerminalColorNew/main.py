from rich.console import Console
from rich.style import Style


console = Console()

def printColor(string, r=0, g=255, b=0):
    rgb_style = Style(color=f"rgb({r},{g},{b})")
    console.print(string, style=rgb_style)