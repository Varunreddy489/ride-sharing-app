import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

revision = "rev1"

down_revision = "rev0"
depends_on = None
branch_labels = None


def upgrade() -> None:
    op.create_table(
        "driver_locations",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True, nullable=False
        ),
        sa.Column(
            "driver_id",
            sa.BigInteger(),
            sa.ForeignKey("drivers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.drop_column("ride_requests", "pickup_location")
    op.drop_column("ride_requests", "dropoff_location")

    op.add_column(
        "ride_requests",
        sa.Column(
            "vehicle_id",
            sa.Column(
                sa.BigInteger(),
                sa.ForeignKey("vehicles.id", ondelete="SET NULL"),
                nullable=True,
            ),
        ),
    )
    op.add_column(
        "ride_requests", sa.Column("pickup_latitude", sa.Float(), nullable=False)
    )

    op.add_column(
        "ride_requests", sa.Column("pickup_longitude", sa.Float(), nullable=False)
    )
    op.add_column(
        "ride_requests", sa.Column("drop_off_latitude", sa.Float(), nullable=False)
    )
    op.add_column(
        "ride_requests", sa.Column("drop_off_longitude", sa.Float(), nullable=False)
    )
