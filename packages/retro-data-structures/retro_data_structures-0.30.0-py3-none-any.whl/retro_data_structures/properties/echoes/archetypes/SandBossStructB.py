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
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class SandBossStructBJson(typing_extensions.TypedDict):
        damage: json_util.JsonObject
        duration: float
        change_direction_interval: float
        unknown_0x1b57d422: float
        change_direction_chance: float
        inner_radius: float
        outer_radius: float
        unknown_0x52642b7e: float
        unknown_0xfda3eb4b: float
        turn_speed: float
        unknown_0x47cde539: float
        sound_charge_beam: int
        unknown_0x8d4f3b88: int
        unknown_0xbf88fe4f: float
        unknown_0x74c702b3: float
    

@dataclasses.dataclass()
class SandBossStructB(BaseProperty):
    damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x337f9524, original_name='Damage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    duration: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8b51e23f, original_name='Duration'
        ),
    })
    change_direction_interval: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x82be06ba, original_name='ChangeDirectionInterval'
        ),
    })
    unknown_0x1b57d422: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1b57d422, original_name='Unknown'
        ),
    })
    change_direction_chance: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x060b9b84, original_name='ChangeDirectionChance'
        ),
    })
    inner_radius: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3f5af46f, original_name='InnerRadius'
        ),
    })
    outer_radius: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x42d842cd, original_name='OuterRadius'
        ),
    })
    unknown_0x52642b7e: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x52642b7e, original_name='Unknown'
        ),
    })
    unknown_0xfda3eb4b: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfda3eb4b, original_name='Unknown'
        ),
    })
    turn_speed: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x020c78bb, original_name='TurnSpeed'
        ),
    })
    unknown_0x47cde539: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x47cde539, original_name='Unknown'
        ),
    })
    sound_charge_beam: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x29d8744a, original_name='Sound_ChargeBeam'
        ),
    })
    unknown_0x8d4f3b88: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x8d4f3b88, original_name='Unknown'
        ),
    })
    unknown_0xbf88fe4f: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbf88fe4f, original_name='Unknown'
        ),
    })
    unknown_0x74c702b3: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x74c702b3, original_name='Unknown'
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
        if property_count != 15:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x337f9524
        damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 0.5, 'di_knock_back_power': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b51e23f
        duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x82be06ba
        change_direction_interval = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b57d422
        unknown_0x1b57d422 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x060b9b84
        change_direction_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3f5af46f
        inner_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x42d842cd
        outer_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x52642b7e
        unknown_0x52642b7e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfda3eb4b
        unknown_0xfda3eb4b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x020c78bb
        turn_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x47cde539
        unknown_0x47cde539 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x29d8744a
        sound_charge_beam = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8d4f3b88
        unknown_0x8d4f3b88 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbf88fe4f
        unknown_0xbf88fe4f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x74c702b3
        unknown_0x74c702b3 = struct.unpack('>f', data.read(4))[0]
    
        return cls(damage, duration, change_direction_interval, unknown_0x1b57d422, change_direction_chance, inner_radius, outer_radius, unknown_0x52642b7e, unknown_0xfda3eb4b, turn_speed, unknown_0x47cde539, sound_charge_beam, unknown_0x8d4f3b88, unknown_0xbf88fe4f, unknown_0x74c702b3)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0f')  # 15 properties

        data.write(b'3\x7f\x95$')  # 0x337f9524
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 0.5, 'di_knock_back_power': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8bQ\xe2?')  # 0x8b51e23f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.duration))

        data.write(b'\x82\xbe\x06\xba')  # 0x82be06ba
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.change_direction_interval))

        data.write(b'\x1bW\xd4"')  # 0x1b57d422
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1b57d422))

        data.write(b'\x06\x0b\x9b\x84')  # 0x60b9b84
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.change_direction_chance))

        data.write(b'?Z\xf4o')  # 0x3f5af46f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.inner_radius))

        data.write(b'B\xd8B\xcd')  # 0x42d842cd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.outer_radius))

        data.write(b'Rd+~')  # 0x52642b7e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x52642b7e))

        data.write(b'\xfd\xa3\xebK')  # 0xfda3eb4b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfda3eb4b))

        data.write(b'\x02\x0cx\xbb')  # 0x20c78bb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.turn_speed))

        data.write(b'G\xcd\xe59')  # 0x47cde539
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x47cde539))

        data.write(b')\xd8tJ')  # 0x29d8744a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_charge_beam))

        data.write(b'\x8dO;\x88')  # 0x8d4f3b88
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x8d4f3b88))

        data.write(b'\xbf\x88\xfeO')  # 0xbf88fe4f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbf88fe4f))

        data.write(b't\xc7\x02\xb3')  # 0x74c702b3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x74c702b3))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SandBossStructBJson", data)
        return cls(
            damage=DamageInfo.from_json(json_data['damage']),
            duration=json_data['duration'],
            change_direction_interval=json_data['change_direction_interval'],
            unknown_0x1b57d422=json_data['unknown_0x1b57d422'],
            change_direction_chance=json_data['change_direction_chance'],
            inner_radius=json_data['inner_radius'],
            outer_radius=json_data['outer_radius'],
            unknown_0x52642b7e=json_data['unknown_0x52642b7e'],
            unknown_0xfda3eb4b=json_data['unknown_0xfda3eb4b'],
            turn_speed=json_data['turn_speed'],
            unknown_0x47cde539=json_data['unknown_0x47cde539'],
            sound_charge_beam=json_data['sound_charge_beam'],
            unknown_0x8d4f3b88=json_data['unknown_0x8d4f3b88'],
            unknown_0xbf88fe4f=json_data['unknown_0xbf88fe4f'],
            unknown_0x74c702b3=json_data['unknown_0x74c702b3'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'damage': self.damage.to_json(),
            'duration': self.duration,
            'change_direction_interval': self.change_direction_interval,
            'unknown_0x1b57d422': self.unknown_0x1b57d422,
            'change_direction_chance': self.change_direction_chance,
            'inner_radius': self.inner_radius,
            'outer_radius': self.outer_radius,
            'unknown_0x52642b7e': self.unknown_0x52642b7e,
            'unknown_0xfda3eb4b': self.unknown_0xfda3eb4b,
            'turn_speed': self.turn_speed,
            'unknown_0x47cde539': self.unknown_0x47cde539,
            'sound_charge_beam': self.sound_charge_beam,
            'unknown_0x8d4f3b88': self.unknown_0x8d4f3b88,
            'unknown_0xbf88fe4f': self.unknown_0xbf88fe4f,
            'unknown_0x74c702b3': self.unknown_0x74c702b3,
        }

    def _dependencies_for_sound_charge_beam(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_charge_beam)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.damage.dependencies_for, "damage", "DamageInfo"),
            (self._dependencies_for_sound_charge_beam, "sound_charge_beam", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for SandBossStructB.{field_name} ({field_type}): {e}"
                )


