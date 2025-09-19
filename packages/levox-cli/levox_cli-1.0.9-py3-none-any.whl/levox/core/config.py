"""
Configuration management for Levox application with hot-reload support.
"""

import os
import json
import yaml
import time
import threading
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging 


from pydantic import BaseModel, Field, validator
from .exceptions import ConfigurationError
from .security import get_security_config, SecurityConfig

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class LicenseTier(str, Enum):
    """License tiers with associated features."""
    STARTER = "starter"  # Renamed from FREE to something cooler
    PRO = "pro"
    ENTERPRISE = "enterprise"

    @classmethod
    def _missing_(cls, value):
        """Allow constructing from uppercase names or mixed-case values.
        E.g., LicenseTier('STANDARD') or LicenseTier('Standard') -> LicenseTier.STANDARD
        """
        try:
            if isinstance(value, str):
                # Try by name (uppercase)
                name = value.upper()
                if name in cls.__members__:
                    return cls.__members__[name]
                # Try by lowercase value
                lowered = value.lower()
                for member in cls:
                    if member.value == lowered:
                        return member
        except Exception:
            pass
        return None

    @classmethod
    def _from_string(cls, value: str) -> Optional['LicenseTier']:
        """Create LicenseTier from string value."""
        try:
            if value:
                lowered = value.lower()
                for member in cls:
                    if member.value == lowered:
                        return member
        except Exception:
            pass
        # Return STARTER as default instead of None
        return cls.STARTER


