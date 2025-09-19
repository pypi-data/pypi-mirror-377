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
import retro_data_structures.enums.corruption as enums
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class ShipCommandIconJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        unknown_0x11234a3f: bool
        unknown_0x4b198e71: bool
        scannable: bool
        function: int
        disabled_texture: int
        category_texture: int
        specific_function_texture: int
        disabled_animation: json_util.JsonObject
        category_animation: json_util.JsonObject
        function_animation: json_util.JsonObject
        necessary_upgrade: int
        unknown_0x48ef8ade: int
        unknown_0x69a7e62c: float
        scan_sound: int
        executing_sound: int
        missile_empty: int
    

@dataclasses.dataclass()
class ShipCommandIcon(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    unknown_0x11234a3f: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x11234a3f, original_name='Unknown'
        ),
    })
    unknown_0x4b198e71: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x4b198e71, original_name='Unknown'
        ),
    })
    scannable: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x8b9b584c, original_name='Scannable'
        ),
    })
    function: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x95f8d644, original_name='Function'
        ),
    })
    disabled_texture: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc39f8936, original_name='DisabledTexture'
        ),
    })
    category_texture: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x222cf8ec, original_name='CategoryTexture'
        ),
    })
    specific_function_texture: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0bf00eb1, original_name='SpecificFunctionTexture'
        ),
    })
    disabled_animation: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x6d10c987, original_name='DisabledAnimation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    category_animation: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x97adb194, original_name='CategoryAnimation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    function_animation: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xa797679c, original_name='FunctionAnimation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    necessary_upgrade: enums.PlayerItemEnum = dataclasses.field(default=enums.PlayerItemEnum.PowerBeam, metadata={
        'reflection': FieldReflection[enums.PlayerItemEnum](
            enums.PlayerItemEnum, id=0x08072da5, original_name='NecessaryUpgrade', from_json=enums.PlayerItemEnum.from_json, to_json=enums.PlayerItemEnum.to_json
        ),
    })
    unknown_0x48ef8ade: int = dataclasses.field(default=4050431932, metadata={
        'reflection': FieldReflection[int](
            int, id=0x48ef8ade, original_name='Unknown'
        ),
    })  # Choice
    unknown_0x69a7e62c: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x69a7e62c, original_name='Unknown'
        ),
    })
    scan_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xce6a78c8, original_name='ScanSound'
        ),
    })
    executing_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x515460ac, original_name='ExecutingSound'
        ),
    })
    missile_empty: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x10289804, original_name='MissileEmpty'
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
        return 'SHCI'

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
        if property_count != 17:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x11234a3f
        unknown_0x11234a3f = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4b198e71
        unknown_0x4b198e71 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b9b584c
        scannable = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95f8d644
        function = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc39f8936
        disabled_texture = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x222cf8ec
        category_texture = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0bf00eb1
        specific_function_texture = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d10c987
        disabled_animation = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x97adb194
        category_animation = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa797679c
        function_animation = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x08072da5
        necessary_upgrade = enums.PlayerItemEnum.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x48ef8ade
        unknown_0x48ef8ade = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x69a7e62c
        unknown_0x69a7e62c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xce6a78c8
        scan_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x515460ac
        executing_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x10289804
        missile_empty = struct.unpack(">Q", data.read(8))[0]
    
        return cls(editor_properties, unknown_0x11234a3f, unknown_0x4b198e71, scannable, function, disabled_texture, category_texture, specific_function_texture, disabled_animation, category_animation, function_animation, necessary_upgrade, unknown_0x48ef8ade, unknown_0x69a7e62c, scan_sound, executing_sound, missile_empty)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x11')  # 17 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x11#J?')  # 0x11234a3f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x11234a3f))

        data.write(b'K\x19\x8eq')  # 0x4b198e71
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x4b198e71))

        data.write(b'\x8b\x9bXL')  # 0x8b9b584c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.scannable))

        data.write(b'\x95\xf8\xd6D')  # 0x95f8d644
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.function))

        data.write(b'\xc3\x9f\x896')  # 0xc39f8936
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.disabled_texture))

        data.write(b'",\xf8\xec')  # 0x222cf8ec
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.category_texture))

        data.write(b'\x0b\xf0\x0e\xb1')  # 0xbf00eb1
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.specific_function_texture))

        data.write(b'm\x10\xc9\x87')  # 0x6d10c987
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.disabled_animation.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x97\xad\xb1\x94')  # 0x97adb194
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.category_animation.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa7\x97g\x9c')  # 0xa797679c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.function_animation.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x08\x07-\xa5')  # 0x8072da5
        data.write(b'\x00\x04')  # size
        self.necessary_upgrade.to_stream(data)

        data.write(b'H\xef\x8a\xde')  # 0x48ef8ade
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.unknown_0x48ef8ade))

        data.write(b'i\xa7\xe6,')  # 0x69a7e62c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x69a7e62c))

        data.write(b'\xcejx\xc8')  # 0xce6a78c8
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.scan_sound))

        data.write(b'QT`\xac')  # 0x515460ac
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.executing_sound))

        data.write(b'\x10(\x98\x04')  # 0x10289804
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.missile_empty))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ShipCommandIconJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            unknown_0x11234a3f=json_data['unknown_0x11234a3f'],
            unknown_0x4b198e71=json_data['unknown_0x4b198e71'],
            scannable=json_data['scannable'],
            function=json_data['function'],
            disabled_texture=json_data['disabled_texture'],
            category_texture=json_data['category_texture'],
            specific_function_texture=json_data['specific_function_texture'],
            disabled_animation=AnimationParameters.from_json(json_data['disabled_animation']),
            category_animation=AnimationParameters.from_json(json_data['category_animation']),
            function_animation=AnimationParameters.from_json(json_data['function_animation']),
            necessary_upgrade=enums.PlayerItemEnum.from_json(json_data['necessary_upgrade']),
            unknown_0x48ef8ade=json_data['unknown_0x48ef8ade'],
            unknown_0x69a7e62c=json_data['unknown_0x69a7e62c'],
            scan_sound=json_data['scan_sound'],
            executing_sound=json_data['executing_sound'],
            missile_empty=json_data['missile_empty'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'unknown_0x11234a3f': self.unknown_0x11234a3f,
            'unknown_0x4b198e71': self.unknown_0x4b198e71,
            'scannable': self.scannable,
            'function': self.function,
            'disabled_texture': self.disabled_texture,
            'category_texture': self.category_texture,
            'specific_function_texture': self.specific_function_texture,
            'disabled_animation': self.disabled_animation.to_json(),
            'category_animation': self.category_animation.to_json(),
            'function_animation': self.function_animation.to_json(),
            'necessary_upgrade': self.necessary_upgrade.to_json(),
            'unknown_0x48ef8ade': self.unknown_0x48ef8ade,
            'unknown_0x69a7e62c': self.unknown_0x69a7e62c,
            'scan_sound': self.scan_sound,
            'executing_sound': self.executing_sound,
            'missile_empty': self.missile_empty,
        }


