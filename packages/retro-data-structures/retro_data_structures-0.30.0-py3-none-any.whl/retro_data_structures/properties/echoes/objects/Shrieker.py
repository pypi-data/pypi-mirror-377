# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.echoes.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ShriekerJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        patterned: json_util.JsonObject
        actor_information: json_util.JsonObject
        buried_vulnerability: json_util.JsonObject
        hostile_accumulate_priority: float
        damage_info: json_util.JsonObject
        part: int
        projectile_damage: json_util.JsonObject
        projectile: int
        combat_visor_max_volume: int
        echo_visor_max_volume: int
        melee_damage: json_util.JsonObject
        melee_effect: int
        unknown_0x9b6a4437: float
        melee_attack_time_variation: float
        melee_range: float
        hover_height: float
        missile_deflection_offset: json_util.JsonValue
        missile_deflection_radius: float
        unknown_0xe70ef8a3: float
        sound_missile_deflection: int
        dodge_time: float
        dodge_percentage: float
        detection_height: float
        unknown_0x4753beb1: float
        pop_detection_radius: float
        morphball_detection_radius: float
        visibility_change_time: float
    

@dataclasses.dataclass()
class Shrieker(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    patterned: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0xb3774750, original_name='Patterned', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    buried_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xd7732923, original_name='BuriedVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    hostile_accumulate_priority: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x281ce55d, original_name='HostileAccumulatePriority'
        ),
    })
    damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x5c072fd0, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    part: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0f676bd9, original_name='PART'
        ),
    })
    projectile_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x553b1339, original_name='ProjectileDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xef485db9, original_name='Projectile'
        ),
    })
    combat_visor_max_volume: int = dataclasses.field(default=50, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6d465cc2, original_name='CombatVisorMaxVolume'
        ),
    })
    echo_visor_max_volume: int = dataclasses.field(default=100, metadata={
        'reflection': FieldReflection[int](
            int, id=0x69ec9107, original_name='EchoVisorMaxVolume'
        ),
    })
    melee_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xc9416034, original_name='MeleeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    melee_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6238b4b5, original_name='MeleeEffect'
        ),
    })
    unknown_0x9b6a4437: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9b6a4437, original_name='Unknown'
        ),
    })
    melee_attack_time_variation: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbe0738ef, original_name='MeleeAttackTimeVariation'
        ),
    })
    melee_range: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x39ab62fb, original_name='MeleeRange'
        ),
    })
    hover_height: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc75998aa, original_name='HoverHeight'
        ),
    })
    missile_deflection_offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=-1.5), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x7ab4ab98, original_name='MissileDeflectionOffset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    missile_deflection_radius: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x88fa2acf, original_name='MissileDeflectionRadius'
        ),
    })
    unknown_0xe70ef8a3: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe70ef8a3, original_name='Unknown'
        ),
    })
    sound_missile_deflection: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x8527b396, original_name='Sound_MissileDeflection'
        ),
    })
    dodge_time: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x67625bef, original_name='DodgeTime'
        ),
    })
    dodge_percentage: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1aaf4c43, original_name='DodgePercentage'
        ),
    })
    detection_height: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9bb6cbc7, original_name='DetectionHeight'
        ),
    })
    unknown_0x4753beb1: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4753beb1, original_name='Unknown'
        ),
    })
    pop_detection_radius: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xee863c15, original_name='PopDetectionRadius'
        ),
    })
    morphball_detection_radius: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xae21d21d, original_name='MorphballDetectionRadius'
        ),
    })
    visibility_change_time: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3d689edd, original_name='VisibilityChangeTime'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'SHRK'

    @classmethod
    def modules(cls) -> list[str]:
        return ['Shrieker.rel']

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        struct_id, size, property_count = struct.unpack(">LHH", data.read(8))
        assert struct_id == 0xFFFFFFFF
        root_size_start = data.tell() - 2

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

        assert data.tell() - root_size_start == size
        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 28:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size, default_override={'min_attack_range': 4.5, 'max_attack_range': 30.0, 'average_attack_time': 3.0, 'collision_height': 4.0, 'creature_size': 1})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd7732923
        buried_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x281ce55d
        hostile_accumulate_priority = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5c072fd0
        damage_info = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 10.0, 'di_radius': 4.5, 'di_knock_back_power': 4.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0f676bd9
        part = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x553b1339
        projectile_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0, 'di_knock_back_power': 3.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef485db9
        projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d465cc2
        combat_visor_max_volume = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x69ec9107
        echo_visor_max_volume = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc9416034
        melee_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 10.0, 'di_radius': 4.5, 'di_knock_back_power': 4.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6238b4b5
        melee_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9b6a4437
        unknown_0x9b6a4437 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe0738ef
        melee_attack_time_variation = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x39ab62fb
        melee_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc75998aa
        hover_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7ab4ab98
        missile_deflection_offset = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x88fa2acf
        missile_deflection_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe70ef8a3
        unknown_0xe70ef8a3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8527b396
        sound_missile_deflection = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x67625bef
        dodge_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1aaf4c43
        dodge_percentage = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9bb6cbc7
        detection_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4753beb1
        unknown_0x4753beb1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xee863c15
        pop_detection_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xae21d21d
        morphball_detection_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d689edd
        visibility_change_time = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, patterned, actor_information, buried_vulnerability, hostile_accumulate_priority, damage_info, part, projectile_damage, projectile, combat_visor_max_volume, echo_visor_max_volume, melee_damage, melee_effect, unknown_0x9b6a4437, melee_attack_time_variation, melee_range, hover_height, missile_deflection_offset, missile_deflection_radius, unknown_0xe70ef8a3, sound_missile_deflection, dodge_time, dodge_percentage, detection_height, unknown_0x4753beb1, pop_detection_radius, morphball_detection_radius, visibility_change_time)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x1c')  # 28 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb3wGP')  # 0xb3774750
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned.to_stream(data, default_override={'min_attack_range': 4.5, 'max_attack_range': 30.0, 'average_attack_time': 3.0, 'collision_height': 4.0, 'creature_size': 1})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'~9\x7f\xed')  # 0x7e397fed
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.actor_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd7s)#')  # 0xd7732923
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.buried_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'(\x1c\xe5]')  # 0x281ce55d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hostile_accumulate_priority))

        data.write(b'\\\x07/\xd0')  # 0x5c072fd0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 10.0, 'di_radius': 4.5, 'di_knock_back_power': 4.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x0fgk\xd9')  # 0xf676bd9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.part))

        data.write(b'U;\x139')  # 0x553b1339
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.projectile_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0, 'di_knock_back_power': 3.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xefH]\xb9')  # 0xef485db9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.projectile))

        data.write(b'mF\\\xc2')  # 0x6d465cc2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.combat_visor_max_volume))

        data.write(b'i\xec\x91\x07')  # 0x69ec9107
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.echo_visor_max_volume))

        data.write(b'\xc9A`4')  # 0xc9416034
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.melee_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 10.0, 'di_radius': 4.5, 'di_knock_back_power': 4.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'b8\xb4\xb5')  # 0x6238b4b5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.melee_effect))

        data.write(b'\x9bjD7')  # 0x9b6a4437
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9b6a4437))

        data.write(b'\xbe\x078\xef')  # 0xbe0738ef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.melee_attack_time_variation))

        data.write(b'9\xabb\xfb')  # 0x39ab62fb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.melee_range))

        data.write(b'\xc7Y\x98\xaa')  # 0xc75998aa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_height))

        data.write(b'z\xb4\xab\x98')  # 0x7ab4ab98
        data.write(b'\x00\x0c')  # size
        self.missile_deflection_offset.to_stream(data)

        data.write(b'\x88\xfa*\xcf')  # 0x88fa2acf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.missile_deflection_radius))

        data.write(b'\xe7\x0e\xf8\xa3')  # 0xe70ef8a3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe70ef8a3))

        data.write(b"\x85'\xb3\x96")  # 0x8527b396
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_missile_deflection))

        data.write(b'gb[\xef')  # 0x67625bef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dodge_time))

        data.write(b'\x1a\xafLC')  # 0x1aaf4c43
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dodge_percentage))

        data.write(b'\x9b\xb6\xcb\xc7')  # 0x9bb6cbc7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.detection_height))

        data.write(b'GS\xbe\xb1')  # 0x4753beb1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4753beb1))

        data.write(b'\xee\x86<\x15')  # 0xee863c15
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pop_detection_radius))

        data.write(b'\xae!\xd2\x1d')  # 0xae21d21d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.morphball_detection_radius))

        data.write(b'=h\x9e\xdd')  # 0x3d689edd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.visibility_change_time))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ShriekerJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            buried_vulnerability=DamageVulnerability.from_json(json_data['buried_vulnerability']),
            hostile_accumulate_priority=json_data['hostile_accumulate_priority'],
            damage_info=DamageInfo.from_json(json_data['damage_info']),
            part=json_data['part'],
            projectile_damage=DamageInfo.from_json(json_data['projectile_damage']),
            projectile=json_data['projectile'],
            combat_visor_max_volume=json_data['combat_visor_max_volume'],
            echo_visor_max_volume=json_data['echo_visor_max_volume'],
            melee_damage=DamageInfo.from_json(json_data['melee_damage']),
            melee_effect=json_data['melee_effect'],
            unknown_0x9b6a4437=json_data['unknown_0x9b6a4437'],
            melee_attack_time_variation=json_data['melee_attack_time_variation'],
            melee_range=json_data['melee_range'],
            hover_height=json_data['hover_height'],
            missile_deflection_offset=Vector.from_json(json_data['missile_deflection_offset']),
            missile_deflection_radius=json_data['missile_deflection_radius'],
            unknown_0xe70ef8a3=json_data['unknown_0xe70ef8a3'],
            sound_missile_deflection=json_data['sound_missile_deflection'],
            dodge_time=json_data['dodge_time'],
            dodge_percentage=json_data['dodge_percentage'],
            detection_height=json_data['detection_height'],
            unknown_0x4753beb1=json_data['unknown_0x4753beb1'],
            pop_detection_radius=json_data['pop_detection_radius'],
            morphball_detection_radius=json_data['morphball_detection_radius'],
            visibility_change_time=json_data['visibility_change_time'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'patterned': self.patterned.to_json(),
            'actor_information': self.actor_information.to_json(),
            'buried_vulnerability': self.buried_vulnerability.to_json(),
            'hostile_accumulate_priority': self.hostile_accumulate_priority,
            'damage_info': self.damage_info.to_json(),
            'part': self.part,
            'projectile_damage': self.projectile_damage.to_json(),
            'projectile': self.projectile,
            'combat_visor_max_volume': self.combat_visor_max_volume,
            'echo_visor_max_volume': self.echo_visor_max_volume,
            'melee_damage': self.melee_damage.to_json(),
            'melee_effect': self.melee_effect,
            'unknown_0x9b6a4437': self.unknown_0x9b6a4437,
            'melee_attack_time_variation': self.melee_attack_time_variation,
            'melee_range': self.melee_range,
            'hover_height': self.hover_height,
            'missile_deflection_offset': self.missile_deflection_offset.to_json(),
            'missile_deflection_radius': self.missile_deflection_radius,
            'unknown_0xe70ef8a3': self.unknown_0xe70ef8a3,
            'sound_missile_deflection': self.sound_missile_deflection,
            'dodge_time': self.dodge_time,
            'dodge_percentage': self.dodge_percentage,
            'detection_height': self.detection_height,
            'unknown_0x4753beb1': self.unknown_0x4753beb1,
            'pop_detection_radius': self.pop_detection_radius,
            'morphball_detection_radius': self.morphball_detection_radius,
            'visibility_change_time': self.visibility_change_time,
        }

    def _dependencies_for_part(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.part)

    def _dependencies_for_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.projectile)

    def _dependencies_for_melee_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.melee_effect)

    def _dependencies_for_sound_missile_deflection(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_missile_deflection)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self.buried_vulnerability.dependencies_for, "buried_vulnerability", "DamageVulnerability"),
            (self.damage_info.dependencies_for, "damage_info", "DamageInfo"),
            (self._dependencies_for_part, "part", "AssetId"),
            (self.projectile_damage.dependencies_for, "projectile_damage", "DamageInfo"),
            (self._dependencies_for_projectile, "projectile", "AssetId"),
            (self.melee_damage.dependencies_for, "melee_damage", "DamageInfo"),
            (self._dependencies_for_melee_effect, "melee_effect", "AssetId"),
            (self._dependencies_for_sound_missile_deflection, "sound_missile_deflection", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Shrieker.{field_name} ({field_type}): {e}"
                )


