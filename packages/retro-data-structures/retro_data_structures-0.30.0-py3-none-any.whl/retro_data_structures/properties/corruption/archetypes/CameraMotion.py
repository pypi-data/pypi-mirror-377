# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.Convergence import Convergence

if typing.TYPE_CHECKING:
    class CameraMotionJson(typing_extensions.TypedDict):
        motion_type: json_util.JsonObject
        collision_type: int
    

@dataclasses.dataclass()
class CameraMotion(BaseProperty):
    motion_type: Convergence = dataclasses.field(default_factory=Convergence, metadata={
        'reflection': FieldReflection[Convergence](
            Convergence, id=0xc1547af3, original_name='MotionType', from_json=Convergence.from_json, to_json=Convergence.to_json
        ),
    })
    collision_type: int = dataclasses.field(default=2969932169, metadata={
        'reflection': FieldReflection[int](
            int, id=0xb674ea3d, original_name='CollisionType'
        ),
    })  # Choice

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
        if property_count != 2:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc1547af3
        motion_type = Convergence.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb674ea3d
        collision_type = struct.unpack(">L", data.read(4))[0]
    
        return cls(motion_type, collision_type)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x02')  # 2 properties

        data.write(b'\xc1Tz\xf3')  # 0xc1547af3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.motion_type.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb6t\xea=')  # 0xb674ea3d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.collision_type))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CameraMotionJson", data)
        return cls(
            motion_type=Convergence.from_json(json_data['motion_type']),
            collision_type=json_data['collision_type'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'motion_type': self.motion_type.to_json(),
            'collision_type': self.collision_type,
        }


def _decode_collision_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack(">L", data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xc1547af3: ('motion_type', Convergence.from_stream),
    0xb674ea3d: ('collision_type', _decode_collision_type),
}
