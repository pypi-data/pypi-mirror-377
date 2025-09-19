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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Vector import Vector

if typing.TYPE_CHECKING:
    class RagDollDataJson(typing_extensions.TypedDict):
        gravity: json_util.JsonValue
        rag_doll_density: float
        air_density: float
        fluid_gravity: json_util.JsonValue
        fluid_density: float
        restitution_multiplier: float
        friction_multiplier: float
        unknown_0x91936b5e: float
        unknown_0x81d40910: float
        static_speed: float
        max_time: float
        sound_impact: int
        unknown_0xce5d16c3: bool
        damp_rotation: bool
        ignore_max_time: bool
        ignore_dock_collision: bool
        ignore_all_collision: bool
        collision_type: int
        collision_plane_normal: json_util.JsonValue
        collision_plane_constant: float
    

class CollisionType(enum.IntEnum):
    Unknown1 = 1750192226
    Unknown2 = 500705356
    Unknown3 = 2418955086

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


_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x9e235c61, 0x6ab0341a, 0x43c02224, 0xa0421aa5, 0x6bd4e178, 0x446a33f5, 0x8b331ce, 0x91936b5e, 0x81d40910, 0x16407ed9, 0x3e7b2b4, 0xe190f77d, 0xce5d16c3, 0xa99a0e33, 0xe7b88d51, 0x7de2e6ba, 0xe1107c4a, 0xb674ea3d, 0x96bb302a, 0x4414d99c)


