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
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Color import Color

if typing.TYPE_CHECKING:
    class UnknownStruct24Json(typing_extensions.TypedDict):
        welding_tip: json_util.JsonObject
        welding_torch: int
        welding_beam: int
        part_0xea2c7744: int
        part_0x5a3ed5a0: int
        start_weld: int
        inside_collision: int
        outside_collision: int
        part_0x5b468021: int
        cmdl: int
        weld_shatter: int
        unknown_0xbface762: json_util.JsonValue
        unknown_0x3761c8e8: json_util.JsonValue
        weld_torch_sound: int
        weld_beam_sound: int
        inside_weld_sound: int
        outside_weld_sound: int
        unknown_0x1961d4a5: int
        start_weld_sound: int
        weld_succeeded_sound: int
        weld_failed_sound: int
        unknown_0x902d66f9: float
        unknown_0xedf4020e: float
        unknown_0x9cf48efc: float
        welding_time: float
    

@dataclasses.dataclass()
class UnknownStruct24(BaseProperty):
    welding_tip: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x6ade8b91, original_name='WeldingTip', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    welding_torch: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xfbf9569b, original_name='WeldingTorch'
        ),
    })
    welding_beam: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x8e14567b, original_name='WeldingBeam'
        ),
    })
    part_0xea2c7744: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xea2c7744, original_name='PART'
        ),
    })
    part_0x5a3ed5a0: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5a3ed5a0, original_name='PART'
        ),
    })
    start_weld: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x70bed427, original_name='StartWeld'
        ),
    })
    inside_collision: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xacd369c1, original_name='InsideCollision'
        ),
    })
    outside_collision: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1dad13a3, original_name='OutsideCollision'
        ),
    })
    part_0x5b468021: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5b468021, original_name='PART'
        ),
    })
    cmdl: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xcecad2c3, original_name='CMDL'
        ),
    })
    weld_shatter: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x7e542eaa, original_name='WeldShatter'
        ),
    })
    unknown_0xbface762: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xbface762, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x3761c8e8: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x3761c8e8, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    weld_torch_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x31c8bcaa, original_name='WeldTorchSound'
        ),
    })
    weld_beam_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1e1a49d5, original_name='WeldBeamSound'
        ),
    })
    inside_weld_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4a8cf2f7, original_name='InsideWeldSound'
        ),
    })
    outside_weld_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xfbf28895, original_name='OutsideWeldSound'
        ),
    })
    unknown_0x1961d4a5: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1961d4a5, original_name='Unknown'
        ),
    })
    start_weld_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1fe966f1, original_name='StartWeldSound'
        ),
    })
    weld_succeeded_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x7dec1aef, original_name='WeldSucceededSound'
        ),
    })
    weld_failed_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb3b5c8cb, original_name='WeldFailedSound'
        ),
    })
    unknown_0x902d66f9: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x902d66f9, original_name='Unknown'
        ),
    })
    unknown_0xedf4020e: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0xedf4020e, original_name='Unknown'
        ),
    })
    unknown_0x9cf48efc: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9cf48efc, original_name='Unknown'
        ),
    })
    welding_time: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe698941f, original_name='WeldingTime'
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
        if property_count != 25:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6ade8b91
        welding_tip = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfbf9569b
        welding_torch = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8e14567b
        welding_beam = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xea2c7744
        part_0xea2c7744 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5a3ed5a0
        part_0x5a3ed5a0 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x70bed427
        start_weld = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xacd369c1
        inside_collision = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1dad13a3
        outside_collision = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5b468021
        part_0x5b468021 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcecad2c3
        cmdl = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e542eaa
        weld_shatter = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbface762
        unknown_0xbface762 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3761c8e8
        unknown_0x3761c8e8 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x31c8bcaa
        weld_torch_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1e1a49d5
        weld_beam_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4a8cf2f7
        inside_weld_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfbf28895
        outside_weld_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1961d4a5
        unknown_0x1961d4a5 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1fe966f1
        start_weld_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7dec1aef
        weld_succeeded_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3b5c8cb
        weld_failed_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x902d66f9
        unknown_0x902d66f9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xedf4020e
        unknown_0xedf4020e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9cf48efc
        unknown_0x9cf48efc = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe698941f
        welding_time = struct.unpack('>f', data.read(4))[0]
    
        return cls(welding_tip, welding_torch, welding_beam, part_0xea2c7744, part_0x5a3ed5a0, start_weld, inside_collision, outside_collision, part_0x5b468021, cmdl, weld_shatter, unknown_0xbface762, unknown_0x3761c8e8, weld_torch_sound, weld_beam_sound, inside_weld_sound, outside_weld_sound, unknown_0x1961d4a5, start_weld_sound, weld_succeeded_sound, weld_failed_sound, unknown_0x902d66f9, unknown_0xedf4020e, unknown_0x9cf48efc, welding_time)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x19')  # 25 properties

        data.write(b'j\xde\x8b\x91')  # 0x6ade8b91
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.welding_tip.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfb\xf9V\x9b')  # 0xfbf9569b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.welding_torch))

        data.write(b'\x8e\x14V{')  # 0x8e14567b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.welding_beam))

        data.write(b'\xea,wD')  # 0xea2c7744
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0xea2c7744))

        data.write(b'Z>\xd5\xa0')  # 0x5a3ed5a0
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x5a3ed5a0))

        data.write(b"p\xbe\xd4'")  # 0x70bed427
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.start_weld))

        data.write(b'\xac\xd3i\xc1')  # 0xacd369c1
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.inside_collision))

        data.write(b'\x1d\xad\x13\xa3')  # 0x1dad13a3
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.outside_collision))

        data.write(b'[F\x80!')  # 0x5b468021
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x5b468021))

        data.write(b'\xce\xca\xd2\xc3')  # 0xcecad2c3
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl))

        data.write(b'~T.\xaa')  # 0x7e542eaa
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.weld_shatter))

        data.write(b'\xbf\xac\xe7b')  # 0xbface762
        data.write(b'\x00\x10')  # size
        self.unknown_0xbface762.to_stream(data)

        data.write(b'7a\xc8\xe8')  # 0x3761c8e8
        data.write(b'\x00\x10')  # size
        self.unknown_0x3761c8e8.to_stream(data)

        data.write(b'1\xc8\xbc\xaa')  # 0x31c8bcaa
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.weld_torch_sound))

        data.write(b'\x1e\x1aI\xd5')  # 0x1e1a49d5
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.weld_beam_sound))

        data.write(b'J\x8c\xf2\xf7')  # 0x4a8cf2f7
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.inside_weld_sound))

        data.write(b'\xfb\xf2\x88\x95')  # 0xfbf28895
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.outside_weld_sound))

        data.write(b'\x19a\xd4\xa5')  # 0x1961d4a5
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.unknown_0x1961d4a5))

        data.write(b'\x1f\xe9f\xf1')  # 0x1fe966f1
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.start_weld_sound))

        data.write(b'}\xec\x1a\xef')  # 0x7dec1aef
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.weld_succeeded_sound))

        data.write(b'\xb3\xb5\xc8\xcb')  # 0xb3b5c8cb
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.weld_failed_sound))

        data.write(b'\x90-f\xf9')  # 0x902d66f9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x902d66f9))

        data.write(b'\xed\xf4\x02\x0e')  # 0xedf4020e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xedf4020e))

        data.write(b'\x9c\xf4\x8e\xfc')  # 0x9cf48efc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9cf48efc))

        data.write(b'\xe6\x98\x94\x1f')  # 0xe698941f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.welding_time))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct24Json", data)
        return cls(
            welding_tip=AnimationParameters.from_json(json_data['welding_tip']),
            welding_torch=json_data['welding_torch'],
            welding_beam=json_data['welding_beam'],
            part_0xea2c7744=json_data['part_0xea2c7744'],
            part_0x5a3ed5a0=json_data['part_0x5a3ed5a0'],
            start_weld=json_data['start_weld'],
            inside_collision=json_data['inside_collision'],
            outside_collision=json_data['outside_collision'],
            part_0x5b468021=json_data['part_0x5b468021'],
            cmdl=json_data['cmdl'],
            weld_shatter=json_data['weld_shatter'],
            unknown_0xbface762=Color.from_json(json_data['unknown_0xbface762']),
            unknown_0x3761c8e8=Color.from_json(json_data['unknown_0x3761c8e8']),
            weld_torch_sound=json_data['weld_torch_sound'],
            weld_beam_sound=json_data['weld_beam_sound'],
            inside_weld_sound=json_data['inside_weld_sound'],
            outside_weld_sound=json_data['outside_weld_sound'],
            unknown_0x1961d4a5=json_data['unknown_0x1961d4a5'],
            start_weld_sound=json_data['start_weld_sound'],
            weld_succeeded_sound=json_data['weld_succeeded_sound'],
            weld_failed_sound=json_data['weld_failed_sound'],
            unknown_0x902d66f9=json_data['unknown_0x902d66f9'],
            unknown_0xedf4020e=json_data['unknown_0xedf4020e'],
            unknown_0x9cf48efc=json_data['unknown_0x9cf48efc'],
            welding_time=json_data['welding_time'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'welding_tip': self.welding_tip.to_json(),
            'welding_torch': self.welding_torch,
            'welding_beam': self.welding_beam,
            'part_0xea2c7744': self.part_0xea2c7744,
            'part_0x5a3ed5a0': self.part_0x5a3ed5a0,
            'start_weld': self.start_weld,
            'inside_collision': self.inside_collision,
            'outside_collision': self.outside_collision,
            'part_0x5b468021': self.part_0x5b468021,
            'cmdl': self.cmdl,
            'weld_shatter': self.weld_shatter,
            'unknown_0xbface762': self.unknown_0xbface762.to_json(),
            'unknown_0x3761c8e8': self.unknown_0x3761c8e8.to_json(),
            'weld_torch_sound': self.weld_torch_sound,
            'weld_beam_sound': self.weld_beam_sound,
            'inside_weld_sound': self.inside_weld_sound,
            'outside_weld_sound': self.outside_weld_sound,
            'unknown_0x1961d4a5': self.unknown_0x1961d4a5,
            'start_weld_sound': self.start_weld_sound,
            'weld_succeeded_sound': self.weld_succeeded_sound,
            'weld_failed_sound': self.weld_failed_sound,
            'unknown_0x902d66f9': self.unknown_0x902d66f9,
            'unknown_0xedf4020e': self.unknown_0xedf4020e,
            'unknown_0x9cf48efc': self.unknown_0x9cf48efc,
            'welding_time': self.welding_time,
        }


def _decode_welding_torch(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_welding_beam(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0xea2c7744(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x5a3ed5a0(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_start_weld(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_inside_collision(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_outside_collision(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x5b468021(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_weld_shatter(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0xbface762(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x3761c8e8(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_weld_torch_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_weld_beam_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_inside_weld_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_outside_weld_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x1961d4a5(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_start_weld_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_weld_succeeded_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_weld_failed_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x902d66f9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xedf4020e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9cf48efc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_welding_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x6ade8b91: ('welding_tip', AnimationParameters.from_stream),
    0xfbf9569b: ('welding_torch', _decode_welding_torch),
    0x8e14567b: ('welding_beam', _decode_welding_beam),
    0xea2c7744: ('part_0xea2c7744', _decode_part_0xea2c7744),
    0x5a3ed5a0: ('part_0x5a3ed5a0', _decode_part_0x5a3ed5a0),
    0x70bed427: ('start_weld', _decode_start_weld),
    0xacd369c1: ('inside_collision', _decode_inside_collision),
    0x1dad13a3: ('outside_collision', _decode_outside_collision),
    0x5b468021: ('part_0x5b468021', _decode_part_0x5b468021),
    0xcecad2c3: ('cmdl', _decode_cmdl),
    0x7e542eaa: ('weld_shatter', _decode_weld_shatter),
    0xbface762: ('unknown_0xbface762', _decode_unknown_0xbface762),
    0x3761c8e8: ('unknown_0x3761c8e8', _decode_unknown_0x3761c8e8),
    0x31c8bcaa: ('weld_torch_sound', _decode_weld_torch_sound),
    0x1e1a49d5: ('weld_beam_sound', _decode_weld_beam_sound),
    0x4a8cf2f7: ('inside_weld_sound', _decode_inside_weld_sound),
    0xfbf28895: ('outside_weld_sound', _decode_outside_weld_sound),
    0x1961d4a5: ('unknown_0x1961d4a5', _decode_unknown_0x1961d4a5),
    0x1fe966f1: ('start_weld_sound', _decode_start_weld_sound),
    0x7dec1aef: ('weld_succeeded_sound', _decode_weld_succeeded_sound),
    0xb3b5c8cb: ('weld_failed_sound', _decode_weld_failed_sound),
    0x902d66f9: ('unknown_0x902d66f9', _decode_unknown_0x902d66f9),
    0xedf4020e: ('unknown_0xedf4020e', _decode_unknown_0xedf4020e),
    0x9cf48efc: ('unknown_0x9cf48efc', _decode_unknown_0x9cf48efc),
    0xe698941f: ('welding_time', _decode_welding_time),
}
