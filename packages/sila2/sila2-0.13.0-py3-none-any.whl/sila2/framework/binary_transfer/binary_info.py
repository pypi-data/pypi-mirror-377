import dataclasses
import datetime


@dataclasses.dataclass
class BinaryInfo:
    """
    Additional information about a binary transfer.

    Attributes
    ----------
    binary_size : int
        The size of the total binary payload in bytes.
    lifetime_of_binary : datetime.timedelta
        The duration for which the binary transfer is valid.
    """

    binary_size: int
    lifetime_of_binary: datetime.timedelta
