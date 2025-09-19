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
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class UnknownStruct10Json(typing_extensions.TypedDict):
        grenade_min_attack_interval: float
        unknown_0xb7994ea1: float
        grenade_attack_chance: float
        unknown_0x25f822c4: float
        unknown_0x765e3a20: float
        grenade_damage: json_util.JsonObject
        grenade_explosion: int
        grenade_effect: int
        grenade_trail: int
        grenade_mass: float
        unknown_0xed086ce0: float
        unknown_0x00fc6646: float
        unknown_0xa7c8e63f: float
        unknown_0x454f16b1: int
        unknown_0x2d4706e8: float
        sound_grenade_bounce: int
        sound_grenade_explode: int
    

@dataclasses.dataclass()
class UnknownStruct10(BaseProperty):
    grenade_min_attack_interval: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x74479b13, original_name='GrenadeMinAttackInterval'
        ),
    })
    unknown_0xb7994ea1: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb7994ea1, original_name='Unknown'
        ),
    })
    grenade_attack_chance: float = dataclasses.field(default=80.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9a86ec4d, original_name='GrenadeAttackChance'
        ),
    })
    unknown_0x25f822c4: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x25f822c4, original_name='Unknown'
        ),
    })
    unknown_0x765e3a20: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x765e3a20, original_name='Unknown'
        ),
    })
    grenade_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x14d1a3a8, original_name='GrenadeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    grenade_explosion: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1319e077, original_name='GrenadeExplosion'
        ),
    })
    grenade_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd207ff0f, original_name='GrenadeEffect'
        ),
    })
    grenade_trail: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2b31c882, original_name='GrenadeTrail'
        ),
    })
    grenade_mass: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9a6bb47f, original_name='GrenadeMass'
        ),
    })
    unknown_0xed086ce0: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed086ce0, original_name='Unknown'
        ),
    })
    unknown_0x00fc6646: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00fc6646, original_name='Unknown'
        ),
    })
    unknown_0xa7c8e63f: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa7c8e63f, original_name='Unknown'
        ),
    })
    unknown_0x454f16b1: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x454f16b1, original_name='Unknown'
        ),
    })
    unknown_0x2d4706e8: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2d4706e8, original_name='Unknown'
        ),
    })
    sound_grenade_bounce: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x258c3e1b, original_name='Sound_GrenadeBounce'
        ),
    })
    sound_grenade_explode: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xaf6aad88, original_name='Sound_GrenadeExplode'
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
        if property_count != 17:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x74479b13
        grenade_min_attack_interval = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb7994ea1
        unknown_0xb7994ea1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9a86ec4d
        grenade_attack_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x25f822c4
        unknown_0x25f822c4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x765e3a20
        unknown_0x765e3a20 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x14d1a3a8
        grenade_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 50.0, 'di_radius': 10.0, 'di_knock_back_power': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1319e077
        grenade_explosion = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd207ff0f
        grenade_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b31c882
        grenade_trail = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9a6bb47f
        grenade_mass = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed086ce0
        unknown_0xed086ce0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x00fc6646
        unknown_0x00fc6646 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa7c8e63f
        unknown_0xa7c8e63f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x454f16b1
        unknown_0x454f16b1 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2d4706e8
        unknown_0x2d4706e8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x258c3e1b
        sound_grenade_bounce = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaf6aad88
        sound_grenade_explode = struct.unpack('>l', data.read(4))[0]
    
        return cls(grenade_min_attack_interval, unknown_0xb7994ea1, grenade_attack_chance, unknown_0x25f822c4, unknown_0x765e3a20, grenade_damage, grenade_explosion, grenade_effect, grenade_trail, grenade_mass, unknown_0xed086ce0, unknown_0x00fc6646, unknown_0xa7c8e63f, unknown_0x454f16b1, unknown_0x2d4706e8, sound_grenade_bounce, sound_grenade_explode)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x11')  # 17 properties

        data.write(b'tG\x9b\x13')  # 0x74479b13
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grenade_min_attack_interval))

        data.write(b'\xb7\x99N\xa1')  # 0xb7994ea1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb7994ea1))

        data.write(b'\x9a\x86\xecM')  # 0x9a86ec4d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grenade_attack_chance))

        data.write(b'%\xf8"\xc4')  # 0x25f822c4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x25f822c4))

        data.write(b'v^: ')  # 0x765e3a20
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x765e3a20))

        data.write(b'\x14\xd1\xa3\xa8')  # 0x14d1a3a8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grenade_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 50.0, 'di_radius': 10.0, 'di_knock_back_power': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x13\x19\xe0w')  # 0x1319e077
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.grenade_explosion))

        data.write(b'\xd2\x07\xff\x0f')  # 0xd207ff0f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.grenade_effect))

        data.write(b'+1\xc8\x82')  # 0x2b31c882
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.grenade_trail))

        data.write(b'\x9ak\xb4\x7f')  # 0x9a6bb47f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grenade_mass))

        data.write(b'\xed\x08l\xe0')  # 0xed086ce0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xed086ce0))

        data.write(b'\x00\xfcfF')  # 0xfc6646
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x00fc6646))

        data.write(b'\xa7\xc8\xe6?')  # 0xa7c8e63f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa7c8e63f))

        data.write(b'EO\x16\xb1')  # 0x454f16b1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x454f16b1))

        data.write(b'-G\x06\xe8')  # 0x2d4706e8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2d4706e8))

        data.write(b'%\x8c>\x1b')  # 0x258c3e1b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_grenade_bounce))

        data.write(b'\xafj\xad\x88')  # 0xaf6aad88
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_grenade_explode))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct10Json", data)
        return cls(
            grenade_min_attack_interval=json_data['grenade_min_attack_interval'],
            unknown_0xb7994ea1=json_data['unknown_0xb7994ea1'],
            grenade_attack_chance=json_data['grenade_attack_chance'],
            unknown_0x25f822c4=json_data['unknown_0x25f822c4'],
            unknown_0x765e3a20=json_data['unknown_0x765e3a20'],
            grenade_damage=DamageInfo.from_json(json_data['grenade_damage']),
            grenade_explosion=json_data['grenade_explosion'],
            grenade_effect=json_data['grenade_effect'],
            grenade_trail=json_data['grenade_trail'],
            grenade_mass=json_data['grenade_mass'],
            unknown_0xed086ce0=json_data['unknown_0xed086ce0'],
            unknown_0x00fc6646=json_data['unknown_0x00fc6646'],
            unknown_0xa7c8e63f=json_data['unknown_0xa7c8e63f'],
            unknown_0x454f16b1=json_data['unknown_0x454f16b1'],
            unknown_0x2d4706e8=json_data['unknown_0x2d4706e8'],
            sound_grenade_bounce=json_data['sound_grenade_bounce'],
            sound_grenade_explode=json_data['sound_grenade_explode'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'grenade_min_attack_interval': self.grenade_min_attack_interval,
            'unknown_0xb7994ea1': self.unknown_0xb7994ea1,
            'grenade_attack_chance': self.grenade_attack_chance,
            'unknown_0x25f822c4': self.unknown_0x25f822c4,
            'unknown_0x765e3a20': self.unknown_0x765e3a20,
            'grenade_damage': self.grenade_damage.to_json(),
            'grenade_explosion': self.grenade_explosion,
            'grenade_effect': self.grenade_effect,
            'grenade_trail': self.grenade_trail,
            'grenade_mass': self.grenade_mass,
            'unknown_0xed086ce0': self.unknown_0xed086ce0,
            'unknown_0x00fc6646': self.unknown_0x00fc6646,
            'unknown_0xa7c8e63f': self.unknown_0xa7c8e63f,
            'unknown_0x454f16b1': self.unknown_0x454f16b1,
            'unknown_0x2d4706e8': self.unknown_0x2d4706e8,
            'sound_grenade_bounce': self.sound_grenade_bounce,
            'sound_grenade_explode': self.sound_grenade_explode,
        }

    def _dependencies_for_grenade_explosion(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.grenade_explosion)

    def _dependencies_for_grenade_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.grenade_effect)

    def _dependencies_for_grenade_trail(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.grenade_trail)

    def _dependencies_for_sound_grenade_bounce(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_grenade_bounce)

    def _dependencies_for_sound_grenade_explode(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_grenade_explode)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.grenade_damage.dependencies_for, "grenade_damage", "DamageInfo"),
            (self._dependencies_for_grenade_explosion, "grenade_explosion", "AssetId"),
            (self._dependencies_for_grenade_effect, "grenade_effect", "AssetId"),
            (self._dependencies_for_grenade_trail, "grenade_trail", "AssetId"),
            (self._dependencies_for_sound_grenade_bounce, "sound_grenade_bounce", "int"),
            (self._dependencies_for_sound_grenade_explode, "sound_grenade_explode", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for UnknownStruct10.{field_name} ({field_type}): {e}"
                )


