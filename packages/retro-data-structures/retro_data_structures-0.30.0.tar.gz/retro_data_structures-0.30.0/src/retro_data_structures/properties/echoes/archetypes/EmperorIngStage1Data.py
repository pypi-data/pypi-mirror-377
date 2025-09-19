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
from retro_data_structures.properties.echoes.archetypes.AudioPlaybackParms import AudioPlaybackParms
from retro_data_structures.properties.echoes.archetypes.EmperorIngStage1TentacleData import EmperorIngStage1TentacleData
from retro_data_structures.properties.echoes.archetypes.UnknownStruct20 import UnknownStruct20
from retro_data_structures.properties.echoes.archetypes.UnknownStruct21 import UnknownStruct21
from retro_data_structures.properties.echoes.archetypes.UnknownStruct22 import UnknownStruct22
from retro_data_structures.properties.echoes.archetypes.UnknownStruct23 import UnknownStruct23
from retro_data_structures.properties.echoes.archetypes.UnknownStruct24 import UnknownStruct24

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class EmperorIngStage1DataJson(typing_extensions.TypedDict):
        tentacle: json_util.JsonObject
        unknown_struct20: json_util.JsonObject
        unknown_struct21: json_util.JsonObject
        unknown_struct22: json_util.JsonObject
        unknown_struct23: json_util.JsonObject
        unknown_struct24: json_util.JsonObject
        heart_exposed_time: float
        unknown_0x905938b8: float
        unknown_0xb826317a: float
        heart_damage_sound: json_util.JsonObject
        turn_speed_accel: float
        max_turn_speed_normal: float
        max_turn_speed_melee: float
        unknown_0xe5a7c358: float
        vulnerability_change_sound: int
        taunt_frequency: float
        attack_interval_min: float
        attack_interval_max: float
    