def _decode_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 0.5, 'di_knock_back_power': 10.0})


def _decode_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_change_direction_interval(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1b57d422(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_change_direction_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_inner_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_outer_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x52642b7e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfda3eb4b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_turn_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x47cde539(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_charge_beam(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x8d4f3b88(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xbf88fe4f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x74c702b3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x337f9524: ('damage', _decode_damage),
    0x8b51e23f: ('duration', _decode_duration),
    0x82be06ba: ('change_direction_interval', _decode_change_direction_interval),
    0x1b57d422: ('unknown_0x1b57d422', _decode_unknown_0x1b57d422),
    0x60b9b84: ('change_direction_chance', _decode_change_direction_chance),
    0x3f5af46f: ('inner_radius', _decode_inner_radius),
    0x42d842cd: ('outer_radius', _decode_outer_radius),
    0x52642b7e: ('unknown_0x52642b7e', _decode_unknown_0x52642b7e),
    0xfda3eb4b: ('unknown_0xfda3eb4b', _decode_unknown_0xfda3eb4b),
    0x20c78bb: ('turn_speed', _decode_turn_speed),
    0x47cde539: ('unknown_0x47cde539', _decode_unknown_0x47cde539),
    0x29d8744a: ('sound_charge_beam', _decode_sound_charge_beam),
    0x8d4f3b88: ('unknown_0x8d4f3b88', _decode_unknown_0x8d4f3b88),
    0xbf88fe4f: ('unknown_0xbf88fe4f', _decode_unknown_0xbf88fe4f),
    0x74c702b3: ('unknown_0x74c702b3', _decode_unknown_0x74c702b3),
}
