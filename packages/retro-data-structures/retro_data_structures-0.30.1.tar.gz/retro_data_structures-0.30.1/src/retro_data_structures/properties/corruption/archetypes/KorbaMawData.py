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
from retro_data_structures.properties.corruption.archetypes.DamageInfo import DamageInfo

if typing.TYPE_CHECKING:
    class KorbaMawDataJson(typing_extensions.TypedDict):
        bite_damage: json_util.JsonObject
        unknown_0x200f67e7: float
        unknown_0xe54de3e1: float
        unknown_0x8a821fee: float
    

@dataclasses.dataclass()
class KorbaMawData(BaseProperty):
    bite_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xdf636c4b, original_name='BiteDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x200f67e7: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x200f67e7, original_name='Unknown'
        ),
    })
    unknown_0xe54de3e1: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe54de3e1, original_name='Unknown'
        ),
    })
    unknown_0x8a821fee: float = dataclasses.field(default=2.799999952316284, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8a821fee, original_name='Unknown'
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
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdf636c4b
        bite_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x200f67e7
        unknown_0x200f67e7 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe54de3e1
        unknown_0xe54de3e1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8a821fee
        unknown_0x8a821fee = struct.unpack('>f', data.read(4))[0]
    
        return cls(bite_damage, unknown_0x200f67e7, unknown_0xe54de3e1, unknown_0x8a821fee)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'\xdfclK')  # 0xdf636c4b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.bite_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b' \x0fg\xe7')  # 0x200f67e7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x200f67e7))

        data.write(b'\xe5M\xe3\xe1')  # 0xe54de3e1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe54de3e1))

        data.write(b'\x8a\x82\x1f\xee')  # 0x8a821fee
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8a821fee))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("KorbaMawDataJson", data)
        return cls(
            bite_damage=DamageInfo.from_json(json_data['bite_damage']),
            unknown_0x200f67e7=json_data['unknown_0x200f67e7'],
            unknown_0xe54de3e1=json_data['unknown_0xe54de3e1'],
            unknown_0x8a821fee=json_data['unknown_0x8a821fee'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'bite_damage': self.bite_damage.to_json(),
            'unknown_0x200f67e7': self.unknown_0x200f67e7,
            'unknown_0xe54de3e1': self.unknown_0xe54de3e1,
            'unknown_0x8a821fee': self.unknown_0x8a821fee,
        }


def _decode_unknown_0x200f67e7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe54de3e1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8a821fee(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xdf636c4b: ('bite_damage', DamageInfo.from_stream),
    0x200f67e7: ('unknown_0x200f67e7', _decode_unknown_0x200f67e7),
    0xe54de3e1: ('unknown_0xe54de3e1', _decode_unknown_0xe54de3e1),
    0x8a821fee: ('unknown_0x8a821fee', _decode_unknown_0x8a821fee),
}
