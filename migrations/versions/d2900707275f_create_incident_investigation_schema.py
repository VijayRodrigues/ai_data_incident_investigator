"""Create incident investigation schema

Revision ID: d2900707275f
Revises:
Create Date: 2026-08-16 19:04:58.127662
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector.sqlalchemy


# revision identifiers, used by Alembic.
revision: str = "d2900707275f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "data_sources",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "source_type",
            sa.Enum(
                "DATABASE",
                "FILE",
                "API",
                "DATA_LAKE",
                "DATA_WAREHOUSE",
                "OTHER",
                name="data_source_type",
            ),
            nullable=False,
        ),
        sa.Column("platform", sa.String(length=100), nullable=False),
        sa.Column(
            "environment",
            sa.Enum(
                "DEV",
                "TEST",
                "UAT",
                "PROD",
                name="environment",
            ),
            nullable=False,
        ),
        sa.Column(
            "connection_reference",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "owner_team",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "extra_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "incident_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("incident_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("actor", sa.String(length=255), nullable=True),
        sa.Column(
            "extra_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["incidents.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_incident_events_incident_id"),
        "incident_events",
        ["incident_id"],
        unique=False,
    )

    op.create_table(
        "investigation_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("incident_id", sa.UUID(), nullable=False),
        sa.Column("run_number", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "RUNNING",
                "COMPLETED",
                "FAILED",
                name="investigation_status",
            ),
            nullable=False,
        ),
        sa.Column(
            "investigator_type",
            sa.Enum(
                "RULE_BASED",
                "AI",
                "HYBRID",
                name="investigator_type",
            ),
            nullable=False,
        ),
        sa.Column("model_name", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "confidence_score",
            sa.Numeric(precision=5, scale=4),
            nullable=True,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["incidents.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_investigation_runs_incident_id"),
        "investigation_runs",
        ["incident_id"],
        unique=False,
    )

    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("incident_id", sa.UUID(), nullable=False),
        sa.Column("pipeline_name", sa.String(length=255), nullable=False),
        sa.Column(
            "pipeline_run_id",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "orchestrator",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "RUNNING",
                "SUCCESS",
                "FAILED",
                "PARTIAL",
                name="pipeline_status",
            ),
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "duration_seconds",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "records_read",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "records_written",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "records_rejected",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "log_reference",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "extra_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["incidents.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_pipeline_runs_incident_id"),
        "pipeline_runs",
        ["incident_id"],
        unique=False,
    )

    op.create_table(
        "evidence",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("incident_id", sa.UUID(), nullable=False),
        sa.Column(
            "investigation_run_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "evidence_type",
            sa.Enum(
                "LOG",
                "DOCUMENT",
                "QUERY_RESULT",
                "DATA_SAMPLE",
                "SCHEMA",
                "PIPELINE_METADATA",
                "OTHER",
                name="evidence_type",
            ),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "storage_uri",
            sa.String(length=1000),
            nullable=True,
        ),
        sa.Column(
            "source_system",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "content_hash",
            sa.String(length=128),
            nullable=True,
        ),
        sa.Column(
            "extra_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["incidents.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["investigation_run_id"],
            ["investigation_runs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_evidence_content_hash"),
        "evidence",
        ["content_hash"],
        unique=False,
    )

    op.create_index(
        op.f("ix_evidence_incident_id"),
        "evidence",
        ["incident_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_evidence_investigation_run_id"),
        "evidence",
        ["investigation_run_id"],
        unique=False,
    )

    op.create_table(
        "findings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "investigation_run_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "finding_type",
            sa.Enum(
                "RECORD_LOSS",
                "FILTER",
                "JOIN",
                "SCHEMA",
                "FRESHNESS",
                "DUPLICATE",
                "DATA_QUALITY",
                "PIPELINE",
                "OTHER",
                name="finding_type",
            ),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.Enum(
                "LOW",
                "MEDIUM",
                "HIGH",
                "CRITICAL",
                name="finding_severity",
            ),
            nullable=False,
        ),
        sa.Column(
            "confidence_score",
            sa.Numeric(precision=5, scale=4),
            nullable=True,
        ),
        sa.Column(
            "is_root_cause_candidate",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "evidence_summary",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["investigation_run_id"],
            ["investigation_runs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_findings_investigation_run_id"),
        "findings",
        ["investigation_run_id"],
        unique=False,
    )

    op.create_table(
        "evidence_chunks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("evidence_id", sa.UUID(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "token_count",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "embedding_model",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "embedding",
            pgvector.sqlalchemy.vector.VECTOR(dim=1024),
            nullable=True,
        ),
        sa.Column(
            "extra_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["evidence_id"],
            ["evidence.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_evidence_chunks_evidence_id"),
        "evidence_chunks",
        ["evidence_id"],
        unique=False,
    )

    op.create_table(
        "remediation_actions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("incident_id", sa.UUID(), nullable=False),
        sa.Column(
            "finding_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column(
            "action",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.Enum(
                "LOW",
                "MEDIUM",
                "HIGH",
                name="remediation_priority",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "PROPOSED",
                "APPROVED",
                "COMPLETED",
                "REJECTED",
                name="remediation_status",
            ),
            nullable=False,
        ),
        sa.Column(
            "owner_team",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "due_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["finding_id"],
            ["findings.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["incidents.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_remediation_actions_finding_id"),
        "remediation_actions",
        ["finding_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_remediation_actions_incident_id"),
        "remediation_actions",
        ["incident_id"],
        unique=False,
    )

    # Extend the existing incidents table.
    #
    # The incidents table existed before Alembic was introduced, so
    # autogenerate did not create the PostgreSQL enum type automatically.
    op.execute(
        """
        CREATE TYPE incident_type AS ENUM (
            'RECORD_LOSS',
            'SCHEMA_DRIFT',
            'FRESHNESS',
            'DUPLICATE',
            'DATA_QUALITY',
            'PIPELINE_FAILURE',
            'OTHER'
        )
        """
    )

    op.add_column(
        "incidents",
        sa.Column(
            "incident_type",
            sa.Enum(
                "RECORD_LOSS",
                "SCHEMA_DRIFT",
                "FRESHNESS",
                "DUPLICATE",
                "DATA_QUALITY",
                "PIPELINE_FAILURE",
                "OTHER",
                name="incident_type",
            ),
            nullable=False,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "source_dataset",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "target_dataset",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "expected_record_count",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "actual_record_count",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "difference_count",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "incidents",
        sa.Column(
            "resolved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("incidents", "resolved_at")
    op.drop_column("incidents", "difference_count")
    op.drop_column("incidents", "actual_record_count")
    op.drop_column("incidents", "expected_record_count")
    op.drop_column("incidents", "target_dataset")
    op.drop_column("incidents", "source_dataset")
    op.drop_column("incidents", "incident_type")
    
    op.execute("DROP TYPE incident_type")

    op.drop_index(
        op.f("ix_remediation_actions_incident_id"),
        table_name="remediation_actions",
    )
    op.drop_index(
        op.f("ix_remediation_actions_finding_id"),
        table_name="remediation_actions",
    )
    op.drop_table("remediation_actions")

    op.drop_index(
        op.f("ix_evidence_chunks_evidence_id"),
        table_name="evidence_chunks",
    )
    op.drop_table("evidence_chunks")

    op.drop_index(
        op.f("ix_findings_investigation_run_id"),
        table_name="findings",
    )
    op.drop_table("findings")

    op.drop_index(
        op.f("ix_evidence_investigation_run_id"),
        table_name="evidence",
    )
    op.drop_index(
        op.f("ix_evidence_incident_id"),
        table_name="evidence",
    )
    op.drop_index(
        op.f("ix_evidence_content_hash"),
        table_name="evidence",
    )
    op.drop_table("evidence")

    op.drop_index(
        op.f("ix_pipeline_runs_incident_id"),
        table_name="pipeline_runs",
    )
    op.drop_table("pipeline_runs")

    op.drop_index(
        op.f("ix_investigation_runs_incident_id"),
        table_name="investigation_runs",
    )
    op.drop_table("investigation_runs")

    op.drop_index(
        op.f("ix_incident_events_incident_id"),
        table_name="incident_events",
    )
    op.drop_table("incident_events")

    op.drop_table("data_sources")