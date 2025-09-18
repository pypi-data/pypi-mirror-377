#!/usr/bin/env python
# gitignore.py
# A simple script to generate a .gitignore file with default entries, additional entries, or
# templates from gitignore.io. It uses rich for console output and supports reading existing .gitignore files.
# Requires Python 3.6+ and the rich library.
# Copyright (c) 2023, Hadi Cahyadi <cumulus13@gmail.com>
# Homepage: https://github.com/cumulus13/gitignore
# Licensed under the MIT License.
# SPDX-License-Identifier: MIT

import sys
import argparse
import urllib.request
from pathlib import Path
from typing import List, Optional, Set
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax

try:
    from licface import CustomRichHelpFormatter
except ImportError:
    class CustomRichHelpFormatter(argparse.HelpFormatter):
        """Fallback formatter if licface is not installed."""
        def __init__(self, prog):
            super().__init__(prog, max_help_position=30, width=120)
            
from rich import traceback as rich_traceback
import os
rich_traceback.install(show_locals=False, theme='fruity', width=os.get_terminal_size().columns, extra_lines=1, word_wrap=True)
console = Console()

class GitignoreGenerator:
    DEFAULT_ENTRIES = [
        "*.pyc", "*.bak", "*.zip", "*.rar", "*.7z", "*.mp3", "*.wav", "*.sublime-workspace",
        ".hg/", "build/", "*.hgignore", "*.hgtags", "*dist/", "*.egg-info/", "traceback.log",
        "__pycache__/", "*.log"
    ]

    ICONS = {
        "start": "🚀",
        "write": "📝",
        "done": "✅",
        "error": "❌",
        "prompt": "❓"
    }

    @classmethod
    def fetch_template(cls, templates: List[str]) -> List[str]:
        try:
            url = f"https://www.toptal.com/developers/gitignore/api/{','.join(templates)}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; GitignoreGenerator/1.0)"}
            )
            with urllib.request.urlopen(req) as res:
                content = res.read().decode()
                return content.strip().splitlines()
        except Exception as e:
            console.print(f"{cls.ICONS['error']} [bold red]Failed fetch template from gitignore.io:[/bold red] {e}")
            return []

    @classmethod
    def read_existing_gitignore(cls, path: Path) -> Set[str]:
        """Read existing .gitignore file and return set of entries (excluding comments and empty lines)"""
        gitignore_path = path / ".gitignore"
        existing_entries = set()
        
        if gitignore_path.exists():
            try:
                with gitignore_path.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            existing_entries.add(line)
            except Exception as e:
                console.print(f"{cls.ICONS['error']} [bold yellow]Warning: Could not read existing .gitignore:[/bold yellow] {e}")
        
        return existing_entries

    @classmethod
    def remove_duplicates(cls, entries: List[str], existing_entries: Set[str] = None) -> List[str]:
        """Remove duplicates from entries list while preserving order and comments"""
        if existing_entries is None:
            existing_entries = set()
            
        seen = existing_entries.copy()
        unique_entries = []
        
        for entry in entries:
            entry = entry.strip()
            # Keep comments and empty lines as-is
            if not entry or entry.startswith('#'):
                unique_entries.append(entry)
            elif entry not in seen:
                seen.add(entry)
                unique_entries.append(entry)
                
        return unique_entries

    @classmethod
    def generate(
        cls,
        path: Path,
        extra_entries: Optional[List[str]] = None,
        append: bool = False,
        force: bool = False,
        templates: Optional[List[str]] = None,
        include_defaults: bool = True
    ) -> None:
        entries = []
        
        # Read existing entries if appending
        existing_entries = set()
        if append:
            existing_entries = cls.read_existing_gitignore(path)

        # Add template entries first
        if templates:
            template_entries = cls.fetch_template(templates)
            entries += template_entries

        # Add default entries only if explicitly requested AND (not appending OR file doesn't exist)
        gitignore_path = path / ".gitignore"
        if include_defaults and (not append or not gitignore_path.exists()):
            entries += cls.DEFAULT_ENTRIES

        # Add extra entries
        if extra_entries:
            entries += extra_entries

        # Remove duplicates
        entries = cls.remove_duplicates(entries, existing_entries)
        
        # Skip if no new entries to add
        if not entries:
            console.print("[yellow]No new entries to add to .gitignore.[/yellow]")
            return

        if gitignore_path.exists() and not force and not append:
            answer = input(f"{cls.ICONS['prompt']} .gitignore file already exists at {gitignore_path}. Overwrite? [y/N] ").strip().lower()
            if answer != 'y':
                console.print("[yellow]Canceled.[/yellow]")
                return

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Writing .gitignore file...", total=None)

                content = "\n".join(entries)
                if content and not content.endswith('\n'):
                    content += "\n"

                if append and gitignore_path.exists():
                    # Add a separator comment when appending
                    if entries:
                        separator = f"\n# Added entries ({len(entries)} items)\n"
                        with gitignore_path.open("a", encoding="utf-8") as f:
                            f.write(separator + content)
                else:
                    gitignore_path.write_text(content, encoding="utf-8")

                progress.update(task, description="[green]Finished writing .gitignore")
                progress.stop()

            action = "appended to" if append and gitignore_path.exists() else "created at"
            console.print(Panel.fit(
                f"{cls.ICONS['done']} [bold green].gitignore successfully {action}:[/bold green] {gitignore_path}",
                border_style="green"
            ))
            
            console.print(f"[dim]Added {len(entries)} entries.[/dim]")
                
        except Exception as e:
            console.print(
                f"{cls.ICONS['error']} [bold red]Failed to write .gitignore:[/bold red] {e}"
            )

    @classmethod
    def read_gitignore(cls, path: Path) -> None:
        """Read .gitignore with rich.syntax Syntax Coloring."""
        gitignore_path = path / ".gitignore"
        if not gitignore_path.exists():
            console.print(f"{cls.ICONS['error']} [bold red].gitignore file does not exist at {gitignore_path}[/bold red]")
            return

        try:
            content = gitignore_path.read_text(encoding="utf-8")
            syntax = Syntax(content, "gitignore", word_wrap=True)
            console.print(Panel.fit(
                syntax,
                title=f"{cls.ICONS['write']} [bold blue]Content of .gitignore[/bold blue]",
                border_style="blue"
            ))
        except Exception as e:
            console.print(f"{cls.ICONS['error']} [bold red]Failed to read .gitignore:[/bold red] {e}")
            

