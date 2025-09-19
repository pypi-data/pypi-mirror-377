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
from retro_data_structures.properties.echoes.archetypes.TDamageInfo import TDamageInfo

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakPlayerGun_UnknownStruct1Json(typing_extensions.TypedDict):
        super_missile: json_util.JsonObject
        darkburst: json_util.JsonObject
        sunburst: json_util.JsonObject
        sonic_boom: json_util.JsonObject
        unknown: json_util.JsonObject
    

@dataclasses.dataclass()
class TweakPlayerGun_UnknownStruct1(BaseProperty):
    super_missile: TDamageInfo = dataclasses.field(default_factory=TDamageInfo, metadata={
        'reflection': FieldReflection[TDamageInfo](
            TDamageInfo, id=0xc713acf9, original_name='Super Missile', from_json=TDamageInfo.from_json, to_json=TDamageInfo.to_json
        ),
    })
    darkburst: TDamageInfo = dataclasses.field(default_factory=TDamageInfo, metadata={
        'reflection': FieldReflection[TDamageInfo](
            TDamageInfo, id=0x19468f2a, original_name='Darkburst', from_json=TDamageInfo.from_json, to_json=TDamageInfo.to_json
        ),
    })
    sunburst: TDamageInfo = dataclasses.field(default_factory=TDamageInfo, metadata={
        'reflection': FieldReflection[TDamageInfo](
            TDamageInfo, id=0x48ac6dd8, original_name='Sunburst', from_json=TDamageInfo.from_json, to_json=TDamageInfo.to_json
        ),
    })
    sonic_boom: TDamageInfo = dataclasses.field(default_factory=TDamageInfo, metadata={
        'reflection': FieldReflection[TDamageInfo](
            TDamageInfo, id=0xc1c315ff, original_name='Sonic Boom', from_json=TDamageInfo.from_json, to_json=TDamageInfo.to_json
        ),
    })
    unknown: TDamageInfo = dataclasses.field(default_factory=TDamageInfo, metadata={
        'reflection': FieldReflection[TDamageInfo](
            TDamageInfo, id=0x42885c6c, original_name='Unknown', from_json=TDamageInfo.from_json, to_json=TDamageInfo.to_json
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
        if property_count != 5:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc713acf9
        super_missile = TDamageInfo.from_stream(data, property_size, default_override={'damage_amount': 180.0, 'radius_damage_amount': 120.0, 'damage_radius': 8.0, 'knock_back_power': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x19468f2a
        darkburst = TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 1, 'damage_amount': 150.0, 'radius_damage_amount': 150.0, 'damage_radius': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x48ac6dd8
        sunburst = TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 2, 'damage_amount': 300.0, 'radius_damage_amount': 150.0, 'damage_radius': 8.0, 'knock_back_power': 8.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc1c315ff
        sonic_boom = TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 3, 'damage_amount': 1.2000000476837158, 'radius_damage_amount': 1.2000000476837158})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x42885c6c
        unknown = TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 8})
    
        return cls(super_missile, darkburst, sunburst, sonic_boom, unknown)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x05')  # 5 properties

        data.write(b'\xc7\x13\xac\xf9')  # 0xc713acf9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.super_missile.to_stream(data, default_override={'damage_amount': 180.0, 'radius_damage_amount': 120.0, 'damage_radius': 8.0, 'knock_back_power': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x19F\x8f*')  # 0x19468f2a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.darkburst.to_stream(data, default_override={'weapon_type': 1, 'damage_amount': 150.0, 'radius_damage_amount': 150.0, 'damage_radius': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'H\xacm\xd8')  # 0x48ac6dd8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sunburst.to_stream(data, default_override={'weapon_type': 2, 'damage_amount': 300.0, 'radius_damage_amount': 150.0, 'damage_radius': 8.0, 'knock_back_power': 8.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc1\xc3\x15\xff')  # 0xc1c315ff
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sonic_boom.to_stream(data, default_override={'weapon_type': 3, 'damage_amount': 1.2000000476837158, 'radius_damage_amount': 1.2000000476837158})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'B\x88\\l')  # 0x42885c6c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown.to_stream(data, default_override={'weapon_type': 8})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayerGun_UnknownStruct1Json", data)
        return cls(
            super_missile=TDamageInfo.from_json(json_data['super_missile']),
            darkburst=TDamageInfo.from_json(json_data['darkburst']),
            sunburst=TDamageInfo.from_json(json_data['sunburst']),
            sonic_boom=TDamageInfo.from_json(json_data['sonic_boom']),
            unknown=TDamageInfo.from_json(json_data['unknown']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'super_missile': self.super_missile.to_json(),
            'darkburst': self.darkburst.to_json(),
            'sunburst': self.sunburst.to_json(),
            'sonic_boom': self.sonic_boom.to_json(),
            'unknown': self.unknown.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.super_missile.dependencies_for, "super_missile", "TDamageInfo"),
            (self.darkburst.dependencies_for, "darkburst", "TDamageInfo"),
            (self.sunburst.dependencies_for, "sunburst", "TDamageInfo"),
            (self.sonic_boom.dependencies_for, "sonic_boom", "TDamageInfo"),
            (self.unknown.dependencies_for, "unknown", "TDamageInfo"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for TweakPlayerGun_UnknownStruct1.{field_name} ({field_type}): {e}"
                )


def _decode_super_missile(data: typing.BinaryIO, property_size: int) -> TDamageInfo:
    return TDamageInfo.from_stream(data, property_size, default_override={'damage_amount': 180.0, 'radius_damage_amount': 120.0, 'damage_radius': 8.0, 'knock_back_power': 8.0})


def _decode_darkburst(data: typing.BinaryIO, property_size: int) -> TDamageInfo:
    return TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 1, 'damage_amount': 150.0, 'radius_damage_amount': 150.0, 'damage_radius': 10.0})


def _decode_sunburst(data: typing.BinaryIO, property_size: int) -> TDamageInfo:
    return TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 2, 'damage_amount': 300.0, 'radius_damage_amount': 150.0, 'damage_radius': 8.0, 'knock_back_power': 8.0})


def _decode_sonic_boom(data: typing.BinaryIO, property_size: int) -> TDamageInfo:
    return TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 3, 'damage_amount': 1.2000000476837158, 'radius_damage_amount': 1.2000000476837158})


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> TDamageInfo:
    return TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 8})


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xc713acf9: ('super_missile', _decode_super_missile),
    0x19468f2a: ('darkburst', _decode_darkburst),
    0x48ac6dd8: ('sunburst', _decode_sunburst),
    0xc1c315ff: ('sonic_boom', _decode_sonic_boom),
    0x42885c6c: ('unknown', _decode_unknown),
}
