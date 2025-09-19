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
from retro_data_structures.properties.echoes.archetypes.ShockWaveInfo import ShockWaveInfo

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class UnknownStruct23Json(typing_extensions.TypedDict):
        loop_duration: float
        destroy_percentage: int
        shock_wave_info: json_util.JsonObject
        sound: int
    

@dataclasses.dataclass()
class UnknownStruct23(BaseProperty):
    loop_duration: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcee68723, original_name='LoopDuration'
        ),
    })
    destroy_percentage: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x01274d6e, original_name='DestroyPercentage'
        ),
    })
    shock_wave_info: ShockWaveInfo = dataclasses.field(default_factory=ShockWaveInfo, metadata={
        'reflection': FieldReflection[ShockWaveInfo](
            ShockWaveInfo, id=0x8f4787cb, original_name='ShockWaveInfo', from_json=ShockWaveInfo.from_json, to_json=ShockWaveInfo.to_json
        ),
    })
    sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x25af490e, original_name='Sound'
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
        if property_count != 4:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcee68723
        loop_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01274d6e
        destroy_percentage = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f4787cb
        shock_wave_info = ShockWaveInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x25af490e
        sound = struct.unpack('>l', data.read(4))[0]
    
        return cls(loop_duration, destroy_percentage, shock_wave_info, sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'\xce\xe6\x87#')  # 0xcee68723
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.loop_duration))

        data.write(b"\x01'Mn")  # 0x1274d6e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.destroy_percentage))

        data.write(b'\x8fG\x87\xcb')  # 0x8f4787cb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shock_wave_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'%\xafI\x0e')  # 0x25af490e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct23Json", data)
        return cls(
            loop_duration=json_data['loop_duration'],
            destroy_percentage=json_data['destroy_percentage'],
            shock_wave_info=ShockWaveInfo.from_json(json_data['shock_wave_info']),
            sound=json_data['sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'loop_duration': self.loop_duration,
            'destroy_percentage': self.destroy_percentage,
            'shock_wave_info': self.shock_wave_info.to_json(),
            'sound': self.sound,
        }

    def _dependencies_for_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.shock_wave_info.dependencies_for, "shock_wave_info", "ShockWaveInfo"),
            (self._dependencies_for_sound, "sound", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for UnknownStruct23.{field_name} ({field_type}): {e}"
                )


def _decode_loop_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_destroy_percentage(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xcee68723: ('loop_duration', _decode_loop_duration),
    0x1274d6e: ('destroy_percentage', _decode_destroy_percentage),
    0x8f4787cb: ('shock_wave_info', ShockWaveInfo.from_stream),
    0x25af490e: ('sound', _decode_sound),
}
