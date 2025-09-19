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
from retro_data_structures.properties.corruption.archetypes.PlayerInventoryItem import PlayerInventoryItem

if typing.TYPE_CHECKING:
    class WeaponsJson(typing_extensions.TypedDict):
        power_beam: bool
        plasma_beam: bool
        nova_beam: bool
        charge_upgrade: bool
        missile: json_util.JsonObject
        ice_missile: bool
        seeker_missile: bool
        grapple_beam_pull: bool
        grapple_beam_swing: bool
        grapple_beam_voltage: bool
        bomb: bool
    

@dataclasses.dataclass()
class Weapons(BaseProperty):
    power_beam: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf9bc3e3d, original_name='PowerBeam'
        ),
    })
    plasma_beam: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x42c900ed, original_name='PlasmaBeam'
        ),
    })
    nova_beam: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x4ae27fe7, original_name='NovaBeam'
        ),
    })
    charge_upgrade: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf34f99d7, original_name='ChargeUpgrade'
        ),
    })
    missile: PlayerInventoryItem = dataclasses.field(default_factory=PlayerInventoryItem, metadata={
        'reflection': FieldReflection[PlayerInventoryItem](
            PlayerInventoryItem, id=0xa387191d, original_name='Missile', from_json=PlayerInventoryItem.from_json, to_json=PlayerInventoryItem.to_json
        ),
    })
    ice_missile: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5db3e694, original_name='IceMissile'
        ),
    })
    seeker_missile: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x9aa405c1, original_name='SeekerMissile'
        ),
    })
    grapple_beam_pull: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa4658688, original_name='GrappleBeamPull'
        ),
    })
    grapple_beam_swing: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xd23cf29d, original_name='GrappleBeamSwing'
        ),
    })
    grapple_beam_voltage: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5a7e301e, original_name='GrappleBeamVoltage'
        ),
    })
    bomb: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xafc6082d, original_name='Bomb'
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
        if property_count != 11:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf9bc3e3d
        power_beam = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x42c900ed
        plasma_beam = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ae27fe7
        nova_beam = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf34f99d7
        charge_upgrade = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa387191d
        missile = PlayerInventoryItem.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5db3e694
        ice_missile = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9aa405c1
        seeker_missile = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa4658688
        grapple_beam_pull = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd23cf29d
        grapple_beam_swing = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5a7e301e
        grapple_beam_voltage = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xafc6082d
        bomb = struct.unpack('>?', data.read(1))[0]
    
        return cls(power_beam, plasma_beam, nova_beam, charge_upgrade, missile, ice_missile, seeker_missile, grapple_beam_pull, grapple_beam_swing, grapple_beam_voltage, bomb)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0b')  # 11 properties

        data.write(b'\xf9\xbc>=')  # 0xf9bc3e3d
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.power_beam))

        data.write(b'B\xc9\x00\xed')  # 0x42c900ed
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.plasma_beam))

        data.write(b'J\xe2\x7f\xe7')  # 0x4ae27fe7
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.nova_beam))

        data.write(b'\xf3O\x99\xd7')  # 0xf34f99d7
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.charge_upgrade))

        data.write(b'\xa3\x87\x19\x1d')  # 0xa387191d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.missile.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b']\xb3\xe6\x94')  # 0x5db3e694
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.ice_missile))

        data.write(b'\x9a\xa4\x05\xc1')  # 0x9aa405c1
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.seeker_missile))

        data.write(b'\xa4e\x86\x88')  # 0xa4658688
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.grapple_beam_pull))

        data.write(b'\xd2<\xf2\x9d')  # 0xd23cf29d
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.grapple_beam_swing))

        data.write(b'Z~0\x1e')  # 0x5a7e301e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.grapple_beam_voltage))

        data.write(b'\xaf\xc6\x08-')  # 0xafc6082d
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.bomb))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("WeaponsJson", data)
        return cls(
            power_beam=json_data['power_beam'],
            plasma_beam=json_data['plasma_beam'],
            nova_beam=json_data['nova_beam'],
            charge_upgrade=json_data['charge_upgrade'],
            missile=PlayerInventoryItem.from_json(json_data['missile']),
            ice_missile=json_data['ice_missile'],
            seeker_missile=json_data['seeker_missile'],
            grapple_beam_pull=json_data['grapple_beam_pull'],
            grapple_beam_swing=json_data['grapple_beam_swing'],
            grapple_beam_voltage=json_data['grapple_beam_voltage'],
            bomb=json_data['bomb'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'power_beam': self.power_beam,
            'plasma_beam': self.plasma_beam,
            'nova_beam': self.nova_beam,
            'charge_upgrade': self.charge_upgrade,
            'missile': self.missile.to_json(),
            'ice_missile': self.ice_missile,
            'seeker_missile': self.seeker_missile,
            'grapple_beam_pull': self.grapple_beam_pull,
            'grapple_beam_swing': self.grapple_beam_swing,
            'grapple_beam_voltage': self.grapple_beam_voltage,
            'bomb': self.bomb,
        }


def _decode_power_beam(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_plasma_beam(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_nova_beam(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_charge_upgrade(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_ice_missile(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_seeker_missile(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_grapple_beam_pull(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_grapple_beam_swing(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_grapple_beam_voltage(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_bomb(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xf9bc3e3d: ('power_beam', _decode_power_beam),
    0x42c900ed: ('plasma_beam', _decode_plasma_beam),
    0x4ae27fe7: ('nova_beam', _decode_nova_beam),
    0xf34f99d7: ('charge_upgrade', _decode_charge_upgrade),
    0xa387191d: ('missile', PlayerInventoryItem.from_stream),
    0x5db3e694: ('ice_missile', _decode_ice_missile),
    0x9aa405c1: ('seeker_missile', _decode_seeker_missile),
    0xa4658688: ('grapple_beam_pull', _decode_grapple_beam_pull),
    0xd23cf29d: ('grapple_beam_swing', _decode_grapple_beam_swing),
    0x5a7e301e: ('grapple_beam_voltage', _decode_grapple_beam_voltage),
    0xafc6082d: ('bomb', _decode_bomb),
}
