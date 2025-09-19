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
from retro_data_structures.properties.corruption.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.corruption.archetypes.GrappleData import GrappleData
from retro_data_structures.properties.corruption.archetypes.LaunchProjectileData import LaunchProjectileData

if typing.TYPE_CHECKING:
    class ShellBugDataJson(typing_extensions.TypedDict):
        launch_projectile_data: json_util.JsonObject
        unknown_0xa023555c: float
        unknown_0x4643fabd: float
        ball_range: float
        ball_radius: float
        look_ahead_time: float
        unknown_0x34bbc7a5: bool
        unknown_0xe5839374: float
        unknown_0x03e33c95: float
        weak_spot_vulnerability: json_util.JsonObject
        unknown_0x84e71870: bool
        unknown_0x76264db1: bool
        grapple_data: json_util.JsonObject
    

@dataclasses.dataclass()
class ShellBugData(BaseProperty):
    launch_projectile_data: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0xaba9a56d, original_name='LaunchProjectileData', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    unknown_0xa023555c: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa023555c, original_name='Unknown'
        ),
    })
    unknown_0x4643fabd: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4643fabd, original_name='Unknown'
        ),
    })
    ball_range: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0057a7d8, original_name='BallRange'
        ),
    })
    ball_radius: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0e2f537f, original_name='BallRadius'
        ),
    })
    look_ahead_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8cb20c53, original_name='LookAheadTime'
        ),
    })
    unknown_0x34bbc7a5: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x34bbc7a5, original_name='Unknown'
        ),
    })
    unknown_0xe5839374: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe5839374, original_name='Unknown'
        ),
    })
    unknown_0x03e33c95: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x03e33c95, original_name='Unknown'
        ),
    })
    weak_spot_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x950318f0, original_name='WeakSpotVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    unknown_0x84e71870: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x84e71870, original_name='Unknown'
        ),
    })
    unknown_0x76264db1: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x76264db1, original_name='Unknown'
        ),
    })
    grapple_data: GrappleData = dataclasses.field(default_factory=GrappleData, metadata={
        'reflection': FieldReflection[GrappleData](
            GrappleData, id=0xf609c637, original_name='GrappleData', from_json=GrappleData.from_json, to_json=GrappleData.to_json
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
        assert property_id == 0xaba9a56d
        launch_projectile_data = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa023555c
        unknown_0xa023555c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4643fabd
        unknown_0x4643fabd = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0057a7d8
        ball_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0e2f537f
        ball_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8cb20c53
        look_ahead_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x34bbc7a5
        unknown_0x34bbc7a5 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe5839374
        unknown_0xe5839374 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x03e33c95
        unknown_0x03e33c95 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x950318f0
        weak_spot_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x84e71870
        unknown_0x84e71870 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x76264db1
        unknown_0x76264db1 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf609c637
        grapple_data = GrappleData.from_stream(data, property_size)
    
        return cls(launch_projectile_data, unknown_0xa023555c, unknown_0x4643fabd, ball_range, ball_radius, look_ahead_time, unknown_0x34bbc7a5, unknown_0xe5839374, unknown_0x03e33c95, weak_spot_vulnerability, unknown_0x84e71870, unknown_0x76264db1, grapple_data)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\r')  # 13 properties

        data.write(b'\xab\xa9\xa5m')  # 0xaba9a56d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.launch_projectile_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa0#U\\')  # 0xa023555c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa023555c))

        data.write(b'FC\xfa\xbd')  # 0x4643fabd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4643fabd))

        data.write(b'\x00W\xa7\xd8')  # 0x57a7d8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_range))

        data.write(b'\x0e/S\x7f')  # 0xe2f537f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_radius))

        data.write(b'\x8c\xb2\x0cS')  # 0x8cb20c53
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.look_ahead_time))

        data.write(b'4\xbb\xc7\xa5')  # 0x34bbc7a5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x34bbc7a5))

        data.write(b'\xe5\x83\x93t')  # 0xe5839374
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe5839374))

        data.write(b'\x03\xe3<\x95')  # 0x3e33c95
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x03e33c95))

        data.write(b'\x95\x03\x18\xf0')  # 0x950318f0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.weak_spot_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x84\xe7\x18p')  # 0x84e71870
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x84e71870))

        data.write(b'v&M\xb1')  # 0x76264db1
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x76264db1))

        data.write(b'\xf6\t\xc67')  # 0xf609c637
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ShellBugDataJson", data)
        return cls(
            launch_projectile_data=LaunchProjectileData.from_json(json_data['launch_projectile_data']),
            unknown_0xa023555c=json_data['unknown_0xa023555c'],
            unknown_0x4643fabd=json_data['unknown_0x4643fabd'],
            ball_range=json_data['ball_range'],
            ball_radius=json_data['ball_radius'],
            look_ahead_time=json_data['look_ahead_time'],
            unknown_0x34bbc7a5=json_data['unknown_0x34bbc7a5'],
            unknown_0xe5839374=json_data['unknown_0xe5839374'],
            unknown_0x03e33c95=json_data['unknown_0x03e33c95'],
            weak_spot_vulnerability=DamageVulnerability.from_json(json_data['weak_spot_vulnerability']),
            unknown_0x84e71870=json_data['unknown_0x84e71870'],
            unknown_0x76264db1=json_data['unknown_0x76264db1'],
            grapple_data=GrappleData.from_json(json_data['grapple_data']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'launch_projectile_data': self.launch_projectile_data.to_json(),
            'unknown_0xa023555c': self.unknown_0xa023555c,
            'unknown_0x4643fabd': self.unknown_0x4643fabd,
            'ball_range': self.ball_range,
            'ball_radius': self.ball_radius,
            'look_ahead_time': self.look_ahead_time,
            'unknown_0x34bbc7a5': self.unknown_0x34bbc7a5,
            'unknown_0xe5839374': self.unknown_0xe5839374,
            'unknown_0x03e33c95': self.unknown_0x03e33c95,
            'weak_spot_vulnerability': self.weak_spot_vulnerability.to_json(),
            'unknown_0x84e71870': self.unknown_0x84e71870,
            'unknown_0x76264db1': self.unknown_0x76264db1,
            'grapple_data': self.grapple_data.to_json(),
        }


def _decode_unknown_0xa023555c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4643fabd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_look_ahead_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x34bbc7a5(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xe5839374(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x03e33c95(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x84e71870(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x76264db1(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xaba9a56d: ('launch_projectile_data', LaunchProjectileData.from_stream),
    0xa023555c: ('unknown_0xa023555c', _decode_unknown_0xa023555c),
    0x4643fabd: ('unknown_0x4643fabd', _decode_unknown_0x4643fabd),
    0x57a7d8: ('ball_range', _decode_ball_range),
    0xe2f537f: ('ball_radius', _decode_ball_radius),
    0x8cb20c53: ('look_ahead_time', _decode_look_ahead_time),
    0x34bbc7a5: ('unknown_0x34bbc7a5', _decode_unknown_0x34bbc7a5),
    0xe5839374: ('unknown_0xe5839374', _decode_unknown_0xe5839374),
    0x3e33c95: ('unknown_0x03e33c95', _decode_unknown_0x03e33c95),
    0x950318f0: ('weak_spot_vulnerability', DamageVulnerability.from_stream),
    0x84e71870: ('unknown_0x84e71870', _decode_unknown_0x84e71870),
    0x76264db1: ('unknown_0x76264db1', _decode_unknown_0x76264db1),
    0xf609c637: ('grapple_data', GrappleData.from_stream),
}
