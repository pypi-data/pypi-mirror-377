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
from retro_data_structures.properties.echoes.archetypes.TDamageInfo import TDamageInfo

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakBall_BoostBallJson(typing_extensions.TypedDict):
        boost_ball_drain_time: float
        boost_ball_min_charge_time: float
        boost_ball_min_relative_speed_for_damage: float
        boost_ball_charge_time1: float
        boost_ball_charge_time2: float
        boost_ball_max_charge_time: float
        boost_ball_incremental_speed1: float
        boost_ball_incremental_speed2: float
        boost_ball_incremental_speed3: float
        unknown_0xbe605660: float
        boost_ball_damage: json_util.JsonObject
        unknown_0x6d210beb: float
        unknown_0xfdc6649d: float
        unknown_0x340be92f: float
    

@dataclasses.dataclass()
class TweakBall_BoostBall(BaseProperty):
    boost_ball_drain_time: float = dataclasses.field(default=0.33000001311302185, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7f336c73, original_name='BoostBallDrainTime'
        ),
    })
    boost_ball_min_charge_time: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0d23dbe7, original_name='BoostBallMinChargeTime'
        ),
    })
    boost_ball_min_relative_speed_for_damage: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x729e3cb3, original_name='BoostBallMinRelativeSpeedForDamage'
        ),
    })
    boost_ball_charge_time1: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0xef7a8e16, original_name='BoostBallChargeTime1'
        ),
    })
    boost_ball_charge_time2: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x69eefcb8, original_name='BoostBallChargeTime2'
        ),
    })
    boost_ball_max_charge_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5e85c303, original_name='BoostBallMaxChargeTime'
        ),
    })
    boost_ball_incremental_speed1: float = dataclasses.field(default=35.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x890d4ae5, original_name='BoostBallIncrementalSpeed1'
        ),
    })
    boost_ball_incremental_speed2: float = dataclasses.field(default=35.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0f99384b, original_name='BoostBallIncrementalSpeed2'
        ),
    })
    boost_ball_incremental_speed3: float = dataclasses.field(default=35.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc4c5ebee, original_name='BoostBallIncrementalSpeed3'
        ),
    })
    unknown_0xbe605660: float = dataclasses.field(default=1.7000000476837158, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbe605660, original_name='Unknown'
        ),
    })
    boost_ball_damage: TDamageInfo = dataclasses.field(default_factory=TDamageInfo, metadata={
        'reflection': FieldReflection[TDamageInfo](
            TDamageInfo, id=0x17e38e7e, original_name='BoostBallDamage', from_json=TDamageInfo.from_json, to_json=TDamageInfo.to_json
        ),
    })
    unknown_0x6d210beb: float = dataclasses.field(default=16.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6d210beb, original_name='Unknown'
        ),
    })
    unknown_0xfdc6649d: float = dataclasses.field(default=32.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfdc6649d, original_name='Unknown'
        ),
    })
    unknown_0x340be92f: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x340be92f, original_name='Unknown'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

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
        assert property_id == 0x7f336c73
        boost_ball_drain_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d23dbe7
        boost_ball_min_charge_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x729e3cb3
        boost_ball_min_relative_speed_for_damage = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef7a8e16
        boost_ball_charge_time1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x69eefcb8
        boost_ball_charge_time2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5e85c303
        boost_ball_max_charge_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x890d4ae5
        boost_ball_incremental_speed1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0f99384b
        boost_ball_incremental_speed2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc4c5ebee
        boost_ball_incremental_speed3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe605660
        unknown_0xbe605660 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x17e38e7e
        boost_ball_damage = TDamageInfo.from_stream(data, property_size, default_override={'damage_amount': 25.0, 'radius_damage_amount': 25.0, 'damage_radius': 2.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d210beb
        unknown_0x6d210beb = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfdc6649d
        unknown_0xfdc6649d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x340be92f
        unknown_0x340be92f = struct.unpack('>f', data.read(4))[0]
    
        return cls(boost_ball_drain_time, boost_ball_min_charge_time, boost_ball_min_relative_speed_for_damage, boost_ball_charge_time1, boost_ball_charge_time2, boost_ball_max_charge_time, boost_ball_incremental_speed1, boost_ball_incremental_speed2, boost_ball_incremental_speed3, unknown_0xbe605660, boost_ball_damage, unknown_0x6d210beb, unknown_0xfdc6649d, unknown_0x340be92f)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0e')  # 14 properties

        data.write(b'\x7f3ls')  # 0x7f336c73
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.boost_ball_drain_time))

        data.write(b'\r#\xdb\xe7')  # 0xd23dbe7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.boost_ball_min_charge_time))

        data.write(b'r\x9e<\xb3')  # 0x729e3cb3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.boost_ball_min_relative_speed_for_damage))

        data.write(b'\xefz\x8e\x16')  # 0xef7a8e16
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.boost_ball_charge_time1))

        data.write(b'i\xee\xfc\xb8')  # 0x69eefcb8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.boost_ball_charge_time2))

        data.write(b'^\x85\xc3\x03')  # 0x5e85c303
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.boost_ball_max_charge_time))

        data.write(b'\x89\rJ\xe5')  # 0x890d4ae5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.boost_ball_incremental_speed1))

        data.write(b'\x0f\x998K')  # 0xf99384b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.boost_ball_incremental_speed2))

        data.write(b'\xc4\xc5\xeb\xee')  # 0xc4c5ebee
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.boost_ball_incremental_speed3))

        data.write(b'\xbe`V`')  # 0xbe605660
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbe605660))

        data.write(b'\x17\xe3\x8e~')  # 0x17e38e7e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.boost_ball_damage.to_stream(data, default_override={'damage_amount': 25.0, 'radius_damage_amount': 25.0, 'damage_radius': 2.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'm!\x0b\xeb')  # 0x6d210beb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6d210beb))

        data.write(b'\xfd\xc6d\x9d')  # 0xfdc6649d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfdc6649d))

        data.write(b'4\x0b\xe9/')  # 0x340be92f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x340be92f))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakBall_BoostBallJson", data)
        return cls(
            boost_ball_drain_time=json_data['boost_ball_drain_time'],
            boost_ball_min_charge_time=json_data['boost_ball_min_charge_time'],
            boost_ball_min_relative_speed_for_damage=json_data['boost_ball_min_relative_speed_for_damage'],
            boost_ball_charge_time1=json_data['boost_ball_charge_time1'],
            boost_ball_charge_time2=json_data['boost_ball_charge_time2'],
            boost_ball_max_charge_time=json_data['boost_ball_max_charge_time'],
            boost_ball_incremental_speed1=json_data['boost_ball_incremental_speed1'],
            boost_ball_incremental_speed2=json_data['boost_ball_incremental_speed2'],
            boost_ball_incremental_speed3=json_data['boost_ball_incremental_speed3'],
            unknown_0xbe605660=json_data['unknown_0xbe605660'],
            boost_ball_damage=TDamageInfo.from_json(json_data['boost_ball_damage']),
            unknown_0x6d210beb=json_data['unknown_0x6d210beb'],
            unknown_0xfdc6649d=json_data['unknown_0xfdc6649d'],
            unknown_0x340be92f=json_data['unknown_0x340be92f'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'boost_ball_drain_time': self.boost_ball_drain_time,
            'boost_ball_min_charge_time': self.boost_ball_min_charge_time,
            'boost_ball_min_relative_speed_for_damage': self.boost_ball_min_relative_speed_for_damage,
            'boost_ball_charge_time1': self.boost_ball_charge_time1,
            'boost_ball_charge_time2': self.boost_ball_charge_time2,
            'boost_ball_max_charge_time': self.boost_ball_max_charge_time,
            'boost_ball_incremental_speed1': self.boost_ball_incremental_speed1,
            'boost_ball_incremental_speed2': self.boost_ball_incremental_speed2,
            'boost_ball_incremental_speed3': self.boost_ball_incremental_speed3,
            'unknown_0xbe605660': self.unknown_0xbe605660,
            'boost_ball_damage': self.boost_ball_damage.to_json(),
            'unknown_0x6d210beb': self.unknown_0x6d210beb,
            'unknown_0xfdc6649d': self.unknown_0xfdc6649d,
            'unknown_0x340be92f': self.unknown_0x340be92f,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.boost_ball_damage.dependencies_for, "boost_ball_damage", "TDamageInfo"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for TweakBall_BoostBall.{field_name} ({field_type}): {e}"
                )


def _decode_boost_ball_drain_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_boost_ball_min_charge_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_boost_ball_min_relative_speed_for_damage(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_boost_ball_charge_time1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_boost_ball_charge_time2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_boost_ball_max_charge_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_boost_ball_incremental_speed1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_boost_ball_incremental_speed2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_boost_ball_incremental_speed3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbe605660(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_boost_ball_damage(data: typing.BinaryIO, property_size: int) -> TDamageInfo:
    return TDamageInfo.from_stream(data, property_size, default_override={'damage_amount': 25.0, 'radius_damage_amount': 25.0, 'damage_radius': 2.0})


def _decode_unknown_0x6d210beb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfdc6649d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x340be92f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x7f336c73: ('boost_ball_drain_time', _decode_boost_ball_drain_time),
    0xd23dbe7: ('boost_ball_min_charge_time', _decode_boost_ball_min_charge_time),
    0x729e3cb3: ('boost_ball_min_relative_speed_for_damage', _decode_boost_ball_min_relative_speed_for_damage),
    0xef7a8e16: ('boost_ball_charge_time1', _decode_boost_ball_charge_time1),
    0x69eefcb8: ('boost_ball_charge_time2', _decode_boost_ball_charge_time2),
    0x5e85c303: ('boost_ball_max_charge_time', _decode_boost_ball_max_charge_time),
    0x890d4ae5: ('boost_ball_incremental_speed1', _decode_boost_ball_incremental_speed1),
    0xf99384b: ('boost_ball_incremental_speed2', _decode_boost_ball_incremental_speed2),
    0xc4c5ebee: ('boost_ball_incremental_speed3', _decode_boost_ball_incremental_speed3),
    0xbe605660: ('unknown_0xbe605660', _decode_unknown_0xbe605660),
    0x17e38e7e: ('boost_ball_damage', _decode_boost_ball_damage),
    0x6d210beb: ('unknown_0x6d210beb', _decode_unknown_0x6d210beb),
    0xfdc6649d: ('unknown_0xfdc6649d', _decode_unknown_0xfdc6649d),
    0x340be92f: ('unknown_0x340be92f', _decode_unknown_0x340be92f),
}
