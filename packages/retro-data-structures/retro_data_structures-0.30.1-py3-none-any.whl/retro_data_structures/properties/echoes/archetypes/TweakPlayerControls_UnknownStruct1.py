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

    class TweakPlayerControls_UnknownStruct1Json(typing_extensions.TypedDict):
        forward: int
        backward: int
        turn_left: int
        turn_right: int
        strafe_left: int
        strafe_right: int
        look_left: int
        look_right: int
        look_up: int
        look_down: int
        jump: int
        jump2: int
        fire_beam: int
        fire_beam2: int
        auto_fire_beam: int
        charge_beam: int
        charge_beam2: int
        use_item: int
        aim_up: int
        aim_down: int
        cycle_beam_up: int
        cycle_beam_down: int
        cycle_item: int
        select_power_beam: int
        select_ice_beam: int
        select_wave_beam: int
        select_plasma_beam: int
        gun_toggle_holster: int
        orbit_close: int
        orbit_far: int
        orbit_object: int
        orbit_select: int
        orbit_confirm: int
        orbit_left: int
        orbit_right: int
        orbit_up: int
        orbit_down: int
        hold_look1: int
        hold_look2: int
        look_zoom_in: int
        look_zoom_out: int
        hold_aim: int
        map_circle_up: int
        map_circle_down: int
        map_circle_left: int
        map_circle_right: int
        map_move_forward: int
        map_move_back: int
        map_move_left: int
        map_move_right: int
        map_zoom_in: int
        map_zoom_out: int
        spider_ball: int
        chase_camera: int
        x_ray_visor: int
        thermo_visor: int
        enviro_visor: int
        no_visor: int
        visor_menu: int
        cycle_visor_up: int
        cycle_visor_down: int
        dark_visor_toggle: int
        crosshairs: int
        unknown_0x29293fb1: int
        use_shield: int
        scan_item: int
        inventory_screen: int
        map_screen: int
        options_screen: int
        log_screen: int
        unknown_0xbf218f4f: int
        unknown_0x05ef2422: int
        boost_ball: int
        morph_into_ball: int
        morph_from_ball: int
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xaf03e16c, 0xcfa71717, 0x91532a8c, 0x7acc58d, 0xacc575a2, 0xdb475e1d, 0xa900887a, 0x534ac106, 0xd723723, 0x5c46b025, 0xf836180a, 0xfe16f98d, 0xfd59aa9f, 0x7e76f1f4, 0x93dd818b, 0x258402ec, 0xb7a20cda, 0x5b9a9219, 0x82a717cd, 0xa7d5c15a, 0x33731936, 0xb72565ff, 0xc592ca02, 0x5228272c, 0x901ac820, 0x4ecea0c0, 0xa4f35804, 0x919d7de0, 0x5200b48b, 0x49c493a3, 0xeb38a36b, 0xc60f66d2, 0x1d97cc2b, 0xc449ae1d, 0x80f17cdb, 0xabc5a6aa, 0x310f9642, 0xc4923775, 0xf57a2de8, 0xba4fb516, 0x9f45c8db, 0x5344d2f7, 0x18c157d, 0xad1e8de5, 0x5858b5ba, 0xc8df5b8b, 0x8d86d7b5, 0xab429ebd, 0x31111d41, 0xe2d939b7, 0xb06d1b60, 0x26293e7c, 0x649b0835, 0x5b1e0e7c, 0xb35d2cca, 0x5a7e4dfc, 0x76faf77e, 0x9ba498f6, 0x2b9a4a7f, 0xd6fb0bf9, 0x8fe3abe, 0xc3f4f3ef, 0x53e56da8, 0x29293fb1, 0x2c06b91, 0xbaa185cf, 0x6cdd19a4, 0xe08f6c6f, 0x1230759b, 0x5b9b4285, 0xbf218f4f, 0x5ef2422, 0xced85a1b, 0x39cf6e72, 0x64003596)


