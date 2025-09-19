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

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakBall_MovementJson(typing_extensions.TypedDict):
        forward_accel_normal: float
        forward_accel_air: float
        forward_accel_ice: float
        forward_accel_organic: float
        forward_accel_water: float
        forward_accel_lava: float
        forward_accel_phazon: float
        forward_accel_shrubbery: float
        movement_friction_normal: float
        movement_friction_air: float
        movement_friction_ice: float
        movement_friction_organic: float
        movement_friction_water: float
        movement_friction_lava: float
        movement_friction_phazon: float
        movement_friction_shrubbery: float
        forward_max_speed_normal: float
        forward_max_speed_air: float
        forward_max_speed_ice: float
        forward_max_speed_organic: float
        forward_max_speed_water: float
        forward_max_speed_lava: float
        forward_max_speed_phazon: float
        forward_max_speed_shrubbery: float
        unknown_0x85ee51ed: float
        unknown_0x6d7811f5: float
        ball_up_gravity: float
        ball_down_gravity: float
        ball_forward_braking_accel_normal: float
        ball_forward_braking_accel_air: float
        ball_forward_braking_accel_ice: float
        ball_forward_braking_accel_organic: float
        ball_forward_braking_accel_water: float
        ball_forward_braking_accel_lava: float
        ball_forward_braking_accel_phazon: float
        ball_forward_braking_accel_shrubbery: float
        ball_gravity: float
        ball_water_gravity: float
        unknown_0xeeb74968: float
        ball_boost_height: float
        unknown_0xe2bb0298: float
        minimum_alignment_speed: float
        tireness: float
        max_lean_angle: float
        tire_to_marble_threshold_speed: float
        marble_to_tire_threshold_speed: float
        force_to_lean_gain: float
        lean_tracking_gain: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x18d0b2da, 0x84f61ac5, 0xedb06c1d, 0x56f9f2af, 0xd05b643f, 0x122ce118, 0xf848dabe, 0x68ac6028, 0xd4a25028, 0x2b5cb136, 0x421ac7ee, 0x586137d, 0xaece038b, 0x3637e815, 0x343a384c, 0xcaf4624, 0xffd4a030, 0x59dfbcb9, 0x3099ca61, 0x16c1fddb, 0x6c648931, 0x4b42f5a9, 0x1f4cc854, 0xb3408173, 0x85ee51ed, 0x6d7811f5, 0xf80a0655, 0x92f30f94, 0xb06ac970, 0xbb3c2629, 0xd27a50f1, 0x60520222, 0xdff9b92, 0xbbaf8577, 0x50f2a114, 0x5b3c4299, 0xd83e5eec, 0x9c905747, 0xeeb74968, 0xbd28af6e, 0xe2bb0298, 0xe46fa96a, 0x4ed87ebd, 0xca8edeab, 0x96226d18, 0x191f4f62, 0x54c20211, 0xb90a721e)


