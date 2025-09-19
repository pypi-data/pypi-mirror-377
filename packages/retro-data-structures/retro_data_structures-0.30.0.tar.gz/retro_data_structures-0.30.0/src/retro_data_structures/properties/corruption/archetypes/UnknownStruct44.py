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
from retro_data_structures.properties.corruption.archetypes.GrappleData import GrappleData
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct44Json(typing_extensions.TypedDict):
        wpsc: int
        carapace1: int
        carapace2: int
        stomach_plate: int
        tongue_piece: int
        tongue_tip: int
        part: int
        max_grapple_distance: float
        grapple_data: json_util.JsonObject
        sound_stomach_hit: int
        sound_phazon_lance: int
        sound_tongue_attack_loop: int
        sound_tongue_latch: int
        sound_tongue_release: int
    

@dataclasses.dataclass()
class UnknownStruct44(BaseProperty):
    wpsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x861cd2a0, original_name='WPSC'
        ),
    })
    carapace1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa8c2ac76, original_name='Carapace1'
        ),
    })
    carapace2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2e56ded8, original_name='Carapace2'
        ),
    })
    stomach_plate: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf47476ce, original_name='StomachPlate'
        ),
    })
    tongue_piece: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x470306be, original_name='TonguePiece'
        ),
    })
    tongue_tip: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x87952fc5, original_name='TongueTip'
        ),
    })
    part: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x01d82eeb, original_name='PART'
        ),
    })
    max_grapple_distance: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1cc93984, original_name='MaxGrappleDistance'
        ),
    })
    grapple_data: GrappleData = dataclasses.field(default_factory=GrappleData, metadata={
        'reflection': FieldReflection[GrappleData](
            GrappleData, id=0xf609c637, original_name='GrappleData', from_json=GrappleData.from_json, to_json=GrappleData.to_json
        ),
    })
    sound_stomach_hit: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd887792b, original_name='Sound_StomachHit'
        ),
    })
    sound_phazon_lance: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf9826473, original_name='Sound_PhazonLance'
        ),
    })
    sound_tongue_attack_loop: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9d6e1a47, original_name='Sound_TongueAttackLoop'
        ),
    })
    sound_tongue_latch: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x87e6e958, original_name='Sound_TongueLatch'
        ),
    })
    sound_tongue_release: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa6597839, original_name='Sound_TongueRelease'
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
        if property_count != 14:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x861cd2a0
        wpsc = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa8c2ac76
        carapace1 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2e56ded8
        carapace2 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf47476ce
        stomach_plate = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x470306be
        tongue_piece = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x87952fc5
        tongue_tip = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01d82eeb
        part = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1cc93984
        max_grapple_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf609c637
        grapple_data = GrappleData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd887792b
        sound_stomach_hit = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf9826473
        sound_phazon_lance = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9d6e1a47
        sound_tongue_attack_loop = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x87e6e958
        sound_tongue_latch = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa6597839
        sound_tongue_release = struct.unpack(">Q", data.read(8))[0]
    
        return cls(wpsc, carapace1, carapace2, stomach_plate, tongue_piece, tongue_tip, part, max_grapple_distance, grapple_data, sound_stomach_hit, sound_phazon_lance, sound_tongue_attack_loop, sound_tongue_latch, sound_tongue_release)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0e')  # 14 properties

        data.write(b'\x86\x1c\xd2\xa0')  # 0x861cd2a0
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.wpsc))

        data.write(b'\xa8\xc2\xacv')  # 0xa8c2ac76
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.carapace1))

        data.write(b'.V\xde\xd8')  # 0x2e56ded8
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.carapace2))

        data.write(b'\xf4tv\xce')  # 0xf47476ce
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.stomach_plate))

        data.write(b'G\x03\x06\xbe')  # 0x470306be
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.tongue_piece))

        data.write(b'\x87\x95/\xc5')  # 0x87952fc5
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.tongue_tip))

        data.write(b'\x01\xd8.\xeb')  # 0x1d82eeb
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part))

        data.write(b'\x1c\xc99\x84')  # 0x1cc93984
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_grapple_distance))

        data.write(b'\xf6\t\xc67')  # 0xf609c637
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd8\x87y+')  # 0xd887792b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_stomach_hit))

        data.write(b'\xf9\x82ds')  # 0xf9826473
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_phazon_lance))

        data.write(b'\x9dn\x1aG')  # 0x9d6e1a47
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_tongue_attack_loop))

        data.write(b'\x87\xe6\xe9X')  # 0x87e6e958
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_tongue_latch))

        data.write(b'\xa6Yx9')  # 0xa6597839
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_tongue_release))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct44Json", data)
        return cls(
            wpsc=json_data['wpsc'],
            carapace1=json_data['carapace1'],
            carapace2=json_data['carapace2'],
            stomach_plate=json_data['stomach_plate'],
            tongue_piece=json_data['tongue_piece'],
            tongue_tip=json_data['tongue_tip'],
            part=json_data['part'],
            max_grapple_distance=json_data['max_grapple_distance'],
            grapple_data=GrappleData.from_json(json_data['grapple_data']),
            sound_stomach_hit=json_data['sound_stomach_hit'],
            sound_phazon_lance=json_data['sound_phazon_lance'],
            sound_tongue_attack_loop=json_data['sound_tongue_attack_loop'],
            sound_tongue_latch=json_data['sound_tongue_latch'],
            sound_tongue_release=json_data['sound_tongue_release'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'wpsc': self.wpsc,
            'carapace1': self.carapace1,
            'carapace2': self.carapace2,
            'stomach_plate': self.stomach_plate,
            'tongue_piece': self.tongue_piece,
            'tongue_tip': self.tongue_tip,
            'part': self.part,
            'max_grapple_distance': self.max_grapple_distance,
            'grapple_data': self.grapple_data.to_json(),
            'sound_stomach_hit': self.sound_stomach_hit,
            'sound_phazon_lance': self.sound_phazon_lance,
            'sound_tongue_attack_loop': self.sound_tongue_attack_loop,
            'sound_tongue_latch': self.sound_tongue_latch,
            'sound_tongue_release': self.sound_tongue_release,
        }


def _decode_wpsc(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_carapace1(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_carapace2(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_stomach_plate(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_tongue_piece(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_tongue_tip(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_max_grapple_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_stomach_hit(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_phazon_lance(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_tongue_attack_loop(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_tongue_latch(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_sound_tongue_release(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x861cd2a0: ('wpsc', _decode_wpsc),
    0xa8c2ac76: ('carapace1', _decode_carapace1),
    0x2e56ded8: ('carapace2', _decode_carapace2),
    0xf47476ce: ('stomach_plate', _decode_stomach_plate),
    0x470306be: ('tongue_piece', _decode_tongue_piece),
    0x87952fc5: ('tongue_tip', _decode_tongue_tip),
    0x1d82eeb: ('part', _decode_part),
    0x1cc93984: ('max_grapple_distance', _decode_max_grapple_distance),
    0xf609c637: ('grapple_data', GrappleData.from_stream),
    0xd887792b: ('sound_stomach_hit', _decode_sound_stomach_hit),
    0xf9826473: ('sound_phazon_lance', _decode_sound_phazon_lance),
    0x9d6e1a47: ('sound_tongue_attack_loop', _decode_sound_tongue_attack_loop),
    0x87e6e958: ('sound_tongue_latch', _decode_sound_tongue_latch),
    0xa6597839: ('sound_tongue_release', _decode_sound_tongue_release),
}