@dataclasses.dataclass()
class TweakPlayerControls_UnknownStruct1(BaseProperty):
    forward: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0xaf03e16c, original_name='Forward'
        ),
    })
    backward: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0xcfa71717, original_name='Backward'
        ),
    })
    turn_left: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0x91532a8c, original_name='TurnLeft'
        ),
    })
    turn_right: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0x07acc58d, original_name='TurnRight'
        ),
    })
    strafe_left: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0xacc575a2, original_name='StrafeLeft'
        ),
    })
    strafe_right: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0xdb475e1d, original_name='StrafeRight'
        ),
    })
    look_left: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa900887a, original_name='LookLeft'
        ),
    })
    look_right: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0x534ac106, original_name='LookRight'
        ),
    })
    look_up: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0d723723, original_name='LookUp'
        ),
    })
    look_down: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5c46b025, original_name='LookDown'
        ),
    })
    jump: int = dataclasses.field(default=16, metadata={
        'reflection': FieldReflection[int](
            int, id=0xf836180a, original_name='Jump'
        ),
    })
    jump2: int = dataclasses.field(default=16, metadata={
        'reflection': FieldReflection[int](
            int, id=0xfe16f98d, original_name='Jump2'
        ),
    })
    fire_beam: int = dataclasses.field(default=15, metadata={
        'reflection': FieldReflection[int](
            int, id=0xfd59aa9f, original_name='FireBeam'
        ),
    })
    fire_beam2: int = dataclasses.field(default=15, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7e76f1f4, original_name='FireBeam2'
        ),
    })
    auto_fire_beam: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x93dd818b, original_name='AutoFireBeam'
        ),
    })
    charge_beam: int = dataclasses.field(default=15, metadata={
        'reflection': FieldReflection[int](
            int, id=0x258402ec, original_name='ChargeBeam'
        ),
    })
    charge_beam2: int = dataclasses.field(default=15, metadata={
        'reflection': FieldReflection[int](
            int, id=0xb7a20cda, original_name='ChargeBeam2'
        ),
    })
    use_item: int = dataclasses.field(default=18, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5b9a9219, original_name='UseItem'
        ),
    })
    aim_up: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x82a717cd, original_name='AimUp'
        ),
    })
    aim_down: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa7d5c15a, original_name='AimDown'
        ),
    })
    cycle_beam_up: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x33731936, original_name='CycleBeamUp'
        ),
    })
    cycle_beam_down: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xb72565ff, original_name='CycleBeamDown'
        ),
    })
    cycle_item: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc592ca02, original_name='CycleItem'
        ),
    })
    select_power_beam: int = dataclasses.field(default=11, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5228272c, original_name='SelectPowerBeam'
        ),
    })
    select_ice_beam: int = dataclasses.field(default=12, metadata={
        'reflection': FieldReflection[int](
            int, id=0x901ac820, original_name='SelectIceBeam'
        ),
    })
    select_wave_beam: int = dataclasses.field(default=14, metadata={
        'reflection': FieldReflection[int](
            int, id=0x4ecea0c0, original_name='SelectWaveBeam'
        ),
    })
    select_plasma_beam: int = dataclasses.field(default=13, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa4f35804, original_name='SelectPlasmaBeam'
        ),
    })
    gun_toggle_holster: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x919d7de0, original_name='GunToggleHolster'
        ),
    })
    orbit_close: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5200b48b, original_name='OrbitClose'
        ),
    })
    orbit_far: int = dataclasses.field(default=9, metadata={
        'reflection': FieldReflection[int](
            int, id=0x49c493a3, original_name='OrbitFar'
        ),
    })
    orbit_object: int = dataclasses.field(default=20, metadata={
        'reflection': FieldReflection[int](
            int, id=0xeb38a36b, original_name='OrbitObject'
        ),
    })
    orbit_select: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc60f66d2, original_name='OrbitSelect'
        ),
    })
    orbit_confirm: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1d97cc2b, original_name='OrbitConfirm'
        ),
    })
    orbit_left: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc449ae1d, original_name='OrbitLeft'
        ),
    })
    orbit_right: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0x80f17cdb, original_name='OrbitRight'
        ),
    })
    orbit_up: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0xabc5a6aa, original_name='OrbitUp'
        ),
    })
    orbit_down: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0x310f9642, original_name='OrbitDown'
        ),
    })
    hold_look1: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc4923775, original_name='HoldLook1'
        ),
    })
    hold_look2: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xf57a2de8, original_name='HoldLook2'
        ),
    })
    look_zoom_in: int = dataclasses.field(default=17, metadata={
        'reflection': FieldReflection[int](
            int, id=0xba4fb516, original_name='LookZoomIn'
        ),
    })
    look_zoom_out: int = dataclasses.field(default=18, metadata={
        'reflection': FieldReflection[int](
            int, id=0x9f45c8db, original_name='LookZoomOut'
        ),
    })
    hold_aim: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5344d2f7, original_name='HoldAim'
        ),
    })
    map_circle_up: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0x018c157d, original_name='MapCircleUp'
        ),
    })
    map_circle_down: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0xad1e8de5, original_name='MapCircleDown'
        ),
    })
    map_circle_left: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5858b5ba, original_name='MapCircleLeft'
        ),
    })
    map_circle_right: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc8df5b8b, original_name='MapCircleRight'
        ),
    })
    map_move_forward: int = dataclasses.field(default=5, metadata={
        'reflection': FieldReflection[int](
            int, id=0x8d86d7b5, original_name='MapMoveForward'
        ),
    })
    map_move_back: int = dataclasses.field(default=6, metadata={
        'reflection': FieldReflection[int](
            int, id=0xab429ebd, original_name='MapMoveBack'
        ),
    })
    map_move_left: int = dataclasses.field(default=7, metadata={
        'reflection': FieldReflection[int](
            int, id=0x31111d41, original_name='MapMoveLeft'
        ),
    })
    map_move_right: int = dataclasses.field(default=8, metadata={
        'reflection': FieldReflection[int](
            int, id=0xe2d939b7, original_name='MapMoveRight'
        ),
    })
    map_zoom_in: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0xb06d1b60, original_name='MapZoomIn'
        ),
    })
    map_zoom_out: int = dataclasses.field(default=9, metadata={
        'reflection': FieldReflection[int](
            int, id=0x26293e7c, original_name='MapZoomOut'
        ),
    })
    spider_ball: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0x649b0835, original_name='SpiderBall'
        ),
    })
    chase_camera: int = dataclasses.field(default=9, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5b1e0e7c, original_name='ChaseCamera'
        ),
    })
    x_ray_visor: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xb35d2cca, original_name='XRayVisor'
        ),
    })
    thermo_visor: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5a7e4dfc, original_name='ThermoVisor'
        ),
    })
    enviro_visor: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x76faf77e, original_name='EnviroVisor'
        ),
    })
    no_visor: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x9ba498f6, original_name='NoVisor'
        ),
    })
    visor_menu: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x2b9a4a7f, original_name='VisorMenu'
        ),
    })
    cycle_visor_up: int = dataclasses.field(default=19, metadata={
        'reflection': FieldReflection[int](
            int, id=0xd6fb0bf9, original_name='CycleVisorUp'
        ),
    })
    cycle_visor_down: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x08fe3abe, original_name='CycleVisorDown'
        ),
    })
    dark_visor_toggle: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc3f4f3ef, original_name='DarkVisorToggle'
        ),
    })
    crosshairs: int = dataclasses.field(default=21, metadata={
        'reflection': FieldReflection[int](
            int, id=0x53e56da8, original_name='Crosshairs'
        ),
    })
    unknown_0x29293fb1: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x29293fb1, original_name='Unknown'
        ),
    })
    use_shield: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x02c06b91, original_name='UseShield'
        ),
    })
    scan_item: int = dataclasses.field(default=9, metadata={
        'reflection': FieldReflection[int](
            int, id=0xbaa185cf, original_name='ScanItem'
        ),
    })
    inventory_screen: int = dataclasses.field(default=13, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6cdd19a4, original_name='InventoryScreen'
        ),
    })
    map_screen: int = dataclasses.field(default=22, metadata={
        'reflection': FieldReflection[int](
            int, id=0xe08f6c6f, original_name='MapScreen'
        ),
    })
    options_screen: int = dataclasses.field(default=12, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1230759b, original_name='OptionsScreen'
        ),
    })
    log_screen: int = dataclasses.field(default=14, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5b9b4285, original_name='LogScreen'
        ),
    })
    unknown_0xbf218f4f: int = dataclasses.field(default=9, metadata={
        'reflection': FieldReflection[int](
            int, id=0xbf218f4f, original_name='Unknown'
        ),
    })
    unknown_0x05ef2422: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0x05ef2422, original_name='Unknown'
        ),
    })
    boost_ball: int = dataclasses.field(default=16, metadata={
        'reflection': FieldReflection[int](
            int, id=0xced85a1b, original_name='BoostBall'
        ),
    })
    morph_into_ball: int = dataclasses.field(default=17, metadata={
        'reflection': FieldReflection[int](
            int, id=0x39cf6e72, original_name='MorphIntoBall'
        ),
    })
    morph_from_ball: int = dataclasses.field(default=17, metadata={
        'reflection': FieldReflection[int](
            int, id=0x64003596, original_name='MorphFromBall'
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
        if property_count != 75:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHlLHl')
    
        dec = _FAST_FORMAT.unpack(data.read(750))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27], dec[30], dec[33], dec[36], dec[39], dec[42], dec[45], dec[48], dec[51], dec[54], dec[57], dec[60], dec[63], dec[66], dec[69], dec[72], dec[75], dec[78], dec[81], dec[84], dec[87], dec[90], dec[93], dec[96], dec[99], dec[102], dec[105], dec[108], dec[111], dec[114], dec[117], dec[120], dec[123], dec[126], dec[129], dec[132], dec[135], dec[138], dec[141], dec[144], dec[147], dec[150], dec[153], dec[156], dec[159], dec[162], dec[165], dec[168], dec[171], dec[174], dec[177], dec[180], dec[183], dec[186], dec[189], dec[192], dec[195], dec[198], dec[201], dec[204], dec[207], dec[210], dec[213], dec[216], dec[219], dec[222]) == _FAST_IDS
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
            dec[152],
            dec[155],
            dec[158],
            dec[161],
            dec[164],
            dec[167],
            dec[170],
            dec[173],
            dec[176],
            dec[179],
            dec[182],
            dec[185],
            dec[188],
            dec[191],
            dec[194],
            dec[197],
            dec[200],
            dec[203],
            dec[206],
            dec[209],
            dec[212],
            dec[215],
            dec[218],
            dec[221],
            dec[224],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00K')  # 75 properties

        data.write(b'\xaf\x03\xe1l')  # 0xaf03e16c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.forward))

        data.write(b'\xcf\xa7\x17\x17')  # 0xcfa71717
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.backward))

        data.write(b'\x91S*\x8c')  # 0x91532a8c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.turn_left))

        data.write(b'\x07\xac\xc5\x8d')  # 0x7acc58d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.turn_right))

        data.write(b'\xac\xc5u\xa2')  # 0xacc575a2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.strafe_left))

        data.write(b'\xdbG^\x1d')  # 0xdb475e1d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.strafe_right))

        data.write(b'\xa9\x00\x88z')  # 0xa900887a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.look_left))

        data.write(b'SJ\xc1\x06')  # 0x534ac106
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.look_right))

        data.write(b'\rr7#')  # 0xd723723
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.look_up))

        data.write(b'\\F\xb0%')  # 0x5c46b025
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.look_down))

        data.write(b'\xf86\x18\n')  # 0xf836180a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.jump))

        data.write(b'\xfe\x16\xf9\x8d')  # 0xfe16f98d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.jump2))

        data.write(b'\xfdY\xaa\x9f')  # 0xfd59aa9f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.fire_beam))

        data.write(b'~v\xf1\xf4')  # 0x7e76f1f4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.fire_beam2))

        data.write(b'\x93\xdd\x81\x8b')  # 0x93dd818b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.auto_fire_beam))

        data.write(b'%\x84\x02\xec')  # 0x258402ec
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.charge_beam))

        data.write(b'\xb7\xa2\x0c\xda')  # 0xb7a20cda
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.charge_beam2))

        data.write(b'[\x9a\x92\x19')  # 0x5b9a9219
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.use_item))

        data.write(b'\x82\xa7\x17\xcd')  # 0x82a717cd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.aim_up))

        data.write(b'\xa7\xd5\xc1Z')  # 0xa7d5c15a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.aim_down))

        data.write(b'3s\x196')  # 0x33731936
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.cycle_beam_up))

        data.write(b'\xb7%e\xff')  # 0xb72565ff
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.cycle_beam_down))

        data.write(b'\xc5\x92\xca\x02')  # 0xc592ca02
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.cycle_item))

        data.write(b"R(',")  # 0x5228272c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.select_power_beam))

        data.write(b'\x90\x1a\xc8 ')  # 0x901ac820
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.select_ice_beam))

        data.write(b'N\xce\xa0\xc0')  # 0x4ecea0c0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.select_wave_beam))

        data.write(b'\xa4\xf3X\x04')  # 0xa4f35804
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.select_plasma_beam))

        data.write(b'\x91\x9d}\xe0')  # 0x919d7de0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.gun_toggle_holster))

        data.write(b'R\x00\xb4\x8b')  # 0x5200b48b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_close))

        data.write(b'I\xc4\x93\xa3')  # 0x49c493a3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_far))

        data.write(b'\xeb8\xa3k')  # 0xeb38a36b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_object))

        data.write(b'\xc6\x0ff\xd2')  # 0xc60f66d2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_select))

        data.write(b'\x1d\x97\xcc+')  # 0x1d97cc2b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_confirm))

        data.write(b'\xc4I\xae\x1d')  # 0xc449ae1d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_left))

        data.write(b'\x80\xf1|\xdb')  # 0x80f17cdb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_right))

        data.write(b'\xab\xc5\xa6\xaa')  # 0xabc5a6aa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_up))

        data.write(b'1\x0f\x96B')  # 0x310f9642
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.orbit_down))

        data.write(b'\xc4\x927u')  # 0xc4923775
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.hold_look1))

        data.write(b'\xf5z-\xe8')  # 0xf57a2de8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.hold_look2))

        data.write(b'\xbaO\xb5\x16')  # 0xba4fb516
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.look_zoom_in))

        data.write(b'\x9fE\xc8\xdb')  # 0x9f45c8db
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.look_zoom_out))

        data.write(b'SD\xd2\xf7')  # 0x5344d2f7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.hold_aim))

        data.write(b'\x01\x8c\x15}')  # 0x18c157d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.map_circle_up))

        data.write(b'\xad\x1e\x8d\xe5')  # 0xad1e8de5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.map_circle_down))

        data.write(b'XX\xb5\xba')  # 0x5858b5ba
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.map_circle_left))

        data.write(b'\xc8\xdf[\x8b')  # 0xc8df5b8b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.map_circle_right))

        data.write(b'\x8d\x86\xd7\xb5')  # 0x8d86d7b5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.map_move_forward))

        data.write(b'\xabB\x9e\xbd')  # 0xab429ebd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.map_move_back))

        data.write(b'1\x11\x1dA')  # 0x31111d41
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.map_move_left))

        data.write(b'\xe2\xd99\xb7')  # 0xe2d939b7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.map_move_right))

        data.write(b'\xb0m\x1b`')  # 0xb06d1b60
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.map_zoom_in))

        data.write(b'&)>|')  # 0x26293e7c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.map_zoom_out))

        data.write(b'd\x9b\x085')  # 0x649b0835
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.spider_ball))

        data.write(b'[\x1e\x0e|')  # 0x5b1e0e7c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.chase_camera))

        data.write(b'\xb3],\xca')  # 0xb35d2cca
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.x_ray_visor))

        data.write(b'Z~M\xfc')  # 0x5a7e4dfc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.thermo_visor))

        data.write(b'v\xfa\xf7~')  # 0x76faf77e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.enviro_visor))

        data.write(b'\x9b\xa4\x98\xf6')  # 0x9ba498f6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.no_visor))

        data.write(b'+\x9aJ\x7f')  # 0x2b9a4a7f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.visor_menu))

        data.write(b'\xd6\xfb\x0b\xf9')  # 0xd6fb0bf9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.cycle_visor_up))

        data.write(b'\x08\xfe:\xbe')  # 0x8fe3abe
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.cycle_visor_down))

        data.write(b'\xc3\xf4\xf3\xef')  # 0xc3f4f3ef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.dark_visor_toggle))

        data.write(b'S\xe5m\xa8')  # 0x53e56da8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.crosshairs))

        data.write(b'))?\xb1')  # 0x29293fb1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x29293fb1))

        data.write(b'\x02\xc0k\x91')  # 0x2c06b91
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.use_shield))

        data.write(b'\xba\xa1\x85\xcf')  # 0xbaa185cf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.scan_item))

        data.write(b'l\xdd\x19\xa4')  # 0x6cdd19a4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.inventory_screen))

        data.write(b'\xe0\x8flo')  # 0xe08f6c6f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.map_screen))

        data.write(b'\x120u\x9b')  # 0x1230759b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.options_screen))

        data.write(b'[\x9bB\x85')  # 0x5b9b4285
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.log_screen))

        data.write(b'\xbf!\x8fO')  # 0xbf218f4f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xbf218f4f))

        data.write(b'\x05\xef$"')  # 0x5ef2422
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x05ef2422))

        data.write(b'\xce\xd8Z\x1b')  # 0xced85a1b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.boost_ball))

        data.write(b'9\xcfnr')  # 0x39cf6e72
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.morph_into_ball))

        data.write(b'd\x005\x96')  # 0x64003596
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.morph_from_ball))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayerControls_UnknownStruct1Json", data)
        return cls(
            forward=json_data['forward'],
            backward=json_data['backward'],
            turn_left=json_data['turn_left'],
            turn_right=json_data['turn_right'],
            strafe_left=json_data['strafe_left'],
            strafe_right=json_data['strafe_right'],
            look_left=json_data['look_left'],
            look_right=json_data['look_right'],
            look_up=json_data['look_up'],
            look_down=json_data['look_down'],
            jump=json_data['jump'],
            jump2=json_data['jump2'],
            fire_beam=json_data['fire_beam'],
            fire_beam2=json_data['fire_beam2'],
            auto_fire_beam=json_data['auto_fire_beam'],
            charge_beam=json_data['charge_beam'],
            charge_beam2=json_data['charge_beam2'],
            use_item=json_data['use_item'],
            aim_up=json_data['aim_up'],
            aim_down=json_data['aim_down'],
            cycle_beam_up=json_data['cycle_beam_up'],
            cycle_beam_down=json_data['cycle_beam_down'],
            cycle_item=json_data['cycle_item'],
            select_power_beam=json_data['select_power_beam'],
            select_ice_beam=json_data['select_ice_beam'],
            select_wave_beam=json_data['select_wave_beam'],
            select_plasma_beam=json_data['select_plasma_beam'],
            gun_toggle_holster=json_data['gun_toggle_holster'],
            orbit_close=json_data['orbit_close'],
            orbit_far=json_data['orbit_far'],
            orbit_object=json_data['orbit_object'],
            orbit_select=json_data['orbit_select'],
            orbit_confirm=json_data['orbit_confirm'],
            orbit_left=json_data['orbit_left'],
            orbit_right=json_data['orbit_right'],
            orbit_up=json_data['orbit_up'],
            orbit_down=json_data['orbit_down'],
            hold_look1=json_data['hold_look1'],
            hold_look2=json_data['hold_look2'],
            look_zoom_in=json_data['look_zoom_in'],
            look_zoom_out=json_data['look_zoom_out'],
            hold_aim=json_data['hold_aim'],
            map_circle_up=json_data['map_circle_up'],
            map_circle_down=json_data['map_circle_down'],
            map_circle_left=json_data['map_circle_left'],
            map_circle_right=json_data['map_circle_right'],
            map_move_forward=json_data['map_move_forward'],
            map_move_back=json_data['map_move_back'],
            map_move_left=json_data['map_move_left'],
            map_move_right=json_data['map_move_right'],
            map_zoom_in=json_data['map_zoom_in'],
            map_zoom_out=json_data['map_zoom_out'],
            spider_ball=json_data['spider_ball'],
            chase_camera=json_data['chase_camera'],
            x_ray_visor=json_data['x_ray_visor'],
            thermo_visor=json_data['thermo_visor'],
            enviro_visor=json_data['enviro_visor'],
            no_visor=json_data['no_visor'],
            visor_menu=json_data['visor_menu'],
            cycle_visor_up=json_data['cycle_visor_up'],
            cycle_visor_down=json_data['cycle_visor_down'],
            dark_visor_toggle=json_data['dark_visor_toggle'],
            crosshairs=json_data['crosshairs'],
            unknown_0x29293fb1=json_data['unknown_0x29293fb1'],
            use_shield=json_data['use_shield'],
            scan_item=json_data['scan_item'],
            inventory_screen=json_data['inventory_screen'],
            map_screen=json_data['map_screen'],
            options_screen=json_data['options_screen'],
            log_screen=json_data['log_screen'],
            unknown_0xbf218f4f=json_data['unknown_0xbf218f4f'],
            unknown_0x05ef2422=json_data['unknown_0x05ef2422'],
            boost_ball=json_data['boost_ball'],
            morph_into_ball=json_data['morph_into_ball'],
            morph_from_ball=json_data['morph_from_ball'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'forward': self.forward,
            'backward': self.backward,
            'turn_left': self.turn_left,
            'turn_right': self.turn_right,
            'strafe_left': self.strafe_left,
            'strafe_right': self.strafe_right,
            'look_left': self.look_left,
            'look_right': self.look_right,
            'look_up': self.look_up,
            'look_down': self.look_down,
            'jump': self.jump,
            'jump2': self.jump2,
            'fire_beam': self.fire_beam,
            'fire_beam2': self.fire_beam2,
            'auto_fire_beam': self.auto_fire_beam,
            'charge_beam': self.charge_beam,
            'charge_beam2': self.charge_beam2,
            'use_item': self.use_item,
            'aim_up': self.aim_up,
            'aim_down': self.aim_down,
            'cycle_beam_up': self.cycle_beam_up,
            'cycle_beam_down': self.cycle_beam_down,
            'cycle_item': self.cycle_item,
            'select_power_beam': self.select_power_beam,
            'select_ice_beam': self.select_ice_beam,
            'select_wave_beam': self.select_wave_beam,
            'select_plasma_beam': self.select_plasma_beam,
            'gun_toggle_holster': self.gun_toggle_holster,
            'orbit_close': self.orbit_close,
            'orbit_far': self.orbit_far,
            'orbit_object': self.orbit_object,
            'orbit_select': self.orbit_select,
            'orbit_confirm': self.orbit_confirm,
            'orbit_left': self.orbit_left,
            'orbit_right': self.orbit_right,
            'orbit_up': self.orbit_up,
            'orbit_down': self.orbit_down,
            'hold_look1': self.hold_look1,
            'hold_look2': self.hold_look2,
            'look_zoom_in': self.look_zoom_in,
            'look_zoom_out': self.look_zoom_out,
            'hold_aim': self.hold_aim,
            'map_circle_up': self.map_circle_up,
            'map_circle_down': self.map_circle_down,
            'map_circle_left': self.map_circle_left,
            'map_circle_right': self.map_circle_right,
            'map_move_forward': self.map_move_forward,
            'map_move_back': self.map_move_back,
            'map_move_left': self.map_move_left,
            'map_move_right': self.map_move_right,
            'map_zoom_in': self.map_zoom_in,
            'map_zoom_out': self.map_zoom_out,
            'spider_ball': self.spider_ball,
            'chase_camera': self.chase_camera,
            'x_ray_visor': self.x_ray_visor,
            'thermo_visor': self.thermo_visor,
            'enviro_visor': self.enviro_visor,
            'no_visor': self.no_visor,
            'visor_menu': self.visor_menu,
            'cycle_visor_up': self.cycle_visor_up,
            'cycle_visor_down': self.cycle_visor_down,
            'dark_visor_toggle': self.dark_visor_toggle,
            'crosshairs': self.crosshairs,
            'unknown_0x29293fb1': self.unknown_0x29293fb1,
            'use_shield': self.use_shield,
            'scan_item': self.scan_item,
            'inventory_screen': self.inventory_screen,
            'map_screen': self.map_screen,
            'options_screen': self.options_screen,
            'log_screen': self.log_screen,
            'unknown_0xbf218f4f': self.unknown_0xbf218f4f,
            'unknown_0x05ef2422': self.unknown_0x05ef2422,
            'boost_ball': self.boost_ball,
            'morph_into_ball': self.morph_into_ball,
            'morph_from_ball': self.morph_from_ball,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_forward(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_backward(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_turn_left(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_turn_right(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_strafe_left(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_strafe_right(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_look_left(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_look_right(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_look_up(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_look_down(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_jump(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_jump2(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_fire_beam(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_fire_beam2(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_auto_fire_beam(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_charge_beam(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_charge_beam2(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_use_item(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_aim_up(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_aim_down(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_cycle_beam_up(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_cycle_beam_down(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_cycle_item(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_select_power_beam(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_select_ice_beam(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_select_wave_beam(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_select_plasma_beam(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_gun_toggle_holster(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_close(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_far(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_object(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_select(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_confirm(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_left(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_right(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_up(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_orbit_down(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_hold_look1(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_hold_look2(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_look_zoom_in(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_look_zoom_out(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_hold_aim(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_map_circle_up(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_map_circle_down(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_map_circle_left(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_map_circle_right(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_map_move_forward(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_map_move_back(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_map_move_left(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_map_move_right(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_map_zoom_in(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_map_zoom_out(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_spider_ball(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_chase_camera(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_x_ray_visor(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_thermo_visor(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_enviro_visor(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_no_visor(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_visor_menu(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_cycle_visor_up(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_cycle_visor_down(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_dark_visor_toggle(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_crosshairs(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x29293fb1(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_use_shield(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_scan_item(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_inventory_screen(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_map_screen(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_options_screen(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_log_screen(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xbf218f4f(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x05ef2422(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_boost_ball(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_morph_into_ball(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_morph_from_ball(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xaf03e16c: ('forward', _decode_forward),
    0xcfa71717: ('backward', _decode_backward),
    0x91532a8c: ('turn_left', _decode_turn_left),
    0x7acc58d: ('turn_right', _decode_turn_right),
    0xacc575a2: ('strafe_left', _decode_strafe_left),
    0xdb475e1d: ('strafe_right', _decode_strafe_right),
    0xa900887a: ('look_left', _decode_look_left),
    0x534ac106: ('look_right', _decode_look_right),
    0xd723723: ('look_up', _decode_look_up),
    0x5c46b025: ('look_down', _decode_look_down),
    0xf836180a: ('jump', _decode_jump),
    0xfe16f98d: ('jump2', _decode_jump2),
    0xfd59aa9f: ('fire_beam', _decode_fire_beam),
    0x7e76f1f4: ('fire_beam2', _decode_fire_beam2),
    0x93dd818b: ('auto_fire_beam', _decode_auto_fire_beam),
    0x258402ec: ('charge_beam', _decode_charge_beam),
    0xb7a20cda: ('charge_beam2', _decode_charge_beam2),
    0x5b9a9219: ('use_item', _decode_use_item),
    0x82a717cd: ('aim_up', _decode_aim_up),
    0xa7d5c15a: ('aim_down', _decode_aim_down),
    0x33731936: ('cycle_beam_up', _decode_cycle_beam_up),
    0xb72565ff: ('cycle_beam_down', _decode_cycle_beam_down),
    0xc592ca02: ('cycle_item', _decode_cycle_item),
    0x5228272c: ('select_power_beam', _decode_select_power_beam),
    0x901ac820: ('select_ice_beam', _decode_select_ice_beam),
    0x4ecea0c0: ('select_wave_beam', _decode_select_wave_beam),
    0xa4f35804: ('select_plasma_beam', _decode_select_plasma_beam),
    0x919d7de0: ('gun_toggle_holster', _decode_gun_toggle_holster),
    0x5200b48b: ('orbit_close', _decode_orbit_close),
    0x49c493a3: ('orbit_far', _decode_orbit_far),
    0xeb38a36b: ('orbit_object', _decode_orbit_object),
    0xc60f66d2: ('orbit_select', _decode_orbit_select),
    0x1d97cc2b: ('orbit_confirm', _decode_orbit_confirm),
    0xc449ae1d: ('orbit_left', _decode_orbit_left),
    0x80f17cdb: ('orbit_right', _decode_orbit_right),
    0xabc5a6aa: ('orbit_up', _decode_orbit_up),
    0x310f9642: ('orbit_down', _decode_orbit_down),
    0xc4923775: ('hold_look1', _decode_hold_look1),
    0xf57a2de8: ('hold_look2', _decode_hold_look2),
    0xba4fb516: ('look_zoom_in', _decode_look_zoom_in),
    0x9f45c8db: ('look_zoom_out', _decode_look_zoom_out),
    0x5344d2f7: ('hold_aim', _decode_hold_aim),
    0x18c157d: ('map_circle_up', _decode_map_circle_up),
    0xad1e8de5: ('map_circle_down', _decode_map_circle_down),
    0x5858b5ba: ('map_circle_left', _decode_map_circle_left),
    0xc8df5b8b: ('map_circle_right', _decode_map_circle_right),
    0x8d86d7b5: ('map_move_forward', _decode_map_move_forward),
    0xab429ebd: ('map_move_back', _decode_map_move_back),
    0x31111d41: ('map_move_left', _decode_map_move_left),
    0xe2d939b7: ('map_move_right', _decode_map_move_right),
    0xb06d1b60: ('map_zoom_in', _decode_map_zoom_in),
    0x26293e7c: ('map_zoom_out', _decode_map_zoom_out),
    0x649b0835: ('spider_ball', _decode_spider_ball),
    0x5b1e0e7c: ('chase_camera', _decode_chase_camera),
    0xb35d2cca: ('x_ray_visor', _decode_x_ray_visor),
    0x5a7e4dfc: ('thermo_visor', _decode_thermo_visor),
    0x76faf77e: ('enviro_visor', _decode_enviro_visor),
    0x9ba498f6: ('no_visor', _decode_no_visor),
    0x2b9a4a7f: ('visor_menu', _decode_visor_menu),
    0xd6fb0bf9: ('cycle_visor_up', _decode_cycle_visor_up),
    0x8fe3abe: ('cycle_visor_down', _decode_cycle_visor_down),
    0xc3f4f3ef: ('dark_visor_toggle', _decode_dark_visor_toggle),
    0x53e56da8: ('crosshairs', _decode_crosshairs),
    0x29293fb1: ('unknown_0x29293fb1', _decode_unknown_0x29293fb1),
    0x2c06b91: ('use_shield', _decode_use_shield),
    0xbaa185cf: ('scan_item', _decode_scan_item),
    0x6cdd19a4: ('inventory_screen', _decode_inventory_screen),
    0xe08f6c6f: ('map_screen', _decode_map_screen),
    0x1230759b: ('options_screen', _decode_options_screen),
    0x5b9b4285: ('log_screen', _decode_log_screen),
    0xbf218f4f: ('unknown_0xbf218f4f', _decode_unknown_0xbf218f4f),
    0x5ef2422: ('unknown_0x05ef2422', _decode_unknown_0x05ef2422),
    0xced85a1b: ('boost_ball', _decode_boost_ball),
    0x39cf6e72: ('morph_into_ball', _decode_morph_into_ball),
    0x64003596: ('morph_from_ball', _decode_morph_from_ball),
}
