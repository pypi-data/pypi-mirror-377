import msgpack
from typing import Union, List, Dict
import datetime

SerializableKey = Union[str, bytes, int]

SerializableType = Union[
    None,
    bool,
    int,
    float,
    str,
    bytes,
    List["SerializableType"],
    Dict[SerializableKey, "SerializableType"],
    datetime.datetime
]




def serialize(data: SerializableType) -> bytes:
    return msgpack.packb(data, use_bin_type=True, datetime=True)

def deserialize(data: bytes, raw_str: bool = False) -> SerializableType:
    return msgpack.unpackb(data, raw=raw_str, timestamp=3)







