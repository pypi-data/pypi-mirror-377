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
from retro_data_structures.properties.corruption.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct37Json(typing_extensions.TypedDict):
        speed: float
        track_time: float
        track_disable_distance: float
        unknown: float
        contact_damage: json_util.JsonObject
        slam_damage: json_util.JsonObject
        throw_damage: json_util.JsonObject
        launch_ball_speed: float
        contact_effect: int
        cable_segment_effect: int
        claw_model: int
        caud: int
        latch_morphball_sound: int
    

@dataclasses.dataclass()
class UnknownStruct37(BaseProperty):
    speed: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6392404e, original_name='Speed'
        ),
    })
    track_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc4489506, original_name='TrackTime'
        ),
    })
    track_disable_distance: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x31ca76c8, original_name='TrackDisableDistance'
        ),
    })
    unknown: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x963c1729, original_name='Unknown'
        ),
    })
    contact_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xd756416e, original_name='ContactDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    slam_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x480103f3, original_name='SlamDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    throw_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xd80b1f34, original_name='ThrowDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    launch_ball_speed: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5324cbfb, original_name='LaunchBallSpeed'
        ),
    })
    contact_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4f387c49, original_name='ContactEffect'
        ),
    })
    cable_segment_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SWHC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xffe83b77, original_name='CableSegmentEffect'
        ),
    })
    claw_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3d313da6, original_name='ClawModel'
        ),
    })
    caud: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5c5bce53, original_name='CAUD'
        ),
    })
    latch_morphball_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb97c1467, original_name='LatchMorphballSound'
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
        if property_count != 13:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6392404e
        speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc4489506
        track_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x31ca76c8
        track_disable_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x963c1729
        unknown = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd756416e
        contact_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x480103f3
        slam_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd80b1f34
        throw_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5324cbfb
        launch_ball_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4f387c49
        contact_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xffe83b77
        cable_segment_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d313da6
        claw_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5c5bce53
        caud = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb97c1467
        latch_morphball_sound = struct.unpack(">Q", data.read(8))[0]
    
        return cls(speed, track_time, track_disable_distance, unknown, contact_damage, slam_damage, throw_damage, launch_ball_speed, contact_effect, cable_segment_effect, claw_model, caud, latch_morphball_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\r')  # 13 properties

        data.write(b'c\x92@N')  # 0x6392404e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.speed))

        data.write(b'\xc4H\x95\x06')  # 0xc4489506
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.track_time))

        data.write(b'1\xcav\xc8')  # 0x31ca76c8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.track_disable_distance))

        data.write(b'\x96<\x17)')  # 0x963c1729
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'\xd7VAn')  # 0xd756416e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.contact_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'H\x01\x03\xf3')  # 0x480103f3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.slam_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd8\x0b\x1f4')  # 0xd80b1f34
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.throw_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'S$\xcb\xfb')  # 0x5324cbfb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.launch_ball_speed))

        data.write(b'O8|I')  # 0x4f387c49
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.contact_effect))

        data.write(b'\xff\xe8;w')  # 0xffe83b77
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cable_segment_effect))

        data.write(b'=1=\xa6')  # 0x3d313da6
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.claw_model))

        data.write(b'\\[\xceS')  # 0x5c5bce53
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud))

        data.write(b'\xb9|\x14g')  # 0xb97c1467
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.latch_morphball_sound))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct37Json", data)
        return cls(
            speed=json_data['speed'],
            track_time=json_data['track_time'],
            track_disable_distance=json_data['track_disable_distance'],
            unknown=json_data['unknown'],
            contact_damage=DamageInfo.from_json(json_data['contact_damage']),
            slam_damage=DamageInfo.from_json(json_data['slam_damage']),
            throw_damage=DamageInfo.from_json(json_data['throw_damage']),
            launch_ball_speed=json_data['launch_ball_speed'],
            contact_effect=json_data['contact_effect'],
            cable_segment_effect=json_data['cable_segment_effect'],
            claw_model=json_data['claw_model'],
            caud=json_data['caud'],
            latch_morphball_sound=json_data['latch_morphball_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'speed': self.speed,
            'track_time': self.track_time,
            'track_disable_distance': self.track_disable_distance,
            'unknown': self.unknown,
            'contact_damage': self.contact_damage.to_json(),
            'slam_damage': self.slam_damage.to_json(),
            'throw_damage': self.throw_damage.to_json(),
            'launch_ball_speed': self.launch_ball_speed,
            'contact_effect': self.contact_effect,
            'cable_segment_effect': self.cable_segment_effect,
            'claw_model': self.claw_model,
            'caud': self.caud,
            'latch_morphball_sound': self.latch_morphball_sound,
        }


def _decode_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_track_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_track_disable_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_launch_ball_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_contact_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cable_segment_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_claw_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_latch_morphball_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x6392404e: ('speed', _decode_speed),
    0xc4489506: ('track_time', _decode_track_time),
    0x31ca76c8: ('track_disable_distance', _decode_track_disable_distance),
    0x963c1729: ('unknown', _decode_unknown),
    0xd756416e: ('contact_damage', DamageInfo.from_stream),
    0x480103f3: ('slam_damage', DamageInfo.from_stream),
    0xd80b1f34: ('throw_damage', DamageInfo.from_stream),
    0x5324cbfb: ('launch_ball_speed', _decode_launch_ball_speed),
    0x4f387c49: ('contact_effect', _decode_contact_effect),
    0xffe83b77: ('cable_segment_effect', _decode_cable_segment_effect),
    0x3d313da6: ('claw_model', _decode_claw_model),
    0x5c5bce53: ('caud', _decode_caud),
    0xb97c1467: ('latch_morphball_sound', _decode_latch_morphball_sound),
}
