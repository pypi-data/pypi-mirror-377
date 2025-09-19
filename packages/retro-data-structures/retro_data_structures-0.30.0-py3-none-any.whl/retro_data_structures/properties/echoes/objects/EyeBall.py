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
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class EyeBallJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        patterned: json_util.JsonObject
        actor_information: json_util.JsonObject
        close_time: float
        fire_wait_time: float
        projectile: int
        ray_damage: json_util.JsonObject
        plasma_burn: int
        plasma_pulse: int
        plasma_texture: int
        plasma_glow: int
        laser_inner_color: json_util.JsonValue
        laser_outer_color: json_util.JsonValue
        unknown_0x81d14be8: int
        unknown_0x6e1320d6: int
        unknown_0x85249bd5: int
        unknown_0x6ae6f0eb: int
        laser_sound: int
        should_be_triggered: bool
        max_audible_distance: float
        drop_off: float
    

@dataclasses.dataclass()
class EyeBall(BaseObjectType):
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
    close_time: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd0d88ea6, original_name='CloseTime'
        ),
    })
    fire_wait_time: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc00cf821, original_name='FireWaitTime'
        ),
    })
    projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xef485db9, original_name='Projectile'
        ),
    })
    ray_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x22a9f2d2, original_name='RayDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    plasma_burn: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xbc19549c, original_name='PlasmaBurn'
        ),
    })
    plasma_pulse: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x28cd86fa, original_name='PlasmaPulse'
        ),
    })
    plasma_texture: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd7a1121d, original_name='PlasmaTexture'
        ),
    })
    plasma_glow: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb7aa958e, original_name='PlasmaGlow'
        ),
    })
    laser_inner_color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x643e5052, original_name='LaserInnerColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    laser_outer_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=1.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xe11643dd, original_name='LaserOuterColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x81d14be8: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x81d14be8, original_name='Unknown'
        ),
    })
    unknown_0x6e1320d6: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6e1320d6, original_name='Unknown'
        ),
    })
    unknown_0x85249bd5: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x85249bd5, original_name='Unknown'
        ),
    })
    unknown_0x6ae6f0eb: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6ae6f0eb, original_name='Unknown'
        ),
    })
    laser_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xe4780219, original_name='LaserSound'
        ),
    })
    should_be_triggered: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2e603ded, original_name='ShouldBeTriggered'
        ),
    })
    max_audible_distance: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x214e48a0, original_name='MaxAudibleDistance'
        ),
    })
    drop_off: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x08bf2e54, original_name='DropOff'
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
        return 'EYEB'

    @classmethod
    def modules(cls) -> list[str]:
        return ['EyeBall.rel']

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
        if property_count != 21:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd0d88ea6
        close_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc00cf821
        fire_wait_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef485db9
        projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x22a9f2d2
        ray_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbc19549c
        plasma_burn = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x28cd86fa
        plasma_pulse = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd7a1121d
        plasma_texture = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb7aa958e
        plasma_glow = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x643e5052
        laser_inner_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe11643dd
        laser_outer_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x81d14be8
        unknown_0x81d14be8 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6e1320d6
        unknown_0x6e1320d6 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x85249bd5
        unknown_0x85249bd5 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6ae6f0eb
        unknown_0x6ae6f0eb = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe4780219
        laser_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2e603ded
        should_be_triggered = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x214e48a0
        max_audible_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x08bf2e54
        drop_off = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, patterned, actor_information, close_time, fire_wait_time, projectile, ray_damage, plasma_burn, plasma_pulse, plasma_texture, plasma_glow, laser_inner_color, laser_outer_color, unknown_0x81d14be8, unknown_0x6e1320d6, unknown_0x85249bd5, unknown_0x6ae6f0eb, laser_sound, should_be_triggered, max_audible_distance, drop_off)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x15')  # 21 properties

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
        self.patterned.to_stream(data)
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

        data.write(b'\xd0\xd8\x8e\xa6')  # 0xd0d88ea6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.close_time))

        data.write(b'\xc0\x0c\xf8!')  # 0xc00cf821
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fire_wait_time))

        data.write(b'\xefH]\xb9')  # 0xef485db9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.projectile))

        data.write(b'"\xa9\xf2\xd2')  # 0x22a9f2d2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ray_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbc\x19T\x9c')  # 0xbc19549c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.plasma_burn))

        data.write(b'(\xcd\x86\xfa')  # 0x28cd86fa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.plasma_pulse))

        data.write(b'\xd7\xa1\x12\x1d')  # 0xd7a1121d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.plasma_texture))

        data.write(b'\xb7\xaa\x95\x8e')  # 0xb7aa958e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.plasma_glow))

        data.write(b'd>PR')  # 0x643e5052
        data.write(b'\x00\x10')  # size
        self.laser_inner_color.to_stream(data)

        data.write(b'\xe1\x16C\xdd')  # 0xe11643dd
        data.write(b'\x00\x10')  # size
        self.laser_outer_color.to_stream(data)

        data.write(b'\x81\xd1K\xe8')  # 0x81d14be8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x81d14be8))

        data.write(b'n\x13 \xd6')  # 0x6e1320d6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x6e1320d6))

        data.write(b'\x85$\x9b\xd5')  # 0x85249bd5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x85249bd5))

        data.write(b'j\xe6\xf0\xeb')  # 0x6ae6f0eb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x6ae6f0eb))

        data.write(b'\xe4x\x02\x19')  # 0xe4780219
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.laser_sound))

        data.write(b'.`=\xed')  # 0x2e603ded
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.should_be_triggered))

        data.write(b'!NH\xa0')  # 0x214e48a0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_audible_distance))

        data.write(b'\x08\xbf.T')  # 0x8bf2e54
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.drop_off))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("EyeBallJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            close_time=json_data['close_time'],
            fire_wait_time=json_data['fire_wait_time'],
            projectile=json_data['projectile'],
            ray_damage=DamageInfo.from_json(json_data['ray_damage']),
            plasma_burn=json_data['plasma_burn'],
            plasma_pulse=json_data['plasma_pulse'],
            plasma_texture=json_data['plasma_texture'],
            plasma_glow=json_data['plasma_glow'],
            laser_inner_color=Color.from_json(json_data['laser_inner_color']),
            laser_outer_color=Color.from_json(json_data['laser_outer_color']),
            unknown_0x81d14be8=json_data['unknown_0x81d14be8'],
            unknown_0x6e1320d6=json_data['unknown_0x6e1320d6'],
            unknown_0x85249bd5=json_data['unknown_0x85249bd5'],
            unknown_0x6ae6f0eb=json_data['unknown_0x6ae6f0eb'],
            laser_sound=json_data['laser_sound'],
            should_be_triggered=json_data['should_be_triggered'],
            max_audible_distance=json_data['max_audible_distance'],
            drop_off=json_data['drop_off'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'patterned': self.patterned.to_json(),
            'actor_information': self.actor_information.to_json(),
            'close_time': self.close_time,
            'fire_wait_time': self.fire_wait_time,
            'projectile': self.projectile,
            'ray_damage': self.ray_damage.to_json(),
            'plasma_burn': self.plasma_burn,
            'plasma_pulse': self.plasma_pulse,
            'plasma_texture': self.plasma_texture,
            'plasma_glow': self.plasma_glow,
            'laser_inner_color': self.laser_inner_color.to_json(),
            'laser_outer_color': self.laser_outer_color.to_json(),
            'unknown_0x81d14be8': self.unknown_0x81d14be8,
            'unknown_0x6e1320d6': self.unknown_0x6e1320d6,
            'unknown_0x85249bd5': self.unknown_0x85249bd5,
            'unknown_0x6ae6f0eb': self.unknown_0x6ae6f0eb,
            'laser_sound': self.laser_sound,
            'should_be_triggered': self.should_be_triggered,
            'max_audible_distance': self.max_audible_distance,
            'drop_off': self.drop_off,
        }

    def _dependencies_for_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.projectile)

    def _dependencies_for_plasma_burn(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.plasma_burn)

    def _dependencies_for_plasma_pulse(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.plasma_pulse)

    def _dependencies_for_plasma_texture(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.plasma_texture)

    def _dependencies_for_plasma_glow(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.plasma_glow)

    def _dependencies_for_laser_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.laser_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self._dependencies_for_projectile, "projectile", "AssetId"),
            (self.ray_damage.dependencies_for, "ray_damage", "DamageInfo"),
            (self._dependencies_for_plasma_burn, "plasma_burn", "AssetId"),
            (self._dependencies_for_plasma_pulse, "plasma_pulse", "AssetId"),
            (self._dependencies_for_plasma_texture, "plasma_texture", "AssetId"),
            (self._dependencies_for_plasma_glow, "plasma_glow", "AssetId"),
            (self._dependencies_for_laser_sound, "laser_sound", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for EyeBall.{field_name} ({field_type}): {e}"
                )


