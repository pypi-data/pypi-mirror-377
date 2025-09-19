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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct48Json(typing_extensions.TypedDict):
        max_attack_angle: float
        hyper_particle_effect: int
        attack_speed_multiplier: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xf11f7384, 0x1ae85bc0, 0x77856668)


@dataclasses.dataclass()
class UnknownStruct48(BaseProperty):
    max_attack_angle: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf11f7384, original_name='MaxAttackAngle'
        ),
    })
    hyper_particle_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1ae85bc0, original_name='HyperParticleEffect'
        ),
    })
    attack_speed_multiplier: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x77856668, original_name='AttackSpeedMultiplier'
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
        if property_count != 3:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHQLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(34))
        assert (dec[0], dec[3], dec[6]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'\xf1\x1fs\x84')  # 0xf11f7384
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_angle))

        data.write(b'\x1a\xe8[\xc0')  # 0x1ae85bc0
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.hyper_particle_effect))

        data.write(b'w\x85fh')  # 0x77856668
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_speed_multiplier))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct48Json", data)
        return cls(
            max_attack_angle=json_data['max_attack_angle'],
            hyper_particle_effect=json_data['hyper_particle_effect'],
            attack_speed_multiplier=json_data['attack_speed_multiplier'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'max_attack_angle': self.max_attack_angle,
            'hyper_particle_effect': self.hyper_particle_effect,
            'attack_speed_multiplier': self.attack_speed_multiplier,
        }


def _decode_max_attack_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hyper_particle_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_attack_speed_multiplier(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xf11f7384: ('max_attack_angle', _decode_max_attack_angle),
    0x1ae85bc0: ('hyper_particle_effect', _decode_hyper_particle_effect),
    0x77856668: ('attack_speed_multiplier', _decode_attack_speed_multiplier),
}
