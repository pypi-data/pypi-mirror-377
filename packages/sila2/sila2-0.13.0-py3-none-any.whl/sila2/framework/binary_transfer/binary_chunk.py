import dataclasses
import datetime


@dataclasses.dataclass
class BinaryChunk:
    """
    One chunk of the overall binary payload.

    Attributes
    ----------
    binary_transfer_uuid : str
        Uniquely identifies a binary transfer request.
    offset : int
        The offset of the chunk in the overall payload in bytes.
    payload: bytes
        The payload data of this chunk.
    lifetime_of_binary : datetime.timedelta
        The duration for which the binary transfer is valid.
    """

    binary_transfer_uuid: str
    offset: int
    payload: bytes
    lifetime_of_binary: datetime.timedelta
