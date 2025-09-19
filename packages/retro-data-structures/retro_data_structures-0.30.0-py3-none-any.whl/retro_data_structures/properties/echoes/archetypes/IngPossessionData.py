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
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class IngPossessionDataJson(typing_extensions.TypedDict):
        is_an_encounter: bool
        unknown_0xb68c0aa3: bool
        ing_possessed_model: int
        ing_possessed_skin_rules: int
        dark_scan_info: int
        ing_possessed_health: json_util.JsonObject
        ing_possessed_damage_multiplier: float
        unknown_0x2befc1bf: int
        ing_vulnerability: json_util.JsonObject
    

@dataclasses.dataclass()
class IngPossessionData(BaseProperty):
    is_an_encounter: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x888fa435, original_name='IsAnEncounter'
        ),
    })
    unknown_0xb68c0aa3: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb68c0aa3, original_name='Unknown'
        ),
    })
    ing_possessed_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xad54da11, original_name='IngPossessedModel'
        ),
    })
    ing_possessed_skin_rules: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CSKR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf5c66384, original_name='IngPossessedSkinRules'
        ),
    })
    dark_scan_info: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x35a9792e, original_name='DarkScanInfo'
        ),
    })
    ing_possessed_health: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0x1d852d4b, original_name='IngPossessedHealth', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    ing_possessed_damage_multiplier: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x487e4f9a, original_name='IngPossessedDamageMultiplier'
        ),
    })
    unknown_0x2befc1bf: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x2befc1bf, original_name='Unknown'
        ),
    })
    ing_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x4aeec093, original_name='IngVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
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
        if property_count != 9:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x888fa435
        is_an_encounter = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb68c0aa3
        unknown_0xb68c0aa3 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad54da11
        ing_possessed_model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf5c66384
        ing_possessed_skin_rules = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x35a9792e
        dark_scan_info = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1d852d4b
        ing_possessed_health = HealthInfo.from_stream(data, property_size, default_override={'health': 150.0, 'hi_knock_back_resistance': 2.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x487e4f9a
        ing_possessed_damage_multiplier = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2befc1bf
        unknown_0x2befc1bf = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4aeec093
        ing_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        return cls(is_an_encounter, unknown_0xb68c0aa3, ing_possessed_model, ing_possessed_skin_rules, dark_scan_info, ing_possessed_health, ing_possessed_damage_multiplier, unknown_0x2befc1bf, ing_vulnerability)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\t')  # 9 properties

        data.write(b'\x88\x8f\xa45')  # 0x888fa435
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_an_encounter))

        data.write(b'\xb6\x8c\n\xa3')  # 0xb68c0aa3
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xb68c0aa3))

        data.write(b'\xadT\xda\x11')  # 0xad54da11
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.ing_possessed_model))

        data.write(b'\xf5\xc6c\x84')  # 0xf5c66384
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.ing_possessed_skin_rules))

        data.write(b'5\xa9y.')  # 0x35a9792e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.dark_scan_info))

        data.write(b'\x1d\x85-K')  # 0x1d852d4b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ing_possessed_health.to_stream(data, default_override={'health': 150.0, 'hi_knock_back_resistance': 2.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'H~O\x9a')  # 0x487e4f9a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ing_possessed_damage_multiplier))

        data.write(b'+\xef\xc1\xbf')  # 0x2befc1bf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x2befc1bf))

        data.write(b'J\xee\xc0\x93')  # 0x4aeec093
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ing_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("IngPossessionDataJson", data)
        return cls(
            is_an_encounter=json_data['is_an_encounter'],
            unknown_0xb68c0aa3=json_data['unknown_0xb68c0aa3'],
            ing_possessed_model=json_data['ing_possessed_model'],
            ing_possessed_skin_rules=json_data['ing_possessed_skin_rules'],
            dark_scan_info=json_data['dark_scan_info'],
            ing_possessed_health=HealthInfo.from_json(json_data['ing_possessed_health']),
            ing_possessed_damage_multiplier=json_data['ing_possessed_damage_multiplier'],
            unknown_0x2befc1bf=json_data['unknown_0x2befc1bf'],
            ing_vulnerability=DamageVulnerability.from_json(json_data['ing_vulnerability']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'is_an_encounter': self.is_an_encounter,
            'unknown_0xb68c0aa3': self.unknown_0xb68c0aa3,
            'ing_possessed_model': self.ing_possessed_model,
            'ing_possessed_skin_rules': self.ing_possessed_skin_rules,
            'dark_scan_info': self.dark_scan_info,
            'ing_possessed_health': self.ing_possessed_health.to_json(),
            'ing_possessed_damage_multiplier': self.ing_possessed_damage_multiplier,
            'unknown_0x2befc1bf': self.unknown_0x2befc1bf,
            'ing_vulnerability': self.ing_vulnerability.to_json(),
        }

    def _dependencies_for_ing_possessed_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.ing_possessed_model)

    def _dependencies_for_ing_possessed_skin_rules(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.ing_possessed_skin_rules)

    def _dependencies_for_dark_scan_info(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.dark_scan_info)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_ing_possessed_model, "ing_possessed_model", "AssetId"),
            (self._dependencies_for_ing_possessed_skin_rules, "ing_possessed_skin_rules", "AssetId"),
            (self._dependencies_for_dark_scan_info, "dark_scan_info", "AssetId"),
            (self.ing_possessed_health.dependencies_for, "ing_possessed_health", "HealthInfo"),
            (self.ing_vulnerability.dependencies_for, "ing_vulnerability", "DamageVulnerability"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for IngPossessionData.{field_name} ({field_type}): {e}"
                )


def _decode_is_an_encounter(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xb68c0aa3(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_ing_possessed_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_ing_possessed_skin_rules(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_dark_scan_info(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_ing_possessed_health(data: typing.BinaryIO, property_size: int) -> HealthInfo:
    return HealthInfo.from_stream(data, property_size, default_override={'health': 150.0, 'hi_knock_back_resistance': 2.0})


def _decode_ing_possessed_damage_multiplier(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2befc1bf(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x888fa435: ('is_an_encounter', _decode_is_an_encounter),
    0xb68c0aa3: ('unknown_0xb68c0aa3', _decode_unknown_0xb68c0aa3),
    0xad54da11: ('ing_possessed_model', _decode_ing_possessed_model),
    0xf5c66384: ('ing_possessed_skin_rules', _decode_ing_possessed_skin_rules),
    0x35a9792e: ('dark_scan_info', _decode_dark_scan_info),
    0x1d852d4b: ('ing_possessed_health', _decode_ing_possessed_health),
    0x487e4f9a: ('ing_possessed_damage_multiplier', _decode_ing_possessed_damage_multiplier),
    0x2befc1bf: ('unknown_0x2befc1bf', _decode_unknown_0x2befc1bf),
    0x4aeec093: ('ing_vulnerability', DamageVulnerability.from_stream),
}