def _decode_patterned(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'min_attack_range': 4.5, 'max_attack_range': 30.0, 'average_attack_time': 3.0, 'collision_height': 4.0, 'creature_size': 1})


def _decode_hostile_accumulate_priority(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_damage_info(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 10.0, 'di_radius': 4.5, 'di_knock_back_power': 4.0})


def _decode_part(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_projectile_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0, 'di_knock_back_power': 3.0})


def _decode_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_combat_visor_max_volume(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_echo_visor_max_volume(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_melee_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 10.0, 'di_radius': 4.5, 'di_knock_back_power': 4.0})


def _decode_melee_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x9b6a4437(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_melee_attack_time_variation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_melee_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hover_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_missile_deflection_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_missile_deflection_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe70ef8a3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_missile_deflection(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_dodge_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dodge_percentage(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_detection_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4753beb1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_pop_detection_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_morphball_detection_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_visibility_change_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xb3774750: ('patterned', _decode_patterned),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0xd7732923: ('buried_vulnerability', DamageVulnerability.from_stream),
    0x281ce55d: ('hostile_accumulate_priority', _decode_hostile_accumulate_priority),
    0x5c072fd0: ('damage_info', _decode_damage_info),
    0xf676bd9: ('part', _decode_part),
    0x553b1339: ('projectile_damage', _decode_projectile_damage),
    0xef485db9: ('projectile', _decode_projectile),
    0x6d465cc2: ('combat_visor_max_volume', _decode_combat_visor_max_volume),
    0x69ec9107: ('echo_visor_max_volume', _decode_echo_visor_max_volume),
    0xc9416034: ('melee_damage', _decode_melee_damage),
    0x6238b4b5: ('melee_effect', _decode_melee_effect),
    0x9b6a4437: ('unknown_0x9b6a4437', _decode_unknown_0x9b6a4437),
    0xbe0738ef: ('melee_attack_time_variation', _decode_melee_attack_time_variation),
    0x39ab62fb: ('melee_range', _decode_melee_range),
    0xc75998aa: ('hover_height', _decode_hover_height),
    0x7ab4ab98: ('missile_deflection_offset', _decode_missile_deflection_offset),
    0x88fa2acf: ('missile_deflection_radius', _decode_missile_deflection_radius),
    0xe70ef8a3: ('unknown_0xe70ef8a3', _decode_unknown_0xe70ef8a3),
    0x8527b396: ('sound_missile_deflection', _decode_sound_missile_deflection),
    0x67625bef: ('dodge_time', _decode_dodge_time),
    0x1aaf4c43: ('dodge_percentage', _decode_dodge_percentage),
    0x9bb6cbc7: ('detection_height', _decode_detection_height),
    0x4753beb1: ('unknown_0x4753beb1', _decode_unknown_0x4753beb1),
    0xee863c15: ('pop_detection_radius', _decode_pop_detection_radius),
    0xae21d21d: ('morphball_detection_radius', _decode_morphball_detection_radius),
    0x3d689edd: ('visibility_change_time', _decode_visibility_change_time),
}