@dataclasses.dataclass()
class TweakBall_Movement(BaseProperty):
    forward_accel_normal: float = dataclasses.field(default=12000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x18d0b2da, original_name='ForwardAccelNormal'
        ),
    })
    forward_accel_air: float = dataclasses.field(default=3000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x84f61ac5, original_name='ForwardAccelAir'
        ),
    })
    forward_accel_ice: float = dataclasses.field(default=12000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xedb06c1d, original_name='ForwardAccelIce'
        ),
    })
    forward_accel_organic: float = dataclasses.field(default=12000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x56f9f2af, original_name='ForwardAccelOrganic'
        ),
    })
    forward_accel_water: float = dataclasses.field(default=8000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd05b643f, original_name='ForwardAccelWater'
        ),
    })
    forward_accel_lava: float = dataclasses.field(default=8000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x122ce118, original_name='ForwardAccelLava'
        ),
    })
    forward_accel_phazon: float = dataclasses.field(default=8000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf848dabe, original_name='ForwardAccelPhazon'
        ),
    })
    forward_accel_shrubbery: float = dataclasses.field(default=8000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x68ac6028, original_name='ForwardAccelShrubbery'
        ),
    })
    movement_friction_normal: float = dataclasses.field(default=0.15000000596046448, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd4a25028, original_name='MovementFrictionNormal'
        ),
    })
    movement_friction_air: float = dataclasses.field(default=0.15000000596046448, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2b5cb136, original_name='MovementFrictionAir'
        ),
    })
    movement_friction_ice: float = dataclasses.field(default=0.15000000596046448, metadata={
        'reflection': FieldReflection[float](
            float, id=0x421ac7ee, original_name='MovementFrictionIce'
        ),
    })
    movement_friction_organic: float = dataclasses.field(default=0.15000000596046448, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0586137d, original_name='MovementFrictionOrganic'
        ),
    })
    movement_friction_water: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0xaece038b, original_name='MovementFrictionWater'
        ),
    })
    movement_friction_lava: float = dataclasses.field(default=0.15000000596046448, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3637e815, original_name='MovementFrictionLava'
        ),
    })
    movement_friction_phazon: float = dataclasses.field(default=0.15000000596046448, metadata={
        'reflection': FieldReflection[float](
            float, id=0x343a384c, original_name='MovementFrictionPhazon'
        ),
    })
    movement_friction_shrubbery: float = dataclasses.field(default=0.15000000596046448, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0caf4624, original_name='MovementFrictionShrubbery'
        ),
    })
    forward_max_speed_normal: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xffd4a030, original_name='ForwardMaxSpeedNormal'
        ),
    })
    forward_max_speed_air: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x59dfbcb9, original_name='ForwardMaxSpeedAir'
        ),
    })
    forward_max_speed_ice: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3099ca61, original_name='ForwardMaxSpeedIce'
        ),
    })
    forward_max_speed_organic: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x16c1fddb, original_name='ForwardMaxSpeedOrganic'
        ),
    })
    forward_max_speed_water: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6c648931, original_name='ForwardMaxSpeedWater'
        ),
    })
    forward_max_speed_lava: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4b42f5a9, original_name='ForwardMaxSpeedLava'
        ),
    })
    forward_max_speed_phazon: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1f4cc854, original_name='ForwardMaxSpeedPhazon'
        ),
    })
    forward_max_speed_shrubbery: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb3408173, original_name='ForwardMaxSpeedShrubbery'
        ),
    })
    unknown_0x85ee51ed: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x85ee51ed, original_name='Unknown'
        ),
    })
    unknown_0x6d7811f5: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6d7811f5, original_name='Unknown'
        ),
    })
    ball_up_gravity: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf80a0655, original_name='BallUpGravity'
        ),
    })
    ball_down_gravity: float = dataclasses.field(default=35.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x92f30f94, original_name='BallDownGravity'
        ),
    })
    ball_forward_braking_accel_normal: float = dataclasses.field(default=12000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb06ac970, original_name='BallForwardBrakingAccelNormal'
        ),
    })
    ball_forward_braking_accel_air: float = dataclasses.field(default=3000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbb3c2629, original_name='BallForwardBrakingAccelAir'
        ),
    })
    ball_forward_braking_accel_ice: float = dataclasses.field(default=12000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd27a50f1, original_name='BallForwardBrakingAccelIce'
        ),
    })
    ball_forward_braking_accel_organic: float = dataclasses.field(default=12000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x60520222, original_name='BallForwardBrakingAccelOrganic'
        ),
    })
    ball_forward_braking_accel_water: float = dataclasses.field(default=12000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0dff9b92, original_name='BallForwardBrakingAccelWater'
        ),
    })
    ball_forward_braking_accel_lava: float = dataclasses.field(default=12000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbbaf8577, original_name='BallForwardBrakingAccelLava'
        ),
    })
    ball_forward_braking_accel_phazon: float = dataclasses.field(default=12000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x50f2a114, original_name='BallForwardBrakingAccelPhazon'
        ),
    })
    ball_forward_braking_accel_shrubbery: float = dataclasses.field(default=12000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5b3c4299, original_name='BallForwardBrakingAccelShrubbery'
        ),
    })
    ball_gravity: float = dataclasses.field(default=76.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd83e5eec, original_name='BallGravity'
        ),
    })
    ball_water_gravity: float = dataclasses.field(default=35.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9c905747, original_name='BallWaterGravity'
        ),
    })
    unknown_0xeeb74968: float = dataclasses.field(default=3.200000047683716, metadata={
        'reflection': FieldReflection[float](
            float, id=0xeeb74968, original_name='Unknown'
        ),
    })
    ball_boost_height: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbd28af6e, original_name='BallBoostHeight'
        ),
    })
    unknown_0xe2bb0298: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe2bb0298, original_name='Unknown'
        ),
    })
    minimum_alignment_speed: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe46fa96a, original_name='MinimumAlignmentSpeed'
        ),
    })
    tireness: float = dataclasses.field(default=120.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4ed87ebd, original_name='Tireness'
        ),
    })
    max_lean_angle: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xca8edeab, original_name='MaxLeanAngle'
        ),
    })
    tire_to_marble_threshold_speed: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x96226d18, original_name='TireToMarbleThresholdSpeed'
        ),
    })
    marble_to_tire_threshold_speed: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x191f4f62, original_name='MarbleToTireThresholdSpeed'
        ),
    })
    force_to_lean_gain: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x54c20211, original_name='ForceToLeanGain'
        ),
    })
    lean_tracking_gain: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb90a721e, original_name='LeanTrackingGain'
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
        if property_count != 48:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(480))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27], dec[30], dec[33], dec[36], dec[39], dec[42], dec[45], dec[48], dec[51], dec[54], dec[57], dec[60], dec[63], dec[66], dec[69], dec[72], dec[75], dec[78], dec[81], dec[84], dec[87], dec[90], dec[93], dec[96], dec[99], dec[102], dec[105], dec[108], dec[111], dec[114], dec[117], dec[120], dec[123], dec[126], dec[129], dec[132], dec[135], dec[138], dec[141]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
            dec[20],
            dec[23],
            dec[26],
            dec[29],
            dec[32],
            dec[35],
            dec[38],
            dec[41],
            dec[44],
            dec[47],
            dec[50],
            dec[53],
            dec[56],
            dec[59],
            dec[62],
            dec[65],
            dec[68],
            dec[71],
            dec[74],
            dec[77],
            dec[80],
            dec[83],
            dec[86],
            dec[89],
            dec[92],
            dec[95],
            dec[98],
            dec[101],
            dec[104],
            dec[107],
            dec[110],
            dec[113],
            dec[116],
            dec[119],
            dec[122],
            dec[125],
            dec[128],
            dec[131],
            dec[134],
            dec[137],
            dec[140],
            dec[143],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x000')  # 48 properties

        data.write(b'\x18\xd0\xb2\xda')  # 0x18d0b2da
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_accel_normal))

        data.write(b'\x84\xf6\x1a\xc5')  # 0x84f61ac5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_accel_air))

        data.write(b'\xed\xb0l\x1d')  # 0xedb06c1d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_accel_ice))

        data.write(b'V\xf9\xf2\xaf')  # 0x56f9f2af
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_accel_organic))

        data.write(b'\xd0[d?')  # 0xd05b643f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_accel_water))

        data.write(b'\x12,\xe1\x18')  # 0x122ce118
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_accel_lava))

        data.write(b'\xf8H\xda\xbe')  # 0xf848dabe
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_accel_phazon))

        data.write(b'h\xac`(')  # 0x68ac6028
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_accel_shrubbery))

        data.write(b'\xd4\xa2P(')  # 0xd4a25028
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.movement_friction_normal))

        data.write(b'+\\\xb16')  # 0x2b5cb136
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.movement_friction_air))

        data.write(b'B\x1a\xc7\xee')  # 0x421ac7ee
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.movement_friction_ice))

        data.write(b'\x05\x86\x13}')  # 0x586137d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.movement_friction_organic))

        data.write(b'\xae\xce\x03\x8b')  # 0xaece038b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.movement_friction_water))

        data.write(b'67\xe8\x15')  # 0x3637e815
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.movement_friction_lava))

        data.write(b'4:8L')  # 0x343a384c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.movement_friction_phazon))

        data.write(b'\x0c\xafF$')  # 0xcaf4624
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.movement_friction_shrubbery))

        data.write(b'\xff\xd4\xa00')  # 0xffd4a030
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_max_speed_normal))

        data.write(b'Y\xdf\xbc\xb9')  # 0x59dfbcb9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_max_speed_air))

        data.write(b'0\x99\xcaa')  # 0x3099ca61
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_max_speed_ice))

        data.write(b'\x16\xc1\xfd\xdb')  # 0x16c1fddb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_max_speed_organic))

        data.write(b'ld\x891')  # 0x6c648931
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_max_speed_water))

        data.write(b'KB\xf5\xa9')  # 0x4b42f5a9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_max_speed_lava))

        data.write(b'\x1fL\xc8T')  # 0x1f4cc854
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_max_speed_phazon))

        data.write(b'\xb3@\x81s')  # 0xb3408173
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_max_speed_shrubbery))

        data.write(b'\x85\xeeQ\xed')  # 0x85ee51ed
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x85ee51ed))

        data.write(b'mx\x11\xf5')  # 0x6d7811f5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6d7811f5))

        data.write(b'\xf8\n\x06U')  # 0xf80a0655
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_up_gravity))

        data.write(b'\x92\xf3\x0f\x94')  # 0x92f30f94
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_down_gravity))

        data.write(b'\xb0j\xc9p')  # 0xb06ac970
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_forward_braking_accel_normal))

        data.write(b'\xbb<&)')  # 0xbb3c2629
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_forward_braking_accel_air))

        data.write(b'\xd2zP\xf1')  # 0xd27a50f1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_forward_braking_accel_ice))

        data.write(b'`R\x02"')  # 0x60520222
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_forward_braking_accel_organic))

        data.write(b'\r\xff\x9b\x92')  # 0xdff9b92
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_forward_braking_accel_water))

        data.write(b'\xbb\xaf\x85w')  # 0xbbaf8577
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_forward_braking_accel_lava))

        data.write(b'P\xf2\xa1\x14')  # 0x50f2a114
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_forward_braking_accel_phazon))

        data.write(b'[<B\x99')  # 0x5b3c4299
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_forward_braking_accel_shrubbery))

        data.write(b'\xd8>^\xec')  # 0xd83e5eec
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_gravity))

        data.write(b'\x9c\x90WG')  # 0x9c905747
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_water_gravity))

        data.write(b'\xee\xb7Ih')  # 0xeeb74968
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xeeb74968))

        data.write(b'\xbd(\xafn')  # 0xbd28af6e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ball_boost_height))

        data.write(b'\xe2\xbb\x02\x98')  # 0xe2bb0298
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe2bb0298))

        data.write(b'\xe4o\xa9j')  # 0xe46fa96a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.minimum_alignment_speed))

        data.write(b'N\xd8~\xbd')  # 0x4ed87ebd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.tireness))

        data.write(b'\xca\x8e\xde\xab')  # 0xca8edeab
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_lean_angle))

        data.write(b'\x96"m\x18')  # 0x96226d18
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.tire_to_marble_threshold_speed))

        data.write(b'\x19\x1fOb')  # 0x191f4f62
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.marble_to_tire_threshold_speed))

        data.write(b'T\xc2\x02\x11')  # 0x54c20211
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.force_to_lean_gain))

        data.write(b'\xb9\nr\x1e')  # 0xb90a721e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.lean_tracking_gain))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakBall_MovementJson", data)
        return cls(
            forward_accel_normal=json_data['forward_accel_normal'],
            forward_accel_air=json_data['forward_accel_air'],
            forward_accel_ice=json_data['forward_accel_ice'],
            forward_accel_organic=json_data['forward_accel_organic'],
            forward_accel_water=json_data['forward_accel_water'],
            forward_accel_lava=json_data['forward_accel_lava'],
            forward_accel_phazon=json_data['forward_accel_phazon'],
            forward_accel_shrubbery=json_data['forward_accel_shrubbery'],
            movement_friction_normal=json_data['movement_friction_normal'],
            movement_friction_air=json_data['movement_friction_air'],
            movement_friction_ice=json_data['movement_friction_ice'],
            movement_friction_organic=json_data['movement_friction_organic'],
            movement_friction_water=json_data['movement_friction_water'],
            movement_friction_lava=json_data['movement_friction_lava'],
            movement_friction_phazon=json_data['movement_friction_phazon'],
            movement_friction_shrubbery=json_data['movement_friction_shrubbery'],
            forward_max_speed_normal=json_data['forward_max_speed_normal'],
            forward_max_speed_air=json_data['forward_max_speed_air'],
            forward_max_speed_ice=json_data['forward_max_speed_ice'],
            forward_max_speed_organic=json_data['forward_max_speed_organic'],
            forward_max_speed_water=json_data['forward_max_speed_water'],
            forward_max_speed_lava=json_data['forward_max_speed_lava'],
            forward_max_speed_phazon=json_data['forward_max_speed_phazon'],
            forward_max_speed_shrubbery=json_data['forward_max_speed_shrubbery'],
            unknown_0x85ee51ed=json_data['unknown_0x85ee51ed'],
            unknown_0x6d7811f5=json_data['unknown_0x6d7811f5'],
            ball_up_gravity=json_data['ball_up_gravity'],
            ball_down_gravity=json_data['ball_down_gravity'],
            ball_forward_braking_accel_normal=json_data['ball_forward_braking_accel_normal'],
            ball_forward_braking_accel_air=json_data['ball_forward_braking_accel_air'],
            ball_forward_braking_accel_ice=json_data['ball_forward_braking_accel_ice'],
            ball_forward_braking_accel_organic=json_data['ball_forward_braking_accel_organic'],
            ball_forward_braking_accel_water=json_data['ball_forward_braking_accel_water'],
            ball_forward_braking_accel_lava=json_data['ball_forward_braking_accel_lava'],
            ball_forward_braking_accel_phazon=json_data['ball_forward_braking_accel_phazon'],
            ball_forward_braking_accel_shrubbery=json_data['ball_forward_braking_accel_shrubbery'],
            ball_gravity=json_data['ball_gravity'],
            ball_water_gravity=json_data['ball_water_gravity'],
            unknown_0xeeb74968=json_data['unknown_0xeeb74968'],
            ball_boost_height=json_data['ball_boost_height'],
            unknown_0xe2bb0298=json_data['unknown_0xe2bb0298'],
            minimum_alignment_speed=json_data['minimum_alignment_speed'],
            tireness=json_data['tireness'],
            max_lean_angle=json_data['max_lean_angle'],
            tire_to_marble_threshold_speed=json_data['tire_to_marble_threshold_speed'],
            marble_to_tire_threshold_speed=json_data['marble_to_tire_threshold_speed'],
            force_to_lean_gain=json_data['force_to_lean_gain'],
            lean_tracking_gain=json_data['lean_tracking_gain'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'forward_accel_normal': self.forward_accel_normal,
            'forward_accel_air': self.forward_accel_air,
            'forward_accel_ice': self.forward_accel_ice,
            'forward_accel_organic': self.forward_accel_organic,
            'forward_accel_water': self.forward_accel_water,
            'forward_accel_lava': self.forward_accel_lava,
            'forward_accel_phazon': self.forward_accel_phazon,
            'forward_accel_shrubbery': self.forward_accel_shrubbery,
            'movement_friction_normal': self.movement_friction_normal,
            'movement_friction_air': self.movement_friction_air,
            'movement_friction_ice': self.movement_friction_ice,
            'movement_friction_organic': self.movement_friction_organic,
            'movement_friction_water': self.movement_friction_water,
            'movement_friction_lava': self.movement_friction_lava,
            'movement_friction_phazon': self.movement_friction_phazon,
            'movement_friction_shrubbery': self.movement_friction_shrubbery,
            'forward_max_speed_normal': self.forward_max_speed_normal,
            'forward_max_speed_air': self.forward_max_speed_air,
            'forward_max_speed_ice': self.forward_max_speed_ice,
            'forward_max_speed_organic': self.forward_max_speed_organic,
            'forward_max_speed_water': self.forward_max_speed_water,
            'forward_max_speed_lava': self.forward_max_speed_lava,
            'forward_max_speed_phazon': self.forward_max_speed_phazon,
            'forward_max_speed_shrubbery': self.forward_max_speed_shrubbery,
            'unknown_0x85ee51ed': self.unknown_0x85ee51ed,
            'unknown_0x6d7811f5': self.unknown_0x6d7811f5,
            'ball_up_gravity': self.ball_up_gravity,
            'ball_down_gravity': self.ball_down_gravity,
            'ball_forward_braking_accel_normal': self.ball_forward_braking_accel_normal,
            'ball_forward_braking_accel_air': self.ball_forward_braking_accel_air,
            'ball_forward_braking_accel_ice': self.ball_forward_braking_accel_ice,
            'ball_forward_braking_accel_organic': self.ball_forward_braking_accel_organic,
            'ball_forward_braking_accel_water': self.ball_forward_braking_accel_water,
            'ball_forward_braking_accel_lava': self.ball_forward_braking_accel_lava,
            'ball_forward_braking_accel_phazon': self.ball_forward_braking_accel_phazon,
            'ball_forward_braking_accel_shrubbery': self.ball_forward_braking_accel_shrubbery,
            'ball_gravity': self.ball_gravity,
            'ball_water_gravity': self.ball_water_gravity,
            'unknown_0xeeb74968': self.unknown_0xeeb74968,
            'ball_boost_height': self.ball_boost_height,
            'unknown_0xe2bb0298': self.unknown_0xe2bb0298,
            'minimum_alignment_speed': self.minimum_alignment_speed,
            'tireness': self.tireness,
            'max_lean_angle': self.max_lean_angle,
            'tire_to_marble_threshold_speed': self.tire_to_marble_threshold_speed,
            'marble_to_tire_threshold_speed': self.marble_to_tire_threshold_speed,
            'force_to_lean_gain': self.force_to_lean_gain,
            'lean_tracking_gain': self.lean_tracking_gain,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_forward_accel_normal(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_accel_air(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_accel_ice(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_accel_organic(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_accel_water(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_accel_lava(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_accel_phazon(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_accel_shrubbery(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_movement_friction_normal(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_movement_friction_air(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_movement_friction_ice(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_movement_friction_organic(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_movement_friction_water(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_movement_friction_lava(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_movement_friction_phazon(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_movement_friction_shrubbery(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_max_speed_normal(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_max_speed_air(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_max_speed_ice(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_max_speed_organic(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_max_speed_water(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_max_speed_lava(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_max_speed_phazon(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_max_speed_shrubbery(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x85ee51ed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6d7811f5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_up_gravity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_down_gravity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_forward_braking_accel_normal(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_forward_braking_accel_air(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_forward_braking_accel_ice(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_forward_braking_accel_organic(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_forward_braking_accel_water(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_forward_braking_accel_lava(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_forward_braking_accel_phazon(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_forward_braking_accel_shrubbery(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_gravity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_water_gravity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xeeb74968(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ball_boost_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe2bb0298(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_minimum_alignment_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_tireness(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_lean_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_tire_to_marble_threshold_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_marble_to_tire_threshold_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_force_to_lean_gain(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_lean_tracking_gain(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x18d0b2da: ('forward_accel_normal', _decode_forward_accel_normal),
    0x84f61ac5: ('forward_accel_air', _decode_forward_accel_air),
    0xedb06c1d: ('forward_accel_ice', _decode_forward_accel_ice),
    0x56f9f2af: ('forward_accel_organic', _decode_forward_accel_organic),
    0xd05b643f: ('forward_accel_water', _decode_forward_accel_water),
    0x122ce118: ('forward_accel_lava', _decode_forward_accel_lava),
    0xf848dabe: ('forward_accel_phazon', _decode_forward_accel_phazon),
    0x68ac6028: ('forward_accel_shrubbery', _decode_forward_accel_shrubbery),
    0xd4a25028: ('movement_friction_normal', _decode_movement_friction_normal),
    0x2b5cb136: ('movement_friction_air', _decode_movement_friction_air),
    0x421ac7ee: ('movement_friction_ice', _decode_movement_friction_ice),
    0x586137d: ('movement_friction_organic', _decode_movement_friction_organic),
    0xaece038b: ('movement_friction_water', _decode_movement_friction_water),
    0x3637e815: ('movement_friction_lava', _decode_movement_friction_lava),
    0x343a384c: ('movement_friction_phazon', _decode_movement_friction_phazon),
    0xcaf4624: ('movement_friction_shrubbery', _decode_movement_friction_shrubbery),
    0xffd4a030: ('forward_max_speed_normal', _decode_forward_max_speed_normal),
    0x59dfbcb9: ('forward_max_speed_air', _decode_forward_max_speed_air),
    0x3099ca61: ('forward_max_speed_ice', _decode_forward_max_speed_ice),
    0x16c1fddb: ('forward_max_speed_organic', _decode_forward_max_speed_organic),
    0x6c648931: ('forward_max_speed_water', _decode_forward_max_speed_water),
    0x4b42f5a9: ('forward_max_speed_lava', _decode_forward_max_speed_lava),
    0x1f4cc854: ('forward_max_speed_phazon', _decode_forward_max_speed_phazon),
    0xb3408173: ('forward_max_speed_shrubbery', _decode_forward_max_speed_shrubbery),
    0x85ee51ed: ('unknown_0x85ee51ed', _decode_unknown_0x85ee51ed),
    0x6d7811f5: ('unknown_0x6d7811f5', _decode_unknown_0x6d7811f5),
    0xf80a0655: ('ball_up_gravity', _decode_ball_up_gravity),
    0x92f30f94: ('ball_down_gravity', _decode_ball_down_gravity),
    0xb06ac970: ('ball_forward_braking_accel_normal', _decode_ball_forward_braking_accel_normal),
    0xbb3c2629: ('ball_forward_braking_accel_air', _decode_ball_forward_braking_accel_air),
    0xd27a50f1: ('ball_forward_braking_accel_ice', _decode_ball_forward_braking_accel_ice),
    0x60520222: ('ball_forward_braking_accel_organic', _decode_ball_forward_braking_accel_organic),
    0xdff9b92: ('ball_forward_braking_accel_water', _decode_ball_forward_braking_accel_water),
    0xbbaf8577: ('ball_forward_braking_accel_lava', _decode_ball_forward_braking_accel_lava),
    0x50f2a114: ('ball_forward_braking_accel_phazon', _decode_ball_forward_braking_accel_phazon),
    0x5b3c4299: ('ball_forward_braking_accel_shrubbery', _decode_ball_forward_braking_accel_shrubbery),
    0xd83e5eec: ('ball_gravity', _decode_ball_gravity),
    0x9c905747: ('ball_water_gravity', _decode_ball_water_gravity),
    0xeeb74968: ('unknown_0xeeb74968', _decode_unknown_0xeeb74968),
    0xbd28af6e: ('ball_boost_height', _decode_ball_boost_height),
    0xe2bb0298: ('unknown_0xe2bb0298', _decode_unknown_0xe2bb0298),
    0xe46fa96a: ('minimum_alignment_speed', _decode_minimum_alignment_speed),
    0x4ed87ebd: ('tireness', _decode_tireness),
    0xca8edeab: ('max_lean_angle', _decode_max_lean_angle),
    0x96226d18: ('tire_to_marble_threshold_speed', _decode_tire_to_marble_threshold_speed),
    0x191f4f62: ('marble_to_tire_threshold_speed', _decode_marble_to_tire_threshold_speed),
    0x54c20211: ('force_to_lean_gain', _decode_force_to_lean_gain),
    0xb90a721e: ('lean_tracking_gain', _decode_lean_tracking_gain),
}
