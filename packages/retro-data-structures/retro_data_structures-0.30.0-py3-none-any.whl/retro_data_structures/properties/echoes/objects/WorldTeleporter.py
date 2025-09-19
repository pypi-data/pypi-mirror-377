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
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class WorldTeleporterJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        world: int
        area: int
        animation_information: json_util.JsonObject
        player_scale: json_util.JsonValue
        platform: int
        platform_scale: json_util.JsonValue
        shaft: int
        shaft_scale: json_util.JsonValue
        unknown_0x2e997e0b: bool
        sound_group: int
        elevator: int
        volume: int
        pan: int
        is_teleport: bool
        display_font: int
        string: int
        is_fade_white: bool
        character_fade_time: float
        characters_per_second: float
        start_delay: float
        audio_stream: str
        display_subtitles: bool
        end_delay: float
        subtitle_fade_in_delay: float
        subtitle_fade_time: float
        unknown_0x5657ca1c: bool
    

@dataclasses.dataclass()
class WorldTeleporter(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    world: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['MLVL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x31ec14bc, original_name='World'
        ),
    })
    area: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['MREA'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe0c17804, original_name='Area'
        ),
    })
    animation_information: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xe25fb08c, original_name='AnimationInformation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    player_scale: Vector = dataclasses.field(default_factory=lambda: Vector(x=1.0, y=1.0, z=1.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0xe56ba365, original_name='PlayerScale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    platform: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9703f961, original_name='Platform'
        ),
    })
    platform_scale: Vector = dataclasses.field(default_factory=lambda: Vector(x=1.0, y=1.0, z=1.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0xca1d9615, original_name='PlatformScale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    shaft: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x09f4b212, original_name='Shaft'
        ),
    })
    shaft_scale: Vector = dataclasses.field(default_factory=lambda: Vector(x=1.0, y=1.0, z=1.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x84b43bc6, original_name='ShaftScale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_0x2e997e0b: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2e997e0b, original_name='Unknown'
        ),
    })
    sound_group: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['AGSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3133c626, original_name='SoundGroup'
        ),
    })
    elevator: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xc11fdb3b, original_name='Elevator'
        ),
    })
    volume: int = dataclasses.field(default=127, metadata={
        'reflection': FieldReflection[int](
            int, id=0x80c66c37, original_name='Volume'
        ),
    })
    pan: int = dataclasses.field(default=64, metadata={
        'reflection': FieldReflection[int](
            int, id=0xd6088bc5, original_name='Pan'
        ),
    })
    is_teleport: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xea974b08, original_name='IsTeleport'
        ),
    })
    display_font: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['FONT'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6c176dd6, original_name='DisplayFont'
        ),
    })
    string: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['STRG'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9182250c, original_name='String'
        ),
    })
    is_fade_white: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc54082e8, original_name='IsFadeWhite'
        ),
    })
    character_fade_time: float = dataclasses.field(default=0.009999999776482582, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd9b2394f, original_name='CharacterFadeTime'
        ),
    })
    characters_per_second: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x353582bd, original_name='CharactersPerSecond'
        ),
    })
    start_delay: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x196e17d9, original_name='StartDelay'
        ),
    })
    audio_stream: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xb28f37b1, original_name='AudioStream'
        ),
    })
    display_subtitles: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa1c4e7f8, original_name='DisplaySubtitles'
        ),
    })
    end_delay: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x79cda57c, original_name='EndDelay'
        ),
    })
    subtitle_fade_in_delay: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0b5240e3, original_name='SubtitleFadeInDelay'
        ),
    })
    subtitle_fade_time: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x71786711, original_name='SubtitleFadeTime'
        ),
    })
    unknown_0x5657ca1c: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5657ca1c, original_name='Unknown'
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
        return 'TEL1'

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
        if property_count != 27:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x31ec14bc
        world = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe0c17804
        area = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe25fb08c
        animation_information = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe56ba365
        player_scale = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9703f961
        platform = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xca1d9615
        platform_scale = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x09f4b212
        shaft = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x84b43bc6
        shaft_scale = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2e997e0b
        unknown_0x2e997e0b = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3133c626
        sound_group = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc11fdb3b
        elevator = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80c66c37
        volume = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd6088bc5
        pan = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xea974b08
        is_teleport = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c176dd6
        display_font = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9182250c
        string = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc54082e8
        is_fade_white = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd9b2394f
        character_fade_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x353582bd
        characters_per_second = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x196e17d9
        start_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb28f37b1
        audio_stream = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa1c4e7f8
        display_subtitles = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x79cda57c
        end_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0b5240e3
        subtitle_fade_in_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71786711
        subtitle_fade_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5657ca1c
        unknown_0x5657ca1c = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, world, area, animation_information, player_scale, platform, platform_scale, shaft, shaft_scale, unknown_0x2e997e0b, sound_group, elevator, volume, pan, is_teleport, display_font, string, is_fade_white, character_fade_time, characters_per_second, start_delay, audio_stream, display_subtitles, end_delay, subtitle_fade_in_delay, subtitle_fade_time, unknown_0x5657ca1c)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x1b')  # 27 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'1\xec\x14\xbc')  # 0x31ec14bc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.world))

        data.write(b'\xe0\xc1x\x04')  # 0xe0c17804
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.area))

        data.write(b'\xe2_\xb0\x8c')  # 0xe25fb08c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.animation_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe5k\xa3e')  # 0xe56ba365
        data.write(b'\x00\x0c')  # size
        self.player_scale.to_stream(data)

        data.write(b'\x97\x03\xf9a')  # 0x9703f961
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.platform))

        data.write(b'\xca\x1d\x96\x15')  # 0xca1d9615
        data.write(b'\x00\x0c')  # size
        self.platform_scale.to_stream(data)

        data.write(b'\t\xf4\xb2\x12')  # 0x9f4b212
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.shaft))

        data.write(b'\x84\xb4;\xc6')  # 0x84b43bc6
        data.write(b'\x00\x0c')  # size
        self.shaft_scale.to_stream(data)

        data.write(b'.\x99~\x0b')  # 0x2e997e0b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x2e997e0b))

        data.write(b'13\xc6&')  # 0x3133c626
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.sound_group))

        data.write(b'\xc1\x1f\xdb;')  # 0xc11fdb3b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.elevator))

        data.write(b'\x80\xc6l7')  # 0x80c66c37
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.volume))

        data.write(b'\xd6\x08\x8b\xc5')  # 0xd6088bc5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.pan))

        data.write(b'\xea\x97K\x08')  # 0xea974b08
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_teleport))

        data.write(b'l\x17m\xd6')  # 0x6c176dd6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.display_font))

        data.write(b'\x91\x82%\x0c')  # 0x9182250c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.string))

        data.write(b'\xc5@\x82\xe8')  # 0xc54082e8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_fade_white))

        data.write(b'\xd9\xb29O')  # 0xd9b2394f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.character_fade_time))

        data.write(b'55\x82\xbd')  # 0x353582bd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.characters_per_second))

        data.write(b'\x19n\x17\xd9')  # 0x196e17d9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.start_delay))

        data.write(b'\xb2\x8f7\xb1')  # 0xb28f37b1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.audio_stream.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa1\xc4\xe7\xf8')  # 0xa1c4e7f8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.display_subtitles))

        data.write(b'y\xcd\xa5|')  # 0x79cda57c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.end_delay))

        data.write(b'\x0bR@\xe3')  # 0xb5240e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.subtitle_fade_in_delay))

        data.write(b'qxg\x11')  # 0x71786711
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.subtitle_fade_time))

        data.write(b'VW\xca\x1c')  # 0x5657ca1c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x5657ca1c))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("WorldTeleporterJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            world=json_data['world'],
            area=json_data['area'],
            animation_information=AnimationParameters.from_json(json_data['animation_information']),
            player_scale=Vector.from_json(json_data['player_scale']),
            platform=json_data['platform'],
            platform_scale=Vector.from_json(json_data['platform_scale']),
            shaft=json_data['shaft'],
            shaft_scale=Vector.from_json(json_data['shaft_scale']),
            unknown_0x2e997e0b=json_data['unknown_0x2e997e0b'],
            sound_group=json_data['sound_group'],
            elevator=json_data['elevator'],
            volume=json_data['volume'],
            pan=json_data['pan'],
            is_teleport=json_data['is_teleport'],
            display_font=json_data['display_font'],
            string=json_data['string'],
            is_fade_white=json_data['is_fade_white'],
            character_fade_time=json_data['character_fade_time'],
            characters_per_second=json_data['characters_per_second'],
            start_delay=json_data['start_delay'],
            audio_stream=json_data['audio_stream'],
            display_subtitles=json_data['display_subtitles'],
            end_delay=json_data['end_delay'],
            subtitle_fade_in_delay=json_data['subtitle_fade_in_delay'],
            subtitle_fade_time=json_data['subtitle_fade_time'],
            unknown_0x5657ca1c=json_data['unknown_0x5657ca1c'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'world': self.world,
            'area': self.area,
            'animation_information': self.animation_information.to_json(),
            'player_scale': self.player_scale.to_json(),
            'platform': self.platform,
            'platform_scale': self.platform_scale.to_json(),
            'shaft': self.shaft,
            'shaft_scale': self.shaft_scale.to_json(),
            'unknown_0x2e997e0b': self.unknown_0x2e997e0b,
            'sound_group': self.sound_group,
            'elevator': self.elevator,
            'volume': self.volume,
            'pan': self.pan,
            'is_teleport': self.is_teleport,
            'display_font': self.display_font,
            'string': self.string,
            'is_fade_white': self.is_fade_white,
            'character_fade_time': self.character_fade_time,
            'characters_per_second': self.characters_per_second,
            'start_delay': self.start_delay,
            'audio_stream': self.audio_stream,
            'display_subtitles': self.display_subtitles,
            'end_delay': self.end_delay,
            'subtitle_fade_in_delay': self.subtitle_fade_in_delay,
            'subtitle_fade_time': self.subtitle_fade_time,
            'unknown_0x5657ca1c': self.unknown_0x5657ca1c,
        }

    def _dependencies_for_platform(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.platform)

    def _dependencies_for_shaft(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.shaft)

    def _dependencies_for_sound_group(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.sound_group)

    def _dependencies_for_elevator(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.elevator)

    def _dependencies_for_display_font(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.display_font)

    def _dependencies_for_string(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.string)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.animation_information.dependencies_for, "animation_information", "AnimationParameters"),
            (self._dependencies_for_platform, "platform", "AssetId"),
            (self._dependencies_for_shaft, "shaft", "AssetId"),
            (self._dependencies_for_sound_group, "sound_group", "AssetId"),
            (self._dependencies_for_elevator, "elevator", "int"),
            (self._dependencies_for_display_font, "display_font", "AssetId"),
            (self._dependencies_for_string, "string", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for WorldTeleporter.{field_name} ({field_type}): {e}"
                )


