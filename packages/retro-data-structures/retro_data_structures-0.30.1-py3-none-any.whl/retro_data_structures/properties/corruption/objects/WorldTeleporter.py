# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class WorldTeleporterJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        world: int
        area: int
        type: int
        ship: json_util.JsonObject
        camera: json_util.JsonObject
        skybox: int
        char_0x05014c61: json_util.JsonObject
        unknown_0xf9ef55d4: json_util.JsonObject
        char_0x3c79e121: json_util.JsonObject
        unknown_0x8e718724: json_util.JsonObject
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
        from_skybox: str
        from_ship: json_util.JsonObject
        from_camera: json_util.JsonObject
        to_skybox: str
        to_ship: json_util.JsonObject
        to_camera: json_util.JsonObject
        ship_grapple: int
        transition_sound: int
        volume: float
        pan: float
        transition_sound2: int
        volume2: float
        pan2: float
        unknown_0x5657ca1c: bool
        min_transition_time: float
    

class Type(enum.IntEnum):
    Unknown1 = 4190668287
    Unknown2 = 3649059742
    Unknown3 = 2346587055
    Unknown4 = 3272497734
    Unknown5 = 4170916833

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


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
    type: Type = dataclasses.field(default=Type.Unknown1, metadata={
        'reflection': FieldReflection[Type](
            Type, id=0x474bcce3, original_name='Type', from_json=Type.from_json, to_json=Type.to_json
        ),
    })
    ship: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xa9496551, original_name='Ship', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    camera: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xbbef4d0d, original_name='Camera', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    skybox: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xccefc618, original_name='Skybox'
        ),
    })
    char_0x05014c61: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x05014c61, original_name='CHAR', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    unknown_0xf9ef55d4: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xf9ef55d4, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    char_0x3c79e121: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x3c79e121, original_name='CHAR', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    unknown_0x8e718724: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x8e718724, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
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
    from_skybox: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x2e26702d, original_name='From_Skybox'
        ),
    })
    from_ship: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x53963a68, original_name='From_Ship', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    from_camera: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x4ebf760d, original_name='From_Camera', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    to_skybox: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x61930573, original_name='To_Skybox'
        ),
    })
    to_ship: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x5d7e79a1, original_name='To_Ship', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    to_camera: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xbb5204c8, original_name='To_Camera', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    ship_grapple: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb7dcd0ca, original_name='ShipGrapple'
        ),
    })
    transition_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x04d03e41, original_name='TransitionSound'
        ),
    })
    volume: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc7a7f189, original_name='Volume'
        ),
    })
    pan: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdf4353a3, original_name='Pan'
        ),
    })
    transition_sound2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x8dff5674, original_name='TransitionSound2'
        ),
    })
    volume2: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x31fa1fe0, original_name='Volume2'
        ),
    })
    pan2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xea593294, original_name='Pan2'
        ),
    })
    unknown_0x5657ca1c: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5657ca1c, original_name='Unknown'
        ),
    })
    min_transition_time: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbd6a406d, original_name='MinTransitionTime'
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
        return 'TEL1'

    @classmethod
    def modules(cls) -> list[str]:
        return ['RSO_ScriptWorldTeleporter.rso']

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
        if property_count != 37:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x31ec14bc
        world = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe0c17804
        area = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x474bcce3
        type = Type.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa9496551
        ship = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbbef4d0d
        camera = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xccefc618
        skybox = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x05014c61
        char_0x05014c61 = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf9ef55d4
        unknown_0xf9ef55d4 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3c79e121
        char_0x3c79e121 = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8e718724
        unknown_0x8e718724 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c176dd6
        display_font = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9182250c
        string = struct.unpack(">Q", data.read(8))[0]
    
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
        assert property_id == 0x2e26702d
        from_skybox = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x53963a68
        from_ship = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ebf760d
        from_camera = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x61930573
        to_skybox = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5d7e79a1
        to_ship = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbb5204c8
        to_camera = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb7dcd0ca
        ship_grapple = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x04d03e41
        transition_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc7a7f189
        volume = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdf4353a3
        pan = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8dff5674
        transition_sound2 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x31fa1fe0
        volume2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xea593294
        pan2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5657ca1c
        unknown_0x5657ca1c = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbd6a406d
        min_transition_time = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, world, area, type, ship, camera, skybox, char_0x05014c61, unknown_0xf9ef55d4, char_0x3c79e121, unknown_0x8e718724, display_font, string, is_fade_white, character_fade_time, characters_per_second, start_delay, audio_stream, display_subtitles, end_delay, subtitle_fade_in_delay, subtitle_fade_time, from_skybox, from_ship, from_camera, to_skybox, to_ship, to_camera, ship_grapple, transition_sound, volume, pan, transition_sound2, volume2, pan2, unknown_0x5657ca1c, min_transition_time)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00%')  # 37 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'1\xec\x14\xbc')  # 0x31ec14bc
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.world))

        data.write(b'\xe0\xc1x\x04')  # 0xe0c17804
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.area))

        data.write(b'GK\xcc\xe3')  # 0x474bcce3
        data.write(b'\x00\x04')  # size
        self.type.to_stream(data)

        data.write(b'\xa9IeQ')  # 0xa9496551
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ship.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbb\xefM\r')  # 0xbbef4d0d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.camera.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xcc\xef\xc6\x18')  # 0xccefc618
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.skybox))

        data.write(b'\x05\x01La')  # 0x5014c61
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.char_0x05014c61.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf9\xefU\xd4')  # 0xf9ef55d4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xf9ef55d4.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'<y\xe1!')  # 0x3c79e121
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.char_0x3c79e121.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8eq\x87$')  # 0x8e718724
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x8e718724.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'l\x17m\xd6')  # 0x6c176dd6
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.display_font))

        data.write(b'\x91\x82%\x0c')  # 0x9182250c
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.string))

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

        data.write(b'.&p-')  # 0x2e26702d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.from_skybox.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'S\x96:h')  # 0x53963a68
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.from_ship.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'N\xbfv\r')  # 0x4ebf760d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.from_camera.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'a\x93\x05s')  # 0x61930573
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.to_skybox.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b']~y\xa1')  # 0x5d7e79a1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.to_ship.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbbR\x04\xc8')  # 0xbb5204c8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.to_camera.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb7\xdc\xd0\xca')  # 0xb7dcd0ca
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ship_grapple))

        data.write(b'\x04\xd0>A')  # 0x4d03e41
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.transition_sound))

        data.write(b'\xc7\xa7\xf1\x89')  # 0xc7a7f189
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.volume))

        data.write(b'\xdfCS\xa3')  # 0xdf4353a3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pan))

        data.write(b'\x8d\xffVt')  # 0x8dff5674
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.transition_sound2))

        data.write(b'1\xfa\x1f\xe0')  # 0x31fa1fe0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.volume2))

        data.write(b'\xeaY2\x94')  # 0xea593294
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pan2))

        data.write(b'VW\xca\x1c')  # 0x5657ca1c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x5657ca1c))

        data.write(b'\xbdj@m')  # 0xbd6a406d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_transition_time))

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
            type=Type.from_json(json_data['type']),
            ship=AnimationParameters.from_json(json_data['ship']),
            camera=AnimationParameters.from_json(json_data['camera']),
            skybox=json_data['skybox'],
            char_0x05014c61=AnimationParameters.from_json(json_data['char_0x05014c61']),
            unknown_0xf9ef55d4=Spline.from_json(json_data['unknown_0xf9ef55d4']),
            char_0x3c79e121=AnimationParameters.from_json(json_data['char_0x3c79e121']),
            unknown_0x8e718724=Spline.from_json(json_data['unknown_0x8e718724']),
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
            from_skybox=json_data['from_skybox'],
            from_ship=AnimationParameters.from_json(json_data['from_ship']),
            from_camera=AnimationParameters.from_json(json_data['from_camera']),
            to_skybox=json_data['to_skybox'],
            to_ship=AnimationParameters.from_json(json_data['to_ship']),
            to_camera=AnimationParameters.from_json(json_data['to_camera']),
            ship_grapple=json_data['ship_grapple'],
            transition_sound=json_data['transition_sound'],
            volume=json_data['volume'],
            pan=json_data['pan'],
            transition_sound2=json_data['transition_sound2'],
            volume2=json_data['volume2'],
            pan2=json_data['pan2'],
            unknown_0x5657ca1c=json_data['unknown_0x5657ca1c'],
            min_transition_time=json_data['min_transition_time'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'world': self.world,
            'area': self.area,
            'type': self.type.to_json(),
            'ship': self.ship.to_json(),
            'camera': self.camera.to_json(),
            'skybox': self.skybox,
            'char_0x05014c61': self.char_0x05014c61.to_json(),
            'unknown_0xf9ef55d4': self.unknown_0xf9ef55d4.to_json(),
            'char_0x3c79e121': self.char_0x3c79e121.to_json(),
            'unknown_0x8e718724': self.unknown_0x8e718724.to_json(),
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
            'from_skybox': self.from_skybox,
            'from_ship': self.from_ship.to_json(),
            'from_camera': self.from_camera.to_json(),
            'to_skybox': self.to_skybox,
            'to_ship': self.to_ship.to_json(),
            'to_camera': self.to_camera.to_json(),
            'ship_grapple': self.ship_grapple,
            'transition_sound': self.transition_sound,
            'volume': self.volume,
            'pan': self.pan,
            'transition_sound2': self.transition_sound2,
            'volume2': self.volume2,
            'pan2': self.pan2,
            'unknown_0x5657ca1c': self.unknown_0x5657ca1c,
            'min_transition_time': self.min_transition_time,
        }


