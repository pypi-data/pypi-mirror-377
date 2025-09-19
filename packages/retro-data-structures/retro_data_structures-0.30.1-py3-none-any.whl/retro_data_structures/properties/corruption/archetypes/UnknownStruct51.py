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
from retro_data_structures.properties.corruption.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.corruption.archetypes.LaunchProjectileData import LaunchProjectileData
from retro_data_structures.properties.corruption.archetypes.UnknownStruct50 import UnknownStruct50
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct51Json(typing_extensions.TypedDict):
        unknown_0xdbd7b020: bool
        unknown_0xf8ec7014: bool
        anti_drain_time: float
        unknown_0x363f4a77: float
        is_orbitable: bool
        hover_speed: float
        attack_delay_time: float
        unknown_0x5a426481: float
        unknown_0x3b846868: float
        unknown_0x809644dc: float
        phazon_drain_amount: float
        unknown_0x0d522c38: float
        launch_projectile_data: json_util.JsonObject
        phazon_drain_visor_effect: int
        unknown_struct50: json_util.JsonObject
        normal_electric_damage_info: json_util.JsonObject
        part_0x934e82b5: int
        starts_prevent_effect: int
        part_0xf13facaf: int
        turn_sound: int
    

@dataclasses.dataclass()
class UnknownStruct51(BaseProperty):
    unknown_0xdbd7b020: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xdbd7b020, original_name='Unknown'
        ),
    })
    unknown_0xf8ec7014: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf8ec7014, original_name='Unknown'
        ),
    })
    anti_drain_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x48d9482b, original_name='AntiDrainTime'
        ),
    })
    unknown_0x363f4a77: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x363f4a77, original_name='Unknown'
        ),
    })
    is_orbitable: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x826bec80, original_name='IsOrbitable'
        ),
    })
    hover_speed: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x845ef489, original_name='HoverSpeed'
        ),
    })
    attack_delay_time: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2b8130b7, original_name='AttackDelayTime'
        ),
    })
    unknown_0x5a426481: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5a426481, original_name='Unknown'
        ),
    })
    unknown_0x3b846868: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3b846868, original_name='Unknown'
        ),
    })
    unknown_0x809644dc: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x809644dc, original_name='Unknown'
        ),
    })
    phazon_drain_amount: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x03336d49, original_name='PhazonDrainAmount'
        ),
    })
    unknown_0x0d522c38: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0d522c38, original_name='Unknown'
        ),
    })
    launch_projectile_data: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x50ae6e55, original_name='LaunchProjectileData', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    phazon_drain_visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x7518cd46, original_name='PhazonDrainVisorEffect'
        ),
    })
    unknown_struct50: UnknownStruct50 = dataclasses.field(default_factory=UnknownStruct50, metadata={
        'reflection': FieldReflection[UnknownStruct50](
            UnknownStruct50, id=0x979d0cfa, original_name='UnknownStruct50', from_json=UnknownStruct50.from_json, to_json=UnknownStruct50.to_json
        ),
    })
    normal_electric_damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x62ac6915, original_name='NormalElectricDamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    part_0x934e82b5: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x934e82b5, original_name='PART'
        ),
    })
    starts_prevent_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x221a902d, original_name='StartsPreventEffect'
        ),
    })
    part_0xf13facaf: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf13facaf, original_name='PART'
        ),
    })
    turn_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc4c39403, original_name='TurnSound'
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
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdbd7b020
        unknown_0xdbd7b020 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf8ec7014
        unknown_0xf8ec7014 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x48d9482b
        anti_drain_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x363f4a77
        unknown_0x363f4a77 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x826bec80
        is_orbitable = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x845ef489
        hover_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b8130b7
        attack_delay_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5a426481
        unknown_0x5a426481 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3b846868
        unknown_0x3b846868 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x809644dc
        unknown_0x809644dc = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x03336d49
        phazon_drain_amount = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d522c38
        unknown_0x0d522c38 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x50ae6e55
        launch_projectile_data = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7518cd46
        phazon_drain_visor_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x979d0cfa
        unknown_struct50 = UnknownStruct50.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x62ac6915
        normal_electric_damage_info = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x934e82b5
        part_0x934e82b5 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x221a902d
        starts_prevent_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf13facaf
        part_0xf13facaf = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc4c39403
        turn_sound = struct.unpack(">Q", data.read(8))[0]
    
        return cls(unknown_0xdbd7b020, unknown_0xf8ec7014, anti_drain_time, unknown_0x363f4a77, is_orbitable, hover_speed, attack_delay_time, unknown_0x5a426481, unknown_0x3b846868, unknown_0x809644dc, phazon_drain_amount, unknown_0x0d522c38, launch_projectile_data, phazon_drain_visor_effect, unknown_struct50, normal_electric_damage_info, part_0x934e82b5, starts_prevent_effect, part_0xf13facaf, turn_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x14')  # 20 properties

        data.write(b'\xdb\xd7\xb0 ')  # 0xdbd7b020
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xdbd7b020))

        data.write(b'\xf8\xecp\x14')  # 0xf8ec7014
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xf8ec7014))

        data.write(b'H\xd9H+')  # 0x48d9482b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.anti_drain_time))

        data.write(b'6?Jw')  # 0x363f4a77
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x363f4a77))

        data.write(b'\x82k\xec\x80')  # 0x826bec80
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_orbitable))

        data.write(b'\x84^\xf4\x89')  # 0x845ef489
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_speed))

        data.write(b'+\x810\xb7')  # 0x2b8130b7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_delay_time))

        data.write(b'ZBd\x81')  # 0x5a426481
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5a426481))

        data.write(b';\x84hh')  # 0x3b846868
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3b846868))

        data.write(b'\x80\x96D\xdc')  # 0x809644dc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x809644dc))

        data.write(b'\x033mI')  # 0x3336d49
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.phazon_drain_amount))

        data.write(b'\rR,8')  # 0xd522c38
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0d522c38))

        data.write(b'P\xaenU')  # 0x50ae6e55
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.launch_projectile_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'u\x18\xcdF')  # 0x7518cd46
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.phazon_drain_visor_effect))

        data.write(b'\x97\x9d\x0c\xfa')  # 0x979d0cfa
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct50.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'b\xaci\x15')  # 0x62ac6915
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.normal_electric_damage_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x93N\x82\xb5')  # 0x934e82b5
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x934e82b5))

        data.write(b'"\x1a\x90-')  # 0x221a902d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.starts_prevent_effect))

        data.write(b'\xf1?\xac\xaf')  # 0xf13facaf
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0xf13facaf))

        data.write(b'\xc4\xc3\x94\x03')  # 0xc4c39403
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.turn_sound))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct51Json", data)
        return cls(
            unknown_0xdbd7b020=json_data['unknown_0xdbd7b020'],
            unknown_0xf8ec7014=json_data['unknown_0xf8ec7014'],
            anti_drain_time=json_data['anti_drain_time'],
            unknown_0x363f4a77=json_data['unknown_0x363f4a77'],
            is_orbitable=json_data['is_orbitable'],
            hover_speed=json_data['hover_speed'],
            attack_delay_time=json_data['attack_delay_time'],
            unknown_0x5a426481=json_data['unknown_0x5a426481'],
            unknown_0x3b846868=json_data['unknown_0x3b846868'],
            unknown_0x809644dc=json_data['unknown_0x809644dc'],
            phazon_drain_amount=json_data['phazon_drain_amount'],
            unknown_0x0d522c38=json_data['unknown_0x0d522c38'],
            launch_projectile_data=LaunchProjectileData.from_json(json_data['launch_projectile_data']),
            phazon_drain_visor_effect=json_data['phazon_drain_visor_effect'],
            unknown_struct50=UnknownStruct50.from_json(json_data['unknown_struct50']),
            normal_electric_damage_info=DamageInfo.from_json(json_data['normal_electric_damage_info']),
            part_0x934e82b5=json_data['part_0x934e82b5'],
            starts_prevent_effect=json_data['starts_prevent_effect'],
            part_0xf13facaf=json_data['part_0xf13facaf'],
            turn_sound=json_data['turn_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xdbd7b020': self.unknown_0xdbd7b020,
            'unknown_0xf8ec7014': self.unknown_0xf8ec7014,
            'anti_drain_time': self.anti_drain_time,
            'unknown_0x363f4a77': self.unknown_0x363f4a77,
            'is_orbitable': self.is_orbitable,
            'hover_speed': self.hover_speed,
            'attack_delay_time': self.attack_delay_time,
            'unknown_0x5a426481': self.unknown_0x5a426481,
            'unknown_0x3b846868': self.unknown_0x3b846868,
            'unknown_0x809644dc': self.unknown_0x809644dc,
            'phazon_drain_amount': self.phazon_drain_amount,
            'unknown_0x0d522c38': self.unknown_0x0d522c38,
            'launch_projectile_data': self.launch_projectile_data.to_json(),
            'phazon_drain_visor_effect': self.phazon_drain_visor_effect,
            'unknown_struct50': self.unknown_struct50.to_json(),
            'normal_electric_damage_info': self.normal_electric_damage_info.to_json(),
            'part_0x934e82b5': self.part_0x934e82b5,
            'starts_prevent_effect': self.starts_prevent_effect,
            'part_0xf13facaf': self.part_0xf13facaf,
            'turn_sound': self.turn_sound,
        }


def _decode_unknown_0xdbd7b020(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xf8ec7014(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_anti_drain_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x363f4a77(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_is_orbitable(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_hover_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_delay_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5a426481(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3b846868(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x809644dc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_phazon_drain_amount(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0d522c38(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_phazon_drain_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x934e82b5(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_starts_prevent_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0xf13facaf(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_turn_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xdbd7b020: ('unknown_0xdbd7b020', _decode_unknown_0xdbd7b020),
    0xf8ec7014: ('unknown_0xf8ec7014', _decode_unknown_0xf8ec7014),
    0x48d9482b: ('anti_drain_time', _decode_anti_drain_time),
    0x363f4a77: ('unknown_0x363f4a77', _decode_unknown_0x363f4a77),
    0x826bec80: ('is_orbitable', _decode_is_orbitable),
    0x845ef489: ('hover_speed', _decode_hover_speed),
    0x2b8130b7: ('attack_delay_time', _decode_attack_delay_time),
    0x5a426481: ('unknown_0x5a426481', _decode_unknown_0x5a426481),
    0x3b846868: ('unknown_0x3b846868', _decode_unknown_0x3b846868),
    0x809644dc: ('unknown_0x809644dc', _decode_unknown_0x809644dc),
    0x3336d49: ('phazon_drain_amount', _decode_phazon_drain_amount),
    0xd522c38: ('unknown_0x0d522c38', _decode_unknown_0x0d522c38),
    0x50ae6e55: ('launch_projectile_data', LaunchProjectileData.from_stream),
    0x7518cd46: ('phazon_drain_visor_effect', _decode_phazon_drain_visor_effect),
    0x979d0cfa: ('unknown_struct50', UnknownStruct50.from_stream),
    0x62ac6915: ('normal_electric_damage_info', DamageInfo.from_stream),
    0x934e82b5: ('part_0x934e82b5', _decode_part_0x934e82b5),
    0x221a902d: ('starts_prevent_effect', _decode_starts_prevent_effect),
    0xf13facaf: ('part_0xf13facaf', _decode_part_0xf13facaf),
    0xc4c39403: ('turn_sound', _decode_turn_sound),
}