def _decode_close_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fire_wait_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_plasma_burn(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_plasma_pulse(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_plasma_texture(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_plasma_glow(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_laser_inner_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_laser_outer_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x81d14be8(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x6e1320d6(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x85249bd5(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x6ae6f0eb(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_laser_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_should_be_triggered(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_max_audible_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_drop_off(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xb3774750: ('patterned', PatternedAITypedef.from_stream),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0xd0d88ea6: ('close_time', _decode_close_time),
    0xc00cf821: ('fire_wait_time', _decode_fire_wait_time),
    0xef485db9: ('projectile', _decode_projectile),
    0x22a9f2d2: ('ray_damage', DamageInfo.from_stream),
    0xbc19549c: ('plasma_burn', _decode_plasma_burn),
    0x28cd86fa: ('plasma_pulse', _decode_plasma_pulse),
    0xd7a1121d: ('plasma_texture', _decode_plasma_texture),
    0xb7aa958e: ('plasma_glow', _decode_plasma_glow),
    0x643e5052: ('laser_inner_color', _decode_laser_inner_color),
    0xe11643dd: ('laser_outer_color', _decode_laser_outer_color),
    0x81d14be8: ('unknown_0x81d14be8', _decode_unknown_0x81d14be8),
    0x6e1320d6: ('unknown_0x6e1320d6', _decode_unknown_0x6e1320d6),
    0x85249bd5: ('unknown_0x85249bd5', _decode_unknown_0x85249bd5),
    0x6ae6f0eb: ('unknown_0x6ae6f0eb', _decode_unknown_0x6ae6f0eb),
    0xe4780219: ('laser_sound', _decode_laser_sound),
    0x2e603ded: ('should_be_triggered', _decode_should_be_triggered),
    0x214e48a0: ('max_audible_distance', _decode_max_audible_distance),
    0x8bf2e54: ('drop_off', _decode_drop_off),
}
