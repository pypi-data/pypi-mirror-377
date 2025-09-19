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
from retro_data_structures.properties.corruption.archetypes.CattleProd import CattleProd
from retro_data_structures.properties.corruption.archetypes.Chakram import Chakram
from retro_data_structures.properties.corruption.archetypes.EnergyWhip import EnergyWhip
from retro_data_structures.properties.corruption.archetypes.ReptilicusHunterStruct import ReptilicusHunterStruct
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class ReptilicusHunterDataJson(typing_extensions.TypedDict):
        use_defense_points: bool
        disable_terrain_alignment: bool
        unknown_0xe9553ffa: bool
        is_initially_cloaked: bool
        min_visible_time: float
        max_visible_time: float
        unknown_0x11286bd3: float
        unknown_0xb7e53921: float
        unknown_0x5867275b: float
        cloak_time: float
        decloak_time: float
        cloak_sound: int
        decloak_sound: int
        unknown_0x221c7ec1: float
        unknown_0x41af5eeb: float
        hear_shot_radius: float
        cover_abort_time: float
        unknown_0x164f8ca8: float
        unknown_0xcdf0df4f: float
        unknown_0xf77e2ae2: float
        unknown_0x14239438: float
        unknown_0xe6c24412: float
        heavy_hit_chance: float
        taunt_chance: float
        aggressiveness: float
        reptilicus_hunter_struct_0x9c5e7d6f: json_util.JsonObject
        reptilicus_hunter_struct_0xaa2bee9a: json_util.JsonObject
        reptilicus_hunter_struct_0xe27a4e87: json_util.JsonObject
        cattle_prod: json_util.JsonObject
        energy_whip: json_util.JsonObject
        chakram: json_util.JsonObject
    

