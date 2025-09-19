# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class PlayerTurretJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        flags_player_turret: int
        unknown_0x17cd8b2a: float
        unknown_0x1473dad2: float
        unknown_0x3650ce75: float
        unknown_0x78520e6e: float
        damage_angle: float
        horiz_speed: float
        vert_speed: float
        fire_rate: float
        weapon_damage: json_util.JsonObject
        weapon_effect: int
        wpsc: int
        unknown_0xe7234f72: int
        unknown_0x3e2f7afb: int
        unknown_0x7cabd1f1: int
        unknown_0x7ef976eb: int
        unknown_0x035459fd: int
    

@dataclasses.dataclass()
class PlayerTurret(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    flags_player_turret: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0xeeadefa6, original_name='FlagsPlayerTurret'
        ),
    })
    unknown_0x17cd8b2a: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x17cd8b2a, original_name='Unknown'
        ),
    })
    unknown_0x1473dad2: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1473dad2, original_name='Unknown'
        ),
    })
    unknown_0x3650ce75: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3650ce75, original_name='Unknown'
        ),
    })
    unknown_0x78520e6e: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x78520e6e, original_name='Unknown'
        ),
    })
    damage_angle: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa39a5d72, original_name='DamageAngle'
        ),
    })
    horiz_speed: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfb2e32db, original_name='HorizSpeed'
        ),
    })
    vert_speed: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1b3c8683, original_name='VertSpeed'
        ),
    })
    fire_rate: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc6e48f18, original_name='FireRate'
        ),
    })
    weapon_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x8e5f7e96, original_name='WeaponDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    weapon_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc43360a7, original_name='WeaponEffect'
        ),
    })
    wpsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa99d3dbe, original_name='WPSC'
        ),
    })
    unknown_0xe7234f72: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xe7234f72, original_name='Unknown'
        ),
    })
    unknown_0x3e2f7afb: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x3e2f7afb, original_name='Unknown'
        ),
    })
    unknown_0x7cabd1f1: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x7cabd1f1, original_name='Unknown'
        ),
    })
    unknown_0x7ef976eb: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x7ef976eb, original_name='Unknown'
        ),
    })
    unknown_0x035459fd: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x035459fd, original_name='Unknown'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'PLRT'

    @classmethod
    def modules(cls) -> list[str]:
        return ['ScriptPlayerTurret.rel']

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
        if property_count != 18:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeeadefa6
        flags_player_turret = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x17cd8b2a
        unknown_0x17cd8b2a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1473dad2
        unknown_0x1473dad2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3650ce75
        unknown_0x3650ce75 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x78520e6e
        unknown_0x78520e6e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa39a5d72
        damage_angle = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfb2e32db
        horiz_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b3c8683
        vert_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6e48f18
        fire_rate = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8e5f7e96
        weapon_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc43360a7
        weapon_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa99d3dbe
        wpsc = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe7234f72
        unknown_0xe7234f72 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3e2f7afb
        unknown_0x3e2f7afb = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7cabd1f1
        unknown_0x7cabd1f1 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7ef976eb
        unknown_0x7ef976eb = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x035459fd
        unknown_0x035459fd = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, flags_player_turret, unknown_0x17cd8b2a, unknown_0x1473dad2, unknown_0x3650ce75, unknown_0x78520e6e, damage_angle, horiz_speed, vert_speed, fire_rate, weapon_damage, weapon_effect, wpsc, unknown_0xe7234f72, unknown_0x3e2f7afb, unknown_0x7cabd1f1, unknown_0x7ef976eb, unknown_0x035459fd)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x12')  # 18 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xee\xad\xef\xa6')  # 0xeeadefa6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.flags_player_turret))

        data.write(b'\x17\xcd\x8b*')  # 0x17cd8b2a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x17cd8b2a))

        data.write(b'\x14s\xda\xd2')  # 0x1473dad2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1473dad2))

        data.write(b'6P\xceu')  # 0x3650ce75
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3650ce75))

        data.write(b'xR\x0en')  # 0x78520e6e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x78520e6e))

        data.write(b'\xa3\x9a]r')  # 0xa39a5d72
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.damage_angle))

        data.write(b'\xfb.2\xdb')  # 0xfb2e32db
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.horiz_speed))

        data.write(b'\x1b<\x86\x83')  # 0x1b3c8683
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.vert_speed))

        data.write(b'\xc6\xe4\x8f\x18')  # 0xc6e48f18
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fire_rate))

        data.write(b'\x8e_~\x96')  # 0x8e5f7e96
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.weapon_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc43`\xa7')  # 0xc43360a7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.weapon_effect))

        data.write(b'\xa9\x9d=\xbe')  # 0xa99d3dbe
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.wpsc))

        data.write(b'\xe7#Or')  # 0xe7234f72
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xe7234f72))

        data.write(b'>/z\xfb')  # 0x3e2f7afb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x3e2f7afb))

        data.write(b'|\xab\xd1\xf1')  # 0x7cabd1f1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x7cabd1f1))

        data.write(b'~\xf9v\xeb')  # 0x7ef976eb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x7ef976eb))

        data.write(b'\x03TY\xfd')  # 0x35459fd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x035459fd))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PlayerTurretJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            flags_player_turret=json_data['flags_player_turret'],
            unknown_0x17cd8b2a=json_data['unknown_0x17cd8b2a'],
            unknown_0x1473dad2=json_data['unknown_0x1473dad2'],
            unknown_0x3650ce75=json_data['unknown_0x3650ce75'],
            unknown_0x78520e6e=json_data['unknown_0x78520e6e'],
            damage_angle=json_data['damage_angle'],
            horiz_speed=json_data['horiz_speed'],
            vert_speed=json_data['vert_speed'],
            fire_rate=json_data['fire_rate'],
            weapon_damage=DamageInfo.from_json(json_data['weapon_damage']),
            weapon_effect=json_data['weapon_effect'],
            wpsc=json_data['wpsc'],
            unknown_0xe7234f72=json_data['unknown_0xe7234f72'],
            unknown_0x3e2f7afb=json_data['unknown_0x3e2f7afb'],
            unknown_0x7cabd1f1=json_data['unknown_0x7cabd1f1'],
            unknown_0x7ef976eb=json_data['unknown_0x7ef976eb'],
            unknown_0x035459fd=json_data['unknown_0x035459fd'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'flags_player_turret': self.flags_player_turret,
            'unknown_0x17cd8b2a': self.unknown_0x17cd8b2a,
            'unknown_0x1473dad2': self.unknown_0x1473dad2,
            'unknown_0x3650ce75': self.unknown_0x3650ce75,
            'unknown_0x78520e6e': self.unknown_0x78520e6e,
            'damage_angle': self.damage_angle,
            'horiz_speed': self.horiz_speed,
            'vert_speed': self.vert_speed,
            'fire_rate': self.fire_rate,
            'weapon_damage': self.weapon_damage.to_json(),
            'weapon_effect': self.weapon_effect,
            'wpsc': self.wpsc,
            'unknown_0xe7234f72': self.unknown_0xe7234f72,
            'unknown_0x3e2f7afb': self.unknown_0x3e2f7afb,
            'unknown_0x7cabd1f1': self.unknown_0x7cabd1f1,
            'unknown_0x7ef976eb': self.unknown_0x7ef976eb,
            'unknown_0x035459fd': self.unknown_0x035459fd,
        }

    def _dependencies_for_weapon_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.weapon_effect)

    def _dependencies_for_wpsc(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc)

    def _dependencies_for_unknown_0xe7234f72(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_0xe7234f72)

    def _dependencies_for_unknown_0x3e2f7afb(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_0x3e2f7afb)

    def _dependencies_for_unknown_0x7cabd1f1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_0x7cabd1f1)

    def _dependencies_for_unknown_0x7ef976eb(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_0x7ef976eb)

    def _dependencies_for_unknown_0x035459fd(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_0x035459fd)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.weapon_damage.dependencies_for, "weapon_damage", "DamageInfo"),
            (self._dependencies_for_weapon_effect, "weapon_effect", "AssetId"),
            (self._dependencies_for_wpsc, "wpsc", "AssetId"),
            (self._dependencies_for_unknown_0xe7234f72, "unknown_0xe7234f72", "int"),
            (self._dependencies_for_unknown_0x3e2f7afb, "unknown_0x3e2f7afb", "int"),
            (self._dependencies_for_unknown_0x7cabd1f1, "unknown_0x7cabd1f1", "int"),
            (self._dependencies_for_unknown_0x7ef976eb, "unknown_0x7ef976eb", "int"),
            (self._dependencies_for_unknown_0x035459fd, "unknown_0x035459fd", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for PlayerTurret.{field_name} ({field_type}): {e}"
                )


def _decode_flags_player_turret(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x17cd8b2a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1473dad2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3650ce75(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x78520e6e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_damage_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_horiz_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_vert_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fire_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_weapon_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_wpsc(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0xe7234f72(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x3e2f7afb(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x7cabd1f1(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x7ef976eb(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x035459fd(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xeeadefa6: ('flags_player_turret', _decode_flags_player_turret),
    0x17cd8b2a: ('unknown_0x17cd8b2a', _decode_unknown_0x17cd8b2a),
    0x1473dad2: ('unknown_0x1473dad2', _decode_unknown_0x1473dad2),
    0x3650ce75: ('unknown_0x3650ce75', _decode_unknown_0x3650ce75),
    0x78520e6e: ('unknown_0x78520e6e', _decode_unknown_0x78520e6e),
    0xa39a5d72: ('damage_angle', _decode_damage_angle),
    0xfb2e32db: ('horiz_speed', _decode_horiz_speed),
    0x1b3c8683: ('vert_speed', _decode_vert_speed),
    0xc6e48f18: ('fire_rate', _decode_fire_rate),
    0x8e5f7e96: ('weapon_damage', DamageInfo.from_stream),
    0xc43360a7: ('weapon_effect', _decode_weapon_effect),
    0xa99d3dbe: ('wpsc', _decode_wpsc),
    0xe7234f72: ('unknown_0xe7234f72', _decode_unknown_0xe7234f72),
    0x3e2f7afb: ('unknown_0x3e2f7afb', _decode_unknown_0x3e2f7afb),
    0x7cabd1f1: ('unknown_0x7cabd1f1', _decode_unknown_0x7cabd1f1),
    0x7ef976eb: ('unknown_0x7ef976eb', _decode_unknown_0x7ef976eb),
    0x35459fd: ('unknown_0x035459fd', _decode_unknown_0x035459fd),
}