def _decode_grenade_min_attack_interval(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb7994ea1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grenade_attack_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x25f822c4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x765e3a20(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grenade_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 50.0, 'di_radius': 10.0, 'di_knock_back_power': 10.0})


def _decode_grenade_explosion(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_grenade_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_grenade_trail(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_grenade_mass(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xed086ce0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x00fc6646(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa7c8e63f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x454f16b1(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x2d4706e8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_grenade_bounce(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_grenade_explode(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x74479b13: ('grenade_min_attack_interval', _decode_grenade_min_attack_interval),
    0xb7994ea1: ('unknown_0xb7994ea1', _decode_unknown_0xb7994ea1),
    0x9a86ec4d: ('grenade_attack_chance', _decode_grenade_attack_chance),
    0x25f822c4: ('unknown_0x25f822c4', _decode_unknown_0x25f822c4),
    0x765e3a20: ('unknown_0x765e3a20', _decode_unknown_0x765e3a20),
    0x14d1a3a8: ('grenade_damage', _decode_grenade_damage),
    0x1319e077: ('grenade_explosion', _decode_grenade_explosion),
    0xd207ff0f: ('grenade_effect', _decode_grenade_effect),
    0x2b31c882: ('grenade_trail', _decode_grenade_trail),
    0x9a6bb47f: ('grenade_mass', _decode_grenade_mass),
    0xed086ce0: ('unknown_0xed086ce0', _decode_unknown_0xed086ce0),
    0xfc6646: ('unknown_0x00fc6646', _decode_unknown_0x00fc6646),
    0xa7c8e63f: ('unknown_0xa7c8e63f', _decode_unknown_0xa7c8e63f),
    0x454f16b1: ('unknown_0x454f16b1', _decode_unknown_0x454f16b1),
    0x2d4706e8: ('unknown_0x2d4706e8', _decode_unknown_0x2d4706e8),
    0x258c3e1b: ('sound_grenade_bounce', _decode_sound_grenade_bounce),
    0xaf6aad88: ('sound_grenade_explode', _decode_sound_grenade_explode),
}
