"""Case insensitive email normalization.

Revision ID: 0002_case_insensitive_email
Revises: 0001_initial_schema
Create Date: 2026-10-11 20:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002_case_insensitive_email"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()

    # Detect case-insensitive duplicate emails without selecting personal email values
    conflict_rows = bind.execute(
        sa.text(
            "SELECT count(*) AS duplicate_count FROM users "
            "GROUP BY lower(email) HAVING count(*) > 1"
        )
    ).fetchall()

    if conflict_rows:
        conflict_group_count = len(conflict_rows)
        raise RuntimeError(
            f"Cannot apply migration {revision}: found {conflict_group_count} "
            "case-insensitive duplicate email group(s) in 'users'. "
            "Resolve conflicting accounts manually before running this migration."
        )

    bind.execute(
        sa.text(
            "UPDATE users SET email = lower(email) WHERE email != lower(email)"
        )
    )

    op.create_index(
        "ix_users_lower_email",
        "users",
        [sa.text("lower(email)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_users_lower_email", table_name="users")
