"""change start time and duration types of the table scenario events

Revision ID: 6b3c92176801
Revises: 14e576cbf423
Create Date: 2026-01-05 12:06:49.924836

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6b3c92176801"
down_revision: Union[str, Sequence[str], None] = "14e576cbf423"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Convert start_time from int (epoch) to timestamptz
    op.execute(
        """
        ALTER TABLE scenario_events
        ALTER COLUMN start_time
        TYPE TIMESTAMP WITH TIME ZONE
        USING TO_TIMESTAMP(start_time)::timestamptz
    """
    )

    # Convert duration from int (seconds) to interval
    op.execute(
        """
        ALTER TABLE scenario_events
        ALTER COLUMN duration
        TYPE INTERVAL
        USING (duration || ' seconds')::interval
    """
    )


def downgrade():
    # Convert back if needed
    op.execute(
        """
        ALTER TABLE scenario_events
        ALTER COLUMN start_time
        TYPE INTEGER
        USING EXTRACT(EPOCH FROM start_time)::integer
    """
    )
    op.execute(
        """
        ALTER TABLE scenario_events
        ALTER COLUMN duration
        TYPE INTEGER
        USING EXTRACT(EPOCH FROM duration)::integer
    """
    )
