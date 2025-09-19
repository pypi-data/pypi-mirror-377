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
from retro_data_structures.properties.corruption.archetypes.LaunchProjectileData import LaunchProjectileData

if typing.TYPE_CHECKING:
    class EyePodStructJson(typing_extensions.TypedDict):
        hyper_mode_check_chance: float
        unknown_0xc8e312dd: float
        unknown_0x2e83bd3c: float
        unknown_0xf06a131d: float
        unknown_0x160abcfc: float
        hyper_mode_duration_min: float
        hyper_mode_duration_max: float
        hyper_mode_vulnerability: json_util.JsonObject
        unknown_0x95e7a2c2: float
        unknown_0x76ba1c18: float
        unknown_0x64d482d5: int
        unknown_0xc3e002ac: int
        unknown_0x77b6541c: float
        unknown_0x9c889645: float
        launch_projectile_data: json_util.JsonObject
    

@dataclasses.dataclass()
class EyePodStruct(BaseProperty):
    hyper_mode_check_chance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf04452f3, original_name='HyperModeCheckChance'
        ),
    })
    unknown_0xc8e312dd: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc8e312dd, original_name='Unknown'
        ),
    })
    unknown_0x2e83bd3c: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2e83bd3c, original_name='Unknown'
        ),
    })
    unknown_0xf06a131d: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf06a131d, original_name='Unknown'
        ),
    })
    unknown_0x160abcfc: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x160abcfc, original_name='Unknown'
        ),
    })
    hyper_mode_duration_min: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4866df6c, original_name='HyperModeDurationMin'
        ),
    })
    hyper_mode_duration_max: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xae06708d, original_name='HyperModeDurationMax'
        ),
    })
    hyper_mode_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xc8a1eac8, original_name='HyperModeVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    unknown_0x95e7a2c2: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x95e7a2c2, original_name='Unknown'
        ),
    })
    unknown_0x76ba1c18: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x76ba1c18, original_name='Unknown'
        ),
    })
    unknown_0x64d482d5: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0x64d482d5, original_name='Unknown'
        ),
    })
    unknown_0xc3e002ac: int = dataclasses.field(default=7, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc3e002ac, original_name='Unknown'
        ),
    })
    unknown_0x77b6541c: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x77b6541c, original_name='Unknown'
        ),
    })
    unknown_0x9c889645: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9c889645, original_name='Unknown'
        ),
    })
    launch_projectile_data: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x11473c13, original_name='LaunchProjectileData', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
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
        if property_count != 15:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf04452f3
        hyper_mode_check_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc8e312dd
        unknown_0xc8e312dd = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2e83bd3c
        unknown_0x2e83bd3c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf06a131d
        unknown_0xf06a131d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x160abcfc
        unknown_0x160abcfc = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4866df6c
        hyper_mode_duration_min = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xae06708d
        hyper_mode_duration_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc8a1eac8
        hyper_mode_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95e7a2c2
        unknown_0x95e7a2c2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x76ba1c18
        unknown_0x76ba1c18 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x64d482d5
        unknown_0x64d482d5 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3e002ac
        unknown_0xc3e002ac = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x77b6541c
        unknown_0x77b6541c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9c889645
        unknown_0x9c889645 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x11473c13
        launch_projectile_data = LaunchProjectileData.from_stream(data, property_size)
    
        return cls(hyper_mode_check_chance, unknown_0xc8e312dd, unknown_0x2e83bd3c, unknown_0xf06a131d, unknown_0x160abcfc, hyper_mode_duration_min, hyper_mode_duration_max, hyper_mode_vulnerability, unknown_0x95e7a2c2, unknown_0x76ba1c18, unknown_0x64d482d5, unknown_0xc3e002ac, unknown_0x77b6541c, unknown_0x9c889645, launch_projectile_data)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0f')  # 15 properties

        data.write(b'\xf0DR\xf3')  # 0xf04452f3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hyper_mode_check_chance))

        data.write(b'\xc8\xe3\x12\xdd')  # 0xc8e312dd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc8e312dd))

        data.write(b'.\x83\xbd<')  # 0x2e83bd3c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2e83bd3c))

        data.write(b'\xf0j\x13\x1d')  # 0xf06a131d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf06a131d))

        data.write(b'\x16\n\xbc\xfc')  # 0x160abcfc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x160abcfc))

        data.write(b'Hf\xdfl')  # 0x4866df6c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hyper_mode_duration_min))

        data.write(b'\xae\x06p\x8d')  # 0xae06708d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hyper_mode_duration_max))

        data.write(b'\xc8\xa1\xea\xc8')  # 0xc8a1eac8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hyper_mode_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x95\xe7\xa2\xc2')  # 0x95e7a2c2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x95e7a2c2))

        data.write(b'v\xba\x1c\x18')  # 0x76ba1c18
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x76ba1c18))

        data.write(b'd\xd4\x82\xd5')  # 0x64d482d5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x64d482d5))

        data.write(b'\xc3\xe0\x02\xac')  # 0xc3e002ac
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xc3e002ac))

        data.write(b'w\xb6T\x1c')  # 0x77b6541c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x77b6541c))

        data.write(b'\x9c\x88\x96E')  # 0x9c889645
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9c889645))

        data.write(b'\x11G<\x13')  # 0x11473c13
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.launch_projectile_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("EyePodStructJson", data)
        return cls(
            hyper_mode_check_chance=json_data['hyper_mode_check_chance'],
            unknown_0xc8e312dd=json_data['unknown_0xc8e312dd'],
            unknown_0x2e83bd3c=json_data['unknown_0x2e83bd3c'],
            unknown_0xf06a131d=json_data['unknown_0xf06a131d'],
            unknown_0x160abcfc=json_data['unknown_0x160abcfc'],
            hyper_mode_duration_min=json_data['hyper_mode_duration_min'],
            hyper_mode_duration_max=json_data['hyper_mode_duration_max'],
            hyper_mode_vulnerability=DamageVulnerability.from_json(json_data['hyper_mode_vulnerability']),
            unknown_0x95e7a2c2=json_data['unknown_0x95e7a2c2'],
            unknown_0x76ba1c18=json_data['unknown_0x76ba1c18'],
            unknown_0x64d482d5=json_data['unknown_0x64d482d5'],
            unknown_0xc3e002ac=json_data['unknown_0xc3e002ac'],
            unknown_0x77b6541c=json_data['unknown_0x77b6541c'],
            unknown_0x9c889645=json_data['unknown_0x9c889645'],
            launch_projectile_data=LaunchProjectileData.from_json(json_data['launch_projectile_data']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'hyper_mode_check_chance': self.hyper_mode_check_chance,
            'unknown_0xc8e312dd': self.unknown_0xc8e312dd,
            'unknown_0x2e83bd3c': self.unknown_0x2e83bd3c,
            'unknown_0xf06a131d': self.unknown_0xf06a131d,
            'unknown_0x160abcfc': self.unknown_0x160abcfc,
            'hyper_mode_duration_min': self.hyper_mode_duration_min,
            'hyper_mode_duration_max': self.hyper_mode_duration_max,
            'hyper_mode_vulnerability': self.hyper_mode_vulnerability.to_json(),
            'unknown_0x95e7a2c2': self.unknown_0x95e7a2c2,
            'unknown_0x76ba1c18': self.unknown_0x76ba1c18,
            'unknown_0x64d482d5': self.unknown_0x64d482d5,
            'unknown_0xc3e002ac': self.unknown_0xc3e002ac,
            'unknown_0x77b6541c': self.unknown_0x77b6541c,
            'unknown_0x9c889645': self.unknown_0x9c889645,
            'launch_projectile_data': self.launch_projectile_data.to_json(),
        }


def _decode_hyper_mode_check_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc8e312dd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2e83bd3c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf06a131d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x160abcfc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hyper_mode_duration_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hyper_mode_duration_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x95e7a2c2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x76ba1c18(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x64d482d5(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xc3e002ac(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x77b6541c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9c889645(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xf04452f3: ('hyper_mode_check_chance', _decode_hyper_mode_check_chance),
    0xc8e312dd: ('unknown_0xc8e312dd', _decode_unknown_0xc8e312dd),
    0x2e83bd3c: ('unknown_0x2e83bd3c', _decode_unknown_0x2e83bd3c),
    0xf06a131d: ('unknown_0xf06a131d', _decode_unknown_0xf06a131d),
    0x160abcfc: ('unknown_0x160abcfc', _decode_unknown_0x160abcfc),
    0x4866df6c: ('hyper_mode_duration_min', _decode_hyper_mode_duration_min),
    0xae06708d: ('hyper_mode_duration_max', _decode_hyper_mode_duration_max),
    0xc8a1eac8: ('hyper_mode_vulnerability', DamageVulnerability.from_stream),
    0x95e7a2c2: ('unknown_0x95e7a2c2', _decode_unknown_0x95e7a2c2),
    0x76ba1c18: ('unknown_0x76ba1c18', _decode_unknown_0x76ba1c18),
    0x64d482d5: ('unknown_0x64d482d5', _decode_unknown_0x64d482d5),
    0xc3e002ac: ('unknown_0xc3e002ac', _decode_unknown_0xc3e002ac),
    0x77b6541c: ('unknown_0x77b6541c', _decode_unknown_0x77b6541c),
    0x9c889645: ('unknown_0x9c889645', _decode_unknown_0x9c889645),
    0x11473c13: ('launch_projectile_data', LaunchProjectileData.from_stream),
}
