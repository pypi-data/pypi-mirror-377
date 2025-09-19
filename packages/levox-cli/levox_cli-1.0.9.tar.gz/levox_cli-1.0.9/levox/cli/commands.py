"""
Levox CLI Commands

This module defines the Click-based CLI commands with clean separation of concerns.
Each command delegates to appropriate services and uses the output manager for display.
"""

import click
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import json 

from .services import ScanService, ReportService, StatusService
from .services import (
    EXIT_SUCCESS,
    EXIT_VIOLATIONS_FOUND,
    EXIT_RUNTIME_ERROR,
    EXIT_CONFIG_ERROR,
)
from .output import OutputManager
from ..core.config import Config, load_default_config
from ..core.exceptions import LevoxException, ConfigurationError

# Global services (initialized in main)
scan_service: Optional[ScanService] = None
report_service: Optional[ReportService] = None
status_service: Optional[StatusService] = None
output_manager: Optional[OutputManager] = None

def initialize_services(config: Config):
    """Initialize global services with configuration."""
    global scan_service, report_service, status_service, output_manager
    
    output_manager = OutputManager(config)
    scan_service = ScanService(config, output_manager)
    report_service = ReportService(config, output_manager)
    status_service = StatusService(config, output_manager)

def print_version(ctx, param, value):
    """Print version information and exit."""
    if not value or ctx.resilient_parsing:
        return
    
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    
    console = Console()
    
    version_text = Text("Levox v1.0.9", style="bold blue")
    subtitle = Text("Enterprise PII/GDPR Detection Tool", style="cyan")
    beta_tag = Text("Beta Ready", style="yellow")
    
    panel = Panel(
        f"{version_text}\n{subtitle}\n{beta_tag}",
        title="🔒 Security Scanner",
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(Align.center(panel))
    ctx.exit()

@click.group()
@click.option('--version', is_flag=True, callback=print_version, 
              expose_value=False, is_eager=True, help='Show version and exit.')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output and detailed logging.')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all output except errors.')
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file.')
@click.option('--debug', is_flag=True, help='Enable debug mode with detailed internal information.')
@click.pass_context
def cli(ctx, verbose, quiet, config, debug):
    """
    Levox - Enterprise PII/GDPR Detection CLI
    
    Detect Personally Identifiable Information (PII) and ensure GDPR compliance
    in your codebase with our 7-stage detection architecture.
    
    Features:
    • Multi-language AST analysis with Tree-Sitter
    • Context-aware detection with 85%+ false positive reduction
    • Control Flow Graph (CFG) analysis for complex PII flows
    • Configurable file discovery and scanning
    • Professional reporting in JSON, HTML, and PDF formats
    • Enterprise-grade performance and scalability
    
    Detection Pipeline:
    • STAGE 1: Regex Detection (Basic)
    • STAGE 2: AST Analysis (Premium+)
    • STAGE 3: Context Analysis (Premium+)
    • STAGE 4: Dataflow Analysis (Enterprise)
    • STAGE 5: CFG Analysis (Premium+)
    • STAGE 6: ML Filtering (Enterprise)
    • STAGE 7: GDPR Compliance (Premium+)
    
    Quick Start:
    • Scan current directory: levox scan
    • Scan with CFG analysis: levox scan --cfg
    • Scan specific path: levox scan /path/to/code
    • Generate reports: levox scan --report json html
    • Show capabilities: levox status
    • Get help: levox <command> --help
    """
    
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Set up configuration
    try:
        if config:
            config_obj = Config.from_file(config)
        else:
            config_obj = load_default_config()
        
        # Override config with CLI flags
        if verbose:
            config_obj.log_level = "DEBUG"
        if quiet:
            config_obj.log_level = "ERROR"
        if debug:
            config_obj.debug_mode = True
            
        # Initialize services
        initialize_services(config_obj)
        
        # Store config in context
        ctx.obj['config'] = config_obj
        
    except Exception as e:
        click.echo(f"Configuration error: {e}", err=True)
        ctx.exit(1)

@cli.command()
@click.argument('path', type=click.Path(exists=False, file_okay=True, dir_okay=True), default='.')
@click.option('--format', 'output_format', type=click.Choice(['summary', 'table', 'json', 'sarif']),
              default='summary', help='Output format for terminal display')
@click.option('--output', '-o', type=click.Path(), help='Output file for results (JSON format)')
@click.option('--max-file-size-mb', type=int, help='Maximum file size to scan in MB')
@click.option('--exclude-patterns', multiple=True, help='File patterns to exclude (glob patterns)')
@click.option('--scan-optional/--no-scan-optional', is_flag=True, default=False, 
              help='Include optional file types (.txt, .md) in addition to source code')
@click.option('--allow-fallback-parsing', is_flag=True, default=True, 
              help='Allow fallback parsing when Tree-Sitter unavailable')
@click.option('--require-full-ast', is_flag=True, 
              help='Require full AST parsing (fail if Tree-Sitter unavailable)')
@click.option('--cfg', '--deep-scan', is_flag=True, 
              help='Enable Control Flow Graph (CFG) analysis for complex PII detection')
@click.option('--cfg-confidence', type=float, default=0.6, 
              help='Minimum confidence threshold to trigger CFG analysis (default: 0.6)')
@click.option('--report', 'report_formats', type=click.Choice(['json', 'html', 'pdf']), multiple=True, 
              help='Generate reports in specific formats (only when explicitly requested)')
@click.option('--verbosity', type=click.Choice(['summary', 'verbose', 'debug']), default='summary',
              help='Output verbosity level')
@click.option('--telemetry', is_flag=True, help='Show detailed capability and performance information')
@click.option('--secret-verify/--no-secret-verify', is_flag=True, default=True,
              help='Validate detected secrets with provider APIs (e.g., AWS STS)')
