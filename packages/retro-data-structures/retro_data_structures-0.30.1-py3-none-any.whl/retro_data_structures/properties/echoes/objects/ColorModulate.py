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
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Spline import Spline

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ColorModulateJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        color_a: json_util.JsonValue
        color_b: json_util.JsonValue
        blend_mode: int
        time_a2_b: float
        time_b2_a: float
        do_reverse: bool
        reset_target_when_done: bool
        depth_compare: bool
        depth_update: bool
        depth_backwards: bool
        auto_start: bool
        update_time: bool
        loop_forever: bool
        external_time: bool
        copy_model_color_to_color_a: bool
        control_spline: json_util.JsonObject
    

@dataclasses.dataclass()
class ColorModulate(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    color_a: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xd6a3d26f, original_name='Color_A', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    color_b: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x5037a0c1, original_name='Color_B', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    blend_mode: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x94f0365c, original_name='Blend_Mode'
        ),
    })
    time_a2_b: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1afa5c48, original_name='Time_A2B'
        ),
    })
    time_b2_a: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x12e12905, original_name='Time_B2A'
        ),
    })
    do_reverse: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xcec5244b, original_name='Do_Reverse'
        ),
    })
    reset_target_when_done: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x81fc979c, original_name='Reset_Target_When_Done'
        ),
    })
    depth_compare: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x94c01b0c, original_name='Depth_Compare'
        ),
    })
    depth_update: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xaed25a51, original_name='Depth_Update'
        ),
    })
    depth_backwards: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x35dc43d0, original_name='Depth_Backwards'
        ),
    })
    auto_start: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x3217dff8, original_name='AutoStart'
        ),
    })
    update_time: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x3a7f59f7, original_name='UpdateTime'
        ),
    })
    loop_forever: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x08bb73c5, original_name='LoopForever'
        ),
    })
    external_time: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7e379ae8, original_name='ExternalTime'
        ),
    })
    copy_model_color_to_color_a: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x74081e94, original_name='CopyModelColorToColorA'
        ),
    })
    control_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x15567fe7, original_name='ControlSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'CLRM'

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
        if property_count != 17:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd6a3d26f
        color_a = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5037a0c1
        color_b = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x94f0365c
        blend_mode = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1afa5c48
        time_a2_b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x12e12905
        time_b2_a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcec5244b
        do_reverse = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x81fc979c
        reset_target_when_done = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x94c01b0c
        depth_compare = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaed25a51
        depth_update = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x35dc43d0
        depth_backwards = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3217dff8
        auto_start = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3a7f59f7
        update_time = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x08bb73c5
        loop_forever = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e379ae8
        external_time = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x74081e94
        copy_model_color_to_color_a = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x15567fe7
        control_spline = Spline.from_stream(data, property_size)
    
        return cls(editor_properties, color_a, color_b, blend_mode, time_a2_b, time_b2_a, do_reverse, reset_target_when_done, depth_compare, depth_update, depth_backwards, auto_start, update_time, loop_forever, external_time, copy_model_color_to_color_a, control_spline)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x11')  # 17 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd6\xa3\xd2o')  # 0xd6a3d26f
        data.write(b'\x00\x10')  # size
        self.color_a.to_stream(data)

        data.write(b'P7\xa0\xc1')  # 0x5037a0c1
        data.write(b'\x00\x10')  # size
        self.color_b.to_stream(data)

        data.write(b'\x94\xf06\\')  # 0x94f0365c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.blend_mode))

        data.write(b'\x1a\xfa\\H')  # 0x1afa5c48
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.time_a2_b))

        data.write(b'\x12\xe1)\x05')  # 0x12e12905
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.time_b2_a))

        data.write(b'\xce\xc5$K')  # 0xcec5244b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.do_reverse))

        data.write(b'\x81\xfc\x97\x9c')  # 0x81fc979c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.reset_target_when_done))

        data.write(b'\x94\xc0\x1b\x0c')  # 0x94c01b0c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.depth_compare))

        data.write(b'\xae\xd2ZQ')  # 0xaed25a51
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.depth_update))

        data.write(b'5\xdcC\xd0')  # 0x35dc43d0
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.depth_backwards))

        data.write(b'2\x17\xdf\xf8')  # 0x3217dff8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.auto_start))

        data.write(b':\x7fY\xf7')  # 0x3a7f59f7
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.update_time))

        data.write(b'\x08\xbbs\xc5')  # 0x8bb73c5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.loop_forever))

        data.write(b'~7\x9a\xe8')  # 0x7e379ae8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.external_time))

        data.write(b't\x08\x1e\x94')  # 0x74081e94
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.copy_model_color_to_color_a))

        data.write(b'\x15V\x7f\xe7')  # 0x15567fe7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.control_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ColorModulateJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            color_a=Color.from_json(json_data['color_a']),
            color_b=Color.from_json(json_data['color_b']),
            blend_mode=json_data['blend_mode'],
            time_a2_b=json_data['time_a2_b'],
            time_b2_a=json_data['time_b2_a'],
            do_reverse=json_data['do_reverse'],
            reset_target_when_done=json_data['reset_target_when_done'],
            depth_compare=json_data['depth_compare'],
            depth_update=json_data['depth_update'],
            depth_backwards=json_data['depth_backwards'],
            auto_start=json_data['auto_start'],
            update_time=json_data['update_time'],
            loop_forever=json_data['loop_forever'],
            external_time=json_data['external_time'],
            copy_model_color_to_color_a=json_data['copy_model_color_to_color_a'],
            control_spline=Spline.from_json(json_data['control_spline']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'color_a': self.color_a.to_json(),
            'color_b': self.color_b.to_json(),
            'blend_mode': self.blend_mode,
            'time_a2_b': self.time_a2_b,
            'time_b2_a': self.time_b2_a,
            'do_reverse': self.do_reverse,
            'reset_target_when_done': self.reset_target_when_done,
            'depth_compare': self.depth_compare,
            'depth_update': self.depth_update,
            'depth_backwards': self.depth_backwards,
            'auto_start': self.auto_start,
            'update_time': self.update_time,
            'loop_forever': self.loop_forever,
            'external_time': self.external_time,
            'copy_model_color_to_color_a': self.copy_model_color_to_color_a,
            'control_spline': self.control_spline.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for ColorModulate.{field_name} ({field_type}): {e}"
                )


