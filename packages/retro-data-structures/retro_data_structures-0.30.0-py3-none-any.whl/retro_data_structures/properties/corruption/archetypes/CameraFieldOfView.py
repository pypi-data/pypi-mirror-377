# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class CameraFieldOfViewJson(typing_extensions.TypedDict):
        fov_type: int
        fov_path_object: int
        desired_fov: float
        unknown_0x972c0e20: json_util.JsonObject
        unknown_0x812cf888: json_util.JsonObject
    

class FOVPathObject(enum.IntEnum):
    Unknown1 = 221052433
    Unknown2 = 3545934728
    Unknown3 = 2921949809

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
class CameraFieldOfView(BaseProperty):
    fov_type: int = dataclasses.field(default=2839405128, metadata={
        'reflection': FieldReflection[int](
            int, id=0x19ea151b, original_name='FOVType'
        ),
    })  # Choice
    fov_path_object: FOVPathObject = dataclasses.field(default=FOVPathObject.Unknown1, metadata={
        'reflection': FieldReflection[FOVPathObject](
            FOVPathObject, id=0xd1e91886, original_name='FOVPathObject', from_json=FOVPathObject.from_json, to_json=FOVPathObject.to_json
        ),
    })
    desired_fov: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcafe3da7, original_name='DesiredFOV'
        ),
    })
    unknown_0x972c0e20: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x972c0e20, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0x812cf888: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x812cf888, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

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
        if property_count != 5:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x19ea151b
        fov_type = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd1e91886
        fov_path_object = FOVPathObject.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcafe3da7
        desired_fov = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x972c0e20
        unknown_0x972c0e20 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x812cf888
        unknown_0x812cf888 = Spline.from_stream(data, property_size)
    
        return cls(fov_type, fov_path_object, desired_fov, unknown_0x972c0e20, unknown_0x812cf888)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x05')  # 5 properties

        data.write(b'\x19\xea\x15\x1b')  # 0x19ea151b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.fov_type))

        data.write(b'\xd1\xe9\x18\x86')  # 0xd1e91886
        data.write(b'\x00\x04')  # size
        self.fov_path_object.to_stream(data)

        data.write(b'\xca\xfe=\xa7')  # 0xcafe3da7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.desired_fov))

        data.write(b'\x97,\x0e ')  # 0x972c0e20
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x972c0e20.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x81,\xf8\x88')  # 0x812cf888
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x812cf888.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CameraFieldOfViewJson", data)
        return cls(
            fov_type=json_data['fov_type'],
            fov_path_object=FOVPathObject.from_json(json_data['fov_path_object']),
            desired_fov=json_data['desired_fov'],
            unknown_0x972c0e20=Spline.from_json(json_data['unknown_0x972c0e20']),
            unknown_0x812cf888=Spline.from_json(json_data['unknown_0x812cf888']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'fov_type': self.fov_type,
            'fov_path_object': self.fov_path_object.to_json(),
            'desired_fov': self.desired_fov,
            'unknown_0x972c0e20': self.unknown_0x972c0e20.to_json(),
            'unknown_0x812cf888': self.unknown_0x812cf888.to_json(),
        }


def _decode_fov_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack(">L", data.read(4))[0]


def _decode_fov_path_object(data: typing.BinaryIO, property_size: int) -> FOVPathObject:
    return FOVPathObject.from_stream(data)


def _decode_desired_fov(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x19ea151b: ('fov_type', _decode_fov_type),
    0xd1e91886: ('fov_path_object', _decode_fov_path_object),
    0xcafe3da7: ('desired_fov', _decode_desired_fov),
    0x972c0e20: ('unknown_0x972c0e20', Spline.from_stream),
    0x812cf888: ('unknown_0x812cf888', Spline.from_stream),
}