@click.pass_context
def scan(ctx, path, output_format, output, max_file_size_mb, 
         exclude_patterns, scan_optional, allow_fallback_parsing, require_full_ast, 
         cfg, cfg_confidence, report_formats, verbosity, telemetry, secret_verify):
    """
    Scan files/directories for PII violations and GDPR compliance issues.
    
    This command performs a comprehensive security scan using our 7-stage detection
    pipeline including regex patterns, AST analysis, context analysis, dataflow analysis,
    CFG analysis, ML filtering, and GDPR compliance checking.
    
    CFG Analysis (--cfg) provides deep scanning for complex PII flows through control
    structures that previous stages may miss. Requires Premium+ license tier.
    
    Reports are only generated when explicitly requested with --report flags.
    """
    
    if not scan_service:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        # Validate and normalize path
        scan_path = Path(path).resolve()
        if not scan_path.exists():
            click.echo(f"Error: Path does not exist: {scan_path}", err=True)
            ctx.exit(1)
        
        # Prepare scan options
        scan_options = {
            'output_format': output_format,
            'output_file': output,
            'max_file_size_mb': max_file_size_mb,
            'exclude_patterns': list(exclude_patterns) if exclude_patterns else None,
            'scan_optional': scan_optional,
            'allow_fallback_parsing': allow_fallback_parsing,
            'require_full_ast': require_full_ast,
            'cfg_enabled': cfg,
            'cfg_confidence': cfg_confidence,
            'report_formats': list(report_formats) if report_formats else None,
            'verbosity': verbosity,
            'telemetry': telemetry,
            'secret_verify': secret_verify,
            'scan_path': str(scan_path)  # Add scan path for result saving
        }
        
        # Execute scan
        exit_code = scan_service.execute_scan(str(scan_path), scan_options)

        # Provide clear exit messaging before exiting
        try:
            if exit_code == EXIT_SUCCESS:
                click.echo("Completed successfully (exit code 0).")
            elif exit_code == EXIT_VIOLATIONS_FOUND:
                click.echo("Violations found (exit code 1).")
            elif exit_code == EXIT_CONFIG_ERROR:
                click.echo("Configuration error (exit code 3).")
            elif exit_code == EXIT_RUNTIME_ERROR:
                click.echo("Runtime error (exit code 2).")
            else:
                click.echo(f"Exited with code {exit_code}.")
        finally:
            ctx.exit(exit_code)
        
    except SystemExit:
        # Re-raise SystemExit to allow Click to handle it properly
        raise
    except Exception:
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)

@cli.command()
@click.argument('results_file', type=click.Path(exists=True), required=False)
@click.option('--format', 'output_format', type=click.Choice(['json', 'html', 'pdf', 'sarif']),
              default='json', help='Report format')
@click.option('--output', '-o', type=click.Path(), help='Output file for report')
@click.option('--template', type=click.Path(exists=True), help='Custom report template file')
@click.option('--include-metadata', is_flag=True, help='Include detailed metadata in report')
@click.option('--latest', is_flag=True, help='Generate report from latest scan results')
@click.option('--list', 'list_results', is_flag=True, help='List available scan results for reporting')
@click.pass_context
def report(ctx, results_file, output_format, output, template, include_metadata, latest, list_results):
    """
    Generate detailed reports from previous scan results.
    
    This command creates professional reports in various formats from saved scan results.
    Reports are only generated when this command is explicitly run.
    
    Examples:
        report --list                           # List available scan results
        report --latest --format html          # Generate HTML report from latest scan
        report results.json --format pdf       # Generate PDF report from specific file
        report results.json --format html -o report.html  # Save HTML report to file
    """
    
    if not report_service:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        # Handle list command
        if list_results:
            exit_code = report_service.list_available_results()
            ctx.exit(exit_code)
        
        # Handle latest report generation
        if latest:
            report_options = {
                'output_format': output_format,
                'output_file': output,
                'template': template,
                'include_metadata': include_metadata
            }
            exit_code = report_service.generate_latest_report(report_options)
            # Provide clear exit messaging
            try:
                if exit_code == EXIT_SUCCESS:
                    click.echo("Report completed successfully (exit code 0).")
                elif exit_code == EXIT_CONFIG_ERROR:
                    click.echo("Report configuration error (exit code 3).")
                elif exit_code == EXIT_RUNTIME_ERROR:
                    click.echo("Report runtime error (exit code 2).")
                else:
                    click.echo(f"Report exited with code {exit_code}.")
            finally:
                ctx.exit(exit_code)
        
        # Handle specific file report generation
        if not results_file:
            click.echo("Error: Must specify a results file or use --latest/--list", err=True)
            click.echo("Use 'report --help' for usage information", err=True)
            ctx.exit(1)
        
        report_options = {
            'output_format': output_format,
            'output_file': output,
            'template': template,
            'include_metadata': include_metadata
        }
        
        exit_code = report_service.generate_report(results_file, report_options)
        # Provide clear exit messaging
        try:
            if exit_code == EXIT_SUCCESS:
                click.echo("Report completed successfully (exit code 0).")
            elif exit_code == EXIT_CONFIG_ERROR:
                click.echo("Report configuration error (exit code 3).")
            elif exit_code == EXIT_RUNTIME_ERROR:
                click.echo("Report runtime error (exit code 2).")
            else:
                click.echo(f"Report exited with code {exit_code}.")
        finally:
            ctx.exit(exit_code)
        
    except SystemExit:
        # Re-raise SystemExit to allow Click to handle it properly
        raise
    except Exception:
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)