def _decode_unknown_0x11234a3f(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x4b198e71(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_scannable(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_function(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_disabled_texture(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_category_texture(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_specific_function_texture(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_necessary_upgrade(data: typing.BinaryIO, property_size: int) -> enums.PlayerItemEnum:
    return enums.PlayerItemEnum.from_stream(data)


def _decode_unknown_0x48ef8ade(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x69a7e62c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scan_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_executing_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_missile_empty(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x11234a3f: ('unknown_0x11234a3f', _decode_unknown_0x11234a3f),
    0x4b198e71: ('unknown_0x4b198e71', _decode_unknown_0x4b198e71),
    0x8b9b584c: ('scannable', _decode_scannable),
    0x95f8d644: ('function', _decode_function),
    0xc39f8936: ('disabled_texture', _decode_disabled_texture),
    0x222cf8ec: ('category_texture', _decode_category_texture),
    0xbf00eb1: ('specific_function_texture', _decode_specific_function_texture),
    0x6d10c987: ('disabled_animation', AnimationParameters.from_stream),
    0x97adb194: ('category_animation', AnimationParameters.from_stream),
    0xa797679c: ('function_animation', AnimationParameters.from_stream),
    0x8072da5: ('necessary_upgrade', _decode_necessary_upgrade),
    0x48ef8ade: ('unknown_0x48ef8ade', _decode_unknown_0x48ef8ade),
    0x69a7e62c: ('unknown_0x69a7e62c', _decode_unknown_0x69a7e62c),
    0xce6a78c8: ('scan_sound', _decode_scan_sound),
    0x515460ac: ('executing_sound', _decode_executing_sound),
    0x10289804: ('missile_empty', _decode_missile_empty),
}
