"""
Levox Service Layer

This module provides the business logic services that are called by the CLI commands.
It separates concerns between command handling and business operations.
"""

import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..core.config import Config
from ..core.engine import DetectionEngine
from ..core.exceptions import LevoxException, DetectionError, ConfigurationError
from ..core.feedback import FeedbackCollector
from ..models.detection_result import DetectionResult
from ..utils.performance import PerformanceMonitor
from ..parsers import get_supported_languages, TREE_SITTER_AVAILABLE
from .output import OutputManager
from ..utils.secret_validation import enrich_detection_with_secret_validation

# Exit codes
EXIT_SUCCESS = 0
EXIT_VIOLATIONS_FOUND = 1
EXIT_RUNTIME_ERROR = 2
EXIT_CONFIG_ERROR = 3

class ScanService:
    """Service for handling scan operations."""
    
    def __init__(self, config: Config, output_manager: OutputManager):
        """Initialize the scan service."""
        self.config = config
        self.output_manager = output_manager
        self.engine = DetectionEngine(config)
        self.feedback_collector = FeedbackCollector(config)
        self.last_scan_results: Optional[DetectionResult] = None
        self.last_scan_path: Optional[str] = None
        self.last_scan_time: Optional[float] = None
        self.scan_history: List[Dict[str, Any]] = []
        self.scan_results_dir = self._get_scan_results_directory()
    
    def _get_scan_results_directory(self) -> Path:
        """Get the directory for storing scan results."""
        if hasattr(self.config, 'scan_results_directory') and self.config.scan_results_directory:
            results_dir = Path(self.config.scan_results_directory)
        else:
            # Default to user's home directory
            results_dir = Path.home() / ".levox" / "scan_results"
        
        # Create directory if it doesn't exist
        results_dir.mkdir(parents=True, exist_ok=True)
        return results_dir
    
    def execute_scan(self, scan_path: str, scan_options: Dict[str, Any]) -> int:
        """Execute a security scan with the given options."""
        try:
            # Configure output manager
            self.output_manager.set_verbosity(scan_options.get('verbosity', 'summary'))
            self.output_manager.set_telemetry(scan_options.get('telemetry', False))
            
            # Show branding for non-interactive scans
            if not self._is_interactive_mode():
                self.output_manager.print_branding()
            
            # Validate scan path
            scan_path_obj = Path(scan_path).resolve()
            if not scan_path_obj.exists():
                self.output_manager.print_error(f"Scan path does not exist: {scan_path}")
                return EXIT_CONFIG_ERROR
            
            # Prepare engine configuration
            engine_config = self._prepare_engine_config(scan_options)
            
            # Execute scan
            start_time = time.time()
            results = self._perform_scan(scan_path_obj, engine_config)
            scan_time = time.time() - start_time
            
            # Store scan results for potential reporting
            self.last_scan_results = results
            self.last_scan_path = scan_path
            self.last_scan_time = scan_time
            
            # Save scan results to file for later reporting
            scan_results_file = self._save_scan_results(results, scan_time, scan_options)
            
            # Add to scan history
            self._add_to_scan_history(scan_path, scan_results_file, scan_time, results, scan_options)
            
            # Handle output file if specified
            if scan_options.get('output_file'):
                self._save_results_to_file(results, scan_options['output_file'])
            
            # Generate reports if requested (explicitly)
            report_formats = scan_options.get('report_formats', [])
            if report_formats:
                self._generate_reports(results, scan_time, scan_options['license_tier'], report_formats)
            
            # Display results
            self._display_scan_results(results, scan_options, scan_time)
            
            # Show scan results file location for later reporting
            if scan_results_file:
                self.output_manager.print_info(f"Scan results saved to: {scan_results_file}")
                self.output_manager.print_info(f"Use 'report {scan_results_file} --format <format>' to generate reports")
            
            # Determine exit code
            total_matches = sum(len(file_result.matches) for file_result in results.file_results)
            return EXIT_VIOLATIONS_FOUND if total_matches > 0 else EXIT_SUCCESS
            
        except DetectionError as e:
            self.output_manager.print_error(f"Detection error: {e}")
            return EXIT_RUNTIME_ERROR
        except ConfigurationError as e:
            self.output_manager.print_error(f"Configuration error: {e}")
            return EXIT_CONFIG_ERROR
        except Exception as e:
            self.output_manager.print_error(f"Unexpected error during scan: {e}")
            if self.config.debug_mode:
                import traceback
                self.output_manager.print_error("Traceback:", traceback.format_exc())
            return EXIT_RUNTIME_ERROR
    
    def submit_feedback(self, feedback_data: Dict[str, Any]) -> int:
        """Submit feedback for a detection match."""
        try:
            feedback_id = self.feedback_collector.submit_feedback(
                match_id=feedback_data['match_id'],
                verdict=feedback_data['verdict'],
                notes=feedback_data.get('notes'),
                confidence=feedback_data.get('confidence')
            )
            
            self.output_manager.print_success(f"Feedback submitted successfully: {feedback_id}")
            return EXIT_SUCCESS
            
        except Exception as e:
            self.output_manager.print_error(f"Failed to submit feedback: {e}")
            return EXIT_RUNTIME_ERROR
    
    def manage_models(self, model_options: Dict[str, Any]) -> int:
        """Manage ML models used for detection."""
        try:
            if model_options.get('list_models'):
                self._list_available_models()
            elif model_options.get('evaluate'):
                self._evaluate_model(model_options['evaluate'])
            elif model_options.get('train'):
                self._train_model(model_options['train'])
            elif model_options.get('export'):
                self._export_model(model_options['export'])
            else:
                self.output_manager.print_info("Use --help to see available model management options")
            
            return EXIT_SUCCESS
            
        except Exception as e:
            self.output_manager.print_error(f"Model management failed: {e}")
            return EXIT_RUNTIME_ERROR
    
    def _prepare_engine_config(self, scan_options: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare engine configuration from scan options."""
        config = {}
        
        # License tier
        config['license_tier'] = scan_options.get('license_tier', 'enterprise')
        
        # File handling options
        if scan_options.get('max_file_size_mb'):
            config['max_file_size_mb'] = scan_options['max_file_size_mb']
        
        if scan_options.get('exclude_patterns'):
            config['exclude_patterns'] = scan_options['exclude_patterns']
        
        if scan_options.get('scan_optional'):
            config['scan_optional'] = scan_options['scan_optional']
        
        # Parsing options
        if scan_options.get('allow_fallback_parsing') is not None:
            config['allow_fallback_parsing'] = scan_options['allow_fallback_parsing']
        
        if scan_options.get('require_full_ast'):
            config['require_full_ast'] = scan_options['require_full_ast']
        
        # CFG Analysis options
        if scan_options.get('cfg_enabled'):
            config['cfg_enabled'] = scan_options['cfg_enabled']
            # Also enable CFG analysis in the config
            self.config.cfg_analysis.enabled = True
        
        if scan_options.get('cfg_confidence'):
            config['cfg_confidence'] = scan_options['cfg_confidence']
            self.config.cfg_analysis.confidence_threshold = scan_options['cfg_confidence']
        
        return config
    
    def _perform_scan(self, scan_path: Path, engine_config: Dict[str, Any]) -> DetectionResult:
        """Perform the actual scan using the detection engine."""
        # Note: Engine configuration is handled during initialization
        # The engine_config options are stored for potential future use
        
        # Determine scan type and execute
        if scan_path.is_file():
            results = self.engine.scan_file(str(scan_path))
        elif scan_path.is_dir():
            results = self.engine.scan_directory(str(scan_path))
        else:
            raise DetectionError(f"Invalid scan path: {scan_path}")
        
        return results
    
    def _display_scan_results(self, results: DetectionResult, scan_options: Dict[str, Any], scan_time: float):
        """Display scan results using the output manager."""
        # Optional secret validation enrichment
        try:
            if scan_options.get('secret_verify') or getattr(self.config, 'enable_secret_validation', False):
                allow_network = getattr(self.config, 'secret_validation_allow_network', False)
                aws_enabled = getattr(self.config, 'secret_validation_aws_enabled', True)
                timeout_secs = getattr(self.config, 'secret_validation_timeout_seconds', 5)
                for fr in results.file_results:
                    for m in fr.matches:
                        enrichment = enrich_detection_with_secret_validation(
                            m,
                            allow_network=allow_network,
                            aws_enabled=aws_enabled,
                            timeout_seconds=timeout_secs,
                        )
                        if enrichment:
                            m.metadata['secret_validation_provider'] = enrichment.provider
                            m.metadata['secret_validation_status'] = enrichment.status
                            m.metadata['secret_validation_details'] = enrichment.details
                            # Severity bump for confirmed
                            if enrichment.status == 'confirmed_active' and m.severity in ['LOW', 'MEDIUM']:
                                m.severity = 'HIGH'
        except Exception:
            # Never break scans due to enrichment issues
            pass
        # Show scan summary
        self.output_manager.show_scan_summary(
            results, 
            scan_time, 
            scan_options.get('license_tier', 'enterprise'),
            scan_options.get('report_formats', [])
        )
        
        # Show top 10 issues by default
        self.output_manager.display_top_10_issues(results)
        
        # Show full results if requested
        output_format = scan_options.get('output_format', 'summary')
        if output_format != 'summary':
            self.output_manager.display_full_results(results, output_format)
        
        # Show telemetry if enabled
        if scan_options.get('telemetry'):
            self.output_manager.show_telemetry_info(results, scan_time)
    
    def _save_results_to_file(self, results: DetectionResult, output_file: str):
        """Save scan results to the specified output file."""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to JSON and save
            json_data = self.output_manager._convert_to_json(results)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            self.output_manager.print_success(f"Results saved to: {output_path}")
            
        except Exception as e:
            self.output_manager.print_warning(f"Failed to save results to {output_file}: {e}")
    
    def _generate_reports(self, results: DetectionResult, scan_time: float, 
                          license_tier: str, report_formats: List[str]):
        """Generate reports in the requested formats."""
        try:
            from .reporting import ReportGenerator
            report_gen = ReportGenerator(self.config, self.output_manager)
            
            for format_type in report_formats:
                report_path = report_gen.generate_report(
                    results, format_type, scan_time, license_tier
                )
                if report_path:
                    self.output_manager.print_success(f"Generated {format_type.upper()} report: {report_path}")
                    
        except Exception as e:
            self.output_manager.print_warning(f"Report generation failed: {e}")
    
    def _is_interactive_mode(self) -> bool:
        """Check if running in interactive mode."""
        # This is a simple heuristic - could be enhanced
        return hasattr(self, '_interactive_mode') and self._interactive_mode
    
    def _list_available_models(self):
        """List available ML models."""
        try:
            model_dir = Path(self.config.ml_model_path) if hasattr(self.config, 'ml_model_path') else None
            if model_dir and model_dir.exists():
                models = list(model_dir.glob("*.pkl"))
                if models:
                    self.output_manager.print_info(f"Found {len(models)} ML models:")
                    for model in models:
                        self.output_manager.console.print(f"  • {model.name}")
                else:
                    self.output_manager.print_info("No ML models found")
            else:
                self.output_manager.print_info("ML model directory not configured")
        except Exception as e:
            self.output_manager.print_warning(f"Could not list models: {e}")
    
    def _evaluate_model(self, test_data_path: str):
        """Evaluate model performance on test data."""
        self.output_manager.print_info(f"Model evaluation not yet implemented for: {test_data_path}")
    
    def _train_model(self, training_data_path: str):
        """Train a new model on labeled data."""
        self.output_manager.print_info(f"Model training not yet implemented for: {training_data_path}")
    
    def _export_model(self, export_path: str):
        """Export current model to file."""
        self.output_manager.print_info(f"Model export not yet implemented to: {export_path}")

    def _save_scan_results(self, results: DetectionResult, scan_time: float, scan_options: Dict[str, Any]) -> Optional[str]:
        """Save scan results to a file for later reporting."""
        try:
            # Generate filename with timestamp and path info
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scan_path = scan_options.get('scan_path', str(results.scan_path) if hasattr(results, 'scan_path') else 'unknown')
            scan_path_safe = Path(scan_path).name.replace(' ', '_').replace('\\', '_').replace('/', '_')
            filename = f"levox_scan_{scan_path_safe}_{timestamp}.json"
            results_path = self.scan_results_dir / filename
            
            # Prepare results data with metadata
            results_data = {
                'scan_metadata': {
                    'scan_path': scan_path,
                    'scan_time': scan_time,
                    'license_tier': scan_options.get('license_tier', 'enterprise'),
                    'scan_options': scan_options,
                    'timestamp': datetime.now().isoformat(),
                    'levox_version': '0.9.0'
                },
                'scan_results': self.output_manager._convert_to_json(results)
            }
            
            # Save to file
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            
            return str(results_path)
            
        except Exception as e:
            self.output_manager.print_warning(f"Failed to save scan results: {e}")
            return None
    
    def _add_to_scan_history(self, scan_path: str, results_file: Optional[str], scan_time: float, 
                            results: DetectionResult, scan_options: Dict[str, Any]):
        """Add scan to history for later reference."""
        total_matches = sum(len(file_result.matches) for file_result in results.file_results)
        
        scan_record = {
            'scan_path': scan_path,
            'results_file': results_file,
            'scan_time': scan_time,
            'total_files': len(results.file_results),
            'total_issues': total_matches,
            'license_tier': scan_options.get('license_tier', 'enterprise'),
            'timestamp': datetime.now().isoformat(),
            'scan_options': scan_options
        }
        
        self.scan_history.append(scan_record)
        
        # Keep only last 50 scans in memory
        if len(self.scan_history) > 50:
            self.scan_history = self.scan_history[-50:]
    
    def get_scan_history(self) -> List[Dict[str, Any]]:
        """Get scan history from memory."""
        return self.scan_history
    
    def list_available_scan_results(self) -> List[Dict[str, Any]]:
        """List available scan results from disk."""
        try:
            available_results = []
            if self.scan_results_dir.exists():
                for result_file in self.scan_results_dir.glob("levox_scan_*.json"):
                    try:
                        with open(result_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Extract metadata
                        scan_metadata = data.get('scan_metadata', {})
                        scan_results = data.get('scan_results', {})
                        
                        # Calculate total issues
                        total_issues = 0
                        if 'file_results' in scan_results:
                            for file_result in scan_results['file_results']:
                                total_issues += len(file_result.get('matches', []))
                        
                        available_results.append({
                            'file_path': str(result_file),
                            'scan_path': scan_metadata.get('scan_path', 'Unknown'),
                            'total_issues': total_issues,
                            'license_tier': scan_metadata.get('license_tier', 'Unknown'),
                            'timestamp': scan_metadata.get('timestamp', 'Unknown'),
                            'scan_time': scan_metadata.get('scan_time', 0)
                        })
                    except Exception as e:
                        self.output_manager.print_warning(f"Failed to read scan result {result_file}: {e}")
                        continue
            
            # Sort by timestamp (newest first)
            available_results.sort(key=lambda x: x['timestamp'], reverse=True)
            return available_results
            
        except Exception as e:
            self.output_manager.print_error(f"Failed to list scan results: {e}")
            return []
    
    def clear_all_scan_history(self) -> int:
        """Clear all scan history and results."""
        try:
            cleared_count = 0
            
            # Clear memory history
            self.scan_history.clear()
            
            # Clear disk results
            if self.scan_results_dir.exists():
                for result_file in self.scan_results_dir.glob("levox_scan_*.json"):
                    try:
                        result_file.unlink()
                        cleared_count += 1
                    except Exception as e:
                        self.output_manager.print_warning(f"Failed to delete {result_file}: {e}")
            
            return cleared_count
            
        except Exception as e:
            self.output_manager.print_error(f"Failed to clear scan history: {e}")
            return 0
    
    def clear_specific_scan_result(self, scan_id: str) -> bool:
        """Clear specific scan result by ID."""
        try:
            # Find the file with the given scan ID
            target_file = self.scan_results_dir / f"{scan_id}.json"
            
            if target_file.exists():
                target_file.unlink()
                
                # Also remove from memory history if present
                self.scan_history = [scan for scan in self.scan_history 
                                   if not scan.get('results_file', '').endswith(f"{scan_id}.json")]
                
                return True
            else:
                return False
                
        except Exception as e:
            self.output_manager.print_error(f"Failed to clear scan result {scan_id}: {e}")
            return False
    
    def get_specific_scan_result(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get details for specific scan result by ID."""
        try:
            # Find the file with the given scan ID
            target_file = self.scan_results_dir / f"{scan_id}.json"
            
            if target_file.exists():
                with open(target_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract metadata
                scan_metadata = data.get('scan_metadata', {})
                scan_results = data.get('scan_results', {})
                
                # Calculate total issues
                total_issues = 0
                if 'file_results' in scan_results:
                    for file_result in scan_results['file_results']:
                        total_issues += len(file_result.get('matches', []))
                
                return {
                    'file_path': str(target_file),
                    'scan_path': scan_metadata.get('scan_path', 'Unknown'),
                    'total_issues': total_issues,
                    'license_tier': scan_metadata.get('license_tier', 'Unknown'),
                    'timestamp': scan_metadata.get('timestamp', 'Unknown'),
                    'scan_time': scan_metadata.get('scan_time', 0)
                }
            else:
                return None
                
        except Exception as e:
            self.output_manager.print_error(f"Failed to get scan result {scan_id}: {e}")
            return None
    
    def export_scan_history(self, export_path: str) -> int:
        """Export scan history to JSON file."""
        try:
            available_results = self.list_available_scan_results()
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_results': len(available_results),
                'scan_results': available_results
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return len(available_results)
            
        except Exception as e:
            self.output_manager.print_error(f"Failed to export scan history: {e}")
            return 0


class ReportService:
    """Service for handling report generation operations."""
    
    def __init__(self, config: Config, output_manager: OutputManager):
        """Initialize the report service."""
        self.config = config
        self.output_manager = output_manager
        self.scan_results_dir = self._get_scan_results_directory()
    
    def _get_scan_results_directory(self) -> Path:
        """Get the directory for storing scan results."""
        if hasattr(self.config, 'scan_results_directory') and self.config.scan_results_directory:
            results_dir = Path(self.config.scan_results_directory)
        else:
            # Default to user's home directory
            results_dir = Path.home() / ".levox" / "scan_results"
        
        # Create directory if it doesn't exist
        results_dir.mkdir(parents=True, exist_ok=True)
        return results_dir
    
    def generate_report(self, results_file: str, report_options: Dict[str, Any]) -> int:
        """Generate a report from saved scan results."""
        try:
            # Load results from file
            results_data = self._load_scan_results(results_file)
            if not results_data:
                return EXIT_CONFIG_ERROR
            
            # Extract results and metadata
            scan_results = results_data.get('scan_results', {})
            scan_metadata = results_data.get('scan_metadata', {})
            
            # Generate report in requested format
            output_format = report_options.get('output_format', 'json')
            output_file = report_options.get('output_file')
            template = report_options.get('template')
            include_metadata = report_options.get('include_metadata', False)
            
            # Import report generator
            from .reporting import ReportGenerator
            report_gen = ReportGenerator(self.config, self.output_manager)
            
            # Generate report - pass the entire results_data to include metadata
            report_path = report_gen.generate_report_from_file(
                results_data, output_format, output_file, template, include_metadata
            )
            
            if report_path:
                self.output_manager.print_success(f"✅ Report generated successfully!")
                self.output_manager.print_info(f"📄 Saved to: {report_path}")
                self.output_manager.print_info(f"🌐 Open in browser: {Path(report_path).absolute()}")
                
                # Show report metadata
                if include_metadata:
                    self._show_report_metadata(scan_metadata)
            else:
                self.output_manager.print_error("❌ Report generation failed")
            
            return EXIT_SUCCESS
            
        except FileNotFoundError:
            self.output_manager.print_error(f"Results file not found: {results_file}")
            return EXIT_CONFIG_ERROR
        except Exception as e:
            self.output_manager.print_error(f"Report generation failed: {e}")
            return EXIT_RUNTIME_ERROR
    
    def _load_scan_results(self, results_file: str) -> Optional[Dict[str, Any]]:
        """Load scan results from file."""
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.output_manager.print_error(f"Failed to load scan results: {e}")
            return None
    
    def _show_report_metadata(self, metadata: Dict[str, Any]):
        """Show metadata about the scan that generated the report."""
        from rich.table import Table
        from rich import box
        
        table = Table(
            title="📋 Scan Metadata",
            show_header=True,
            header_style="bold blue",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1)
        )
        
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="white", width=40)
        
        table.add_row("Scan Path", metadata.get('scan_path', 'Unknown'))
        table.add_row("Scan Time", f"{metadata.get('scan_time', 0):.2f}s")
        table.add_row("License Tier", metadata.get('license_tier', 'Unknown'))
        table.add_row("Timestamp", metadata.get('timestamp', 'Unknown'))
        
        self.output_manager.console.print(table)
    
    def list_available_results(self) -> int:
        """List all available scan result files for reporting."""
        try:
            available_results = self._get_available_scan_results()
            
            if not available_results:
                self.output_manager.print_info("No scan results found. Run a scan first to generate results.")
                return EXIT_SUCCESS
            
            # Display available results
            from rich.table import Table
            from rich import box
            
            table = Table(
                title="📊 Available Scan Results for Reporting",
                show_header=True,
                header_style="bold blue",
                border_style="blue",
                box=box.ROUNDED,
                padding=(0, 1)
            )
            
            table.add_column("#", justify="center", width=5)
            table.add_column("File", style="cyan", width=30)
            table.add_column("Scan Path", style="white", width=30)
            table.add_column("Issues", justify="center", width=10)
            table.add_column("License", justify="center", width=12)
            table.add_column("Timestamp", style="yellow", width=20)
            
            for i, result in enumerate(available_results, 1):
                timestamp = result['timestamp'][:19] if result['timestamp'] != 'Unknown' else 'Unknown'
                table.add_row(
                    str(i),
                    Path(result['file_path']).name,
                    Path(result['scan_path']).name if result['scan_path'] != 'Unknown' else 'Unknown',
                    str(result['total_issues']),
                    result['license_tier'],
                    timestamp
                )
            
            self.output_manager.console.print(table)
            self.output_manager.print_info(f"\nUse 'report <file_path> --format <format>' to generate reports")
            self.output_manager.print_info(f"Example: report {available_results[0]['file_path']} --format html")
            
            return EXIT_SUCCESS
            
        except Exception as e:
            self.output_manager.print_error(f"Failed to list scan results: {e}")
            return EXIT_RUNTIME_ERROR
    
    def _get_available_scan_results(self) -> List[Dict[str, Any]]:
        """Get list of available scan result files."""
        available_results = []
        
        # Check scan results directory
        for results_file in self.scan_results_dir.glob("levox_scan_*.json"):
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    available_results.append({
                        'file_path': str(results_file),
                        'scan_path': data.get('scan_metadata', {}).get('scan_path', 'Unknown'),
                        'timestamp': data.get('scan_metadata', {}).get('timestamp', 'Unknown'),
                        'total_issues': data.get('scan_results', {}).get('total_issues_found', 0),
                        'license_tier': data.get('scan_metadata', {}).get('license_tier', 'Unknown')
                    })
            except Exception:
                # Skip corrupted files
                continue
        
        # Sort by timestamp (newest first)
        available_results.sort(key=lambda x: x['timestamp'], reverse=True)
        return available_results
    
    def generate_latest_report(self, report_options: Dict[str, Any]) -> int:
        """Generate a report from the latest scan results."""
        try:
            available_results = self._get_available_scan_results()
            
            if not available_results:
                self.output_manager.print_error("No scan results found. Run a scan first to generate results.")
                return EXIT_CONFIG_ERROR
            
            latest_file = available_results[0]['file_path']
            self.output_manager.print_info(f"Generating report from latest scan: {Path(latest_file).name}")
            
            return self.generate_report(latest_file, report_options)
            
        except Exception as e:
            self.output_manager.print_error(f"Failed to generate latest report: {e}")
            return EXIT_RUNTIME_ERROR


