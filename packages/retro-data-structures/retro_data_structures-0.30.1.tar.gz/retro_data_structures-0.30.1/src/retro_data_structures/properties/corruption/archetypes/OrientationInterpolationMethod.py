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
from retro_data_structures.properties.corruption.archetypes.InterpolationMethod import InterpolationMethod

if typing.TYPE_CHECKING:
    class OrientationInterpolationMethodJson(typing_extensions.TypedDict):
        orientation_type: int
        orientation_control: json_util.JsonObject
    

class OrientationType(enum.IntEnum):
    Unknown1 = 894727893
    Unknown2 = 1703284864
    Unknown3 = 2424825473
    Unknown4 = 293088044
    Unknown5 = 1061457362

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
class OrientationInterpolationMethod(BaseProperty):
    orientation_type: OrientationType = dataclasses.field(default=OrientationType.Unknown1, metadata={
        'reflection': FieldReflection[OrientationType](
            OrientationType, id=0x5c72a964, original_name='OrientationType', from_json=OrientationType.from_json, to_json=OrientationType.to_json
        ),
    })
    orientation_control: InterpolationMethod = dataclasses.field(default_factory=InterpolationMethod, metadata={
        'reflection': FieldReflection[InterpolationMethod](
            InterpolationMethod, id=0x8654b081, original_name='OrientationControl', from_json=InterpolationMethod.from_json, to_json=InterpolationMethod.to_json
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
        if property_count != 2:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5c72a964
        orientation_type = OrientationType.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8654b081
        orientation_control = InterpolationMethod.from_stream(data, property_size)
    
        return cls(orientation_type, orientation_control)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x02')  # 2 properties

        data.write(b'\\r\xa9d')  # 0x5c72a964
        data.write(b'\x00\x04')  # size
        self.orientation_type.to_stream(data)

        data.write(b'\x86T\xb0\x81')  # 0x8654b081
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.orientation_control.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("OrientationInterpolationMethodJson", data)
        return cls(
            orientation_type=OrientationType.from_json(json_data['orientation_type']),
            orientation_control=InterpolationMethod.from_json(json_data['orientation_control']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'orientation_type': self.orientation_type.to_json(),
            'orientation_control': self.orientation_control.to_json(),
        }


def _decode_orientation_type(data: typing.BinaryIO, property_size: int) -> OrientationType:
    return OrientationType.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x5c72a964: ('orientation_type', _decode_orientation_type),
    0x8654b081: ('orientation_control', InterpolationMethod.from_stream),
}
