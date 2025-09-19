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
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.echoes.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.echoes.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class AmbientAIJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        collision_box: json_util.JsonValue
        collision_offset: json_util.JsonValue
        mass: float
        health: json_util.JsonObject
        vulnerability: json_util.JsonObject
        animation_information: json_util.JsonObject
        actor_information: json_util.JsonObject
        detect_radius: float
        explode_radius: float
        unknown_0xbfe017de: int
        unknown_0xed5f16ac: int
    

@dataclasses.dataclass()
class AmbientAI(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    collision_box: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0xf344c0b0, original_name='CollisionBox', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    collision_offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x2e686c2a, original_name='CollisionOffset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    mass: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x75dbb375, original_name='Mass'
        ),
    })
    health: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0xcf90d15e, original_name='Health', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x7b71ae90, original_name='Vulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    animation_information: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xe25fb08c, original_name='AnimationInformation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    detect_radius: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa7d00780, original_name='DetectRadius'
        ),
    })
    explode_radius: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd4d52631, original_name='ExplodeRadius'
        ),
    })
    unknown_0xbfe017de: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xbfe017de, original_name='Unknown'
        ),
    })
    unknown_0xed5f16ac: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xed5f16ac, original_name='Unknown'
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
        return 'AMIA'

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
        if property_count != 12:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf344c0b0
        collision_box = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2e686c2a
        collision_offset = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x75dbb375
        mass = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf90d15e
        health = HealthInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b71ae90
        vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe25fb08c
        animation_information = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa7d00780
        detect_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd4d52631
        explode_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbfe017de
        unknown_0xbfe017de = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed5f16ac
        unknown_0xed5f16ac = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, collision_box, collision_offset, mass, health, vulnerability, animation_information, actor_information, detect_radius, explode_radius, unknown_0xbfe017de, unknown_0xed5f16ac)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0c')  # 12 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf3D\xc0\xb0')  # 0xf344c0b0
        data.write(b'\x00\x0c')  # size
        self.collision_box.to_stream(data)

        data.write(b'.hl*')  # 0x2e686c2a
        data.write(b'\x00\x0c')  # size
        self.collision_offset.to_stream(data)

        data.write(b'u\xdb\xb3u')  # 0x75dbb375
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.mass))

        data.write(b'\xcf\x90\xd1^')  # 0xcf90d15e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.health.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'{q\xae\x90')  # 0x7b71ae90
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe2_\xb0\x8c')  # 0xe25fb08c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.animation_information.to_stream(data)
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

        data.write(b'\xa7\xd0\x07\x80')  # 0xa7d00780
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.detect_radius))

        data.write(b'\xd4\xd5&1')  # 0xd4d52631
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.explode_radius))

        data.write(b'\xbf\xe0\x17\xde')  # 0xbfe017de
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xbfe017de))

        data.write(b'\xed_\x16\xac')  # 0xed5f16ac
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xed5f16ac))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AmbientAIJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            collision_box=Vector.from_json(json_data['collision_box']),
            collision_offset=Vector.from_json(json_data['collision_offset']),
            mass=json_data['mass'],
            health=HealthInfo.from_json(json_data['health']),
            vulnerability=DamageVulnerability.from_json(json_data['vulnerability']),
            animation_information=AnimationParameters.from_json(json_data['animation_information']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            detect_radius=json_data['detect_radius'],
            explode_radius=json_data['explode_radius'],
            unknown_0xbfe017de=json_data['unknown_0xbfe017de'],
            unknown_0xed5f16ac=json_data['unknown_0xed5f16ac'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'collision_box': self.collision_box.to_json(),
            'collision_offset': self.collision_offset.to_json(),
            'mass': self.mass,
            'health': self.health.to_json(),
            'vulnerability': self.vulnerability.to_json(),
            'animation_information': self.animation_information.to_json(),
            'actor_information': self.actor_information.to_json(),
            'detect_radius': self.detect_radius,
            'explode_radius': self.explode_radius,
            'unknown_0xbfe017de': self.unknown_0xbfe017de,
            'unknown_0xed5f16ac': self.unknown_0xed5f16ac,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.health.dependencies_for, "health", "HealthInfo"),
            (self.vulnerability.dependencies_for, "vulnerability", "DamageVulnerability"),
            (self.animation_information.dependencies_for, "animation_information", "AnimationParameters"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for AmbientAI.{field_name} ({field_type}): {e}"
                )


def _decode_collision_box(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_collision_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_mass(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_detect_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_explode_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbfe017de(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xed5f16ac(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xf344c0b0: ('collision_box', _decode_collision_box),
    0x2e686c2a: ('collision_offset', _decode_collision_offset),
    0x75dbb375: ('mass', _decode_mass),
    0xcf90d15e: ('health', HealthInfo.from_stream),
    0x7b71ae90: ('vulnerability', DamageVulnerability.from_stream),
    0xe25fb08c: ('animation_information', AnimationParameters.from_stream),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0xa7d00780: ('detect_radius', _decode_detect_radius),
    0xd4d52631: ('explode_radius', _decode_explode_radius),
    0xbfe017de: ('unknown_0xbfe017de', _decode_unknown_0xbfe017de),
    0xed5f16ac: ('unknown_0xed5f16ac', _decode_unknown_0xed5f16ac),
}
