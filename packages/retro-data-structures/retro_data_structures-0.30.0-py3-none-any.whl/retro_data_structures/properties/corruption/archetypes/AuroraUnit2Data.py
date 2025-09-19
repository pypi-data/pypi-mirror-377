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
from retro_data_structures.properties.corruption.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.corruption.archetypes.UnknownStruct11 import UnknownStruct11
from retro_data_structures.properties.corruption.archetypes.UnknownStruct12 import UnknownStruct12
from retro_data_structures.properties.corruption.archetypes.UnknownStruct13 import UnknownStruct13
from retro_data_structures.properties.corruption.archetypes.UnknownStruct14 import UnknownStruct14
from retro_data_structures.properties.corruption.archetypes.UnknownStruct7 import UnknownStruct7

if typing.TYPE_CHECKING:
    class AuroraUnit2DataJson(typing_extensions.TypedDict):
        unknown_0x0a072c48: float
        unknown_0xdde5ac10: float
        flight_max_speed: float
        flight_acceleration: float
        flight_deceleration: float
        dodge_time: float
        dodge_time_variance: float
        dodge_chance: float
        unknown_0xefd78a41: float
        hover_height: float
        min_follow_distance: float
        max_follow_distance: float
        initial_attack_time: float
        attack_time: float
        attack_time_variance: float
        unknown_0x059b46cf: float
        unknown_0x1aa98d7f: float
        junction_vulnerability: json_util.JsonObject
        unknown_struct7: json_util.JsonObject
        unknown_struct11: json_util.JsonObject
        unknown_struct12: json_util.JsonObject
        unknown_struct13: json_util.JsonObject
        unknown_struct14: json_util.JsonObject
    

