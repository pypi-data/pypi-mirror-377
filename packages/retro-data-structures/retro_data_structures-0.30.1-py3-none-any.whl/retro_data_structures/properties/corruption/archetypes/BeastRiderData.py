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
from retro_data_structures.properties.corruption.archetypes.PlasmaBeamInfo import PlasmaBeamInfo
from retro_data_structures.properties.corruption.archetypes.RagDollData import RagDollData
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class BeastRiderDataJson(typing_extensions.TypedDict):
        phazon_lance: int
        plasma_beam_info: json_util.JsonObject
        helmet: int
        rag_doll_properties: json_util.JsonObject
        death_sound: int
    

@dataclasses.dataclass()
class BeastRiderData(BaseProperty):
    phazon_lance: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb3a26a80, original_name='PhazonLance'
        ),
    })
    plasma_beam_info: PlasmaBeamInfo = dataclasses.field(default_factory=PlasmaBeamInfo, metadata={
        'reflection': FieldReflection[PlasmaBeamInfo](
            PlasmaBeamInfo, id=0xa6001ce0, original_name='PlasmaBeamInfo', from_json=PlasmaBeamInfo.from_json, to_json=PlasmaBeamInfo.to_json
        ),
    })
    helmet: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb3343f83, original_name='Helmet'
        ),
    })
    rag_doll_properties: RagDollData = dataclasses.field(default_factory=RagDollData, metadata={
        'reflection': FieldReflection[RagDollData](
            RagDollData, id=0xa149701e, original_name='RagDollProperties', from_json=RagDollData.from_json, to_json=RagDollData.to_json
        ),
    })
    death_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc7c3f610, original_name='DeathSound'
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
        if property_count != 5:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3a26a80
        phazon_lance = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa6001ce0
        plasma_beam_info = PlasmaBeamInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3343f83
        helmet = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa149701e
        rag_doll_properties = RagDollData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc7c3f610
        death_sound = struct.unpack(">Q", data.read(8))[0]
    
        return cls(phazon_lance, plasma_beam_info, helmet, rag_doll_properties, death_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x05')  # 5 properties

        data.write(b'\xb3\xa2j\x80')  # 0xb3a26a80
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.phazon_lance))

        data.write(b'\xa6\x00\x1c\xe0')  # 0xa6001ce0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.plasma_beam_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb34?\x83')  # 0xb3343f83
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.helmet))

        data.write(b'\xa1Ip\x1e')  # 0xa149701e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.rag_doll_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc7\xc3\xf6\x10')  # 0xc7c3f610
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.death_sound))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("BeastRiderDataJson", data)
        return cls(
            phazon_lance=json_data['phazon_lance'],
            plasma_beam_info=PlasmaBeamInfo.from_json(json_data['plasma_beam_info']),
            helmet=json_data['helmet'],
            rag_doll_properties=RagDollData.from_json(json_data['rag_doll_properties']),
            death_sound=json_data['death_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'phazon_lance': self.phazon_lance,
            'plasma_beam_info': self.plasma_beam_info.to_json(),
            'helmet': self.helmet,
            'rag_doll_properties': self.rag_doll_properties.to_json(),
            'death_sound': self.death_sound,
        }


def _decode_phazon_lance(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_helmet(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_death_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xb3a26a80: ('phazon_lance', _decode_phazon_lance),
    0xa6001ce0: ('plasma_beam_info', PlasmaBeamInfo.from_stream),
    0xb3343f83: ('helmet', _decode_helmet),
    0xa149701e: ('rag_doll_properties', RagDollData.from_stream),
    0xc7c3f610: ('death_sound', _decode_death_sound),
}
