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
from retro_data_structures.properties.corruption.archetypes.SpindlePositionInterpolant import SpindlePositionInterpolant

if typing.TYPE_CHECKING:
    class SpindleOrientationJson(typing_extensions.TypedDict):
        flags_spindle_orientation: int
        look_at_angular_offset: json_util.JsonObject
        look_at_z_offset: json_util.JsonObject
    

@dataclasses.dataclass()
class SpindleOrientation(BaseProperty):
    flags_spindle_orientation: int = dataclasses.field(default=786432, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1b4962bf, original_name='FlagsSpindleOrientation'
        ),
    })  # Flagset
    look_at_angular_offset: SpindlePositionInterpolant = dataclasses.field(default_factory=SpindlePositionInterpolant, metadata={
        'reflection': FieldReflection[SpindlePositionInterpolant](
            SpindlePositionInterpolant, id=0x609c0608, original_name='LookAtAngularOffset', from_json=SpindlePositionInterpolant.from_json, to_json=SpindlePositionInterpolant.to_json
        ),
    })
    look_at_z_offset: SpindlePositionInterpolant = dataclasses.field(default_factory=SpindlePositionInterpolant, metadata={
        'reflection': FieldReflection[SpindlePositionInterpolant](
            SpindlePositionInterpolant, id=0xf6c828c0, original_name='LookAtZOffset', from_json=SpindlePositionInterpolant.from_json, to_json=SpindlePositionInterpolant.to_json
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
        if property_count != 3:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b4962bf
        flags_spindle_orientation = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x609c0608
        look_at_angular_offset = SpindlePositionInterpolant.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf6c828c0
        look_at_z_offset = SpindlePositionInterpolant.from_stream(data, property_size)
    
        return cls(flags_spindle_orientation, look_at_angular_offset, look_at_z_offset)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'\x1bIb\xbf')  # 0x1b4962bf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.flags_spindle_orientation))

        data.write(b'`\x9c\x06\x08')  # 0x609c0608
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.look_at_angular_offset.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf6\xc8(\xc0')  # 0xf6c828c0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.look_at_z_offset.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SpindleOrientationJson", data)
        return cls(
            flags_spindle_orientation=json_data['flags_spindle_orientation'],
            look_at_angular_offset=SpindlePositionInterpolant.from_json(json_data['look_at_angular_offset']),
            look_at_z_offset=SpindlePositionInterpolant.from_json(json_data['look_at_z_offset']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'flags_spindle_orientation': self.flags_spindle_orientation,
            'look_at_angular_offset': self.look_at_angular_offset.to_json(),
            'look_at_z_offset': self.look_at_z_offset.to_json(),
        }


def _decode_flags_spindle_orientation(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack(">L", data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x1b4962bf: ('flags_spindle_orientation', _decode_flags_spindle_orientation),
    0x609c0608: ('look_at_angular_offset', SpindlePositionInterpolant.from_stream),
    0xf6c828c0: ('look_at_z_offset', SpindlePositionInterpolant.from_stream),
}
