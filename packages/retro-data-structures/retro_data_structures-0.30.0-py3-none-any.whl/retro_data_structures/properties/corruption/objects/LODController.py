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
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class LODControllerJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        unknown_0x00b17e5f: int
        model01: int
        distance01: float
        model02: int
        distance02: float
        model03: int
        distance03: float
        model04: int
        distance04: float
        model05: int
        distance05: float
        model06: int
        distance06: float
        model07: int
        distance07: float
        model08: int
        distance08: float
        model09: int
        distance09: float
        model10: int
        distance10: float
        unknown_0xb67e3bf9: bool
    

@dataclasses.dataclass()
class LODController(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    unknown_0x00b17e5f: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00b17e5f, original_name='Unknown'
        ),
    })
    model01: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x03bee47e, original_name='Model01'
        ),
    })
    distance01: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa1018ef9, original_name='Distance01'
        ),
    })
    model02: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x852a96d0, original_name='Model02'
        ),
    })
    distance02: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2795fc57, original_name='Distance02'
        ),
    })
    model03: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4e764575, original_name='Model03'
        ),
    })
    distance03: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xecc92ff2, original_name='Distance03'
        ),
    })
    model04: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x537375cd, original_name='Model04'
        ),
    })
    distance04: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf1cc1f4a, original_name='Distance04'
        ),
    })
    model05: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x982fa668, original_name='Model05'
        ),
    })
    distance05: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3a90ccef, original_name='Distance05'
        ),
    })
    model06: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1ebbd4c6, original_name='Model06'
        ),
    })
    distance06: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbc04be41, original_name='Distance06'
        ),
    })
    model07: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd5e70763, original_name='Model07'
        ),
    })
    distance07: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x77586de4, original_name='Distance07'
        ),
    })
    model08: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x24b1b5b6, original_name='Model08'
        ),
    })
    distance08: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x860edf31, original_name='Distance08'
        ),
    })
    model09: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xefed6613, original_name='Model09'
        ),
    })
    distance09: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4d520c94, original_name='Distance09'
        ),
    })
    model10: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6e953c6f, original_name='Model10'
        ),
    })
    distance10: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcc2a56e8, original_name='Distance10'
        ),
    })
    unknown_0xb67e3bf9: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb67e3bf9, original_name='Unknown'
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
        return 'LODC'

    @classmethod
    def modules(cls) -> list[str]:
        return ['RSO_ScriptLODController.rso']

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
        if property_count != 23:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x00b17e5f
        unknown_0x00b17e5f = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x03bee47e
        model01 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa1018ef9
        distance01 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x852a96d0
        model02 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2795fc57
        distance02 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4e764575
        model03 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xecc92ff2
        distance03 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x537375cd
        model04 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf1cc1f4a
        distance04 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x982fa668
        model05 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3a90ccef
        distance05 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1ebbd4c6
        model06 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbc04be41
        distance06 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd5e70763
        model07 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x77586de4
        distance07 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x24b1b5b6
        model08 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x860edf31
        distance08 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xefed6613
        model09 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d520c94
        distance09 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6e953c6f
        model10 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcc2a56e8
        distance10 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb67e3bf9
        unknown_0xb67e3bf9 = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, unknown_0x00b17e5f, model01, distance01, model02, distance02, model03, distance03, model04, distance04, model05, distance05, model06, distance06, model07, distance07, model08, distance08, model09, distance09, model10, distance10, unknown_0xb67e3bf9)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x17')  # 23 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x00\xb1~_')  # 0xb17e5f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x00b17e5f))

        data.write(b'\x03\xbe\xe4~')  # 0x3bee47e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.model01))

        data.write(b'\xa1\x01\x8e\xf9')  # 0xa1018ef9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance01))

        data.write(b'\x85*\x96\xd0')  # 0x852a96d0
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.model02))

        data.write(b"'\x95\xfcW")  # 0x2795fc57
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance02))

        data.write(b'NvEu')  # 0x4e764575
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.model03))

        data.write(b'\xec\xc9/\xf2')  # 0xecc92ff2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance03))

        data.write(b'Ssu\xcd')  # 0x537375cd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.model04))

        data.write(b'\xf1\xcc\x1fJ')  # 0xf1cc1f4a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance04))

        data.write(b'\x98/\xa6h')  # 0x982fa668
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.model05))

        data.write(b':\x90\xcc\xef')  # 0x3a90ccef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance05))

        data.write(b'\x1e\xbb\xd4\xc6')  # 0x1ebbd4c6
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.model06))

        data.write(b'\xbc\x04\xbeA')  # 0xbc04be41
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance06))

        data.write(b'\xd5\xe7\x07c')  # 0xd5e70763
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.model07))

        data.write(b'wXm\xe4')  # 0x77586de4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance07))

        data.write(b'$\xb1\xb5\xb6')  # 0x24b1b5b6
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.model08))

        data.write(b'\x86\x0e\xdf1')  # 0x860edf31
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance08))

        data.write(b'\xef\xedf\x13')  # 0xefed6613
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.model09))

        data.write(b'MR\x0c\x94')  # 0x4d520c94
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance09))

        data.write(b'n\x95<o')  # 0x6e953c6f
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.model10))

        data.write(b'\xcc*V\xe8')  # 0xcc2a56e8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance10))

        data.write(b'\xb6~;\xf9')  # 0xb67e3bf9
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xb67e3bf9))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("LODControllerJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            unknown_0x00b17e5f=json_data['unknown_0x00b17e5f'],
            model01=json_data['model01'],
            distance01=json_data['distance01'],
            model02=json_data['model02'],
            distance02=json_data['distance02'],
            model03=json_data['model03'],
            distance03=json_data['distance03'],
            model04=json_data['model04'],
            distance04=json_data['distance04'],
            model05=json_data['model05'],
            distance05=json_data['distance05'],
            model06=json_data['model06'],
            distance06=json_data['distance06'],
            model07=json_data['model07'],
            distance07=json_data['distance07'],
            model08=json_data['model08'],
            distance08=json_data['distance08'],
            model09=json_data['model09'],
            distance09=json_data['distance09'],
            model10=json_data['model10'],
            distance10=json_data['distance10'],
            unknown_0xb67e3bf9=json_data['unknown_0xb67e3bf9'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'unknown_0x00b17e5f': self.unknown_0x00b17e5f,
            'model01': self.model01,
            'distance01': self.distance01,
            'model02': self.model02,
            'distance02': self.distance02,
            'model03': self.model03,
            'distance03': self.distance03,
            'model04': self.model04,
            'distance04': self.distance04,
            'model05': self.model05,
            'distance05': self.distance05,
            'model06': self.model06,
            'distance06': self.distance06,
            'model07': self.model07,
            'distance07': self.distance07,
            'model08': self.model08,
            'distance08': self.distance08,
            'model09': self.model09,
            'distance09': self.distance09,
            'model10': self.model10,
            'distance10': self.distance10,
            'unknown_0xb67e3bf9': self.unknown_0xb67e3bf9,
        }


def _decode_unknown_0x00b17e5f(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_model01(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_distance01(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_model02(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_distance02(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_model03(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_distance03(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_model04(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_distance04(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_model05(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_distance05(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_model06(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_distance06(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_model07(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_distance07(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_model08(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_distance08(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_model09(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_distance09(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_model10(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_distance10(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb67e3bf9(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xb17e5f: ('unknown_0x00b17e5f', _decode_unknown_0x00b17e5f),
    0x3bee47e: ('model01', _decode_model01),
    0xa1018ef9: ('distance01', _decode_distance01),
    0x852a96d0: ('model02', _decode_model02),
    0x2795fc57: ('distance02', _decode_distance02),
    0x4e764575: ('model03', _decode_model03),
    0xecc92ff2: ('distance03', _decode_distance03),
    0x537375cd: ('model04', _decode_model04),
    0xf1cc1f4a: ('distance04', _decode_distance04),
    0x982fa668: ('model05', _decode_model05),
    0x3a90ccef: ('distance05', _decode_distance05),
    0x1ebbd4c6: ('model06', _decode_model06),
    0xbc04be41: ('distance06', _decode_distance06),
    0xd5e70763: ('model07', _decode_model07),
    0x77586de4: ('distance07', _decode_distance07),
    0x24b1b5b6: ('model08', _decode_model08),
    0x860edf31: ('distance08', _decode_distance08),
    0xefed6613: ('model09', _decode_model09),
    0x4d520c94: ('distance09', _decode_distance09),
    0x6e953c6f: ('model10', _decode_model10),
    0xcc2a56e8: ('distance10', _decode_distance10),
    0xb67e3bf9: ('unknown_0xb67e3bf9', _decode_unknown_0xb67e3bf9),
}
