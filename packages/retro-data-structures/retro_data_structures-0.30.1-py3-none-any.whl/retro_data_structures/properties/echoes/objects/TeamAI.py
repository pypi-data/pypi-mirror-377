# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TeamAIJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        max_team_size: int
        max_melee_attackers: int
        max_ranged_attackers: int
        unknown_0x9fa9c457: int
        unknown_0x54cd2755: int
        unknown_0xc36ed15c: int
        team_formation: int
        unknown_0xd3ad55b6: float
        unknown_0x8d00b839: float
    

@dataclasses.dataclass()
class TeamAI(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    max_team_size: int = dataclasses.field(default=20, metadata={
        'reflection': FieldReflection[int](
            int, id=0xbf37e518, original_name='MaxTeamSize'
        ),
    })
    max_melee_attackers: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0xcebee4ab, original_name='MaxMeleeAttackers'
        ),
    })
    max_ranged_attackers: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7555c1ea, original_name='MaxRangedAttackers'
        ),
    })
    unknown_0x9fa9c457: int = dataclasses.field(default=30, metadata={
        'reflection': FieldReflection[int](
            int, id=0x9fa9c457, original_name='Unknown'
        ),
    })
    unknown_0x54cd2755: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x54cd2755, original_name='Unknown'
        ),
    })
    unknown_0xc36ed15c: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc36ed15c, original_name='Unknown'
        ),
    })
    team_formation: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x37a20376, original_name='TeamFormation'
        ),
    })
    unknown_0xd3ad55b6: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd3ad55b6, original_name='Unknown'
        ),
    })
    unknown_0x8d00b839: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8d00b839, original_name='Unknown'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'TMAI'

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        struct_id, size, property_count = struct.unpack(">LHH", data.read(8))
        assert struct_id == 0xFFFFFFFF
        root_size_start = data.tell() - 2

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

        assert data.tell() - root_size_start == size
        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 10:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbf37e518
        max_team_size = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcebee4ab
        max_melee_attackers = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7555c1ea
        max_ranged_attackers = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9fa9c457
        unknown_0x9fa9c457 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x54cd2755
        unknown_0x54cd2755 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc36ed15c
        unknown_0xc36ed15c = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x37a20376
        team_formation = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd3ad55b6
        unknown_0xd3ad55b6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8d00b839
        unknown_0x8d00b839 = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, max_team_size, max_melee_attackers, max_ranged_attackers, unknown_0x9fa9c457, unknown_0x54cd2755, unknown_0xc36ed15c, team_formation, unknown_0xd3ad55b6, unknown_0x8d00b839)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\n')  # 10 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbf7\xe5\x18')  # 0xbf37e518
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_team_size))

        data.write(b'\xce\xbe\xe4\xab')  # 0xcebee4ab
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_melee_attackers))

        data.write(b'uU\xc1\xea')  # 0x7555c1ea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_ranged_attackers))

        data.write(b'\x9f\xa9\xc4W')  # 0x9fa9c457
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x9fa9c457))

        data.write(b"T\xcd'U")  # 0x54cd2755
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x54cd2755))

        data.write(b'\xc3n\xd1\\')  # 0xc36ed15c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xc36ed15c))

        data.write(b'7\xa2\x03v')  # 0x37a20376
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.team_formation))

        data.write(b'\xd3\xadU\xb6')  # 0xd3ad55b6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd3ad55b6))

        data.write(b'\x8d\x00\xb89')  # 0x8d00b839
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8d00b839))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TeamAIJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            max_team_size=json_data['max_team_size'],
            max_melee_attackers=json_data['max_melee_attackers'],
            max_ranged_attackers=json_data['max_ranged_attackers'],
            unknown_0x9fa9c457=json_data['unknown_0x9fa9c457'],
            unknown_0x54cd2755=json_data['unknown_0x54cd2755'],
            unknown_0xc36ed15c=json_data['unknown_0xc36ed15c'],
            team_formation=json_data['team_formation'],
            unknown_0xd3ad55b6=json_data['unknown_0xd3ad55b6'],
            unknown_0x8d00b839=json_data['unknown_0x8d00b839'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'max_team_size': self.max_team_size,
            'max_melee_attackers': self.max_melee_attackers,
            'max_ranged_attackers': self.max_ranged_attackers,
            'unknown_0x9fa9c457': self.unknown_0x9fa9c457,
            'unknown_0x54cd2755': self.unknown_0x54cd2755,
            'unknown_0xc36ed15c': self.unknown_0xc36ed15c,
            'team_formation': self.team_formation,
            'unknown_0xd3ad55b6': self.unknown_0xd3ad55b6,
            'unknown_0x8d00b839': self.unknown_0x8d00b839,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for TeamAI.{field_name} ({field_type}): {e}"
                )


def _decode_max_team_size(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_max_melee_attackers(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_max_ranged_attackers(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x9fa9c457(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x54cd2755(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xc36ed15c(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_team_formation(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xd3ad55b6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8d00b839(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xbf37e518: ('max_team_size', _decode_max_team_size),
    0xcebee4ab: ('max_melee_attackers', _decode_max_melee_attackers),
    0x7555c1ea: ('max_ranged_attackers', _decode_max_ranged_attackers),
    0x9fa9c457: ('unknown_0x9fa9c457', _decode_unknown_0x9fa9c457),
    0x54cd2755: ('unknown_0x54cd2755', _decode_unknown_0x54cd2755),
    0xc36ed15c: ('unknown_0xc36ed15c', _decode_unknown_0xc36ed15c),
    0x37a20376: ('team_formation', _decode_team_formation),
    0xd3ad55b6: ('unknown_0xd3ad55b6', _decode_unknown_0xd3ad55b6),
    0x8d00b839: ('unknown_0x8d00b839', _decode_unknown_0x8d00b839),
}