def _decode_world(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_area(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_type(data: typing.BinaryIO, property_size: int) -> Type:
    return Type.from_stream(data)


def _decode_skybox(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_display_font(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_string(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


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


def _decode_from_skybox(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_to_skybox(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_ship_grapple(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_transition_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_volume(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_pan(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_transition_sound2(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_volume2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_pan2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5657ca1c(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_min_transition_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x31ec14bc: ('world', _decode_world),
    0xe0c17804: ('area', _decode_area),
    0x474bcce3: ('type', _decode_type),
    0xa9496551: ('ship', AnimationParameters.from_stream),
    0xbbef4d0d: ('camera', AnimationParameters.from_stream),
    0xccefc618: ('skybox', _decode_skybox),
    0x5014c61: ('char_0x05014c61', AnimationParameters.from_stream),
    0xf9ef55d4: ('unknown_0xf9ef55d4', Spline.from_stream),
    0x3c79e121: ('char_0x3c79e121', AnimationParameters.from_stream),
    0x8e718724: ('unknown_0x8e718724', Spline.from_stream),
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
    0x2e26702d: ('from_skybox', _decode_from_skybox),
    0x53963a68: ('from_ship', AnimationParameters.from_stream),
    0x4ebf760d: ('from_camera', AnimationParameters.from_stream),
    0x61930573: ('to_skybox', _decode_to_skybox),
    0x5d7e79a1: ('to_ship', AnimationParameters.from_stream),
    0xbb5204c8: ('to_camera', AnimationParameters.from_stream),
    0xb7dcd0ca: ('ship_grapple', _decode_ship_grapple),
    0x4d03e41: ('transition_sound', _decode_transition_sound),
    0xc7a7f189: ('volume', _decode_volume),
    0xdf4353a3: ('pan', _decode_pan),
    0x8dff5674: ('transition_sound2', _decode_transition_sound2),
    0x31fa1fe0: ('volume2', _decode_volume2),
    0xea593294: ('pan2', _decode_pan2),
    0x5657ca1c: ('unknown_0x5657ca1c', _decode_unknown_0x5657ca1c),
    0xbd6a406d: ('min_transition_time', _decode_min_transition_time),
}
