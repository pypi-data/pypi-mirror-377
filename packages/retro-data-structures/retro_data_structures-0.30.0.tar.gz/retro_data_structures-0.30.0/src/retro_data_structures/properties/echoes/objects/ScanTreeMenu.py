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
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ScanTreeMenuJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        name_string_table: int
        name_string_name: str
        unknown_0x0261a4e0: int
        menu_options_string_table: int
        option_1_string_name: str
        unknown_0x50bce632: int
        option_2_string_name: str
        unknown_0x420949dc: int
        option_3_string_name: str
        unknown_0xfab52eb9: int
        option_4_string_name: str
        unknown_0x67621600: int
    

@dataclasses.dataclass()
class ScanTreeMenu(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    name_string_table: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['STRG'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x46219bac, original_name='Name String Table'
        ),
    })
    name_string_name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x32698bd6, original_name='Name String Name'
        ),
    })
    unknown_0x0261a4e0: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0261a4e0, original_name='Unknown'
        ),
    })
    menu_options_string_table: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['STRG'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa6a874e9, original_name='Menu Options String Table'
        ),
    })
    option_1_string_name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x30531924, original_name='Option 1 String Name'
        ),
    })
    unknown_0x50bce632: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x50bce632, original_name='Unknown'
        ),
    })
    option_2_string_name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x01bb03b9, original_name='Option 2 String Name'
        ),
    })
    unknown_0x420949dc: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x420949dc, original_name='Unknown'
        ),
    })
    option_3_string_name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xa7cc080d, original_name='Option 3 String Name'
        ),
    })
    unknown_0xfab52eb9: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xfab52eb9, original_name='Unknown'
        ),
    })
    option_4_string_name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x626b3683, original_name='Option 4 String Name'
        ),
    })
    unknown_0x67621600: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x67621600, original_name='Unknown'
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
        return 'SCMN'

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
        if property_count != 13:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x46219bac
        name_string_table = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x32698bd6
        name_string_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0261a4e0
        unknown_0x0261a4e0 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa6a874e9
        menu_options_string_table = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x30531924
        option_1_string_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x50bce632
        unknown_0x50bce632 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01bb03b9
        option_2_string_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x420949dc
        unknown_0x420949dc = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa7cc080d
        option_3_string_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfab52eb9
        unknown_0xfab52eb9 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x626b3683
        option_4_string_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x67621600
        unknown_0x67621600 = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, name_string_table, name_string_name, unknown_0x0261a4e0, menu_options_string_table, option_1_string_name, unknown_0x50bce632, option_2_string_name, unknown_0x420949dc, option_3_string_name, unknown_0xfab52eb9, option_4_string_name, unknown_0x67621600)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\r')  # 13 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'F!\x9b\xac')  # 0x46219bac
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.name_string_table))

        data.write(b'2i\x8b\xd6')  # 0x32698bd6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.name_string_name.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x02a\xa4\xe0')  # 0x261a4e0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x0261a4e0))

        data.write(b'\xa6\xa8t\xe9')  # 0xa6a874e9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.menu_options_string_table))

        data.write(b'0S\x19$')  # 0x30531924
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.option_1_string_name.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'P\xbc\xe62')  # 0x50bce632
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x50bce632))

        data.write(b'\x01\xbb\x03\xb9')  # 0x1bb03b9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.option_2_string_name.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'B\tI\xdc')  # 0x420949dc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x420949dc))

        data.write(b'\xa7\xcc\x08\r')  # 0xa7cc080d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.option_3_string_name.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfa\xb5.\xb9')  # 0xfab52eb9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xfab52eb9))

        data.write(b'bk6\x83')  # 0x626b3683
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.option_4_string_name.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'gb\x16\x00')  # 0x67621600
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x67621600))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ScanTreeMenuJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            name_string_table=json_data['name_string_table'],
            name_string_name=json_data['name_string_name'],
            unknown_0x0261a4e0=json_data['unknown_0x0261a4e0'],
            menu_options_string_table=json_data['menu_options_string_table'],
            option_1_string_name=json_data['option_1_string_name'],
            unknown_0x50bce632=json_data['unknown_0x50bce632'],
            option_2_string_name=json_data['option_2_string_name'],
            unknown_0x420949dc=json_data['unknown_0x420949dc'],
            option_3_string_name=json_data['option_3_string_name'],
            unknown_0xfab52eb9=json_data['unknown_0xfab52eb9'],
            option_4_string_name=json_data['option_4_string_name'],
            unknown_0x67621600=json_data['unknown_0x67621600'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'name_string_table': self.name_string_table,
            'name_string_name': self.name_string_name,
            'unknown_0x0261a4e0': self.unknown_0x0261a4e0,
            'menu_options_string_table': self.menu_options_string_table,
            'option_1_string_name': self.option_1_string_name,
            'unknown_0x50bce632': self.unknown_0x50bce632,
            'option_2_string_name': self.option_2_string_name,
            'unknown_0x420949dc': self.unknown_0x420949dc,
            'option_3_string_name': self.option_3_string_name,
            'unknown_0xfab52eb9': self.unknown_0xfab52eb9,
            'option_4_string_name': self.option_4_string_name,
            'unknown_0x67621600': self.unknown_0x67621600,
        }

    def _dependencies_for_name_string_table(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.name_string_table)

    def _dependencies_for_menu_options_string_table(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.menu_options_string_table)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self._dependencies_for_name_string_table, "name_string_table", "AssetId"),
            (self._dependencies_for_menu_options_string_table, "menu_options_string_table", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for ScanTreeMenu.{field_name} ({field_type}): {e}"
                )


def _decode_name_string_table(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_name_string_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0x0261a4e0(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_menu_options_string_table(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_option_1_string_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0x50bce632(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_option_2_string_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0x420949dc(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_option_3_string_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0xfab52eb9(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_option_4_string_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0x67621600(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x46219bac: ('name_string_table', _decode_name_string_table),
    0x32698bd6: ('name_string_name', _decode_name_string_name),
    0x261a4e0: ('unknown_0x0261a4e0', _decode_unknown_0x0261a4e0),
    0xa6a874e9: ('menu_options_string_table', _decode_menu_options_string_table),
    0x30531924: ('option_1_string_name', _decode_option_1_string_name),
    0x50bce632: ('unknown_0x50bce632', _decode_unknown_0x50bce632),
    0x1bb03b9: ('option_2_string_name', _decode_option_2_string_name),
    0x420949dc: ('unknown_0x420949dc', _decode_unknown_0x420949dc),
    0xa7cc080d: ('option_3_string_name', _decode_option_3_string_name),
    0xfab52eb9: ('unknown_0xfab52eb9', _decode_unknown_0xfab52eb9),
    0x626b3683: ('option_4_string_name', _decode_option_4_string_name),
    0x67621600: ('unknown_0x67621600', _decode_unknown_0x67621600),
}
