"""create table

Revision ID: 677490ee2043
Revises:
Create Date: 2020-04-12 18:52:47.498131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '677490ee2043'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "race_denma",
        sa.Column("race_denma_id", sa.String(255), primary_key=True),
        sa.Column("race_id", sa.String(255), nullable=False),
        sa.Column("vote_id", sa.String(255), nullable=False),
        sa.Column("horse_number", sa.Integer, nullable=False),
        sa.Column("horse_name", sa.String(255), nullable=False),
        sa.Column("favorite", sa.Integer, nullable=True),
        sa.Column("odds_win", sa.Float, nullable=True),
        sa.Column("create_timestamp", sa.DateTime, nullable=False),
    )

    op.create_table(
        "vote_record",
        sa.Column("vote_record_id", sa.String(255), primary_key=True),
        sa.Column("race_id", sa.String(255), nullable=False),
        sa.Column("vote_id", sa.String(255), nullable=False),
        sa.Column("bet_type", sa.String(255), nullable=False),
        sa.Column("horse_number_1", sa.Integer, nullable=False),
        sa.Column("horse_number_2", sa.Integer, nullable=True),
        sa.Column("horse_number_3", sa.Integer, nullable=True),
        sa.Column("vote_cost", sa.Integer, nullable=False),
        sa.Column("algorithm", sa.String(255), nullable=False),
        sa.Column("vote_parameter", sa.String(4000), nullable=False),
        sa.Column("create_timestamp", sa.DateTime, nullable=False),
    )


def downgrade():
    pass
