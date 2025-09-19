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

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class EchoParametersJson(typing_extensions.TypedDict):
        is_echo_emitter: bool
        only_emit_damage: bool
        num_sound_waves: int
        space_between_waves: float
        wave_line_size: float
        forced_minimum_vis: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x17addfc6, 0xf5df62ad, 0xd0073a0c, 0xed6d6782, 0xdb190f68, 0xf87a15e7)


@dataclasses.dataclass()
class EchoParameters(BaseProperty):
    is_echo_emitter: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x17addfc6, original_name='IsEchoEmitter'
        ),
    })
    only_emit_damage: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf5df62ad, original_name='OnlyEmitDamage'
        ),
    })
    num_sound_waves: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0xd0073a0c, original_name='NumSoundWaves'
        ),
    })
    space_between_waves: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed6d6782, original_name='SpaceBetweenWaves'
        ),
    })
    wave_line_size: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdb190f68, original_name='WaveLineSize'
        ),
    })
    forced_minimum_vis: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf87a15e7, original_name='ForcedMinimumVis?'
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
        if property_count != 6:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LH?LH?LHlLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(54))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'\x17\xad\xdf\xc6')  # 0x17addfc6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_echo_emitter))

        data.write(b'\xf5\xdfb\xad')  # 0xf5df62ad
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.only_emit_damage))

        data.write(b'\xd0\x07:\x0c')  # 0xd0073a0c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.num_sound_waves))

        data.write(b'\xedmg\x82')  # 0xed6d6782
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.space_between_waves))

        data.write(b'\xdb\x19\x0fh')  # 0xdb190f68
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.wave_line_size))

        data.write(b'\xf8z\x15\xe7')  # 0xf87a15e7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forced_minimum_vis))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("EchoParametersJson", data)
        return cls(
            is_echo_emitter=json_data['is_echo_emitter'],
            only_emit_damage=json_data['only_emit_damage'],
            num_sound_waves=json_data['num_sound_waves'],
            space_between_waves=json_data['space_between_waves'],
            wave_line_size=json_data['wave_line_size'],
            forced_minimum_vis=json_data['forced_minimum_vis'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'is_echo_emitter': self.is_echo_emitter,
            'only_emit_damage': self.only_emit_damage,
            'num_sound_waves': self.num_sound_waves,
            'space_between_waves': self.space_between_waves,
            'wave_line_size': self.wave_line_size,
            'forced_minimum_vis': self.forced_minimum_vis,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_is_echo_emitter(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_only_emit_damage(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_num_sound_waves(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_space_between_waves(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_wave_line_size(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forced_minimum_vis(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x17addfc6: ('is_echo_emitter', _decode_is_echo_emitter),
    0xf5df62ad: ('only_emit_damage', _decode_only_emit_damage),
    0xd0073a0c: ('num_sound_waves', _decode_num_sound_waves),
    0xed6d6782: ('space_between_waves', _decode_space_between_waves),
    0xdb190f68: ('wave_line_size', _decode_wave_line_size),
    0xf87a15e7: ('forced_minimum_vis', _decode_forced_minimum_vis),
}
