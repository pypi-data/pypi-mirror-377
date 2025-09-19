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
import retro_data_structures.enums.corruption as enums
from retro_data_structures.properties.corruption.archetypes.RagDollData import RagDollData
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class CablePropertiesJson(typing_extensions.TypedDict):
        cable_segment_effect: int
        cable_bloom: int
        cable_lighting: int
        cable_type: int
        spline_type: int
        unknown_0xb6a06760: bool
        num_segments: int
        min_burn_rate: float
        max_burn_rate: float
        location_of_effect1: int
        location_of_effect2: int
        location_of_effect3: int
        unknown_0x833e4985: float
        is_shootable: bool
        is_generated: bool
        rag_doll_data: json_util.JsonObject
        impulse_magnitude: float
        impulse_frequency: float
        impulse_duration: float
        impulse_location: int
    

class CableBloom(enum.IntEnum):
    Unknown1 = 1131364394
    Unknown2 = 3535683408
    Unknown3 = 3476137679
    Unknown4 = 1255115501
    Unknown5 = 176197152

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


class CableLighting(enum.IntEnum):
    Unknown1 = 746881774
    Unknown2 = 596484757
    Unknown3 = 654430001

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


class CableType(enum.IntEnum):
    Unknown1 = 2487912838
    Unknown2 = 3596787146

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


class SplineType(enum.IntEnum):
    Unknown1 = 3115803663
    Unknown2 = 3253497337
    Unknown3 = 3709664811

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


