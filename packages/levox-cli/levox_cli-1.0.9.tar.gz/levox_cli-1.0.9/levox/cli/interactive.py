"""
Levox Interactive CLI

This module provides an interactive command-line interface for Levox,
allowing users to run commands in a conversational manner.
"""

import sys
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt
from rich.align import Align
from rich import box

from .commands import cli
from .output import OutputManager
from ..core.config import load_default_config

class InteractiveCLI:
    """Interactive CLI interface for Levox."""
    
    def __init__(self):
        """Initialize the interactive CLI."""
        self.console = Console(emoji=(sys.platform != 'win32'))
        self.config = load_default_config()
        self.output_manager = OutputManager(self.config)
        self.running = True
        self.logging_enabled = False  # Track logging state
        
        # Set default logging level to ERROR (quiet mode)
        import logging
        logging.getLogger().setLevel(logging.ERROR)
    
    def run(self):
        """Run the interactive CLI."""
        try:
            # Show welcome screen
            self._show_welcome()
            
            # Main interactive loop
            while self.running:
                try:
                    user_input = Prompt.ask("\n[bold blue][levox][/bold blue]", default="help").strip()
                    if not user_input:
                        continue
                    
                    # Smart path handling: if user pasted a path, offer to scan it
                    maybe_path = user_input.strip('"').strip("'")
                    if self._looks_like_path(maybe_path):
                        path_obj = Path(self._normalize_windows_path(maybe_path)) if sys.platform == 'win32' else Path(maybe_path)
                        if path_obj.exists():
                            choice = Prompt.ask(
                                f"Detected path: [cyan]{path_obj}[/cyan]. Scan now?",
                                choices=["y", "n"],
                                default="y"
                            )
                            if choice.lower() == 'y':
                                # Execute scan directly and skip further parsing noise
                                self._execute_scan_command(f"scan {str(path_obj)}")
                                continue
                            else:
                                # Do not show an error; just continue the loop quietly
                                continue
                    
                    if user_input.lower() in ['exit', 'quit', 'q']:
                        self._show_goodbye()
                        break
                    
                    if user_input.lower() in ['help', 'h', '?']:
                        self._show_help()
                        continue
                    
                    if user_input.lower() in ['clear', 'cls']:
                        self.console.clear()
                        self._show_welcome()
                        continue
                    
                    # Handle log toggle command
                    if user_input.lower() in ['enable log', 'disable log', 'toggle log']:
                        self._toggle_logging(user_input.lower())
                        continue

                    
                    # Parse and execute command
                    self._execute_command(user_input)
                    
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]💡 Tip: Use 'exit' to quit the CLI[/yellow]")
                except SystemExit as e:
                    if e.code not in (0, None, 1):
                        self.console.print(f"[red]Command exited with code {e.code}[/red]")
                except Exception as e:
                    self.console.print(Panel(
                        f"[red]Error: {e}[/red]\n[dim]The command encountered an unexpected error[/dim]",
                        title="⚠️ Error",
                        border_style="red"
                    ))
                    
        except KeyboardInterrupt:
            self.console.print("\nOperation cancelled by user.")
            sys.exit(1)
    
    def _show_welcome(self):
        """Show the welcome screen."""
        self.output_manager.print_branding()
        
        # Compact welcome message
        self.console.print("[bold cyan]Welcome to Levox Interactive CLI![/bold cyan]")
        self.console.print("[dim]Type [bold]help[/bold] for commands • [bold]exit[/bold] to quit • [bold]clear[/bold] to clear screen[/dim]")
    
    def _show_help(self):
        """Show the help information."""
        help_table = Table(
            title="[bold cyan]Levox CLI Commands[/bold cyan]",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="white")
        help_table.add_column("Usage", style="dim")
        
        # Core Commands
        help_table.add_row("[bold]scan[/bold]", "Scan files/directories for PII/GDPR violations", "scan <path> [options]")
        help_table.add_row("[bold]status[/bold]", "Show capability status and license tiers", "status [--detailed]")
        help_table.add_row("[bold]report[/bold]", "Generate reports from saved results", "report <file> [options]")
        help_table.add_row("[bold]license[/bold]", "Manage license, register, or upgrade", "license [--register] [--upgrade]")
        help_table.add_row("[bold]feedback[/bold]", "Provide feedback to improve detection", "feedback <match_id> <verdict>")
        help_table.add_row("[bold]models[/bold]", "Manage and evaluate ML models", "models [options]")
        help_table.add_row("[bold]generate_report[/bold]", "Generate report from latest scan", "generate_report [options]")
        help_table.add_row("[bold]history[/bold]", "Show scan history and available results", "history [--detailed] [--limit N]")
        help_table.add_row("[bold]history[/bold]", "Clear all history: history --clear", "history --clear")
        help_table.add_row("[bold]history[/bold]", "Clear specific result: history --clear-id <id>", "history --clear-id <id>")
        help_table.add_row("[bold]history[/bold]", "Select specific result: history --select <id>", "history --select <id>")
        help_table.add_row("[bold]history[/bold]", "Export history: history --export <file>", "history --export <file>")
        
        # Advanced Commands
        help_table.add_row("[bold]ml_health[/bold]", "Check ML system health and performance", "ml_health [options]")
        help_table.add_row("[bold]switch_model[/bold]", "Switch to a different ML model", "switch_model [options]")
        help_table.add_row("[bold]generate_report[/bold]", "Generate reports from last scan", "generate_report [options]")
        help_table.add_row("[bold]set-report-directory[/bold]", "Choose where reports are saved", "set-report-directory")
        
        # Utility Commands
        help_table.add_row("[bold]clear[/bold]", "Clear the screen", "clear")
        help_table.add_row("[bold]enable log[/bold]", "Enable verbose logging output", "enable log")
        help_table.add_row("[bold]disable log[/bold]", "Disable verbose logging output", "disable log")
        help_table.add_row("[bold]toggle log[/bold]", "Toggle verbose logging on/off", "toggle log")
        help_table.add_row("[bold]exit[/bold]", "Exit the CLI application", "exit")
        
        self.console.print(help_table)
        
        # Show compact examples
        self.console.print("[bold yellow]💡 Quick Examples:[/bold yellow]")
        self.console.print("[cyan]•[/cyan] scan . --report json html  [cyan]•[/cyan] status --detailed  [cyan]•[/cyan] report --latest --format html")
        self.console.print("[cyan]•[/cyan] license --register  [cyan]•[/cyan] license --upgrade  [cyan]•[/cyan] history  [cyan]•[/cyan] set-report-directory")
    
    def _show_goodbye(self):
        """Show the goodbye message."""
        self.console.print("\n[bold green]Thank you for using Levox! 👋[/bold green]")
        self.console.print("[dim]Stay secure, stay compliant![/dim]")
    
    def _toggle_logging(self, command: str):
        """Toggle logging state and provide feedback."""
        if command == 'enable log':
            self.logging_enabled = True
            self.console.print("[green]✅ Logging enabled - verbose output will be shown[/green]")
        elif command == 'disable log':
            self.logging_enabled = False
            self.console.print("[yellow]🔇 Logging disabled - only essential output will be shown[/yellow]")
        elif command == 'toggle log':
            self.logging_enabled = not self.logging_enabled
            status = "enabled" if self.logging_enabled else "disabled"
            color = "green" if self.logging_enabled else "yellow"
            self.console.print(f"[{color}]🔄 Logging {status}[/{color}]")
        
        # Update the global logging level
        import logging
        if self.logging_enabled:
            logging.getLogger().setLevel(logging.INFO)
        else:
            logging.getLogger().setLevel(logging.ERROR)
        
        # Show current status
        status_text = "ON" if self.logging_enabled else "OFF"
        status_color = "green" if self.logging_enabled else "red"
        self.console.print(f"[dim]Current logging status: [{status_color}]{status_text}[/{status_color}][/dim]")

    
    def _execute_command(self, user_input: str):
        """Execute a user command."""
        # Handle scan command with special path parsing
        if user_input.lower().startswith('scan '):
            self._execute_scan_command(user_input)
            return
        
        # Handle report command with special parsing
        if user_input.lower().startswith('report '):
            self._execute_report_command(user_input)
            return
        
        # Handle generate_report command
        if user_input.lower().startswith('generate_report'):
            self._execute_generate_report_command(user_input)
            return
        
        # Handle other commands
        parts = user_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in {'scan', 'status', 'report', 'license', 'feedback', 'models', 'history', 'ml_health', 'switch_model', 'generate_report', 'set-report-directory'}:
            # Parse toggle flags for all commands
            parsed_args = [command]
            input_lower = user_input.lower()
            
            # Parse common toggle flags that work across commands
            if '--verbose' in input_lower or '-v' in input_lower:
                parsed_args.append('--verbose')
            elif self.logging_enabled:
                # Auto-add verbose flag if logging is enabled
                parsed_args.append('--verbose')
            if '--debug' in input_lower:
                parsed_args.append('--debug')
            if '--quiet' in input_lower or '-q' in input_lower:
                parsed_args.append('--quiet')
            if '--detailed' in input_lower:
                parsed_args.append('--detailed')
            if '--auto' in input_lower:
                parsed_args.append('--auto')
            if '--list' in input_lower:
                parsed_args.append('--list')
            if '--latest' in input_lower:
                parsed_args.append('--latest')
            if '--include-metadata' in input_lower:
                parsed_args.append('--include-metadata')
            if '--check-dependencies' in input_lower:
                parsed_args.append('--check-dependencies')
            
            # Special handling for license command to allow --register <KEY>
            if command == 'license':
                # Preserve the raw args to pass through to click parser
                raw_args = user_input.split()[1:]
                args = ['license'] + raw_args
                try:
                    exit_code = cli.main(args, standalone_mode=False)
                    if exit_code in (2, 3):
                        self.console.print(Panel(
                            f"[yellow]Command completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(args)}[/dim]",
                            title="⚠️ Command Warning",
                            border_style="yellow"
                        ))
                except Exception as e:
                    self.console.print(Panel(
                        f"[red]Error executing command: {e}[/red]\n[dim]Command: {' '.join(args)}[/dim]",
                        title="❌ Command Error",
                        border_style="red"
                    ))
                return

            # Parse format options
            if '--format' in input_lower:
                if 'json' in input_lower:
                    parsed_args.extend(['--format', 'json'])
                elif 'html' in input_lower:
                    parsed_args.extend(['--format', 'html'])
                elif 'pdf' in input_lower:
                    parsed_args.extend(['--format', 'pdf'])
                elif 'table' in input_lower:
                    parsed_args.extend(['--format', 'table'])
                elif 'markdown' in input_lower:
                    parsed_args.extend(['--format', 'markdown'])
            
            # Parse output options
            if '--output' in input_lower or '-o' in input_lower:
                import re
                match = re.search(r'--output\s+([^\s]+)', user_input)
                if match:
                    parsed_args.extend(['--output', match.group(1)])
                else:
                    match = re.search(r'-o\s+([^\s]+)', user_input)
                    if match:
                        parsed_args.extend(['--output', match.group(1)])
            
            # License tier is now automatically detected - no need to parse
            # Users should verify their license with: levox license --verify
            
            # Parse limit options
            if '--limit' in input_lower:
                import re
                match = re.search(r'--limit\s+(\d+)', user_input)
                if match:
                    parsed_args.extend(['--limit', match.group(1)])
            
            # Parse history-specific options
            if command == 'history':
                if '--clear' in input_lower:
                    parsed_args.append('--clear')
                if '--clear-id' in input_lower:
                    import re
                    match = re.search(r'--clear-id\s+([^\s]+)', user_input)
                    if match:
                        parsed_args.extend(['--clear-id', match.group(1)])
                if '--select' in input_lower:
                    import re
                    match = re.search(r'--select\s+([^\s]+)', user_input)
                    if match:
                        parsed_args.extend(['--select', match.group(1)])
                if '--export' in input_lower:
                    import re
                    match = re.search(r'--export\s+([^\s]+)', user_input)
                    if match:
                        parsed_args.extend(['--export', match.group(1)])
            
            # Execute command with parsed arguments
            try:
                exit_code = cli.main(parsed_args, standalone_mode=False)
                # Reduce noise: only show warning for actual errors (2/3)
                if exit_code in (2, 3):
                    self.console.print(Panel(
                        f"[yellow]Command completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(parsed_args)}[/dim]",
                        title="⚠️ Command Warning",
                        border_style="yellow"
                    ))
            except Exception as e:
                self.console.print(Panel(
                    f"[red]Error executing command: {e}[/red]\n[dim]Command: {' '.join(parsed_args)}[/dim]",
                    title="❌ Command Error",
                    border_style="red"
                ))
        else:
            # If it's not a known command and not a path, keep feedback minimal
            self.console.print("[yellow]Unknown command. Type 'help' for a list of commands.[/yellow]")
    
    def _execute_scan_command(self, user_input: str):
        """Execute a scan command with proper path handling."""
        # Extract the scan command and path
        command = 'scan'
        input_parts = user_input[5:].strip()  # Remove 'scan ' prefix
        
        # Parse the input to separate path from flags
        # Handle Windows paths with spaces properly
        import re
        
        # Find all flags (starting with -- or -)
        flag_pattern = r'\s+(--[a-zA-Z0-9-]+(?:[=:]\S+)?|\-[a-zA-Z0-9])\s*'
        flags_found = re.findall(flag_pattern, input_parts)
        
        # Remove flags from the input to get the path
        path_part = re.sub(flag_pattern, '', input_parts).strip()
        
        # If no path found, try to extract from the original input
        if not path_part:
            # Split by spaces and find the first non-flag argument
            parts = input_parts.split()
            for part in parts:
                if not part.startswith('--') and not part.startswith('-'):
                    path_part = part
                    break
        
        # Build the parts list
        parts = [path_part] + flags_found if path_part else flags_found
        
        # Now we have the path and flags separated
        flags = flags_found
        
        # If no path found, error
        if path_part is None:
            self.console.print("[red]Error: No path specified for scan command[/red]")
            return
        
        # Build the parsed parts
        parsed_parts = [path_part] + flags
        
        # First part should be the path
        path_part = parsed_parts[0]
        
        # Handle quoted paths
        if path_part.startswith('"') and path_part.endswith('"'):
            path_part = path_part[1:-1]
        elif path_part.startswith("'") and path_part.endswith("'"):
            path_part = path_part[1:-1]
        
        # Handle Windows path normalization
        if sys.platform == 'win32':
            path_part = self._normalize_windows_path(path_part)
        
        # Build the complete command line arguments
        args = ['scan', path_part]
        
        # Parse all options from the parsed parts (skip the first part which is the path)
        remaining_parts = parsed_parts[1:] if len(parsed_parts) > 1 else []
        
        # Process each flag
        i = 0
        while i < len(remaining_parts):
            flag = remaining_parts[i]
            
            if flag == '--report':
                # Handle --report format
                if i + 1 < len(remaining_parts):
                    report_format = remaining_parts[i + 1]
                    args.extend(['--report', report_format])
                    i += 2
                else:
                    i += 1
            elif flag in ['--verbose', '-v']:
                args.append('--verbose')
                i += 1
            elif flag == '--debug':
                args.append('--debug')
                i += 1
            elif flag in ['--quiet', '-q']:
                args.append('--quiet')
                i += 1
            elif flag in ['--cfg', '--deep-scan']:
                args.append('--cfg')
                i += 1
            elif flag == '--cfg-confidence':
                # Handle --cfg-confidence value
                if i + 1 < len(remaining_parts):
                    confidence = remaining_parts[i + 1]
                    args.extend(['--cfg-confidence', confidence])
                    i += 2
                else:
                    i += 1
            else:
                # Unknown flag, skip it
                i += 1
        
        # Add any remaining flags that weren't processed above
        for flag in remaining_parts:
            if flag not in ['--report', '--verbose', '-v', '--debug', '--quiet', '-q', '--cfg', '--deep-scan', '--cfg-confidence']:
                # Check if it's a format flag
                if flag == '--format' and remaining_parts.index(flag) + 1 < len(remaining_parts):
                    format_value = remaining_parts[remaining_parts.index(flag) + 1]
                    args.extend(['--format', format_value])
                # Check for other toggle flags
                elif flag in ['--telemetry', '--dev', '--scan-optional', '--no-scan-optional', 
                             '--allow-fallback-parsing', '--require-full-ast', '--no-report']:
                    args.append(flag)
        
        # Add verbose flag if logging is enabled and not already present
        if self.logging_enabled and '--verbose' not in args:
            args.append('--verbose')
        # Remove verbose flag if logging is disabled and present
        elif not self.logging_enabled and '--verbose' in args:
            args.remove('--verbose')
        
        # Debug output to see what's being executed
        self.console.print(f"[dim]Executing: {' '.join(args)}[/dim]")
        
        # Execute the command
        try:
            exit_code = cli.main(args, standalone_mode=False)
            # Reduce noise: only show warning for actual errors (2/3)
            if exit_code in (2, 3):
                self.console.print(Panel(
                    f"[yellow]Command completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(args)}[/dim]",
                    title="⚠️ Command Warning",
                    border_style="yellow"
                ))
        except Exception as e:
            self.console.print(Panel(
                f"[red]Error executing scan command: {e}[/red]\n[dim]Command: {' '.join(args)}[/dim]",
                title="❌ Scan Error",
                border_style="red"
            ))
    
    def _execute_report_command(self, user_input: str):
        """Execute a report command with proper parsing."""
        # Extract the report command and arguments
        command = 'report'
        args_part = user_input[7:].strip()  # Remove 'report ' prefix
        
        # Parse arguments
        args = ['report']
        
        # Check for file path (first argument)
        parts = args_part.split()
        if parts:
            # First part should be the results file
            args.append(parts[0])
            
            # Parse remaining options
            remaining = ' '.join(parts[1:])
            remaining_lower = remaining.lower()
            
            # Check for output format
            if '--format' in remaining_lower:
                # Extract the format value properly
                import re
                format_match = re.search(r'--format\s+(\w+)', remaining)
                if format_match:
                    format_value = format_match.group(1)
                    args.extend(['--format', format_value])
            
            # Check for output file
            if '--output' in remaining_lower or '-o' in remaining_lower:
                import re
                match = re.search(r'--output\s+([^\s]+)', remaining)
                if match:
                    args.extend(['--output', match.group(1)])
                else:
                    match = re.search(r'-o\s+([^\s]+)', remaining)
                    if match:
                        args.extend(['--output', match.group(1)])
        
        # Check for all report toggle flags
        if '--latest' in remaining_lower:
            args.append('--latest')
        
        if '--list' in remaining_lower:
            args.append('--list')
        
        if '--include-metadata' in remaining_lower:
            args.append('--include-metadata')
        
        if '--template' in remaining_lower:
            import re
            match = re.search(r'--template\s+([^\s]+)', remaining)
            if match:
                args.extend(['--template', match.group(1)])
        
        # Execute the command
        try:
            exit_code = cli.main(args, standalone_mode=False)
            # Reduce noise: only show warning for actual errors (2/3)
            if exit_code in (2, 3):
                self.console.print(Panel(
                    f"[yellow]Command completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(args)}[/dim]",
                    title="⚠️ Command Warning",
                    border_style="yellow"
                ))
        except Exception as e:
            self.console.print(Panel(
                f"[red]Error executing report command: {e}[/red]\n[dim]Command: {' '.join(args)}[/dim]",
                title="❌ Report Error",
                border_style="red"
            ))
    
    def _execute_generate_report_command(self, user_input: str):
        """Execute a generate_report command."""
        # Parse the command and options
        parts = user_input.split()
        command = 'generate-report'
        args = [command]
        
        # Parse format options
        input_lower = user_input.lower()
        if '--format' in input_lower:
            if 'json' in input_lower:
                args.extend(['--format', 'json'])
            elif 'html' in input_lower:
                args.extend(['--format', 'html'])
            elif 'pdf' in input_lower:
                args.extend(['--format', 'pdf'])
            elif 'table' in input_lower:
                args.extend(['--format', 'table'])
            elif 'markdown' in input_lower:
                args.extend(['--format', 'markdown'])
        
        # Parse output options
        if '--output' in input_lower or '-o' in input_lower:
            import re
            match = re.search(r'--output\s+([^\s]+)', user_input)
            if match:
                args.extend(['--output', match.group(1)])
            else:
                match = re.search(r'-o\s+([^\s]+)', user_input)
                if match:
                    args.extend(['--output', match.group(1)])
        
        # Parse other options
        if '--verbose' in input_lower or '-v' in input_lower:
            args.append('--verbose')
        if '--latest' in input_lower:
            args.append('--latest')
        
        try:
            # Execute the command
            from levox.cli.commands import cli
            exit_code = cli.main(args=args, standalone_mode=False)
            
            if exit_code == 0:
                self.console.print(Panel(
                    f"[green]Report generated successfully![/green]\n[dim]Command: {' '.join(args)}[/dim]",
                    title="✅ Report Generated",
                    border_style="green"
                ))
            else:
                self.console.print(Panel(
                    f"[yellow]Report generation completed with exit code: {exit_code}[/yellow]\n[dim]Command: {' '.join(args)}[/dim]",
                    title="⚠️ Report Warning",
                    border_style="yellow"
                ))
        except Exception as e:
            self.console.print(Panel(
                f"[red]Error executing generate_report command: {e}[/red]\n[dim]Command: {' '.join(args)}[/dim]",
                title="❌ Generate Report Error",
                border_style="red"
            ))
    
    def _normalize_windows_path(self, path_part: str) -> str:
        """Normalize Windows path for better compatibility."""
        # Convert forward slashes to backslashes for Windows
        path_part = path_part.replace('/', '\\')
        
        # Handle UNC paths and drive letters
        if path_part.startswith('\\\\'):
            # UNC path - leave as is
            pass
        elif len(path_part) >= 2 and path_part[1] == ':':
            # Drive letter path - ensure proper format
            path_part = path_part[0].upper() + path_part[1:]
        elif not path_part.startswith('\\\\') and not path_part.startswith('.') and not path_part.startswith('\\'):
            # Relative path - ensure it's properly formatted
            path_part = str(Path.cwd() / path_part)
        
        return path_part

    def _looks_like_path(self, text: str) -> bool:
        """Heuristic to detect if user pasted a filesystem path."""
        if not text:
            return False
        # Windows drive or UNC, absolute/relative paths, or contains path separators
        if sys.platform == 'win32':
            return (
                (len(text) >= 2 and text[1] == ':') or
                text.startswith('\\\\') or
                '\\' in text or '/' in text or
                text.startswith('.')
            )
        else:
            return text.startswith('/') or '/' in text or text.startswith('.')
