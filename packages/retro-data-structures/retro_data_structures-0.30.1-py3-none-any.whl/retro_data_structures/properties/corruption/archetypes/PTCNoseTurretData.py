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
    class PTCNoseTurretDataJson(typing_extensions.TypedDict):
        aiming_prediction: float
        scanning_range_min: float
        scanning_range_max: float
        scanning_speed: float
        max_detection_angle: float
        unknown_0x494be648: float
        max_attack_angle: float
        max_rotation_speed: float
        max_rotation: float
        min_rotation: float
        max_pitch_speed: float
        max_pitch: float
        min_pitch: float
        projectile: int
        damage: json_util.JsonObject
        burst_delay: float
        unknown_0xb5702ca3: int
        burst_shot_delay: float
        unknown_0xaf28dc00: int
        sound_shot: int
        unknown_0x55d9abef: bool
    

@dataclasses.dataclass()
class PTCNoseTurretData(BaseProperty):
    aiming_prediction: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x395b81ef, original_name='AimingPrediction'
        ),
    })
    scanning_range_min: float = dataclasses.field(default=-90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x44e01377, original_name='ScanningRangeMin'
        ),
    })
    scanning_range_max: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa280bc96, original_name='ScanningRangeMax'
        ),
    })
    scanning_speed: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf71c6dd7, original_name='ScanningSpeed'
        ),
    })
    max_detection_angle: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x679028ba, original_name='MaxDetectionAngle'
        ),
    })
    unknown_0x494be648: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x494be648, original_name='Unknown'
        ),
    })
    max_attack_angle: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf11f7384, original_name='MaxAttackAngle'
        ),
    })
    max_rotation_speed: float = dataclasses.field(default=360.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x50eeb9e3, original_name='MaxRotationSpeed'
        ),
    })
    max_rotation: float = dataclasses.field(default=135.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7721deea, original_name='MaxRotation'
        ),
    })
    min_rotation: float = dataclasses.field(default=-135.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x26d865b7, original_name='MinRotation'
        ),
    })
    max_pitch_speed: float = dataclasses.field(default=360.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9597a329, original_name='MaxPitchSpeed'
        ),
    })
    max_pitch: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcd8c8763, original_name='MaxPitch'
        ),
    })
    min_pitch: float = dataclasses.field(default=-45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8dc3ff15, original_name='MinPitch'
        ),
    })
    projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xef485db9, original_name='Projectile'
        ),
    })
    damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x337f9524, original_name='Damage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    burst_delay: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xeb903473, original_name='BurstDelay'
        ),
    })
    unknown_0xb5702ca3: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0xb5702ca3, original_name='Unknown'
        ),
    })
    burst_shot_delay: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe8f29e1e, original_name='BurstShotDelay'
        ),
    })
    unknown_0xaf28dc00: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0xaf28dc00, original_name='Unknown'
        ),
    })
    sound_shot: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc23a1955, original_name='Sound_Shot'
        ),
    })
    unknown_0x55d9abef: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x55d9abef, original_name='Unknown'
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
        if property_count != 21:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x395b81ef
        aiming_prediction = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x44e01377
        scanning_range_min = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa280bc96
        scanning_range_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf71c6dd7
        scanning_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x679028ba
        max_detection_angle = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x494be648
        unknown_0x494be648 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf11f7384
        max_attack_angle = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x50eeb9e3
        max_rotation_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7721deea
        max_rotation = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x26d865b7
        min_rotation = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9597a329
        max_pitch_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcd8c8763
        max_pitch = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8dc3ff15
        min_pitch = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef485db9
        projectile = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x337f9524
        damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeb903473
        burst_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb5702ca3
        unknown_0xb5702ca3 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8f29e1e
        burst_shot_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaf28dc00
        unknown_0xaf28dc00 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc23a1955
        sound_shot = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x55d9abef
        unknown_0x55d9abef = struct.unpack('>?', data.read(1))[0]
    
        return cls(aiming_prediction, scanning_range_min, scanning_range_max, scanning_speed, max_detection_angle, unknown_0x494be648, max_attack_angle, max_rotation_speed, max_rotation, min_rotation, max_pitch_speed, max_pitch, min_pitch, projectile, damage, burst_delay, unknown_0xb5702ca3, burst_shot_delay, unknown_0xaf28dc00, sound_shot, unknown_0x55d9abef)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x15')  # 21 properties

        data.write(b'9[\x81\xef')  # 0x395b81ef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aiming_prediction))

        data.write(b'D\xe0\x13w')  # 0x44e01377
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scanning_range_min))

        data.write(b'\xa2\x80\xbc\x96')  # 0xa280bc96
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scanning_range_max))

        data.write(b'\xf7\x1cm\xd7')  # 0xf71c6dd7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scanning_speed))

        data.write(b'g\x90(\xba')  # 0x679028ba
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_detection_angle))

        data.write(b'IK\xe6H')  # 0x494be648
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x494be648))

        data.write(b'\xf1\x1fs\x84')  # 0xf11f7384
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_angle))

        data.write(b'P\xee\xb9\xe3')  # 0x50eeb9e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_rotation_speed))

        data.write(b'w!\xde\xea')  # 0x7721deea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_rotation))

        data.write(b'&\xd8e\xb7')  # 0x26d865b7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_rotation))

        data.write(b'\x95\x97\xa3)')  # 0x9597a329
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_pitch_speed))

        data.write(b'\xcd\x8c\x87c')  # 0xcd8c8763
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_pitch))

        data.write(b'\x8d\xc3\xff\x15')  # 0x8dc3ff15
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_pitch))

        data.write(b'\xefH]\xb9')  # 0xef485db9
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.projectile))

        data.write(b'3\x7f\x95$')  # 0x337f9524
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xeb\x904s')  # 0xeb903473
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.burst_delay))

        data.write(b'\xb5p,\xa3')  # 0xb5702ca3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xb5702ca3))

        data.write(b'\xe8\xf2\x9e\x1e')  # 0xe8f29e1e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.burst_shot_delay))

        data.write(b'\xaf(\xdc\x00')  # 0xaf28dc00
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xaf28dc00))

        data.write(b'\xc2:\x19U')  # 0xc23a1955
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_shot))

        data.write(b'U\xd9\xab\xef')  # 0x55d9abef
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x55d9abef))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PTCNoseTurretDataJson", data)
        return cls(
            aiming_prediction=json_data['aiming_prediction'],
            scanning_range_min=json_data['scanning_range_min'],
            scanning_range_max=json_data['scanning_range_max'],
            scanning_speed=json_data['scanning_speed'],
            max_detection_angle=json_data['max_detection_angle'],
            unknown_0x494be648=json_data['unknown_0x494be648'],
            max_attack_angle=json_data['max_attack_angle'],
            max_rotation_speed=json_data['max_rotation_speed'],
            max_rotation=json_data['max_rotation'],
            min_rotation=json_data['min_rotation'],
            max_pitch_speed=json_data['max_pitch_speed'],
            max_pitch=json_data['max_pitch'],
            min_pitch=json_data['min_pitch'],
            projectile=json_data['projectile'],
            damage=DamageInfo.from_json(json_data['damage']),
            burst_delay=json_data['burst_delay'],
            unknown_0xb5702ca3=json_data['unknown_0xb5702ca3'],
            burst_shot_delay=json_data['burst_shot_delay'],
            unknown_0xaf28dc00=json_data['unknown_0xaf28dc00'],
            sound_shot=json_data['sound_shot'],
            unknown_0x55d9abef=json_data['unknown_0x55d9abef'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'aiming_prediction': self.aiming_prediction,
            'scanning_range_min': self.scanning_range_min,
            'scanning_range_max': self.scanning_range_max,
            'scanning_speed': self.scanning_speed,
            'max_detection_angle': self.max_detection_angle,
            'unknown_0x494be648': self.unknown_0x494be648,
            'max_attack_angle': self.max_attack_angle,
            'max_rotation_speed': self.max_rotation_speed,
            'max_rotation': self.max_rotation,
            'min_rotation': self.min_rotation,
            'max_pitch_speed': self.max_pitch_speed,
            'max_pitch': self.max_pitch,
            'min_pitch': self.min_pitch,
            'projectile': self.projectile,
            'damage': self.damage.to_json(),
            'burst_delay': self.burst_delay,
            'unknown_0xb5702ca3': self.unknown_0xb5702ca3,
            'burst_shot_delay': self.burst_shot_delay,
            'unknown_0xaf28dc00': self.unknown_0xaf28dc00,
            'sound_shot': self.sound_shot,
            'unknown_0x55d9abef': self.unknown_0x55d9abef,
        }


def _decode_aiming_prediction(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scanning_range_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scanning_range_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scanning_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_detection_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x494be648(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attack_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_rotation_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_rotation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_rotation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_pitch_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_pitch(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_pitch(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_burst_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb5702ca3(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_burst_shot_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xaf28dc00(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_shot(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x55d9abef(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x395b81ef: ('aiming_prediction', _decode_aiming_prediction),
    0x44e01377: ('scanning_range_min', _decode_scanning_range_min),
    0xa280bc96: ('scanning_range_max', _decode_scanning_range_max),
    0xf71c6dd7: ('scanning_speed', _decode_scanning_speed),
    0x679028ba: ('max_detection_angle', _decode_max_detection_angle),
    0x494be648: ('unknown_0x494be648', _decode_unknown_0x494be648),
    0xf11f7384: ('max_attack_angle', _decode_max_attack_angle),
    0x50eeb9e3: ('max_rotation_speed', _decode_max_rotation_speed),
    0x7721deea: ('max_rotation', _decode_max_rotation),
    0x26d865b7: ('min_rotation', _decode_min_rotation),
    0x9597a329: ('max_pitch_speed', _decode_max_pitch_speed),
    0xcd8c8763: ('max_pitch', _decode_max_pitch),
    0x8dc3ff15: ('min_pitch', _decode_min_pitch),
    0xef485db9: ('projectile', _decode_projectile),
    0x337f9524: ('damage', DamageInfo.from_stream),
    0xeb903473: ('burst_delay', _decode_burst_delay),
    0xb5702ca3: ('unknown_0xb5702ca3', _decode_unknown_0xb5702ca3),
    0xe8f29e1e: ('burst_shot_delay', _decode_burst_shot_delay),
    0xaf28dc00: ('unknown_0xaf28dc00', _decode_unknown_0xaf28dc00),
    0xc23a1955: ('sound_shot', _decode_sound_shot),
    0x55d9abef: ('unknown_0x55d9abef', _decode_unknown_0x55d9abef),
}
