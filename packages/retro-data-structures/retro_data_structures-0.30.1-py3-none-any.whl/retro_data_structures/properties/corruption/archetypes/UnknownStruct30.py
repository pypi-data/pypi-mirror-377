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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct30Json(typing_extensions.TypedDict):
        weapon_system: int
        damage: json_util.JsonObject
        visor_effect: int
        visor_impact_sound: int
        unknown_0x2f79b3d0: float
        unknown_0x11cc7b58: float
    

@dataclasses.dataclass()
class UnknownStruct30(BaseProperty):
    weapon_system: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x459ae4a8, original_name='WeaponSystem'
        ),
    })
    damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x337f9524, original_name='Damage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART', 'ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe9c8e2bd, original_name='VisorEffect'
        ),
    })
    visor_impact_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x86ffb3f6, original_name='VisorImpactSound'
        ),
    })
    unknown_0x2f79b3d0: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2f79b3d0, original_name='Unknown'
        ),
    })
    unknown_0x11cc7b58: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x11cc7b58, original_name='Unknown'
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
        if property_count != 6:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x459ae4a8
        weapon_system = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x337f9524
        damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe9c8e2bd
        visor_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x86ffb3f6
        visor_impact_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2f79b3d0
        unknown_0x2f79b3d0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x11cc7b58
        unknown_0x11cc7b58 = struct.unpack('>f', data.read(4))[0]
    
        return cls(weapon_system, damage, visor_effect, visor_impact_sound, unknown_0x2f79b3d0, unknown_0x11cc7b58)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'E\x9a\xe4\xa8')  # 0x459ae4a8
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.weapon_system))

        data.write(b'3\x7f\x95$')  # 0x337f9524
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe9\xc8\xe2\xbd')  # 0xe9c8e2bd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.visor_effect))

        data.write(b'\x86\xff\xb3\xf6')  # 0x86ffb3f6
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.visor_impact_sound))

        data.write(b'/y\xb3\xd0')  # 0x2f79b3d0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2f79b3d0))

        data.write(b'\x11\xcc{X')  # 0x11cc7b58
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x11cc7b58))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct30Json", data)
        return cls(
            weapon_system=json_data['weapon_system'],
            damage=DamageInfo.from_json(json_data['damage']),
            visor_effect=json_data['visor_effect'],
            visor_impact_sound=json_data['visor_impact_sound'],
            unknown_0x2f79b3d0=json_data['unknown_0x2f79b3d0'],
            unknown_0x11cc7b58=json_data['unknown_0x11cc7b58'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'weapon_system': self.weapon_system,
            'damage': self.damage.to_json(),
            'visor_effect': self.visor_effect,
            'visor_impact_sound': self.visor_impact_sound,
            'unknown_0x2f79b3d0': self.unknown_0x2f79b3d0,
            'unknown_0x11cc7b58': self.unknown_0x11cc7b58,
        }


def _decode_weapon_system(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_visor_impact_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x2f79b3d0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x11cc7b58(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x459ae4a8: ('weapon_system', _decode_weapon_system),
    0x337f9524: ('damage', DamageInfo.from_stream),
    0xe9c8e2bd: ('visor_effect', _decode_visor_effect),
    0x86ffb3f6: ('visor_impact_sound', _decode_visor_impact_sound),
    0x2f79b3d0: ('unknown_0x2f79b3d0', _decode_unknown_0x2f79b3d0),
    0x11cc7b58: ('unknown_0x11cc7b58', _decode_unknown_0x11cc7b58),
}
