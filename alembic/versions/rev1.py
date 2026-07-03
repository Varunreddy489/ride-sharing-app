import sqlalchemy as sa
from geoalchemy2 import Geography
from sqlalchemy.dialects.postgresql import ENUM

from alembic import op  # type: ignore[attr-defined]

revision = "rev1_rev2_combined"

down_revision = "rev0"
depends_on = None
branch_labels = None

USER_ROLES_ENUM = ENUM("ADMIN", "DRIVER", "RIDER", name="user_roles", create_type=False)

RIDE_STATUS_ENUM = ENUM(
    "PENDING",
    "DRIVER_ASSIGNED",
    "DRIVER_ARRIVING",
    "DRIVER_ARRIVED",
    "RIDE_STARTED",
    "IN_PROGRESS",
    "COMPLETED",
    "CANCELED",
    "REJECTED",
    "TIMED_OUT",
    name="ride_status",
    create_type=False,
)

TRANSACTION_TYPE_ENUM = ENUM(
    "RIDE_PAYMENT",
    "REFUND",
    "ADD_FUNDS",
    name="transaction_type",
    create_type=False,
)

TRANSACTIONS_STATUS_ENUM = ENUM(
    "PROCESSING",
    "COMPLETED",
    "FAILED",
    "TIMED_OUT",
    name="transactions_status",
    create_type=False,
)

WALLET_TRANSACTION_TYPE_ENUM = ENUM(
    "CREDIT",
    "DEBIT",
    name="wallet_transaction_type",
    create_type=False,
)

ENUM_TYPES = (
    USER_ROLES_ENUM,
    RIDE_STATUS_ENUM,
    TRANSACTION_TYPE_ENUM,
    TRANSACTIONS_STATUS_ENUM,
    WALLET_TRANSACTION_TYPE_ENUM,
)

CREATED_INDEXES = (
    ("ix_wallet_transactions_status", "wallet_transactions"),
    ("ix_wallet_transactions_wallet_id", "wallet_transactions"),
    ("ix_payments_transaction_status", "payments"),
    ("ix_ride_events_ride_request_id", "ride_events"),
    ("ix_ride_requests_active", "ride_requests"),
    ("ix_ride_requests_status", "ride_requests"),
    ("ix_ride_requests_driver_id", "ride_requests"),
    ("ix_ride_requests_rider_id", "ride_requests"),
)

CREATED_TABLES = (
    "wallet_transactions",
    "wallets",
    "payments",
    "ride_events",
    "ride_requests",
    "vehicles",
    "drivers",
    "users",
    "driver_locations",
)


