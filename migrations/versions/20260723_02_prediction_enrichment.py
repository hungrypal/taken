"""Add role and prediction-enrichment columns for existing databases.

Revision ID: 20260723_02
Revises: 20260723_01
Create Date: 2026-07-23
"""

from alembic import op
import sqlalchemy as sa


revision = "20260723_02"
down_revision = "20260723_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing deployments created by revision 01 receive the Feature 3/15
    # fields. New installs get these columns directly from revision 01.
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()))
    with op.batch_alter_table("farms") as batch:
        batch.alter_column("name", new_column_name="farm_name", existing_type=sa.String(length=120))
        batch.alter_column("crop_type", new_column_name="crop", existing_type=sa.String(length=80), existing_nullable=True)
        batch.alter_column("area_hectares", new_column_name="area", existing_type=sa.Float(), existing_nullable=True)
    with op.batch_alter_table("predictions") as batch:
        batch.add_column(sa.Column("climate", sa.JSON(), nullable=True))
        batch.add_column(sa.Column("recommendations", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("predictions") as batch:
        batch.drop_column("recommendations")
        batch.drop_column("climate")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("is_admin")
    with op.batch_alter_table("farms") as batch:
        batch.alter_column("area", new_column_name="area_hectares", existing_type=sa.Float(), existing_nullable=True)
        batch.alter_column("crop", new_column_name="crop_type", existing_type=sa.String(length=80), existing_nullable=True)
        batch.alter_column("farm_name", new_column_name="name", existing_type=sa.String(length=120))
