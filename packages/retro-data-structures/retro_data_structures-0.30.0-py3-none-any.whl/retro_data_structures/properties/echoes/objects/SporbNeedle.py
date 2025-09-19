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
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class SporbNeedleJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        actor_information: json_util.JsonObject
        model: int
        initial_speed: float
        mass: float
        attack_damage: json_util.JsonObject
        fuse_time: float
        trail_effect: int
        explosion_effect: int
        launch_sound: int
        flight_sound: int
        hit_player_sound: int
        collision_sound: int
        explosion_sound: int
    

@dataclasses.dataclass()
class SporbNeedle(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc27ffa8f, original_name='Model'
        ),
    })
    initial_speed: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcb14d97c, original_name='InitialSpeed'
        ),
    })
    mass: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x75dbb375, original_name='Mass'
        ),
    })
    attack_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x66dcaacb, original_name='AttackDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    fuse_time: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5cc14b87, original_name='FuseTime'
        ),
    })
    trail_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x36eee791, original_name='TrailEffect'
        ),
    })
    explosion_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf8b7ba26, original_name='ExplosionEffect'
        ),
    })
    launch_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x0dd66f77, original_name='LaunchSound'
        ),
    })
    flight_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x1bc7f2fc, original_name='FlightSound'
        ),
    })
    hit_player_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xdfbd90e1, original_name='HitPlayerSound'
        ),
    })
    collision_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x92caa97d, original_name='CollisionSound'
        ),
    })
    explosion_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x6028d1cc, original_name='ExplosionSound'
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
        return 'SPBN'

    @classmethod
    def modules(cls) -> list[str]:
        return ['Sporb.rel']

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
        if property_count != 14:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc27ffa8f
        model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcb14d97c
        initial_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x75dbb375
        mass = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x66dcaacb
        attack_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 9, 'di_damage': 5.0, 'di_knock_back_power': 2.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5cc14b87
        fuse_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x36eee791
        trail_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf8b7ba26
        explosion_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0dd66f77
        launch_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1bc7f2fc
        flight_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdfbd90e1
        hit_player_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x92caa97d
        collision_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6028d1cc
        explosion_sound = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, actor_information, model, initial_speed, mass, attack_damage, fuse_time, trail_effect, explosion_effect, launch_sound, flight_sound, hit_player_sound, collision_sound, explosion_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0e')  # 14 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
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

        data.write(b'\xc2\x7f\xfa\x8f')  # 0xc27ffa8f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.model))

        data.write(b'\xcb\x14\xd9|')  # 0xcb14d97c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.initial_speed))

        data.write(b'u\xdb\xb3u')  # 0x75dbb375
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.mass))

        data.write(b'f\xdc\xaa\xcb')  # 0x66dcaacb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.attack_damage.to_stream(data, default_override={'di_weapon_type': 9, 'di_damage': 5.0, 'di_knock_back_power': 2.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\\\xc1K\x87')  # 0x5cc14b87
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fuse_time))

        data.write(b'6\xee\xe7\x91')  # 0x36eee791
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.trail_effect))

        data.write(b'\xf8\xb7\xba&')  # 0xf8b7ba26
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.explosion_effect))

        data.write(b'\r\xd6ow')  # 0xdd66f77
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.launch_sound))

        data.write(b'\x1b\xc7\xf2\xfc')  # 0x1bc7f2fc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.flight_sound))

        data.write(b'\xdf\xbd\x90\xe1')  # 0xdfbd90e1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.hit_player_sound))

        data.write(b'\x92\xca\xa9}')  # 0x92caa97d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.collision_sound))

        data.write(b'`(\xd1\xcc')  # 0x6028d1cc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.explosion_sound))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SporbNeedleJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            model=json_data['model'],
            initial_speed=json_data['initial_speed'],
            mass=json_data['mass'],
            attack_damage=DamageInfo.from_json(json_data['attack_damage']),
            fuse_time=json_data['fuse_time'],
            trail_effect=json_data['trail_effect'],
            explosion_effect=json_data['explosion_effect'],
            launch_sound=json_data['launch_sound'],
            flight_sound=json_data['flight_sound'],
            hit_player_sound=json_data['hit_player_sound'],
            collision_sound=json_data['collision_sound'],
            explosion_sound=json_data['explosion_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'actor_information': self.actor_information.to_json(),
            'model': self.model,
            'initial_speed': self.initial_speed,
            'mass': self.mass,
            'attack_damage': self.attack_damage.to_json(),
            'fuse_time': self.fuse_time,
            'trail_effect': self.trail_effect,
            'explosion_effect': self.explosion_effect,
            'launch_sound': self.launch_sound,
            'flight_sound': self.flight_sound,
            'hit_player_sound': self.hit_player_sound,
            'collision_sound': self.collision_sound,
            'explosion_sound': self.explosion_sound,
        }

    def _dependencies_for_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model)

    def _dependencies_for_trail_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.trail_effect)

    def _dependencies_for_explosion_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.explosion_effect)

    def _dependencies_for_launch_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.launch_sound)

    def _dependencies_for_flight_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.flight_sound)

    def _dependencies_for_hit_player_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.hit_player_sound)

    def _dependencies_for_collision_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.collision_sound)

    def _dependencies_for_explosion_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.explosion_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self._dependencies_for_model, "model", "AssetId"),
            (self.attack_damage.dependencies_for, "attack_damage", "DamageInfo"),
            (self._dependencies_for_trail_effect, "trail_effect", "AssetId"),
            (self._dependencies_for_explosion_effect, "explosion_effect", "AssetId"),
            (self._dependencies_for_launch_sound, "launch_sound", "int"),
            (self._dependencies_for_flight_sound, "flight_sound", "int"),
            (self._dependencies_for_hit_player_sound, "hit_player_sound", "int"),
            (self._dependencies_for_collision_sound, "collision_sound", "int"),
            (self._dependencies_for_explosion_sound, "explosion_sound", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for SporbNeedle.{field_name} ({field_type}): {e}"
                )


def _decode_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_initial_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_mass(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 9, 'di_damage': 5.0, 'di_knock_back_power': 2.0})


def _decode_fuse_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_trail_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_explosion_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_launch_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_flight_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_hit_player_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_collision_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_explosion_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0xc27ffa8f: ('model', _decode_model),
    0xcb14d97c: ('initial_speed', _decode_initial_speed),
    0x75dbb375: ('mass', _decode_mass),
    0x66dcaacb: ('attack_damage', _decode_attack_damage),
    0x5cc14b87: ('fuse_time', _decode_fuse_time),
    0x36eee791: ('trail_effect', _decode_trail_effect),
    0xf8b7ba26: ('explosion_effect', _decode_explosion_effect),
    0xdd66f77: ('launch_sound', _decode_launch_sound),
    0x1bc7f2fc: ('flight_sound', _decode_flight_sound),
    0xdfbd90e1: ('hit_player_sound', _decode_hit_player_sound),
    0x92caa97d: ('collision_sound', _decode_collision_sound),
    0x6028d1cc: ('explosion_sound', _decode_explosion_sound),
}
