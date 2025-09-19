from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LidarScan2D(_message.Message):
    __slots__ = ("ranges", "angles", "qualities", "timestamp_ns", "angle_min", "angle_max", "angle_increment", "time_increment", "scan_time", "range_min", "range_max")
    RANGES_FIELD_NUMBER: _ClassVar[int]
    ANGLES_FIELD_NUMBER: _ClassVar[int]
    QUALITIES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_NS_FIELD_NUMBER: _ClassVar[int]
    ANGLE_MIN_FIELD_NUMBER: _ClassVar[int]
    ANGLE_MAX_FIELD_NUMBER: _ClassVar[int]
    ANGLE_INCREMENT_FIELD_NUMBER: _ClassVar[int]
    TIME_INCREMENT_FIELD_NUMBER: _ClassVar[int]
    SCAN_TIME_FIELD_NUMBER: _ClassVar[int]
    RANGE_MIN_FIELD_NUMBER: _ClassVar[int]
    RANGE_MAX_FIELD_NUMBER: _ClassVar[int]
    ranges: _containers.RepeatedScalarFieldContainer[float]
    angles: _containers.RepeatedScalarFieldContainer[float]
    qualities: _containers.RepeatedScalarFieldContainer[int]
    timestamp_ns: int
    angle_min: float
    angle_max: float
    angle_increment: float
    time_increment: float
    scan_time: float
    range_min: float
    range_max: float
    def __init__(self, ranges: _Optional[_Iterable[float]] = ..., angles: _Optional[_Iterable[float]] = ..., qualities: _Optional[_Iterable[int]] = ..., timestamp_ns: _Optional[int] = ..., angle_min: _Optional[float] = ..., angle_max: _Optional[float] = ..., angle_increment: _Optional[float] = ..., time_increment: _Optional[float] = ..., scan_time: _Optional[float] = ..., range_min: _Optional[float] = ..., range_max: _Optional[float] = ...) -> None: ...

class LidarBatch(_message.Message):
    __slots__ = ("scans",)
    SCANS_FIELD_NUMBER: _ClassVar[int]
    scans: _containers.RepeatedCompositeFieldContainer[LidarScan2D]
    def __init__(self, scans: _Optional[_Iterable[_Union[LidarScan2D, _Mapping]]] = ...) -> None: ...
