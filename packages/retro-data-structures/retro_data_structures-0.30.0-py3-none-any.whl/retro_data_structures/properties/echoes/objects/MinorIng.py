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
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.echoes.archetypes.UnknownStruct33 import UnknownStruct33
from retro_data_structures.properties.echoes.archetypes.UnknownStruct34 import UnknownStruct34
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class MinorIngJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        patterned: json_util.JsonObject
        actor_information: json_util.JsonObject
        projectile_damage: json_util.JsonObject
        projectile: int
        unknown_0xa03e450c: float
        attack_angle_limit: float
        unknown_0x99bb2559: float
        unknown_0xd6c8eac2: float
        unknown_0x2a5449ba: float
        hearing_radius: float
        unknown_0x399d1eaa: bool
        unknown_0xbce16644: bool
        unknown_0x142433d3: bool
        unknown_0xb6cc0063: bool
        unknown_0xe601f7bd: bool
        unknown_0x09207f51: bool
        unknown_0x2107e4fb: bool
        unknown_struct33: json_util.JsonObject
        unknown_struct34: json_util.JsonObject
    

@dataclasses.dataclass()
class MinorIng(BaseObjectType):
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
    unknown_0xa03e450c: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa03e450c, original_name='Unknown'
        ),
    })
    attack_angle_limit: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7b9a0bb4, original_name='AttackAngleLimit'
        ),
    })
    unknown_0x99bb2559: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x99bb2559, original_name='Unknown'
        ),
    })
    unknown_0xd6c8eac2: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd6c8eac2, original_name='Unknown'
        ),
    })
    unknown_0x2a5449ba: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2a5449ba, original_name='Unknown'
        ),
    })
    hearing_radius: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed69488f, original_name='HearingRadius'
        ),
    })
    unknown_0x399d1eaa: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x399d1eaa, original_name='Unknown'
        ),
    })
    unknown_0xbce16644: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xbce16644, original_name='Unknown'
        ),
    })
    unknown_0x142433d3: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x142433d3, original_name='Unknown'
        ),
    })
    unknown_0xb6cc0063: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb6cc0063, original_name='Unknown'
        ),
    })
    unknown_0xe601f7bd: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe601f7bd, original_name='Unknown'
        ),
    })
    unknown_0x09207f51: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x09207f51, original_name='Unknown'
        ),
    })
    unknown_0x2107e4fb: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2107e4fb, original_name='Unknown'
        ),
    })
    unknown_struct33: UnknownStruct33 = dataclasses.field(default_factory=UnknownStruct33, metadata={
        'reflection': FieldReflection[UnknownStruct33](
            UnknownStruct33, id=0x07e9d446, original_name='UnknownStruct33', from_json=UnknownStruct33.from_json, to_json=UnknownStruct33.to_json
        ),
    })
    unknown_struct34: UnknownStruct34 = dataclasses.field(default_factory=UnknownStruct34, metadata={
        'reflection': FieldReflection[UnknownStruct34](
            UnknownStruct34, id=0x3da35851, original_name='UnknownStruct34', from_json=UnknownStruct34.from_json, to_json=UnknownStruct34.to_json
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
        return 'MNNG'

    @classmethod
    def modules(cls) -> list[str]:
        return ['GeomBlobV2.rel', 'MinorIng.rel']

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
        if property_count != 20:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size, default_override={'min_attack_range': 4.5, 'max_attack_range': 30.0, 'average_attack_time': 3.0, 'collision_height': 4.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x553b1339
        projectile_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0, 'di_knock_back_power': 3.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef485db9
        projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa03e450c
        unknown_0xa03e450c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b9a0bb4
        attack_angle_limit = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x99bb2559
        unknown_0x99bb2559 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd6c8eac2
        unknown_0xd6c8eac2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2a5449ba
        unknown_0x2a5449ba = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed69488f
        hearing_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x399d1eaa
        unknown_0x399d1eaa = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbce16644
        unknown_0xbce16644 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x142433d3
        unknown_0x142433d3 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb6cc0063
        unknown_0xb6cc0063 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe601f7bd
        unknown_0xe601f7bd = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x09207f51
        unknown_0x09207f51 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2107e4fb
        unknown_0x2107e4fb = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x07e9d446
        unknown_struct33 = UnknownStruct33.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3da35851
        unknown_struct34 = UnknownStruct34.from_stream(data, property_size)
    
        return cls(editor_properties, patterned, actor_information, projectile_damage, projectile, unknown_0xa03e450c, attack_angle_limit, unknown_0x99bb2559, unknown_0xd6c8eac2, unknown_0x2a5449ba, hearing_radius, unknown_0x399d1eaa, unknown_0xbce16644, unknown_0x142433d3, unknown_0xb6cc0063, unknown_0xe601f7bd, unknown_0x09207f51, unknown_0x2107e4fb, unknown_struct33, unknown_struct34)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x14')  # 20 properties

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
        self.patterned.to_stream(data, default_override={'min_attack_range': 4.5, 'max_attack_range': 30.0, 'average_attack_time': 3.0, 'collision_height': 4.0})
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

        data.write(b'\xa0>E\x0c')  # 0xa03e450c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa03e450c))

        data.write(b'{\x9a\x0b\xb4')  # 0x7b9a0bb4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_angle_limit))

        data.write(b'\x99\xbb%Y')  # 0x99bb2559
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x99bb2559))

        data.write(b'\xd6\xc8\xea\xc2')  # 0xd6c8eac2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd6c8eac2))

        data.write(b'*TI\xba')  # 0x2a5449ba
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2a5449ba))

        data.write(b'\xediH\x8f')  # 0xed69488f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hearing_radius))

        data.write(b'9\x9d\x1e\xaa')  # 0x399d1eaa
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x399d1eaa))

        data.write(b'\xbc\xe1fD')  # 0xbce16644
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xbce16644))

        data.write(b'\x14$3\xd3')  # 0x142433d3
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x142433d3))

        data.write(b'\xb6\xcc\x00c')  # 0xb6cc0063
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xb6cc0063))

        data.write(b'\xe6\x01\xf7\xbd')  # 0xe601f7bd
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xe601f7bd))

        data.write(b'\t \x7fQ')  # 0x9207f51
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x09207f51))

        data.write(b'!\x07\xe4\xfb')  # 0x2107e4fb
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x2107e4fb))

        data.write(b'\x07\xe9\xd4F')  # 0x7e9d446
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct33.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'=\xa3XQ')  # 0x3da35851
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct34.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MinorIngJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            projectile_damage=DamageInfo.from_json(json_data['projectile_damage']),
            projectile=json_data['projectile'],
            unknown_0xa03e450c=json_data['unknown_0xa03e450c'],
            attack_angle_limit=json_data['attack_angle_limit'],
            unknown_0x99bb2559=json_data['unknown_0x99bb2559'],
            unknown_0xd6c8eac2=json_data['unknown_0xd6c8eac2'],
            unknown_0x2a5449ba=json_data['unknown_0x2a5449ba'],
            hearing_radius=json_data['hearing_radius'],
            unknown_0x399d1eaa=json_data['unknown_0x399d1eaa'],
            unknown_0xbce16644=json_data['unknown_0xbce16644'],
            unknown_0x142433d3=json_data['unknown_0x142433d3'],
            unknown_0xb6cc0063=json_data['unknown_0xb6cc0063'],
            unknown_0xe601f7bd=json_data['unknown_0xe601f7bd'],
            unknown_0x09207f51=json_data['unknown_0x09207f51'],
            unknown_0x2107e4fb=json_data['unknown_0x2107e4fb'],
            unknown_struct33=UnknownStruct33.from_json(json_data['unknown_struct33']),
            unknown_struct34=UnknownStruct34.from_json(json_data['unknown_struct34']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'patterned': self.patterned.to_json(),
            'actor_information': self.actor_information.to_json(),
            'projectile_damage': self.projectile_damage.to_json(),
            'projectile': self.projectile,
            'unknown_0xa03e450c': self.unknown_0xa03e450c,
            'attack_angle_limit': self.attack_angle_limit,
            'unknown_0x99bb2559': self.unknown_0x99bb2559,
            'unknown_0xd6c8eac2': self.unknown_0xd6c8eac2,
            'unknown_0x2a5449ba': self.unknown_0x2a5449ba,
            'hearing_radius': self.hearing_radius,
            'unknown_0x399d1eaa': self.unknown_0x399d1eaa,
            'unknown_0xbce16644': self.unknown_0xbce16644,
            'unknown_0x142433d3': self.unknown_0x142433d3,
            'unknown_0xb6cc0063': self.unknown_0xb6cc0063,
            'unknown_0xe601f7bd': self.unknown_0xe601f7bd,
            'unknown_0x09207f51': self.unknown_0x09207f51,
            'unknown_0x2107e4fb': self.unknown_0x2107e4fb,
            'unknown_struct33': self.unknown_struct33.to_json(),
            'unknown_struct34': self.unknown_struct34.to_json(),
        }

    def _dependencies_for_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.projectile)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self.projectile_damage.dependencies_for, "projectile_damage", "DamageInfo"),
            (self._dependencies_for_projectile, "projectile", "AssetId"),
            (self.unknown_struct33.dependencies_for, "unknown_struct33", "UnknownStruct33"),
            (self.unknown_struct34.dependencies_for, "unknown_struct34", "UnknownStruct34"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for MinorIng.{field_name} ({field_type}): {e}"
                )


