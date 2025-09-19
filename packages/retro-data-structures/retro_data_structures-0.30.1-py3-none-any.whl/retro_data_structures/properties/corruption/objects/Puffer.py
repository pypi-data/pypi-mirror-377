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
from retro_data_structures.properties.corruption.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.corruption.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class PufferJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        actor_information: json_util.JsonObject
        patterned: json_util.JsonObject
        is_orbitable: bool
        hover_speed: float
        cloud_effect: int
        cloud_damage: json_util.JsonObject
        cloud_steam: int
        cloud_steam_alpha: float
        orbit_interpolant_followed: bool
        cloud_in_dark: bool
        cloud_in_echo: bool
        explosion_damage: json_util.JsonObject
        turn_sound: int
        death_sound: int
    

@dataclasses.dataclass()
class Puffer(BaseObjectType):
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
    patterned: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0xb3774750, original_name='Patterned', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    is_orbitable: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x826bec80, original_name='IsOrbitable'
        ),
    })
    hover_speed: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x845ef489, original_name='HoverSpeed'
        ),
    })
    cloud_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x670b9a1f, original_name='CloudEffect'
        ),
    })
    cloud_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xe8619082, original_name='CloudDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    cloud_steam: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1aa418f4, original_name='CloudSteam'
        ),
    })
    cloud_steam_alpha: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc9a55479, original_name='CloudSteamAlpha'
        ),
    })
    orbit_interpolant_followed: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x98647f20, original_name='OrbitInterpolantFollowed?'
        ),
    })
    cloud_in_dark: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x8a30112f, original_name='CloudInDark'
        ),
    })
    cloud_in_echo: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x86c887a5, original_name='CloudInEcho'
        ),
    })
    explosion_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xdeff74ea, original_name='ExplosionDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    turn_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc4c39403, original_name='TurnSound'
        ),
    })
    death_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc7c3f610, original_name='DeathSound'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'PUFR'

    @classmethod
    def modules(cls) -> list[str]:
        return ['RSO_Puffer.rso']

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
        if property_count != 15:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x826bec80
        is_orbitable = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x845ef489
        hover_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x670b9a1f
        cloud_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8619082
        cloud_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1aa418f4
        cloud_steam = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc9a55479
        cloud_steam_alpha = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x98647f20
        orbit_interpolant_followed = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8a30112f
        cloud_in_dark = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x86c887a5
        cloud_in_echo = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdeff74ea
        explosion_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc4c39403
        turn_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc7c3f610
        death_sound = struct.unpack(">Q", data.read(8))[0]
    
        return cls(editor_properties, actor_information, patterned, is_orbitable, hover_speed, cloud_effect, cloud_damage, cloud_steam, cloud_steam_alpha, orbit_interpolant_followed, cloud_in_dark, cloud_in_echo, explosion_damage, turn_sound, death_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0f')  # 15 properties

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

        data.write(b'\xb3wGP')  # 0xb3774750
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x82k\xec\x80')  # 0x826bec80
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_orbitable))

        data.write(b'\x84^\xf4\x89')  # 0x845ef489
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_speed))

        data.write(b'g\x0b\x9a\x1f')  # 0x670b9a1f
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cloud_effect))

        data.write(b'\xe8a\x90\x82')  # 0xe8619082
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.cloud_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1a\xa4\x18\xf4')  # 0x1aa418f4
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cloud_steam))

        data.write(b'\xc9\xa5Ty')  # 0xc9a55479
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cloud_steam_alpha))

        data.write(b'\x98d\x7f ')  # 0x98647f20
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.orbit_interpolant_followed))

        data.write(b'\x8a0\x11/')  # 0x8a30112f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.cloud_in_dark))

        data.write(b'\x86\xc8\x87\xa5')  # 0x86c887a5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.cloud_in_echo))

        data.write(b'\xde\xfft\xea')  # 0xdeff74ea
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.explosion_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc4\xc3\x94\x03')  # 0xc4c39403
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.turn_sound))

        data.write(b'\xc7\xc3\xf6\x10')  # 0xc7c3f610
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.death_sound))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PufferJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            is_orbitable=json_data['is_orbitable'],
            hover_speed=json_data['hover_speed'],
            cloud_effect=json_data['cloud_effect'],
            cloud_damage=DamageInfo.from_json(json_data['cloud_damage']),
            cloud_steam=json_data['cloud_steam'],
            cloud_steam_alpha=json_data['cloud_steam_alpha'],
            orbit_interpolant_followed=json_data['orbit_interpolant_followed'],
            cloud_in_dark=json_data['cloud_in_dark'],
            cloud_in_echo=json_data['cloud_in_echo'],
            explosion_damage=DamageInfo.from_json(json_data['explosion_damage']),
            turn_sound=json_data['turn_sound'],
            death_sound=json_data['death_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'actor_information': self.actor_information.to_json(),
            'patterned': self.patterned.to_json(),
            'is_orbitable': self.is_orbitable,
            'hover_speed': self.hover_speed,
            'cloud_effect': self.cloud_effect,
            'cloud_damage': self.cloud_damage.to_json(),
            'cloud_steam': self.cloud_steam,
            'cloud_steam_alpha': self.cloud_steam_alpha,
            'orbit_interpolant_followed': self.orbit_interpolant_followed,
            'cloud_in_dark': self.cloud_in_dark,
            'cloud_in_echo': self.cloud_in_echo,
            'explosion_damage': self.explosion_damage.to_json(),
            'turn_sound': self.turn_sound,
            'death_sound': self.death_sound,
        }


def _decode_is_orbitable(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_hover_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_cloud_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cloud_steam(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cloud_steam_alpha(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_interpolant_followed(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_cloud_in_dark(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_cloud_in_echo(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_turn_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_death_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0xb3774750: ('patterned', PatternedAITypedef.from_stream),
    0x826bec80: ('is_orbitable', _decode_is_orbitable),
    0x845ef489: ('hover_speed', _decode_hover_speed),
    0x670b9a1f: ('cloud_effect', _decode_cloud_effect),
    0xe8619082: ('cloud_damage', DamageInfo.from_stream),
    0x1aa418f4: ('cloud_steam', _decode_cloud_steam),
    0xc9a55479: ('cloud_steam_alpha', _decode_cloud_steam_alpha),
    0x98647f20: ('orbit_interpolant_followed', _decode_orbit_interpolant_followed),
    0x8a30112f: ('cloud_in_dark', _decode_cloud_in_dark),
    0x86c887a5: ('cloud_in_echo', _decode_cloud_in_echo),
    0xdeff74ea: ('explosion_damage', DamageInfo.from_stream),
    0xc4c39403: ('turn_sound', _decode_turn_sound),
    0xc7c3f610: ('death_sound', _decode_death_sound),
}
