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
from retro_data_structures.properties.corruption.archetypes.RevolutionControl import RevolutionControl
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class PlayerMovementControlsJson(typing_extensions.TypedDict):
        forward: json_util.JsonObject
        backward: json_util.JsonObject
        turn_left: json_util.JsonObject
        turn_right: json_util.JsonObject
        unknown_0xf86e276b: json_util.JsonObject
        unknown_0xd0106d0d: json_util.JsonObject
        strafe_left: json_util.JsonObject
        strafe_right: json_util.JsonObject
        jump: json_util.JsonObject
        lean_left: json_util.JsonObject
        lean_right: json_util.JsonObject
        unknown_0x4058d24a: json_util.JsonObject
        unknown_0x466568f7: json_util.JsonObject
        unknown_0x1580c929: json_util.JsonObject
        unknown_0xff5cc926: json_util.JsonObject
    

@dataclasses.dataclass()
class PlayerMovementControls(BaseProperty):
    forward: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x04124a09, original_name='Forward', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    backward: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xade0103b, original_name='Backward', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    turn_left: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x416d1cc1, original_name='TurnLeft', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    turn_right: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xe6aa24c0, original_name='TurnRight', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0xf86e276b: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xf86e276b, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0xd0106d0d: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xd0106d0d, original_name='Unknown', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    strafe_left: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x7adf18cd, original_name='StrafeLeft', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    strafe_right: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xef27daef, original_name='StrafeRight', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    jump: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x6b6fce63, original_name='Jump', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    lean_left: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x3d8d6854, original_name='LeanLeft', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    lean_right: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x66b3a37f, original_name='LeanRight', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    unknown_0x4058d24a: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x4058d24a, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0x466568f7: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x466568f7, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0x1580c929: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x1580c929, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0xff5cc926: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xff5cc926, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
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
        if property_count != 15:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x04124a09
        forward = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xade0103b
        backward = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x416d1cc1
        turn_left = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe6aa24c0
        turn_right = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf86e276b
        unknown_0xf86e276b = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd0106d0d
        unknown_0xd0106d0d = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7adf18cd
        strafe_left = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef27daef
        strafe_right = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6b6fce63
        jump = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d8d6854
        lean_left = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x66b3a37f
        lean_right = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4058d24a
        unknown_0x4058d24a = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x466568f7
        unknown_0x466568f7 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1580c929
        unknown_0x1580c929 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xff5cc926
        unknown_0xff5cc926 = Spline.from_stream(data, property_size)
    
        return cls(forward, backward, turn_left, turn_right, unknown_0xf86e276b, unknown_0xd0106d0d, strafe_left, strafe_right, jump, lean_left, lean_right, unknown_0x4058d24a, unknown_0x466568f7, unknown_0x1580c929, unknown_0xff5cc926)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0f')  # 15 properties

        data.write(b'\x04\x12J\t')  # 0x4124a09
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.forward.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xad\xe0\x10;')  # 0xade0103b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.backward.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'Am\x1c\xc1')  # 0x416d1cc1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.turn_left.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe6\xaa$\xc0')  # 0xe6aa24c0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.turn_right.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"\xf8n'k")  # 0xf86e276b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xf86e276b.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd0\x10m\r')  # 0xd0106d0d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xd0106d0d.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'z\xdf\x18\xcd')  # 0x7adf18cd
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.strafe_left.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"\xef'\xda\xef")  # 0xef27daef
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.strafe_right.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'ko\xcec')  # 0x6b6fce63
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.jump.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'=\x8dhT')  # 0x3d8d6854
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.lean_left.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'f\xb3\xa3\x7f')  # 0x66b3a37f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.lean_right.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'@X\xd2J')  # 0x4058d24a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x4058d24a.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'Feh\xf7')  # 0x466568f7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x466568f7.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x15\x80\xc9)')  # 0x1580c929
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x1580c929.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xff\\\xc9&')  # 0xff5cc926
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xff5cc926.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PlayerMovementControlsJson", data)
        return cls(
            forward=RevolutionControl.from_json(json_data['forward']),
            backward=RevolutionControl.from_json(json_data['backward']),
            turn_left=RevolutionControl.from_json(json_data['turn_left']),
            turn_right=RevolutionControl.from_json(json_data['turn_right']),
            unknown_0xf86e276b=RevolutionControl.from_json(json_data['unknown_0xf86e276b']),
            unknown_0xd0106d0d=RevolutionControl.from_json(json_data['unknown_0xd0106d0d']),
            strafe_left=RevolutionControl.from_json(json_data['strafe_left']),
            strafe_right=RevolutionControl.from_json(json_data['strafe_right']),
            jump=RevolutionControl.from_json(json_data['jump']),
            lean_left=RevolutionControl.from_json(json_data['lean_left']),
            lean_right=RevolutionControl.from_json(json_data['lean_right']),
            unknown_0x4058d24a=Spline.from_json(json_data['unknown_0x4058d24a']),
            unknown_0x466568f7=Spline.from_json(json_data['unknown_0x466568f7']),
            unknown_0x1580c929=Spline.from_json(json_data['unknown_0x1580c929']),
            unknown_0xff5cc926=Spline.from_json(json_data['unknown_0xff5cc926']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'forward': self.forward.to_json(),
            'backward': self.backward.to_json(),
            'turn_left': self.turn_left.to_json(),
            'turn_right': self.turn_right.to_json(),
            'unknown_0xf86e276b': self.unknown_0xf86e276b.to_json(),
            'unknown_0xd0106d0d': self.unknown_0xd0106d0d.to_json(),
            'strafe_left': self.strafe_left.to_json(),
            'strafe_right': self.strafe_right.to_json(),
            'jump': self.jump.to_json(),
            'lean_left': self.lean_left.to_json(),
            'lean_right': self.lean_right.to_json(),
            'unknown_0x4058d24a': self.unknown_0x4058d24a.to_json(),
            'unknown_0x466568f7': self.unknown_0x466568f7.to_json(),
            'unknown_0x1580c929': self.unknown_0x1580c929.to_json(),
            'unknown_0xff5cc926': self.unknown_0xff5cc926.to_json(),
        }


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x4124a09: ('forward', RevolutionControl.from_stream),
    0xade0103b: ('backward', RevolutionControl.from_stream),
    0x416d1cc1: ('turn_left', RevolutionControl.from_stream),
    0xe6aa24c0: ('turn_right', RevolutionControl.from_stream),
    0xf86e276b: ('unknown_0xf86e276b', RevolutionControl.from_stream),
    0xd0106d0d: ('unknown_0xd0106d0d', RevolutionControl.from_stream),
    0x7adf18cd: ('strafe_left', RevolutionControl.from_stream),
    0xef27daef: ('strafe_right', RevolutionControl.from_stream),
    0x6b6fce63: ('jump', RevolutionControl.from_stream),
    0x3d8d6854: ('lean_left', RevolutionControl.from_stream),
    0x66b3a37f: ('lean_right', RevolutionControl.from_stream),
    0x4058d24a: ('unknown_0x4058d24a', Spline.from_stream),
    0x466568f7: ('unknown_0x466568f7', Spline.from_stream),
    0x1580c929: ('unknown_0x1580c929', Spline.from_stream),
    0xff5cc926: ('unknown_0xff5cc926', Spline.from_stream),
}