def upgrade() -> None:
    bind = op.get_bind()
    # Ensure PostGIS is available
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Create ENUM types first
    for enum_type in ENUM_TYPES:
        enum_type.create(bind, checkfirst=True)

    # Users table
    op.create_table(
        "users",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True, nullable=False
        ),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("phone_number", sa.String, nullable=False),
        sa.Column("password", sa.String, nullable=False),
        sa.Column("role", USER_ROLES_ENUM, nullable=False, server_default="RIDER"),
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
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("phone_number", name="uq_users_phone_number"),
    )

    # Drivers table
    op.create_table(
        "drivers",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True, nullable=False
        ),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("license_number", sa.String, nullable=False),
        sa.Column("is_online", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column(
            "is_available", sa.Boolean, nullable=False, server_default=sa.false()
        ),
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
        sa.UniqueConstraint("user_id", name="uq_drivers_user_id"),
        sa.UniqueConstraint("license_number", name="uq_drivers_license_number"),
    )

    # Vehicles table
    op.create_table(
        "vehicles",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True, nullable=False
        ),
        sa.Column(
            "driver_id",
            sa.BigInteger(),
            sa.ForeignKey("drivers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("capacity", sa.Integer, nullable=False),
        sa.Column("license_plate", sa.String, nullable=False),
        sa.UniqueConstraint("license_plate", name="uq_vehicles_license_plate"),
        sa.CheckConstraint("capacity > 0", name="chk_vehicles_capacity"),
    )

    # Ride requests: use PostGIS Geography POINT columns for pickup and dropoff
    op.create_table(
        "ride_requests",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True, nullable=False
        ),
        sa.Column("lock_version", sa.Integer, nullable=False),
        sa.Column(
            "rider_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "driver_id", sa.BigInteger(), sa.ForeignKey("drivers.id"), nullable=True
        ),
        # store as geography POINT (lon, lat) with SRID 4326 so you can store values like 17.3616 N, 78.4747 E
        sa.Column(
            "pickup_point",
            nullable=False,
        ),
        sa.Column(
            "dropoff_point",
            Geography(geometry_type="POINT", srid=4326),
            nullable=False,
        ),
        sa.Column("status", RIDE_STATUS_ENUM, nullable=False, server_default="PENDING"),
        sa.Column("fare", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.String, nullable=True),
        sa.Column("distance_km", sa.Float, nullable=True),
        sa.Column("duration_minutes", sa.Float, nullable=True),
        sa.CheckConstraint("fare IS NULL OR fare >= 0", name="chk_ride_fare"),
        sa.Column(
            "vehicle_id",
            sa.BigInteger(),
            sa.ForeignKey("vehicles.id", ondelete="SET NULL"),
            nullable=True,
        ),
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

    op.create_index("ix_ride_requests_active", "ride_requests", ["rider_id", "status"])
    op.create_index("ix_ride_requests_rider_id", "ride_requests", ["rider_id"])
    op.create_index("ix_ride_requests_driver_id", "ride_requests", ["driver_id"])
    op.create_index("ix_ride_requests_status", "ride_requests", ["status"])

    # Payments
    op.create_table(
        "payments",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True, nullable=False
        ),
        sa.Column(
            "ride_request_id",
            sa.BigInteger(),
            sa.ForeignKey("ride_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("transaction_type", TRANSACTION_TYPE_ENUM, nullable=False),
        sa.Column(
            "transaction_status",
            TRANSACTIONS_STATUS_ENUM,
            nullable=False,
            server_default="PROCESSING",
        ),
        sa.CheckConstraint("amount>0", name="chk_payments_amount"),
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

    op.create_index(
        "ix_payments_transaction_status", "payments", ["transaction_status"]
    )

    # Wallets
    op.create_table(
        "wallets",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True, nullable=False
        ),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "balance",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="0.0",
        ),
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
        sa.CheckConstraint("balance >= 0", name="chk_wallet_balance"),
        sa.UniqueConstraint("user_id", name="uq_wallets_user_id"),
    )

    # Wallet transactions
    op.create_table(
        "wallet_transactions",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True, nullable=False
        ),
        sa.Column(
            "wallet_id",
            sa.BigInteger(),
            sa.ForeignKey("wallets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("transaction_type", WALLET_TRANSACTION_TYPE_ENUM, nullable=False),
        sa.Column(
            "transaction_status",
            TRANSACTIONS_STATUS_ENUM,
            nullable=False,
            server_default="PROCESSING",
        ),
        sa.CheckConstraint("amount>0", name="chk_wallet_transactions_amount"),
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

    op.create_index(
        "ix_wallet_transactions_wallet_id", "wallet_transactions", ["wallet_id"]
    )

    op.create_index(
        "ix_wallet_transactions_status", "wallet_transactions", ["transaction_status"]
    )

    # Driver locations: use a single geography point column instead of lat/long
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
        sa.Column(
            "location",
            Geography(geometry_type="POINT", srid=4326),
            nullable=False,
        ),
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


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS postgis")

    # Drop indexes
    for index_name, table_name in CREATED_INDEXES:
        op.drop_index(index_name, table_name=table_name, if_exists=True)

    # Drop tables (if_exists to be safe)
    for table_name in CREATED_TABLES:
        op.drop_table(table_name, if_exists=True)

    # Drop enum types
    bind = op.get_bind()
    for enum_type in reversed(ENUM_TYPES):
        enum_type.drop(bind, checkfirst=True)