def _decode_patterned(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'min_attack_range': 4.5, 'max_attack_range': 30.0, 'average_attack_time': 3.0, 'collision_height': 4.0})


def _decode_projectile_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0, 'di_knock_back_power': 3.0})


def _decode_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0xa03e450c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_angle_limit(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x99bb2559(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd6c8eac2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2a5449ba(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hearing_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x399d1eaa(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xbce16644(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x142433d3(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xb6cc0063(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xe601f7bd(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x09207f51(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x2107e4fb(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xb3774750: ('patterned', _decode_patterned),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0x553b1339: ('projectile_damage', _decode_projectile_damage),
    0xef485db9: ('projectile', _decode_projectile),
    0xa03e450c: ('unknown_0xa03e450c', _decode_unknown_0xa03e450c),
    0x7b9a0bb4: ('attack_angle_limit', _decode_attack_angle_limit),
    0x99bb2559: ('unknown_0x99bb2559', _decode_unknown_0x99bb2559),
    0xd6c8eac2: ('unknown_0xd6c8eac2', _decode_unknown_0xd6c8eac2),
    0x2a5449ba: ('unknown_0x2a5449ba', _decode_unknown_0x2a5449ba),
    0xed69488f: ('hearing_radius', _decode_hearing_radius),
    0x399d1eaa: ('unknown_0x399d1eaa', _decode_unknown_0x399d1eaa),
    0xbce16644: ('unknown_0xbce16644', _decode_unknown_0xbce16644),
    0x142433d3: ('unknown_0x142433d3', _decode_unknown_0x142433d3),
    0xb6cc0063: ('unknown_0xb6cc0063', _decode_unknown_0xb6cc0063),
    0xe601f7bd: ('unknown_0xe601f7bd', _decode_unknown_0xe601f7bd),
    0x9207f51: ('unknown_0x09207f51', _decode_unknown_0x09207f51),
    0x2107e4fb: ('unknown_0x2107e4fb', _decode_unknown_0x2107e4fb),
    0x7e9d446: ('unknown_struct33', UnknownStruct33.from_stream),
    0x3da35851: ('unknown_struct34', UnknownStruct34.from_stream),
}
