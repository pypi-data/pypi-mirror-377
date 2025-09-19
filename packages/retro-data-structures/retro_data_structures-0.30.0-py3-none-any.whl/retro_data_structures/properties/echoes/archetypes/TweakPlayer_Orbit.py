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

    class TweakPlayer_OrbitJson(typing_extensions.TypedDict):
        orbit_close_min_distance: float
        orbit_close_normal_distance: float
        orbit_close_max_distance: float
        orbit_far_min_distance: float
        orbit_far_normal_distance: float
        orbit_far_max_distance: float
        orbit_carcass_min_distance: float
        orbit_carcass_normal_distance: float
        orbit_carcass_max_distance: float
        orbit_max_angular_change: float
        orbit_mode_timer: float
        orbit_camera_speed: float
        orbit_upper_angle: float
        orbit_lower_angle: float
        orbit_horiz_angle: float
        orbit_upper_camera_angle: float
        orbit_lower_camera_angle: float
        orbit_max_target_distance: float
        orbit_max_lock_distance: float
        unknown_0x55f7d145: float
        orbit_distance_threshold: float
        orbit_zone_width: int
        orbit_zone_height: int
        unknown_0x58ee9d03: int
        unknown_0xe052fa66: int
        unknown_0xc452b61e: int
        unknown_0x7ceed17b: int
        orbit_scan_zone_width: int
        orbit_scan_zone_height: int
        unknown_0xec529a5e: int
        unknown_0x54eefd3b: int
        unknown_0x73ebdce2: int
        unknown_0xcb57bb87: int
        orbit_box_width: float
        orbit_box_height: float
        orbit_min_camera_pitch_distance: float
        orbit_max_camera_pitch_distance: float
        unknown_0x478c15f9: float
        orbit_z_range: float
        orbit_selection_close_angle: float
        orbit_selection_max_angle: float
        unknown_0x90b71b2e: float
        orbit_prevention_time: float
        orbit_dash: bool
        orbit_dash_uses_tap: bool
        orbit_dash_tap_time: float
        orbit_dash_stick_threshold: float
        orbit_dash_double_jump_impulse: float
        unknown_0x75a00cfb: float
        unknown_0xc4775e5f: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x68738246, 0x991180ef, 0x398a391b, 0x495caff1, 0xd2fb0fed, 0x18a514ac, 0x31072813, 0xf0e68dab, 0x60fe934e, 0xa6332f81, 0x663a6f89, 0xe60bbbbb, 0x914977b4, 0xee0c7156, 0xc6960be2, 0x6f6dffdd, 0x48c63796, 0x598beb71, 0x30b2f98e, 0x55f7d145, 0xf034335c, 0x40ae584e, 0x111e9dec, 0x58ee9d03, 0xe052fa66, 0xc452b61e, 0x7ceed17b, 0x44989f30, 0xa6a7f710, 0xec529a5e, 0x54eefd3b, 0x73ebdce2, 0xcb57bb87, 0xd2a8cc1f, 0xd5cbcec1, 0x141ed3b9, 0x72fbb5cd, 0x478c15f9, 0x93b712ba, 0x7b4688ce, 0x2e0cf3cd, 0x90b71b2e, 0x775761c5, 0xfa255139, 0x8f80e39e, 0xd290d7b5, 0x2421b618, 0xb814530b, 0x75a00cfb, 0xc4775e5f)


