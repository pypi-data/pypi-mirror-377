"""
Data models for GDPR compliance analysis and reporting.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum

from pydantic import BaseModel, Field


class GDPRArticle(str, Enum):
    """GDPR articles that can be referenced in compliance issues."""
    ARTICLE_5 = "Article 5"  # Principles of processing
    ARTICLE_6 = "Article 6"  # Lawfulness of processing
    ARTICLE_7 = "Article 7"  # Conditions for consent
    ARTICLE_12 = "Article 12"  # Transparent information
    ARTICLE_15 = "Article 15"  # Right of access (DSAR)
    ARTICLE_16 = "Article 16"  # Right to rectification
    ARTICLE_17 = "Article 17"  # Right to erasure (Right to be forgotten)
    ARTICLE_18 = "Article 18"  # Right to restriction
    ARTICLE_20 = "Article 20"  # Right to data portability
    ARTICLE_25 = "Article 25"  # Data protection by design
    ARTICLE_30 = "Article 30"  # Records of processing activities
    ARTICLE_32 = "Article 32"  # Security of processing
    ARTICLE_33 = "Article 33"  # Notification of personal data breach
    ARTICLE_34 = "Article 34"  # Communication of personal data breach
    ARTICLE_35 = "Article 35"  # Data protection impact assessment
    ARTICLE_44 = "Article 44"  # General principle for transfers
    ARTICLE_45 = "Article 45"  # Transfers on basis of adequacy decision
    ARTICLE_46 = "Article 46"  # Transfers subject to safeguards
    ARTICLE_47 = "Article 47"  # Binding corporate rules
    ARTICLE_48 = "Article 48"  # Transfers or disclosures not authorized by Union law
    ARTICLE_49 = "Article 49"  # Derogations for specific situations
    GENERAL = "General"  # General compliance issues


class ComplianceLevel(str, Enum):
    """Compliance issue severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceCategory(str, Enum):
    """Categories of compliance issues."""
    SECURITY = "security"
    DATA_RIGHTS = "data_rights"
    CONSENT = "consent"
    DATA_TRANSFER = "data_transfer"
    RETENTION = "retention"
    TRANSPARENCY = "transparency"
    BREACH_NOTIFICATION = "breach_notification"
    IMPACT_ASSESSMENT = "impact_assessment"
    DATA_PROTECTION_BY_DESIGN = "data_protection_by_design"
    PURPOSE_LIMITATION = "purpose_limitation"
    DATA_MINIMIZATION = "data_minimization"
    ACCOUNTABILITY = "accountability"
    RISK_ASSESSMENT = "risk_assessment"
    LAWFUL_BASIS = "lawful_basis"
    GENERAL = "general"


@dataclass
class ComplianceIssue:
    """Represents a single GDPR compliance issue."""
    
    id: str
    severity: ComplianceLevel
    article_ref: GDPRArticle
    category: ComplianceCategory
    description: str
    location: str
    line_number: Optional[int] = None
    column_start: Optional[int] = None
    column_end: Optional[int] = None
    file_path: Optional[str] = None
    remediation_suggestion: str = ""
    evidence: str = ""
    false_positive: bool = False
    validated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=2)
    
    @property
    def is_critical(self) -> bool:
        """Check if this is a critical issue."""
        return self.severity == ComplianceLevel.CRITICAL
    
    @property
    def is_high_priority(self) -> bool:
        """Check if this is a high priority issue."""
        return self.severity in [ComplianceLevel.CRITICAL, ComplianceLevel.HIGH]


@dataclass
class ComplianceResult:
    """Represents the complete result of a GDPR compliance audit."""
    
    project_path: str
    audit_timestamp: datetime
    completion_timestamp: datetime
    compliance_score: float
    total_issues: int
    issues_by_severity: Dict[ComplianceLevel, int]
    issues_by_article: Dict[GDPRArticle, int]
    detection_result: Any  # DetectionResult from core engine
    compliance_issues: List[ComplianceIssue]
    audit_options: Any  # ComplianceAuditOptions
    report: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_compliant(self) -> bool:
        """Check if the project meets compliance threshold."""
        return self.compliance_score >= 80.0
    
    @property
    def needs_attention(self) -> bool:
        """Check if the project needs immediate attention."""
        return self.compliance_score < 70.0
    
    @property
    def critical_issues_count(self) -> int:
        """Get count of critical issues."""
        return self.issues_by_severity.get(ComplianceLevel.CRITICAL, 0)
    
    @property
    def high_issues_count(self) -> int:
        """Get count of high priority issues."""
        return self.issues_by_severity.get(ComplianceLevel.HIGH, 0)
    
    @property
    def audit_duration(self) -> float:
        """Get audit duration in seconds."""
        return (self.completion_timestamp - self.audit_timestamp).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = asdict(self)
        data['audit_timestamp'] = self.audit_timestamp.isoformat()
        data['completion_timestamp'] = self.completion_timestamp.isoformat()
        data['is_compliant'] = self.is_compliant
        data['needs_attention'] = self.needs_attention
        data['critical_issues_count'] = self.critical_issues_count
        data['high_issues_count'] = self.high_issues_count
        data['audit_duration'] = self.audit_duration
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=2)


@dataclass
class DSARRequest:
    """Data Subject Access Request (DSAR) information."""
    
    request_id: str
    user_id: str
    request_type: str  # access, rectification, erasure, portability
    status: str  # pending, processing, completed, denied
    request_date: datetime
    completion_date: Optional[datetime] = None
    data_categories: List[str] = field(default_factory=list)
    processing_time_hours: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityCheck:
    """Security-related compliance check result."""
    
    check_id: str
    check_name: str
    article_ref: GDPRArticle
    status: str  # passed, failed, warning
    description: str
    evidence: str
    remediation: str
    severity: ComplianceLevel
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DataTransferInfo:
    """Information about cross-border data transfers."""
    
    transfer_id: str
    destination_country: str
    transfer_basis: str  # adequacy, safeguards, derogations
    risk_assessment: str  # low, medium, high
    safeguards_used: List[str] = field(default_factory=list)
    documentation_available: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceMetrics:
    """Aggregated compliance metrics."""
    
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    compliance_rate: float
    average_resolution_time_hours: float
    critical_issues_resolved: int
    total_issues_resolved: int
    last_audit_date: Optional[datetime] = None
    trend_data: Dict[str, List[float]] = field(default_factory=dict)


class ComplianceReport(BaseModel):
    """Structured compliance report."""
    
    report_id: str = Field(description="Unique report identifier")
    project_name: str = Field(description="Name of the audited project")
    audit_date: datetime = Field(description="Date of the audit")
    compliance_score: float = Field(description="Overall compliance score (0-100)")
    executive_summary: str = Field(description="Executive summary of findings")
    critical_findings: List[str] = Field(description="List of critical findings")
    recommendations: List[str] = Field(description="List of recommendations")
    next_steps: List[str] = Field(description="Recommended next steps")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Export all models
__all__ = [
    'GDPRArticle',
    'ComplianceLevel',
    'ComplianceCategory',
    'ComplianceIssue',
    'ComplianceResult',
    'DSARRequest',
    'SecurityCheck',
    'DataTransferInfo',
    'ComplianceMetrics',
    'ComplianceReport'
]
