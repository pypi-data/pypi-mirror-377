# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.echoes.archetypes.UnknownStruct2 import UnknownStruct2

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class EmperorIngStage3StructBJson(typing_extensions.TypedDict):
        min_health_percentage: float
        unknown_0x95e7a2c2: float
        unknown_0x76ba1c18: float
        unknown_struct2_0x3826ec75: json_util.JsonObject
        unknown_struct2_0x93bf1106: json_util.JsonObject
        unknown_struct2_0xc4b88b80: json_util.JsonObject
        unknown_struct2_0x32c6dc77: json_util.JsonObject
        unknown_struct2_0xc6e7b293: json_util.JsonObject
        unknown_struct2_0x20746b56: json_util.JsonObject
        unknown_struct2_0x2ab44adb: json_util.JsonObject
        unknown_struct2_0xe2e78a78: json_util.JsonObject
    

@dataclasses.dataclass()
class EmperorIngStage3StructB(BaseProperty):
    min_health_percentage: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdfea46b3, original_name='MinHealthPercentage'
        ),
    })
    unknown_0x95e7a2c2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x95e7a2c2, original_name='Unknown'
        ),
    })
    unknown_0x76ba1c18: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x76ba1c18, original_name='Unknown'
        ),
    })
    unknown_struct2_0x3826ec75: UnknownStruct2 = dataclasses.field(default_factory=UnknownStruct2, metadata={
        'reflection': FieldReflection[UnknownStruct2](
            UnknownStruct2, id=0x3826ec75, original_name='UnknownStruct2', from_json=UnknownStruct2.from_json, to_json=UnknownStruct2.to_json
        ),
    })
    unknown_struct2_0x93bf1106: UnknownStruct2 = dataclasses.field(default_factory=UnknownStruct2, metadata={
        'reflection': FieldReflection[UnknownStruct2](
            UnknownStruct2, id=0x93bf1106, original_name='UnknownStruct2', from_json=UnknownStruct2.from_json, to_json=UnknownStruct2.to_json
        ),
    })
    unknown_struct2_0xc4b88b80: UnknownStruct2 = dataclasses.field(default_factory=UnknownStruct2, metadata={
        'reflection': FieldReflection[UnknownStruct2](
            UnknownStruct2, id=0xc4b88b80, original_name='UnknownStruct2', from_json=UnknownStruct2.from_json, to_json=UnknownStruct2.to_json
        ),
    })
    unknown_struct2_0x32c6dc77: UnknownStruct2 = dataclasses.field(default_factory=UnknownStruct2, metadata={
        'reflection': FieldReflection[UnknownStruct2](
            UnknownStruct2, id=0x32c6dc77, original_name='UnknownStruct2', from_json=UnknownStruct2.from_json, to_json=UnknownStruct2.to_json
        ),
    })
    unknown_struct2_0xc6e7b293: UnknownStruct2 = dataclasses.field(default_factory=UnknownStruct2, metadata={
        'reflection': FieldReflection[UnknownStruct2](
            UnknownStruct2, id=0xc6e7b293, original_name='UnknownStruct2', from_json=UnknownStruct2.from_json, to_json=UnknownStruct2.to_json
        ),
    })
    unknown_struct2_0x20746b56: UnknownStruct2 = dataclasses.field(default_factory=UnknownStruct2, metadata={
        'reflection': FieldReflection[UnknownStruct2](
            UnknownStruct2, id=0x20746b56, original_name='UnknownStruct2', from_json=UnknownStruct2.from_json, to_json=UnknownStruct2.to_json
        ),
    })
    unknown_struct2_0x2ab44adb: UnknownStruct2 = dataclasses.field(default_factory=UnknownStruct2, metadata={
        'reflection': FieldReflection[UnknownStruct2](
            UnknownStruct2, id=0x2ab44adb, original_name='UnknownStruct2', from_json=UnknownStruct2.from_json, to_json=UnknownStruct2.to_json
        ),
    })
    unknown_struct2_0xe2e78a78: UnknownStruct2 = dataclasses.field(default_factory=UnknownStruct2, metadata={
        'reflection': FieldReflection[UnknownStruct2](
            UnknownStruct2, id=0xe2e78a78, original_name='UnknownStruct2', from_json=UnknownStruct2.from_json, to_json=UnknownStruct2.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack(">H", data.read(2))[0]
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

        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 11:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdfea46b3
        min_health_percentage = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95e7a2c2
        unknown_0x95e7a2c2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x76ba1c18
        unknown_0x76ba1c18 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3826ec75
        unknown_struct2_0x3826ec75 = UnknownStruct2.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x93bf1106
        unknown_struct2_0x93bf1106 = UnknownStruct2.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc4b88b80
        unknown_struct2_0xc4b88b80 = UnknownStruct2.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x32c6dc77
        unknown_struct2_0x32c6dc77 = UnknownStruct2.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6e7b293
        unknown_struct2_0xc6e7b293 = UnknownStruct2.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x20746b56
        unknown_struct2_0x20746b56 = UnknownStruct2.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2ab44adb
        unknown_struct2_0x2ab44adb = UnknownStruct2.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe2e78a78
        unknown_struct2_0xe2e78a78 = UnknownStruct2.from_stream(data, property_size)
    
        return cls(min_health_percentage, unknown_0x95e7a2c2, unknown_0x76ba1c18, unknown_struct2_0x3826ec75, unknown_struct2_0x93bf1106, unknown_struct2_0xc4b88b80, unknown_struct2_0x32c6dc77, unknown_struct2_0xc6e7b293, unknown_struct2_0x20746b56, unknown_struct2_0x2ab44adb, unknown_struct2_0xe2e78a78)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0b')  # 11 properties

        data.write(b'\xdf\xeaF\xb3')  # 0xdfea46b3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_health_percentage))

        data.write(b'\x95\xe7\xa2\xc2')  # 0x95e7a2c2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x95e7a2c2))

        data.write(b'v\xba\x1c\x18')  # 0x76ba1c18
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x76ba1c18))

        data.write(b'8&\xecu')  # 0x3826ec75
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct2_0x3826ec75.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x93\xbf\x11\x06')  # 0x93bf1106
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct2_0x93bf1106.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc4\xb8\x8b\x80')  # 0xc4b88b80
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct2_0xc4b88b80.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'2\xc6\xdcw')  # 0x32c6dc77
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct2_0x32c6dc77.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc6\xe7\xb2\x93')  # 0xc6e7b293
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct2_0xc6e7b293.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b' tkV')  # 0x20746b56
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct2_0x20746b56.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'*\xb4J\xdb')  # 0x2ab44adb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct2_0x2ab44adb.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe2\xe7\x8ax')  # 0xe2e78a78
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct2_0xe2e78a78.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("EmperorIngStage3StructBJson", data)
        return cls(
            min_health_percentage=json_data['min_health_percentage'],
            unknown_0x95e7a2c2=json_data['unknown_0x95e7a2c2'],
            unknown_0x76ba1c18=json_data['unknown_0x76ba1c18'],
            unknown_struct2_0x3826ec75=UnknownStruct2.from_json(json_data['unknown_struct2_0x3826ec75']),
            unknown_struct2_0x93bf1106=UnknownStruct2.from_json(json_data['unknown_struct2_0x93bf1106']),
            unknown_struct2_0xc4b88b80=UnknownStruct2.from_json(json_data['unknown_struct2_0xc4b88b80']),
            unknown_struct2_0x32c6dc77=UnknownStruct2.from_json(json_data['unknown_struct2_0x32c6dc77']),
            unknown_struct2_0xc6e7b293=UnknownStruct2.from_json(json_data['unknown_struct2_0xc6e7b293']),
            unknown_struct2_0x20746b56=UnknownStruct2.from_json(json_data['unknown_struct2_0x20746b56']),
            unknown_struct2_0x2ab44adb=UnknownStruct2.from_json(json_data['unknown_struct2_0x2ab44adb']),
            unknown_struct2_0xe2e78a78=UnknownStruct2.from_json(json_data['unknown_struct2_0xe2e78a78']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'min_health_percentage': self.min_health_percentage,
            'unknown_0x95e7a2c2': self.unknown_0x95e7a2c2,
            'unknown_0x76ba1c18': self.unknown_0x76ba1c18,
            'unknown_struct2_0x3826ec75': self.unknown_struct2_0x3826ec75.to_json(),
            'unknown_struct2_0x93bf1106': self.unknown_struct2_0x93bf1106.to_json(),
            'unknown_struct2_0xc4b88b80': self.unknown_struct2_0xc4b88b80.to_json(),
            'unknown_struct2_0x32c6dc77': self.unknown_struct2_0x32c6dc77.to_json(),
            'unknown_struct2_0xc6e7b293': self.unknown_struct2_0xc6e7b293.to_json(),
            'unknown_struct2_0x20746b56': self.unknown_struct2_0x20746b56.to_json(),
            'unknown_struct2_0x2ab44adb': self.unknown_struct2_0x2ab44adb.to_json(),
            'unknown_struct2_0xe2e78a78': self.unknown_struct2_0xe2e78a78.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unknown_struct2_0x3826ec75.dependencies_for, "unknown_struct2_0x3826ec75", "UnknownStruct2"),
            (self.unknown_struct2_0x93bf1106.dependencies_for, "unknown_struct2_0x93bf1106", "UnknownStruct2"),
            (self.unknown_struct2_0xc4b88b80.dependencies_for, "unknown_struct2_0xc4b88b80", "UnknownStruct2"),
            (self.unknown_struct2_0x32c6dc77.dependencies_for, "unknown_struct2_0x32c6dc77", "UnknownStruct2"),
            (self.unknown_struct2_0xc6e7b293.dependencies_for, "unknown_struct2_0xc6e7b293", "UnknownStruct2"),
            (self.unknown_struct2_0x20746b56.dependencies_for, "unknown_struct2_0x20746b56", "UnknownStruct2"),
            (self.unknown_struct2_0x2ab44adb.dependencies_for, "unknown_struct2_0x2ab44adb", "UnknownStruct2"),
            (self.unknown_struct2_0xe2e78a78.dependencies_for, "unknown_struct2_0xe2e78a78", "UnknownStruct2"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for EmperorIngStage3StructB.{field_name} ({field_type}): {e}"
                )


def _decode_min_health_percentage(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x95e7a2c2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x76ba1c18(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xdfea46b3: ('min_health_percentage', _decode_min_health_percentage),
    0x95e7a2c2: ('unknown_0x95e7a2c2', _decode_unknown_0x95e7a2c2),
    0x76ba1c18: ('unknown_0x76ba1c18', _decode_unknown_0x76ba1c18),
    0x3826ec75: ('unknown_struct2_0x3826ec75', UnknownStruct2.from_stream),
    0x93bf1106: ('unknown_struct2_0x93bf1106', UnknownStruct2.from_stream),
    0xc4b88b80: ('unknown_struct2_0xc4b88b80', UnknownStruct2.from_stream),
    0x32c6dc77: ('unknown_struct2_0x32c6dc77', UnknownStruct2.from_stream),
    0xc6e7b293: ('unknown_struct2_0xc6e7b293', UnknownStruct2.from_stream),
    0x20746b56: ('unknown_struct2_0x20746b56', UnknownStruct2.from_stream),
    0x2ab44adb: ('unknown_struct2_0x2ab44adb', UnknownStruct2.from_stream),
    0xe2e78a78: ('unknown_struct2_0xe2e78a78', UnknownStruct2.from_stream),
}
