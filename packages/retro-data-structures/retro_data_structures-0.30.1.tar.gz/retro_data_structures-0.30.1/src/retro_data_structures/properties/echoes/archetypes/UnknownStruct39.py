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
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class UnknownStruct39Json(typing_extensions.TypedDict):
        start_state: int
        explosion_damage: json_util.JsonObject
        min_height: float
        max_height: float
        min_down_height: float
        max_down_height: float
        separation_distance: float
        min_life_time: float
        max_life_time: float
        normal_knockback: float
        heavy_knockback: float
        knockback_decline: float
        is_dark_shredder: bool
        desired_distance: float
    

@dataclasses.dataclass()
class UnknownStruct39(BaseProperty):
    start_state: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0x46d866d1, original_name='StartState'
        ),
    })
    explosion_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xdeff74ea, original_name='ExplosionDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    min_height: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc6c4232c, original_name='MinHeight'
        ),
    })
    max_height: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7fe2b85d, original_name='MaxHeight'
        ),
    })
    min_down_height: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x10be8ad3, original_name='MinDownHeight'
        ),
    })
    max_down_height: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x43189237, original_name='MaxDownHeight'
        ),
    })
    separation_distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x01559f27, original_name='SeparationDistance'
        ),
    })
    min_life_time: float = dataclasses.field(default=14.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x07dcd404, original_name='MinLifeTime'
        ),
    })
    max_life_time: float = dataclasses.field(default=16.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x56256f59, original_name='MaxLifeTime'
        ),
    })
    normal_knockback: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3061976c, original_name='NormalKnockback'
        ),
    })
    heavy_knockback: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x93a80aa2, original_name='HeavyKnockback'
        ),
    })
    knockback_decline: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4c6b2421, original_name='KnockbackDecline'
        ),
    })
    is_dark_shredder: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xcff9971b, original_name='IsDarkShredder'
        ),
    })
    desired_distance: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x60be35a1, original_name='DesiredDistance'
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
        assert property_id == 0x46d866d1
        start_state = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdeff74ea
        explosion_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6c4232c
        min_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fe2b85d
        max_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x10be8ad3
        min_down_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x43189237
        max_down_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01559f27
        separation_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x07dcd404
        min_life_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x56256f59
        max_life_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3061976c
        normal_knockback = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x93a80aa2
        heavy_knockback = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4c6b2421
        knockback_decline = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcff9971b
        is_dark_shredder = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x60be35a1
        desired_distance = struct.unpack('>f', data.read(4))[0]
    
        return cls(start_state, explosion_damage, min_height, max_height, min_down_height, max_down_height, separation_distance, min_life_time, max_life_time, normal_knockback, heavy_knockback, knockback_decline, is_dark_shredder, desired_distance)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0e')  # 14 properties

        data.write(b'F\xd8f\xd1')  # 0x46d866d1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.start_state))

        data.write(b'\xde\xfft\xea')  # 0xdeff74ea
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.explosion_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc6\xc4#,')  # 0xc6c4232c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_height))

        data.write(b'\x7f\xe2\xb8]')  # 0x7fe2b85d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_height))

        data.write(b'\x10\xbe\x8a\xd3')  # 0x10be8ad3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_down_height))

        data.write(b'C\x18\x927')  # 0x43189237
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_down_height))

        data.write(b"\x01U\x9f'")  # 0x1559f27
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.separation_distance))

        data.write(b'\x07\xdc\xd4\x04')  # 0x7dcd404
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_life_time))

        data.write(b'V%oY')  # 0x56256f59
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_life_time))

        data.write(b'0a\x97l')  # 0x3061976c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.normal_knockback))

        data.write(b'\x93\xa8\n\xa2')  # 0x93a80aa2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.heavy_knockback))

        data.write(b'Lk$!')  # 0x4c6b2421
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.knockback_decline))

        data.write(b'\xcf\xf9\x97\x1b')  # 0xcff9971b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_dark_shredder))

        data.write(b'`\xbe5\xa1')  # 0x60be35a1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.desired_distance))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct39Json", data)
        return cls(
            start_state=json_data['start_state'],
            explosion_damage=DamageInfo.from_json(json_data['explosion_damage']),
            min_height=json_data['min_height'],
            max_height=json_data['max_height'],
            min_down_height=json_data['min_down_height'],
            max_down_height=json_data['max_down_height'],
            separation_distance=json_data['separation_distance'],
            min_life_time=json_data['min_life_time'],
            max_life_time=json_data['max_life_time'],
            normal_knockback=json_data['normal_knockback'],
            heavy_knockback=json_data['heavy_knockback'],
            knockback_decline=json_data['knockback_decline'],
            is_dark_shredder=json_data['is_dark_shredder'],
            desired_distance=json_data['desired_distance'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'start_state': self.start_state,
            'explosion_damage': self.explosion_damage.to_json(),
            'min_height': self.min_height,
            'max_height': self.max_height,
            'min_down_height': self.min_down_height,
            'max_down_height': self.max_down_height,
            'separation_distance': self.separation_distance,
            'min_life_time': self.min_life_time,
            'max_life_time': self.max_life_time,
            'normal_knockback': self.normal_knockback,
            'heavy_knockback': self.heavy_knockback,
            'knockback_decline': self.knockback_decline,
            'is_dark_shredder': self.is_dark_shredder,
            'desired_distance': self.desired_distance,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.explosion_damage.dependencies_for, "explosion_damage", "DamageInfo"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for UnknownStruct39.{field_name} ({field_type}): {e}"
                )


def _decode_start_state(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_min_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_down_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_down_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_separation_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_life_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_life_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_normal_knockback(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_heavy_knockback(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_knockback_decline(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_is_dark_shredder(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_desired_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x46d866d1: ('start_state', _decode_start_state),
    0xdeff74ea: ('explosion_damage', DamageInfo.from_stream),
    0xc6c4232c: ('min_height', _decode_min_height),
    0x7fe2b85d: ('max_height', _decode_max_height),
    0x10be8ad3: ('min_down_height', _decode_min_down_height),
    0x43189237: ('max_down_height', _decode_max_down_height),
    0x1559f27: ('separation_distance', _decode_separation_distance),
    0x7dcd404: ('min_life_time', _decode_min_life_time),
    0x56256f59: ('max_life_time', _decode_max_life_time),
    0x3061976c: ('normal_knockback', _decode_normal_knockback),
    0x93a80aa2: ('heavy_knockback', _decode_heavy_knockback),
    0x4c6b2421: ('knockback_decline', _decode_knockback_decline),
    0xcff9971b: ('is_dark_shredder', _decode_is_dark_shredder),
    0x60be35a1: ('desired_distance', _decode_desired_distance),
}
