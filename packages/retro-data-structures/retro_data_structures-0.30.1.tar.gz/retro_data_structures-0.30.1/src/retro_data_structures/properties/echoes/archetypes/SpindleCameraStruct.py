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

    class SpindleCameraStructJson(typing_extensions.TypedDict):
        interpolant_type: int
        interpolant_spline: json_util.JsonObject
    

@dataclasses.dataclass()
class SpindleCameraStruct(BaseProperty):
    interpolant_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x3e9cf140, original_name='InterpolantType'
        ),
    })
    interpolant_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x9a598fa5, original_name='InterpolantSpline', from_json=Spline.from_json, to_json=Spline.to_json
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
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3e9cf140
        interpolant_type = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9a598fa5
        interpolant_spline = Spline.from_stream(data, property_size)
    
        return cls(interpolant_type, interpolant_spline)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x02')  # 2 properties

        data.write(b'>\x9c\xf1@')  # 0x3e9cf140
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.interpolant_type))

        data.write(b'\x9aY\x8f\xa5')  # 0x9a598fa5
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.interpolant_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SpindleCameraStructJson", data)
        return cls(
            interpolant_type=json_data['interpolant_type'],
            interpolant_spline=Spline.from_json(json_data['interpolant_spline']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'interpolant_type': self.interpolant_type,
            'interpolant_spline': self.interpolant_spline.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_interpolant_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x3e9cf140: ('interpolant_type', _decode_interpolant_type),
    0x9a598fa5: ('interpolant_spline', Spline.from_stream),
}
