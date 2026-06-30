from enum import StrEnum


class UserRoles(StrEnum):
    ADMIN = "ADMIN"
    DRIVER = "DRIVER"
    RIDER = "RIDER"


class RideStatus(StrEnum):
    PENDING = "PENDING"
    DRIVER_ASSIGNED = "DRIVER_ASSIGNED"
    DRIVER_ARRIVING = "DRIVER_ARRIVING"
    DRIVER_ARRIVED = "DRIVER_ARRIVED"
    RIDE_STARTED = "RIDE_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    TIMED_OUT = "TIMED_OUT"
    REJECTED = "REJECTED"


class TransactionType(StrEnum):
    RIDE_PAYMENT = "RIDE_PAYMENT"
    REFUND = "REFUND"
    ADD_FUNDS = "ADD_FUNDS"


class TransactionStatus(StrEnum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


class WalletTransactionType(StrEnum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
