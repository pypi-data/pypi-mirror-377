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
from retro_data_structures.properties.echoes.archetypes.UnknownStruct16 import UnknownStruct16

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class UnknownStruct17Json(typing_extensions.TypedDict):
        unknown_0xb5af7831: float
        unknown_0xac65eb7a: float
        unknown_0x4f3855a0: float
        unknown_0x08c0b02c: float
        unknown_0x695f68c7: float
        unknown_0xd061ff99: float
        pause_duration_min: float
        pause_duration_max: float
        chance_to_double_dash: float
        unknown_struct16: json_util.JsonObject
        unknown_0x3ff87a8c: bool
        unknown_0x49b9936d: bool
        unknown_0xc96b8223: bool
        unknown_0x53fdcb5b: bool
        unknown_0x0d7ef013: bool
        unknown_0xaa85c885: bool
        pause: float
        taunt: float
        look_around: bool
        melee_attack: float
        melee_dash: float
        scatter_shot: float
        unknown_0x94f48974: float
        dive_attack: float
        unknown_0xb2c1e4fa: bool
        unknown_0xf5cf3c0f: bool
        normal_missile: float
        missile_jump: float
        super_missile: float
        unknown_0xe63286eb: float
        unknown_0x4aae6186: float
        sweep_beam: float
        boost_ball: float
        unknown_0x2d7551e6: bool
        phazon_attack: float
        phazon_enrage: float
        unknown_0x911a2476: bool
    

