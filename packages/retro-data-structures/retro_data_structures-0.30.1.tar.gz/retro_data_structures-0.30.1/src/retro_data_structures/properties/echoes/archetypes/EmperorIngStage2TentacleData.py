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

    class EmperorIngStage2TentacleDataJson(typing_extensions.TypedDict):
        detection_time: float
        forget_time: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xbaa9254a, 0x1fe28a36)


@dataclasses.dataclass()
class EmperorIngStage2TentacleData(BaseProperty):
    detection_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbaa9254a, original_name='DetectionTime'
        ),
    })
    forget_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1fe28a36, original_name='ForgetTime'
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
        if property_count != 2:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(20))
        assert (dec[0], dec[3]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x02')  # 2 properties

        data.write(b'\xba\xa9%J')  # 0xbaa9254a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.detection_time))

        data.write(b'\x1f\xe2\x8a6')  # 0x1fe28a36
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forget_time))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("EmperorIngStage2TentacleDataJson", data)
        return cls(
            detection_time=json_data['detection_time'],
            forget_time=json_data['forget_time'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'detection_time': self.detection_time,
            'forget_time': self.forget_time,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_detection_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forget_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xbaa9254a: ('detection_time', _decode_detection_time),
    0x1fe28a36: ('forget_time', _decode_forget_time),
}
