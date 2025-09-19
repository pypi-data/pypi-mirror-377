# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.archetypes.RainProperties import RainProperties
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class AreaAttributesJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        need_sky: bool
        environment_effects: int
        rain_properties: json_util.JsonObject
        environment_group_sound: int
        density: float
        normal_lighting: float
        unknown_0x6dade808: float
        override_sky: int
        use_override_sky: bool
        unknown_0xe3426206: bool
        phazon_damage: int
        unknown_0x07b26bf9: bool
        unknown_0x46cc1b48: bool
        damage_spline: json_util.JsonObject
        environment_damage_info: json_util.JsonObject
    

class EnvironmentEffects(enum.IntEnum):
    Unknown1 = 4188577367
    Unknown2 = 2965060395
    Unknown3 = 829035573
    Unknown4 = 187254247
    Unknown5 = 1692838265
    Unknown6 = 2922967539

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


class PhazonDamage(enum.IntEnum):
    Unknown1 = 4044895378
    Unknown2 = 278612995
    Unknown3 = 306082665

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


@dataclasses.dataclass()
class AreaAttributes(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    need_sky: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x95d4bee7, original_name='NeedSky'
        ),
    })
    environment_effects: EnvironmentEffects = dataclasses.field(default=EnvironmentEffects.Unknown1, metadata={
        'reflection': FieldReflection[EnvironmentEffects](
            EnvironmentEffects, id=0xea2700e9, original_name='EnvironmentEffects', from_json=EnvironmentEffects.from_json, to_json=EnvironmentEffects.to_json
        ),
    })
    rain_properties: RainProperties = dataclasses.field(default_factory=RainProperties, metadata={
        'reflection': FieldReflection[RainProperties](
            RainProperties, id=0xce0328fa, original_name='RainProperties', from_json=RainProperties.from_json, to_json=RainProperties.to_json
        ),
    })
    environment_group_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x56263e35, original_name='EnvironmentGroupSound'
        ),
    })
    density: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x64e5fe9f, original_name='Density'
        ),
    })
    normal_lighting: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xba5f801e, original_name='NormalLighting'
        ),
    })
    unknown_0x6dade808: float = dataclasses.field(default=42.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6dade808, original_name='Unknown'
        ),
    })
    override_sky: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd208c9fa, original_name='OverrideSky'
        ),
    })
    use_override_sky: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x29445302, original_name='UseOverrideSky'
        ),
    })
    unknown_0xe3426206: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe3426206, original_name='Unknown'
        ),
    })
    phazon_damage: PhazonDamage = dataclasses.field(default=PhazonDamage.Unknown1, metadata={
        'reflection': FieldReflection[PhazonDamage](
            PhazonDamage, id=0x4e08b984, original_name='PhazonDamage', from_json=PhazonDamage.from_json, to_json=PhazonDamage.to_json
        ),
    })
    unknown_0x07b26bf9: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x07b26bf9, original_name='Unknown'
        ),
    })
    unknown_0x46cc1b48: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x46cc1b48, original_name='Unknown'
        ),
    })
    damage_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xfa873a67, original_name='DamageSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    environment_damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xe7a0e69b, original_name='EnvironmentDamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'REAA'

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        struct_id, size, property_count = struct.unpack(">LHH", data.read(8))
        assert struct_id == 0xFFFFFFFF
        root_size_start = data.tell() - 2

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

        assert data.tell() - root_size_start == size
        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 16:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95d4bee7
        need_sky = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xea2700e9
        environment_effects = EnvironmentEffects.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xce0328fa
        rain_properties = RainProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x56263e35
        environment_group_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x64e5fe9f
        density = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xba5f801e
        normal_lighting = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6dade808
        unknown_0x6dade808 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd208c9fa
        override_sky = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x29445302
        use_override_sky = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe3426206
        unknown_0xe3426206 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4e08b984
        phazon_damage = PhazonDamage.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x07b26bf9
        unknown_0x07b26bf9 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x46cc1b48
        unknown_0x46cc1b48 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfa873a67
        damage_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe7a0e69b
        environment_damage_info = DamageInfo.from_stream(data, property_size)
    
        return cls(editor_properties, need_sky, environment_effects, rain_properties, environment_group_sound, density, normal_lighting, unknown_0x6dade808, override_sky, use_override_sky, unknown_0xe3426206, phazon_damage, unknown_0x07b26bf9, unknown_0x46cc1b48, damage_spline, environment_damage_info)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x10')  # 16 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x95\xd4\xbe\xe7')  # 0x95d4bee7
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.need_sky))

        data.write(b"\xea'\x00\xe9")  # 0xea2700e9
        data.write(b'\x00\x04')  # size
        self.environment_effects.to_stream(data)

        data.write(b'\xce\x03(\xfa')  # 0xce0328fa
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.rain_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'V&>5')  # 0x56263e35
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.environment_group_sound))

        data.write(b'd\xe5\xfe\x9f')  # 0x64e5fe9f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.density))

        data.write(b'\xba_\x80\x1e')  # 0xba5f801e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.normal_lighting))

        data.write(b'm\xad\xe8\x08')  # 0x6dade808
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6dade808))

        data.write(b'\xd2\x08\xc9\xfa')  # 0xd208c9fa
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.override_sky))

        data.write(b')DS\x02')  # 0x29445302
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.use_override_sky))

        data.write(b'\xe3Bb\x06')  # 0xe3426206
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xe3426206))

        data.write(b'N\x08\xb9\x84')  # 0x4e08b984
        data.write(b'\x00\x04')  # size
        self.phazon_damage.to_stream(data)

        data.write(b'\x07\xb2k\xf9')  # 0x7b26bf9
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x07b26bf9))

        data.write(b'F\xcc\x1bH')  # 0x46cc1b48
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x46cc1b48))

        data.write(b'\xfa\x87:g')  # 0xfa873a67
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe7\xa0\xe6\x9b')  # 0xe7a0e69b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.environment_damage_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AreaAttributesJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            need_sky=json_data['need_sky'],
            environment_effects=EnvironmentEffects.from_json(json_data['environment_effects']),
            rain_properties=RainProperties.from_json(json_data['rain_properties']),
            environment_group_sound=json_data['environment_group_sound'],
            density=json_data['density'],
            normal_lighting=json_data['normal_lighting'],
            unknown_0x6dade808=json_data['unknown_0x6dade808'],
            override_sky=json_data['override_sky'],
            use_override_sky=json_data['use_override_sky'],
            unknown_0xe3426206=json_data['unknown_0xe3426206'],
            phazon_damage=PhazonDamage.from_json(json_data['phazon_damage']),
            unknown_0x07b26bf9=json_data['unknown_0x07b26bf9'],
            unknown_0x46cc1b48=json_data['unknown_0x46cc1b48'],
            damage_spline=Spline.from_json(json_data['damage_spline']),
            environment_damage_info=DamageInfo.from_json(json_data['environment_damage_info']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'need_sky': self.need_sky,
            'environment_effects': self.environment_effects.to_json(),
            'rain_properties': self.rain_properties.to_json(),
            'environment_group_sound': self.environment_group_sound,
            'density': self.density,
            'normal_lighting': self.normal_lighting,
            'unknown_0x6dade808': self.unknown_0x6dade808,
            'override_sky': self.override_sky,
            'use_override_sky': self.use_override_sky,
            'unknown_0xe3426206': self.unknown_0xe3426206,
            'phazon_damage': self.phazon_damage.to_json(),
            'unknown_0x07b26bf9': self.unknown_0x07b26bf9,
            'unknown_0x46cc1b48': self.unknown_0x46cc1b48,
            'damage_spline': self.damage_spline.to_json(),
            'environment_damage_info': self.environment_damage_info.to_json(),
        }


