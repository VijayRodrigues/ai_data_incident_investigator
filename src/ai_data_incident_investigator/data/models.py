from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class IncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class IncidentType(str, Enum):
    RECORD_LOSS = "RECORD_LOSS"
    SCHEMA_DRIFT = "SCHEMA_DRIFT"
    FRESHNESS = "FRESHNESS"
    DUPLICATE = "DUPLICATE"
    DATA_QUALITY = "DATA_QUALITY"
    PIPELINE_FAILURE = "PIPELINE_FAILURE"
    OTHER = "OTHER"


class DataSourceType(str, Enum):
    DATABASE = "DATABASE"
    FILE = "FILE"
    API = "API"
    DATA_LAKE = "DATA_LAKE"
    DATA_WAREHOUSE = "DATA_WAREHOUSE"
    OTHER = "OTHER"


class Environment(str, Enum):
    DEV = "DEV"
    TEST = "TEST"
    UAT = "UAT"
    PROD = "PROD"


class PipelineStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class InvestigationStatus(str, Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class InvestigatorType(str, Enum):
    RULE_BASED = "RULE_BASED"
    AI = "AI"
    HYBRID = "HYBRID"


class FindingType(str, Enum):
    RECORD_LOSS = "RECORD_LOSS"
    FILTER = "FILTER"
    JOIN = "JOIN"
    SCHEMA = "SCHEMA"
    FRESHNESS = "FRESHNESS"
    DUPLICATE = "DUPLICATE"
    DATA_QUALITY = "DATA_QUALITY"
    PIPELINE = "PIPELINE"
    OTHER = "OTHER"


class EvidenceType(str, Enum):
    LOG = "LOG"
    DOCUMENT = "DOCUMENT"
    QUERY_RESULT = "QUERY_RESULT"
    DATA_SAMPLE = "DATA_SAMPLE"
    SCHEMA = "SCHEMA"
    PIPELINE_METADATA = "PIPELINE_METADATA"
    OTHER = "OTHER"


class RemediationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RemediationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


# ---------------------------------------------------------------------------
# Incidents
# ---------------------------------------------------------------------------


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    incident_number: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    severity: Mapped[IncidentSeverity] = mapped_column(
        SQLEnum(IncidentSeverity, name="incident_severity"),
        nullable=False,
        default=IncidentSeverity.MEDIUM,
    )

    status: Mapped[IncidentStatus] = mapped_column(
        SQLEnum(IncidentStatus, name="incident_status"),
        nullable=False,
        default=IncidentStatus.OPEN,
    )

    incident_type: Mapped[IncidentType] = mapped_column(
        SQLEnum(IncidentType, name="incident_type"),
        nullable=False,
        default=IncidentType.OTHER,
    )

    source_system: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    target_system: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    source_dataset: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    target_dataset: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    expected_record_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    actual_record_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    difference_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    detected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    pipeline_runs: Mapped[list["PipelineRun"]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )

    investigation_runs: Mapped[list["InvestigationRun"]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )

    evidence: Mapped[list["Evidence"]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )

    remediation_actions: Mapped[list["RemediationAction"]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )

    events: Mapped[list["IncidentEvent"]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )


# ---------------------------------------------------------------------------
# Data sources
# ---------------------------------------------------------------------------


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    source_type: Mapped[DataSourceType] = mapped_column(
        SQLEnum(DataSourceType, name="data_source_type"),
        nullable=False,
    )

    platform: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    environment: Mapped[Environment] = mapped_column(
        SQLEnum(Environment, name="environment"),
        nullable=False,
    )

    connection_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    owner_team: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    extra_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


# ---------------------------------------------------------------------------
# Pipeline runs
# ---------------------------------------------------------------------------


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    incident_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    pipeline_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    pipeline_run_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    orchestrator: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[PipelineStatus] = mapped_column(
        SQLEnum(PipelineStatus, name="pipeline_status"),
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    records_read: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    records_written: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    records_rejected: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    log_reference: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    extra_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    incident: Mapped["Incident"] = relationship(
        back_populates="pipeline_runs",
    )


# ---------------------------------------------------------------------------
# Investigation runs
# ---------------------------------------------------------------------------


class InvestigationRun(Base):
    __tablename__ = "investigation_runs"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    incident_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    run_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[InvestigationStatus] = mapped_column(
        SQLEnum(InvestigationStatus, name="investigation_status"),
        nullable=False,
        default=InvestigationStatus.RUNNING,
    )

    investigator_type: Mapped[InvestigatorType] = mapped_column(
        SQLEnum(InvestigatorType, name="investigator_type"),
        nullable=False,
        default=InvestigatorType.HYBRID,
    )

    model_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence_score: Mapped[float | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    incident: Mapped["Incident"] = relationship(
        back_populates="investigation_runs",
    )

    findings: Mapped[list["Finding"]] = relationship(
        back_populates="investigation_run",
        cascade="all, delete-orphan",
    )

    evidence: Mapped[list["Evidence"]] = relationship(
        back_populates="investigation_run",
        cascade="all, delete-orphan",
    )


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    investigation_run_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("investigation_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    finding_type: Mapped[FindingType] = mapped_column(
        SQLEnum(FindingType, name="finding_type"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    severity: Mapped[IncidentSeverity] = mapped_column(
        SQLEnum(
            IncidentSeverity,
            name="finding_severity",
        ),
        nullable=False,
    )

    confidence_score: Mapped[float | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )

    is_root_cause_candidate: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    evidence_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    investigation_run: Mapped["InvestigationRun"] = relationship(
        back_populates="findings",
    )

    remediation_actions: Mapped[list["RemediationAction"]] = relationship(
        back_populates="finding",
        cascade="all, delete-orphan",
    )

    evidence_links: Mapped[list["FindingEvidence"]] = relationship(
        back_populates="finding",
        cascade="all, delete-orphan",
    )


# ---------------------------------------------------------------------------
# Finding evidence links
# ---------------------------------------------------------------------------


class FindingEvidence(Base):
    __tablename__ = "finding_evidence"

    __table_args__ = (
        UniqueConstraint(
            "finding_id",
            "evidence_chunk_id",
            name="uq_finding_evidence_finding_chunk",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    finding_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    evidence_chunk_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("evidence_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    relevance_distance: Mapped[float | None] = mapped_column(
        Numeric(12, 8),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    finding: Mapped["Finding"] = relationship(
        back_populates="evidence_links",
    )

    evidence_chunk: Mapped["EvidenceChunk"] = relationship(
        back_populates="finding_links",
    )


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    incident_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    investigation_run_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("investigation_runs.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    evidence_type: Mapped[EvidenceType] = mapped_column(
        SQLEnum(EvidenceType, name="evidence_type"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    storage_uri: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    source_system: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    content_hash: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    extra_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    incident: Mapped["Incident"] = relationship(
        back_populates="evidence",
    )

    investigation_run: Mapped["InvestigationRun | None"] = relationship(
        back_populates="evidence",
    )

    chunks: Mapped[list["EvidenceChunk"]] = relationship(
        back_populates="evidence",
        cascade="all, delete-orphan",
    )


# ---------------------------------------------------------------------------
# Evidence chunks / RAG
# ---------------------------------------------------------------------------


class EvidenceChunk(Base):
    __tablename__ = "evidence_chunks"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    evidence_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("evidence.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    token_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(1024),
        nullable=True,
    )

    extra_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    evidence: Mapped["Evidence"] = relationship(
        back_populates="chunks",
    )

    finding_links: Mapped[list["FindingEvidence"]] = relationship(
        back_populates="evidence_chunk",
        cascade="all, delete-orphan",
    )


# ---------------------------------------------------------------------------
# Remediation actions
# ---------------------------------------------------------------------------


class RemediationAction(Base):
    __tablename__ = "remediation_actions"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    incident_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    finding_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    priority: Mapped[RemediationPriority] = mapped_column(
        SQLEnum(
            RemediationPriority,
            name="remediation_priority",
        ),
        nullable=False,
    )

    status: Mapped[RemediationStatus] = mapped_column(
        SQLEnum(
            RemediationStatus,
            name="remediation_status",
        ),
        nullable=False,
        default=RemediationStatus.PROPOSED,
    )

    owner_team: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    incident: Mapped["Incident"] = relationship(
        back_populates="remediation_actions",
    )

    finding: Mapped["Finding | None"] = relationship(
        back_populates="remediation_actions",
    )


# ---------------------------------------------------------------------------
# Incident events / audit trail
# ---------------------------------------------------------------------------


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    incident_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    actor: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    extra_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    incident: Mapped["Incident"] = relationship(
        back_populates="events",
    )