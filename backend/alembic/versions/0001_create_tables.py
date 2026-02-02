"""create tables

Revision ID: 0001
Revises: 
Create Date: 2024-02-02
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("audience", sa.String(length=255)),
        sa.Column("deadline", sa.Date),
        sa.Column("owner_id", sa.String(length=100)),
        sa.Column("created_at", sa.DateTime),
    )
    op.create_table(
        "drafts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("content", sa.Text),
        sa.Column("updated_at", sa.DateTime),
    )
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("publisher", sa.String(length=255)),
        sa.Column("author", sa.String(length=255)),
        sa.Column("published_date", sa.Date),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text),
        sa.Column("excerpts", sa.Text),
        sa.Column("is_primary", sa.Boolean, default=False),
        sa.Column("is_historical", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime),
    )
    op.create_table(
        "interviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("person", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=255)),
        sa.Column("interview_date", sa.Date),
        sa.Column("transcript", sa.Text),
        sa.Column("extracted_quotes", sa.Text),
    )
    op.create_table(
        "claims",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("category", sa.String(length=50)),
        sa.Column("claim_type", sa.String(length=50)),
        sa.Column("status", sa.String(length=50)),
        sa.Column("confidence", sa.Float),
        sa.Column("notes", sa.Text),
    )
    op.create_table(
        "claim_source_matches",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("claim_id", sa.Integer, sa.ForeignKey("claims.id"), nullable=False),
        sa.Column("source_id", sa.Integer, sa.ForeignKey("sources.id")),
        sa.Column("interview_id", sa.Integer, sa.ForeignKey("interviews.id")),
        sa.Column("match_score", sa.Float),
        sa.Column("overlap", sa.Text),
        sa.Column("needs_review", sa.Boolean, default=False),
    )
    op.create_table(
        "ethics_checklists",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("right_of_reply", sa.Boolean, default=False),
        sa.Column("separate_fact_opinion", sa.Boolean, default=False),
        sa.Column("avoid_sensational", sa.Boolean, default=False),
        sa.Column("quote_integrity", sa.Boolean, default=False),
        sa.Column("updated_at", sa.DateTime),
    )


def downgrade():
    op.drop_table("ethics_checklists")
    op.drop_table("claim_source_matches")
    op.drop_table("claims")
    op.drop_table("interviews")
    op.drop_table("sources")
    op.drop_table("drafts")
    op.drop_table("projects")
