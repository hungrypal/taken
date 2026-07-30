"""Create TerraScore's initial domain database schema.

Revision ID: 20260723_01
Revises: 
Create Date: 2026-07-23
"""

from alembic import op
import sqlalchemy as sa


revision = "20260723_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "farms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("area_hectares", sa.Float(), nullable=True),
        sa.Column("crop_type", sa.String(length=80), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_farms_user_id", "farms", ["user_id"])

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("farm_id", sa.Integer(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("prediction_date", sa.Date(), nullable=False),
        sa.Column("drought_index", sa.Float(), nullable=False),
        sa.Column("ndvi", sa.Float(), nullable=False),
        sa.Column("lst", sa.Float(), nullable=False),
        sa.Column("risk_classification", sa.String(length=40), nullable=False),
        sa.Column("credit_score", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_predictions_farm_id", "predictions", ["farm_id"])
    op.create_index("ix_predictions_user_id", "predictions", ["user_id"])

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("farm_id", sa.Integer(), nullable=True),
        sa.Column("prediction_id", sa.Integer(), nullable=True),
        sa.Column("report_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="generated"),
        sa.Column("storage_uri", sa.String(length=1024), nullable=True),
        sa.Column("report_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reports_farm_id", "reports", ["farm_id"])
    op.create_index("ix_reports_prediction_id", "reports", ["prediction_id"])
    op.create_index("ix_reports_user_id", "reports", ["user_id"])

    op.create_table(
        "training_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="completed"),
        sa.Column("model_path", sa.String(length=1024), nullable=True),
        sa.Column("model_version", sa.String(length=80), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.String(length=2000), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_training_history_user_id", "training_history", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_training_history_user_id", table_name="training_history")
    op.drop_table("training_history")
    op.drop_index("ix_reports_user_id", table_name="reports")
    op.drop_index("ix_reports_prediction_id", table_name="reports")
    op.drop_index("ix_reports_farm_id", table_name="reports")
    op.drop_table("reports")
    op.drop_index("ix_predictions_user_id", table_name="predictions")
    op.drop_index("ix_predictions_farm_id", table_name="predictions")
    op.drop_table("predictions")
    op.drop_index("ix_farms_user_id", table_name="farms")
    op.drop_table("farms")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
