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
from retro_data_structures.properties.corruption.archetypes.MultiModelActorStruct import MultiModelActorStruct

if typing.TYPE_CHECKING:
    class MultiModelInformationJson(typing_extensions.TypedDict):
        unknown: int
        use_fade: bool
        fade_time: float
        multi_model_actor_struct_0x681c4457: json_util.JsonObject
        multi_model_actor_struct_0xc674d5c6: json_util.JsonObject
        multi_model_actor_struct_0x3b8d2db3: json_util.JsonObject
        multi_model_actor_struct_0x95e5bc22: json_util.JsonObject
        multi_model_actor_struct_0xbc2d08d0: json_util.JsonObject
        multi_model_actor_struct_0x12459941: json_util.JsonObject
        multi_model_actor_struct_0x9caffe7b: json_util.JsonObject
        multi_model_actor_struct_0x32c76fea: json_util.JsonObject
        multi_model_actor_struct_0x681aaa77: json_util.JsonObject
    

@dataclasses.dataclass()
class MultiModelInformation(BaseProperty):
    unknown: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6439f487, original_name='Unknown'
        ),
    })
    use_fade: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe25a15c1, original_name='UseFade'
        ),
    })
    fade_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd4124c4c, original_name='FadeTime'
        ),
    })
    multi_model_actor_struct_0x681c4457: MultiModelActorStruct = dataclasses.field(default_factory=MultiModelActorStruct, metadata={
        'reflection': FieldReflection[MultiModelActorStruct](
            MultiModelActorStruct, id=0x681c4457, original_name='MultiModelActorStruct', from_json=MultiModelActorStruct.from_json, to_json=MultiModelActorStruct.to_json
        ),
    })
    multi_model_actor_struct_0xc674d5c6: MultiModelActorStruct = dataclasses.field(default_factory=MultiModelActorStruct, metadata={
        'reflection': FieldReflection[MultiModelActorStruct](
            MultiModelActorStruct, id=0xc674d5c6, original_name='MultiModelActorStruct', from_json=MultiModelActorStruct.from_json, to_json=MultiModelActorStruct.to_json
        ),
    })
    multi_model_actor_struct_0x3b8d2db3: MultiModelActorStruct = dataclasses.field(default_factory=MultiModelActorStruct, metadata={
        'reflection': FieldReflection[MultiModelActorStruct](
            MultiModelActorStruct, id=0x3b8d2db3, original_name='MultiModelActorStruct', from_json=MultiModelActorStruct.from_json, to_json=MultiModelActorStruct.to_json
        ),
    })
    multi_model_actor_struct_0x95e5bc22: MultiModelActorStruct = dataclasses.field(default_factory=MultiModelActorStruct, metadata={
        'reflection': FieldReflection[MultiModelActorStruct](
            MultiModelActorStruct, id=0x95e5bc22, original_name='MultiModelActorStruct', from_json=MultiModelActorStruct.from_json, to_json=MultiModelActorStruct.to_json
        ),
    })
    multi_model_actor_struct_0xbc2d08d0: MultiModelActorStruct = dataclasses.field(default_factory=MultiModelActorStruct, metadata={
        'reflection': FieldReflection[MultiModelActorStruct](
            MultiModelActorStruct, id=0xbc2d08d0, original_name='MultiModelActorStruct', from_json=MultiModelActorStruct.from_json, to_json=MultiModelActorStruct.to_json
        ),
    })
    multi_model_actor_struct_0x12459941: MultiModelActorStruct = dataclasses.field(default_factory=MultiModelActorStruct, metadata={
        'reflection': FieldReflection[MultiModelActorStruct](
            MultiModelActorStruct, id=0x12459941, original_name='MultiModelActorStruct', from_json=MultiModelActorStruct.from_json, to_json=MultiModelActorStruct.to_json
        ),
    })
    multi_model_actor_struct_0x9caffe7b: MultiModelActorStruct = dataclasses.field(default_factory=MultiModelActorStruct, metadata={
        'reflection': FieldReflection[MultiModelActorStruct](
            MultiModelActorStruct, id=0x9caffe7b, original_name='MultiModelActorStruct', from_json=MultiModelActorStruct.from_json, to_json=MultiModelActorStruct.to_json
        ),
    })
    multi_model_actor_struct_0x32c76fea: MultiModelActorStruct = dataclasses.field(default_factory=MultiModelActorStruct, metadata={
        'reflection': FieldReflection[MultiModelActorStruct](
            MultiModelActorStruct, id=0x32c76fea, original_name='MultiModelActorStruct', from_json=MultiModelActorStruct.from_json, to_json=MultiModelActorStruct.to_json
        ),
    })
    multi_model_actor_struct_0x681aaa77: MultiModelActorStruct = dataclasses.field(default_factory=MultiModelActorStruct, metadata={
        'reflection': FieldReflection[MultiModelActorStruct](
            MultiModelActorStruct, id=0x681aaa77, original_name='MultiModelActorStruct', from_json=MultiModelActorStruct.from_json, to_json=MultiModelActorStruct.to_json
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
        if property_count != 12:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6439f487
        unknown = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe25a15c1
        use_fade = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd4124c4c
        fade_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x681c4457
        multi_model_actor_struct_0x681c4457 = MultiModelActorStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc674d5c6
        multi_model_actor_struct_0xc674d5c6 = MultiModelActorStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3b8d2db3
        multi_model_actor_struct_0x3b8d2db3 = MultiModelActorStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95e5bc22
        multi_model_actor_struct_0x95e5bc22 = MultiModelActorStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbc2d08d0
        multi_model_actor_struct_0xbc2d08d0 = MultiModelActorStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x12459941
        multi_model_actor_struct_0x12459941 = MultiModelActorStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9caffe7b
        multi_model_actor_struct_0x9caffe7b = MultiModelActorStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x32c76fea
        multi_model_actor_struct_0x32c76fea = MultiModelActorStruct.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x681aaa77
        multi_model_actor_struct_0x681aaa77 = MultiModelActorStruct.from_stream(data, property_size)
    
        return cls(unknown, use_fade, fade_time, multi_model_actor_struct_0x681c4457, multi_model_actor_struct_0xc674d5c6, multi_model_actor_struct_0x3b8d2db3, multi_model_actor_struct_0x95e5bc22, multi_model_actor_struct_0xbc2d08d0, multi_model_actor_struct_0x12459941, multi_model_actor_struct_0x9caffe7b, multi_model_actor_struct_0x32c76fea, multi_model_actor_struct_0x681aaa77)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0c')  # 12 properties

        data.write(b'd9\xf4\x87')  # 0x6439f487
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown))

        data.write(b'\xe2Z\x15\xc1')  # 0xe25a15c1
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.use_fade))

        data.write(b'\xd4\x12LL')  # 0xd4124c4c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_time))

        data.write(b'h\x1cDW')  # 0x681c4457
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.multi_model_actor_struct_0x681c4457.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc6t\xd5\xc6')  # 0xc674d5c6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.multi_model_actor_struct_0xc674d5c6.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b';\x8d-\xb3')  # 0x3b8d2db3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.multi_model_actor_struct_0x3b8d2db3.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x95\xe5\xbc"')  # 0x95e5bc22
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.multi_model_actor_struct_0x95e5bc22.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbc-\x08\xd0')  # 0xbc2d08d0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.multi_model_actor_struct_0xbc2d08d0.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x12E\x99A')  # 0x12459941
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.multi_model_actor_struct_0x12459941.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9c\xaf\xfe{')  # 0x9caffe7b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.multi_model_actor_struct_0x9caffe7b.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'2\xc7o\xea')  # 0x32c76fea
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.multi_model_actor_struct_0x32c76fea.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'h\x1a\xaaw')  # 0x681aaa77
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.multi_model_actor_struct_0x681aaa77.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MultiModelInformationJson", data)
        return cls(
            unknown=json_data['unknown'],
            use_fade=json_data['use_fade'],
            fade_time=json_data['fade_time'],
            multi_model_actor_struct_0x681c4457=MultiModelActorStruct.from_json(json_data['multi_model_actor_struct_0x681c4457']),
            multi_model_actor_struct_0xc674d5c6=MultiModelActorStruct.from_json(json_data['multi_model_actor_struct_0xc674d5c6']),
            multi_model_actor_struct_0x3b8d2db3=MultiModelActorStruct.from_json(json_data['multi_model_actor_struct_0x3b8d2db3']),
            multi_model_actor_struct_0x95e5bc22=MultiModelActorStruct.from_json(json_data['multi_model_actor_struct_0x95e5bc22']),
            multi_model_actor_struct_0xbc2d08d0=MultiModelActorStruct.from_json(json_data['multi_model_actor_struct_0xbc2d08d0']),
            multi_model_actor_struct_0x12459941=MultiModelActorStruct.from_json(json_data['multi_model_actor_struct_0x12459941']),
            multi_model_actor_struct_0x9caffe7b=MultiModelActorStruct.from_json(json_data['multi_model_actor_struct_0x9caffe7b']),
            multi_model_actor_struct_0x32c76fea=MultiModelActorStruct.from_json(json_data['multi_model_actor_struct_0x32c76fea']),
            multi_model_actor_struct_0x681aaa77=MultiModelActorStruct.from_json(json_data['multi_model_actor_struct_0x681aaa77']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown': self.unknown,
            'use_fade': self.use_fade,
            'fade_time': self.fade_time,
            'multi_model_actor_struct_0x681c4457': self.multi_model_actor_struct_0x681c4457.to_json(),
            'multi_model_actor_struct_0xc674d5c6': self.multi_model_actor_struct_0xc674d5c6.to_json(),
            'multi_model_actor_struct_0x3b8d2db3': self.multi_model_actor_struct_0x3b8d2db3.to_json(),
            'multi_model_actor_struct_0x95e5bc22': self.multi_model_actor_struct_0x95e5bc22.to_json(),
            'multi_model_actor_struct_0xbc2d08d0': self.multi_model_actor_struct_0xbc2d08d0.to_json(),
            'multi_model_actor_struct_0x12459941': self.multi_model_actor_struct_0x12459941.to_json(),
            'multi_model_actor_struct_0x9caffe7b': self.multi_model_actor_struct_0x9caffe7b.to_json(),
            'multi_model_actor_struct_0x32c76fea': self.multi_model_actor_struct_0x32c76fea.to_json(),
            'multi_model_actor_struct_0x681aaa77': self.multi_model_actor_struct_0x681aaa77.to_json(),
        }


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_use_fade(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_fade_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x6439f487: ('unknown', _decode_unknown),
    0xe25a15c1: ('use_fade', _decode_use_fade),
    0xd4124c4c: ('fade_time', _decode_fade_time),
    0x681c4457: ('multi_model_actor_struct_0x681c4457', MultiModelActorStruct.from_stream),
    0xc674d5c6: ('multi_model_actor_struct_0xc674d5c6', MultiModelActorStruct.from_stream),
    0x3b8d2db3: ('multi_model_actor_struct_0x3b8d2db3', MultiModelActorStruct.from_stream),
    0x95e5bc22: ('multi_model_actor_struct_0x95e5bc22', MultiModelActorStruct.from_stream),
    0xbc2d08d0: ('multi_model_actor_struct_0xbc2d08d0', MultiModelActorStruct.from_stream),
    0x12459941: ('multi_model_actor_struct_0x12459941', MultiModelActorStruct.from_stream),
    0x9caffe7b: ('multi_model_actor_struct_0x9caffe7b', MultiModelActorStruct.from_stream),
    0x32c76fea: ('multi_model_actor_struct_0x32c76fea', MultiModelActorStruct.from_stream),
    0x681aaa77: ('multi_model_actor_struct_0x681aaa77', MultiModelActorStruct.from_stream),
}