@cli.command()
@click.option('--detailed', is_flag=True, help='Show detailed capability information')
@click.option('--check-dependencies', is_flag=True, help='Verify all dependencies are available')
@click.pass_context
def status(ctx, detailed, check_dependencies):
    """
    Show system status, capabilities, scan analytics, and dependency information.
    
    This command displays the current system status, available detection methods,
    real scan analytics, and validates that all required dependencies are properly installed.
    """
    
    try:
        # Get actual license tier from license client if available
        try:
            from ..core.license_client import get_license_client
            
            # Try to get the actual license tier from the license client
            client = get_license_client()
            license_info = client.get_license_info()
            
            if license_info and license_info.is_valid:
                actual_tier = license_info.tier.value
                license_tier = actual_tier
                click.echo(f"License validated: {actual_tier} tier")
            else:
                click.echo("No valid license found, using standard tier")
                license_tier = 'standard'
        except Exception as e:
            click.echo(f"License validation failed: {e}, using standard tier")
            license_tier = 'standard'
        
        # Get scan analytics from scan service
        scan_analytics = _get_scan_analytics(ctx)
        
        # Display scan analytics
        if scan_analytics:
            click.echo("\n📊 Scan Analytics:")
            click.echo("=" * 50)
            click.echo(f"📁 Total Scans: {scan_analytics['total_scans']}")
            click.echo(f"📄 Files Scanned: {scan_analytics['total_files_scanned']}")
            click.echo(f"🔍 Total Matches: {scan_analytics['total_matches']}")
            click.echo(f"📂 Directories Scanned: {scan_analytics['total_directories']}")
            click.echo(f"⏱️  Total Scan Time: {scan_analytics['total_scan_time']:.2f}s")
            click.echo(f"📈 Average Files/sec: {scan_analytics['avg_files_per_second']:.1f}")
            
            if scan_analytics['last_scan']:
                last_scan = scan_analytics['last_scan']
                click.echo(f"\n🕒 Last Scan: {last_scan['timestamp']}")
                click.echo(f"📁 Path: {last_scan['scan_path']}")
                click.echo(f"📄 Files: {last_scan['files_scanned']}")
                click.echo(f"🔍 Matches: {last_scan['matches_found']}")
                click.echo(f"⏱️  Duration: {last_scan['scan_time']:.2f}s")
        
        # Display system capabilities with dynamic feature checking
        click.echo("\n🔧 System Capabilities:")
        click.echo("=" * 50)
        
        # Dynamic feature checking
        feature_status = _check_feature_availability()
        
        # Tree-Sitter status
        tree_sitter_status = "✅ Available" if feature_status['tree_sitter'] else "❌ Not Available"
        click.echo(f"Tree-Sitter Parser: {tree_sitter_status}")
        
        # Language support
        lang_count = feature_status['supported_languages']
        if lang_count > 0:
            click.echo(f"Language Support: ✅ {lang_count} Languages")
        else:
            click.echo("Language Support: ❌ Not Available")
        
        # ML Libraries
        ml_status = "✅ Available" if feature_status['ml_libraries'] else "❌ Not Available"
        click.echo(f"ML Libraries: {ml_status}")
        
        # License tier
        click.echo(f"License Tier: 🔓 {license_tier.title()}")
        
        # Show dynamic feature availability (aligned with plan gating)
        click.echo("\n🚀 Feature Availability:")
        click.echo("=" * 50)
        
        # Check each feature dynamically
        features_to_check = [
            ("AST Analysis", "ast_analysis", feature_status['ast_analysis']),
            ("Context Analysis", "context_analysis", True),
            ("CFG Analysis", "cfg_analysis", feature_status['cfg_analysis']),
            ("Advanced Reporting", "advanced_reporting", True),
            ("Custom Rules", "custom_rules", True),
            ("Dataflow Analysis", "dataflow_analysis", feature_status['dataflow_analysis']),
            ("ML Filtering", "ml_filtering", feature_status['ml_libraries']),
            ("API Integration", "api_integration", True),
            ("Enterprise Logging", "enterprise_logging", True),
            ("GDPR Compliance", "gdpr_compliance", True),
            ("Compliance Reporting", "compliance_reporting", True),
        ]
        
        def _has_feature(tier: str, key: str) -> bool:
            tier = tier.lower()
            starter = {"regex_detection", "basic_logging", "file_scanning", "basic_reporting"}
            pro = starter | {"ast_analysis", "context_analysis", "cfg_analysis", "advanced_reporting", "custom_rules", "multi_language", "performance_metrics"}
            ent = pro | {"ml_filtering", "dataflow_analysis", "api_integration", "enterprise_logging", "compliance_audit", "gdpr_analysis", "compliance_reporting", "crypto_verification", "custom_integrations"}
            feature_sets = {"starter": starter, "pro": pro, "enterprise": ent}
            return key in feature_sets.get(tier, set())

        for feature_name, feature_key, is_available in features_to_check:
            if _has_feature(license_tier, feature_key):
                if is_available:
                    click.echo(f"✅ {feature_name}: Available")
                else:
                    click.echo(f"⚠️  {feature_name}: Dependency missing")
                    if feature_key == 'ml_filtering':
                        click.echo("   💡 Install: pip install xgboost scikit-learn")
                    elif feature_key == 'ast_analysis':
                        click.echo("   💡 Install: pip install tree-sitter")
            else:
                required = 'Pro+' if feature_key in {"ast_analysis", "context_analysis", "cfg_analysis", "advanced_reporting", "custom_rules"} else 'Enterprise'
                click.echo(f"🔒 {feature_name}: Requires {required} License")
        
        # Show detailed information if requested
        if detailed:
            click.echo("\n📊 Detailed Information:")
            click.echo("=" * 30)
            click.echo(f"Python Version: {feature_status['python_version']}")
            click.echo(f"Platform: {feature_status['platform']}")
            click.echo(f"Memory Usage: {feature_status['memory_usage']:.1f} MB")
            
            if scan_analytics and scan_analytics['performance_stats']:
                perf = scan_analytics['performance_stats']
                click.echo(f"Average Scan Duration: {perf.get('avg_scan_duration', 0):.2f}s")
                click.echo(f"Peak Memory Usage: {perf.get('peak_memory_mb', 0):.1f} MB")
        
        click.echo("\n💡 For complete feature details, visit: https://levox.aifenrix.com/plans")
        return 0
        
    except Exception as e:
        click.echo(f"Status check failed: {e}", err=True)
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        return 1