@dataclasses.dataclass()
class AuroraUnit2Data(BaseProperty):
    unknown_0x0a072c48: float = dataclasses.field(default=0.6000000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0a072c48, original_name='Unknown'
        ),
    })
    unknown_0xdde5ac10: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdde5ac10, original_name='Unknown'
        ),
    })
    flight_max_speed: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd4dec629, original_name='FlightMaxSpeed'
        ),
    })
    flight_acceleration: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7a2bb377, original_name='FlightAcceleration'
        ),
    })
    flight_deceleration: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdd14361f, original_name='FlightDeceleration'
        ),
    })
    dodge_time: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x67625bef, original_name='DodgeTime'
        ),
    })
    dodge_time_variance: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x34b97edb, original_name='DodgeTimeVariance'
        ),
    })
    dodge_chance: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x47be3298, original_name='DodgeChance'
        ),
    })
    unknown_0xefd78a41: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xefd78a41, original_name='Unknown'
        ),
    })
    hover_height: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc75998aa, original_name='HoverHeight'
        ),
    })
    min_follow_distance: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x93716a88, original_name='MinFollowDistance'
        ),
    })
    max_follow_distance: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd266550e, original_name='MaxFollowDistance'
        ),
    })
    initial_attack_time: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x446efcad, original_name='InitialAttackTime'
        ),
    })
    attack_time: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdca1e8b6, original_name='AttackTime'
        ),
    })
    attack_time_variance: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9f269614, original_name='AttackTimeVariance'
        ),
    })
    unknown_0x059b46cf: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x059b46cf, original_name='Unknown'
        ),
    })
    unknown_0x1aa98d7f: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1aa98d7f, original_name='Unknown'
        ),
    })
    junction_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xfdd2fe20, original_name='JunctionVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    unknown_struct7: UnknownStruct7 = dataclasses.field(default_factory=UnknownStruct7, metadata={
        'reflection': FieldReflection[UnknownStruct7](
            UnknownStruct7, id=0xc108cfa0, original_name='UnknownStruct7', from_json=UnknownStruct7.from_json, to_json=UnknownStruct7.to_json
        ),
    })
    unknown_struct11: UnknownStruct11 = dataclasses.field(default_factory=UnknownStruct11, metadata={
        'reflection': FieldReflection[UnknownStruct11](
            UnknownStruct11, id=0x91502686, original_name='UnknownStruct11', from_json=UnknownStruct11.from_json, to_json=UnknownStruct11.to_json
        ),
    })
    unknown_struct12: UnknownStruct12 = dataclasses.field(default_factory=UnknownStruct12, metadata={
        'reflection': FieldReflection[UnknownStruct12](
            UnknownStruct12, id=0xad62c993, original_name='UnknownStruct12', from_json=UnknownStruct12.from_json, to_json=UnknownStruct12.to_json
        ),
    })
    unknown_struct13: UnknownStruct13 = dataclasses.field(default_factory=UnknownStruct13, metadata={
        'reflection': FieldReflection[UnknownStruct13](
            UnknownStruct13, id=0x03a319df, original_name='UnknownStruct13', from_json=UnknownStruct13.from_json, to_json=UnknownStruct13.to_json
        ),
    })
    unknown_struct14: UnknownStruct14 = dataclasses.field(default_factory=UnknownStruct14, metadata={
        'reflection': FieldReflection[UnknownStruct14](
            UnknownStruct14, id=0x9dd3bb57, original_name='UnknownStruct14', from_json=UnknownStruct14.from_json, to_json=UnknownStruct14.to_json
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
        if property_count != 23:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0a072c48
        unknown_0x0a072c48 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdde5ac10
        unknown_0xdde5ac10 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd4dec629
        flight_max_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7a2bb377
        flight_acceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdd14361f
        flight_deceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x67625bef
        dodge_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x34b97edb
        dodge_time_variance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x47be3298
        dodge_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xefd78a41
        unknown_0xefd78a41 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc75998aa
        hover_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x93716a88
        min_follow_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd266550e
        max_follow_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x446efcad
        initial_attack_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdca1e8b6
        attack_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9f269614
        attack_time_variance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x059b46cf
        unknown_0x059b46cf = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1aa98d7f
        unknown_0x1aa98d7f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfdd2fe20
        junction_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc108cfa0
        unknown_struct7 = UnknownStruct7.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x91502686
        unknown_struct11 = UnknownStruct11.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad62c993
        unknown_struct12 = UnknownStruct12.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x03a319df
        unknown_struct13 = UnknownStruct13.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9dd3bb57
        unknown_struct14 = UnknownStruct14.from_stream(data, property_size)
    
        return cls(unknown_0x0a072c48, unknown_0xdde5ac10, flight_max_speed, flight_acceleration, flight_deceleration, dodge_time, dodge_time_variance, dodge_chance, unknown_0xefd78a41, hover_height, min_follow_distance, max_follow_distance, initial_attack_time, attack_time, attack_time_variance, unknown_0x059b46cf, unknown_0x1aa98d7f, junction_vulnerability, unknown_struct7, unknown_struct11, unknown_struct12, unknown_struct13, unknown_struct14)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x17')  # 23 properties

        data.write(b'\n\x07,H')  # 0xa072c48
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0a072c48))

        data.write(b'\xdd\xe5\xac\x10')  # 0xdde5ac10
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xdde5ac10))

        data.write(b'\xd4\xde\xc6)')  # 0xd4dec629
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flight_max_speed))

        data.write(b'z+\xb3w')  # 0x7a2bb377
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flight_acceleration))

        data.write(b'\xdd\x146\x1f')  # 0xdd14361f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flight_deceleration))

        data.write(b'gb[\xef')  # 0x67625bef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dodge_time))

        data.write(b'4\xb9~\xdb')  # 0x34b97edb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dodge_time_variance))

        data.write(b'G\xbe2\x98')  # 0x47be3298
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dodge_chance))

        data.write(b'\xef\xd7\x8aA')  # 0xefd78a41
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xefd78a41))

        data.write(b'\xc7Y\x98\xaa')  # 0xc75998aa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_height))

        data.write(b'\x93qj\x88')  # 0x93716a88
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_follow_distance))

        data.write(b'\xd2fU\x0e')  # 0xd266550e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_follow_distance))

        data.write(b'Dn\xfc\xad')  # 0x446efcad
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.initial_attack_time))

        data.write(b'\xdc\xa1\xe8\xb6')  # 0xdca1e8b6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_time))

        data.write(b'\x9f&\x96\x14')  # 0x9f269614
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_time_variance))

        data.write(b'\x05\x9bF\xcf')  # 0x59b46cf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x059b46cf))

        data.write(b'\x1a\xa9\x8d\x7f')  # 0x1aa98d7f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1aa98d7f))

        data.write(b'\xfd\xd2\xfe ')  # 0xfdd2fe20
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.junction_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc1\x08\xcf\xa0')  # 0xc108cfa0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct7.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x91P&\x86')  # 0x91502686
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct11.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xadb\xc9\x93')  # 0xad62c993
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct12.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x03\xa3\x19\xdf')  # 0x3a319df
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct13.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9d\xd3\xbbW')  # 0x9dd3bb57
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct14.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AuroraUnit2DataJson", data)
        return cls(
            unknown_0x0a072c48=json_data['unknown_0x0a072c48'],
            unknown_0xdde5ac10=json_data['unknown_0xdde5ac10'],
            flight_max_speed=json_data['flight_max_speed'],
            flight_acceleration=json_data['flight_acceleration'],
            flight_deceleration=json_data['flight_deceleration'],
            dodge_time=json_data['dodge_time'],
            dodge_time_variance=json_data['dodge_time_variance'],
            dodge_chance=json_data['dodge_chance'],
            unknown_0xefd78a41=json_data['unknown_0xefd78a41'],
            hover_height=json_data['hover_height'],
            min_follow_distance=json_data['min_follow_distance'],
            max_follow_distance=json_data['max_follow_distance'],
            initial_attack_time=json_data['initial_attack_time'],
            attack_time=json_data['attack_time'],
            attack_time_variance=json_data['attack_time_variance'],
            unknown_0x059b46cf=json_data['unknown_0x059b46cf'],
            unknown_0x1aa98d7f=json_data['unknown_0x1aa98d7f'],
            junction_vulnerability=DamageVulnerability.from_json(json_data['junction_vulnerability']),
            unknown_struct7=UnknownStruct7.from_json(json_data['unknown_struct7']),
            unknown_struct11=UnknownStruct11.from_json(json_data['unknown_struct11']),
            unknown_struct12=UnknownStruct12.from_json(json_data['unknown_struct12']),
            unknown_struct13=UnknownStruct13.from_json(json_data['unknown_struct13']),
            unknown_struct14=UnknownStruct14.from_json(json_data['unknown_struct14']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x0a072c48': self.unknown_0x0a072c48,
            'unknown_0xdde5ac10': self.unknown_0xdde5ac10,
            'flight_max_speed': self.flight_max_speed,
            'flight_acceleration': self.flight_acceleration,
            'flight_deceleration': self.flight_deceleration,
            'dodge_time': self.dodge_time,
            'dodge_time_variance': self.dodge_time_variance,
            'dodge_chance': self.dodge_chance,
            'unknown_0xefd78a41': self.unknown_0xefd78a41,
            'hover_height': self.hover_height,
            'min_follow_distance': self.min_follow_distance,
            'max_follow_distance': self.max_follow_distance,
            'initial_attack_time': self.initial_attack_time,
            'attack_time': self.attack_time,
            'attack_time_variance': self.attack_time_variance,
            'unknown_0x059b46cf': self.unknown_0x059b46cf,
            'unknown_0x1aa98d7f': self.unknown_0x1aa98d7f,
            'junction_vulnerability': self.junction_vulnerability.to_json(),
            'unknown_struct7': self.unknown_struct7.to_json(),
            'unknown_struct11': self.unknown_struct11.to_json(),
            'unknown_struct12': self.unknown_struct12.to_json(),
            'unknown_struct13': self.unknown_struct13.to_json(),
            'unknown_struct14': self.unknown_struct14.to_json(),
        }


def _decode_unknown_0x0a072c48(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdde5ac10(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flight_max_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flight_acceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flight_deceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dodge_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dodge_time_variance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dodge_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xefd78a41(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hover_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_follow_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_follow_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_initial_attack_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_time_variance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x059b46cf(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1aa98d7f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xa072c48: ('unknown_0x0a072c48', _decode_unknown_0x0a072c48),
    0xdde5ac10: ('unknown_0xdde5ac10', _decode_unknown_0xdde5ac10),
    0xd4dec629: ('flight_max_speed', _decode_flight_max_speed),
    0x7a2bb377: ('flight_acceleration', _decode_flight_acceleration),
    0xdd14361f: ('flight_deceleration', _decode_flight_deceleration),
    0x67625bef: ('dodge_time', _decode_dodge_time),
    0x34b97edb: ('dodge_time_variance', _decode_dodge_time_variance),
    0x47be3298: ('dodge_chance', _decode_dodge_chance),
    0xefd78a41: ('unknown_0xefd78a41', _decode_unknown_0xefd78a41),
    0xc75998aa: ('hover_height', _decode_hover_height),
    0x93716a88: ('min_follow_distance', _decode_min_follow_distance),
    0xd266550e: ('max_follow_distance', _decode_max_follow_distance),
    0x446efcad: ('initial_attack_time', _decode_initial_attack_time),
    0xdca1e8b6: ('attack_time', _decode_attack_time),
    0x9f269614: ('attack_time_variance', _decode_attack_time_variance),
    0x59b46cf: ('unknown_0x059b46cf', _decode_unknown_0x059b46cf),
    0x1aa98d7f: ('unknown_0x1aa98d7f', _decode_unknown_0x1aa98d7f),
    0xfdd2fe20: ('junction_vulnerability', DamageVulnerability.from_stream),
    0xc108cfa0: ('unknown_struct7', UnknownStruct7.from_stream),
    0x91502686: ('unknown_struct11', UnknownStruct11.from_stream),
    0xad62c993: ('unknown_struct12', UnknownStruct12.from_stream),
    0x3a319df: ('unknown_struct13', UnknownStruct13.from_stream),
    0x9dd3bb57: ('unknown_struct14', UnknownStruct14.from_stream),
}
