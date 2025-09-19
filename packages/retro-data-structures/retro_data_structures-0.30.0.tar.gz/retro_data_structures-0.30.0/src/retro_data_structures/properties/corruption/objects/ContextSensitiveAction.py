# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class ContextSensitiveActionJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        animation: int
        rotation_blend_mode: int
        blend: json_util.JsonObject
        mode: int
        controller_type: int
        unknown: float
        hide_aiming_cursor: bool
    

class RotationBlendMode(enum.IntEnum):
    Unknown1 = 3792314206
    Unknown2 = 687395058

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


class Mode(enum.IntEnum):
    Unknown1 = 1123045001
    Unknown2 = 2484558442
    Unknown3 = 3387220509

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


class ControllerType(enum.IntEnum):
    Unknown1 = 3024507316
    Unknown2 = 268540483
    Unknown3 = 1722423905

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
class ContextSensitiveAction(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    animation: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xaacdb11c, original_name='Animation'
        ),
    })
    rotation_blend_mode: RotationBlendMode = dataclasses.field(default=RotationBlendMode.Unknown1, metadata={
        'reflection': FieldReflection[RotationBlendMode](
            RotationBlendMode, id=0xb068f40b, original_name='RotationBlendMode', from_json=RotationBlendMode.from_json, to_json=RotationBlendMode.to_json
        ),
    })
    blend: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xf9dfe01d, original_name='Blend', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    mode: Mode = dataclasses.field(default=Mode.Unknown1, metadata={
        'reflection': FieldReflection[Mode](
            Mode, id=0xb8f60f9a, original_name='Mode', from_json=Mode.from_json, to_json=Mode.to_json
        ),
    })
    controller_type: ControllerType = dataclasses.field(default=ControllerType.Unknown1, metadata={
        'reflection': FieldReflection[ControllerType](
            ControllerType, id=0x8972a86f, original_name='ControllerType', from_json=ControllerType.from_json, to_json=ControllerType.to_json
        ),
    })
    unknown: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbf0adf40, original_name='Unknown'
        ),
    })
    hide_aiming_cursor: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xca4016a1, original_name='HideAimingCursor'
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
        return 'CSAC'

    @classmethod
    def modules(cls) -> list[str]:
        return ['RSO_ScriptContextSensitiveAction.rso']

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
        if property_count != 8:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaacdb11c
        animation = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb068f40b
        rotation_blend_mode = RotationBlendMode.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf9dfe01d
        blend = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb8f60f9a
        mode = Mode.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8972a86f
        controller_type = ControllerType.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbf0adf40
        unknown = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xca4016a1
        hide_aiming_cursor = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, animation, rotation_blend_mode, blend, mode, controller_type, unknown, hide_aiming_cursor)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xaa\xcd\xb1\x1c')  # 0xaacdb11c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.animation))

        data.write(b'\xb0h\xf4\x0b')  # 0xb068f40b
        data.write(b'\x00\x04')  # size
        self.rotation_blend_mode.to_stream(data)

        data.write(b'\xf9\xdf\xe0\x1d')  # 0xf9dfe01d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.blend.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb8\xf6\x0f\x9a')  # 0xb8f60f9a
        data.write(b'\x00\x04')  # size
        self.mode.to_stream(data)

        data.write(b'\x89r\xa8o')  # 0x8972a86f
        data.write(b'\x00\x04')  # size
        self.controller_type.to_stream(data)

        data.write(b'\xbf\n\xdf@')  # 0xbf0adf40
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'\xca@\x16\xa1')  # 0xca4016a1
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.hide_aiming_cursor))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ContextSensitiveActionJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            animation=json_data['animation'],
            rotation_blend_mode=RotationBlendMode.from_json(json_data['rotation_blend_mode']),
            blend=Spline.from_json(json_data['blend']),
            mode=Mode.from_json(json_data['mode']),
            controller_type=ControllerType.from_json(json_data['controller_type']),
            unknown=json_data['unknown'],
            hide_aiming_cursor=json_data['hide_aiming_cursor'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'animation': self.animation,
            'rotation_blend_mode': self.rotation_blend_mode.to_json(),
            'blend': self.blend.to_json(),
            'mode': self.mode.to_json(),
            'controller_type': self.controller_type.to_json(),
            'unknown': self.unknown,
            'hide_aiming_cursor': self.hide_aiming_cursor,
        }


def _decode_animation(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_rotation_blend_mode(data: typing.BinaryIO, property_size: int) -> RotationBlendMode:
    return RotationBlendMode.from_stream(data)


def _decode_mode(data: typing.BinaryIO, property_size: int) -> Mode:
    return Mode.from_stream(data)


def _decode_controller_type(data: typing.BinaryIO, property_size: int) -> ControllerType:
    return ControllerType.from_stream(data)


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hide_aiming_cursor(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xaacdb11c: ('animation', _decode_animation),
    0xb068f40b: ('rotation_blend_mode', _decode_rotation_blend_mode),
    0xf9dfe01d: ('blend', Spline.from_stream),
    0xb8f60f9a: ('mode', _decode_mode),
    0x8972a86f: ('controller_type', _decode_controller_type),
    0xbf0adf40: ('unknown', _decode_unknown),
    0xca4016a1: ('hide_aiming_cursor', _decode_hide_aiming_cursor),
}
