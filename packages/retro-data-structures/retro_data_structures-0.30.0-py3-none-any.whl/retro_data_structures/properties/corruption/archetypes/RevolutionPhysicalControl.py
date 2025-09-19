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
import retro_data_structures.enums.corruption as enums
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class RevolutionPhysicalControlJson(typing_extensions.TypedDict):
        physical_control: int
        control_spline: json_util.JsonObject
    

@dataclasses.dataclass()
class RevolutionPhysicalControl(BaseProperty):
    physical_control: enums.PhysicalControlEnum = dataclasses.field(default=enums.PhysicalControlEnum.Unknown1, metadata={
        'reflection': FieldReflection[enums.PhysicalControlEnum](
            enums.PhysicalControlEnum, id=0x60d66244, original_name='PhysicalControl', from_json=enums.PhysicalControlEnum.from_json, to_json=enums.PhysicalControlEnum.to_json
        ),
    })
    control_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x15567fe7, original_name='ControlSpline', from_json=Spline.from_json, to_json=Spline.to_json
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
        assert property_id == 0x60d66244
        physical_control = enums.PhysicalControlEnum.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x15567fe7
        control_spline = Spline.from_stream(data, property_size)
    
        return cls(physical_control, control_spline)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x02')  # 2 properties

        data.write(b'`\xd6bD')  # 0x60d66244
        data.write(b'\x00\x04')  # size
        self.physical_control.to_stream(data)

        data.write(b'\x15V\x7f\xe7')  # 0x15567fe7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.control_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("RevolutionPhysicalControlJson", data)
        return cls(
            physical_control=enums.PhysicalControlEnum.from_json(json_data['physical_control']),
            control_spline=Spline.from_json(json_data['control_spline']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'physical_control': self.physical_control.to_json(),
            'control_spline': self.control_spline.to_json(),
        }


def _decode_physical_control(data: typing.BinaryIO, property_size: int) -> enums.PhysicalControlEnum:
    return enums.PhysicalControlEnum.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x60d66244: ('physical_control', _decode_physical_control),
    0x15567fe7: ('control_spline', Spline.from_stream),
}
