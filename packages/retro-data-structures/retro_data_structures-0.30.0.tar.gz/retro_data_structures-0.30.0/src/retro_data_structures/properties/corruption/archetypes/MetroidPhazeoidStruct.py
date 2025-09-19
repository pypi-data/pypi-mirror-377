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

if typing.TYPE_CHECKING:
    class MetroidPhazeoidStructJson(typing_extensions.TypedDict):
        phase_out_radius: float
        push_radius: float
        push_strength: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x837498c3, 0xda48646, 0xce995b2f)


@dataclasses.dataclass()
class MetroidPhazeoidStruct(BaseProperty):
    phase_out_radius: float = dataclasses.field(default=0.8999999761581421, metadata={
        'reflection': FieldReflection[float](
            float, id=0x837498c3, original_name='PhaseOutRadius'
        ),
    })
    push_radius: float = dataclasses.field(default=1.100000023841858, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0da48646, original_name='PushRadius'
        ),
    })
    push_strength: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xce995b2f, original_name='PushStrength'
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
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(30))
        assert (dec[0], dec[3], dec[6]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'\x83t\x98\xc3')  # 0x837498c3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.phase_out_radius))

        data.write(b'\r\xa4\x86F')  # 0xda48646
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.push_radius))

        data.write(b'\xce\x99[/')  # 0xce995b2f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.push_strength))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MetroidPhazeoidStructJson", data)
        return cls(
            phase_out_radius=json_data['phase_out_radius'],
            push_radius=json_data['push_radius'],
            push_strength=json_data['push_strength'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'phase_out_radius': self.phase_out_radius,
            'push_radius': self.push_radius,
            'push_strength': self.push_strength,
        }


def _decode_phase_out_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_push_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_push_strength(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x837498c3: ('phase_out_radius', _decode_phase_out_radius),
    0xda48646: ('push_radius', _decode_push_radius),
    0xce995b2f: ('push_strength', _decode_push_strength),
}