def _decode_need_sky(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_environment_effects(data: typing.BinaryIO, property_size: int) -> EnvironmentEffects:
    return EnvironmentEffects.from_stream(data)


def _decode_environment_group_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_density(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_normal_lighting(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6dade808(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_override_sky(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_use_override_sky(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xe3426206(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_phazon_damage(data: typing.BinaryIO, property_size: int) -> PhazonDamage:
    return PhazonDamage.from_stream(data)


def _decode_unknown_0x07b26bf9(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x46cc1b48(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x95d4bee7: ('need_sky', _decode_need_sky),
    0xea2700e9: ('environment_effects', _decode_environment_effects),
    0xce0328fa: ('rain_properties', RainProperties.from_stream),
    0x56263e35: ('environment_group_sound', _decode_environment_group_sound),
    0x64e5fe9f: ('density', _decode_density),
    0xba5f801e: ('normal_lighting', _decode_normal_lighting),
    0x6dade808: ('unknown_0x6dade808', _decode_unknown_0x6dade808),
    0xd208c9fa: ('override_sky', _decode_override_sky),
    0x29445302: ('use_override_sky', _decode_use_override_sky),
    0xe3426206: ('unknown_0xe3426206', _decode_unknown_0xe3426206),
    0x4e08b984: ('phazon_damage', _decode_phazon_damage),
    0x7b26bf9: ('unknown_0x07b26bf9', _decode_unknown_0x07b26bf9),
    0x46cc1b48: ('unknown_0x46cc1b48', _decode_unknown_0x46cc1b48),
    0xfa873a67: ('damage_spline', Spline.from_stream),
    0xe7a0e69b: ('environment_damage_info', DamageInfo.from_stream),
}