def _decode_color_a(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_color_b(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_blend_mode(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_time_a2_b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_time_b2_a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_do_reverse(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_reset_target_when_done(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_depth_compare(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_depth_update(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_depth_backwards(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_auto_start(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_update_time(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_loop_forever(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_external_time(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_copy_model_color_to_color_a(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xd6a3d26f: ('color_a', _decode_color_a),
    0x5037a0c1: ('color_b', _decode_color_b),
    0x94f0365c: ('blend_mode', _decode_blend_mode),
    0x1afa5c48: ('time_a2_b', _decode_time_a2_b),
    0x12e12905: ('time_b2_a', _decode_time_b2_a),
    0xcec5244b: ('do_reverse', _decode_do_reverse),
    0x81fc979c: ('reset_target_when_done', _decode_reset_target_when_done),
    0x94c01b0c: ('depth_compare', _decode_depth_compare),
    0xaed25a51: ('depth_update', _decode_depth_update),
    0x35dc43d0: ('depth_backwards', _decode_depth_backwards),
    0x3217dff8: ('auto_start', _decode_auto_start),
    0x3a7f59f7: ('update_time', _decode_update_time),
    0x8bb73c5: ('loop_forever', _decode_loop_forever),
    0x7e379ae8: ('external_time', _decode_external_time),
    0x74081e94: ('copy_model_color_to_color_a', _decode_copy_model_color_to_color_a),
    0x15567fe7: ('control_spline', Spline.from_stream),
}
