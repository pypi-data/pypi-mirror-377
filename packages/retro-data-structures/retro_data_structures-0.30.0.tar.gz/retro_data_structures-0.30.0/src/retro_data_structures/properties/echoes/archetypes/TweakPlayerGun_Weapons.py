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
from retro_data_structures.properties.echoes.archetypes.TBeamInfo import TBeamInfo
from retro_data_structures.properties.echoes.archetypes.TDamageInfo import TDamageInfo

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakPlayerGun_WeaponsJson(typing_extensions.TypedDict):
        bomb: json_util.JsonObject
        unknown_0xe8907530: float
        unknown_0x0a9186cb: float
        power_bomb: json_util.JsonObject
        missile: json_util.JsonObject
        power_beam: json_util.JsonObject
        dark_beam: json_util.JsonObject
        dark_beam_blob: json_util.JsonObject
        light_beam: json_util.JsonObject
        annihilator_beam: json_util.JsonObject
        phazon_beam: json_util.JsonObject
    

@dataclasses.dataclass()
class TweakPlayerGun_Weapons(BaseProperty):
    bomb: TDamageInfo = dataclasses.field(default_factory=TDamageInfo, metadata={
        'reflection': FieldReflection[TDamageInfo](
            TDamageInfo, id=0x6173ad96, original_name='Bomb', from_json=TDamageInfo.from_json, to_json=TDamageInfo.to_json
        ),
    })
    unknown_0xe8907530: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe8907530, original_name='Unknown'
        ),
    })
    unknown_0x0a9186cb: float = dataclasses.field(default=0.6000000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0a9186cb, original_name='Unknown'
        ),
    })
    power_bomb: TDamageInfo = dataclasses.field(default_factory=TDamageInfo, metadata={
        'reflection': FieldReflection[TDamageInfo](
            TDamageInfo, id=0xdcc0c6fb, original_name='Power_Bomb', from_json=TDamageInfo.from_json, to_json=TDamageInfo.to_json
        ),
    })
    missile: TDamageInfo = dataclasses.field(default_factory=TDamageInfo, metadata={
        'reflection': FieldReflection[TDamageInfo](
            TDamageInfo, id=0x58f00b0a, original_name='Missile', from_json=TDamageInfo.from_json, to_json=TDamageInfo.to_json
        ),
    })
    power_beam: TBeamInfo = dataclasses.field(default_factory=TBeamInfo, metadata={
        'reflection': FieldReflection[TBeamInfo](
            TBeamInfo, id=0x1f6c1a6b, original_name='Power_Beam', from_json=TBeamInfo.from_json, to_json=TBeamInfo.to_json
        ),
    })
    dark_beam: TBeamInfo = dataclasses.field(default_factory=TBeamInfo, metadata={
        'reflection': FieldReflection[TBeamInfo](
            TBeamInfo, id=0xc50f608b, original_name='Dark_Beam', from_json=TBeamInfo.from_json, to_json=TBeamInfo.to_json
        ),
    })
    dark_beam_blob: TDamageInfo = dataclasses.field(default_factory=TDamageInfo, metadata={
        'reflection': FieldReflection[TDamageInfo](
            TDamageInfo, id=0x059dce11, original_name='Dark_Beam_Blob', from_json=TDamageInfo.from_json, to_json=TDamageInfo.to_json
        ),
    })
    light_beam: TBeamInfo = dataclasses.field(default_factory=TBeamInfo, metadata={
        'reflection': FieldReflection[TBeamInfo](
            TBeamInfo, id=0xde7a8255, original_name='Light_Beam', from_json=TBeamInfo.from_json, to_json=TBeamInfo.to_json
        ),
    })
    annihilator_beam: TBeamInfo = dataclasses.field(default_factory=TBeamInfo, metadata={
        'reflection': FieldReflection[TBeamInfo](
            TBeamInfo, id=0x74b9b983, original_name='Annihilator_Beam', from_json=TBeamInfo.from_json, to_json=TBeamInfo.to_json
        ),
    })
    phazon_beam: TBeamInfo = dataclasses.field(default_factory=TBeamInfo, metadata={
        'reflection': FieldReflection[TBeamInfo](
            TBeamInfo, id=0xdd5f2e3d, original_name='Phazon_Beam', from_json=TBeamInfo.from_json, to_json=TBeamInfo.to_json
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
        if property_count != 11:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6173ad96
        bomb = TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 4, 'radius_damage_amount': 10.0, 'damage_radius': 3.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8907530
        unknown_0xe8907530 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0a9186cb
        unknown_0x0a9186cb = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdcc0c6fb
        power_bomb = TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 5, 'damage_amount': 100.0, 'radius_damage_amount': 50.0, 'damage_radius': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x58f00b0a
        missile = TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 6, 'damage_amount': 30.0, 'radius_damage_amount': 15.0, 'damage_radius': 4.5, 'knock_back_power': 4.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1f6c1a6b
        power_beam = TBeamInfo.from_stream(data, property_size, default_override={'cooldown': 0.11100000143051147})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc50f608b
        dark_beam = TBeamInfo.from_stream(data, property_size, default_override={'cooldown': 0.30000001192092896})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x059dce11
        dark_beam_blob = TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 1, 'damage_amount': 1.0, 'radius_damage_amount': 0.0, 'damage_radius': 0.0, 'knock_back_power': 0.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xde7a8255
        light_beam = TBeamInfo.from_stream(data, property_size, default_override={'cooldown': 0.5})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x74b9b983
        annihilator_beam = TBeamInfo.from_stream(data, property_size, default_override={'cooldown': 0.33000001311302185})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdd5f2e3d
        phazon_beam = TBeamInfo.from_stream(data, property_size, default_override={'cooldown': 0.10000000149011612})
    
        return cls(bomb, unknown_0xe8907530, unknown_0x0a9186cb, power_bomb, missile, power_beam, dark_beam, dark_beam_blob, light_beam, annihilator_beam, phazon_beam)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0b')  # 11 properties

        data.write(b'as\xad\x96')  # 0x6173ad96
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.bomb.to_stream(data, default_override={'weapon_type': 4, 'radius_damage_amount': 10.0, 'damage_radius': 3.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe8\x90u0')  # 0xe8907530
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe8907530))

        data.write(b'\n\x91\x86\xcb')  # 0xa9186cb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0a9186cb))

        data.write(b'\xdc\xc0\xc6\xfb')  # 0xdcc0c6fb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.power_bomb.to_stream(data, default_override={'weapon_type': 5, 'damage_amount': 100.0, 'radius_damage_amount': 50.0, 'damage_radius': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'X\xf0\x0b\n')  # 0x58f00b0a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.missile.to_stream(data, default_override={'weapon_type': 6, 'damage_amount': 30.0, 'radius_damage_amount': 15.0, 'damage_radius': 4.5, 'knock_back_power': 4.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1fl\x1ak')  # 0x1f6c1a6b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.power_beam.to_stream(data, default_override={'cooldown': 0.11100000143051147})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc5\x0f`\x8b')  # 0xc50f608b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.dark_beam.to_stream(data, default_override={'cooldown': 0.30000001192092896})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x05\x9d\xce\x11')  # 0x59dce11
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.dark_beam_blob.to_stream(data, default_override={'weapon_type': 1, 'damage_amount': 1.0, 'radius_damage_amount': 0.0, 'damage_radius': 0.0, 'knock_back_power': 0.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdez\x82U')  # 0xde7a8255
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.light_beam.to_stream(data, default_override={'cooldown': 0.5})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b't\xb9\xb9\x83')  # 0x74b9b983
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.annihilator_beam.to_stream(data, default_override={'cooldown': 0.33000001311302185})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdd_.=')  # 0xdd5f2e3d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.phazon_beam.to_stream(data, default_override={'cooldown': 0.10000000149011612})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayerGun_WeaponsJson", data)
        return cls(
            bomb=TDamageInfo.from_json(json_data['bomb']),
            unknown_0xe8907530=json_data['unknown_0xe8907530'],
            unknown_0x0a9186cb=json_data['unknown_0x0a9186cb'],
            power_bomb=TDamageInfo.from_json(json_data['power_bomb']),
            missile=TDamageInfo.from_json(json_data['missile']),
            power_beam=TBeamInfo.from_json(json_data['power_beam']),
            dark_beam=TBeamInfo.from_json(json_data['dark_beam']),
            dark_beam_blob=TDamageInfo.from_json(json_data['dark_beam_blob']),
            light_beam=TBeamInfo.from_json(json_data['light_beam']),
            annihilator_beam=TBeamInfo.from_json(json_data['annihilator_beam']),
            phazon_beam=TBeamInfo.from_json(json_data['phazon_beam']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'bomb': self.bomb.to_json(),
            'unknown_0xe8907530': self.unknown_0xe8907530,
            'unknown_0x0a9186cb': self.unknown_0x0a9186cb,
            'power_bomb': self.power_bomb.to_json(),
            'missile': self.missile.to_json(),
            'power_beam': self.power_beam.to_json(),
            'dark_beam': self.dark_beam.to_json(),
            'dark_beam_blob': self.dark_beam_blob.to_json(),
            'light_beam': self.light_beam.to_json(),
            'annihilator_beam': self.annihilator_beam.to_json(),
            'phazon_beam': self.phazon_beam.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.bomb.dependencies_for, "bomb", "TDamageInfo"),
            (self.power_bomb.dependencies_for, "power_bomb", "TDamageInfo"),
            (self.missile.dependencies_for, "missile", "TDamageInfo"),
            (self.power_beam.dependencies_for, "power_beam", "TBeamInfo"),
            (self.dark_beam.dependencies_for, "dark_beam", "TBeamInfo"),
            (self.dark_beam_blob.dependencies_for, "dark_beam_blob", "TDamageInfo"),
            (self.light_beam.dependencies_for, "light_beam", "TBeamInfo"),
            (self.annihilator_beam.dependencies_for, "annihilator_beam", "TBeamInfo"),
            (self.phazon_beam.dependencies_for, "phazon_beam", "TBeamInfo"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for TweakPlayerGun_Weapons.{field_name} ({field_type}): {e}"
                )


def _decode_bomb(data: typing.BinaryIO, property_size: int) -> TDamageInfo:
    return TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 4, 'radius_damage_amount': 10.0, 'damage_radius': 3.0})


def _decode_unknown_0xe8907530(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0a9186cb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_power_bomb(data: typing.BinaryIO, property_size: int) -> TDamageInfo:
    return TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 5, 'damage_amount': 100.0, 'radius_damage_amount': 50.0, 'damage_radius': 10.0})


def _decode_missile(data: typing.BinaryIO, property_size: int) -> TDamageInfo:
    return TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 6, 'damage_amount': 30.0, 'radius_damage_amount': 15.0, 'damage_radius': 4.5, 'knock_back_power': 4.0})


