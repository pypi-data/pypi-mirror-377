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
from retro_data_structures.properties.corruption.archetypes.GrappleBlock import GrappleBlock
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class JetPackJson(typing_extensions.TypedDict):
        unknown: float
        grapple_stunned_time: float
        stunned_hover_height: float
        stunned_hover_speed: float
        part_0x2c79052c: int
        part_0x016b65a9: int
        part_0xd8a92aaa: int
        spin_death_damage: json_util.JsonObject
        stunned_grapple_block: json_util.JsonObject
    

@dataclasses.dataclass()
class JetPack(BaseProperty):
    unknown: float = dataclasses.field(default=120.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc6e9d30e, original_name='Unknown'
        ),
    })
    grapple_stunned_time: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9e9d2bd6, original_name='GrappleStunnedTime'
        ),
    })
    stunned_hover_height: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf3a72af9, original_name='StunnedHoverHeight'
        ),
    })
    stunned_hover_speed: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x14355be0, original_name='StunnedHoverSpeed'
        ),
    })
    part_0x2c79052c: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2c79052c, original_name='PART'
        ),
    })
    part_0x016b65a9: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x016b65a9, original_name='PART'
        ),
    })
    part_0xd8a92aaa: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd8a92aaa, original_name='PART'
        ),
    })
    spin_death_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x5bf6f8e4, original_name='SpinDeathDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    stunned_grapple_block: GrappleBlock = dataclasses.field(default_factory=GrappleBlock, metadata={
        'reflection': FieldReflection[GrappleBlock](
            GrappleBlock, id=0x85543e4e, original_name='StunnedGrappleBlock', from_json=GrappleBlock.from_json, to_json=GrappleBlock.to_json
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
        assert property_id == 0xc6e9d30e
        unknown = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9e9d2bd6
        grapple_stunned_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf3a72af9
        stunned_hover_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x14355be0
        stunned_hover_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2c79052c
        part_0x2c79052c = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x016b65a9
        part_0x016b65a9 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd8a92aaa
        part_0xd8a92aaa = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5bf6f8e4
        spin_death_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x85543e4e
        stunned_grapple_block = GrappleBlock.from_stream(data, property_size)
    
        return cls(unknown, grapple_stunned_time, stunned_hover_height, stunned_hover_speed, part_0x2c79052c, part_0x016b65a9, part_0xd8a92aaa, spin_death_damage, stunned_grapple_block)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\t')  # 9 properties

        data.write(b'\xc6\xe9\xd3\x0e')  # 0xc6e9d30e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'\x9e\x9d+\xd6')  # 0x9e9d2bd6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grapple_stunned_time))

        data.write(b'\xf3\xa7*\xf9')  # 0xf3a72af9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.stunned_hover_height))

        data.write(b'\x145[\xe0')  # 0x14355be0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.stunned_hover_speed))

        data.write(b',y\x05,')  # 0x2c79052c
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x2c79052c))

        data.write(b'\x01ke\xa9')  # 0x16b65a9
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x016b65a9))

        data.write(b'\xd8\xa9*\xaa')  # 0xd8a92aaa
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0xd8a92aaa))

        data.write(b'[\xf6\xf8\xe4')  # 0x5bf6f8e4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.spin_death_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x85T>N')  # 0x85543e4e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.stunned_grapple_block.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("JetPackJson", data)
        return cls(
            unknown=json_data['unknown'],
            grapple_stunned_time=json_data['grapple_stunned_time'],
            stunned_hover_height=json_data['stunned_hover_height'],
            stunned_hover_speed=json_data['stunned_hover_speed'],
            part_0x2c79052c=json_data['part_0x2c79052c'],
            part_0x016b65a9=json_data['part_0x016b65a9'],
            part_0xd8a92aaa=json_data['part_0xd8a92aaa'],
            spin_death_damage=DamageInfo.from_json(json_data['spin_death_damage']),
            stunned_grapple_block=GrappleBlock.from_json(json_data['stunned_grapple_block']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown': self.unknown,
            'grapple_stunned_time': self.grapple_stunned_time,
            'stunned_hover_height': self.stunned_hover_height,
            'stunned_hover_speed': self.stunned_hover_speed,
            'part_0x2c79052c': self.part_0x2c79052c,
            'part_0x016b65a9': self.part_0x016b65a9,
            'part_0xd8a92aaa': self.part_0xd8a92aaa,
            'spin_death_damage': self.spin_death_damage.to_json(),
            'stunned_grapple_block': self.stunned_grapple_block.to_json(),
        }


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grapple_stunned_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_stunned_hover_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_stunned_hover_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_part_0x2c79052c(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x016b65a9(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0xd8a92aaa(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xc6e9d30e: ('unknown', _decode_unknown),
    0x9e9d2bd6: ('grapple_stunned_time', _decode_grapple_stunned_time),
    0xf3a72af9: ('stunned_hover_height', _decode_stunned_hover_height),
    0x14355be0: ('stunned_hover_speed', _decode_stunned_hover_speed),
    0x2c79052c: ('part_0x2c79052c', _decode_part_0x2c79052c),
    0x16b65a9: ('part_0x016b65a9', _decode_part_0x016b65a9),
    0xd8a92aaa: ('part_0xd8a92aaa', _decode_part_0xd8a92aaa),
    0x5bf6f8e4: ('spin_death_damage', DamageInfo.from_stream),
    0x85543e4e: ('stunned_grapple_block', GrappleBlock.from_stream),
}