class RiskLevel(str, Enum):
    """Risk levels for detected PII."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DetectionPattern:
    """Configuration for a detection pattern."""
    name: str
    regex: str
    confidence: float = 0.8
    risk_level: RiskLevel = RiskLevel.MEDIUM
    description: str = ""
    enabled: bool = True
    languages: List[str] = field(default_factory=list)


@dataclass
class PerformanceConfig:
    """Performance configuration settings."""
    max_file_size_mb: int = 100
    max_scan_time_seconds: int = 300
    memory_limit_mb: int = 500
    concurrent_workers: int = 4
    incremental_scan_timeout: int = 10
    full_scan_timeout: int = 30


class CFGConfig(BaseModel):
    """Control Flow Graph analysis configuration."""
    enabled: bool = Field(default=False, description="Enable CFG analysis")
    confidence_threshold: float = Field(default=0.6, description="Minimum confidence to trigger CFG analysis")
    max_file_size_bytes: int = Field(default=51200, description="Skip files larger than 50KB")
    max_cfg_nodes: int = Field(default=1000, description="Skip functions with more than 1000 estimated nodes")
    max_analysis_time_seconds: int = Field(default=30, description="Timeout per function analysis")
    supported_languages: List[str] = Field(default_factory=lambda: ["python", "javascript"], 
                                         description="Languages supported for CFG analysis")
    cache_ast_parses: bool = Field(default=True, description="Use AST parsing cache for performance")
    
    @validator('confidence_threshold')
    def validate_confidence_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('confidence_threshold must be between 0.0 and 1.0')
        return v
    
    @validator('max_file_size_bytes')
    def validate_max_file_size(cls, v):
        if v <= 0:
            raise ValueError('max_file_size_bytes must be positive')
        return v
    
    @validator('max_cfg_nodes')
    def validate_max_cfg_nodes(cls, v):
        if v <= 0:
            raise ValueError('max_cfg_nodes must be positive')
        return v
    
    @validator('max_analysis_time_seconds')
    def validate_max_analysis_time(cls, v):
        if v <= 0:
            raise ValueError('max_analysis_time_seconds must be positive')
        return v


class LicenseConfig(BaseModel):
    """License configuration with feature gates."""
    tier: LicenseTier = LicenseTier.STARTER
    license_key: Optional[str] = None
    expiry_date: Optional[str] = None
    
    @property
    def features(self) -> Dict[str, bool]:
        """Get available features based on license tier."""
        base_features = {
            "regex_detection": True,
            "basic_logging": True,
            "file_scanning": True,
        }
        
        if self.tier == LicenseTier.STARTER:
            # Starter: basic features only (match website Starter)
            base_features.update({
                "basic_reporting": True
            })
        
        if self.tier == LicenseTier.PRO:
            # Pro: AST, Context, CFG, Advanced Reporting, Custom Rules
            base_features.update({
                "ast_analysis": True,
                "context_analysis": True,
                "cfg_analysis": True,
                "advanced_reporting": True,
                "custom_rules": True,
                "multi_language": True,
                "performance_metrics": True
            })
        
        
        if self.tier == LicenseTier.ENTERPRISE:
            # Enterprise: Full 7-stage pipeline and admin/enterprise features
            base_features.update({
                "ast_analysis": True,
                "context_analysis": True,
                "cfg_analysis": True,
                "advanced_reporting": True,
                "custom_rules": True,
                "multi_language": True,
                "performance_metrics": True,
                "ml_filtering": True,
                "dataflow_analysis": True,
                "api_integration": True,
                "enterprise_logging": True,
                "compliance_audit": True,
                "gdpr_analysis": True,
                "compliance_reporting": True,
                "audit_logging": True,
                "crypto_verification": True,
                "custom_integrations": True
            })
        
        return base_features


class Config(BaseModel):
    """Main configuration class for Levox."""
    
    # Core settings
    license: LicenseConfig = Field(default_factory=LicenseConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    
    # Security settings
    security: SecurityConfig = Field(default_factory=get_security_config)
    
    # CFG Analysis configuration
    cfg_analysis: CFGConfig = Field(default_factory=CFGConfig)
    
    # Detection patterns
    patterns: List[DetectionPattern] = Field(default_factory=list)
    
    # File handling
    include_patterns: List[str] = Field(default_factory=lambda: [
        "*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c",
        # Include common config/data and env/log files by default
        "*.json", 
        ".env", ".env.*", "*.env",
        "*.log", "*.log.*"
    ])
    exclude_patterns: List[str] = Field(default_factory=lambda: ["*.git/*", "*.venv/*", "node_modules/*", "__pycache__/*"])
    exclude_dirs: List[str] = Field(default_factory=lambda: [".git", ".venv", "node_modules", "__pycache__"])
    
    # Enhanced file discovery settings
    scan_optional: bool = Field(default=False, description="Scan optional file types (.txt, .md) in addition to default scannable files")
    
    # Output settings
    output_format: str = "json"
    output_file: Optional[str] = None
    # Preferred directory for saving generated reports (set via UI command)
    report_directory: Optional[str] = None
    verbose: bool = False
    quiet: bool = False
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "json"
    debug_mode: bool = False
    
    # ML settings
    ml_enabled: bool = False
    ml_model_path: Optional[str] = None
    confidence_threshold: float = 0.7

    # Secret validation settings
    enable_secret_validation: bool = True
    secret_validation_timeout_seconds: int = 5
    secret_validation_aws_enabled: bool = True
    secret_validation_allow_network: bool = False
    
    # Feature flags
    enable_ast: bool = False
    enable_dataflow: bool = False
    enable_ml: bool = False
    enable_context_analysis: bool = True
    
    # Compliance settings
    enable_compliance_audit: bool = False
    gdpr_check_level: str = "standard"  # basic, standard, strict
    audit_log_retention_days: int = 90
    
    # False Positive Reduction settings
    enable_context_aware_filtering: bool = True
    enable_safe_literal_detection: bool = True
    enable_variable_heuristics: bool = True
    enable_placeholder_detection: bool = True
    confidence_threshold: float = 0.7
    safe_literals: List[str] = Field(default_factory=lambda: [
        "localhost", "127.0.0.1", "0.0.0.0", "::1",
        "dummy", "test", "example", "sample", "placeholder",
        "use_environment_variable_instead", "config_value_here",
        "your_api_key_here", "your_secret_here", "your_password_here",
        "admin@localhost", "test@example.com", "user@test.com",
        "000-00-0000", "111-11-1111", "999-99-9999",
        "4111-1111-1111-1111", "5555-5555-5555-4444"
    ])
    safe_variable_patterns: List[str] = Field(default_factory=lambda: [
        "*_id", "*_type", "*_config", "*_setting", "*_option",
        "*_param", "*_property", "*_attribute", "*_flag", "*_status"
    ])
    test_file_indicators: List[str] = Field(default_factory=lambda: [
        "test_", "_test", "spec_", "_spec", "mock_", "_mock",
        "fixture_", "_fixture", "example_", "_example", "sample_", "_sample"
    ])
    
    # ML Production Configuration
    enable_ml_monitoring: bool = True
    ml_max_workers: int = 4
    ml_failure_threshold: int = 5
    ml_recovery_timeout: int = 300
    ml_success_threshold: int = 3
    ml_health_check_interval: int = 60
    ml_improvement_threshold: float = 0.05
    ml_max_errors: int = 10
    ml_model_path: Optional[str] = None
    ml_health_verbose_logging: bool = False  # Control health check warning verbosity
    
    # Threading and performance
    max_workers: int = 4
    cache_size: int = 1000
    
    # Parser settings
    allow_fallback_parsing: bool = True
    require_full_ast: bool = False
    fallback_parser_warnings: bool = True
    
    @validator('confidence_threshold')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('confidence_threshold must be between 0.0 and 1.0')
        return v
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """Load configuration from file."""
        try:
            config_path = Path(config_path)
            if not config_path.exists():
                raise ConfigurationError(f"Configuration file not found: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    # SECURITY: Use safe YAML loading with size limits
                    import yaml
                    
                    # Read with size limit to prevent YAML bomb attacks
                    content = f.read()
                    if len(content) > 1024 * 1024:  # 1MB limit
                        raise ConfigurationError(f"Configuration file too large: {len(content)} bytes")
                    
                    # Use safe_load to prevent code execution
                    data = yaml.safe_load(content)
                elif config_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    raise ConfigurationError(f"Unsupported configuration file format: {config_path.suffix}")
            
            return cls(**data)
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to file."""
        try:
            config_path = Path(config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = self.dict()
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(data, f, indent=2)
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def get_pattern(self, name: str) -> Optional[DetectionPattern]:
        """Get a detection pattern by name."""
        for pattern in self.patterns:
            if pattern.name == name:
                return pattern
        
        # Return a default pattern if none found, instead of None
        if name == "credit_card":
            return DetectionPattern(
                name="credit_card",
                regex=r'\b(?:\d{4}[-\s]?){3}\d{4}\b|\b3[47]\d{13}\b',
                confidence=0.8,
                risk_level=RiskLevel.HIGH,
                description="Credit card number detection"
            )
        elif name == "email":
            return DetectionPattern(
                name="email",
                regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                confidence=0.9,
                risk_level=RiskLevel.MEDIUM,
                description="Email address detection"
            )
        
        return None
    
    def update_license_tier(self, tier: LicenseTier) -> None:
        """Update license tier and enable/disable features accordingly."""
        # Create a new LicenseConfig instance with the updated tier, preserving existing data
        self.license = LicenseConfig(
            tier=tier,
            license_key=self.license.license_key,
            expiry_date=self.license.expiry_date
        )
        
        # Update ML settings based on license
        if tier == LicenseTier.ENTERPRISE:
            self.ml_enabled = True
            self.enable_ast = True
            self.enable_dataflow = True
            self.enable_ml = True
            if not self.ml_model_path:
                # Set default ML model path
                default_model_path = Path(__file__).parent.parent.parent / "configs" / "ml_models" / "levox_model.pkl"
                self.ml_model_path = str(default_model_path)
        else:
            self.ml_enabled = False
            self.enable_ast = False
            self.enable_dataflow = False
            self.enable_ml = False
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled based on license."""
        # Get features from the current license tier
        return self.license.features.get(feature, False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback to default (dict-like interface)."""
        # Check if the key exists as an attribute
        if hasattr(self, key):
            return getattr(self, key)
        
        # Check nested objects
        if key == 'languages':
            return ['python', 'javascript', 'typescript', 'java', 'cpp']
        elif key == 'context_modifiers':
            return {}
        elif key == 'max_flow_distance':
            return getattr(self.performance, 'max_scan_time_seconds', 10)
        elif key == 'max_concurrent_files':
            return getattr(self.performance, 'concurrent_workers', 4)
        elif key == 'analysis_timeout_seconds':
            return getattr(self.performance, 'max_scan_time_seconds', 30.0)
        elif key == 'enable_async':
            return True
        elif key == 'max_file_size':
            return getattr(self.performance, 'max_file_size_mb', 100) * 1024 * 1024
        
        return default
    
    def validate(self) -> None:
        """Validate configuration settings."""
        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            raise ConfigurationError("confidence_threshold must be between 0.0 and 1.0")
        
        if self.performance.max_file_size_mb <= 0:
            raise ConfigurationError("max_file_size_mb must be positive")
        
        if self.performance.max_scan_time_seconds <= 0:
            raise ConfigurationError("max_scan_time_seconds must be positive")

    @classmethod
    def load_detection_rules(cls, config_dir: Path) -> Dict[str, Any]:
        """
        Dynamically load detection rules from configuration files.
        
        Args:
            config_dir: Directory containing rules.yaml and patterns.json
            
        Returns:
            Dictionary containing loaded rules and patterns
        """
        rules = {}
        
        try:
            # Load rules.yaml
            rules_file = config_dir / "rules.yaml"
            if rules_file.exists():
                with open(rules_file, 'r', encoding='utf-8') as f:
                    # SECURITY: Use safe YAML loading with size limits
                    content = f.read()
                    if len(content) > 1024 * 1024:  # 1MB limit
                        logging.getLogger(__name__).warning(f"Rules file too large, skipping: {len(content)} bytes")
                        return rules
                    
                    yaml_rules = yaml.safe_load(content)
                    if yaml_rules:
                        rules.update(yaml_rules)
            
            # Load patterns.json
            patterns_file = config_dir / "patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    json_patterns = json.load(f)
                    rules['patterns'] = json_patterns.get('patterns', [])
                    rules['patterns_metadata'] = json_patterns.get('metadata', {})
            
            return rules
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to load detection rules: {e}")
            return {}
    
    @classmethod
    def reload_detection_rules(cls, config_dir: Path) -> Dict[str, Any]:
        """
        Reload detection rules from configuration files.
        Useful for hot-reloading during development.
        
        Args:
            config_dir: Directory containing rules.yaml and patterns.json
            
        Returns:
            Dictionary containing reloaded rules and patterns
        """
        logging.getLogger(__name__).info("Reloading detection rules...")
        return cls.load_detection_rules(config_dir)
    
    def get_detection_patterns(self) -> List[DetectionPattern]:
        """Get list of detection patterns from configuration."""
        patterns = []
        
        try:
            if hasattr(self, 'patterns') and self.patterns:
                for pattern_data in self.patterns:
                    if isinstance(pattern_data, dict):
                        pattern = DetectionPattern(
                            name=pattern_data.get('name', ''),
                            regex=pattern_data.get('regex', ''),
                            confidence=pattern_data.get('confidence', 0.8),
                            risk_level=RiskLevel(pattern_data.get('risk_level', 'medium')),
                            description=pattern_data.get('description', ''),
                            enabled=pattern_data.get('enabled', True),
                            languages=pattern_data.get('languages', [])
                        )
                        patterns.append(pattern)
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to parse detection patterns: {e}")
        
        return patterns
    
    def get_pattern_by_name(self, pattern_name: str) -> Optional[DetectionPattern]:
        """Get a specific detection pattern by name."""
        patterns = self.get_detection_patterns()
        for pattern in patterns:
            if pattern.name == pattern_name:
                return pattern
        return None
    
    def is_pattern_enabled(self, pattern_name: str) -> bool:
        """Check if a specific pattern is enabled."""
        pattern = self.get_pattern_by_name(pattern_name)
        return pattern.enabled if pattern else False


def load_default_config() -> Config:
    """Load default configuration, merging with user config if present."""
    # Try to load user config from ~/.levox/config.yaml and merge
    user_config_path = Path.home() / ".levox" / "config.yaml"
    if user_config_path.exists():
        try:
            with open(user_config_path, 'r', encoding='utf-8') as f:
                # SECURITY: Use safe YAML loading with size limits
                content = f.read()
                if len(content) > 1024 * 1024:  # 1MB limit
                    logging.getLogger(__name__).warning(f"User config file too large, using defaults: {len(content)} bytes")
                    return Config()
                
                user_data = yaml.safe_load(content) or {}
            # Pydantic will apply defaults for missing fields
            config = Config(**user_data)
        except Exception:
            # Fallback to pure defaults on any error
            config = Config()
    else:
        config = Config()
    
    # Keep default as STANDARD unless explicitly changed by caller/tests
    # (Do not auto-upgrade to enterprise in library code to avoid test surprises.)
    
    # Add default detection patterns
    default_patterns = [
        DetectionPattern(
            name="credit_card",
            regex=r'\b(?:\d{4}[-\s]?){3}\d{4}\b|\b3[47]\d{13}\b',
            confidence=0.8,
            risk_level=RiskLevel.HIGH,
            description="Credit card number detection",
            languages=["python", "javascript", "java", "cpp"]
        ),
        DetectionPattern(
            name="email",
            regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            confidence=0.9,
            risk_level=RiskLevel.MEDIUM,
            description="Email address detection",
            languages=["python", "javascript", "java", "cpp"]
        ),
        DetectionPattern(
            name="ssn",
            regex=r'(?:\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b)',
            confidence=0.9,
            risk_level=RiskLevel.HIGH,
            description="Social Security Number detection",
            languages=["python", "javascript", "java", "cpp"]
        ),
        DetectionPattern(
            name="phone",
            # Stricter: typical North American and E.164 forms; avoid catching random digit clusters
            regex=r'(?:\b\+?\d{1,3}[-\s]?(?:\(\d{2,4}\)|\d{2,4})[-\s]?\d{3}[-\s]?\d{4}\b|\b\(\d{3}\)\s?\d{3}[-\s]?\d{4}\b|\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b)',
            confidence=0.75,
            risk_level=RiskLevel.MEDIUM,
            description="Phone number detection",
            languages=["python", "javascript", "java", "cpp"]
        ),
    ]
    
    config.patterns = default_patterns
    
    # Set default ML model path for enterprise tier
    if config.license.tier == LicenseTier.ENTERPRISE:
        models_dir = Path(__file__).parent.parent.parent / "configs" / "ml_models"
        # Prefer a stable pointer if present, fall back to legacy name
        preferred = models_dir / "levox_latest.pkl"
        fallback = models_dir / "levox_model.pkl"
        config.ml_model_path = str(preferred if preferred.exists() else fallback)
        config.ml_enabled = True
        config.enable_ast = True
        config.enable_dataflow = True
        config.enable_ml = True
    
    return config


def _is_development_environment() -> bool:
    """Detect if we're running in a development environment."""
    # Check for common development indicators
    dev_indicators = [
        # Check if we're in the Levox source directory
        Path(__file__).parent.parent.parent.name == "levox",
        # Check for development environment variables
        os.getenv("LEVOX_DEV", "").lower() in ("1", "true", "yes"),
        os.getenv("PYTHONPATH", "").find("levox") != -1,
        # Check if we're running from source
        Path(__file__).parent.parent.parent.exists(),
        # Check for common dev files
        (Path(__file__).parent.parent.parent / "setup.py").exists(),
        (Path(__file__).parent.parent.parent / "requirements.txt").exists(),
    ]
    
    return any(dev_indicators)


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for configuration changes."""
    
    def __init__(self, config_path: Path, callback: Callable[[Config], None], debounce_seconds: float = 1.0):
        super().__init__()
        self.config_path = config_path
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.last_modified = 0
        self.logger = logging.getLogger(__name__)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        event_path = Path(event.src_path)
        if event_path.resolve() == self.config_path.resolve():
            current_time = time.time()
            
            # Debounce rapid file changes
            if current_time - self.last_modified < self.debounce_seconds:
                return
            
            self.last_modified = current_time
            
            try:
                # Reload configuration
                new_config = Config.from_file(str(self.config_path))
                self.logger.info(f"Configuration reloaded from {self.config_path}")
                self.callback(new_config)
                
            except Exception as e:
                self.logger.error(f"Failed to reload configuration: {e}")


class ConfigWatcher:
    """Configuration file watcher with hot-reload capability."""
    
    def __init__(self, config_path: Path, callback: Callable[[Config], None]):
        self.config_path = config_path
        self.callback = callback
        self.observer = None
        self.handler = None
        self.logger = logging.getLogger(__name__)
        
        if not WATCHDOG_AVAILABLE:
            self.logger.warning("Watchdog not available - config hot-reload disabled")
    
    def start(self) -> bool:
        """Start watching the configuration file."""
        if not WATCHDOG_AVAILABLE:
            return False
        
        if not self.config_path.exists():
            self.logger.warning(f"Config file {self.config_path} does not exist - cannot watch")
            return False
        
        try:
            self.observer = Observer()
            self.handler = ConfigFileHandler(self.config_path, self.callback)
            
            # Watch the directory containing the config file
            watch_dir = self.config_path.parent
            self.observer.schedule(self.handler, str(watch_dir), recursive=False)
            self.observer.start()
            
            self.logger.info(f"Started watching config file: {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start config watcher: {e}")
            return False
    
    def stop(self):
        """Stop watching the configuration file."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=5.0)
            self.logger.info("Stopped config watcher")
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


class ThreadSafeConfig:
    """Thread-safe configuration wrapper with hot-reload support."""
    
    def __init__(self, initial_config: Config, config_path: Optional[Path] = None):
        self._config = initial_config
        self._lock = threading.RLock()
        self._watcher = None
        self._change_callbacks = []
        self.logger = logging.getLogger(__name__)
        
        if config_path and WATCHDOG_AVAILABLE:
            self._watcher = ConfigWatcher(config_path, self._on_config_changed)
            self._watcher.start()
    
    def _on_config_changed(self, new_config: Config):
        """Handle configuration changes."""
        with self._lock:
            old_config = self._config
            self._config = new_config
            
            # Notify all registered callbacks
            for callback in self._change_callbacks:
                try:
                    callback(old_config, new_config)
                except Exception as e:
                    self.logger.error(f"Error in config change callback: {e}")
    
    def get_config(self) -> Config:
        """Get current configuration (thread-safe)."""
        with self._lock:
            return self._config
    
    def register_change_callback(self, callback: Callable[[Config, Config], None]):
        """Register a callback to be called when configuration changes."""
        with self._lock:
            self._change_callbacks.append(callback)
    
    def unregister_change_callback(self, callback: Callable[[Config, Config], None]):
        """Unregister a configuration change callback."""
        with self._lock:
            if callback in self._change_callbacks:
                self._change_callbacks.remove(callback)
    
    def stop_watching(self):
        """Stop configuration file watching."""
        if self._watcher:
            self._watcher.stop()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_watching()
    
    # Delegate attribute access to the underlying config
    def __getattr__(self, name):
        with self._lock:
            return getattr(self._config, name)
