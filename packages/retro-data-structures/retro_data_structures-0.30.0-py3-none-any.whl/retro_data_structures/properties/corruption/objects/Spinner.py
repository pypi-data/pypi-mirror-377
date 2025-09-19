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
    class SpinnerJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        forward_speed: float
        backward_speed: float
        unknown_0x449dd059: float
        unknown_0xfc849759: float
        shot_spinner: bool
        allow_wrap: bool
        no_backward: bool
        spline_control: bool
        unknown_0x865322ca: bool
        loop_sound: int
        start_sound: int
        stop_sound: int
    

@dataclasses.dataclass()
class Spinner(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    forward_speed: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xde4f6a76, original_name='ForwardSpeed'
        ),
    })
    backward_speed: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x54e15a3c, original_name='BackwardSpeed'
        ),
    })
    unknown_0x449dd059: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x449dd059, original_name='Unknown'
        ),
    })
    unknown_0xfc849759: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfc849759, original_name='Unknown'
        ),
    })
    shot_spinner: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x50501e17, original_name='ShotSpinner'
        ),
    })
    allow_wrap: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x3983cba7, original_name='AllowWrap'
        ),
    })
    no_backward: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf1c8a0ae, original_name='NoBackward'
        ),
    })
    spline_control: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe8f0a1ce, original_name='SplineControl'
        ),
    })
    unknown_0x865322ca: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x865322ca, original_name='Unknown'
        ),
    })
    loop_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x7147757a, original_name='LoopSound'
        ),
    })
    start_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa8cc48b3, original_name='StartSound'
        ),
    })
    stop_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x12afe499, original_name='StopSound'
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
        return 'SPIN'

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
        if property_count != 13:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xde4f6a76
        forward_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x54e15a3c
        backward_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x449dd059
        unknown_0x449dd059 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfc849759
        unknown_0xfc849759 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x50501e17
        shot_spinner = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3983cba7
        allow_wrap = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf1c8a0ae
        no_backward = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8f0a1ce
        spline_control = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x865322ca
        unknown_0x865322ca = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7147757a
        loop_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa8cc48b3
        start_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x12afe499
        stop_sound = struct.unpack(">Q", data.read(8))[0]
    
        return cls(editor_properties, forward_speed, backward_speed, unknown_0x449dd059, unknown_0xfc849759, shot_spinner, allow_wrap, no_backward, spline_control, unknown_0x865322ca, loop_sound, start_sound, stop_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\r')  # 13 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdeOjv')  # 0xde4f6a76
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_speed))

        data.write(b'T\xe1Z<')  # 0x54e15a3c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.backward_speed))

        data.write(b'D\x9d\xd0Y')  # 0x449dd059
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x449dd059))

        data.write(b'\xfc\x84\x97Y')  # 0xfc849759
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfc849759))

        data.write(b'PP\x1e\x17')  # 0x50501e17
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.shot_spinner))

        data.write(b'9\x83\xcb\xa7')  # 0x3983cba7
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.allow_wrap))

        data.write(b'\xf1\xc8\xa0\xae')  # 0xf1c8a0ae
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.no_backward))

        data.write(b'\xe8\xf0\xa1\xce')  # 0xe8f0a1ce
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.spline_control))

        data.write(b'\x86S"\xca')  # 0x865322ca
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x865322ca))

        data.write(b'qGuz')  # 0x7147757a
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.loop_sound))

        data.write(b'\xa8\xccH\xb3')  # 0xa8cc48b3
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.start_sound))

        data.write(b'\x12\xaf\xe4\x99')  # 0x12afe499
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.stop_sound))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SpinnerJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            forward_speed=json_data['forward_speed'],
            backward_speed=json_data['backward_speed'],
            unknown_0x449dd059=json_data['unknown_0x449dd059'],
            unknown_0xfc849759=json_data['unknown_0xfc849759'],
            shot_spinner=json_data['shot_spinner'],
            allow_wrap=json_data['allow_wrap'],
            no_backward=json_data['no_backward'],
            spline_control=json_data['spline_control'],
            unknown_0x865322ca=json_data['unknown_0x865322ca'],
            loop_sound=json_data['loop_sound'],
            start_sound=json_data['start_sound'],
            stop_sound=json_data['stop_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'forward_speed': self.forward_speed,
            'backward_speed': self.backward_speed,
            'unknown_0x449dd059': self.unknown_0x449dd059,
            'unknown_0xfc849759': self.unknown_0xfc849759,
            'shot_spinner': self.shot_spinner,
            'allow_wrap': self.allow_wrap,
            'no_backward': self.no_backward,
            'spline_control': self.spline_control,
            'unknown_0x865322ca': self.unknown_0x865322ca,
            'loop_sound': self.loop_sound,
            'start_sound': self.start_sound,
            'stop_sound': self.stop_sound,
        }


def _decode_forward_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_backward_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x449dd059(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfc849759(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_shot_spinner(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_allow_wrap(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_no_backward(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_spline_control(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x865322ca(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_loop_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_start_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_stop_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xde4f6a76: ('forward_speed', _decode_forward_speed),
    0x54e15a3c: ('backward_speed', _decode_backward_speed),
    0x449dd059: ('unknown_0x449dd059', _decode_unknown_0x449dd059),
    0xfc849759: ('unknown_0xfc849759', _decode_unknown_0xfc849759),
    0x50501e17: ('shot_spinner', _decode_shot_spinner),
    0x3983cba7: ('allow_wrap', _decode_allow_wrap),
    0xf1c8a0ae: ('no_backward', _decode_no_backward),
    0xe8f0a1ce: ('spline_control', _decode_spline_control),
    0x865322ca: ('unknown_0x865322ca', _decode_unknown_0x865322ca),
    0x7147757a: ('loop_sound', _decode_loop_sound),
    0xa8cc48b3: ('start_sound', _decode_start_sound),
    0x12afe499: ('stop_sound', _decode_stop_sound),
}
