import ctypes
import enum
import json
from typing import List

import numpy as np


class Object(ctypes.LittleEndianStructure):
    """
    Single object data structure

    単一オブジェクトのデータ構造
    """

    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("vx", ctypes.c_float),
        ("vy", ctypes.c_float),
        ("length", ctypes.c_float),
        ("width", ctypes.c_float),
        ("height", ctypes.c_float),
        ("theta", ctypes.c_float),
        ("classification", ctypes.c_uint32),
        ("object_id", ctypes.c_uint32),
    ]


class ObjectsHeader(ctypes.LittleEndianStructure):
    """
    Header portion of the Objects frame

    Objectsフレームのヘッダー部分
    """

    _fields_ = [
        ("magic", ctypes.c_char * 4),  # "COBJ" - マジック番号
        ("num_objects", ctypes.c_uint32),  # オブジェクト数
        ("sequence_id", ctypes.c_uint32),  # シーケンスID
    ]


class Objects(ctypes.LittleEndianStructure):
    """
    Complete Objects frame structure

    完全なObjectsフレーム構造
    """

    _fields_ = [
        ("magic", ctypes.c_char * 4),  # "COBJ" - マジック番号
        ("num_objects", ctypes.c_uint32),  # オブジェクト数
        ("sequence_id", ctypes.c_uint32),  # シーケンスID
        # Note: objects array needs to be handled separately due to dynamic size
        # 注意: オブジェクト配列は動的サイズのため別途処理が必要
    ]

    def __init__(self, num_objects: int = 0):
        super().__init__()
        self.magic = b"COBJ"
        self.num_objects = num_objects
        self.sequence_id = 0

    @classmethod
    def from_bytes(cls, data: bytes):
        """
        Parse Objects frame from binary data

        バイナリデータからObjectsフレームをパースします
        """
        # Parse header first
        # 最初にヘッダーをパースします
        header = ObjectsHeader.from_buffer_copy(data[: ctypes.sizeof(ObjectsHeader)])

        if header.magic != b"COBJ":
            raise ValueError(f"Invalid magic: {header.magic}")

        # Create Objects instance
        # Objectsインスタンスを作成します
        objects_frame = cls(header.num_objects)
        objects_frame.sequence_id = header.sequence_id

        # Parse objects array
        # オブジェクト配列をパースします
        objects_start = ctypes.sizeof(ObjectsHeader)
        object_size = ctypes.sizeof(Object)
        objects_data = []

        for i in range(header.num_objects):
            offset = objects_start + (i * object_size)
            obj_bytes = data[offset : offset + object_size]
            obj = Object.from_buffer_copy(obj_bytes)
            objects_data.append(obj)

        objects_frame.objects = objects_data
        return objects_frame

    def to_bytes(self) -> bytes:
        """
        Serialize Objects frame to binary data

        Objectsフレームをバイナリデータにシリアライズします
        """
        # Create header
        # ヘッダーを作成します
        header_data = bytes(self)

        # Serialize objects
        # オブジェクトをシリアライズします
        objects_data = b""
        for obj in getattr(self, "objects", []):
            objects_data += bytes(obj)

        return header_data + objects_data


class _CloudClass(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("magic", ctypes.c_char * 4),
        ("sequence_id", ctypes.c_uint32),
        ("num_points", ctypes.c_uint32),
        # Note: positions array needs to be handled separately due to dynamic size
    ]

    def __init__(self, data: bytes):
        super().__init__()

        header_size = ctypes.sizeof(self)
        ctypes.memmove(ctypes.addressof(self), data[:header_size], header_size)

        if self.magic != self._token:
            raise ValueError(f"Invalid magic: {self.magic}")

        # Parse points as a numpy array
        positions_data = data[header_size:]
        self.positions = np.frombuffer(positions_data, dtype="f4").reshape(-1, 3)

    def to_bytes(self) -> bytes:
        """Serialize the GroundCloud to bytes"""
        # Create header
        header_data = bytes(self)

        # Serialize positions
        position_data = b""
        for pos in getattr(self, "positions", []):
            position_data += bytes(pos)

        return header_data + position_data


class ForegroundCloud(_CloudClass):
    _token = b"FGCL"


class BackgroundCloud(_CloudClass):
    _token = b"BGCL"


class GroundCloud(_CloudClass):
    _token = b"GRCL"


class BaseCloud(_CloudClass):
    _token = b"HCLD"


class ZoneType(enum.Enum):
    """
    Zone type enumeration.

    ゾーンの種類。
    """

    Event = enum.auto()  # Detect debris inside
    Exclusion = enum.auto()  # Exclude points inside from detection
    Inclusion = enum.auto()  # Exclude points OUTSIDE from detection


class Zone:
    """
    Zone data structure.

    ゾーンの定義。
    """

    def __init__(self, name: str, points: List[List[float]], type: ZoneType):
        self.name = name
        self.points = points
        self.type = type

    @classmethod
    def from_dict(cls, data: dict) -> "Zone":
        """Create a Zone instance from a dict."""
        return cls(
            name=data["name"],
            points=data["points"],
            type=ZoneType[data["type"]],
        )


class ZoneSettings:
    """
    Zone settings data structure

    ゾーン設定。
    """

    _token = "ZONE"

    def __init__(self, zones: List[Zone]):
        self.zones = zones

    @classmethod
    def from_str(cls, data: str) -> "ZoneSettings":
        """Create a ZoneSettings instance from a JSON string."""
        payload = json.loads(data)
        zones = [Zone.from_dict(zone) for zone in payload]
        return cls(zones)
