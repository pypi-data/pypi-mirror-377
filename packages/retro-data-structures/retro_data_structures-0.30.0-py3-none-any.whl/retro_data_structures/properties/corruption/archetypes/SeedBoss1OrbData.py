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
from retro_data_structures.properties.corruption.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.corruption.archetypes.GrappleBlock import GrappleBlock
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Color import Color

if typing.TYPE_CHECKING:
    class SeedBoss1OrbDataJson(typing_extensions.TypedDict):
        normal_vulnerability: json_util.JsonObject
        damage_vulnerability: json_util.JsonObject
        grapple_block: json_util.JsonObject
        initial_color: json_util.JsonValue
        should_generate: bool
        orb_damage_effect: int
        orb_destroyed_sound: int
        travel_time: float
        unknown: float
        regen_rate: float
        regen_delay: float
    

@dataclasses.dataclass()
class SeedBoss1OrbData(BaseProperty):
    normal_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x29df61e1, original_name='NormalVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    damage_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xed8f36cf, original_name='DamageVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    grapple_block: GrappleBlock = dataclasses.field(default_factory=GrappleBlock, metadata={
        'reflection': FieldReflection[GrappleBlock](
            GrappleBlock, id=0x922ef2cd, original_name='GrappleBlock', from_json=GrappleBlock.from_json, to_json=GrappleBlock.to_json
        ),
    })
    initial_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=1.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x9f4149af, original_name='InitialColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    should_generate: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5319e29b, original_name='ShouldGenerate'
        ),
    })
    orb_damage_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa0285357, original_name='OrbDamageEffect'
        ),
    })
    orb_destroyed_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x53cf49f6, original_name='OrbDestroyedSound'
        ),
    })
    travel_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x88474244, original_name='TravelTime'
        ),
    })
    unknown: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb3187a53, original_name='Unknown'
        ),
    })
    regen_rate: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x46e661f7, original_name='RegenRate'
        ),
    })
    regen_delay: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcf1456ca, original_name='RegenDelay'
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
        if property_count != 11:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x29df61e1
        normal_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed8f36cf
        damage_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x922ef2cd
        grapple_block = GrappleBlock.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9f4149af
        initial_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5319e29b
        should_generate = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa0285357
        orb_damage_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x53cf49f6
        orb_destroyed_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x88474244
        travel_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3187a53
        unknown = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x46e661f7
        regen_rate = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf1456ca
        regen_delay = struct.unpack('>f', data.read(4))[0]
    
        return cls(normal_vulnerability, damage_vulnerability, grapple_block, initial_color, should_generate, orb_damage_effect, orb_destroyed_sound, travel_time, unknown, regen_rate, regen_delay)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0b')  # 11 properties

        data.write(b')\xdfa\xe1')  # 0x29df61e1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.normal_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xed\x8f6\xcf')  # 0xed8f36cf
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x92.\xf2\xcd')  # 0x922ef2cd
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_block.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9fAI\xaf')  # 0x9f4149af
        data.write(b'\x00\x10')  # size
        self.initial_color.to_stream(data)

        data.write(b'S\x19\xe2\x9b')  # 0x5319e29b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.should_generate))

        data.write(b'\xa0(SW')  # 0xa0285357
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.orb_damage_effect))

        data.write(b'S\xcfI\xf6')  # 0x53cf49f6
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.orb_destroyed_sound))

        data.write(b'\x88GBD')  # 0x88474244
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.travel_time))

        data.write(b'\xb3\x18zS')  # 0xb3187a53
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'F\xe6a\xf7')  # 0x46e661f7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.regen_rate))

        data.write(b'\xcf\x14V\xca')  # 0xcf1456ca
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.regen_delay))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SeedBoss1OrbDataJson", data)
        return cls(
            normal_vulnerability=DamageVulnerability.from_json(json_data['normal_vulnerability']),
            damage_vulnerability=DamageVulnerability.from_json(json_data['damage_vulnerability']),
            grapple_block=GrappleBlock.from_json(json_data['grapple_block']),
            initial_color=Color.from_json(json_data['initial_color']),
            should_generate=json_data['should_generate'],
            orb_damage_effect=json_data['orb_damage_effect'],
            orb_destroyed_sound=json_data['orb_destroyed_sound'],
            travel_time=json_data['travel_time'],
            unknown=json_data['unknown'],
            regen_rate=json_data['regen_rate'],
            regen_delay=json_data['regen_delay'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'normal_vulnerability': self.normal_vulnerability.to_json(),
            'damage_vulnerability': self.damage_vulnerability.to_json(),
            'grapple_block': self.grapple_block.to_json(),
            'initial_color': self.initial_color.to_json(),
            'should_generate': self.should_generate,
            'orb_damage_effect': self.orb_damage_effect,
            'orb_destroyed_sound': self.orb_destroyed_sound,
            'travel_time': self.travel_time,
            'unknown': self.unknown,
            'regen_rate': self.regen_rate,
            'regen_delay': self.regen_delay,
        }


def _decode_initial_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_should_generate(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_orb_damage_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_orb_destroyed_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_travel_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_regen_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_regen_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x29df61e1: ('normal_vulnerability', DamageVulnerability.from_stream),
    0xed8f36cf: ('damage_vulnerability', DamageVulnerability.from_stream),
    0x922ef2cd: ('grapple_block', GrappleBlock.from_stream),
    0x9f4149af: ('initial_color', _decode_initial_color),
    0x5319e29b: ('should_generate', _decode_should_generate),
    0xa0285357: ('orb_damage_effect', _decode_orb_damage_effect),
    0x53cf49f6: ('orb_destroyed_sound', _decode_orb_destroyed_sound),
    0x88474244: ('travel_time', _decode_travel_time),
    0xb3187a53: ('unknown', _decode_unknown),
    0x46e661f7: ('regen_rate', _decode_regen_rate),
    0xcf1456ca: ('regen_delay', _decode_regen_delay),
}
