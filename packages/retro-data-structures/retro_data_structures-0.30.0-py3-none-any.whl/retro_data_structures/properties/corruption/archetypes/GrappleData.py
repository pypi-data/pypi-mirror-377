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
from retro_data_structures.properties.corruption.archetypes.GrappleBlock import GrappleBlock
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class GrappleDataJson(typing_extensions.TypedDict):
        grapple_type: int
        point_visible: bool
        unknown_0xb2bd2723: bool
        unknown_0x1a8dbea7: float
        unknown_0xa439ca6a: bool
        unknown_0x4b848c9b: bool
        grapple_block1: json_util.JsonObject
        grapple_block2: json_util.JsonObject
        grapple_block3: json_util.JsonObject
        grapple_block4: json_util.JsonObject
        grapple_block5: json_util.JsonObject
        unknown_0x5bbbe79e: float
        unknown_0x426f2f60: float
        sound_effect: int
        voltage_min_energy: float
        voltage_max_energy: float
        voltage_initial_energy: float
        voltage_energy_rate: float
        unknown_0x07648f63: int
    

@dataclasses.dataclass()
class GrappleData(BaseProperty):
    grapple_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5dcf91e1, original_name='GrappleType'
        ),
    })
    point_visible: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc10219bf, original_name='PointVisible'
        ),
    })
    unknown_0xb2bd2723: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb2bd2723, original_name='Unknown'
        ),
    })
    unknown_0x1a8dbea7: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1a8dbea7, original_name='Unknown'
        ),
    })
    unknown_0xa439ca6a: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa439ca6a, original_name='Unknown'
        ),
    })
    unknown_0x4b848c9b: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x4b848c9b, original_name='Unknown'
        ),
    })
    grapple_block1: GrappleBlock = dataclasses.field(default_factory=GrappleBlock, metadata={
        'reflection': FieldReflection[GrappleBlock](
            GrappleBlock, id=0x5f669ba0, original_name='GrappleBlock1', from_json=GrappleBlock.from_json, to_json=GrappleBlock.to_json
        ),
    })
    grapple_block2: GrappleBlock = dataclasses.field(default_factory=GrappleBlock, metadata={
        'reflection': FieldReflection[GrappleBlock](
            GrappleBlock, id=0xe2acf76e, original_name='GrappleBlock2', from_json=GrappleBlock.from_json, to_json=GrappleBlock.to_json
        ),
    })
    grapple_block3: GrappleBlock = dataclasses.field(default_factory=GrappleBlock, metadata={
        'reflection': FieldReflection[GrappleBlock](
            GrappleBlock, id=0x3f3a2eeb, original_name='GrappleBlock3', from_json=GrappleBlock.from_json, to_json=GrappleBlock.to_json
        ),
    })
    grapple_block4: GrappleBlock = dataclasses.field(default_factory=GrappleBlock, metadata={
        'reflection': FieldReflection[GrappleBlock](
            GrappleBlock, id=0x424928b3, original_name='GrappleBlock4', from_json=GrappleBlock.from_json, to_json=GrappleBlock.to_json
        ),
    })
    grapple_block5: GrappleBlock = dataclasses.field(default_factory=GrappleBlock, metadata={
        'reflection': FieldReflection[GrappleBlock](
            GrappleBlock, id=0x9fdff136, original_name='GrappleBlock5', from_json=GrappleBlock.from_json, to_json=GrappleBlock.to_json
        ),
    })
    unknown_0x5bbbe79e: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5bbbe79e, original_name='Unknown'
        ),
    })
    unknown_0x426f2f60: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x426f2f60, original_name='Unknown'
        ),
    })
    sound_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x771a3176, original_name='SoundEffect'
        ),
    })
    voltage_min_energy: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xefd287d9, original_name='VoltageMinEnergy'
        ),
    })
    voltage_max_energy: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x56f41ca8, original_name='VoltageMaxEnergy'
        ),
    })
    voltage_initial_energy: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4bdee69a, original_name='VoltageInitialEnergy'
        ),
    })
    voltage_energy_rate: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0598b045, original_name='VoltageEnergyRate'
        ),
    })
    unknown_0x07648f63: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x07648f63, original_name='Unknown'
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
        if property_count != 19:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5dcf91e1
        grapple_type = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc10219bf
        point_visible = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb2bd2723
        unknown_0xb2bd2723 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a8dbea7
        unknown_0x1a8dbea7 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa439ca6a
        unknown_0xa439ca6a = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4b848c9b
        unknown_0x4b848c9b = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5f669ba0
        grapple_block1 = GrappleBlock.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe2acf76e
        grapple_block2 = GrappleBlock.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3f3a2eeb
        grapple_block3 = GrappleBlock.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x424928b3
        grapple_block4 = GrappleBlock.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9fdff136
        grapple_block5 = GrappleBlock.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5bbbe79e
        unknown_0x5bbbe79e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x426f2f60
        unknown_0x426f2f60 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x771a3176
        sound_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xefd287d9
        voltage_min_energy = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x56f41ca8
        voltage_max_energy = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4bdee69a
        voltage_initial_energy = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0598b045
        voltage_energy_rate = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x07648f63
        unknown_0x07648f63 = struct.unpack('>l', data.read(4))[0]
    
        return cls(grapple_type, point_visible, unknown_0xb2bd2723, unknown_0x1a8dbea7, unknown_0xa439ca6a, unknown_0x4b848c9b, grapple_block1, grapple_block2, grapple_block3, grapple_block4, grapple_block5, unknown_0x5bbbe79e, unknown_0x426f2f60, sound_effect, voltage_min_energy, voltage_max_energy, voltage_initial_energy, voltage_energy_rate, unknown_0x07648f63)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        num_properties_offset = data.tell()
        data.write(b'\x00\x07')  # 7 properties
        num_properties_written = 7

        data.write(b']\xcf\x91\xe1')  # 0x5dcf91e1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.grapple_type))

        data.write(b'\xc1\x02\x19\xbf')  # 0xc10219bf
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.point_visible))

        if self.unknown_0xb2bd2723 != default_override.get('unknown_0xb2bd2723', False):
            num_properties_written += 1
            data.write(b"\xb2\xbd'#")  # 0xb2bd2723
            data.write(b'\x00\x01')  # size
            data.write(struct.pack('>?', self.unknown_0xb2bd2723))

        data.write(b'\x1a\x8d\xbe\xa7')  # 0x1a8dbea7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1a8dbea7))

        data.write(b'\xa49\xcaj')  # 0xa439ca6a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xa439ca6a))

        data.write(b'K\x84\x8c\x9b')  # 0x4b848c9b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x4b848c9b))

        data.write(b'_f\x9b\xa0')  # 0x5f669ba0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_block1.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe2\xac\xf7n')  # 0xe2acf76e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_block2.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        if self.grapple_block3 != default_override.get('grapple_block3', GrappleBlock()):
            num_properties_written += 1
            data.write(b'?:.\xeb')  # 0x3f3a2eeb
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.grapple_block3.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.grapple_block4 != default_override.get('grapple_block4', GrappleBlock()):
            num_properties_written += 1
            data.write(b'BI(\xb3')  # 0x424928b3
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.grapple_block4.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.grapple_block5 != default_override.get('grapple_block5', GrappleBlock()):
            num_properties_written += 1
            data.write(b'\x9f\xdf\xf16')  # 0x9fdff136
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.grapple_block5.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0x5bbbe79e != default_override.get('unknown_0x5bbbe79e', 8.0):
            num_properties_written += 1
            data.write(b'[\xbb\xe7\x9e')  # 0x5bbbe79e
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>f', self.unknown_0x5bbbe79e))

        if self.unknown_0x426f2f60 != default_override.get('unknown_0x426f2f60', 6.0):
            num_properties_written += 1
            data.write(b'Bo/`')  # 0x426f2f60
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>f', self.unknown_0x426f2f60))

        if self.sound_effect != default_override.get('sound_effect', default_asset_id):
            num_properties_written += 1
            data.write(b'w\x1a1v')  # 0x771a3176
            data.write(b'\x00\x08')  # size
            data.write(struct.pack(">Q", self.sound_effect))

        if self.voltage_min_energy != default_override.get('voltage_min_energy', 0.0):
            num_properties_written += 1
            data.write(b'\xef\xd2\x87\xd9')  # 0xefd287d9
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>f', self.voltage_min_energy))

        if self.voltage_max_energy != default_override.get('voltage_max_energy', 100.0):
            num_properties_written += 1
            data.write(b'V\xf4\x1c\xa8')  # 0x56f41ca8
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>f', self.voltage_max_energy))

        if self.voltage_initial_energy != default_override.get('voltage_initial_energy', 50.0):
            num_properties_written += 1
            data.write(b'K\xde\xe6\x9a')  # 0x4bdee69a
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>f', self.voltage_initial_energy))

        if self.voltage_energy_rate != default_override.get('voltage_energy_rate', 10.0):
            num_properties_written += 1
            data.write(b'\x05\x98\xb0E')  # 0x598b045
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>f', self.voltage_energy_rate))

        if self.unknown_0x07648f63 != default_override.get('unknown_0x07648f63', 0):
            num_properties_written += 1
            data.write(b'\x07d\x8fc')  # 0x7648f63
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>l', self.unknown_0x07648f63))

        if num_properties_written != 7:
            struct_end_offset = data.tell()
            data.seek(num_properties_offset)
            data.write(struct.pack(">H", num_properties_written))
            data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("GrappleDataJson", data)
        return cls(
            grapple_type=json_data['grapple_type'],
            point_visible=json_data['point_visible'],
            unknown_0xb2bd2723=json_data['unknown_0xb2bd2723'],
            unknown_0x1a8dbea7=json_data['unknown_0x1a8dbea7'],
            unknown_0xa439ca6a=json_data['unknown_0xa439ca6a'],
            unknown_0x4b848c9b=json_data['unknown_0x4b848c9b'],
            grapple_block1=GrappleBlock.from_json(json_data['grapple_block1']),
            grapple_block2=GrappleBlock.from_json(json_data['grapple_block2']),
            grapple_block3=GrappleBlock.from_json(json_data['grapple_block3']),
            grapple_block4=GrappleBlock.from_json(json_data['grapple_block4']),
            grapple_block5=GrappleBlock.from_json(json_data['grapple_block5']),
            unknown_0x5bbbe79e=json_data['unknown_0x5bbbe79e'],
            unknown_0x426f2f60=json_data['unknown_0x426f2f60'],
            sound_effect=json_data['sound_effect'],
            voltage_min_energy=json_data['voltage_min_energy'],
            voltage_max_energy=json_data['voltage_max_energy'],
            voltage_initial_energy=json_data['voltage_initial_energy'],
            voltage_energy_rate=json_data['voltage_energy_rate'],
            unknown_0x07648f63=json_data['unknown_0x07648f63'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'grapple_type': self.grapple_type,
            'point_visible': self.point_visible,
            'unknown_0xb2bd2723': self.unknown_0xb2bd2723,
            'unknown_0x1a8dbea7': self.unknown_0x1a8dbea7,
            'unknown_0xa439ca6a': self.unknown_0xa439ca6a,
            'unknown_0x4b848c9b': self.unknown_0x4b848c9b,
            'grapple_block1': self.grapple_block1.to_json(),
            'grapple_block2': self.grapple_block2.to_json(),
            'grapple_block3': self.grapple_block3.to_json(),
            'grapple_block4': self.grapple_block4.to_json(),
            'grapple_block5': self.grapple_block5.to_json(),
            'unknown_0x5bbbe79e': self.unknown_0x5bbbe79e,
            'unknown_0x426f2f60': self.unknown_0x426f2f60,
            'sound_effect': self.sound_effect,
            'voltage_min_energy': self.voltage_min_energy,
            'voltage_max_energy': self.voltage_max_energy,
            'voltage_initial_energy': self.voltage_initial_energy,
            'voltage_energy_rate': self.voltage_energy_rate,
            'unknown_0x07648f63': self.unknown_0x07648f63,
        }


def _decode_grapple_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_point_visible(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xb2bd2723(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x1a8dbea7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa439ca6a(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x4b848c9b(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x5bbbe79e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x426f2f60(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_voltage_min_energy(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_voltage_max_energy(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_voltage_initial_energy(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_voltage_energy_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x07648f63(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x5dcf91e1: ('grapple_type', _decode_grapple_type),
    0xc10219bf: ('point_visible', _decode_point_visible),
    0xb2bd2723: ('unknown_0xb2bd2723', _decode_unknown_0xb2bd2723),
    0x1a8dbea7: ('unknown_0x1a8dbea7', _decode_unknown_0x1a8dbea7),
    0xa439ca6a: ('unknown_0xa439ca6a', _decode_unknown_0xa439ca6a),
    0x4b848c9b: ('unknown_0x4b848c9b', _decode_unknown_0x4b848c9b),
    0x5f669ba0: ('grapple_block1', GrappleBlock.from_stream),
    0xe2acf76e: ('grapple_block2', GrappleBlock.from_stream),
    0x3f3a2eeb: ('grapple_block3', GrappleBlock.from_stream),
    0x424928b3: ('grapple_block4', GrappleBlock.from_stream),
    0x9fdff136: ('grapple_block5', GrappleBlock.from_stream),
    0x5bbbe79e: ('unknown_0x5bbbe79e', _decode_unknown_0x5bbbe79e),
    0x426f2f60: ('unknown_0x426f2f60', _decode_unknown_0x426f2f60),
    0x771a3176: ('sound_effect', _decode_sound_effect),
    0xefd287d9: ('voltage_min_energy', _decode_voltage_min_energy),
    0x56f41ca8: ('voltage_max_energy', _decode_voltage_max_energy),
    0x4bdee69a: ('voltage_initial_energy', _decode_voltage_initial_energy),
    0x598b045: ('voltage_energy_rate', _decode_voltage_energy_rate),
    0x7648f63: ('unknown_0x07648f63', _decode_unknown_0x07648f63),
}