class ImpulseLocation(enum.IntEnum):
    Unknown1 = 2161975732
    Unknown2 = 590757843

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
class CableProperties(BaseProperty):
    cable_segment_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SWHC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xffe83b77, original_name='CableSegmentEffect'
        ),
    })
    cable_bloom: CableBloom = dataclasses.field(default=CableBloom.Unknown1, metadata={
        'reflection': FieldReflection[CableBloom](
            CableBloom, id=0xd4b4b3d2, original_name='CableBloom', from_json=CableBloom.from_json, to_json=CableBloom.to_json
        ),
    })
    cable_lighting: CableLighting = dataclasses.field(default=CableLighting.Unknown1, metadata={
        'reflection': FieldReflection[CableLighting](
            CableLighting, id=0x3afbe300, original_name='CableLighting', from_json=CableLighting.from_json, to_json=CableLighting.to_json
        ),
    })
    cable_type: CableType = dataclasses.field(default=CableType.Unknown2, metadata={
        'reflection': FieldReflection[CableType](
            CableType, id=0x4b3a87e6, original_name='CableType', from_json=CableType.from_json, to_json=CableType.to_json
        ),
    })
    spline_type: SplineType = dataclasses.field(default=SplineType.Unknown1, metadata={
        'reflection': FieldReflection[SplineType](
            SplineType, id=0xcd578193, original_name='SplineType', from_json=SplineType.from_json, to_json=SplineType.to_json
        ),
    })
    unknown_0xb6a06760: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb6a06760, original_name='Unknown'
        ),
    })
    num_segments: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6586ec98, original_name='NumSegments'
        ),
    })
    min_burn_rate: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x405e8f55, original_name='MinBurnRate'
        ),
    })
    max_burn_rate: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x11a73408, original_name='MaxBurnRate'
        ),
    })
    location_of_effect1: enums.CableEnumEnum = dataclasses.field(default=enums.CableEnumEnum.Unknown1, metadata={
        'reflection': FieldReflection[enums.CableEnumEnum](
            enums.CableEnumEnum, id=0x44ef4dab, original_name='LocationOfEffect1', from_json=enums.CableEnumEnum.from_json, to_json=enums.CableEnumEnum.to_json
        ),
    })
    location_of_effect2: enums.CableEnumEnum = dataclasses.field(default=enums.CableEnumEnum.Unknown3, metadata={
        'reflection': FieldReflection[enums.CableEnumEnum](
            enums.CableEnumEnum, id=0x034f377b, original_name='LocationOfEffect2', from_json=enums.CableEnumEnum.from_json, to_json=enums.CableEnumEnum.to_json
        ),
    })
    location_of_effect3: enums.CableEnumEnum = dataclasses.field(default=enums.CableEnumEnum.Unknown2, metadata={
        'reflection': FieldReflection[enums.CableEnumEnum](
            enums.CableEnumEnum, id=0x3e2f1ecb, original_name='LocationOfEffect3', from_json=enums.CableEnumEnum.from_json, to_json=enums.CableEnumEnum.to_json
        ),
    })
    unknown_0x833e4985: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x833e4985, original_name='Unknown'
        ),
    })
    is_shootable: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x8c73cb7c, original_name='IsShootable'
        ),
    })
    is_generated: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xddb5e1d1, original_name='IsGenerated'
        ),
    })
    rag_doll_data: RagDollData = dataclasses.field(default_factory=RagDollData, metadata={
        'reflection': FieldReflection[RagDollData](
            RagDollData, id=0x84843807, original_name='RagDollData', from_json=RagDollData.from_json, to_json=RagDollData.to_json
        ),
    })
    impulse_magnitude: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6ad55d50, original_name='ImpulseMagnitude'
        ),
    })
    impulse_frequency: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xeb5ee47c, original_name='ImpulseFrequency'
        ),
    })
    impulse_duration: float = dataclasses.field(default=0.016699999570846558, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc25dc1b8, original_name='ImpulseDuration'
        ),
    })
    impulse_location: ImpulseLocation = dataclasses.field(default=ImpulseLocation.Unknown2, metadata={
        'reflection': FieldReflection[ImpulseLocation](
            ImpulseLocation, id=0xa0add2df, original_name='ImpulseLocation', from_json=ImpulseLocation.from_json, to_json=ImpulseLocation.to_json
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
        if property_count != 20:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xffe83b77
        cable_segment_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd4b4b3d2
        cable_bloom = CableBloom.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3afbe300
        cable_lighting = CableLighting.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4b3a87e6
        cable_type = CableType.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcd578193
        spline_type = SplineType.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb6a06760
        unknown_0xb6a06760 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6586ec98
        num_segments = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x405e8f55
        min_burn_rate = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x11a73408
        max_burn_rate = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x44ef4dab
        location_of_effect1 = enums.CableEnumEnum.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x034f377b
        location_of_effect2 = enums.CableEnumEnum.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3e2f1ecb
        location_of_effect3 = enums.CableEnumEnum.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x833e4985
        unknown_0x833e4985 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8c73cb7c
        is_shootable = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xddb5e1d1
        is_generated = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x84843807
        rag_doll_data = RagDollData.from_stream(data, property_size, default_override={'damp_rotation': False, 'ignore_max_time': True, 'ignore_all_collision': True})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6ad55d50
        impulse_magnitude = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeb5ee47c
        impulse_frequency = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc25dc1b8
        impulse_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa0add2df
        impulse_location = ImpulseLocation.from_stream(data)
    
        return cls(cable_segment_effect, cable_bloom, cable_lighting, cable_type, spline_type, unknown_0xb6a06760, num_segments, min_burn_rate, max_burn_rate, location_of_effect1, location_of_effect2, location_of_effect3, unknown_0x833e4985, is_shootable, is_generated, rag_doll_data, impulse_magnitude, impulse_frequency, impulse_duration, impulse_location)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x14')  # 20 properties

        data.write(b'\xff\xe8;w')  # 0xffe83b77
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cable_segment_effect))

        data.write(b'\xd4\xb4\xb3\xd2')  # 0xd4b4b3d2
        data.write(b'\x00\x04')  # size
        self.cable_bloom.to_stream(data)

        data.write(b':\xfb\xe3\x00')  # 0x3afbe300
        data.write(b'\x00\x04')  # size
        self.cable_lighting.to_stream(data)

        data.write(b'K:\x87\xe6')  # 0x4b3a87e6
        data.write(b'\x00\x04')  # size
        self.cable_type.to_stream(data)

        data.write(b'\xcdW\x81\x93')  # 0xcd578193
        data.write(b'\x00\x04')  # size
        self.spline_type.to_stream(data)

        data.write(b'\xb6\xa0g`')  # 0xb6a06760
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xb6a06760))

        data.write(b'e\x86\xec\x98')  # 0x6586ec98
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.num_segments))

        data.write(b'@^\x8fU')  # 0x405e8f55
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_burn_rate))

        data.write(b'\x11\xa74\x08')  # 0x11a73408
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_burn_rate))

        data.write(b'D\xefM\xab')  # 0x44ef4dab
        data.write(b'\x00\x04')  # size
        self.location_of_effect1.to_stream(data)

        data.write(b'\x03O7{')  # 0x34f377b
        data.write(b'\x00\x04')  # size
        self.location_of_effect2.to_stream(data)

        data.write(b'>/\x1e\xcb')  # 0x3e2f1ecb
        data.write(b'\x00\x04')  # size
        self.location_of_effect3.to_stream(data)

        data.write(b'\x83>I\x85')  # 0x833e4985
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x833e4985))

        data.write(b'\x8cs\xcb|')  # 0x8c73cb7c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_shootable))

        data.write(b'\xdd\xb5\xe1\xd1')  # 0xddb5e1d1
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_generated))

        data.write(b'\x84\x848\x07')  # 0x84843807
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.rag_doll_data.to_stream(data, default_override={'damp_rotation': False, 'ignore_max_time': True, 'ignore_all_collision': True})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'j\xd5]P')  # 0x6ad55d50
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.impulse_magnitude))

        data.write(b'\xeb^\xe4|')  # 0xeb5ee47c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.impulse_frequency))

        data.write(b'\xc2]\xc1\xb8')  # 0xc25dc1b8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.impulse_duration))

        data.write(b'\xa0\xad\xd2\xdf')  # 0xa0add2df
        data.write(b'\x00\x04')  # size
        self.impulse_location.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CablePropertiesJson", data)
        return cls(
            cable_segment_effect=json_data['cable_segment_effect'],
            cable_bloom=CableBloom.from_json(json_data['cable_bloom']),
            cable_lighting=CableLighting.from_json(json_data['cable_lighting']),
            cable_type=CableType.from_json(json_data['cable_type']),
            spline_type=SplineType.from_json(json_data['spline_type']),
            unknown_0xb6a06760=json_data['unknown_0xb6a06760'],
            num_segments=json_data['num_segments'],
            min_burn_rate=json_data['min_burn_rate'],
            max_burn_rate=json_data['max_burn_rate'],
            location_of_effect1=enums.CableEnumEnum.from_json(json_data['location_of_effect1']),
            location_of_effect2=enums.CableEnumEnum.from_json(json_data['location_of_effect2']),
            location_of_effect3=enums.CableEnumEnum.from_json(json_data['location_of_effect3']),
            unknown_0x833e4985=json_data['unknown_0x833e4985'],
            is_shootable=json_data['is_shootable'],
            is_generated=json_data['is_generated'],
            rag_doll_data=RagDollData.from_json(json_data['rag_doll_data']),
            impulse_magnitude=json_data['impulse_magnitude'],
            impulse_frequency=json_data['impulse_frequency'],
            impulse_duration=json_data['impulse_duration'],
            impulse_location=ImpulseLocation.from_json(json_data['impulse_location']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'cable_segment_effect': self.cable_segment_effect,
            'cable_bloom': self.cable_bloom.to_json(),
            'cable_lighting': self.cable_lighting.to_json(),
            'cable_type': self.cable_type.to_json(),
            'spline_type': self.spline_type.to_json(),
            'unknown_0xb6a06760': self.unknown_0xb6a06760,
            'num_segments': self.num_segments,
            'min_burn_rate': self.min_burn_rate,
            'max_burn_rate': self.max_burn_rate,
            'location_of_effect1': self.location_of_effect1.to_json(),
            'location_of_effect2': self.location_of_effect2.to_json(),
            'location_of_effect3': self.location_of_effect3.to_json(),
            'unknown_0x833e4985': self.unknown_0x833e4985,
            'is_shootable': self.is_shootable,
            'is_generated': self.is_generated,
            'rag_doll_data': self.rag_doll_data.to_json(),
            'impulse_magnitude': self.impulse_magnitude,
            'impulse_frequency': self.impulse_frequency,
            'impulse_duration': self.impulse_duration,
            'impulse_location': self.impulse_location.to_json(),
        }


def _decode_cable_segment_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cable_bloom(data: typing.BinaryIO, property_size: int) -> CableBloom:
    return CableBloom.from_stream(data)


def _decode_cable_lighting(data: typing.BinaryIO, property_size: int) -> CableLighting:
    return CableLighting.from_stream(data)


def _decode_cable_type(data: typing.BinaryIO, property_size: int) -> CableType:
    return CableType.from_stream(data)


def _decode_spline_type(data: typing.BinaryIO, property_size: int) -> SplineType:
    return SplineType.from_stream(data)


def _decode_unknown_0xb6a06760(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_num_segments(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_min_burn_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_burn_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_location_of_effect1(data: typing.BinaryIO, property_size: int) -> enums.CableEnumEnum:
    return enums.CableEnumEnum.from_stream(data)


def _decode_location_of_effect2(data: typing.BinaryIO, property_size: int) -> enums.CableEnumEnum:
    return enums.CableEnumEnum.from_stream(data)


def _decode_location_of_effect3(data: typing.BinaryIO, property_size: int) -> enums.CableEnumEnum:
    return enums.CableEnumEnum.from_stream(data)


def _decode_unknown_0x833e4985(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_is_shootable(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_is_generated(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_rag_doll_data(data: typing.BinaryIO, property_size: int) -> RagDollData:
    return RagDollData.from_stream(data, property_size, default_override={'damp_rotation': False, 'ignore_max_time': True, 'ignore_all_collision': True})


def _decode_impulse_magnitude(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_impulse_frequency(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_impulse_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_impulse_location(data: typing.BinaryIO, property_size: int) -> ImpulseLocation:
    return ImpulseLocation.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xffe83b77: ('cable_segment_effect', _decode_cable_segment_effect),
    0xd4b4b3d2: ('cable_bloom', _decode_cable_bloom),
    0x3afbe300: ('cable_lighting', _decode_cable_lighting),
    0x4b3a87e6: ('cable_type', _decode_cable_type),
    0xcd578193: ('spline_type', _decode_spline_type),
    0xb6a06760: ('unknown_0xb6a06760', _decode_unknown_0xb6a06760),
    0x6586ec98: ('num_segments', _decode_num_segments),
    0x405e8f55: ('min_burn_rate', _decode_min_burn_rate),
    0x11a73408: ('max_burn_rate', _decode_max_burn_rate),
    0x44ef4dab: ('location_of_effect1', _decode_location_of_effect1),
    0x34f377b: ('location_of_effect2', _decode_location_of_effect2),
    0x3e2f1ecb: ('location_of_effect3', _decode_location_of_effect3),
    0x833e4985: ('unknown_0x833e4985', _decode_unknown_0x833e4985),
    0x8c73cb7c: ('is_shootable', _decode_is_shootable),
    0xddb5e1d1: ('is_generated', _decode_is_generated),
    0x84843807: ('rag_doll_data', _decode_rag_doll_data),
    0x6ad55d50: ('impulse_magnitude', _decode_impulse_magnitude),
    0xeb5ee47c: ('impulse_frequency', _decode_impulse_frequency),
    0xc25dc1b8: ('impulse_duration', _decode_impulse_duration),
    0xa0add2df: ('impulse_location', _decode_impulse_location),
}