@dataclasses.dataclass()
class EmperorIngStage1Data(BaseProperty):
    tentacle: EmperorIngStage1TentacleData = dataclasses.field(default_factory=EmperorIngStage1TentacleData, metadata={
        'reflection': FieldReflection[EmperorIngStage1TentacleData](
            EmperorIngStage1TentacleData, id=0xb3c6398f, original_name='Tentacle', from_json=EmperorIngStage1TentacleData.from_json, to_json=EmperorIngStage1TentacleData.to_json
        ),
    })
    unknown_struct20: UnknownStruct20 = dataclasses.field(default_factory=UnknownStruct20, metadata={
        'reflection': FieldReflection[UnknownStruct20](
            UnknownStruct20, id=0xf59f9a60, original_name='UnknownStruct20', from_json=UnknownStruct20.from_json, to_json=UnknownStruct20.to_json
        ),
    })
    unknown_struct21: UnknownStruct21 = dataclasses.field(default_factory=UnknownStruct21, metadata={
        'reflection': FieldReflection[UnknownStruct21](
            UnknownStruct21, id=0xa1cda0b6, original_name='UnknownStruct21', from_json=UnknownStruct21.from_json, to_json=UnknownStruct21.to_json
        ),
    })
    unknown_struct22: UnknownStruct22 = dataclasses.field(default_factory=UnknownStruct22, metadata={
        'reflection': FieldReflection[UnknownStruct22](
            UnknownStruct22, id=0x85f36473, original_name='UnknownStruct22', from_json=UnknownStruct22.from_json, to_json=UnknownStruct22.to_json
        ),
    })
    unknown_struct23: UnknownStruct23 = dataclasses.field(default_factory=UnknownStruct23, metadata={
        'reflection': FieldReflection[UnknownStruct23](
            UnknownStruct23, id=0xb4bc04c4, original_name='UnknownStruct23', from_json=UnknownStruct23.from_json, to_json=UnknownStruct23.to_json
        ),
    })
    unknown_struct24: UnknownStruct24 = dataclasses.field(default_factory=UnknownStruct24, metadata={
        'reflection': FieldReflection[UnknownStruct24](
            UnknownStruct24, id=0x8e6d20ec, original_name='UnknownStruct24', from_json=UnknownStruct24.from_json, to_json=UnknownStruct24.to_json
        ),
    })
    heart_exposed_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa588afd1, original_name='HeartExposedTime'
        ),
    })
    unknown_0x905938b8: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x905938b8, original_name='Unknown'
        ),
    })
    unknown_0xb826317a: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb826317a, original_name='Unknown'
        ),
    })
    heart_damage_sound: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0x88232388, original_name='HeartDamageSound', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })
    turn_speed_accel: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc36ae5ca, original_name='TurnSpeedAccel'
        ),
    })
    max_turn_speed_normal: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd30d9bb9, original_name='MaxTurnSpeedNormal'
        ),
    })
    max_turn_speed_melee: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb02cd31f, original_name='MaxTurnSpeedMelee'
        ),
    })
    unknown_0xe5a7c358: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe5a7c358, original_name='Unknown'
        ),
    })
    vulnerability_change_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x93357240, original_name='VulnerabilityChangeSound'
        ),
    })
    taunt_frequency: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x293a0c19, original_name='TauntFrequency'
        ),
    })
    attack_interval_min: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x31ebf869, original_name='AttackIntervalMin'
        ),
    })
    attack_interval_max: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd78b5788, original_name='AttackIntervalMax'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

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
        if property_count != 18:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3c6398f
        tentacle = EmperorIngStage1TentacleData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf59f9a60
        unknown_struct20 = UnknownStruct20.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa1cda0b6
        unknown_struct21 = UnknownStruct21.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x85f36473
        unknown_struct22 = UnknownStruct22.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb4bc04c4
        unknown_struct23 = UnknownStruct23.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8e6d20ec
        unknown_struct24 = UnknownStruct24.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa588afd1
        heart_exposed_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x905938b8
        unknown_0x905938b8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb826317a
        unknown_0xb826317a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x88232388
        heart_damage_sound = AudioPlaybackParms.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc36ae5ca
        turn_speed_accel = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd30d9bb9
        max_turn_speed_normal = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb02cd31f
        max_turn_speed_melee = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe5a7c358
        unknown_0xe5a7c358 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x93357240
        vulnerability_change_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x293a0c19
        taunt_frequency = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x31ebf869
        attack_interval_min = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd78b5788
        attack_interval_max = struct.unpack('>f', data.read(4))[0]
    
        return cls(tentacle, unknown_struct20, unknown_struct21, unknown_struct22, unknown_struct23, unknown_struct24, heart_exposed_time, unknown_0x905938b8, unknown_0xb826317a, heart_damage_sound, turn_speed_accel, max_turn_speed_normal, max_turn_speed_melee, unknown_0xe5a7c358, vulnerability_change_sound, taunt_frequency, attack_interval_min, attack_interval_max)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x12')  # 18 properties

        data.write(b'\xb3\xc69\x8f')  # 0xb3c6398f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.tentacle.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf5\x9f\x9a`')  # 0xf59f9a60
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct20.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa1\xcd\xa0\xb6')  # 0xa1cda0b6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct21.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x85\xf3ds')  # 0x85f36473
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct22.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb4\xbc\x04\xc4')  # 0xb4bc04c4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct23.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8em \xec')  # 0x8e6d20ec
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct24.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa5\x88\xaf\xd1')  # 0xa588afd1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.heart_exposed_time))

        data.write(b'\x90Y8\xb8')  # 0x905938b8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x905938b8))

        data.write(b'\xb8&1z')  # 0xb826317a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb826317a))

        data.write(b'\x88##\x88')  # 0x88232388
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.heart_damage_sound.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc3j\xe5\xca')  # 0xc36ae5ca
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.turn_speed_accel))

        data.write(b'\xd3\r\x9b\xb9')  # 0xd30d9bb9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_turn_speed_normal))

        data.write(b'\xb0,\xd3\x1f')  # 0xb02cd31f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_turn_speed_melee))

        data.write(b'\xe5\xa7\xc3X')  # 0xe5a7c358
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe5a7c358))

        data.write(b'\x935r@')  # 0x93357240
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.vulnerability_change_sound))

        data.write(b'):\x0c\x19')  # 0x293a0c19
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.taunt_frequency))

        data.write(b'1\xeb\xf8i')  # 0x31ebf869
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_interval_min))

        data.write(b'\xd7\x8bW\x88')  # 0xd78b5788
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_interval_max))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("EmperorIngStage1DataJson", data)
        return cls(
            tentacle=EmperorIngStage1TentacleData.from_json(json_data['tentacle']),
            unknown_struct20=UnknownStruct20.from_json(json_data['unknown_struct20']),
            unknown_struct21=UnknownStruct21.from_json(json_data['unknown_struct21']),
            unknown_struct22=UnknownStruct22.from_json(json_data['unknown_struct22']),
            unknown_struct23=UnknownStruct23.from_json(json_data['unknown_struct23']),
            unknown_struct24=UnknownStruct24.from_json(json_data['unknown_struct24']),
            heart_exposed_time=json_data['heart_exposed_time'],
            unknown_0x905938b8=json_data['unknown_0x905938b8'],
            unknown_0xb826317a=json_data['unknown_0xb826317a'],
            heart_damage_sound=AudioPlaybackParms.from_json(json_data['heart_damage_sound']),
            turn_speed_accel=json_data['turn_speed_accel'],
            max_turn_speed_normal=json_data['max_turn_speed_normal'],
            max_turn_speed_melee=json_data['max_turn_speed_melee'],
            unknown_0xe5a7c358=json_data['unknown_0xe5a7c358'],
            vulnerability_change_sound=json_data['vulnerability_change_sound'],
            taunt_frequency=json_data['taunt_frequency'],
            attack_interval_min=json_data['attack_interval_min'],
            attack_interval_max=json_data['attack_interval_max'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'tentacle': self.tentacle.to_json(),
            'unknown_struct20': self.unknown_struct20.to_json(),
            'unknown_struct21': self.unknown_struct21.to_json(),
            'unknown_struct22': self.unknown_struct22.to_json(),
            'unknown_struct23': self.unknown_struct23.to_json(),
            'unknown_struct24': self.unknown_struct24.to_json(),
            'heart_exposed_time': self.heart_exposed_time,
            'unknown_0x905938b8': self.unknown_0x905938b8,
            'unknown_0xb826317a': self.unknown_0xb826317a,
            'heart_damage_sound': self.heart_damage_sound.to_json(),
            'turn_speed_accel': self.turn_speed_accel,
            'max_turn_speed_normal': self.max_turn_speed_normal,
            'max_turn_speed_melee': self.max_turn_speed_melee,
            'unknown_0xe5a7c358': self.unknown_0xe5a7c358,
            'vulnerability_change_sound': self.vulnerability_change_sound,
            'taunt_frequency': self.taunt_frequency,
            'attack_interval_min': self.attack_interval_min,
            'attack_interval_max': self.attack_interval_max,
        }

    def _dependencies_for_vulnerability_change_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.vulnerability_change_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.tentacle.dependencies_for, "tentacle", "EmperorIngStage1TentacleData"),
            (self.unknown_struct20.dependencies_for, "unknown_struct20", "UnknownStruct20"),
            (self.unknown_struct21.dependencies_for, "unknown_struct21", "UnknownStruct21"),
            (self.unknown_struct22.dependencies_for, "unknown_struct22", "UnknownStruct22"),
            (self.unknown_struct23.dependencies_for, "unknown_struct23", "UnknownStruct23"),
            (self.unknown_struct24.dependencies_for, "unknown_struct24", "UnknownStruct24"),
            (self.heart_damage_sound.dependencies_for, "heart_damage_sound", "AudioPlaybackParms"),
            (self._dependencies_for_vulnerability_change_sound, "vulnerability_change_sound", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for EmperorIngStage1Data.{field_name} ({field_type}): {e}"
                )


