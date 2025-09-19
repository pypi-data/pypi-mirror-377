from plexus.msgs import plexus_common_pb2 as _plexus_common_pb2
from plexus.msgs import plexus_common_message_pb2 as _plexus_common_message_pb2
from plexus.msgs import plexus_common_geom_pb2 as _plexus_common_geom_pb2
from plexus.msgs import plexus_common_entity_pb2 as _plexus_common_entity_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ObstacleDetection(_message.Message):
    __slots__ = ("obstacles",)
    class MonoCameraBox2ObstacleDetection(_message.Message):
        __slots__ = ("detection_uid", "camera_message_header", "image_box2", "obstacle_type", "properties")
        DETECTION_UID_FIELD_NUMBER: _ClassVar[int]
        CAMERA_MESSAGE_HEADER_FIELD_NUMBER: _ClassVar[int]
        IMAGE_BOX2_FIELD_NUMBER: _ClassVar[int]
        OBSTACLE_TYPE_FIELD_NUMBER: _ClassVar[int]
        PROPERTIES_FIELD_NUMBER: _ClassVar[int]
        detection_uid: str
        camera_message_header: _plexus_common_message_pb2.MessageHeader
        image_box2: _plexus_common_geom_pb2.Box2
        obstacle_type: _plexus_common_entity_pb2.Obstacle.ObstacleTypeEnum
        properties: _containers.RepeatedCompositeFieldContainer[_plexus_common_pb2.KeyValue]
        def __init__(self, detection_uid: _Optional[str] = ..., camera_message_header: _Optional[_Union[_plexus_common_message_pb2.MessageHeader, _Mapping]] = ..., image_box2: _Optional[_Union[_plexus_common_geom_pb2.Box2, _Mapping]] = ..., obstacle_type: _Optional[_Union[_plexus_common_entity_pb2.Obstacle.ObstacleTypeEnum, str]] = ..., properties: _Optional[_Iterable[_Union[_plexus_common_pb2.KeyValue, _Mapping]]] = ...) -> None: ...
    class StereoCameraBox2ObstacleDetection(_message.Message):
        __slots__ = ("detection_uid", "left_camera_message_header", "right_camera_message_header", "left_image_box2", "right_image_box2", "obstacle_type", "properties")
        DETECTION_UID_FIELD_NUMBER: _ClassVar[int]
        LEFT_CAMERA_MESSAGE_HEADER_FIELD_NUMBER: _ClassVar[int]
        RIGHT_CAMERA_MESSAGE_HEADER_FIELD_NUMBER: _ClassVar[int]
        LEFT_IMAGE_BOX2_FIELD_NUMBER: _ClassVar[int]
        RIGHT_IMAGE_BOX2_FIELD_NUMBER: _ClassVar[int]
        OBSTACLE_TYPE_FIELD_NUMBER: _ClassVar[int]
        PROPERTIES_FIELD_NUMBER: _ClassVar[int]
        detection_uid: str
        left_camera_message_header: _plexus_common_message_pb2.MessageHeader
        right_camera_message_header: _plexus_common_message_pb2.MessageHeader
        left_image_box2: _plexus_common_geom_pb2.Box2
        right_image_box2: _plexus_common_geom_pb2.Box2
        obstacle_type: _plexus_common_entity_pb2.Obstacle.ObstacleTypeEnum
        properties: _containers.RepeatedCompositeFieldContainer[_plexus_common_pb2.KeyValue]
        def __init__(self, detection_uid: _Optional[str] = ..., left_camera_message_header: _Optional[_Union[_plexus_common_message_pb2.MessageHeader, _Mapping]] = ..., right_camera_message_header: _Optional[_Union[_plexus_common_message_pb2.MessageHeader, _Mapping]] = ..., left_image_box2: _Optional[_Union[_plexus_common_geom_pb2.Box2, _Mapping]] = ..., right_image_box2: _Optional[_Union[_plexus_common_geom_pb2.Box2, _Mapping]] = ..., obstacle_type: _Optional[_Union[_plexus_common_entity_pb2.Obstacle.ObstacleTypeEnum, str]] = ..., properties: _Optional[_Iterable[_Union[_plexus_common_pb2.KeyValue, _Mapping]]] = ...) -> None: ...
    class LidarBox3ObstacleDetection(_message.Message):
        __slots__ = ("detection_uid", "lidar_message_header", "world_box3", "obstacle_type", "properties")
        DETECTION_UID_FIELD_NUMBER: _ClassVar[int]
        LIDAR_MESSAGE_HEADER_FIELD_NUMBER: _ClassVar[int]
        WORLD_BOX3_FIELD_NUMBER: _ClassVar[int]
        OBSTACLE_TYPE_FIELD_NUMBER: _ClassVar[int]
        PROPERTIES_FIELD_NUMBER: _ClassVar[int]
        detection_uid: str
        lidar_message_header: _plexus_common_message_pb2.MessageHeader
        world_box3: _plexus_common_geom_pb2.Box3
        obstacle_type: _plexus_common_entity_pb2.Obstacle.ObstacleTypeEnum
        properties: _containers.RepeatedCompositeFieldContainer[_plexus_common_pb2.KeyValue]
        def __init__(self, detection_uid: _Optional[str] = ..., lidar_message_header: _Optional[_Union[_plexus_common_message_pb2.MessageHeader, _Mapping]] = ..., world_box3: _Optional[_Union[_plexus_common_geom_pb2.Box3, _Mapping]] = ..., obstacle_type: _Optional[_Union[_plexus_common_entity_pb2.Obstacle.ObstacleTypeEnum, str]] = ..., properties: _Optional[_Iterable[_Union[_plexus_common_pb2.KeyValue, _Mapping]]] = ...) -> None: ...
    class ObstacleDetectionVariant(_message.Message):
        __slots__ = ("mono_camera_box2", "stereo_camera_box2", "lidar_box3")
        MONO_CAMERA_BOX2_FIELD_NUMBER: _ClassVar[int]
        STEREO_CAMERA_BOX2_FIELD_NUMBER: _ClassVar[int]
        LIDAR_BOX3_FIELD_NUMBER: _ClassVar[int]
        mono_camera_box2: ObstacleDetection.MonoCameraBox2ObstacleDetection
        stereo_camera_box2: ObstacleDetection.StereoCameraBox2ObstacleDetection
        lidar_box3: ObstacleDetection.LidarBox3ObstacleDetection
        def __init__(self, mono_camera_box2: _Optional[_Union[ObstacleDetection.MonoCameraBox2ObstacleDetection, _Mapping]] = ..., stereo_camera_box2: _Optional[_Union[ObstacleDetection.StereoCameraBox2ObstacleDetection, _Mapping]] = ..., lidar_box3: _Optional[_Union[ObstacleDetection.LidarBox3ObstacleDetection, _Mapping]] = ...) -> None: ...
    class Obstacle(_message.Message):
        __slots__ = ("obstacle_uid", "detections", "world_box3", "obstacle_type", "properties")
        OBSTACLE_UID_FIELD_NUMBER: _ClassVar[int]
        DETECTIONS_FIELD_NUMBER: _ClassVar[int]
        WORLD_BOX3_FIELD_NUMBER: _ClassVar[int]
        OBSTACLE_TYPE_FIELD_NUMBER: _ClassVar[int]
        PROPERTIES_FIELD_NUMBER: _ClassVar[int]
        obstacle_uid: str
        detections: _containers.RepeatedCompositeFieldContainer[ObstacleDetection.ObstacleDetectionVariant]
        world_box3: _plexus_common_geom_pb2.Box3
        obstacle_type: _plexus_common_entity_pb2.Obstacle.ObstacleTypeEnum
        properties: _containers.RepeatedCompositeFieldContainer[_plexus_common_pb2.KeyValue]
        def __init__(self, obstacle_uid: _Optional[str] = ..., detections: _Optional[_Iterable[_Union[ObstacleDetection.ObstacleDetectionVariant, _Mapping]]] = ..., world_box3: _Optional[_Union[_plexus_common_geom_pb2.Box3, _Mapping]] = ..., obstacle_type: _Optional[_Union[_plexus_common_entity_pb2.Obstacle.ObstacleTypeEnum, str]] = ..., properties: _Optional[_Iterable[_Union[_plexus_common_pb2.KeyValue, _Mapping]]] = ...) -> None: ...
    OBSTACLES_FIELD_NUMBER: _ClassVar[int]
    obstacles: _containers.RepeatedCompositeFieldContainer[ObstacleDetection.Obstacle]
    def __init__(self, obstacles: _Optional[_Iterable[_Union[ObstacleDetection.Obstacle, _Mapping]]] = ...) -> None: ...