@dataclasses.dataclass()
class TweakPlayer_Orbit(BaseProperty):
    orbit_close_min_distance: float = dataclasses.field(default=27.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x68738246, original_name='OrbitCloseMinDistance'
        ),
    })
    orbit_close_normal_distance: float = dataclasses.field(default=75.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x991180ef, original_name='OrbitCloseNormalDistance'
        ),
    })
    orbit_close_max_distance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x398a391b, original_name='OrbitCloseMaxDistance'
        ),
    })
    orbit_far_min_distance: float = dataclasses.field(default=27.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x495caff1, original_name='OrbitFarMinDistance'
        ),
    })
    orbit_far_normal_distance: float = dataclasses.field(default=75.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd2fb0fed, original_name='OrbitFarNormalDistance'
        ),
    })
    orbit_far_max_distance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x18a514ac, original_name='OrbitFarMaxDistance'
        ),
    })
    orbit_carcass_min_distance: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x31072813, original_name='OrbitCarcassMinDistance'
        ),
    })
    orbit_carcass_normal_distance: float = dataclasses.field(default=75.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf0e68dab, original_name='OrbitCarcassNormalDistance'
        ),
    })
    orbit_carcass_max_distance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x60fe934e, original_name='OrbitCarcassMaxDistance'
        ),
    })
    orbit_max_angular_change: float = dataclasses.field(default=360.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa6332f81, original_name='OrbitMaxAngularChange'
        ),
    })
    orbit_mode_timer: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x663a6f89, original_name='OrbitModeTimer'
        ),
    })
    orbit_camera_speed: float = dataclasses.field(default=360.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe60bbbbb, original_name='OrbitCameraSpeed'
        ),
    })
    orbit_upper_angle: float = dataclasses.field(default=70.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x914977b4, original_name='OrbitUpperAngle'
        ),
    })
    orbit_lower_angle: float = dataclasses.field(default=70.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xee0c7156, original_name='OrbitLowerAngle'
        ),
    })
    orbit_horiz_angle: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc6960be2, original_name='OrbitHorizAngle'
        ),
    })
    orbit_upper_camera_angle: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6f6dffdd, original_name='OrbitUpperCameraAngle'
        ),
    })
    orbit_lower_camera_angle: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x48c63796, original_name='OrbitLowerCameraAngle'
        ),
    })
    orbit_max_target_distance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x598beb71, original_name='OrbitMaxTargetDistance'
        ),
    })
    orbit_max_lock_distance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x30b2f98e, original_name='OrbitMaxLockDistance'
        ),
    })
    unknown_0x55f7d145: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x55f7d145, original_name='Unknown'
        ),
    })
    orbit_distance_threshold: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf034335c, original_name='OrbitDistanceThreshold'
        ),
    })
    orbit_zone_width: int = dataclasses.field(default=180, metadata={
        'reflection': FieldReflection[int](
            int, id=0x40ae584e, original_name='OrbitZoneWidth'
        ),
    })
    orbit_zone_height: int = dataclasses.field(default=180, metadata={
        'reflection': FieldReflection[int](
            int, id=0x111e9dec, original_name='OrbitZoneHeight'
        ),
    })
    unknown_0x58ee9d03: int = dataclasses.field(default=320, metadata={
        'reflection': FieldReflection[int](
            int, id=0x58ee9d03, original_name='Unknown'
        ),
    })
    unknown_0xe052fa66: int = dataclasses.field(default=224, metadata={
        'reflection': FieldReflection[int](
            int, id=0xe052fa66, original_name='Unknown'
        ),
    })
    unknown_0xc452b61e: int = dataclasses.field(default=320, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc452b61e, original_name='Unknown'
        ),
    })
    unknown_0x7ceed17b: int = dataclasses.field(default=224, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7ceed17b, original_name='Unknown'
        ),
    })
    orbit_scan_zone_width: int = dataclasses.field(default=126, metadata={
        'reflection': FieldReflection[int](
            int, id=0x44989f30, original_name='OrbitScanZoneWidth'
        ),
    })
    orbit_scan_zone_height: int = dataclasses.field(default=44, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa6a7f710, original_name='OrbitScanZoneHeight'
        ),
    })
    unknown_0xec529a5e: int = dataclasses.field(default=320, metadata={
        'reflection': FieldReflection[int](
            int, id=0xec529a5e, original_name='Unknown'
        ),
    })
    unknown_0x54eefd3b: int = dataclasses.field(default=224, metadata={
        'reflection': FieldReflection[int](
            int, id=0x54eefd3b, original_name='Unknown'
        ),
    })
    unknown_0x73ebdce2: int = dataclasses.field(default=320, metadata={
        'reflection': FieldReflection[int](
            int, id=0x73ebdce2, original_name='Unknown'
        ),
    })
    unknown_0xcb57bb87: int = dataclasses.field(default=224, metadata={
        'reflection': FieldReflection[int](
            int, id=0xcb57bb87, original_name='Unknown'
        ),
    })
    orbit_box_width: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd2a8cc1f, original_name='OrbitBoxWidth'
        ),
    })
    orbit_box_height: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd5cbcec1, original_name='OrbitBoxHeight'
        ),
    })
    orbit_min_camera_pitch_distance: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x141ed3b9, original_name='OrbitMinCameraPitchDistance'
        ),
    })
    orbit_max_camera_pitch_distance: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x72fbb5cd, original_name='OrbitMaxCameraPitchDistance'
        ),
    })
    unknown_0x478c15f9: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x478c15f9, original_name='Unknown'
        ),
    })
    orbit_z_range: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x93b712ba, original_name='OrbitZRange'
        ),
    })
    orbit_selection_close_angle: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7b4688ce, original_name='OrbitSelectionCloseAngle'
        ),
    })
    orbit_selection_max_angle: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2e0cf3cd, original_name='OrbitSelectionMaxAngle'
        ),
    })
    unknown_0x90b71b2e: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x90b71b2e, original_name='Unknown'
        ),
    })
    orbit_prevention_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x775761c5, original_name='OrbitPreventionTime'
        ),
    })
    orbit_dash: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xfa255139, original_name='OrbitDash'
        ),
    })
    orbit_dash_uses_tap: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x8f80e39e, original_name='OrbitDashUsesTap'
        ),
    })
    orbit_dash_tap_time: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd290d7b5, original_name='OrbitDashTapTime'
        ),
    })
    orbit_dash_stick_threshold: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2421b618, original_name='OrbitDashStickThreshold'
        ),
    })
    orbit_dash_double_jump_impulse: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb814530b, original_name='OrbitDashDoubleJumpImpulse'
        ),
    })
    unknown_0x75a00cfb: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x75a00cfb, original_name='Unknown'
        ),
    })
    unknown_0xc4775e5f: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc4775e5f, original_name='Unknown'
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
        if property_count != 50:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLH?LH?LHfLHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(494))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27], dec[30], dec[33], dec[36], dec[39], dec[42], dec[45], dec[48], dec[51], dec[54], dec[57], dec[60], dec[63], dec[66], dec[69], dec[72], dec[75], dec[78], dec[81], dec[84], dec[87], dec[90], dec[93], dec[96], dec[99], dec[102], dec[105], dec[108], dec[111], dec[114], dec[117], dec[120], dec[123], dec[126], dec[129], dec[132], dec[135], dec[138], dec[141], dec[144], dec[147]) == _FAST_IDS
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
            dec[146],
            dec[149],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x002')  # 50 properties

        data.write(b'hs\x82F')  # 0x68738246
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_close_min_distance))

        data.write(b'\x99\x11\x80\xef')  # 0x991180ef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_close_normal_distance))

        data.write(b'9\x8a9\x1b')  # 0x398a391b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_close_max_distance))

        data.write(b'I\\\xaf\xf1')  # 0x495caff1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_far_min_distance))

        data.write(b'\xd2\xfb\x0f\xed')  # 0xd2fb0fed
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_far_normal_distance))

        data.write(b'\x18\xa5\x14\xac')  # 0x18a514ac
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_far_max_distance))

        data.write(b'1\x07(\x13')  # 0x31072813
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_carcass_min_distance))

        data.write(b'\xf0\xe6\x8d\xab')  # 0xf0e68dab
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_carcass_normal_distance))

        data.write(b'`\xfe\x93N')  # 0x60fe934e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_carcass_max_distance))

        data.write(b'\xa63/\x81')  # 0xa6332f81
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_max_angular_change))

        data.write(b'f:o\x89')  # 0x663a6f89
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_mode_timer))

        data.write(b'\xe6\x0b\xbb\xbb')  # 0xe60bbbbb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_camera_speed))

        data.write(b'\x91Iw\xb4')  # 0x914977b4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_upper_angle))

        data.write(b'\xee\x0cqV')  # 0xee0c7156
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_lower_angle))

        data.write(b'\xc6\x96\x0b\xe2')  # 0xc6960be2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_horiz_angle))

        data.write(b'om\xff\xdd')  # 0x6f6dffdd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_upper_camera_angle))

        data.write(b'H\xc67\x96')  # 0x48c63796
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_lower_camera_angle))

        data.write(b'Y\x8b\xebq')  # 0x598beb71
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_max_target_distance))

        data.write(b'0\xb2\xf9\x8e')  # 0x30b2f98e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_max_lock_distance))

        data.write(b'U\xf7\xd1E')  # 0x55f7d145
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x55f7d145))

        data.write(b'\xf043\\')  # 0xf034335c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_distance_threshold))

        data.write(b'@\xaeXN')  # 0x40ae584e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_zone_width))

        data.write(b'\x11\x1e\x9d\xec')  # 0x111e9dec
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_zone_height))

        data.write(b'X\xee\x9d\x03')  # 0x58ee9d03
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x58ee9d03))

        data.write(b'\xe0R\xfaf')  # 0xe052fa66
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xe052fa66))

        data.write(b'\xc4R\xb6\x1e')  # 0xc452b61e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xc452b61e))

        data.write(b'|\xee\xd1{')  # 0x7ceed17b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x7ceed17b))

        data.write(b'D\x98\x9f0')  # 0x44989f30
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_scan_zone_width))

        data.write(b'\xa6\xa7\xf7\x10')  # 0xa6a7f710
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_scan_zone_height))

        data.write(b'\xecR\x9a^')  # 0xec529a5e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xec529a5e))

        data.write(b'T\xee\xfd;')  # 0x54eefd3b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x54eefd3b))

        data.write(b's\xeb\xdc\xe2')  # 0x73ebdce2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x73ebdce2))

        data.write(b'\xcbW\xbb\x87')  # 0xcb57bb87
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xcb57bb87))

        data.write(b'\xd2\xa8\xcc\x1f')  # 0xd2a8cc1f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_box_width))

        data.write(b'\xd5\xcb\xce\xc1')  # 0xd5cbcec1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_box_height))

        data.write(b'\x14\x1e\xd3\xb9')  # 0x141ed3b9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_min_camera_pitch_distance))

        data.write(b'r\xfb\xb5\xcd')  # 0x72fbb5cd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_max_camera_pitch_distance))

        data.write(b'G\x8c\x15\xf9')  # 0x478c15f9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x478c15f9))

        data.write(b'\x93\xb7\x12\xba')  # 0x93b712ba
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_z_range))

        data.write(b'{F\x88\xce')  # 0x7b4688ce
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_selection_close_angle))

        data.write(b'.\x0c\xf3\xcd')  # 0x2e0cf3cd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_selection_max_angle))

        data.write(b'\x90\xb7\x1b.')  # 0x90b71b2e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x90b71b2e))

        data.write(b'wWa\xc5')  # 0x775761c5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_prevention_time))

        data.write(b'\xfa%Q9')  # 0xfa255139
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.orbit_dash))

        data.write(b'\x8f\x80\xe3\x9e')  # 0x8f80e39e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.orbit_dash_uses_tap))

        data.write(b'\xd2\x90\xd7\xb5')  # 0xd290d7b5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_dash_tap_time))

        data.write(b'$!\xb6\x18')  # 0x2421b618
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_dash_stick_threshold))

        data.write(b'\xb8\x14S\x0b')  # 0xb814530b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.orbit_dash_double_jump_impulse))

        data.write(b'u\xa0\x0c\xfb')  # 0x75a00cfb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x75a00cfb))

        data.write(b'\xc4w^_')  # 0xc4775e5f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc4775e5f))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayer_OrbitJson", data)
        return cls(
            orbit_close_min_distance=json_data['orbit_close_min_distance'],
            orbit_close_normal_distance=json_data['orbit_close_normal_distance'],
            orbit_close_max_distance=json_data['orbit_close_max_distance'],
            orbit_far_min_distance=json_data['orbit_far_min_distance'],
            orbit_far_normal_distance=json_data['orbit_far_normal_distance'],
            orbit_far_max_distance=json_data['orbit_far_max_distance'],
            orbit_carcass_min_distance=json_data['orbit_carcass_min_distance'],
            orbit_carcass_normal_distance=json_data['orbit_carcass_normal_distance'],
            orbit_carcass_max_distance=json_data['orbit_carcass_max_distance'],
            orbit_max_angular_change=json_data['orbit_max_angular_change'],
            orbit_mode_timer=json_data['orbit_mode_timer'],
            orbit_camera_speed=json_data['orbit_camera_speed'],
            orbit_upper_angle=json_data['orbit_upper_angle'],
            orbit_lower_angle=json_data['orbit_lower_angle'],
            orbit_horiz_angle=json_data['orbit_horiz_angle'],
            orbit_upper_camera_angle=json_data['orbit_upper_camera_angle'],
            orbit_lower_camera_angle=json_data['orbit_lower_camera_angle'],
            orbit_max_target_distance=json_data['orbit_max_target_distance'],
            orbit_max_lock_distance=json_data['orbit_max_lock_distance'],
            unknown_0x55f7d145=json_data['unknown_0x55f7d145'],
            orbit_distance_threshold=json_data['orbit_distance_threshold'],
            orbit_zone_width=json_data['orbit_zone_width'],
            orbit_zone_height=json_data['orbit_zone_height'],
            unknown_0x58ee9d03=json_data['unknown_0x58ee9d03'],
            unknown_0xe052fa66=json_data['unknown_0xe052fa66'],
            unknown_0xc452b61e=json_data['unknown_0xc452b61e'],
            unknown_0x7ceed17b=json_data['unknown_0x7ceed17b'],
            orbit_scan_zone_width=json_data['orbit_scan_zone_width'],
            orbit_scan_zone_height=json_data['orbit_scan_zone_height'],
            unknown_0xec529a5e=json_data['unknown_0xec529a5e'],
            unknown_0x54eefd3b=json_data['unknown_0x54eefd3b'],
            unknown_0x73ebdce2=json_data['unknown_0x73ebdce2'],
            unknown_0xcb57bb87=json_data['unknown_0xcb57bb87'],
            orbit_box_width=json_data['orbit_box_width'],
            orbit_box_height=json_data['orbit_box_height'],
            orbit_min_camera_pitch_distance=json_data['orbit_min_camera_pitch_distance'],
            orbit_max_camera_pitch_distance=json_data['orbit_max_camera_pitch_distance'],
            unknown_0x478c15f9=json_data['unknown_0x478c15f9'],
            orbit_z_range=json_data['orbit_z_range'],
            orbit_selection_close_angle=json_data['orbit_selection_close_angle'],
            orbit_selection_max_angle=json_data['orbit_selection_max_angle'],
            unknown_0x90b71b2e=json_data['unknown_0x90b71b2e'],
            orbit_prevention_time=json_data['orbit_prevention_time'],
            orbit_dash=json_data['orbit_dash'],
            orbit_dash_uses_tap=json_data['orbit_dash_uses_tap'],
            orbit_dash_tap_time=json_data['orbit_dash_tap_time'],
            orbit_dash_stick_threshold=json_data['orbit_dash_stick_threshold'],
            orbit_dash_double_jump_impulse=json_data['orbit_dash_double_jump_impulse'],
            unknown_0x75a00cfb=json_data['unknown_0x75a00cfb'],
            unknown_0xc4775e5f=json_data['unknown_0xc4775e5f'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'orbit_close_min_distance': self.orbit_close_min_distance,
            'orbit_close_normal_distance': self.orbit_close_normal_distance,
            'orbit_close_max_distance': self.orbit_close_max_distance,
            'orbit_far_min_distance': self.orbit_far_min_distance,
            'orbit_far_normal_distance': self.orbit_far_normal_distance,
            'orbit_far_max_distance': self.orbit_far_max_distance,
            'orbit_carcass_min_distance': self.orbit_carcass_min_distance,
            'orbit_carcass_normal_distance': self.orbit_carcass_normal_distance,
            'orbit_carcass_max_distance': self.orbit_carcass_max_distance,
            'orbit_max_angular_change': self.orbit_max_angular_change,
            'orbit_mode_timer': self.orbit_mode_timer,
            'orbit_camera_speed': self.orbit_camera_speed,
            'orbit_upper_angle': self.orbit_upper_angle,
            'orbit_lower_angle': self.orbit_lower_angle,
            'orbit_horiz_angle': self.orbit_horiz_angle,
            'orbit_upper_camera_angle': self.orbit_upper_camera_angle,
            'orbit_lower_camera_angle': self.orbit_lower_camera_angle,
            'orbit_max_target_distance': self.orbit_max_target_distance,
            'orbit_max_lock_distance': self.orbit_max_lock_distance,
            'unknown_0x55f7d145': self.unknown_0x55f7d145,
            'orbit_distance_threshold': self.orbit_distance_threshold,
            'orbit_zone_width': self.orbit_zone_width,
            'orbit_zone_height': self.orbit_zone_height,
            'unknown_0x58ee9d03': self.unknown_0x58ee9d03,
            'unknown_0xe052fa66': self.unknown_0xe052fa66,
            'unknown_0xc452b61e': self.unknown_0xc452b61e,
            'unknown_0x7ceed17b': self.unknown_0x7ceed17b,
            'orbit_scan_zone_width': self.orbit_scan_zone_width,
            'orbit_scan_zone_height': self.orbit_scan_zone_height,
            'unknown_0xec529a5e': self.unknown_0xec529a5e,
            'unknown_0x54eefd3b': self.unknown_0x54eefd3b,
            'unknown_0x73ebdce2': self.unknown_0x73ebdce2,
            'unknown_0xcb57bb87': self.unknown_0xcb57bb87,
            'orbit_box_width': self.orbit_box_width,
            'orbit_box_height': self.orbit_box_height,
            'orbit_min_camera_pitch_distance': self.orbit_min_camera_pitch_distance,
            'orbit_max_camera_pitch_distance': self.orbit_max_camera_pitch_distance,
            'unknown_0x478c15f9': self.unknown_0x478c15f9,
            'orbit_z_range': self.orbit_z_range,
            'orbit_selection_close_angle': self.orbit_selection_close_angle,
            'orbit_selection_max_angle': self.orbit_selection_max_angle,
            'unknown_0x90b71b2e': self.unknown_0x90b71b2e,
            'orbit_prevention_time': self.orbit_prevention_time,
            'orbit_dash': self.orbit_dash,
            'orbit_dash_uses_tap': self.orbit_dash_uses_tap,
            'orbit_dash_tap_time': self.orbit_dash_tap_time,
            'orbit_dash_stick_threshold': self.orbit_dash_stick_threshold,
            'orbit_dash_double_jump_impulse': self.orbit_dash_double_jump_impulse,
            'unknown_0x75a00cfb': self.unknown_0x75a00cfb,
            'unknown_0xc4775e5f': self.unknown_0xc4775e5f,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_orbit_close_min_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_close_normal_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_close_max_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_far_min_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_far_normal_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_far_max_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_carcass_min_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_carcass_normal_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_carcass_max_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_max_angular_change(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_mode_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_camera_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_upper_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_lower_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_horiz_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_upper_camera_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_lower_camera_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_max_target_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_max_lock_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x55f7d145(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_distance_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_zone_width(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_zone_height(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x58ee9d03(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xe052fa66(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xc452b61e(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x7ceed17b(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_scan_zone_width(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_scan_zone_height(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xec529a5e(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x54eefd3b(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x73ebdce2(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xcb57bb87(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_box_width(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_box_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_min_camera_pitch_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_max_camera_pitch_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x478c15f9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_z_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_selection_close_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_selection_max_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x90b71b2e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_prevention_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_dash(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_orbit_dash_uses_tap(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_orbit_dash_tap_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_dash_stick_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_orbit_dash_double_jump_impulse(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x75a00cfb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc4775e5f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x68738246: ('orbit_close_min_distance', _decode_orbit_close_min_distance),
    0x991180ef: ('orbit_close_normal_distance', _decode_orbit_close_normal_distance),
    0x398a391b: ('orbit_close_max_distance', _decode_orbit_close_max_distance),
    0x495caff1: ('orbit_far_min_distance', _decode_orbit_far_min_distance),
    0xd2fb0fed: ('orbit_far_normal_distance', _decode_orbit_far_normal_distance),
    0x18a514ac: ('orbit_far_max_distance', _decode_orbit_far_max_distance),
    0x31072813: ('orbit_carcass_min_distance', _decode_orbit_carcass_min_distance),
    0xf0e68dab: ('orbit_carcass_normal_distance', _decode_orbit_carcass_normal_distance),
    0x60fe934e: ('orbit_carcass_max_distance', _decode_orbit_carcass_max_distance),
    0xa6332f81: ('orbit_max_angular_change', _decode_orbit_max_angular_change),
    0x663a6f89: ('orbit_mode_timer', _decode_orbit_mode_timer),
    0xe60bbbbb: ('orbit_camera_speed', _decode_orbit_camera_speed),
    0x914977b4: ('orbit_upper_angle', _decode_orbit_upper_angle),
    0xee0c7156: ('orbit_lower_angle', _decode_orbit_lower_angle),
    0xc6960be2: ('orbit_horiz_angle', _decode_orbit_horiz_angle),
    0x6f6dffdd: ('orbit_upper_camera_angle', _decode_orbit_upper_camera_angle),
    0x48c63796: ('orbit_lower_camera_angle', _decode_orbit_lower_camera_angle),
    0x598beb71: ('orbit_max_target_distance', _decode_orbit_max_target_distance),
    0x30b2f98e: ('orbit_max_lock_distance', _decode_orbit_max_lock_distance),
    0x55f7d145: ('unknown_0x55f7d145', _decode_unknown_0x55f7d145),
    0xf034335c: ('orbit_distance_threshold', _decode_orbit_distance_threshold),
    0x40ae584e: ('orbit_zone_width', _decode_orbit_zone_width),
    0x111e9dec: ('orbit_zone_height', _decode_orbit_zone_height),
    0x58ee9d03: ('unknown_0x58ee9d03', _decode_unknown_0x58ee9d03),
    0xe052fa66: ('unknown_0xe052fa66', _decode_unknown_0xe052fa66),
    0xc452b61e: ('unknown_0xc452b61e', _decode_unknown_0xc452b61e),
    0x7ceed17b: ('unknown_0x7ceed17b', _decode_unknown_0x7ceed17b),
    0x44989f30: ('orbit_scan_zone_width', _decode_orbit_scan_zone_width),
    0xa6a7f710: ('orbit_scan_zone_height', _decode_orbit_scan_zone_height),
    0xec529a5e: ('unknown_0xec529a5e', _decode_unknown_0xec529a5e),
    0x54eefd3b: ('unknown_0x54eefd3b', _decode_unknown_0x54eefd3b),
    0x73ebdce2: ('unknown_0x73ebdce2', _decode_unknown_0x73ebdce2),
    0xcb57bb87: ('unknown_0xcb57bb87', _decode_unknown_0xcb57bb87),
    0xd2a8cc1f: ('orbit_box_width', _decode_orbit_box_width),
    0xd5cbcec1: ('orbit_box_height', _decode_orbit_box_height),
    0x141ed3b9: ('orbit_min_camera_pitch_distance', _decode_orbit_min_camera_pitch_distance),
    0x72fbb5cd: ('orbit_max_camera_pitch_distance', _decode_orbit_max_camera_pitch_distance),
    0x478c15f9: ('unknown_0x478c15f9', _decode_unknown_0x478c15f9),
    0x93b712ba: ('orbit_z_range', _decode_orbit_z_range),
    0x7b4688ce: ('orbit_selection_close_angle', _decode_orbit_selection_close_angle),
    0x2e0cf3cd: ('orbit_selection_max_angle', _decode_orbit_selection_max_angle),
    0x90b71b2e: ('unknown_0x90b71b2e', _decode_unknown_0x90b71b2e),
    0x775761c5: ('orbit_prevention_time', _decode_orbit_prevention_time),
    0xfa255139: ('orbit_dash', _decode_orbit_dash),
    0x8f80e39e: ('orbit_dash_uses_tap', _decode_orbit_dash_uses_tap),
    0xd290d7b5: ('orbit_dash_tap_time', _decode_orbit_dash_tap_time),
    0x2421b618: ('orbit_dash_stick_threshold', _decode_orbit_dash_stick_threshold),
    0xb814530b: ('orbit_dash_double_jump_impulse', _decode_orbit_dash_double_jump_impulse),
    0x75a00cfb: ('unknown_0x75a00cfb', _decode_unknown_0x75a00cfb),
    0xc4775e5f: ('unknown_0xc4775e5f', _decode_unknown_0xc4775e5f),
}
