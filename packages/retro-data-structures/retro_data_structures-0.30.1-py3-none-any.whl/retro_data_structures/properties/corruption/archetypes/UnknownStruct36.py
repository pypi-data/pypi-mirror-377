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
from retro_data_structures.properties.corruption.archetypes.GhorStructC import GhorStructC
from retro_data_structures.properties.corruption.archetypes.ShockWaveInfo import ShockWaveInfo
from retro_data_structures.properties.corruption.archetypes.UnknownStruct35 import UnknownStruct35
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class UnknownStruct36Json(typing_extensions.TypedDict):
        is_gandrayda: bool
        slip_time: float
        collision_set: str
        unknown_0xfaf186b6: str
        snap_locator: str
        unknown_struct35: json_util.JsonObject
        ghor_struct_c: json_util.JsonObject
        ball_target_extend: json_util.JsonObject
        ball_target_retract: json_util.JsonObject
        unknown_0x13d02889: str
        unknown_0x4a744859: json_util.JsonObject
        jump_distance: float
        jump_height: float
        jump_shockwave: json_util.JsonObject
        shock_wave_info: json_util.JsonObject
        move_min_range: float
        move_max_range: float
        move_desired_range: float
        move_min_distance: float
        move_desired_distance: float
        unknown_0xa31d0055: float
        unknown_0x9ae279da: float
        unknown_0xb39c84c2: float
        unknown_0x2a35593b: float
    