@dataclasses.dataclass()
class ReptilicusHunterData(BaseProperty):
    use_defense_points: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x217e944a, original_name='UseDefensePoints'
        ),
    })
    disable_terrain_alignment: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0c81681a, original_name='DisableTerrainAlignment'
        ),
    })
    unknown_0xe9553ffa: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe9553ffa, original_name='Unknown'
        ),
    })
    is_initially_cloaked: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x1c893f54, original_name='IsInitiallyCloaked'
        ),
    })
    min_visible_time: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x369d0874, original_name='MinVisibleTime'
        ),
    })
    max_visible_time: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x91a9880d, original_name='MaxVisibleTime'
        ),
    })
    unknown_0x11286bd3: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x11286bd3, original_name='Unknown'
        ),
    })
    unknown_0xb7e53921: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb7e53921, original_name='Unknown'
        ),
    })
    unknown_0x5867275b: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5867275b, original_name='Unknown'
        ),
    })
    cloak_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x388bc31f, original_name='CloakTime'
        ),
    })
    decloak_time: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4319c840, original_name='DecloakTime'
        ),
    })
    cloak_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x052bf617, original_name='CloakSound'
        ),
    })
    decloak_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xfe842879, original_name='DecloakSound'
        ),
    })
    unknown_0x221c7ec1: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x221c7ec1, original_name='Unknown'
        ),
    })
    unknown_0x41af5eeb: float = dataclasses.field(default=300.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x41af5eeb, original_name='Unknown'
        ),
    })
    hear_shot_radius: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0cf887f1, original_name='HearShotRadius'
        ),
    })
    cover_abort_time: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x18a9876b, original_name='CoverAbortTime'
        ),
    })
    unknown_0x164f8ca8: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x164f8ca8, original_name='Unknown'
        ),
    })
    unknown_0xcdf0df4f: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcdf0df4f, original_name='Unknown'
        ),
    })
    unknown_0xf77e2ae2: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf77e2ae2, original_name='Unknown'
        ),
    })
    unknown_0x14239438: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x14239438, original_name='Unknown'
        ),
    })
    unknown_0xe6c24412: float = dataclasses.field(default=7.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe6c24412, original_name='Unknown'
        ),
    })
    heavy_hit_chance: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x583c1b1e, original_name='HeavyHitChance'
        ),
    })
    taunt_chance: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa77f6212, original_name='TauntChance'
        ),
    })
    aggressiveness: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9579b1f2, original_name='Aggressiveness'
        ),
    })
    reptilicus_hunter_struct_0x9c5e7d6f: ReptilicusHunterStruct = dataclasses.field(default_factory=ReptilicusHunterStruct, metadata={
        'reflection': FieldReflection[ReptilicusHunterStruct](
            ReptilicusHunterStruct, id=0x9c5e7d6f, original_name='ReptilicusHunterStruct', from_json=ReptilicusHunterStruct.from_json, to_json=ReptilicusHunterStruct.to_json
        ),
    })
    reptilicus_hunter_struct_0xaa2bee9a: ReptilicusHunterStruct = dataclasses.field(default_factory=ReptilicusHunterStruct, metadata={
        'reflection': FieldReflection[ReptilicusHunterStruct](
            ReptilicusHunterStruct, id=0xaa2bee9a, original_name='ReptilicusHunterStruct', from_json=ReptilicusHunterStruct.from_json, to_json=ReptilicusHunterStruct.to_json
        ),
    })
    reptilicus_hunter_struct_0xe27a4e87: ReptilicusHunterStruct = dataclasses.field(default_factory=ReptilicusHunterStruct, metadata={
        'reflection': FieldReflection[ReptilicusHunterStruct](
            ReptilicusHunterStruct, id=0xe27a4e87, original_name='ReptilicusHunterStruct', from_json=ReptilicusHunterStruct.from_json, to_json=ReptilicusHunterStruct.to_json
        ),
    })
    cattle_prod: CattleProd = dataclasses.field(default_factory=CattleProd, metadata={
        'reflection': FieldReflection[CattleProd](
            CattleProd, id=0x87b10a69, original_name='CattleProd', from_json=CattleProd.from_json, to_json=CattleProd.to_json
        ),
    })
    energy_whip: EnergyWhip = dataclasses.field(default_factory=EnergyWhip, metadata={
        'reflection': FieldReflection[EnergyWhip](
            EnergyWhip, id=0xd7548e97, original_name='EnergyWhip', from_json=EnergyWhip.from_json, to_json=EnergyWhip.to_json
        ),
    })
    chakram: Chakram = dataclasses.field(default_factory=Chakram, metadata={
        'reflection': FieldReflection[Chakram](
            Chakram, id=0x19a58c31, original_name='Chakram', from_json=Chakram.from_json, to_json=Chakram.to_json
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
        if property_count != 31:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x217e944a
        use_defense_points = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0c81681a
        disable_terrain_alignment = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe9553ffa
        unknown_0xe9553ffa = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1c893f54
        is_initially_cloaked = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x369d0874
        min_visible_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x91a9880d
        max_visible_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x11286bd3
        unknown_0x11286bd3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb7e53921
        unknown_0xb7e53921 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5867275b
        unknown_0x5867275b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x388bc31f
        cloak_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4319c840
        decloak_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x052bf617
        cloak_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfe842879
        decloak_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x221c7ec1
        unknown_0x221c7ec1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x41af5eeb
        unknown_0x41af5eeb = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0cf887f1
        hear_shot_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x18a9876b
        cover_abort_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x164f8ca8
        unknown_0x164f8ca8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcdf0df4f
        unknown_0xcdf0df4f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf77e2ae2
        unknown_0xf77e2ae2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x14239438
        unknown_0x14239438 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe6c24412
        unknown_0xe6c24412 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x583c1b1e
        heavy_hit_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa77f6212
        taunt_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9579b1f2
        aggressiveness = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9c5e7d6f
        reptilicus_hunter_struct_0x9c5e7d6f = ReptilicusHunterStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaa2bee9a
        reptilicus_hunter_struct_0xaa2bee9a = ReptilicusHunterStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe27a4e87
        reptilicus_hunter_struct_0xe27a4e87 = ReptilicusHunterStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x87b10a69
        cattle_prod = CattleProd.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd7548e97
        energy_whip = EnergyWhip.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x19a58c31
        chakram = Chakram.from_stream(data, property_size)
    
        return cls(use_defense_points, disable_terrain_alignment, unknown_0xe9553ffa, is_initially_cloaked, min_visible_time, max_visible_time, unknown_0x11286bd3, unknown_0xb7e53921, unknown_0x5867275b, cloak_time, decloak_time, cloak_sound, decloak_sound, unknown_0x221c7ec1, unknown_0x41af5eeb, hear_shot_radius, cover_abort_time, unknown_0x164f8ca8, unknown_0xcdf0df4f, unknown_0xf77e2ae2, unknown_0x14239438, unknown_0xe6c24412, heavy_hit_chance, taunt_chance, aggressiveness, reptilicus_hunter_struct_0x9c5e7d6f, reptilicus_hunter_struct_0xaa2bee9a, reptilicus_hunter_struct_0xe27a4e87, cattle_prod, energy_whip, chakram)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x1f')  # 31 properties

        data.write(b'!~\x94J')  # 0x217e944a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.use_defense_points))

        data.write(b'\x0c\x81h\x1a')  # 0xc81681a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.disable_terrain_alignment))

        data.write(b'\xe9U?\xfa')  # 0xe9553ffa
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xe9553ffa))

        data.write(b'\x1c\x89?T')  # 0x1c893f54
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_initially_cloaked))

        data.write(b'6\x9d\x08t')  # 0x369d0874
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_visible_time))

        data.write(b'\x91\xa9\x88\r')  # 0x91a9880d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_visible_time))

        data.write(b'\x11(k\xd3')  # 0x11286bd3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x11286bd3))

        data.write(b'\xb7\xe59!')  # 0xb7e53921
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb7e53921))

        data.write(b"Xg'[")  # 0x5867275b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5867275b))

        data.write(b'8\x8b\xc3\x1f')  # 0x388bc31f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cloak_time))

        data.write(b'C\x19\xc8@')  # 0x4319c840
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.decloak_time))

        data.write(b'\x05+\xf6\x17')  # 0x52bf617
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cloak_sound))

        data.write(b'\xfe\x84(y')  # 0xfe842879
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.decloak_sound))

        data.write(b'"\x1c~\xc1')  # 0x221c7ec1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x221c7ec1))

        data.write(b'A\xaf^\xeb')  # 0x41af5eeb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x41af5eeb))

        data.write(b'\x0c\xf8\x87\xf1')  # 0xcf887f1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hear_shot_radius))

        data.write(b'\x18\xa9\x87k')  # 0x18a9876b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cover_abort_time))

        data.write(b'\x16O\x8c\xa8')  # 0x164f8ca8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x164f8ca8))

        data.write(b'\xcd\xf0\xdfO')  # 0xcdf0df4f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcdf0df4f))

        data.write(b'\xf7~*\xe2')  # 0xf77e2ae2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf77e2ae2))

        data.write(b'\x14#\x948')  # 0x14239438
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x14239438))

        data.write(b'\xe6\xc2D\x12')  # 0xe6c24412
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe6c24412))

        data.write(b'X<\x1b\x1e')  # 0x583c1b1e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.heavy_hit_chance))

        data.write(b'\xa7\x7fb\x12')  # 0xa77f6212
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.taunt_chance))

        data.write(b'\x95y\xb1\xf2')  # 0x9579b1f2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aggressiveness))

        data.write(b'\x9c^}o')  # 0x9c5e7d6f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.reptilicus_hunter_struct_0x9c5e7d6f.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xaa+\xee\x9a')  # 0xaa2bee9a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.reptilicus_hunter_struct_0xaa2bee9a.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe2zN\x87')  # 0xe27a4e87
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.reptilicus_hunter_struct_0xe27a4e87.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x87\xb1\ni')  # 0x87b10a69
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.cattle_prod.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd7T\x8e\x97')  # 0xd7548e97
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.energy_whip.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x19\xa5\x8c1')  # 0x19a58c31
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.chakram.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ReptilicusHunterDataJson", data)
        return cls(
            use_defense_points=json_data['use_defense_points'],
            disable_terrain_alignment=json_data['disable_terrain_alignment'],
            unknown_0xe9553ffa=json_data['unknown_0xe9553ffa'],
            is_initially_cloaked=json_data['is_initially_cloaked'],
            min_visible_time=json_data['min_visible_time'],
            max_visible_time=json_data['max_visible_time'],
            unknown_0x11286bd3=json_data['unknown_0x11286bd3'],
            unknown_0xb7e53921=json_data['unknown_0xb7e53921'],
            unknown_0x5867275b=json_data['unknown_0x5867275b'],
            cloak_time=json_data['cloak_time'],
            decloak_time=json_data['decloak_time'],
            cloak_sound=json_data['cloak_sound'],
            decloak_sound=json_data['decloak_sound'],
            unknown_0x221c7ec1=json_data['unknown_0x221c7ec1'],
            unknown_0x41af5eeb=json_data['unknown_0x41af5eeb'],
            hear_shot_radius=json_data['hear_shot_radius'],
            cover_abort_time=json_data['cover_abort_time'],
            unknown_0x164f8ca8=json_data['unknown_0x164f8ca8'],
            unknown_0xcdf0df4f=json_data['unknown_0xcdf0df4f'],
            unknown_0xf77e2ae2=json_data['unknown_0xf77e2ae2'],
            unknown_0x14239438=json_data['unknown_0x14239438'],
            unknown_0xe6c24412=json_data['unknown_0xe6c24412'],
            heavy_hit_chance=json_data['heavy_hit_chance'],
            taunt_chance=json_data['taunt_chance'],
            aggressiveness=json_data['aggressiveness'],
            reptilicus_hunter_struct_0x9c5e7d6f=ReptilicusHunterStruct.from_json(json_data['reptilicus_hunter_struct_0x9c5e7d6f']),
            reptilicus_hunter_struct_0xaa2bee9a=ReptilicusHunterStruct.from_json(json_data['reptilicus_hunter_struct_0xaa2bee9a']),
            reptilicus_hunter_struct_0xe27a4e87=ReptilicusHunterStruct.from_json(json_data['reptilicus_hunter_struct_0xe27a4e87']),
            cattle_prod=CattleProd.from_json(json_data['cattle_prod']),
            energy_whip=EnergyWhip.from_json(json_data['energy_whip']),
            chakram=Chakram.from_json(json_data['chakram']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'use_defense_points': self.use_defense_points,
            'disable_terrain_alignment': self.disable_terrain_alignment,
            'unknown_0xe9553ffa': self.unknown_0xe9553ffa,
            'is_initially_cloaked': self.is_initially_cloaked,
            'min_visible_time': self.min_visible_time,
            'max_visible_time': self.max_visible_time,
            'unknown_0x11286bd3': self.unknown_0x11286bd3,
            'unknown_0xb7e53921': self.unknown_0xb7e53921,
            'unknown_0x5867275b': self.unknown_0x5867275b,
            'cloak_time': self.cloak_time,
            'decloak_time': self.decloak_time,
            'cloak_sound': self.cloak_sound,
            'decloak_sound': self.decloak_sound,
            'unknown_0x221c7ec1': self.unknown_0x221c7ec1,
            'unknown_0x41af5eeb': self.unknown_0x41af5eeb,
            'hear_shot_radius': self.hear_shot_radius,
            'cover_abort_time': self.cover_abort_time,
            'unknown_0x164f8ca8': self.unknown_0x164f8ca8,
            'unknown_0xcdf0df4f': self.unknown_0xcdf0df4f,
            'unknown_0xf77e2ae2': self.unknown_0xf77e2ae2,
            'unknown_0x14239438': self.unknown_0x14239438,
            'unknown_0xe6c24412': self.unknown_0xe6c24412,
            'heavy_hit_chance': self.heavy_hit_chance,
            'taunt_chance': self.taunt_chance,
            'aggressiveness': self.aggressiveness,
            'reptilicus_hunter_struct_0x9c5e7d6f': self.reptilicus_hunter_struct_0x9c5e7d6f.to_json(),
            'reptilicus_hunter_struct_0xaa2bee9a': self.reptilicus_hunter_struct_0xaa2bee9a.to_json(),
            'reptilicus_hunter_struct_0xe27a4e87': self.reptilicus_hunter_struct_0xe27a4e87.to_json(),
            'cattle_prod': self.cattle_prod.to_json(),
            'energy_whip': self.energy_whip.to_json(),
            'chakram': self.chakram.to_json(),
        }


def _decode_use_defense_points(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_disable_terrain_alignment(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xe9553ffa(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_is_initially_cloaked(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_min_visible_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_visible_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x11286bd3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb7e53921(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5867275b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_cloak_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_decloak_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_cloak_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_decloak_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x221c7ec1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x41af5eeb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hear_shot_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_cover_abort_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x164f8ca8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcdf0df4f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf77e2ae2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x14239438(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe6c24412(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_heavy_hit_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_taunt_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aggressiveness(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x217e944a: ('use_defense_points', _decode_use_defense_points),
    0xc81681a: ('disable_terrain_alignment', _decode_disable_terrain_alignment),
    0xe9553ffa: ('unknown_0xe9553ffa', _decode_unknown_0xe9553ffa),
    0x1c893f54: ('is_initially_cloaked', _decode_is_initially_cloaked),
    0x369d0874: ('min_visible_time', _decode_min_visible_time),
    0x91a9880d: ('max_visible_time', _decode_max_visible_time),
    0x11286bd3: ('unknown_0x11286bd3', _decode_unknown_0x11286bd3),
    0xb7e53921: ('unknown_0xb7e53921', _decode_unknown_0xb7e53921),
    0x5867275b: ('unknown_0x5867275b', _decode_unknown_0x5867275b),
    0x388bc31f: ('cloak_time', _decode_cloak_time),
    0x4319c840: ('decloak_time', _decode_decloak_time),
    0x52bf617: ('cloak_sound', _decode_cloak_sound),
    0xfe842879: ('decloak_sound', _decode_decloak_sound),
    0x221c7ec1: ('unknown_0x221c7ec1', _decode_unknown_0x221c7ec1),
    0x41af5eeb: ('unknown_0x41af5eeb', _decode_unknown_0x41af5eeb),
    0xcf887f1: ('hear_shot_radius', _decode_hear_shot_radius),
    0x18a9876b: ('cover_abort_time', _decode_cover_abort_time),
    0x164f8ca8: ('unknown_0x164f8ca8', _decode_unknown_0x164f8ca8),
    0xcdf0df4f: ('unknown_0xcdf0df4f', _decode_unknown_0xcdf0df4f),
    0xf77e2ae2: ('unknown_0xf77e2ae2', _decode_unknown_0xf77e2ae2),
    0x14239438: ('unknown_0x14239438', _decode_unknown_0x14239438),
    0xe6c24412: ('unknown_0xe6c24412', _decode_unknown_0xe6c24412),
    0x583c1b1e: ('heavy_hit_chance', _decode_heavy_hit_chance),
    0xa77f6212: ('taunt_chance', _decode_taunt_chance),
    0x9579b1f2: ('aggressiveness', _decode_aggressiveness),
    0x9c5e7d6f: ('reptilicus_hunter_struct_0x9c5e7d6f', ReptilicusHunterStruct.from_stream),
    0xaa2bee9a: ('reptilicus_hunter_struct_0xaa2bee9a', ReptilicusHunterStruct.from_stream),
    0xe27a4e87: ('reptilicus_hunter_struct_0xe27a4e87', ReptilicusHunterStruct.from_stream),
    0x87b10a69: ('cattle_prod', CattleProd.from_stream),
    0xd7548e97: ('energy_whip', EnergyWhip.from_stream),
    0x19a58c31: ('chakram', Chakram.from_stream),
}
