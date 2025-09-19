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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class ElectricBeamInfoJson(typing_extensions.TypedDict):
        beam_weapon: int
        beam_projectile: int
        beam_visor_effect: int
        beam_visor_sound: int
        visor_effect_delay: float
        beam_damage_info: json_util.JsonObject
        length: float
        radius: float
        travel_speed: float
        contact_effect: int
        fade_time: float
        damage_delay: float
    

@dataclasses.dataclass()
class ElectricBeamInfo(BaseProperty):
    beam_weapon: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2d39450e, original_name='BeamWeapon'
        ),
    })
    beam_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1c5687cc, original_name='BeamProjectile'
        ),
    })
    beam_visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc95479d4, original_name='BeamVisorEffect'
        ),
    })
    beam_visor_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x174455ba, original_name='BeamVisorSound'
        ),
    })
    visor_effect_delay: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x104284e6, original_name='VisorEffectDelay'
        ),
    })
    beam_damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x98821996, original_name='BeamDamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    length: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc26c291c, original_name='Length'
        ),
    })
    radius: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x78c507eb, original_name='Radius'
        ),
    })
    travel_speed: float = dataclasses.field(default=150.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3fed5e52, original_name='TravelSpeed'
        ),
    })
    contact_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4f387c49, original_name='ContactEffect'
        ),
    })
    fade_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd4124c4c, original_name='FadeTime'
        ),
    })
    damage_delay: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8f4fb79d, original_name='DamageDelay'
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
        if property_count != 12:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2d39450e
        beam_weapon = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1c5687cc
        beam_projectile = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc95479d4
        beam_visor_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x174455ba
        beam_visor_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x104284e6
        visor_effect_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x98821996
        beam_damage_info = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc26c291c
        length = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x78c507eb
        radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3fed5e52
        travel_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4f387c49
        contact_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd4124c4c
        fade_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f4fb79d
        damage_delay = struct.unpack('>f', data.read(4))[0]
    
        return cls(beam_weapon, beam_projectile, beam_visor_effect, beam_visor_sound, visor_effect_delay, beam_damage_info, length, radius, travel_speed, contact_effect, fade_time, damage_delay)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        num_properties_offset = data.tell()
        data.write(b'\x00\x06')  # 6 properties
        num_properties_written = 6

        data.write(b'-9E\x0e')  # 0x2d39450e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.beam_weapon))

        if self.beam_projectile != default_override.get('beam_projectile', default_asset_id):
            num_properties_written += 1
            data.write(b'\x1cV\x87\xcc')  # 0x1c5687cc
            data.write(b'\x00\x08')  # size
            data.write(struct.pack(">Q", self.beam_projectile))

        data.write(b'\xc9Ty\xd4')  # 0xc95479d4
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.beam_visor_effect))

        data.write(b'\x17DU\xba')  # 0x174455ba
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.beam_visor_sound))

        data.write(b'\x10B\x84\xe6')  # 0x104284e6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.visor_effect_delay))

        data.write(b'\x98\x82\x19\x96')  # 0x98821996
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.beam_damage_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        if self.length != default_override.get('length', 10.0):
            num_properties_written += 1
            data.write(b'\xc2l)\x1c')  # 0xc26c291c
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>f', self.length))

        if self.radius != default_override.get('radius', 0.10000000149011612):
            num_properties_written += 1
            data.write(b'x\xc5\x07\xeb')  # 0x78c507eb
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>f', self.radius))

        if self.travel_speed != default_override.get('travel_speed', 150.0):
            num_properties_written += 1
            data.write(b'?\xed^R')  # 0x3fed5e52
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>f', self.travel_speed))

        if self.contact_effect != default_override.get('contact_effect', default_asset_id):
            num_properties_written += 1
            data.write(b'O8|I')  # 0x4f387c49
            data.write(b'\x00\x08')  # size
            data.write(struct.pack(">Q", self.contact_effect))

        if self.fade_time != default_override.get('fade_time', 1.0):
            num_properties_written += 1
            data.write(b'\xd4\x12LL')  # 0xd4124c4c
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>f', self.fade_time))

        data.write(b'\x8fO\xb7\x9d')  # 0x8f4fb79d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.damage_delay))

        if num_properties_written != 6:
            struct_end_offset = data.tell()
            data.seek(num_properties_offset)
            data.write(struct.pack(">H", num_properties_written))
            data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ElectricBeamInfoJson", data)
        return cls(
            beam_weapon=json_data['beam_weapon'],
            beam_projectile=json_data['beam_projectile'],
            beam_visor_effect=json_data['beam_visor_effect'],
            beam_visor_sound=json_data['beam_visor_sound'],
            visor_effect_delay=json_data['visor_effect_delay'],
            beam_damage_info=DamageInfo.from_json(json_data['beam_damage_info']),
            length=json_data['length'],
            radius=json_data['radius'],
            travel_speed=json_data['travel_speed'],
            contact_effect=json_data['contact_effect'],
            fade_time=json_data['fade_time'],
            damage_delay=json_data['damage_delay'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'beam_weapon': self.beam_weapon,
            'beam_projectile': self.beam_projectile,
            'beam_visor_effect': self.beam_visor_effect,
            'beam_visor_sound': self.beam_visor_sound,
            'visor_effect_delay': self.visor_effect_delay,
            'beam_damage_info': self.beam_damage_info.to_json(),
            'length': self.length,
            'radius': self.radius,
            'travel_speed': self.travel_speed,
            'contact_effect': self.contact_effect,
            'fade_time': self.fade_time,
            'damage_delay': self.damage_delay,
        }


def _decode_beam_weapon(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_beam_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_beam_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_beam_visor_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_visor_effect_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_length(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_travel_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_contact_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_fade_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_damage_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x2d39450e: ('beam_weapon', _decode_beam_weapon),
    0x1c5687cc: ('beam_projectile', _decode_beam_projectile),
    0xc95479d4: ('beam_visor_effect', _decode_beam_visor_effect),
    0x174455ba: ('beam_visor_sound', _decode_beam_visor_sound),
    0x104284e6: ('visor_effect_delay', _decode_visor_effect_delay),
    0x98821996: ('beam_damage_info', DamageInfo.from_stream),
    0xc26c291c: ('length', _decode_length),
    0x78c507eb: ('radius', _decode_radius),
    0x3fed5e52: ('travel_speed', _decode_travel_speed),
    0x4f387c49: ('contact_effect', _decode_contact_effect),
    0xd4124c4c: ('fade_time', _decode_fade_time),
    0x8f4fb79d: ('damage_delay', _decode_damage_delay),
}
