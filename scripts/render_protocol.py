# /// script
# requires-python = ">=3.12"
# dependencies = ["mistune>=3,<4"]
# ///
"""Lay out a campaign protocol as the A4 sheet carried to the bench.

Markdown in, a self-contained HTML page and a PDF out. The tracked markdown
stays the record; this only sets it, so the sheet and the document it came
from cannot drift apart.

Three conventions in the markdown drive the layout, and each is already the
natural way to write the thing:

- a table whose first header cell is empty is a form -- its first column
  labels, its empty cells become writing space, and a header row that is
  empty throughout is dropped;
- a table whose first header cell is `#` is a numbered run of steps;
- `- [ ]` prints as a checkbox;
- a closing paragraph -- the free-text section every sheet ends with -- is
  followed by a box to write in.

Nothing here stamps the output with a generation date. The sheet carries a
date field because a person fills it in at the bench.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import mistune
from mistune.renderers.html import HTMLRenderer

REPO_ROOT = Path(__file__).resolve().parent.parent
STYLESHEET = Path(__file__).with_name("protocol-sheet.css")
DEFAULT_OUT_DIR = REPO_ROOT / "build"

# Checked in PATH first, then at their usual installed locations. Any
# Chromium build will do; the PDF is produced by its print path.
BROWSER_NAMES = ("chrome", "chromium", "chromium-browser", "msedge", "brave")
BROWSER_PATHS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
)


class SheetRenderer(HTMLRenderer):
    """Emits the classes the stylesheet keys off.

    Header cells are collected as they render so that a table can be
    classified once its header is known: `fill` for a form, `steps` for a
    numbered run, `data` otherwise. A form whose header is empty throughout
    also carries `headless`, and the stylesheet drops the header row.
    """

    def __init__(self) -> None:
        super().__init__()
        self._head: list[str] = []

    def table_cell(self, text: str, align: str | None = None, head: bool = False) -> str:
        tag = "th" if head else "td"
        attrs = f' style="text-align:{align}"' if align else ""
        if head:
            self._head.append(text.strip())
        elif not text.strip():
            attrs += ' class="blank"'
        return f"<{tag}{attrs}>{text}</{tag}>\n"

    def table(self, text: str) -> str:
        head, self._head = self._head, []
        if head and not head[0]:
            kind = "fill" if any(head) else "fill headless"
        elif head[:1] == ["#"]:
            kind = "steps"
        else:
            kind = "data"
        return f'<table class="{kind}">\n{text}</table>\n'


def render_html(markdown_text: str, css: str) -> str:
    """Wrap the rendered markdown in a standalone page with the CSS inlined."""
    to_html = mistune.create_markdown(
        renderer=SheetRenderer(), plugins=["table", "task_lists"]
    )
    body = to_html(markdown_text)
    title = next(
        (line[2:].strip() for line in markdown_text.splitlines() if line.startswith("# ")),
        "Protocol",
    )
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{title}</title>\n<style>\n{css}</style>\n</head>\n"
        f"<body>\n{body}</body>\n</html>\n"
    )


def find_browser() -> str | None:
    """Locate a Chromium build, honouring BEANOMETER_BROWSER if it is set."""
    override = os.environ.get("BEANOMETER_BROWSER")
    if override:
        return override
    for name in BROWSER_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return next((p for p in BROWSER_PATHS if Path(p).exists()), None)


def html_to_pdf(browser: str, html_path: Path, pdf_path: Path) -> None:
    """Print the page through a headless browser, in a throwaway profile.

    The profile is disposable so that the run neither picks up nor disturbs a
    browser the operator already has open.
    """
    with tempfile.TemporaryDirectory(prefix="beanometer-print-") as profile:
        subprocess.run(
            [
                browser,
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--user-data-dir={profile}",
                "--virtual-time-budget=4000",
                f"--print-to-pdf={pdf_path}",
                html_path.as_uri(),
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )


def output_stem(source: Path) -> str:
    """Name the output for its campaign, since every campaign has a protocol."""
    source = source.resolve()
    if source.parent.name in ("", "docs", "experiments"):
        return source.stem
    return f"{source.parent.name}-{source.stem}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path, help="the protocol markdown to lay out")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help=f"output PDF path (default: {DEFAULT_OUT_DIR.name}/<campaign>-<name>.pdf)",
    )
    parser.add_argument(
        "--html-only", action="store_true", help="write the page and skip the PDF"
    )
    args = parser.parse_args()

    pdf_path = args.out or DEFAULT_OUT_DIR / f"{output_stem(args.source)}.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    html_path = pdf_path.with_suffix(".html")

    html = render_html(
        args.source.read_text(encoding="utf-8"), STYLESHEET.read_text(encoding="utf-8")
    )
    html_path.write_text(html, encoding="utf-8", newline="\n")
    print(f"page {html_path}")

    if args.html_only:
        return 0

    browser = find_browser()
    if browser is None:
        print(
            "no Chromium build found: open the page above and print it to PDF,"
            " A4 at 100%, or set BEANOMETER_BROWSER",
            file=sys.stderr,
        )
        return 1

    html_to_pdf(browser, html_path, pdf_path)
    print(f"sheet {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
