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
from retro_data_structures.properties.corruption.archetypes.PIDConvergence import PIDConvergence
from retro_data_structures.properties.corruption.archetypes.ProportionalConvergence import ProportionalConvergence
from retro_data_structures.properties.corruption.archetypes.SpringConvergence import SpringConvergence
from retro_data_structures.properties.corruption.archetypes.VelocityConvergence import VelocityConvergence

if typing.TYPE_CHECKING:
    class ConvergenceJson(typing_extensions.TypedDict):
        convergence_type: int
        velocity: json_util.JsonObject
        spring: json_util.JsonObject
        pid: json_util.JsonObject
        proportional: json_util.JsonObject
    

class ConvergenceType(enum.IntEnum):
    Unknown1 = 197952338
    Unknown2 = 10840534
    Unknown3 = 2916633979
    Unknown4 = 1845080979
    Unknown5 = 2654787412

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
class Convergence(BaseProperty):
    convergence_type: ConvergenceType = dataclasses.field(default=ConvergenceType.Unknown1, metadata={
        'reflection': FieldReflection[ConvergenceType](
            ConvergenceType, id=0x2ef22401, original_name='ConvergenceType', from_json=ConvergenceType.from_json, to_json=ConvergenceType.to_json
        ),
    })
    velocity: VelocityConvergence = dataclasses.field(default_factory=VelocityConvergence, metadata={
        'reflection': FieldReflection[VelocityConvergence](
            VelocityConvergence, id=0x6f9d9b33, original_name='Velocity', from_json=VelocityConvergence.from_json, to_json=VelocityConvergence.to_json
        ),
    })
    spring: SpringConvergence = dataclasses.field(default_factory=SpringConvergence, metadata={
        'reflection': FieldReflection[SpringConvergence](
            SpringConvergence, id=0x0cf33816, original_name='Spring', from_json=SpringConvergence.from_json, to_json=SpringConvergence.to_json
        ),
    })
    pid: PIDConvergence = dataclasses.field(default_factory=PIDConvergence, metadata={
        'reflection': FieldReflection[PIDConvergence](
            PIDConvergence, id=0xf9e402ef, original_name='PID', from_json=PIDConvergence.from_json, to_json=PIDConvergence.to_json
        ),
    })
    proportional: ProportionalConvergence = dataclasses.field(default_factory=ProportionalConvergence, metadata={
        'reflection': FieldReflection[ProportionalConvergence](
            ProportionalConvergence, id=0x085648bc, original_name='Proportional', from_json=ProportionalConvergence.from_json, to_json=ProportionalConvergence.to_json
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
        assert property_id == 0x2ef22401
        convergence_type = ConvergenceType.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6f9d9b33
        velocity = VelocityConvergence.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0cf33816
        spring = SpringConvergence.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf9e402ef
        pid = PIDConvergence.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x085648bc
        proportional = ProportionalConvergence.from_stream(data, property_size)
    
        return cls(convergence_type, velocity, spring, pid, proportional)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x05')  # 5 properties

        data.write(b'.\xf2$\x01')  # 0x2ef22401
        data.write(b'\x00\x04')  # size
        self.convergence_type.to_stream(data)

        data.write(b'o\x9d\x9b3')  # 0x6f9d9b33
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.velocity.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x0c\xf38\x16')  # 0xcf33816
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.spring.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf9\xe4\x02\xef')  # 0xf9e402ef
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.pid.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x08VH\xbc')  # 0x85648bc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.proportional.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ConvergenceJson", data)
        return cls(
            convergence_type=ConvergenceType.from_json(json_data['convergence_type']),
            velocity=VelocityConvergence.from_json(json_data['velocity']),
            spring=SpringConvergence.from_json(json_data['spring']),
            pid=PIDConvergence.from_json(json_data['pid']),
            proportional=ProportionalConvergence.from_json(json_data['proportional']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'convergence_type': self.convergence_type.to_json(),
            'velocity': self.velocity.to_json(),
            'spring': self.spring.to_json(),
            'pid': self.pid.to_json(),
            'proportional': self.proportional.to_json(),
        }


def _decode_convergence_type(data: typing.BinaryIO, property_size: int) -> ConvergenceType:
    return ConvergenceType.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x2ef22401: ('convergence_type', _decode_convergence_type),
    0x6f9d9b33: ('velocity', VelocityConvergence.from_stream),
    0xcf33816: ('spring', SpringConvergence.from_stream),
    0xf9e402ef: ('pid', PIDConvergence.from_stream),
    0x85648bc: ('proportional', ProportionalConvergence.from_stream),
}