def _decode_heart_exposed_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x905938b8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb826317a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_turn_speed_accel(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_turn_speed_normal(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_turn_speed_melee(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe5a7c358(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_vulnerability_change_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_taunt_frequency(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_interval_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_interval_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xb3c6398f: ('tentacle', EmperorIngStage1TentacleData.from_stream),
    0xf59f9a60: ('unknown_struct20', UnknownStruct20.from_stream),
    0xa1cda0b6: ('unknown_struct21', UnknownStruct21.from_stream),
    0x85f36473: ('unknown_struct22', UnknownStruct22.from_stream),
    0xb4bc04c4: ('unknown_struct23', UnknownStruct23.from_stream),
    0x8e6d20ec: ('unknown_struct24', UnknownStruct24.from_stream),
    0xa588afd1: ('heart_exposed_time', _decode_heart_exposed_time),
    0x905938b8: ('unknown_0x905938b8', _decode_unknown_0x905938b8),
    0xb826317a: ('unknown_0xb826317a', _decode_unknown_0xb826317a),
    0x88232388: ('heart_damage_sound', AudioPlaybackParms.from_stream),
    0xc36ae5ca: ('turn_speed_accel', _decode_turn_speed_accel),
    0xd30d9bb9: ('max_turn_speed_normal', _decode_max_turn_speed_normal),
    0xb02cd31f: ('max_turn_speed_melee', _decode_max_turn_speed_melee),
    0xe5a7c358: ('unknown_0xe5a7c358', _decode_unknown_0xe5a7c358),
    0x93357240: ('vulnerability_change_sound', _decode_vulnerability_change_sound),
    0x293a0c19: ('taunt_frequency', _decode_taunt_frequency),
    0x31ebf869: ('attack_interval_min', _decode_attack_interval_min),
    0xd78b5788: ('attack_interval_max', _decode_attack_interval_max),
}
