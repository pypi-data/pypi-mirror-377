# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.Convergence import Convergence

if typing.TYPE_CHECKING:
    class ColliderPositionJson(typing_extensions.TypedDict):
        collider_position_type: int
        distance: float
        backwards_distance: float
        z_offset: float
        distance_convergence: json_util.JsonObject
        centroid_convergence: json_util.JsonObject
        camera_convergence: json_util.JsonObject
    

class ColliderPositionType(enum.IntEnum):
    Unknown1 = 3074795145

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


@dataclasses.dataclass()
class ColliderPosition(BaseProperty):
    collider_position_type: ColliderPositionType = dataclasses.field(default=ColliderPositionType.Unknown1, metadata={
        'reflection': FieldReflection[ColliderPositionType](
            ColliderPositionType, id=0xe2ae470c, original_name='ColliderPositionType', from_json=ColliderPositionType.from_json, to_json=ColliderPositionType.to_json
        ),
    })
    distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc3bf43be, original_name='Distance'
        ),
    })
    backwards_distance: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe7562bee, original_name='BackwardsDistance'
        ),
    })
    z_offset: float = dataclasses.field(default=2.7360000610351562, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8033f9a3, original_name='ZOffset'
        ),
    })
    distance_convergence: Convergence = dataclasses.field(default_factory=Convergence, metadata={
        'reflection': FieldReflection[Convergence](
            Convergence, id=0xb11d9e90, original_name='DistanceConvergence', from_json=Convergence.from_json, to_json=Convergence.to_json
        ),
    })
    centroid_convergence: Convergence = dataclasses.field(default_factory=Convergence, metadata={
        'reflection': FieldReflection[Convergence](
            Convergence, id=0x81d49c61, original_name='CentroidConvergence', from_json=Convergence.from_json, to_json=Convergence.to_json
        ),
    })
    camera_convergence: Convergence = dataclasses.field(default_factory=Convergence, metadata={
        'reflection': FieldReflection[Convergence](
            Convergence, id=0x51b11f91, original_name='CameraConvergence', from_json=Convergence.from_json, to_json=Convergence.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack(">H", data.read(2))[0]
        if (result := cls._fast_decode(data, property_count)) is not None:
            return result

        present_fields = default_override or {}
        for _ in range(property_count):
            property_id, property_size = struct.unpack(">LH", data.read(6))
            start = data.tell()
            try:
                property_name, decoder = _property_decoder[property_id]
                present_fields[property_name] = decoder(data, property_size)
            except KeyError:
                raise RuntimeError(f"Unknown property: 0x{property_id:08x}")
            assert data.tell() - start == property_size

        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 7:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe2ae470c
        collider_position_type = ColliderPositionType.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3bf43be
        distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe7562bee
        backwards_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8033f9a3
        z_offset = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb11d9e90
        distance_convergence = Convergence.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x81d49c61
        centroid_convergence = Convergence.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x51b11f91
        camera_convergence = Convergence.from_stream(data, property_size)
    
        return cls(collider_position_type, distance, backwards_distance, z_offset, distance_convergence, centroid_convergence, camera_convergence)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'\xe2\xaeG\x0c')  # 0xe2ae470c
        data.write(b'\x00\x04')  # size
        self.collider_position_type.to_stream(data)

        data.write(b'\xc3\xbfC\xbe')  # 0xc3bf43be
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance))

        data.write(b'\xe7V+\xee')  # 0xe7562bee
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.backwards_distance))

        data.write(b'\x803\xf9\xa3')  # 0x8033f9a3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.z_offset))

        data.write(b'\xb1\x1d\x9e\x90')  # 0xb11d9e90
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.distance_convergence.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x81\xd4\x9ca')  # 0x81d49c61
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.centroid_convergence.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'Q\xb1\x1f\x91')  # 0x51b11f91
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.camera_convergence.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ColliderPositionJson", data)
        return cls(
            collider_position_type=ColliderPositionType.from_json(json_data['collider_position_type']),
            distance=json_data['distance'],
            backwards_distance=json_data['backwards_distance'],
            z_offset=json_data['z_offset'],
            distance_convergence=Convergence.from_json(json_data['distance_convergence']),
            centroid_convergence=Convergence.from_json(json_data['centroid_convergence']),
            camera_convergence=Convergence.from_json(json_data['camera_convergence']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'collider_position_type': self.collider_position_type.to_json(),
            'distance': self.distance,
            'backwards_distance': self.backwards_distance,
            'z_offset': self.z_offset,
            'distance_convergence': self.distance_convergence.to_json(),
            'centroid_convergence': self.centroid_convergence.to_json(),
            'camera_convergence': self.camera_convergence.to_json(),
        }


def _decode_collider_position_type(data: typing.BinaryIO, property_size: int) -> ColliderPositionType:
    return ColliderPositionType.from_stream(data)


def _decode_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_backwards_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_z_offset(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xe2ae470c: ('collider_position_type', _decode_collider_position_type),
    0xc3bf43be: ('distance', _decode_distance),
    0xe7562bee: ('backwards_distance', _decode_backwards_distance),
    0x8033f9a3: ('z_offset', _decode_z_offset),
    0xb11d9e90: ('distance_convergence', Convergence.from_stream),
    0x81d49c61: ('centroid_convergence', Convergence.from_stream),
    0x51b11f91: ('camera_convergence', Convergence.from_stream),
}
