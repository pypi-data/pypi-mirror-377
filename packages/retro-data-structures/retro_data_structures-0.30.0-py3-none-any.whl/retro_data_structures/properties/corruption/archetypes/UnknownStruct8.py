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
from retro_data_structures.properties.corruption.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.corruption.archetypes.PlasmaBeamInfo import PlasmaBeamInfo

if typing.TYPE_CHECKING:
    class UnknownStruct8Json(typing_extensions.TypedDict):
        beam_info: json_util.JsonObject
        damage: json_util.JsonObject
        attack_duration: float
        unknown_0x47cde539: float
        turn_speed: float
        unknown_0x82bd3b10: float
        acceleration_time: float
        min_fire_dist: float
        max_fire_dist: float
    

@dataclasses.dataclass()
class UnknownStruct8(BaseProperty):
    beam_info: PlasmaBeamInfo = dataclasses.field(default_factory=PlasmaBeamInfo, metadata={
        'reflection': FieldReflection[PlasmaBeamInfo](
            PlasmaBeamInfo, id=0x1598012a, original_name='BeamInfo', from_json=PlasmaBeamInfo.from_json, to_json=PlasmaBeamInfo.to_json
        ),
    })
    damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x337f9524, original_name='Damage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    attack_duration: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x16342c18, original_name='AttackDuration'
        ),
    })
    unknown_0x47cde539: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x47cde539, original_name='Unknown'
        ),
    })
    turn_speed: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x020c78bb, original_name='TurnSpeed'
        ),
    })
    unknown_0x82bd3b10: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x82bd3b10, original_name='Unknown'
        ),
    })
    acceleration_time: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1a1a315a, original_name='AccelerationTime'
        ),
    })
    min_fire_dist: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x700771b7, original_name='MinFireDist'
        ),
    })
    max_fire_dist: float = dataclasses.field(default=75.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x21fecaea, original_name='MaxFireDist'
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
        if property_count != 9:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1598012a
        beam_info = PlasmaBeamInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x337f9524
        damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x16342c18
        attack_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x47cde539
        unknown_0x47cde539 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x020c78bb
        turn_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x82bd3b10
        unknown_0x82bd3b10 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a1a315a
        acceleration_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x700771b7
        min_fire_dist = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x21fecaea
        max_fire_dist = struct.unpack('>f', data.read(4))[0]
    
        return cls(beam_info, damage, attack_duration, unknown_0x47cde539, turn_speed, unknown_0x82bd3b10, acceleration_time, min_fire_dist, max_fire_dist)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\t')  # 9 properties

        data.write(b'\x15\x98\x01*')  # 0x1598012a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.beam_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'3\x7f\x95$')  # 0x337f9524
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x164,\x18')  # 0x16342c18
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_duration))

        data.write(b'G\xcd\xe59')  # 0x47cde539
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x47cde539))

        data.write(b'\x02\x0cx\xbb')  # 0x20c78bb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.turn_speed))

        data.write(b'\x82\xbd;\x10')  # 0x82bd3b10
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x82bd3b10))

        data.write(b'\x1a\x1a1Z')  # 0x1a1a315a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.acceleration_time))

        data.write(b'p\x07q\xb7')  # 0x700771b7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_fire_dist))

        data.write(b'!\xfe\xca\xea')  # 0x21fecaea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_fire_dist))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct8Json", data)
        return cls(
            beam_info=PlasmaBeamInfo.from_json(json_data['beam_info']),
            damage=DamageInfo.from_json(json_data['damage']),
            attack_duration=json_data['attack_duration'],
            unknown_0x47cde539=json_data['unknown_0x47cde539'],
            turn_speed=json_data['turn_speed'],
            unknown_0x82bd3b10=json_data['unknown_0x82bd3b10'],
            acceleration_time=json_data['acceleration_time'],
            min_fire_dist=json_data['min_fire_dist'],
            max_fire_dist=json_data['max_fire_dist'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'beam_info': self.beam_info.to_json(),
            'damage': self.damage.to_json(),
            'attack_duration': self.attack_duration,
            'unknown_0x47cde539': self.unknown_0x47cde539,
            'turn_speed': self.turn_speed,
            'unknown_0x82bd3b10': self.unknown_0x82bd3b10,
            'acceleration_time': self.acceleration_time,
            'min_fire_dist': self.min_fire_dist,
            'max_fire_dist': self.max_fire_dist,
        }


def _decode_attack_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x47cde539(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_turn_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x82bd3b10(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_acceleration_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_fire_dist(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_fire_dist(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x1598012a: ('beam_info', PlasmaBeamInfo.from_stream),
    0x337f9524: ('damage', DamageInfo.from_stream),
    0x16342c18: ('attack_duration', _decode_attack_duration),
    0x47cde539: ('unknown_0x47cde539', _decode_unknown_0x47cde539),
    0x20c78bb: ('turn_speed', _decode_turn_speed),
    0x82bd3b10: ('unknown_0x82bd3b10', _decode_unknown_0x82bd3b10),
    0x1a1a315a: ('acceleration_time', _decode_acceleration_time),
    0x700771b7: ('min_fire_dist', _decode_min_fire_dist),
    0x21fecaea: ('max_fire_dist', _decode_max_fire_dist),
}
