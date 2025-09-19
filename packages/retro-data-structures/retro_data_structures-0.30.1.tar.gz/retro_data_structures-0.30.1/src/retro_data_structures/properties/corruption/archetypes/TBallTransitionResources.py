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
from retro_data_structures.properties.corruption.archetypes.TGunResources import TGunResources
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class TBallTransitionResourcesJson(typing_extensions.TypedDict):
        unknown_0xd48e4124: str
        unknown_0x01e12c84: json_util.JsonObject
        unknown_0xf24b055d: json_util.JsonObject
        unknown_0xa342c3a6: json_util.JsonObject
        unknown_0x15b6840d: json_util.JsonObject
        unknown_0x23fb0e93: json_util.JsonObject
        unknown_0x564262f0: json_util.JsonObject
        movement_control: json_util.JsonObject
    

@dataclasses.dataclass()
class TBallTransitionResources(BaseProperty):
    unknown_0xd48e4124: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xd48e4124, original_name='Unknown'
        ),
    })
    unknown_0x01e12c84: TGunResources = dataclasses.field(default_factory=TGunResources, metadata={
        'reflection': FieldReflection[TGunResources](
            TGunResources, id=0x01e12c84, original_name='Unknown', from_json=TGunResources.from_json, to_json=TGunResources.to_json
        ),
    })
    unknown_0xf24b055d: TGunResources = dataclasses.field(default_factory=TGunResources, metadata={
        'reflection': FieldReflection[TGunResources](
            TGunResources, id=0xf24b055d, original_name='Unknown', from_json=TGunResources.from_json, to_json=TGunResources.to_json
        ),
    })
    unknown_0xa342c3a6: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xa342c3a6, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0x15b6840d: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x15b6840d, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0x23fb0e93: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x23fb0e93, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0x564262f0: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x564262f0, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    movement_control: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x9183a262, original_name='MovementControl', from_json=Spline.from_json, to_json=Spline.to_json
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
        if property_count != 8:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd48e4124
        unknown_0xd48e4124 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01e12c84
        unknown_0x01e12c84 = TGunResources.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf24b055d
        unknown_0xf24b055d = TGunResources.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa342c3a6
        unknown_0xa342c3a6 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x15b6840d
        unknown_0x15b6840d = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x23fb0e93
        unknown_0x23fb0e93 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x564262f0
        unknown_0x564262f0 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9183a262
        movement_control = Spline.from_stream(data, property_size)
    
        return cls(unknown_0xd48e4124, unknown_0x01e12c84, unknown_0xf24b055d, unknown_0xa342c3a6, unknown_0x15b6840d, unknown_0x23fb0e93, unknown_0x564262f0, movement_control)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'\xd4\x8eA$')  # 0xd48e4124
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0xd48e4124.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x01\xe1,\x84')  # 0x1e12c84
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x01e12c84.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf2K\x05]')  # 0xf24b055d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xf24b055d.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa3B\xc3\xa6')  # 0xa342c3a6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xa342c3a6.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x15\xb6\x84\r')  # 0x15b6840d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x15b6840d.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'#\xfb\x0e\x93')  # 0x23fb0e93
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x23fb0e93.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'VBb\xf0')  # 0x564262f0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x564262f0.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x91\x83\xa2b')  # 0x9183a262
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.movement_control.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TBallTransitionResourcesJson", data)
        return cls(
            unknown_0xd48e4124=json_data['unknown_0xd48e4124'],
            unknown_0x01e12c84=TGunResources.from_json(json_data['unknown_0x01e12c84']),
            unknown_0xf24b055d=TGunResources.from_json(json_data['unknown_0xf24b055d']),
            unknown_0xa342c3a6=Spline.from_json(json_data['unknown_0xa342c3a6']),
            unknown_0x15b6840d=Spline.from_json(json_data['unknown_0x15b6840d']),
            unknown_0x23fb0e93=Spline.from_json(json_data['unknown_0x23fb0e93']),
            unknown_0x564262f0=Spline.from_json(json_data['unknown_0x564262f0']),
            movement_control=Spline.from_json(json_data['movement_control']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xd48e4124': self.unknown_0xd48e4124,
            'unknown_0x01e12c84': self.unknown_0x01e12c84.to_json(),
            'unknown_0xf24b055d': self.unknown_0xf24b055d.to_json(),
            'unknown_0xa342c3a6': self.unknown_0xa342c3a6.to_json(),
            'unknown_0x15b6840d': self.unknown_0x15b6840d.to_json(),
            'unknown_0x23fb0e93': self.unknown_0x23fb0e93.to_json(),
            'unknown_0x564262f0': self.unknown_0x564262f0.to_json(),
            'movement_control': self.movement_control.to_json(),
        }


def _decode_unknown_0xd48e4124(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xd48e4124: ('unknown_0xd48e4124', _decode_unknown_0xd48e4124),
    0x1e12c84: ('unknown_0x01e12c84', TGunResources.from_stream),
    0xf24b055d: ('unknown_0xf24b055d', TGunResources.from_stream),
    0xa342c3a6: ('unknown_0xa342c3a6', Spline.from_stream),
    0x15b6840d: ('unknown_0x15b6840d', Spline.from_stream),
    0x23fb0e93: ('unknown_0x23fb0e93', Spline.from_stream),
    0x564262f0: ('unknown_0x564262f0', Spline.from_stream),
    0x9183a262: ('movement_control', Spline.from_stream),
}
