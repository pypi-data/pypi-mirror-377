from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional
import contextlib

import click

from . import __version__
from .core import DEFAULT_EXCLUDES, scan_directory
from .formatter import format_result, MARKDOWN, XML

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _comma_separated(ctx, param, value):  # click callback
    if value is None:
        return None
    parts = sorted({p.strip().lower().lstrip(".") for p in value.split(",") if p.strip()})
    return parts if parts else None


# --------------------------------------------------------------------------- #
# CLI definition
# --------------------------------------------------------------------------- #

examples = """
--------------------------------

Examples:

# Scan current directory with default rules
\n
scanc .
\n
# Scan only JS & TS files, include a tree, write to file
\n
scanc -e js,ts --tree -o scan.md .
\n
# Token count only (no output)
\n
scanc --tokens gpt-4o
\n
"""

@click.command(
    context_settings=dict(
        help_option_names=["-h", "--help"],
        max_content_width=100,
    ),
    help="Scan source code and emit AI-ready Markdown (or XML).",
    epilog=examples,
)

@click.version_option(__version__, "--version", "-V", prog_name="scanc")
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(file_okay=True, dir_okay=True, exists=True, path_type=Path),
    required=False,
    metavar="PATHS",
)
@click.option(
    "-e", "--ext", "extensions",
    callback=_comma_separated,
    metavar="EXTS",
    help="Comma-separated list of file extensions to include (e.g. py,js,ts). "
         "Case-insensitive; dots optional. Omit to include all.",
)
@click.option(
    "-i", "--include-regex", "include_regex",
    multiple=True,
    metavar="PATTERN",
    help="Regex pattern(s) to include. Matches against the full path. Can be repeated.",
)
@click.option(
    "-x", "--exclude-regex", "exclude_regex",
    multiple=True,
    metavar="PATTERN",
    help="Regex pattern(s) to exclude. Matches against the full path. Can be repeated.",
)
@click.option(
    "--no-default-excludes",
    is_flag=True,
    help=f"Do not use the built-in ignore list (default: {', '.join(sorted(DEFAULT_EXCLUDES))}).",
)
@click.option(
    "-t", "--tree/--no-tree",
    default=False,
    help="Prepend a Markdown directory tree to the scan result.",
)
@click.option(
    "-T", "--tokens", "model_name",
    metavar="MODEL",
    help="Print token count for MODEL (e.g. gpt-4o, gpt-3.5-turbo) and exit. Suppresses normal output.",
)
@click.option(
    "--max-size",
    type=int,
    metavar="BYTES",
    default=1_048_576,
    show_default=True,
    help="Skip individual files larger than this size.",
)
@click.option(
    "-o", "--out", "outfile",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    metavar="FILE",
    help="Write result to FILE instead of STDOUT.",
)
@click.option(
    "-f", "--format", "format_name",
    type=click.Choice(["markdown", "xml"], case_sensitive=False),
    default="markdown",
    show_default=True,
    help="Output format. Additional formats can be added via entry points.",
)
@click.option(
    "--follow-symlinks/--no-follow-symlinks",
    default=False,
    help="Traverse symlinks.",
)

def main(
    paths: List[Path],
    extensions: Optional[List[str]],
    include_regex: List[str],
    exclude_regex: List[str],
    no_default_excludes: bool,
    tree: bool,
    model_name: Optional[str],
    max_size: int,
    outfile: Optional[Path],
    format_name: str,
    follow_symlinks: bool,
) -> None:
    """
    Scan project source code and emit AI-ready Markdown.

    Examples

    --------

    • Scan current directory, default rules::
        scanc .

    • Scan only JS & TS files, include tree, write to file::

        scanc -e js,ts --tree -o scan.md .

    • Token count only::

        scanc --tokens gpt-4o
    """
    if not paths:
        paths = [Path.cwd()]
    # --------------------------------------------------------------------- #
    # Collect files
    files, tree_str = scan_directory(
        paths=paths,
        extensions=extensions,
        include_regex=include_regex,
        exclude_regex=exclude_regex,
        use_default_excludes=not no_default_excludes,
        include_tree=tree,
        max_size=max_size,
        follow_symlinks=follow_symlinks,
    )

    if model_name:
        from .token_counter import count_tokens, _require_tiktoken

        _require_tiktoken(cli=True)
        token_count = count_tokens(files, model_name)
        click.echo(f"{token_count:,.2f}")
        return

    formatted = format_result(
        files=files,
        tree=tree_str if tree_str else None,
        format_name=format_name,
    )

    try:
        stream_ctx = (
            outfile.open("w", encoding="utf-8")      # file handle
            if outfile
            else contextlib.nullcontext(click.get_text_stream("stdout"))  # keep stdout open
        )
        with stream_ctx as dest:
            dest.write(formatted)
    except OSError as exc:
        click.echo(f"✗ Could not write output: {exc}", err=True)
        sys.exit(1)
    if outfile:
        click.echo(f"✓ Saved to {outfile}", err=True)


if __name__ == "__main__":  # pragma: no cover
    main()