@dataclasses.dataclass()
class RagDollData(BaseProperty):
    gravity: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=-50.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x9e235c61, original_name='Gravity', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    rag_doll_density: float = dataclasses.field(default=8000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6ab0341a, original_name='RagDollDensity'
        ),
    })
    air_density: float = dataclasses.field(default=1.2000000476837158, metadata={
        'reflection': FieldReflection[float](
            float, id=0x43c02224, original_name='AirDensity'
        ),
    })
    fluid_gravity: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=-3.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0xa0421aa5, original_name='FluidGravity', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    fluid_density: float = dataclasses.field(default=1000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6bd4e178, original_name='FluidDensity'
        ),
    })
    restitution_multiplier: float = dataclasses.field(default=0.125, metadata={
        'reflection': FieldReflection[float](
            float, id=0x446a33f5, original_name='RestitutionMultiplier'
        ),
    })
    friction_multiplier: float = dataclasses.field(default=0.8500000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0x08b331ce, original_name='FrictionMultiplier'
        ),
    })
    unknown_0x91936b5e: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x91936b5e, original_name='Unknown'
        ),
    })
    unknown_0x81d40910: float = dataclasses.field(default=3000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x81d40910, original_name='Unknown'
        ),
    })
    static_speed: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x16407ed9, original_name='StaticSpeed'
        ),
    })
    max_time: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x03e7b2b4, original_name='MaxTime'
        ),
    })
    sound_impact: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe190f77d, original_name='Sound_Impact'
        ),
    })
    unknown_0xce5d16c3: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xce5d16c3, original_name='Unknown'
        ),
    })
    damp_rotation: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa99a0e33, original_name='DampRotation'
        ),
    })
    ignore_max_time: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe7b88d51, original_name='IgnoreMaxTime'
        ),
    })
    ignore_dock_collision: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7de2e6ba, original_name='IgnoreDockCollision'
        ),
    })
    ignore_all_collision: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe1107c4a, original_name='IgnoreAllCollision'
        ),
    })
    collision_type: CollisionType = dataclasses.field(default=CollisionType.Unknown3, metadata={
        'reflection': FieldReflection[CollisionType](
            CollisionType, id=0xb674ea3d, original_name='CollisionType', from_json=CollisionType.from_json, to_json=CollisionType.to_json
        ),
    })
    collision_plane_normal: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=1.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x96bb302a, original_name='CollisionPlaneNormal', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    collision_plane_constant: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4414d99c, original_name='CollisionPlaneConstant'
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
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfffLHfLHfLHfffLHfLHfLHfLHfLHfLHfLHfLHQLH?LH?LH?LH?LH?LHLLHfffLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(213))
        assert (dec[0], dec[5], dec[8], dec[11], dec[16], dec[19], dec[22], dec[25], dec[28], dec[31], dec[34], dec[37], dec[40], dec[43], dec[46], dec[49], dec[52], dec[55], dec[58], dec[63]) == _FAST_IDS
        return cls(
            Vector(*dec[2:5]),
            dec[7],
            dec[10],
            Vector(*dec[13:16]),
            dec[18],
            dec[21],
            dec[24],
            dec[27],
            dec[30],
            dec[33],
            dec[36],
            dec[39],
            dec[42],
            dec[45],
            dec[48],
            dec[51],
            dec[54],
            CollisionType(dec[57]),
            Vector(*dec[60:63]),
            dec[65],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x14')  # 20 properties

        data.write(b'\x9e#\\a')  # 0x9e235c61
        data.write(b'\x00\x0c')  # size
        self.gravity.to_stream(data)

        data.write(b'j\xb04\x1a')  # 0x6ab0341a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.rag_doll_density))

        data.write(b'C\xc0"$')  # 0x43c02224
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.air_density))

        data.write(b'\xa0B\x1a\xa5')  # 0xa0421aa5
        data.write(b'\x00\x0c')  # size
        self.fluid_gravity.to_stream(data)

        data.write(b'k\xd4\xe1x')  # 0x6bd4e178
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fluid_density))

        data.write(b'Dj3\xf5')  # 0x446a33f5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.restitution_multiplier))

        data.write(b'\x08\xb31\xce')  # 0x8b331ce
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.friction_multiplier))

        data.write(b'\x91\x93k^')  # 0x91936b5e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x91936b5e))

        data.write(b'\x81\xd4\t\x10')  # 0x81d40910
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x81d40910))

        data.write(b'\x16@~\xd9')  # 0x16407ed9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.static_speed))

        data.write(b'\x03\xe7\xb2\xb4')  # 0x3e7b2b4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_time))

        data.write(b'\xe1\x90\xf7}')  # 0xe190f77d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_impact))

        data.write(b'\xce]\x16\xc3')  # 0xce5d16c3
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xce5d16c3))

        data.write(b'\xa9\x9a\x0e3')  # 0xa99a0e33
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.damp_rotation))

        data.write(b'\xe7\xb8\x8dQ')  # 0xe7b88d51
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.ignore_max_time))

        data.write(b'}\xe2\xe6\xba')  # 0x7de2e6ba
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.ignore_dock_collision))

        data.write(b'\xe1\x10|J')  # 0xe1107c4a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.ignore_all_collision))

        data.write(b'\xb6t\xea=')  # 0xb674ea3d
        data.write(b'\x00\x04')  # size
        self.collision_type.to_stream(data)

        data.write(b'\x96\xbb0*')  # 0x96bb302a
        data.write(b'\x00\x0c')  # size
        self.collision_plane_normal.to_stream(data)

        data.write(b'D\x14\xd9\x9c')  # 0x4414d99c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.collision_plane_constant))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("RagDollDataJson", data)
        return cls(
            gravity=Vector.from_json(json_data['gravity']),
            rag_doll_density=json_data['rag_doll_density'],
            air_density=json_data['air_density'],
            fluid_gravity=Vector.from_json(json_data['fluid_gravity']),
            fluid_density=json_data['fluid_density'],
            restitution_multiplier=json_data['restitution_multiplier'],
            friction_multiplier=json_data['friction_multiplier'],
            unknown_0x91936b5e=json_data['unknown_0x91936b5e'],
            unknown_0x81d40910=json_data['unknown_0x81d40910'],
            static_speed=json_data['static_speed'],
            max_time=json_data['max_time'],
            sound_impact=json_data['sound_impact'],
            unknown_0xce5d16c3=json_data['unknown_0xce5d16c3'],
            damp_rotation=json_data['damp_rotation'],
            ignore_max_time=json_data['ignore_max_time'],
            ignore_dock_collision=json_data['ignore_dock_collision'],
            ignore_all_collision=json_data['ignore_all_collision'],
            collision_type=CollisionType.from_json(json_data['collision_type']),
            collision_plane_normal=Vector.from_json(json_data['collision_plane_normal']),
            collision_plane_constant=json_data['collision_plane_constant'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'gravity': self.gravity.to_json(),
            'rag_doll_density': self.rag_doll_density,
            'air_density': self.air_density,
            'fluid_gravity': self.fluid_gravity.to_json(),
            'fluid_density': self.fluid_density,
            'restitution_multiplier': self.restitution_multiplier,
            'friction_multiplier': self.friction_multiplier,
            'unknown_0x91936b5e': self.unknown_0x91936b5e,
            'unknown_0x81d40910': self.unknown_0x81d40910,
            'static_speed': self.static_speed,
            'max_time': self.max_time,
            'sound_impact': self.sound_impact,
            'unknown_0xce5d16c3': self.unknown_0xce5d16c3,
            'damp_rotation': self.damp_rotation,
            'ignore_max_time': self.ignore_max_time,
            'ignore_dock_collision': self.ignore_dock_collision,
            'ignore_all_collision': self.ignore_all_collision,
            'collision_type': self.collision_type.to_json(),
            'collision_plane_normal': self.collision_plane_normal.to_json(),
            'collision_plane_constant': self.collision_plane_constant,
        }


def _decode_gravity(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_rag_doll_density(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_air_density(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fluid_gravity(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_fluid_density(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_restitution_multiplier(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_friction_multiplier(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x91936b5e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x81d40910(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_static_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_impact(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0xce5d16c3(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_damp_rotation(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_ignore_max_time(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_ignore_dock_collision(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_ignore_all_collision(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_collision_type(data: typing.BinaryIO, property_size: int) -> CollisionType:
    return CollisionType.from_stream(data)


def _decode_collision_plane_normal(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_collision_plane_constant(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x9e235c61: ('gravity', _decode_gravity),
    0x6ab0341a: ('rag_doll_density', _decode_rag_doll_density),
    0x43c02224: ('air_density', _decode_air_density),
    0xa0421aa5: ('fluid_gravity', _decode_fluid_gravity),
    0x6bd4e178: ('fluid_density', _decode_fluid_density),
    0x446a33f5: ('restitution_multiplier', _decode_restitution_multiplier),
    0x8b331ce: ('friction_multiplier', _decode_friction_multiplier),
    0x91936b5e: ('unknown_0x91936b5e', _decode_unknown_0x91936b5e),
    0x81d40910: ('unknown_0x81d40910', _decode_unknown_0x81d40910),
    0x16407ed9: ('static_speed', _decode_static_speed),
    0x3e7b2b4: ('max_time', _decode_max_time),
    0xe190f77d: ('sound_impact', _decode_sound_impact),
    0xce5d16c3: ('unknown_0xce5d16c3', _decode_unknown_0xce5d16c3),
    0xa99a0e33: ('damp_rotation', _decode_damp_rotation),
    0xe7b88d51: ('ignore_max_time', _decode_ignore_max_time),
    0x7de2e6ba: ('ignore_dock_collision', _decode_ignore_dock_collision),
    0xe1107c4a: ('ignore_all_collision', _decode_ignore_all_collision),
    0xb674ea3d: ('collision_type', _decode_collision_type),
    0x96bb302a: ('collision_plane_normal', _decode_collision_plane_normal),
    0x4414d99c: ('collision_plane_constant', _decode_collision_plane_constant),
}