class GitCleaner:
    """GitIgnore Cleaner - Remove duplicate entries from .gitignore file"""

    ICONS = {
        "clean": "🧹",
        "done": "✅",
        "error": "❌"
    }

    @classmethod
    def clean_gitignore(cls, file_path: Path, backup: bool = True) -> None:
        """Clean duplicate entries from .gitignore file"""
        
        if not file_path.exists():
            console.print(f"[bold red]{cls.ICONS['error']} Error:[/bold red] {file_path} does not exist.")
            return
        
        try:
            # Read original content
            with file_path.open('r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Create backup if requested
            if backup:
                backup_path = file_path.with_suffix('.gitignore.bak')
                backup_path.write_text(''.join(lines), encoding='utf-8')
                console.print(f"[dim]Backup created: {backup_path}[/dim]")
            
            # Process lines to remove duplicates
            seen = set()
            cleaned_lines = []
            removed_count = 0
            
            for line in lines:
                stripped_line = line.strip()
                
                # Keep empty lines and comments as-is
                if not stripped_line or stripped_line.startswith('#'):
                    cleaned_lines.append(line)
                elif stripped_line not in seen:
                    seen.add(stripped_line)
                    cleaned_lines.append(line)
                else:
                    removed_count += 1
            
            # Write cleaned content back
            if removed_count > 0:
                with file_path.open('w', encoding='utf-8') as f:
                    f.writelines(cleaned_lines)
                
                console.print(Panel.fit(
                    f"[bold green]{cls.ICONS['done']} Cleaned {file_path}[/bold green]\n"
                    f"[dim]• Removed {removed_count} duplicate entries\n"
                    f"• Total unique entries: {len(seen)}[/dim]",
                    border_style="green",
                    title="Cleanup Complete"
                ))
            else:
                console.print(f"[yellow]No duplicates found in {file_path}[/yellow]")
                
        except Exception as e:
            console.print(f"[bold red]{cls.ICONS['error']} Error processing {file_path}:[/bold red] {e}")

    @classmethod
    def preview_changes(cls, file_path: Path) -> None:
        """Preview what would be removed without making changes"""
        
        if not file_path.exists():
            console.print(f"[bold red]{cls.ICONS['error']} Error:[/bold red] {file_path} does not exist.")
            return
        
        try:
            with file_path.open('r', encoding='utf-8') as f:
                lines = f.readlines()
            
            seen = set()
            duplicates = []
            unique_count = 0
            
            for i, line in enumerate(lines, 1):
                stripped_line = line.strip()
                
                if stripped_line and not stripped_line.startswith('#'):
                    if stripped_line in seen:
                        duplicates.append((i, stripped_line))
                    else:
                        seen.add(stripped_line)
                        unique_count += 1
            
            if duplicates:
                console.print(Panel.fit(
                    f"[bold yellow]Preview for {file_path}[/bold yellow]\n\n"
                    f"[dim]Duplicate entries that would be removed:[/dim]\n" +
                    "\n".join([f"Line {line_num}: {entry}" for line_num, entry in duplicates[:10]]) +
                    (f"\n... and {len(duplicates) - 10} more" if len(duplicates) > 10 else "") +
                    f"\n\n[dim]• Total duplicates: {len(duplicates)}\n"
                    f"• Unique entries: {unique_count}[/dim]",
                    border_style="yellow",
                    title="Preview Mode"
                ))
            else:
                console.print(f"[green]No duplicates found in {file_path}[/green]")
                
        except Exception as e:
            console.print(f"[bold red]{cls.ICONS['error']} Error previewing {file_path}:[/bold red] {e}")


def get_version():
    """
    Get the version.
    Version is taken from the __version__.py file if it exists.
    The content of __version__.py should be:
    version = "0.33"
    """
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
        else:
            return "0.0.0"  # Fallback if version file is not found
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            console.print_exception(show_locals=False, theme='fruity', width=os.get_terminal_size().columns, extra_lines=1, word_wrap=True)
        else:
            console.print(f"ERROR: {e}")

    return "0.0.0"
            

def main():
    parser = argparse.ArgumentParser(
        description="Generate .gitignore with default data, additional entries, or templates.",
        formatter_class=CustomRichHelpFormatter,
        prog='gitign'
    )
    
    # Main gitignore generator arguments
    parser.add_argument(
        "entries", nargs="*",
        help="Additional entries to add to .gitignore"
    )
    parser.add_argument(
        "-p", "--path", type=Path, default=Path("."),
        help="Path target .gitignore (default: current directory)"
    )
    parser.add_argument(
        "-d", "--data", action="append", default=[],
        help="Additional entry .gitignore (can be repeated)"
    )
    parser.add_argument(
        "-t", "--template", nargs="+", help="Use a template from gitignore.io (for example: python node java)"
    )
    parser.add_argument(
        "-a", "--append", action="store_true", help="Add to .gitignore without overwrite"
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="Skip the prompt if .gitignore already exists"
    )
    parser.add_argument(
        "--no-defaults", action="store_true", help="Don't include default entries"
    )
    parser.add_argument('-r', '--read', action='store_true', help='Read .gitignore file and print its content')
    parser.add_argument('-v', '--version', action='version', version=f'gitign {get_version()}',
                        help='Show the version of this script')
    
    # Clean arguments
    parser.add_argument(
        "--clean", action="store_true",
        help="Clean duplicate entries from .gitignore"
    )
    parser.add_argument(
        "--preview", action="store_true", 
        help="Preview changes without applying them (use with --clean)"
    )
    parser.add_argument(
        "--no-backup", action="store_true", 
        help="Don't create backup file (use with --clean)"
    )

    if len(sys.argv) == 1:
        parser.print_help()
        console.print(f"\n{GitignoreGenerator.ICONS['start']} [bold blue]Starting to create .gitignore ...[/bold blue]")
        GitignoreGenerator.generate(path=Path("."))
        sys.exit(0)
        
    args = parser.parse_args()
    
    # Handle clean command
    if args.clean:
        gitignore_path = args.path / ".gitignore"
        console.print(f"[bold blue]{GitCleaner.ICONS['clean']} GitIgnore Cleaner[/bold blue]")
        console.print(f"[dim]Target: {gitignore_path}[/dim]\n")
        
        if args.preview:
            GitCleaner.preview_changes(gitignore_path)
        else:
            GitCleaner.clean_gitignore(gitignore_path, backup=not args.no_backup)
        return

    # Process positional entries
    if args.entries:
        for entrie in args.entries:
            # Replace \ to /
            entrie = entrie.replace("\\", "/")
            if "," in entrie:
                args.data.extend(entrie.split(","))
            elif "\n" in entrie:
                args.data.extend(entrie.splitlines())
            elif ";" in entrie:
                args.data.extend(entrie.split(";"))
            elif ":" in entrie:
                args.data.extend(entrie.split(":"))
            elif "|" in entrie:
                args.data.extend(entrie.split("|"))
            elif " " in entrie:
                args.data.extend(entrie.split())
            elif entrie.startswith("[") and entrie.endswith("]"):
                args.data.extend(entrie[1:-1].split(","))
            elif entrie.startswith("{") and entrie.endswith("}"):
                args.data.extend(entrie[1:-1].split(","))
            elif entrie.startswith('"') and entrie.endswith('"'):
                args.data.append(entrie[1:-1])
            elif entrie.startswith("'") and entrie.endswith("'"):
                args.data.append(entrie[1:-1])
            elif entrie.startswith("`") and entrie.endswith("`"):
                args.data.append(entrie[1:-1])
            elif entrie.strip():
                args.data.append(entrie.strip())
            else:
                args.data.append(entrie)
            
    if args.read:
        GitignoreGenerator.read_gitignore(path=args.path)
        return

    console.print(f"{GitignoreGenerator.ICONS['start']} [bold blue]Starting to create .gitignore ...[/bold blue]")
    
    # Automatically use append mode if .gitignore exists and user provided entries
    auto_append = False
    gitignore_path = args.path / ".gitignore"
    if gitignore_path.exists() and (args.entries or args.data) and not args.force:
        auto_append = True
    
    GitignoreGenerator.generate(
        path=args.path,
        extra_entries=args.data if args.data else None,
        append=args.append or auto_append,
        force=args.force,
        templates=args.template,
        include_defaults=not args.no_defaults
    )


if __name__ == "__main__":
    main()