@dataclasses.dataclass()
class UnknownStruct36(BaseProperty):
    is_gandrayda: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x531a8c85, original_name='IsGandrayda'
        ),
    })
    slip_time: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe9865fc0, original_name='SlipTime'
        ),
    })
    collision_set: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x9ce31ffa, original_name='CollisionSet'
        ),
    })
    unknown_0xfaf186b6: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xfaf186b6, original_name='Unknown'
        ),
    })
    snap_locator: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x5d1949b5, original_name='SnapLocator'
        ),
    })
    unknown_struct35: UnknownStruct35 = dataclasses.field(default_factory=UnknownStruct35, metadata={
        'reflection': FieldReflection[UnknownStruct35](
            UnknownStruct35, id=0xaec7546e, original_name='UnknownStruct35', from_json=UnknownStruct35.from_json, to_json=UnknownStruct35.to_json
        ),
    })
    ghor_struct_c: GhorStructC = dataclasses.field(default_factory=GhorStructC, metadata={
        'reflection': FieldReflection[GhorStructC](
            GhorStructC, id=0x810ec49a, original_name='GhorStructC', from_json=GhorStructC.from_json, to_json=GhorStructC.to_json
        ),
    })
    ball_target_extend: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x9b98f8ce, original_name='BallTargetExtend', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    ball_target_retract: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x3d14fb8e, original_name='BallTargetRetract', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0x13d02889: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x13d02889, original_name='Unknown'
        ),
    })
    unknown_0x4a744859: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x4a744859, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    jump_distance: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9b2ea489, original_name='JumpDistance'
        ),
    })
    jump_height: float = dataclasses.field(default=14.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd0475191, original_name='JumpHeight'
        ),
    })
    jump_shockwave: ShockWaveInfo = dataclasses.field(default_factory=ShockWaveInfo, metadata={
        'reflection': FieldReflection[ShockWaveInfo](
            ShockWaveInfo, id=0x56c192f3, original_name='JumpShockwave', from_json=ShockWaveInfo.from_json, to_json=ShockWaveInfo.to_json
        ),
    })
    shock_wave_info: ShockWaveInfo = dataclasses.field(default_factory=ShockWaveInfo, metadata={
        'reflection': FieldReflection[ShockWaveInfo](
            ShockWaveInfo, id=0xf55a1548, original_name='ShockWaveInfo', from_json=ShockWaveInfo.from_json, to_json=ShockWaveInfo.to_json
        ),
    })
    move_min_range: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8554e360, original_name='MoveMinRange'
        ),
    })
    move_max_range: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc51b9b16, original_name='MoveMaxRange'
        ),
    })
    move_desired_range: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xafecab12, original_name='MoveDesiredRange'
        ),
    })
    move_min_distance: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7cc59b31, original_name='MoveMinDistance'
        ),
    })
    move_desired_distance: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd6aad996, original_name='MoveDesiredDistance'
        ),
    })
    unknown_0xa31d0055: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa31d0055, original_name='Unknown'
        ),
    })
    unknown_0x9ae279da: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9ae279da, original_name='Unknown'
        ),
    })
    unknown_0xb39c84c2: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb39c84c2, original_name='Unknown'
        ),
    })
    unknown_0x2a35593b: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2a35593b, original_name='Unknown'
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
        if property_count != 24:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x531a8c85
        is_gandrayda = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe9865fc0
        slip_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9ce31ffa
        collision_set = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfaf186b6
        unknown_0xfaf186b6 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5d1949b5
        snap_locator = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaec7546e
        unknown_struct35 = UnknownStruct35.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x810ec49a
        ghor_struct_c = GhorStructC.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9b98f8ce
        ball_target_extend = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d14fb8e
        ball_target_retract = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x13d02889
        unknown_0x13d02889 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4a744859
        unknown_0x4a744859 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9b2ea489
        jump_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd0475191
        jump_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x56c192f3
        jump_shockwave = ShockWaveInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf55a1548
        shock_wave_info = ShockWaveInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8554e360
        move_min_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc51b9b16
        move_max_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xafecab12
        move_desired_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7cc59b31
        move_min_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd6aad996
        move_desired_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa31d0055
        unknown_0xa31d0055 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9ae279da
        unknown_0x9ae279da = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb39c84c2
        unknown_0xb39c84c2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2a35593b
        unknown_0x2a35593b = struct.unpack('>f', data.read(4))[0]
    
        return cls(is_gandrayda, slip_time, collision_set, unknown_0xfaf186b6, snap_locator, unknown_struct35, ghor_struct_c, ball_target_extend, ball_target_retract, unknown_0x13d02889, unknown_0x4a744859, jump_distance, jump_height, jump_shockwave, shock_wave_info, move_min_range, move_max_range, move_desired_range, move_min_distance, move_desired_distance, unknown_0xa31d0055, unknown_0x9ae279da, unknown_0xb39c84c2, unknown_0x2a35593b)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x18')  # 24 properties

        data.write(b'S\x1a\x8c\x85')  # 0x531a8c85
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_gandrayda))

        data.write(b'\xe9\x86_\xc0')  # 0xe9865fc0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.slip_time))

        data.write(b'\x9c\xe3\x1f\xfa')  # 0x9ce31ffa
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.collision_set.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfa\xf1\x86\xb6')  # 0xfaf186b6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0xfaf186b6.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b']\x19I\xb5')  # 0x5d1949b5
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.snap_locator.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xae\xc7Tn')  # 0xaec7546e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct35.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x81\x0e\xc4\x9a')  # 0x810ec49a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_c.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9b\x98\xf8\xce')  # 0x9b98f8ce
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ball_target_extend.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'=\x14\xfb\x8e')  # 0x3d14fb8e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ball_target_retract.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x13\xd0(\x89')  # 0x13d02889
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0x13d02889.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'JtHY')  # 0x4a744859
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x4a744859.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9b.\xa4\x89')  # 0x9b2ea489
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.jump_distance))

        data.write(b'\xd0GQ\x91')  # 0xd0475191
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.jump_height))

        data.write(b'V\xc1\x92\xf3')  # 0x56c192f3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.jump_shockwave.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf5Z\x15H')  # 0xf55a1548
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shock_wave_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x85T\xe3`')  # 0x8554e360
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.move_min_range))

        data.write(b'\xc5\x1b\x9b\x16')  # 0xc51b9b16
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.move_max_range))

        data.write(b'\xaf\xec\xab\x12')  # 0xafecab12
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.move_desired_range))

        data.write(b'|\xc5\x9b1')  # 0x7cc59b31
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.move_min_distance))

        data.write(b'\xd6\xaa\xd9\x96')  # 0xd6aad996
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.move_desired_distance))

        data.write(b'\xa3\x1d\x00U')  # 0xa31d0055
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa31d0055))

        data.write(b'\x9a\xe2y\xda')  # 0x9ae279da
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9ae279da))

        data.write(b'\xb3\x9c\x84\xc2')  # 0xb39c84c2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb39c84c2))

        data.write(b'*5Y;')  # 0x2a35593b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2a35593b))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct36Json", data)
        return cls(
            is_gandrayda=json_data['is_gandrayda'],
            slip_time=json_data['slip_time'],
            collision_set=json_data['collision_set'],
            unknown_0xfaf186b6=json_data['unknown_0xfaf186b6'],
            snap_locator=json_data['snap_locator'],
            unknown_struct35=UnknownStruct35.from_json(json_data['unknown_struct35']),
            ghor_struct_c=GhorStructC.from_json(json_data['ghor_struct_c']),
            ball_target_extend=Spline.from_json(json_data['ball_target_extend']),
            ball_target_retract=Spline.from_json(json_data['ball_target_retract']),
            unknown_0x13d02889=json_data['unknown_0x13d02889'],
            unknown_0x4a744859=Spline.from_json(json_data['unknown_0x4a744859']),
            jump_distance=json_data['jump_distance'],
            jump_height=json_data['jump_height'],
            jump_shockwave=ShockWaveInfo.from_json(json_data['jump_shockwave']),
            shock_wave_info=ShockWaveInfo.from_json(json_data['shock_wave_info']),
            move_min_range=json_data['move_min_range'],
            move_max_range=json_data['move_max_range'],
            move_desired_range=json_data['move_desired_range'],
            move_min_distance=json_data['move_min_distance'],
            move_desired_distance=json_data['move_desired_distance'],
            unknown_0xa31d0055=json_data['unknown_0xa31d0055'],
            unknown_0x9ae279da=json_data['unknown_0x9ae279da'],
            unknown_0xb39c84c2=json_data['unknown_0xb39c84c2'],
            unknown_0x2a35593b=json_data['unknown_0x2a35593b'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'is_gandrayda': self.is_gandrayda,
            'slip_time': self.slip_time,
            'collision_set': self.collision_set,
            'unknown_0xfaf186b6': self.unknown_0xfaf186b6,
            'snap_locator': self.snap_locator,
            'unknown_struct35': self.unknown_struct35.to_json(),
            'ghor_struct_c': self.ghor_struct_c.to_json(),
            'ball_target_extend': self.ball_target_extend.to_json(),
            'ball_target_retract': self.ball_target_retract.to_json(),
            'unknown_0x13d02889': self.unknown_0x13d02889,
            'unknown_0x4a744859': self.unknown_0x4a744859.to_json(),
            'jump_distance': self.jump_distance,
            'jump_height': self.jump_height,
            'jump_shockwave': self.jump_shockwave.to_json(),
            'shock_wave_info': self.shock_wave_info.to_json(),
            'move_min_range': self.move_min_range,
            'move_max_range': self.move_max_range,
            'move_desired_range': self.move_desired_range,
            'move_min_distance': self.move_min_distance,
            'move_desired_distance': self.move_desired_distance,
            'unknown_0xa31d0055': self.unknown_0xa31d0055,
            'unknown_0x9ae279da': self.unknown_0x9ae279da,
            'unknown_0xb39c84c2': self.unknown_0xb39c84c2,
            'unknown_0x2a35593b': self.unknown_0x2a35593b,
        }


def _decode_is_gandrayda(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_slip_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_collision_set(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0xfaf186b6(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_snap_locator(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0x13d02889(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_jump_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_jump_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_move_min_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_move_max_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_move_desired_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_move_min_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_move_desired_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa31d0055(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9ae279da(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb39c84c2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2a35593b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x531a8c85: ('is_gandrayda', _decode_is_gandrayda),
    0xe9865fc0: ('slip_time', _decode_slip_time),
    0x9ce31ffa: ('collision_set', _decode_collision_set),
    0xfaf186b6: ('unknown_0xfaf186b6', _decode_unknown_0xfaf186b6),
    0x5d1949b5: ('snap_locator', _decode_snap_locator),
    0xaec7546e: ('unknown_struct35', UnknownStruct35.from_stream),
    0x810ec49a: ('ghor_struct_c', GhorStructC.from_stream),
    0x9b98f8ce: ('ball_target_extend', Spline.from_stream),
    0x3d14fb8e: ('ball_target_retract', Spline.from_stream),
    0x13d02889: ('unknown_0x13d02889', _decode_unknown_0x13d02889),
    0x4a744859: ('unknown_0x4a744859', Spline.from_stream),
    0x9b2ea489: ('jump_distance', _decode_jump_distance),
    0xd0475191: ('jump_height', _decode_jump_height),
    0x56c192f3: ('jump_shockwave', ShockWaveInfo.from_stream),
    0xf55a1548: ('shock_wave_info', ShockWaveInfo.from_stream),
    0x8554e360: ('move_min_range', _decode_move_min_range),
    0xc51b9b16: ('move_max_range', _decode_move_max_range),
    0xafecab12: ('move_desired_range', _decode_move_desired_range),
    0x7cc59b31: ('move_min_distance', _decode_move_min_distance),
    0xd6aad996: ('move_desired_distance', _decode_move_desired_distance),
    0xa31d0055: ('unknown_0xa31d0055', _decode_unknown_0xa31d0055),
    0x9ae279da: ('unknown_0x9ae279da', _decode_unknown_0x9ae279da),
    0xb39c84c2: ('unknown_0xb39c84c2', _decode_unknown_0xb39c84c2),
    0x2a35593b: ('unknown_0x2a35593b', _decode_unknown_0x2a35593b),
}