def _decode_world(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_area(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_player_scale(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_platform(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_platform_scale(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_shaft(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_shaft_scale(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_unknown_0x2e997e0b(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_sound_group(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_elevator(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_volume(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_pan(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_is_teleport(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_display_font(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_string(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_is_fade_white(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_character_fade_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_characters_per_second(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_start_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_audio_stream(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_display_subtitles(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_end_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_subtitle_fade_in_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_subtitle_fade_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5657ca1c(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x31ec14bc: ('world', _decode_world),
    0xe0c17804: ('area', _decode_area),
    0xe25fb08c: ('animation_information', AnimationParameters.from_stream),
    0xe56ba365: ('player_scale', _decode_player_scale),
    0x9703f961: ('platform', _decode_platform),
    0xca1d9615: ('platform_scale', _decode_platform_scale),
    0x9f4b212: ('shaft', _decode_shaft),
    0x84b43bc6: ('shaft_scale', _decode_shaft_scale),
    0x2e997e0b: ('unknown_0x2e997e0b', _decode_unknown_0x2e997e0b),
    0x3133c626: ('sound_group', _decode_sound_group),
    0xc11fdb3b: ('elevator', _decode_elevator),
    0x80c66c37: ('volume', _decode_volume),
    0xd6088bc5: ('pan', _decode_pan),
    0xea974b08: ('is_teleport', _decode_is_teleport),
    0x6c176dd6: ('display_font', _decode_display_font),
    0x9182250c: ('string', _decode_string),
    0xc54082e8: ('is_fade_white', _decode_is_fade_white),
    0xd9b2394f: ('character_fade_time', _decode_character_fade_time),
    0x353582bd: ('characters_per_second', _decode_characters_per_second),
    0x196e17d9: ('start_delay', _decode_start_delay),
    0xb28f37b1: ('audio_stream', _decode_audio_stream),
    0xa1c4e7f8: ('display_subtitles', _decode_display_subtitles),
    0x79cda57c: ('end_delay', _decode_end_delay),
    0xb5240e3: ('subtitle_fade_in_delay', _decode_subtitle_fade_in_delay),
    0x71786711: ('subtitle_fade_time', _decode_subtitle_fade_time),
    0x5657ca1c: ('unknown_0x5657ca1c', _decode_unknown_0x5657ca1c),
}
