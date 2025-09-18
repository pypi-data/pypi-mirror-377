from plexus.msgs import plexus_common_pb2 as _plexus_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Transform2(_message.Message):
    __slots__ = ("translation", "rotation")
    TRANSLATION_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    translation: _plexus_common_pb2.Vector2
    rotation: _plexus_common_pb2.Matrix2
    def __init__(self, translation: _Optional[_Union[_plexus_common_pb2.Vector2, _Mapping]] = ..., rotation: _Optional[_Union[_plexus_common_pb2.Matrix2, _Mapping]] = ...) -> None: ...

class Transform3(_message.Message):
    __slots__ = ("translation", "rotation")
    TRANSLATION_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    translation: _plexus_common_pb2.Vector3
    rotation: _plexus_common_pb2.Matrix3
    def __init__(self, translation: _Optional[_Union[_plexus_common_pb2.Vector3, _Mapping]] = ..., rotation: _Optional[_Union[_plexus_common_pb2.Matrix3, _Mapping]] = ...) -> None: ...

class Pose(_message.Message):
    __slots__ = ("position", "orientation")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    position: _plexus_common_pb2.Vector3
    orientation: _plexus_common_pb2.Vector4
    def __init__(self, position: _Optional[_Union[_plexus_common_pb2.Vector3, _Mapping]] = ..., orientation: _Optional[_Union[_plexus_common_pb2.Vector4, _Mapping]] = ...) -> None: ...

class Twist(_message.Message):
    __slots__ = ("linear", "angular")
    LINEAR_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_FIELD_NUMBER: _ClassVar[int]
    linear: _plexus_common_pb2.Vector3
    angular: _plexus_common_pb2.Vector3
    def __init__(self, linear: _Optional[_Union[_plexus_common_pb2.Vector3, _Mapping]] = ..., angular: _Optional[_Union[_plexus_common_pb2.Vector3, _Mapping]] = ...) -> None: ...

class Box2(_message.Message):
    __slots__ = ("transform", "size")
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    transform: Transform2
    size: _plexus_common_pb2.Vector2
    def __init__(self, transform: _Optional[_Union[Transform2, _Mapping]] = ..., size: _Optional[_Union[_plexus_common_pb2.Vector2, _Mapping]] = ...) -> None: ...

class Box3(_message.Message):
    __slots__ = ("transform", "size")
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    transform: Transform3
    size: _plexus_common_pb2.Vector3
    def __init__(self, transform: _Optional[_Union[Transform3, _Mapping]] = ..., size: _Optional[_Union[_plexus_common_pb2.Vector3, _Mapping]] = ...) -> None: ...

class Rectangle(_message.Message):
    __slots__ = ("transform", "size")
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    transform: Transform2
    size: _plexus_common_pb2.Vector2
    def __init__(self, transform: _Optional[_Union[Transform2, _Mapping]] = ..., size: _Optional[_Union[_plexus_common_pb2.Vector2, _Mapping]] = ...) -> None: ...

class Circle(_message.Message):
    __slots__ = ("transform", "radius")
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    transform: Transform2
    radius: float
    def __init__(self, transform: _Optional[_Union[Transform2, _Mapping]] = ..., radius: _Optional[float] = ...) -> None: ...

class Ellipse(_message.Message):
    __slots__ = ("transform", "radii")
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    RADII_FIELD_NUMBER: _ClassVar[int]
    transform: Transform2
    radii: _plexus_common_pb2.Vector2
    def __init__(self, transform: _Optional[_Union[Transform2, _Mapping]] = ..., radii: _Optional[_Union[_plexus_common_pb2.Vector2, _Mapping]] = ...) -> None: ...

class Cuboid(_message.Message):
    __slots__ = ("transform", "size")
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    transform: Transform3
    size: _plexus_common_pb2.Vector3
    def __init__(self, transform: _Optional[_Union[Transform3, _Mapping]] = ..., size: _Optional[_Union[_plexus_common_pb2.Vector3, _Mapping]] = ...) -> None: ...

class Sphere(_message.Message):
    __slots__ = ("transform", "radius")
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    transform: Transform3
    radius: float
    def __init__(self, transform: _Optional[_Union[Transform3, _Mapping]] = ..., radius: _Optional[float] = ...) -> None: ...

class Ellipsoid(_message.Message):
    __slots__ = ("transform", "radii")
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    RADII_FIELD_NUMBER: _ClassVar[int]
    transform: Transform3
    radii: _plexus_common_pb2.Vector3
    def __init__(self, transform: _Optional[_Union[Transform3, _Mapping]] = ..., radii: _Optional[_Union[_plexus_common_pb2.Vector3, _Mapping]] = ...) -> None: ...

class Polygon2(_message.Message):
    __slots__ = ("transform", "points")
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    transform: Transform3
    points: _containers.RepeatedCompositeFieldContainer[_plexus_common_pb2.Vector2]
    def __init__(self, transform: _Optional[_Union[Transform3, _Mapping]] = ..., points: _Optional[_Iterable[_Union[_plexus_common_pb2.Vector2, _Mapping]]] = ...) -> None: ...

class Polygon3(_message.Message):
    __slots__ = ("transform", "points")
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    transform: Transform3
    points: _containers.RepeatedCompositeFieldContainer[_plexus_common_pb2.Vector3]
    def __init__(self, transform: _Optional[_Union[Transform3, _Mapping]] = ..., points: _Optional[_Iterable[_Union[_plexus_common_pb2.Vector3, _Mapping]]] = ...) -> None: ...