def _decode_power_beam(data: typing.BinaryIO, property_size: int) -> TBeamInfo:
    return TBeamInfo.from_stream(data, property_size, default_override={'cooldown': 0.11100000143051147})


def _decode_dark_beam(data: typing.BinaryIO, property_size: int) -> TBeamInfo:
    return TBeamInfo.from_stream(data, property_size, default_override={'cooldown': 0.30000001192092896})


def _decode_dark_beam_blob(data: typing.BinaryIO, property_size: int) -> TDamageInfo:
    return TDamageInfo.from_stream(data, property_size, default_override={'weapon_type': 1, 'damage_amount': 1.0, 'radius_damage_amount': 0.0, 'damage_radius': 0.0, 'knock_back_power': 0.0})


def _decode_light_beam(data: typing.BinaryIO, property_size: int) -> TBeamInfo:
    return TBeamInfo.from_stream(data, property_size, default_override={'cooldown': 0.5})


def _decode_annihilator_beam(data: typing.BinaryIO, property_size: int) -> TBeamInfo:
    return TBeamInfo.from_stream(data, property_size, default_override={'cooldown': 0.33000001311302185})


def _decode_phazon_beam(data: typing.BinaryIO, property_size: int) -> TBeamInfo:
    return TBeamInfo.from_stream(data, property_size, default_override={'cooldown': 0.10000000149011612})


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x6173ad96: ('bomb', _decode_bomb),
    0xe8907530: ('unknown_0xe8907530', _decode_unknown_0xe8907530),
    0xa9186cb: ('unknown_0x0a9186cb', _decode_unknown_0x0a9186cb),
    0xdcc0c6fb: ('power_bomb', _decode_power_bomb),
    0x58f00b0a: ('missile', _decode_missile),
    0x1f6c1a6b: ('power_beam', _decode_power_beam),
    0xc50f608b: ('dark_beam', _decode_dark_beam),
    0x59dce11: ('dark_beam_blob', _decode_dark_beam_blob),
    0xde7a8255: ('light_beam', _decode_light_beam),
    0x74b9b983: ('annihilator_beam', _decode_annihilator_beam),
    0xdd5f2e3d: ('phazon_beam', _decode_phazon_beam),
}
