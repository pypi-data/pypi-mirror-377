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
from retro_data_structures.properties.echoes.core.Spline import Spline

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DynamicLightIntensityJson(typing_extensions.TypedDict):
        intensity: json_util.JsonObject
        intensity_duration: float
        intensity_loops: bool
    

@dataclasses.dataclass()
class DynamicLightIntensity(BaseProperty):
    intensity: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x239d0d2b, original_name='Intensity', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    intensity_duration: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc90d8899, original_name='IntensityDuration'
        ),
    })
    intensity_loops: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xae67e050, original_name='IntensityLoops'
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
        if property_count != 3:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x239d0d2b
        intensity = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc90d8899
        intensity_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xae67e050
        intensity_loops = struct.unpack('>?', data.read(1))[0]
    
        return cls(intensity, intensity_duration, intensity_loops)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'#\x9d\r+')  # 0x239d0d2b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.intensity.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc9\r\x88\x99')  # 0xc90d8899
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.intensity_duration))

        data.write(b'\xaeg\xe0P')  # 0xae67e050
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.intensity_loops))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DynamicLightIntensityJson", data)
        return cls(
            intensity=Spline.from_json(json_data['intensity']),
            intensity_duration=json_data['intensity_duration'],
            intensity_loops=json_data['intensity_loops'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'intensity': self.intensity.to_json(),
            'intensity_duration': self.intensity_duration,
            'intensity_loops': self.intensity_loops,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_intensity_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_intensity_loops(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x239d0d2b: ('intensity', Spline.from_stream),
    0xc90d8899: ('intensity_duration', _decode_intensity_duration),
    0xae67e050: ('intensity_loops', _decode_intensity_loops),
}