@cli.command()
@click.argument('match_id')
@click.argument('verdict', type=click.Choice(['true_positive', 'false_positive', 'uncertain']))
@click.option('--notes', help='Optional notes about the feedback')
@click.option('--confidence', type=click.FloatRange(0.0, 1.0), help='Confidence in your verdict (0.0-1.0)')
@click.pass_context
def feedback(ctx, match_id, verdict, notes, confidence):
    """
    Submit feedback for a detection match to improve accuracy.
    
    This command allows you to provide feedback on detection results, which helps
    improve the ML models and reduce false positives in future scans.
    """
    
    if not scan_service:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        feedback_data = {
            'match_id': match_id,
            'verdict': verdict,
            'notes': notes,
            'confidence': confidence
        }
        
        exit_code = scan_service.submit_feedback(feedback_data)
        ctx.exit(exit_code)
        
    except SystemExit:
        # Re-raise SystemExit to allow Click to handle it properly
        raise
    except Exception as e:
        click.echo(f"Feedback submission failed: {e}", err=True)
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)

@cli.command()
@click.option('--validate', is_flag=True, help='Force license validation with server')
@click.option('--refresh', is_flag=True, help='Refresh license cache and re-validate')
@click.option('--clear-cache', is_flag=True, help='Clear license cache')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed license information')
@click.option('--register', 'license_key', metavar='<KEY>', help='Register a license key')
@click.option('--upgrade', is_flag=True, help='Open license upgrade page in web browser')
@click.option('--server-url', default='https://levox.aifenrix.com', help='License server URL')
@click.pass_context
def license(ctx, validate, refresh, clear_cache, verbose, license_key, upgrade, server_url):
    """
    Manage and validate Levox license.
    
    This command allows you to check your current license status,
    validate it with the license server, manage license cache,
    and access license registration/upgrade options.
    """
    
    try:
        from ..core.license_client import get_license_client
        
        client = get_license_client()
        
        # Handle license registration
        if license_key is not None:
            if not license_key.strip():
                # Handle --register without a value
                click.echo("❌ Error: License key is required for registration")
                click.echo("")
                click.echo("📝 Usage: levox license --register <your-license-key>")
                click.echo("")
                click.echo("🔗 To get a license key:")
                click.echo("   1. Visit: https://levox.aifenrix.com/plans")
                click.echo("   2. Choose your plan and complete registration")
                click.echo("   3. Copy your license key and use it with --register")
                click.echo("")
                click.echo("💡 Example: levox license --register abc123-def456-ghi789")
                ctx.exit(1)
            try:
                click.echo(f"🔑 Registering license key: {license_key}")
                
                # Verify the license with the server
                license_info = client.verify_license(license_key)
                
                if license_info.is_valid:
                    click.echo("✅ License registered successfully!")
                    click.echo(f"📧 Email: {license_info.email}")
                    click.echo(f"🎯 Tier: {license_info.tier.value.title()}")
                    click.echo(f"📅 Expires: {license_info.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    click.echo(f"🔢 Device Limit: {license_info.device_limit}")
                    click.echo(f"🌐 Current Devices: {license_info.current_devices}")
                    click.echo("\n🎉 Your license is now active! You can use all available features.")
                else:
                    click.echo("❌ License registration failed: License is not valid")
                    ctx.exit(1)
                    
            except Exception as e:
                click.echo(f"❌ License registration failed: {e}")
                click.echo("💡 Please check your license key and try again")
                ctx.exit(1)
        
        # Handle upgrade request
        if upgrade:
            try:
                import webbrowser
                upgrade_url = f"{server_url.rstrip('/')}/upgrade"
                click.echo(f"🌐 Opening license upgrade page: {upgrade_url}")
                webbrowser.open(upgrade_url)
                click.echo("✅ Upgrade page opened in your default browser")
                return
            except Exception as e:
                click.echo(f"❌ Failed to open browser: {e}")
                click.echo(f"💻 Please manually visit: {server_url.rstrip('/')}/upgrade")
                return
        
        if clear_cache:
            client.clear_cache()
            click.echo("✅ License cache cleared")
            return
        
        if refresh:
            # Clear cache first, then get fresh info
            client.clear_cache()
            click.echo("🔄 Refreshing license validation...")
        
        # Get license information
        license_info = client.get_license_info()
        
        if not license_info:
            click.echo("❌ No license information available")
            ctx.exit(1)
        
        # Display license information
        click.echo("\n🔑 License Information:")
        click.echo("=" * 50)
        
        click.echo(f"License Key: {license_info.license_key}")
        click.echo(f"Tier: {license_info.tier.value.title()}")
        click.echo(f"Email: {license_info.email}")
        click.echo(f"Valid: {'✅ Yes' if license_info.is_valid else '❌ No'}")
        click.echo(f"Expires: {license_info.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"Device Limit: {license_info.device_limit}")
        click.echo(f"Current Devices: {license_info.current_devices}")
        
        if verbose:
            click.echo(f"\n📋 Additional Details:")
            click.echo(f"JWT Token: {license_info.jwt_token[:50]}..." if license_info.jwt_token else "None")
            click.echo(f"Device Fingerprint: {client.device_fingerprint}")
        
        # Show validation status
        if license_info.is_valid:
            click.echo(f"\n✅ License is valid and active!")
            click.echo(f"🎯 Available features: {license_info.tier.value.title()} tier")
        else:
            click.echo(f"\n⚠️  License is not valid or expired")
            click.echo(f"🔒 Running in demo mode with limited features")
        
        # Show server connection status (use a GET health endpoint that returns 200)
        try:
            health = client._make_request("license", "GET")
            if isinstance(health, dict):
                click.echo(f"\n🌐 Server Connection: ✅ Connected to license server")
            else:
                click.echo(f"\n🌐 Server Connection: ❌ Unexpected response from server")
        except Exception as e:
            click.echo(f"\n🌐 Server Connection: ❌ Connection failed: {e}")
        
        ctx.exit(0)
        
    except SystemExit as e:
        # Treat normal exits as success; propagate non-zero codes
        if e.code not in (0, None):
            raise
        return
    except Exception as e:
        click.echo(f"❌ License check failed: {e}", err=True)
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)

@cli.command()
@click.option('--list', 'list_models', is_flag=True, help='List available ML models')
@click.option('--evaluate', type=click.Path(exists=True), help='Evaluate model performance on test data')
@click.option('--train', type=click.Path(exists=True), help='Train new model on labeled data')
@click.option('--export', type=click.Path(), help='Export current model to file')
@click.pass_context
def models(ctx, list_models, evaluate, train, export):
    """
    Manage and evaluate ML models used for detection.
    
    This command provides tools for managing the machine learning models that
    help reduce false positives and improve detection accuracy.
    """
    
    if not scan_service:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        model_options = {
            'list_models': list_models,
            'evaluate': evaluate,
            'train': train,
            'export': export
        }
        
        exit_code = scan_service.manage_models(model_options)
        ctx.exit(exit_code)
        
    except SystemExit:
        # Re-raise SystemExit to allow Click to handle it properly
        raise
    except Exception as e:
        click.echo(f"Model management failed: {e}", err=True)
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)

