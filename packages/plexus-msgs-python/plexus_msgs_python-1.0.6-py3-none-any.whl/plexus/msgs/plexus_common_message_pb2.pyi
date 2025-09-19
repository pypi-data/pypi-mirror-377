from plexus.msgs import plexus_common_pb2 as _plexus_common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MessageHeader(_message.Message):
    __slots__ = ("timestamp", "frame_id", "device_uid", "topic_name", "payload_type")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FRAME_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_UID_FIELD_NUMBER: _ClassVar[int]
    TOPIC_NAME_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _plexus_common_pb2.Timestamp
    frame_id: int
    device_uid: str
    topic_name: str
    payload_type: str
    def __init__(self, timestamp: _Optional[_Union[_plexus_common_pb2.Timestamp, _Mapping]] = ..., frame_id: _Optional[int] = ..., device_uid: _Optional[str] = ..., topic_name: _Optional[str] = ..., payload_type: _Optional[str] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ("header", "payload")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    payload: bytes
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ..., payload: _Optional[bytes] = ...) -> None: ...
