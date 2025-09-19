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
    class UnknownStruct43Json(typing_extensions.TypedDict):
        unknown_0xde7e9f94: int
        crawl_radius: float
        roll_radius: float
        unknown_0xa265383c: float
        forward_priority: float
        unknown_0xe776332a: float
        scan_delay_max: float
        explode_effect: int
        explode_sound: int
        explode_damage: json_util.JsonObject
        visor_goo_effect: int
    

@dataclasses.dataclass()
class UnknownStruct43(BaseProperty):
    unknown_0xde7e9f94: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xde7e9f94, original_name='Unknown'
        ),
    })
    crawl_radius: float = dataclasses.field(default=0.3499999940395355, metadata={
        'reflection': FieldReflection[float](
            float, id=0xad98e16d, original_name='CrawlRadius'
        ),
    })
    roll_radius: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x81d699b0, original_name='RollRadius'
        ),
    })
    unknown_0xa265383c: float = dataclasses.field(default=0.019999999552965164, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa265383c, original_name='Unknown'
        ),
    })
    forward_priority: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0xad08e189, original_name='ForwardPriority'
        ),
    })
    unknown_0xe776332a: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe776332a, original_name='Unknown'
        ),
    })
    scan_delay_max: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x01169ccb, original_name='ScanDelayMax'
        ),
    })
    explode_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1a9c4c4c, original_name='ExplodeEffect'
        ),
    })
    explode_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x098536dd, original_name='ExplodeSound'
        ),
    })
    explode_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xf6206a12, original_name='ExplodeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    visor_goo_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa233accd, original_name='VisorGooEffect'
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
        if property_count != 11:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xde7e9f94
        unknown_0xde7e9f94 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad98e16d
        crawl_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x81d699b0
        roll_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa265383c
        unknown_0xa265383c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad08e189
        forward_priority = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe776332a
        unknown_0xe776332a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01169ccb
        scan_delay_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a9c4c4c
        explode_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x098536dd
        explode_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf6206a12
        explode_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa233accd
        visor_goo_effect = struct.unpack(">Q", data.read(8))[0]
    
        return cls(unknown_0xde7e9f94, crawl_radius, roll_radius, unknown_0xa265383c, forward_priority, unknown_0xe776332a, scan_delay_max, explode_effect, explode_sound, explode_damage, visor_goo_effect)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0b')  # 11 properties

        data.write(b'\xde~\x9f\x94')  # 0xde7e9f94
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xde7e9f94))

        data.write(b'\xad\x98\xe1m')  # 0xad98e16d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.crawl_radius))

        data.write(b'\x81\xd6\x99\xb0')  # 0x81d699b0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.roll_radius))

        data.write(b'\xa2e8<')  # 0xa265383c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa265383c))

        data.write(b'\xad\x08\xe1\x89')  # 0xad08e189
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_priority))

        data.write(b'\xe7v3*')  # 0xe776332a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe776332a))

        data.write(b'\x01\x16\x9c\xcb')  # 0x1169ccb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scan_delay_max))

        data.write(b'\x1a\x9cLL')  # 0x1a9c4c4c
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.explode_effect))

        data.write(b'\t\x856\xdd')  # 0x98536dd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.explode_sound))

        data.write(b'\xf6 j\x12')  # 0xf6206a12
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.explode_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa23\xac\xcd')  # 0xa233accd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.visor_goo_effect))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct43Json", data)
        return cls(
            unknown_0xde7e9f94=json_data['unknown_0xde7e9f94'],
            crawl_radius=json_data['crawl_radius'],
            roll_radius=json_data['roll_radius'],
            unknown_0xa265383c=json_data['unknown_0xa265383c'],
            forward_priority=json_data['forward_priority'],
            unknown_0xe776332a=json_data['unknown_0xe776332a'],
            scan_delay_max=json_data['scan_delay_max'],
            explode_effect=json_data['explode_effect'],
            explode_sound=json_data['explode_sound'],
            explode_damage=DamageInfo.from_json(json_data['explode_damage']),
            visor_goo_effect=json_data['visor_goo_effect'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xde7e9f94': self.unknown_0xde7e9f94,
            'crawl_radius': self.crawl_radius,
            'roll_radius': self.roll_radius,
            'unknown_0xa265383c': self.unknown_0xa265383c,
            'forward_priority': self.forward_priority,
            'unknown_0xe776332a': self.unknown_0xe776332a,
            'scan_delay_max': self.scan_delay_max,
            'explode_effect': self.explode_effect,
            'explode_sound': self.explode_sound,
            'explode_damage': self.explode_damage.to_json(),
            'visor_goo_effect': self.visor_goo_effect,
        }


def _decode_unknown_0xde7e9f94(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_crawl_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_roll_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa265383c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_priority(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe776332a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scan_delay_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_explode_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_explode_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_visor_goo_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xde7e9f94: ('unknown_0xde7e9f94', _decode_unknown_0xde7e9f94),
    0xad98e16d: ('crawl_radius', _decode_crawl_radius),
    0x81d699b0: ('roll_radius', _decode_roll_radius),
    0xa265383c: ('unknown_0xa265383c', _decode_unknown_0xa265383c),
    0xad08e189: ('forward_priority', _decode_forward_priority),
    0xe776332a: ('unknown_0xe776332a', _decode_unknown_0xe776332a),
    0x1169ccb: ('scan_delay_max', _decode_scan_delay_max),
    0x1a9c4c4c: ('explode_effect', _decode_explode_effect),
    0x98536dd: ('explode_sound', _decode_explode_sound),
    0xf6206a12: ('explode_damage', DamageInfo.from_stream),
    0xa233accd: ('visor_goo_effect', _decode_visor_goo_effect),
}
