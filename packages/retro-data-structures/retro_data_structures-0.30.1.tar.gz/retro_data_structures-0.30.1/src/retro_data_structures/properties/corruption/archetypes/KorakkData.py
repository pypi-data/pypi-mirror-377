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
from retro_data_structures.properties.corruption.archetypes.DamageVulnerability import DamageVulnerability

if typing.TYPE_CHECKING:
    class KorakkDataJson(typing_extensions.TypedDict):
        unknown_0x27b15c35: float
        unknown_0x6c6b5700: int
        mouth_vulnerability: json_util.JsonObject
        tongue_damage: json_util.JsonObject
        morphball_bite_damage: json_util.JsonObject
        damage_info_0x77941011: json_util.JsonObject
        damage_info_0x4d07f7b1: json_util.JsonObject
        phazon_lance_damage: json_util.JsonObject
        damage_info_0x8333b35f: json_util.JsonObject
        stab_damage: json_util.JsonObject
    

@dataclasses.dataclass()
class KorakkData(BaseProperty):
    unknown_0x27b15c35: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x27b15c35, original_name='Unknown'
        ),
    })
    unknown_0x6c6b5700: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6c6b5700, original_name='Unknown'
        ),
    })
    mouth_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xed7edca3, original_name='MouthVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    tongue_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xda5e9630, original_name='TongueDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    morphball_bite_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x508f7177, original_name='MorphballBiteDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_info_0x77941011: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x77941011, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_info_0x4d07f7b1: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x4d07f7b1, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    phazon_lance_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x21a2121d, original_name='PhazonLanceDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_info_0x8333b35f: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x8333b35f, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    stab_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x946016a9, original_name='StabDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
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
        if property_count != 10:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x27b15c35
        unknown_0x27b15c35 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c6b5700
        unknown_0x6c6b5700 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed7edca3
        mouth_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xda5e9630
        tongue_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x508f7177
        morphball_bite_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x77941011
        damage_info_0x77941011 = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d07f7b1
        damage_info_0x4d07f7b1 = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x21a2121d
        phazon_lance_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8333b35f
        damage_info_0x8333b35f = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x946016a9
        stab_damage = DamageInfo.from_stream(data, property_size)
    
        return cls(unknown_0x27b15c35, unknown_0x6c6b5700, mouth_vulnerability, tongue_damage, morphball_bite_damage, damage_info_0x77941011, damage_info_0x4d07f7b1, phazon_lance_damage, damage_info_0x8333b35f, stab_damage)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\n')  # 10 properties

        data.write(b"'\xb1\\5")  # 0x27b15c35
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x27b15c35))

        data.write(b'lkW\x00')  # 0x6c6b5700
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x6c6b5700))

        data.write(b'\xed~\xdc\xa3')  # 0xed7edca3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.mouth_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xda^\x960')  # 0xda5e9630
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.tongue_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'P\x8fqw')  # 0x508f7177
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.morphball_bite_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'w\x94\x10\x11')  # 0x77941011
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0x77941011.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'M\x07\xf7\xb1')  # 0x4d07f7b1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0x4d07f7b1.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'!\xa2\x12\x1d')  # 0x21a2121d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.phazon_lance_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x833\xb3_')  # 0x8333b35f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0x8333b35f.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x94`\x16\xa9')  # 0x946016a9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.stab_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("KorakkDataJson", data)
        return cls(
            unknown_0x27b15c35=json_data['unknown_0x27b15c35'],
            unknown_0x6c6b5700=json_data['unknown_0x6c6b5700'],
            mouth_vulnerability=DamageVulnerability.from_json(json_data['mouth_vulnerability']),
            tongue_damage=DamageInfo.from_json(json_data['tongue_damage']),
            morphball_bite_damage=DamageInfo.from_json(json_data['morphball_bite_damage']),
            damage_info_0x77941011=DamageInfo.from_json(json_data['damage_info_0x77941011']),
            damage_info_0x4d07f7b1=DamageInfo.from_json(json_data['damage_info_0x4d07f7b1']),
            phazon_lance_damage=DamageInfo.from_json(json_data['phazon_lance_damage']),
            damage_info_0x8333b35f=DamageInfo.from_json(json_data['damage_info_0x8333b35f']),
            stab_damage=DamageInfo.from_json(json_data['stab_damage']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x27b15c35': self.unknown_0x27b15c35,
            'unknown_0x6c6b5700': self.unknown_0x6c6b5700,
            'mouth_vulnerability': self.mouth_vulnerability.to_json(),
            'tongue_damage': self.tongue_damage.to_json(),
            'morphball_bite_damage': self.morphball_bite_damage.to_json(),
            'damage_info_0x77941011': self.damage_info_0x77941011.to_json(),
            'damage_info_0x4d07f7b1': self.damage_info_0x4d07f7b1.to_json(),
            'phazon_lance_damage': self.phazon_lance_damage.to_json(),
            'damage_info_0x8333b35f': self.damage_info_0x8333b35f.to_json(),
            'stab_damage': self.stab_damage.to_json(),
        }


def _decode_unknown_0x27b15c35(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6c6b5700(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x27b15c35: ('unknown_0x27b15c35', _decode_unknown_0x27b15c35),
    0x6c6b5700: ('unknown_0x6c6b5700', _decode_unknown_0x6c6b5700),
    0xed7edca3: ('mouth_vulnerability', DamageVulnerability.from_stream),
    0xda5e9630: ('tongue_damage', DamageInfo.from_stream),
    0x508f7177: ('morphball_bite_damage', DamageInfo.from_stream),
    0x77941011: ('damage_info_0x77941011', DamageInfo.from_stream),
    0x4d07f7b1: ('damage_info_0x4d07f7b1', DamageInfo.from_stream),
    0x21a2121d: ('phazon_lance_damage', DamageInfo.from_stream),
    0x8333b35f: ('damage_info_0x8333b35f', DamageInfo.from_stream),
    0x946016a9: ('stab_damage', DamageInfo.from_stream),
}
