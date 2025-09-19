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
    class SwarmSoundDataJson(typing_extensions.TypedDict):
        sound_asset: int
        max_count: int
        min_delay: float
        max_delay: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xfc0d589e, 0x54b68c4c, 0xb5f9c71a, 0xf5b6bf6c)


@dataclasses.dataclass()
class SwarmSoundData(BaseProperty):
    sound_asset: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xfc0d589e, original_name='SoundAsset'
        ),
    })
    max_count: int = dataclasses.field(default=5, metadata={
        'reflection': FieldReflection[int](
            int, id=0x54b68c4c, original_name='MaxCount'
        ),
    })
    min_delay: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb5f9c71a, original_name='MinDelay'
        ),
    })
    max_delay: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf5b6bf6c, original_name='MaxDelay'
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
        if property_count != 4:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHQLHlLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(44))
        assert (dec[0], dec[3], dec[6], dec[9]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'\xfc\rX\x9e')  # 0xfc0d589e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_asset))

        data.write(b'T\xb6\x8cL')  # 0x54b68c4c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_count))

        data.write(b'\xb5\xf9\xc7\x1a')  # 0xb5f9c71a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_delay))

        data.write(b'\xf5\xb6\xbfl')  # 0xf5b6bf6c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_delay))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SwarmSoundDataJson", data)
        return cls(
            sound_asset=json_data['sound_asset'],
            max_count=json_data['max_count'],
            min_delay=json_data['min_delay'],
            max_delay=json_data['max_delay'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'sound_asset': self.sound_asset,
            'max_count': self.max_count,
            'min_delay': self.min_delay,
            'max_delay': self.max_delay,
        }


def _decode_sound_asset(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_max_count(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_min_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xfc0d589e: ('sound_asset', _decode_sound_asset),
    0x54b68c4c: ('max_count', _decode_max_count),
    0xb5f9c71a: ('min_delay', _decode_min_delay),
    0xf5b6bf6c: ('max_delay', _decode_max_delay),
}