@dataclasses.dataclass()
class UnknownStruct17(BaseProperty):
    unknown_0xb5af7831: float = dataclasses.field(default=-1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb5af7831, original_name='Unknown'
        ),
    })
    unknown_0xac65eb7a: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xac65eb7a, original_name='Unknown'
        ),
    })
    unknown_0x4f3855a0: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4f3855a0, original_name='Unknown'
        ),
    })
    unknown_0x08c0b02c: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x08c0b02c, original_name='Unknown'
        ),
    })
    unknown_0x695f68c7: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x695f68c7, original_name='Unknown'
        ),
    })
    unknown_0xd061ff99: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd061ff99, original_name='Unknown'
        ),
    })
    pause_duration_min: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x97dbd42a, original_name='PauseDurationMin'
        ),
    })
    pause_duration_max: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x71bb7bcb, original_name='PauseDurationMax'
        ),
    })
    chance_to_double_dash: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb751778b, original_name='ChanceToDoubleDash'
        ),
    })
    unknown_struct16: UnknownStruct16 = dataclasses.field(default_factory=UnknownStruct16, metadata={
        'reflection': FieldReflection[UnknownStruct16](
            UnknownStruct16, id=0xd6740348, original_name='UnknownStruct16', from_json=UnknownStruct16.from_json, to_json=UnknownStruct16.to_json
        ),
    })
    unknown_0x3ff87a8c: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x3ff87a8c, original_name='Unknown'
        ),
    })
    unknown_0x49b9936d: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x49b9936d, original_name='Unknown'
        ),
    })
    unknown_0xc96b8223: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc96b8223, original_name='Unknown'
        ),
    })
    unknown_0x53fdcb5b: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x53fdcb5b, original_name='Unknown'
        ),
    })
    unknown_0x0d7ef013: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0d7ef013, original_name='Unknown'
        ),
    })
    unknown_0xaa85c885: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xaa85c885, original_name='Unknown'
        ),
    })
    pause: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x80f7e605, original_name='Pause'
        ),
    })
    taunt: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x479f6a4f, original_name='Taunt'
        ),
    })
    look_around: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x778791f5, original_name='LookAround'
        ),
    })
    melee_attack: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xce4c4668, original_name='MeleeAttack'
        ),
    })
    melee_dash: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5951a03f, original_name='MeleeDash'
        ),
    })
    scatter_shot: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x94615651, original_name='ScatterShot'
        ),
    })
    unknown_0x94f48974: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x94f48974, original_name='Unknown'
        ),
    })
    dive_attack: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6e40fb76, original_name='DiveAttack'
        ),
    })
    unknown_0xb2c1e4fa: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb2c1e4fa, original_name='Unknown'
        ),
    })
    unknown_0xf5cf3c0f: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf5cf3c0f, original_name='Unknown'
        ),
    })
    normal_missile: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6847efa7, original_name='NormalMissile'
        ),
    })
    missile_jump: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x083fd602, original_name='MissileJump'
        ),
    })
    super_missile: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdb21402f, original_name='SuperMissile'
        ),
    })
    unknown_0xe63286eb: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe63286eb, original_name='Unknown'
        ),
    })
    unknown_0x4aae6186: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4aae6186, original_name='Unknown'
        ),
    })
    sweep_beam: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2bd1c15b, original_name='SweepBeam'
        ),
    })
    boost_ball: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb53693fa, original_name='BoostBall'
        ),
    })
    unknown_0x2d7551e6: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2d7551e6, original_name='Unknown'
        ),
    })
    phazon_attack: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x93a876f3, original_name='PhazonAttack'
        ),
    })
    phazon_enrage: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xaea228b9, original_name='PhazonEnrage'
        ),
    })
    unknown_0x911a2476: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x911a2476, original_name='Unknown'
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
        if property_count != 37:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb5af7831
        unknown_0xb5af7831 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xac65eb7a
        unknown_0xac65eb7a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4f3855a0
        unknown_0x4f3855a0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x08c0b02c
        unknown_0x08c0b02c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x695f68c7
        unknown_0x695f68c7 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd061ff99
        unknown_0xd061ff99 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x97dbd42a
        pause_duration_min = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71bb7bcb
        pause_duration_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb751778b
        chance_to_double_dash = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd6740348
        unknown_struct16 = UnknownStruct16.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3ff87a8c
        unknown_0x3ff87a8c = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x49b9936d
        unknown_0x49b9936d = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc96b8223
        unknown_0xc96b8223 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x53fdcb5b
        unknown_0x53fdcb5b = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d7ef013
        unknown_0x0d7ef013 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaa85c885
        unknown_0xaa85c885 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80f7e605
        pause = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x479f6a4f
        taunt = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x778791f5
        look_around = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xce4c4668
        melee_attack = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5951a03f
        melee_dash = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x94615651
        scatter_shot = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x94f48974
        unknown_0x94f48974 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6e40fb76
        dive_attack = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb2c1e4fa
        unknown_0xb2c1e4fa = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf5cf3c0f
        unknown_0xf5cf3c0f = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6847efa7
        normal_missile = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x083fd602
        missile_jump = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdb21402f
        super_missile = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe63286eb
        unknown_0xe63286eb = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4aae6186
        unknown_0x4aae6186 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2bd1c15b
        sweep_beam = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb53693fa
        boost_ball = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2d7551e6
        unknown_0x2d7551e6 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x93a876f3
        phazon_attack = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaea228b9
        phazon_enrage = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x911a2476
        unknown_0x911a2476 = struct.unpack('>?', data.read(1))[0]
    
        return cls(unknown_0xb5af7831, unknown_0xac65eb7a, unknown_0x4f3855a0, unknown_0x08c0b02c, unknown_0x695f68c7, unknown_0xd061ff99, pause_duration_min, pause_duration_max, chance_to_double_dash, unknown_struct16, unknown_0x3ff87a8c, unknown_0x49b9936d, unknown_0xc96b8223, unknown_0x53fdcb5b, unknown_0x0d7ef013, unknown_0xaa85c885, pause, taunt, look_around, melee_attack, melee_dash, scatter_shot, unknown_0x94f48974, dive_attack, unknown_0xb2c1e4fa, unknown_0xf5cf3c0f, normal_missile, missile_jump, super_missile, unknown_0xe63286eb, unknown_0x4aae6186, sweep_beam, boost_ball, unknown_0x2d7551e6, phazon_attack, phazon_enrage, unknown_0x911a2476)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00%')  # 37 properties

        data.write(b'\xb5\xafx1')  # 0xb5af7831
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb5af7831))

        data.write(b'\xace\xebz')  # 0xac65eb7a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xac65eb7a))

        data.write(b'O8U\xa0')  # 0x4f3855a0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4f3855a0))

        data.write(b'\x08\xc0\xb0,')  # 0x8c0b02c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x08c0b02c))

        data.write(b'i_h\xc7')  # 0x695f68c7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x695f68c7))

        data.write(b'\xd0a\xff\x99')  # 0xd061ff99
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd061ff99))

        data.write(b'\x97\xdb\xd4*')  # 0x97dbd42a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pause_duration_min))

        data.write(b'q\xbb{\xcb')  # 0x71bb7bcb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pause_duration_max))

        data.write(b'\xb7Qw\x8b')  # 0xb751778b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.chance_to_double_dash))

        data.write(b'\xd6t\x03H')  # 0xd6740348
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct16.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'?\xf8z\x8c')  # 0x3ff87a8c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x3ff87a8c))

        data.write(b'I\xb9\x93m')  # 0x49b9936d
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x49b9936d))

        data.write(b'\xc9k\x82#')  # 0xc96b8223
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xc96b8223))

        data.write(b'S\xfd\xcb[')  # 0x53fdcb5b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x53fdcb5b))

        data.write(b'\r~\xf0\x13')  # 0xd7ef013
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x0d7ef013))

        data.write(b'\xaa\x85\xc8\x85')  # 0xaa85c885
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xaa85c885))

        data.write(b'\x80\xf7\xe6\x05')  # 0x80f7e605
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pause))

        data.write(b'G\x9fjO')  # 0x479f6a4f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.taunt))

        data.write(b'w\x87\x91\xf5')  # 0x778791f5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.look_around))

        data.write(b'\xceLFh')  # 0xce4c4668
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.melee_attack))

        data.write(b'YQ\xa0?')  # 0x5951a03f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.melee_dash))

        data.write(b'\x94aVQ')  # 0x94615651
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scatter_shot))

        data.write(b'\x94\xf4\x89t')  # 0x94f48974
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x94f48974))

        data.write(b'n@\xfbv')  # 0x6e40fb76
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dive_attack))

        data.write(b'\xb2\xc1\xe4\xfa')  # 0xb2c1e4fa
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xb2c1e4fa))

        data.write(b'\xf5\xcf<\x0f')  # 0xf5cf3c0f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xf5cf3c0f))

        data.write(b'hG\xef\xa7')  # 0x6847efa7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.normal_missile))

        data.write(b'\x08?\xd6\x02')  # 0x83fd602
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.missile_jump))

        data.write(b'\xdb!@/')  # 0xdb21402f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.super_missile))

        data.write(b'\xe62\x86\xeb')  # 0xe63286eb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe63286eb))

        data.write(b'J\xaea\x86')  # 0x4aae6186
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4aae6186))

        data.write(b'+\xd1\xc1[')  # 0x2bd1c15b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.sweep_beam))

        data.write(b'\xb56\x93\xfa')  # 0xb53693fa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.boost_ball))

        data.write(b'-uQ\xe6')  # 0x2d7551e6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x2d7551e6))

        data.write(b'\x93\xa8v\xf3')  # 0x93a876f3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.phazon_attack))

        data.write(b'\xae\xa2(\xb9')  # 0xaea228b9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.phazon_enrage))

        data.write(b'\x91\x1a$v')  # 0x911a2476
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x911a2476))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct17Json", data)
        return cls(
            unknown_0xb5af7831=json_data['unknown_0xb5af7831'],
            unknown_0xac65eb7a=json_data['unknown_0xac65eb7a'],
            unknown_0x4f3855a0=json_data['unknown_0x4f3855a0'],
            unknown_0x08c0b02c=json_data['unknown_0x08c0b02c'],
            unknown_0x695f68c7=json_data['unknown_0x695f68c7'],
            unknown_0xd061ff99=json_data['unknown_0xd061ff99'],
            pause_duration_min=json_data['pause_duration_min'],
            pause_duration_max=json_data['pause_duration_max'],
            chance_to_double_dash=json_data['chance_to_double_dash'],
            unknown_struct16=UnknownStruct16.from_json(json_data['unknown_struct16']),
            unknown_0x3ff87a8c=json_data['unknown_0x3ff87a8c'],
            unknown_0x49b9936d=json_data['unknown_0x49b9936d'],
            unknown_0xc96b8223=json_data['unknown_0xc96b8223'],
            unknown_0x53fdcb5b=json_data['unknown_0x53fdcb5b'],
            unknown_0x0d7ef013=json_data['unknown_0x0d7ef013'],
            unknown_0xaa85c885=json_data['unknown_0xaa85c885'],
            pause=json_data['pause'],
            taunt=json_data['taunt'],
            look_around=json_data['look_around'],
            melee_attack=json_data['melee_attack'],
            melee_dash=json_data['melee_dash'],
            scatter_shot=json_data['scatter_shot'],
            unknown_0x94f48974=json_data['unknown_0x94f48974'],
            dive_attack=json_data['dive_attack'],
            unknown_0xb2c1e4fa=json_data['unknown_0xb2c1e4fa'],
            unknown_0xf5cf3c0f=json_data['unknown_0xf5cf3c0f'],
            normal_missile=json_data['normal_missile'],
            missile_jump=json_data['missile_jump'],
            super_missile=json_data['super_missile'],
            unknown_0xe63286eb=json_data['unknown_0xe63286eb'],
            unknown_0x4aae6186=json_data['unknown_0x4aae6186'],
            sweep_beam=json_data['sweep_beam'],
            boost_ball=json_data['boost_ball'],
            unknown_0x2d7551e6=json_data['unknown_0x2d7551e6'],
            phazon_attack=json_data['phazon_attack'],
            phazon_enrage=json_data['phazon_enrage'],
            unknown_0x911a2476=json_data['unknown_0x911a2476'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xb5af7831': self.unknown_0xb5af7831,
            'unknown_0xac65eb7a': self.unknown_0xac65eb7a,
            'unknown_0x4f3855a0': self.unknown_0x4f3855a0,
            'unknown_0x08c0b02c': self.unknown_0x08c0b02c,
            'unknown_0x695f68c7': self.unknown_0x695f68c7,
            'unknown_0xd061ff99': self.unknown_0xd061ff99,
            'pause_duration_min': self.pause_duration_min,
            'pause_duration_max': self.pause_duration_max,
            'chance_to_double_dash': self.chance_to_double_dash,
            'unknown_struct16': self.unknown_struct16.to_json(),
            'unknown_0x3ff87a8c': self.unknown_0x3ff87a8c,
            'unknown_0x49b9936d': self.unknown_0x49b9936d,
            'unknown_0xc96b8223': self.unknown_0xc96b8223,
            'unknown_0x53fdcb5b': self.unknown_0x53fdcb5b,
            'unknown_0x0d7ef013': self.unknown_0x0d7ef013,
            'unknown_0xaa85c885': self.unknown_0xaa85c885,
            'pause': self.pause,
            'taunt': self.taunt,
            'look_around': self.look_around,
            'melee_attack': self.melee_attack,
            'melee_dash': self.melee_dash,
            'scatter_shot': self.scatter_shot,
            'unknown_0x94f48974': self.unknown_0x94f48974,
            'dive_attack': self.dive_attack,
            'unknown_0xb2c1e4fa': self.unknown_0xb2c1e4fa,
            'unknown_0xf5cf3c0f': self.unknown_0xf5cf3c0f,
            'normal_missile': self.normal_missile,
            'missile_jump': self.missile_jump,
            'super_missile': self.super_missile,
            'unknown_0xe63286eb': self.unknown_0xe63286eb,
            'unknown_0x4aae6186': self.unknown_0x4aae6186,
            'sweep_beam': self.sweep_beam,
            'boost_ball': self.boost_ball,
            'unknown_0x2d7551e6': self.unknown_0x2d7551e6,
            'phazon_attack': self.phazon_attack,
            'phazon_enrage': self.phazon_enrage,
            'unknown_0x911a2476': self.unknown_0x911a2476,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unknown_struct16.dependencies_for, "unknown_struct16", "UnknownStruct16"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for UnknownStruct17.{field_name} ({field_type}): {e}"
                )


def _decode_unknown_0xb5af7831(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xac65eb7a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4f3855a0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x08c0b02c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x695f68c7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd061ff99(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_pause_duration_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_pause_duration_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_chance_to_double_dash(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3ff87a8c(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x49b9936d(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xc96b8223(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x53fdcb5b(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x0d7ef013(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xaa85c885(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_pause(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_taunt(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_look_around(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_melee_attack(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_melee_dash(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scatter_shot(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x94f48974(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dive_attack(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb2c1e4fa(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xf5cf3c0f(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_normal_missile(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_missile_jump(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_super_missile(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe63286eb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4aae6186(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sweep_beam(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_boost_ball(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2d7551e6(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_phazon_attack(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_phazon_enrage(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x911a2476(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xb5af7831: ('unknown_0xb5af7831', _decode_unknown_0xb5af7831),
    0xac65eb7a: ('unknown_0xac65eb7a', _decode_unknown_0xac65eb7a),
    0x4f3855a0: ('unknown_0x4f3855a0', _decode_unknown_0x4f3855a0),
    0x8c0b02c: ('unknown_0x08c0b02c', _decode_unknown_0x08c0b02c),
    0x695f68c7: ('unknown_0x695f68c7', _decode_unknown_0x695f68c7),
    0xd061ff99: ('unknown_0xd061ff99', _decode_unknown_0xd061ff99),
    0x97dbd42a: ('pause_duration_min', _decode_pause_duration_min),
    0x71bb7bcb: ('pause_duration_max', _decode_pause_duration_max),
    0xb751778b: ('chance_to_double_dash', _decode_chance_to_double_dash),
    0xd6740348: ('unknown_struct16', UnknownStruct16.from_stream),
    0x3ff87a8c: ('unknown_0x3ff87a8c', _decode_unknown_0x3ff87a8c),
    0x49b9936d: ('unknown_0x49b9936d', _decode_unknown_0x49b9936d),
    0xc96b8223: ('unknown_0xc96b8223', _decode_unknown_0xc96b8223),
    0x53fdcb5b: ('unknown_0x53fdcb5b', _decode_unknown_0x53fdcb5b),
    0xd7ef013: ('unknown_0x0d7ef013', _decode_unknown_0x0d7ef013),
    0xaa85c885: ('unknown_0xaa85c885', _decode_unknown_0xaa85c885),
    0x80f7e605: ('pause', _decode_pause),
    0x479f6a4f: ('taunt', _decode_taunt),
    0x778791f5: ('look_around', _decode_look_around),
    0xce4c4668: ('melee_attack', _decode_melee_attack),
    0x5951a03f: ('melee_dash', _decode_melee_dash),
    0x94615651: ('scatter_shot', _decode_scatter_shot),
    0x94f48974: ('unknown_0x94f48974', _decode_unknown_0x94f48974),
    0x6e40fb76: ('dive_attack', _decode_dive_attack),
    0xb2c1e4fa: ('unknown_0xb2c1e4fa', _decode_unknown_0xb2c1e4fa),
    0xf5cf3c0f: ('unknown_0xf5cf3c0f', _decode_unknown_0xf5cf3c0f),
    0x6847efa7: ('normal_missile', _decode_normal_missile),
    0x83fd602: ('missile_jump', _decode_missile_jump),
    0xdb21402f: ('super_missile', _decode_super_missile),
    0xe63286eb: ('unknown_0xe63286eb', _decode_unknown_0xe63286eb),
    0x4aae6186: ('unknown_0x4aae6186', _decode_unknown_0x4aae6186),
    0x2bd1c15b: ('sweep_beam', _decode_sweep_beam),
    0xb53693fa: ('boost_ball', _decode_boost_ball),
    0x2d7551e6: ('unknown_0x2d7551e6', _decode_unknown_0x2d7551e6),
    0x93a876f3: ('phazon_attack', _decode_phazon_attack),
    0xaea228b9: ('phazon_enrage', _decode_phazon_enrage),
    0x911a2476: ('unknown_0x911a2476', _decode_unknown_0x911a2476),
}