@cli.command()
@click.option('--format', type=click.Choice(['table', 'json', 'markdown']), default='table', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def help(ctx, format, output, verbose):
    """
    Show comprehensive help with all available commands and options.
    
    This command provides a complete overview of all Levox CLI commands,
    their usage, and available options for different verbosity levels.
    """
    try:
        help_data = {
            "cli_overview": {
                "description": "Levox - Enterprise PII/GDPR Detection CLI",
                "version": "0.9.0 Beta",
                "main_commands": ["scan", "status", "report", "feedback", "models", "help", "history", "ml_health", "generate_report", "switch_model"]
            },
            "all_commands": {
                "scan": {
                    "description": "Scan files/directories for PII violations and GDPR compliance issues",
                    "usage": "levox scan <path> [options]",
                    "key_options": [
                        "--format", "--output", "--verbose", "--debug", "--telemetry",
                        "--max-file-size-mb", "--exclude-patterns", "--scan-optional", "--allow-fallback-parsing",
                        "--require-full-ast", "--cfg", "--cfg-confidence", "--report", "--no-report", "--dev", "--verbosity"
                    ]
                },
                "status": {
                    "description": "Show system status, capabilities, and dependency information",
                    "usage": "levox status [options]",
                    "key_options": ["--detailed", "--check-dependencies"]
                },
                "report": {
                    "description": "Generate detailed reports from previous scan results",
                    "usage": "levox report [file] [options]",
                    "key_options": [
                        "--format", "--output", "--template", "--include-metadata", "--latest", "--list"
                    ]
                },
                "feedback": {
                    "description": "Submit feedback for detection matches to improve accuracy",
                    "usage": "levox feedback <match_id> <verdict> [options]",
                    "key_options": ["--notes", "--confidence"]
                },
                "feedback_stats": {
                    "description": "Show feedback statistics",
                    "usage": "levox feedback stats [options]",
                    "key_options": ["--days"]
                },
                "feedback_export": {
                    "description": "Export feedback data to JSONL format",
                    "usage": "levox feedback export <output_path> [options]",
                    "key_options": ["--limit"]
                },
                "models": {
                    "description": "Manage and evaluate ML models used for detection",
                    "usage": "levox models [options]",
                    "key_options": ["--list", "--evaluate", "--train", "--export", "--format", "--output", "--verbose"]
                },
                "history": {
                    "description": "Show scan history and available results for reporting",
                    "usage": "levox history [options]",
                    "key_options": ["--detailed", "--limit"]
                },
                "ml_health": {
                    "description": "Check ML system health and performance",
                    "usage": "levox ml_health [options]",
                    "key_options": ["--format", "--output", "--verbose"]
                },
                "switch_model": {
                    "description": "Switch to a different ML model",
                    "usage": "levox switch_model [options]",
                    "key_options": ["--model-id", "--auto", "--verbose"]
                },
                "generate_report": {
                    "description": "Generate reports from the last scan results",
                    "usage": "levox generate_report [options]",
                    "key_options": ["--format", "--output-dir", "--from-last-scan"]
                },
                "help": {
                    "description": "Show comprehensive help with all available commands and options",
                    "usage": "levox help [options]",
                    "key_options": ["--format", "--output", "--verbose"]
                }
            },
            "global_options": {
                "description": "Global options that apply to all commands",
                "options": [
                    "--version", "--verbose, -v", "--quiet, -q", "--config, -c", "--debug"
                ]
            },
            "toggle_flags": {
                "description": "Boolean toggle flags for controlling behavior",
                "scan_toggles": [
                    "--scan-optional/--no-scan-optional", "--allow-fallback-parsing", "--require-full-ast",
                    "--cfg, --deep-scan", "--telemetry", "--no-report", "--dev"
                ],
                "report_toggles": [
                    "--include-metadata", "--latest", "--list", "--from-last-scan"
                ],
                "output_toggles": [
                    "--detailed", "--check-dependencies", "--verbose"
                ],
                "ml_toggles": [
                    "--auto", "--list", "--evaluate", "--train", "--export"
                ]
            },
            "configuration_toggles": {
                "description": "Configuration-based toggles (set in config files)",
                "detection_toggles": [
                    "enable_ast", "enable_dataflow", "enable_ml", "enable_context_analysis",
                    "enable_compliance_audit", "enable_context_aware_filtering",
                    "enable_safe_literal_detection", "enable_variable_heuristics",
                    "enable_placeholder_detection", "enable_ml_monitoring"
                ],
                "performance_toggles": [
                    "enable_async", "cache_ast_parses", "enable_compression"
                ],
                "compliance_toggles": [
                    "include_security_checks", "include_dsar_checks", "include_deletion_checks",
                    "include_transfer_checks", "include_consent_checks", "include_retention_checks",
                    "enable_crypto_verification"
                ],
                "reporting_toggles": [
                    "enable_dashboards", "enable_trends", "enable_export"
                ]
            },
            "quick_examples": {
                "basic_scan": "levox scan /path/to/code",
                "verbose_scan": "levox scan /path/to/code --verbosity verbose",
                "debug_scan": "levox scan /path/to/code --verbosity debug",
                "generate_reports": "levox scan /path/to/code --report json --report html",
                "developer_mode": "levox scan /path/to/code --dev",
                "save_results": "levox scan /path/to/code --output results.json",
                "check_status": "levox status --detailed",
                "view_history": "levox history --detailed --limit 20",
                "cfg_analysis": "levox scan /path --cfg --cfg-confidence 0.7",
                "ml_health_check": "levox ml_health --verbose",
                "switch_best_model": "levox switch_model --auto",
                "feedback_stats": "levox feedback stats --days 30"
            }
        }
        
        if format == 'json':
            output_content = json.dumps(help_data, indent=2, default=str)
        elif format == 'markdown':
            output_content = _generate_markdown_help(help_data)
        else:
            # Default table format
            _display_help_table(help_data, verbose)
            return
        
        # Handle output
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_content)
            click.echo(f"Help documentation saved to {output}")
        else:
            click.echo(output_content)
            
    except Exception as e:
        click.echo(f"❌ Error generating help: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()


def _display_help_table(help_data, verbose):
    """Display help information in a formatted table."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    
    # CLI Overview
    overview = help_data["cli_overview"]
    console.print(Panel(
        f"[bold blue]{overview['description']}[/bold blue]\n"
        f"[dim]Version: {overview['version']}[/dim]\n"
        f"[cyan]Available Commands: {len(overview['main_commands'])}[/cyan]",
        title="🚀 Levox CLI Overview",
        border_style="blue"
    ))
    
    # Global Options
    if "global_options" in help_data:
        console.print("\n[bold green]🌐 Global Options[/bold green]")
        global_panel = Panel(
            "\n".join([f"• {opt}" for opt in help_data["global_options"]["options"]]),
            title="🔧 Global Options (apply to all commands)",
            border_style="blue"
        )
        console.print(global_panel)
    
    # All Available Commands
    console.print("\n[bold green]📋 All Available Commands[/bold green]")
    commands_table = Table(show_header=True, header_style="bold magenta")
    commands_table.add_column("Command", style="cyan", width=15)
    commands_table.add_column("Description", style="white", width=50)
    commands_table.add_column("Usage", style="yellow", width=30)
    commands_table.add_column("Key Options", style="green", width=25)
    
    for cmd_name, cmd_info in help_data["all_commands"].items():
        # Show first 3 options, then indicate there are more
        options_display = ", ".join(cmd_info["key_options"][:3])
        if len(cmd_info["key_options"]) > 3:
            options_display += f" (+{len(cmd_info['key_options']) - 3} more)"
        
        commands_table.add_row(
            cmd_name,
            cmd_info["description"][:47] + "..." if len(cmd_info["description"]) > 50 else cmd_info["description"],
            cmd_info["usage"],
            options_display
        )
    
    console.print(commands_table)
    
    # Quick Examples
    console.print("\n[bold green]💡 Quick Examples[/bold green]")
    examples_table = Table(show_header=True, header_style="bold magenta")
    examples_table.add_column("Use Case", style="cyan")
    examples_table.add_column("Command", style="yellow")
    
    for use_case, command in help_data["quick_examples"].items():
        examples_table.add_row(use_case.replace("_", " ").title(), command)
    
    console.print(examples_table)
    
    # Footer
    console.print("\n[dim]💡 Tip: Use 'levox <command> --help' for detailed help on specific commands[/dim]")
    console.print("[dim]📚 For more information, visit the project documentation[/dim]")


def _generate_markdown_help(help_data):
    """Generate markdown format help documentation."""
    md_content = []
    
    # Header
    md_content.append(f"# {help_data['cli_overview']['description']}")
    md_content.append(f"**Version:** {help_data['cli_overview']['version']}")
    md_content.append("")
    
    # Global Options
    if "global_options" in help_data:
        md_content.append("## Global Options")
        md_content.append("")
        md_content.append("These options apply to all commands:")
        for option in help_data["global_options"]["options"]:
            md_content.append(f"- `{option}`")
        md_content.append("")
    
    # All Available Commands
    md_content.append("## All Available Commands")
    md_content.append("")
    
    for cmd_name, cmd_info in help_data["all_commands"].items():
        md_content.append(f"### {cmd_name}")
        md_content.append(f"**Description:** {cmd_info['description']}")
        md_content.append(f"**Usage:** `{cmd_info['usage']}`")
        md_content.append("**Key Options:**")
        for option in cmd_info["key_options"]:
            md_content.append(f"- `{option}`")
        md_content.append("")
    
    # Quick Examples
    md_content.append("## Quick Examples")
    md_content.append("")
    
    for use_case, command in help_data["quick_examples"].items():
        md_content.append(f"**{use_case.replace('_', ' ').title()}:**")
        md_content.append(f"```bash")
        md_content.append(command)
        md_content.append("")
    
    return "\n".join(md_content)


@cli.command()
@click.option('--detailed', is_flag=True, help='Show detailed scan information')
@click.option('--limit', type=int, default=10, help='Maximum number of scans to show')
@click.option('--clear', 'clear_all', is_flag=True, help='Clear all scan history and results')
@click.option('--clear-id', type=str, help='Clear specific scan result by ID (filename without extension)')
@click.option('--select', type=str, help='Select and show details for specific scan result by ID')
@click.option('--export', type=click.Path(), help='Export scan history to JSON file')
@click.pass_context
def history(ctx, detailed, limit, clear_all, clear_id, select, export):
    """
    Show scan history and available results for reporting.
    
    This command displays a list of recent scans and their results,
    making it easy to identify which scans to generate reports from.
    
    Additional features:
    • Clear all history: history --clear
    • Clear specific result: history --clear-id <scan_id>
    • Select specific result: history --select <scan_id>
    • Export history: history --export history.json
    """
    
    if not scan_service:
        click.echo("Error: Services not initialized", err=True)
        ctx.exit(1)
    
    try:
        # Handle clear all history
        if clear_all:
            if click.confirm("Are you sure you want to clear ALL scan history and results?"):
                cleared_count = scan_service.clear_all_scan_history()
                click.echo(f"✅ Cleared {cleared_count} scan results and history")
            else:
                click.echo("Operation cancelled")
            ctx.exit(0)
        
        # Handle clear specific result
        if clear_id:
            if scan_service.clear_specific_scan_result(clear_id):
                click.echo(f"✅ Cleared scan result: {clear_id}")
            else:
                click.echo(f"❌ Scan result not found: {clear_id}")
            ctx.exit(0)
        
        # Handle select specific result
        if select:
            result_details = scan_service.get_specific_scan_result(select)
            if result_details:
                click.echo(f"📋 Details for scan: {select}")
                click.echo("=" * 80)
                click.echo(f"📁 File: {result_details['file_path']}")
                click.echo(f"📁 Scan Path: {result_details['scan_path']}")
                click.echo(f"🚨 Issues: {result_details['total_issues']}")
                click.echo(f"🔓 License: {result_details['license_tier']}")
                click.echo(f"📅 Timestamp: {result_details['timestamp']}")
                click.echo()
                click.echo("💡 To generate a report from this scan:")
                click.echo(f"   report {result_details['file_path']} --format html")
            else:
                click.echo(f"❌ Scan result not found: {select}")
            ctx.exit(0)
        
        # Handle export history
        if export:
            exported_count = scan_service.export_scan_history(export)
            click.echo(f"✅ Exported {exported_count} scan results to: {export}")
            ctx.exit(0)
        
        # Get scan history
        scan_history = scan_service.get_scan_history()
        available_results = scan_service.list_available_scan_results()
        
        if not scan_history and not available_results:
            click.echo("No scan history found. Run a scan first to generate results.")
            ctx.exit(0)
        
        # Display scan history
        if scan_history:
            click.echo(f"📊 Recent Scans (Last {min(limit, len(scan_history))}):")
            click.echo("=" * 80)
            
            for i, scan in enumerate(scan_history[-limit:], 1):
                scan_time = scan.get('scan_time', 0)
                total_issues = scan.get('total_issues', 0)
                timestamp = scan.get('timestamp', 'Unknown')[:19] if scan.get('timestamp') != 'Unknown' else 'Unknown'
                
                click.echo(f"{i:2d}. {Path(scan['scan_path']).name}")
                click.echo(f"    📁 Path: {scan['scan_path']}")
                click.echo(f"    ⏱️  Time: {scan_time:.2f}s")
                click.echo(f"    🚨 Issues: {total_issues}")
                click.echo(f"    🔓 License: {scan.get('license_tier', 'Unknown')}")
                click.echo(f"    📅 {timestamp}")
                if scan.get('results_file'):
                    click.echo(f"    💾 Results: {Path(scan['results_file']).name}")
                click.echo()
        else:
            click.echo("📊 Recent Scans: No recent scans in memory")
            click.echo("(This is normal for existing installations - scan history will be populated with new scans)")
            click.echo()
        
        # Display available results
        if available_results:
            click.echo(f"📋 Available Results for Reporting (Last {min(limit, len(available_results))}):")
            click.echo("=" * 80)
            
            for i, result in enumerate(available_results[:limit], 1):
                timestamp = result.get('timestamp', 'Unknown')[:19] if result.get('timestamp') != 'Unknown' else 'Unknown'
                scan_id = Path(result['file_path']).stem  # Get filename without extension
                
                click.echo(f"{i:2d}. {Path(result['file_path']).name}")
                click.echo(f"    🆔 ID: {scan_id}")
                click.echo(f"    📁 Scan: {Path(result['scan_path']).name}")
                click.echo(f"    🚨 Issues: {result['total_issues']}")
                click.echo(f"    🔓 License: {result['license_tier']}")
                click.echo(f"    📅 {timestamp}")
                click.echo()
        else:
            click.echo("📋 Available Results: No scan results found")
            click.echo("Run a scan first to generate results for reporting")
            click.echo()
        
        # Show usage examples
        click.echo("💡 Usage Examples:")
        click.echo("  • report --list                    # List all available results")
        click.echo("  • report --latest --format html    # Generate HTML report from latest scan")
        click.echo("  • history --select <scan_id>       # Show details for specific scan")
        click.echo("  • history --clear-id <scan_id>     # Clear specific scan result")
        click.echo("  • history --clear                  # Clear all scan history")
        click.echo("  • history --export history.json    # Export scan history")
        if available_results:
            latest_file = available_results[0]['file_path']
            click.echo(f"  • report {latest_file} --format pdf  # Generate PDF from specific file")
        
    except Exception as e:
        click.echo(f"Failed to show scan history: {e}", err=True)
        if ctx.obj.get('config', {}).get('debug_mode'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)
    
    # Exit successfully
    ctx.exit(0)


@cli.command()
@click.option('--format', '-f', type=click.Choice(['json', 'html', 'pdf', 'table', 'markdown']), 
              default='html', help='Report format (default: html)')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--latest', is_flag=True, help='Generate report from latest scan')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def generate_report(format, output, latest, verbose):
    """
    Generate a report from the most recent scan results.
    
    This command creates a formatted report from the latest scan results.
    """
    try:
        # Initialize services
        config = load_default_config()
        initialize_services(config)
        
        if not report_service:
            click.echo("❌ Report service not available")
            return EXIT_RUNTIME_ERROR
        
        # Get the latest scan results
        results_dir = Path.home() / ".levox" / "scan_results"
        if not results_dir.exists():
            click.echo("❌ No scan results found. Run a scan first.")
            return EXIT_RUNTIME_ERROR
        
        # Find the latest scan result file
        result_files = list(results_dir.glob("levox_scan_*.json"))
        if not result_files:
            click.echo("❌ No scan results found. Run a scan first.")
            return EXIT_RUNTIME_ERROR
        
        # Sort by modification time and get the latest
        latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
        
        if verbose:
            click.echo(f"📁 Using scan results: {latest_file.name}")
        
        # Generate the report
        report_options = {
            'format': format,
            'output': output,
            'verbose': verbose
        }
        
        exit_code = report_service.generate_report(str(latest_file), report_options)
        
        if exit_code == EXIT_SUCCESS:
            click.echo(f"✅ Report generated successfully in {format.upper()} format")
            if output:
                click.echo(f"📄 Saved to: {output}")
        else:
            click.echo("⚠️ Report generation completed with warnings")
        
        return exit_code
        
    except Exception as e:
        click.echo(f"❌ Error generating report: {e}")
        return EXIT_RUNTIME_ERROR


@cli.command()
def set_report_directory():
    """Choose where reports are saved using Windows Explorer."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        import os
        
        # Hide the main tkinter window
        root = tk.Tk()
        root.withdraw()
        
        # Open folder picker dialog
        folder_path = filedialog.askdirectory(
            title="Choose Directory for Levox Reports",
            initialdir=os.path.expanduser("~")
        )
        
        if folder_path:
            # Save the selected directory to configuration
            config_path = os.path.expanduser("~/.levox/config.yaml")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Load existing config or create new
            config = {}
            if os.path.exists(config_path):
                try:
                    import yaml
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f) or {}
                except:
                    pass
            
            # Update report directory
            config['report_directory'] = folder_path
            
            # Save updated config
            try:
                import yaml
                with open(config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                
                click.echo(f"✅ Report directory set to: {folder_path}")
                click.echo(f"📁 Reports will now be saved to: {folder_path}")
                click.echo(f"💾 Configuration saved to: {config_path}")
                
            except Exception as e:
                click.echo(f"❌ Failed to save configuration: {e}")
                click.echo(f"📁 Selected directory: {folder_path}")
                click.echo("💡 You can manually set this in your config file")
        else:
            click.echo("❌ No directory selected. Report directory unchanged.")
            
    except ImportError:
        click.echo("❌ tkinter not available. Please install tkinter or manually set report directory in config.")
    except Exception as e:
        click.echo(f"❌ Error setting report directory: {e}")


def _get_scan_analytics(ctx) -> Optional[Dict[str, Any]]:
    """Get scan analytics from the scan service."""
    try:
        # Try to get scan service from context
        scan_service = ctx.obj.get('scan_service')
        if not scan_service:
            return None
        
        # Get scan history
        scan_history = scan_service.get_scan_history()
        if not scan_history:
            return None
        
        # Calculate analytics
        total_scans = len(scan_history)
        total_files_scanned = sum(scan.get('files_scanned', 0) for scan in scan_history)
        total_matches = sum(scan.get('matches_found', 0) for scan in scan_history)
        total_scan_time = sum(scan.get('scan_time', 0) for scan in scan_history)
        
        # Count unique directories
        unique_dirs = set(scan.get('scan_path', '') for scan in scan_history)
        total_directories = len(unique_dirs)
        
        # Calculate average files per second
        avg_files_per_second = total_files_scanned / total_scan_time if total_scan_time > 0 else 0
        
        # Get last scan
        last_scan = scan_history[-1] if scan_history else None
        
        # Get performance stats from engine if available
        performance_stats = {}
        try:
            if hasattr(scan_service, 'engine') and scan_service.engine:
                perf_stats = scan_service.engine.get_performance_stats()
                performance_stats = {
                    'avg_scan_duration': perf_stats.get('avg_scan_duration', 0),
                    'peak_memory_mb': perf_stats.get('peak_memory_mb', 0)
                }
        except:
            pass
        
        return {
            'total_scans': total_scans,
            'total_files_scanned': total_files_scanned,
            'total_matches': total_matches,
            'total_directories': total_directories,
            'total_scan_time': total_scan_time,
            'avg_files_per_second': avg_files_per_second,
            'last_scan': last_scan,
            'performance_stats': performance_stats
        }
        
    except Exception:
        return None


def _check_feature_availability() -> Dict[str, Any]:
    """Check the availability of various features and dependencies."""
    feature_status = {
        'tree_sitter': False,
        'supported_languages': 0,
        'ml_libraries': False,
        'ast_analysis': False,
        'cfg_analysis': False,
        'dataflow_analysis': False,
        'ml_filtering': False,
        'gdpr_compliance': False,
        'context_analysis': False,
        'advanced_reporting': False,
        'custom_patterns': False,
        'api_integration': False,
        'enterprise_logging': False,
        'python_version': 'Unknown',
        'platform': 'Unknown',
        'memory_usage': 0.0
    }
    
    try:
        import sys
        import platform
        import psutil
        
        # Basic system info
        feature_status['python_version'] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        feature_status['platform'] = platform.system()
        feature_status['memory_usage'] = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Check Tree-Sitter
        try:
            from ..detection.regex_engine import TREE_SITTER_AVAILABLE
            feature_status['tree_sitter'] = TREE_SITTER_AVAILABLE
        except:
            pass
        
        # Check supported languages
        try:
            from ..utils.file_handler import get_supported_languages
            support_info = get_supported_languages()
            feature_status['supported_languages'] = len(support_info.get('languages', []))
        except:
            pass
        
        # Check ML libraries
        try:
            import xgboost
            import sklearn
            feature_status['ml_libraries'] = True
        except ImportError:
            pass
        
        # Check AST analysis
        try:
            import tree_sitter
            feature_status['ast_analysis'] = True
        except ImportError:
            pass
        
        # Check CFG analysis (depends on AST)
        feature_status['cfg_analysis'] = feature_status['ast_analysis']
        
        # Check dataflow analysis (depends on AST)
        feature_status['dataflow_analysis'] = feature_status['ast_analysis']
        
        # Check ML filtering
        feature_status['ml_filtering'] = feature_status['ml_libraries']
        
        # Check GDPR compliance (always available if license allows)
        feature_status['gdpr_compliance'] = True
        
        # Check context analysis (always available)
        feature_status['context_analysis'] = True
        
        # Check advanced reporting (always available)
        feature_status['advanced_reporting'] = True
        
        # Check custom patterns (always available)
        feature_status['custom_patterns'] = True
        
        # Check API integration (always available)
        feature_status['api_integration'] = True
        
        # Check enterprise logging (always available)
        feature_status['enterprise_logging'] = True
        
    except Exception:
        pass
    
    return feature_status


if __name__ == '__main__':
    cli()