class StatusService:
    """Service for handling status and capability checks."""
    
    def __init__(self, config: Config, output_manager: OutputManager):
        """Initialize the status service."""
        self.config = config
        self.output_manager = output_manager
    
    def show_status(self, status_options: Dict[str, Any]) -> int:
        """Show system status and capabilities."""
        try:
            # Show branding
            self.output_manager.print_branding()
            
            # Get capabilities
            capabilities = self._validate_dependencies()
            
            # Get actual license tier from license client if available
            try:
                from ..core.license_client import get_license_client
                
                # Try to get the actual license tier from the license client
                client = get_license_client()
                license_info = client.get_license_info()
                
                if license_info and license_info.is_valid:
                    actual_tier = license_info.tier.value
                    license_tier = actual_tier
                else:
                    # Fallback to options or default
                    license_tier = status_options.get('license_tier', 'standard')
            except Exception:
                # Fallback to options or default if license client not available
                license_tier = status_options.get('license_tier', 'standard')
            
            detailed = status_options.get('detailed', False)
            check_dependencies = status_options.get('check_dependencies', False)
            
            # Debug: Print license tier
            print(f"DEBUG: License tier being passed to display: {license_tier}")
            
            # Display capability status
            self._display_capability_status(capabilities, license_tier, detailed)
            
            # Check dependencies if requested
            if check_dependencies:
                self._check_dependency_status(capabilities)
            
            return EXIT_SUCCESS
            
        except Exception as e:
            self.output_manager.print_error(f"Status check failed: {e}")
            return EXIT_RUNTIME_ERROR
    
    def _validate_dependencies(self) -> Dict[str, Any]:
        """Validate required dependencies and return capability status."""
        support_info = get_supported_languages()
        capabilities = {
            'tree_sitter_available': TREE_SITTER_AVAILABLE,
            'languages': list(support_info['languages'].keys()),
            'language_details': support_info['languages'],
            'ml_libraries': self._check_ml_libraries(),
            'optional_libraries': self._check_optional_libraries()
        }
        
        return capabilities
    
    def _check_ml_libraries(self) -> Dict[str, bool]:
        """Check ML library availability."""
        ml_status = {}
        
        try:
            import xgboost
            ml_status['xgboost'] = True
        except ImportError:
            ml_status['xgboost'] = False
        
        try:
            import sklearn
            ml_status['scikit_learn'] = True
        except ImportError:
            ml_status['scikit_learn'] = False
        
        return ml_status
    
    def _check_optional_libraries(self) -> Dict[str, bool]:
        """Check optional library availability."""
        optional_status = {}
        
        try:
            import watchdog
            optional_status['watchdog'] = True
        except ImportError:
            optional_status['watchdog'] = False
        
        try:
            import sqlite3
            optional_status['sqlite3'] = True
        except ImportError:
            optional_status['sqlite3'] = False
        
        return optional_status
    
    def _display_capability_status(self, capabilities: Dict[str, Any], license_tier: str, detailed: bool):
        """Display capability status with beautiful formatting."""
        from rich.table import Table
        from rich import box
        
        # Main capabilities table
        table = Table(
            title="🔧 System Capabilities",
            show_header=True,
            header_style="bold blue",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1)
        )
        
        table.add_column("Component", style="cyan", width=25)
        table.add_column("Status", justify="center", width=15)
        table.add_column("Details", style="white", width=40)
        
        # Tree-Sitter status
        tree_sitter_status = "✅ Available" if capabilities['tree_sitter_available'] else "❌ Not Available"
        tree_sitter_details = "Full AST parsing support" if capabilities['tree_sitter_available'] else "Limited parsing capabilities"
        table.add_row("Tree-Sitter Parser", tree_sitter_status, tree_sitter_details)
        
        # Language support
        supported_langs = len(capabilities['languages'])
        lang_status = f"✅ {supported_langs} Languages"
        lang_details = ", ".join(capabilities['languages'][:3]) + ("..." if supported_langs > 3 else "")
        table.add_row("Language Support", lang_status, lang_details)
        
        # ML libraries
        ml_available = sum(capabilities['ml_libraries'].values())
        ml_total = len(capabilities['ml_libraries'])
        ml_status = f"✅ {ml_available}/{ml_total} Available"
        ml_details = "ML-based false positive reduction"
        table.add_row("Machine Learning", ml_status, ml_details)
        
        # License tier
        license_status = f"🔓 {license_tier.title()}"
        license_details = self._get_license_features(license_tier)
        table.add_row("License Tier", license_status, license_details)
        
        self.output_manager.console.print(table)
        self.output_manager.console.print()
        
        # Show detailed information if requested
        if detailed:
            self._show_detailed_capabilities(capabilities)
    
    def _get_license_features(self, license_tier: str) -> str:
        """Get feature description for license tier."""
        features = {
            'standard': 'Basic detection patterns',
            'premium': 'Advanced patterns + ML filtering',
            'enterprise': 'Full feature set + custom rules'
        }
        return features.get(license_tier, 'Unknown tier')
    
    def _show_detailed_capabilities(self, capabilities: Dict[str, Any]):
        """Show detailed capability information."""
        from rich.table import Table
        from rich import box
        
        # ML libraries detail
        ml_table = Table(
            title="🤖 ML Library Status",
            show_header=True,
            header_style="bold magenta",
            border_style="magenta",
            box=box.ROUNDED,
            padding=(0, 1)
        )
        
        ml_table.add_column("Library", style="cyan")
        ml_table.add_column("Status", justify="center")
        ml_table.add_column("Version", justify="center")
        
        for lib_name, available in capabilities['ml_libraries'].items():
            if available:
                try:
                    # SECURITY: Validate library name before importing
                    import re
                    import importlib
                    
                    # Only allow alphanumeric characters, underscores, and dots
                    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', lib_name):
                        raise ImportError(f"Invalid library name: {lib_name}")
                    
                    # Check against whitelist of allowed libraries
                    allowed_libs = {
                        'numpy', 'pandas', 'sklearn', 'scipy', 'matplotlib', 'seaborn',
                        'requests', 'urllib3', 'json', 'yaml', 'csv', 'xml', 're',
                        'datetime', 'time', 'os', 'sys', 'pathlib', 'collections',
                        'itertools', 'functools', 'operator', 'math', 'statistics'
                    }
                    
                    # Extract base module name (before first dot)
                    base_lib = lib_name.split('.')[0]
                    if base_lib not in allowed_libs:
                        raise ImportError(f"Library not in allowed list: {base_lib}")
                    
                    lib = importlib.import_module(lib_name)
                    version = getattr(lib, '__version__', 'Unknown')
                    ml_table.add_row(lib_name.title(), "✅ Available", version)
                except Exception:
                    ml_table.add_row(lib_name.title(), "✅ Available", "Unknown")
            else:
                ml_table.add_row(lib_name.title(), "❌ Not Available", "N/A")
        
        self.output_manager.console.print(ml_table)
        self.output_manager.console.print()
        
        # Optional libraries detail
        opt_table = Table(
            title="🔧 Optional Libraries",
            show_header=True,
            header_style="bold yellow",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(0, 1)
        )
        
        opt_table.add_column("Library", style="cyan")
        opt_table.add_column("Status", justify="center")
        opt_table.add_column("Purpose", style="white")
        
        purposes = {
            'watchdog': 'File system monitoring',
            'sqlite3': 'Local data storage'
        }
        
        for lib_name, available in capabilities['optional_libraries'].items():
            status = "✅ Available" if available else "❌ Not Available"
            purpose = purposes.get(lib_name, 'Additional functionality')
            opt_table.add_row(lib_name.title(), status, purpose)
        
        self.output_manager.console.print(opt_table)
        self.output_manager.console.print()
    
    def _check_dependency_status(self, capabilities: Dict[str, Any]):
        """Check and display dependency status."""
        from rich.panel import Panel
        
        # Check critical dependencies
        critical_issues = []
        
        if not capabilities['tree_sitter_available']:
            critical_issues.append("Tree-Sitter not available - AST parsing limited")
        
        ml_available = sum(capabilities['ml_libraries'].values())
        if ml_available == 0:
            critical_issues.append("No ML libraries available - false positive reduction disabled")
        
        # Display status
        if critical_issues:
            issues_text = "\n".join(f"• {issue}" for issue in critical_issues)
            warning_panel = Panel(
                f"[yellow]⚠️  Critical Dependencies Missing:[/yellow]\n\n{issues_text}",
                title="Dependency Check",
                border_style="yellow",
                padding=(1, 2)
            )
            self.output_manager.console.print(warning_panel)
        else:
            success_panel = Panel(
                "[green]✅ All critical dependencies are available[/green]",
                title="Dependency Check",
                border_style="green",
                padding=(1, 2)
            )
            self.output_manager.console.print(success_panel)
        
        self.output_manager.console.print()
