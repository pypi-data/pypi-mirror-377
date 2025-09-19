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
from retro_data_structures.properties.echoes.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class UnknownStruct22Json(typing_extensions.TypedDict):
        portal_effect: int
        attack_tip: json_util.JsonObject
        stab_damage: json_util.JsonObject
        unknown_0xecfab026: int
        unknown_0x94880277: int
        sound_0x1c3e84b6: int
        sound_0xa93f0198: int
    

@dataclasses.dataclass()
class UnknownStruct22(BaseProperty):
    portal_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4a7c4ec2, original_name='PortalEffect'
        ),
    })
    attack_tip: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xf10b6ef6, original_name='AttackTip', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    stab_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x946016a9, original_name='StabDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0xecfab026: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xecfab026, original_name='Unknown'
        ),
    })
    unknown_0x94880277: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x94880277, original_name='Unknown'
        ),
    })
    sound_0x1c3e84b6: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x1c3e84b6, original_name='Sound'
        ),
    })
    sound_0xa93f0198: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xa93f0198, original_name='Sound'
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
        if property_count != 7:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4a7c4ec2
        portal_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf10b6ef6
        attack_tip = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x946016a9
        stab_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xecfab026
        unknown_0xecfab026 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x94880277
        unknown_0x94880277 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1c3e84b6
        sound_0x1c3e84b6 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa93f0198
        sound_0xa93f0198 = struct.unpack('>l', data.read(4))[0]
    
        return cls(portal_effect, attack_tip, stab_damage, unknown_0xecfab026, unknown_0x94880277, sound_0x1c3e84b6, sound_0xa93f0198)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'J|N\xc2')  # 0x4a7c4ec2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.portal_effect))

        data.write(b'\xf1\x0bn\xf6')  # 0xf10b6ef6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.attack_tip.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x94`\x16\xa9')  # 0x946016a9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.stab_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xec\xfa\xb0&')  # 0xecfab026
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xecfab026))

        data.write(b'\x94\x88\x02w')  # 0x94880277
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x94880277))

        data.write(b'\x1c>\x84\xb6')  # 0x1c3e84b6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x1c3e84b6))

        data.write(b'\xa9?\x01\x98')  # 0xa93f0198
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0xa93f0198))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct22Json", data)
        return cls(
            portal_effect=json_data['portal_effect'],
            attack_tip=AnimationParameters.from_json(json_data['attack_tip']),
            stab_damage=DamageInfo.from_json(json_data['stab_damage']),
            unknown_0xecfab026=json_data['unknown_0xecfab026'],
            unknown_0x94880277=json_data['unknown_0x94880277'],
            sound_0x1c3e84b6=json_data['sound_0x1c3e84b6'],
            sound_0xa93f0198=json_data['sound_0xa93f0198'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'portal_effect': self.portal_effect,
            'attack_tip': self.attack_tip.to_json(),
            'stab_damage': self.stab_damage.to_json(),
            'unknown_0xecfab026': self.unknown_0xecfab026,
            'unknown_0x94880277': self.unknown_0x94880277,
            'sound_0x1c3e84b6': self.sound_0x1c3e84b6,
            'sound_0xa93f0198': self.sound_0xa93f0198,
        }

    def _dependencies_for_portal_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.portal_effect)

    def _dependencies_for_sound_0x1c3e84b6(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x1c3e84b6)

    def _dependencies_for_sound_0xa93f0198(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0xa93f0198)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_portal_effect, "portal_effect", "AssetId"),
            (self.attack_tip.dependencies_for, "attack_tip", "AnimationParameters"),
            (self.stab_damage.dependencies_for, "stab_damage", "DamageInfo"),
            (self._dependencies_for_sound_0x1c3e84b6, "sound_0x1c3e84b6", "int"),
            (self._dependencies_for_sound_0xa93f0198, "sound_0xa93f0198", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for UnknownStruct22.{field_name} ({field_type}): {e}"
                )


def _decode_portal_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0xecfab026(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x94880277(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0x1c3e84b6(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0xa93f0198(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x4a7c4ec2: ('portal_effect', _decode_portal_effect),
    0xf10b6ef6: ('attack_tip', AnimationParameters.from_stream),
    0x946016a9: ('stab_damage', DamageInfo.from_stream),
    0xecfab026: ('unknown_0xecfab026', _decode_unknown_0xecfab026),
    0x94880277: ('unknown_0x94880277', _decode_unknown_0x94880277),
    0x1c3e84b6: ('sound_0x1c3e84b6', _decode_sound_0x1c3e84b6),
    0xa93f0198: ('sound_0xa93f0198', _decode_sound_0xa93f0198),
}
