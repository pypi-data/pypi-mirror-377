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
from retro_data_structures.properties.prime.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class WorldTeleporterJson(typing_extensions.TypedDict):
        name: str
        active: bool
        world: int
        area: int
        player_model: json_util.JsonObject
        player_scale: json_util.JsonValue
        elevator_platform_model: int
        elevator_platform_scale: json_util.JsonValue
        elevator_background_model: int
        elevator_background_scale: json_util.JsonValue
        upward_elevator: bool
        elevator_sound: int
        sound_volume: int
        unknown_sound_related: int
        show_text_instead_of_cutscene: bool
        font: int
        string: int
        fade_in_from_out_to_white: bool
        character_fade_in_time: float
        characters_per_second: float
        delay_before_showing_text: float
    

@dataclasses.dataclass()
class WorldTeleporter(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    active: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000001, original_name='Active'
        ),
    })
    world: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['MLVL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000002, original_name='World'
        ),
    })
    area: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['MREA'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000003, original_name='Area'
        ),
    })
    player_model: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x00000004, original_name='Player Model', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    player_scale: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000005, original_name='Player Scale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    elevator_platform_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000006, original_name='Elevator Platform Model'
        ),
    })
    elevator_platform_scale: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000007, original_name='Elevator Platform Scale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    elevator_background_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000008, original_name='Elevator Background Model'
        ),
    })
    elevator_background_scale: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000009, original_name='Elevator Background Scale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    upward_elevator: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000a, original_name='Upward Elevator'
        ),
    })
    elevator_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x0000000b, original_name='Elevator Sound'
        ),
    })
    sound_volume: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000c, original_name='Sound Volume'
        ),
    })
    unknown_sound_related: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000d, original_name='Unknown (Sound-Related)'
        ),
    })
    show_text_instead_of_cutscene: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000e, original_name='Show Text Instead Of Cutscene'
        ),
    })
    font: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['FONT'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000f, original_name='Font'
        ),
    })
    string: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['STRG'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000010, original_name='String'
        ),
    })
    fade_in_from_out_to_white: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000011, original_name='Fade In From/Out To White'
        ),
    })
    character_fade_in_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000012, original_name='Character Fade In Time'
        ),
    })
    characters_per_second: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000013, original_name='Characters Per Second'
        ),
    })
    delay_before_showing_text: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000014, original_name='Delay Before Showing Text'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    def get_name(self) -> str | None:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    @classmethod
    def object_type(cls) -> int:
        return 0x62

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        active = struct.unpack('>?', data.read(1))[0]
        world = struct.unpack(">L", data.read(4))[0]
        area = struct.unpack(">L", data.read(4))[0]
        player_model = AnimationParameters.from_stream(data, property_size)
        player_scale = Vector.from_stream(data)
        elevator_platform_model = struct.unpack(">L", data.read(4))[0]
        elevator_platform_scale = Vector.from_stream(data)
        elevator_background_model = struct.unpack(">L", data.read(4))[0]
        elevator_background_scale = Vector.from_stream(data)
        upward_elevator = struct.unpack('>?', data.read(1))[0]
        elevator_sound = struct.unpack('>l', data.read(4))[0]
        sound_volume = struct.unpack('>l', data.read(4))[0]
        unknown_sound_related = struct.unpack('>l', data.read(4))[0]
        show_text_instead_of_cutscene = struct.unpack('>?', data.read(1))[0]
        font = struct.unpack(">L", data.read(4))[0]
        string = struct.unpack(">L", data.read(4))[0]
        fade_in_from_out_to_white = struct.unpack('>?', data.read(1))[0]
        character_fade_in_time = struct.unpack('>f', data.read(4))[0]
        characters_per_second = struct.unpack('>f', data.read(4))[0]
        delay_before_showing_text = struct.unpack('>f', data.read(4))[0]
        return cls(name, active, world, area, player_model, player_scale, elevator_platform_model, elevator_platform_scale, elevator_background_model, elevator_background_scale, upward_elevator, elevator_sound, sound_volume, unknown_sound_related, show_text_instead_of_cutscene, font, string, fade_in_from_out_to_white, character_fade_in_time, characters_per_second, delay_before_showing_text)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x15')  # 21 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>?', self.active))
        data.write(struct.pack(">L", self.world))
        data.write(struct.pack(">L", self.area))
        self.player_model.to_stream(data)
        self.player_scale.to_stream(data)
        data.write(struct.pack(">L", self.elevator_platform_model))
        self.elevator_platform_scale.to_stream(data)
        data.write(struct.pack(">L", self.elevator_background_model))
        self.elevator_background_scale.to_stream(data)
        data.write(struct.pack('>?', self.upward_elevator))
        data.write(struct.pack('>l', self.elevator_sound))
        data.write(struct.pack('>l', self.sound_volume))
        data.write(struct.pack('>l', self.unknown_sound_related))
        data.write(struct.pack('>?', self.show_text_instead_of_cutscene))
        data.write(struct.pack(">L", self.font))
        data.write(struct.pack(">L", self.string))
        data.write(struct.pack('>?', self.fade_in_from_out_to_white))
        data.write(struct.pack('>f', self.character_fade_in_time))
        data.write(struct.pack('>f', self.characters_per_second))
        data.write(struct.pack('>f', self.delay_before_showing_text))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("WorldTeleporterJson", data)
        return cls(
            name=json_data['name'],
            active=json_data['active'],
            world=json_data['world'],
            area=json_data['area'],
            player_model=AnimationParameters.from_json(json_data['player_model']),
            player_scale=Vector.from_json(json_data['player_scale']),
            elevator_platform_model=json_data['elevator_platform_model'],
            elevator_platform_scale=Vector.from_json(json_data['elevator_platform_scale']),
            elevator_background_model=json_data['elevator_background_model'],
            elevator_background_scale=Vector.from_json(json_data['elevator_background_scale']),
            upward_elevator=json_data['upward_elevator'],
            elevator_sound=json_data['elevator_sound'],
            sound_volume=json_data['sound_volume'],
            unknown_sound_related=json_data['unknown_sound_related'],
            show_text_instead_of_cutscene=json_data['show_text_instead_of_cutscene'],
            font=json_data['font'],
            string=json_data['string'],
            fade_in_from_out_to_white=json_data['fade_in_from_out_to_white'],
            character_fade_in_time=json_data['character_fade_in_time'],
            characters_per_second=json_data['characters_per_second'],
            delay_before_showing_text=json_data['delay_before_showing_text'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'active': self.active,
            'world': self.world,
            'area': self.area,
            'player_model': self.player_model.to_json(),
            'player_scale': self.player_scale.to_json(),
            'elevator_platform_model': self.elevator_platform_model,
            'elevator_platform_scale': self.elevator_platform_scale.to_json(),
            'elevator_background_model': self.elevator_background_model,
            'elevator_background_scale': self.elevator_background_scale.to_json(),
            'upward_elevator': self.upward_elevator,
            'elevator_sound': self.elevator_sound,
            'sound_volume': self.sound_volume,
            'unknown_sound_related': self.unknown_sound_related,
            'show_text_instead_of_cutscene': self.show_text_instead_of_cutscene,
            'font': self.font,
            'string': self.string,
            'fade_in_from_out_to_white': self.fade_in_from_out_to_white,
            'character_fade_in_time': self.character_fade_in_time,
            'characters_per_second': self.characters_per_second,
            'delay_before_showing_text': self.delay_before_showing_text,
        }

    def _dependencies_for_elevator_platform_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.elevator_platform_model)

    def _dependencies_for_elevator_background_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.elevator_background_model)

    def _dependencies_for_elevator_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.elevator_sound)

    def _dependencies_for_font(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.font)

    def _dependencies_for_string(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.string)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.player_model.dependencies_for, "player_model", "AnimationParameters"),
            (self._dependencies_for_elevator_platform_model, "elevator_platform_model", "AssetId"),
            (self._dependencies_for_elevator_background_model, "elevator_background_model", "AssetId"),
            (self._dependencies_for_elevator_sound, "elevator_sound", "int"),
            (self._dependencies_for_font, "font", "AssetId"),
            (self._dependencies_for_string, "string", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for WorldTeleporter.{field_name} ({field_type}): {e}"
                )
