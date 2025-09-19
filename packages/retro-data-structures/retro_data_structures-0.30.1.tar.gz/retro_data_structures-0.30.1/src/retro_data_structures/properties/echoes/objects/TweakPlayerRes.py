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
from retro_data_structures.properties.echoes.archetypes.TBallTransitionResources import TBallTransitionResources
from retro_data_structures.properties.echoes.archetypes.TGunResources import TGunResources
from retro_data_structures.properties.echoes.archetypes.TweakPlayerRes_AutoMapperIcons import TweakPlayerRes_AutoMapperIcons
from retro_data_structures.properties.echoes.archetypes.TweakPlayerRes_MapScreenIcons import TweakPlayerRes_MapScreenIcons

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakPlayerResJson(typing_extensions.TypedDict):
        instance_name: str
        auto_mapper_icons: json_util.JsonObject
        map_screen_icons: json_util.JsonObject
        ball_transition_resources: json_util.JsonObject
        cinematic_resources: json_util.JsonObject
        unknown: float
    

@dataclasses.dataclass()
class TweakPlayerRes(BaseObjectType):
    instance_name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x7fda1466, original_name='InstanceName'
        ),
    })
    auto_mapper_icons: TweakPlayerRes_AutoMapperIcons = dataclasses.field(default_factory=TweakPlayerRes_AutoMapperIcons, metadata={
        'reflection': FieldReflection[TweakPlayerRes_AutoMapperIcons](
            TweakPlayerRes_AutoMapperIcons, id=0x357741e0, original_name='AutoMapperIcons', from_json=TweakPlayerRes_AutoMapperIcons.from_json, to_json=TweakPlayerRes_AutoMapperIcons.to_json
        ),
    })
    map_screen_icons: TweakPlayerRes_MapScreenIcons = dataclasses.field(default_factory=TweakPlayerRes_MapScreenIcons, metadata={
        'reflection': FieldReflection[TweakPlayerRes_MapScreenIcons](
            TweakPlayerRes_MapScreenIcons, id=0x0d5e02a0, original_name='MapScreenIcons', from_json=TweakPlayerRes_MapScreenIcons.from_json, to_json=TweakPlayerRes_MapScreenIcons.to_json
        ),
    })
    ball_transition_resources: TBallTransitionResources = dataclasses.field(default_factory=TBallTransitionResources, metadata={
        'reflection': FieldReflection[TBallTransitionResources](
            TBallTransitionResources, id=0x279852ba, original_name='BallTransitionResources', from_json=TBallTransitionResources.from_json, to_json=TBallTransitionResources.to_json
        ),
    })
    cinematic_resources: TGunResources = dataclasses.field(default_factory=TGunResources, metadata={
        'reflection': FieldReflection[TGunResources](
            TGunResources, id=0x5e630608, original_name='CinematicResources', from_json=TGunResources.from_json, to_json=TGunResources.to_json
        ),
    })
    unknown: float = dataclasses.field(default=-0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x36ad9d19, original_name='Unknown'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return None

    def set_name(self, name: str) -> None:
        raise RuntimeError(f"{self.__class__.__name__} does not have name")

    @classmethod
    def object_type(cls) -> str:
        return 'TWPR'

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
        if property_count != 6:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fda1466
        instance_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x357741e0
        auto_mapper_icons = TweakPlayerRes_AutoMapperIcons.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d5e02a0
        map_screen_icons = TweakPlayerRes_MapScreenIcons.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x279852ba
        ball_transition_resources = TBallTransitionResources.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5e630608
        cinematic_resources = TGunResources.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x36ad9d19
        unknown = struct.unpack('>f', data.read(4))[0]
    
        return cls(instance_name, auto_mapper_icons, map_screen_icons, ball_transition_resources, cinematic_resources, unknown)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'\x7f\xda\x14f')  # 0x7fda1466
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.instance_name.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'5wA\xe0')  # 0x357741e0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.auto_mapper_icons.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\r^\x02\xa0')  # 0xd5e02a0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.map_screen_icons.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"'\x98R\xba")  # 0x279852ba
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ball_transition_resources.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'^c\x06\x08')  # 0x5e630608
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.cinematic_resources.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'6\xad\x9d\x19')  # 0x36ad9d19
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayerResJson", data)
        return cls(
            instance_name=json_data['instance_name'],
            auto_mapper_icons=TweakPlayerRes_AutoMapperIcons.from_json(json_data['auto_mapper_icons']),
            map_screen_icons=TweakPlayerRes_MapScreenIcons.from_json(json_data['map_screen_icons']),
            ball_transition_resources=TBallTransitionResources.from_json(json_data['ball_transition_resources']),
            cinematic_resources=TGunResources.from_json(json_data['cinematic_resources']),
            unknown=json_data['unknown'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'instance_name': self.instance_name,
            'auto_mapper_icons': self.auto_mapper_icons.to_json(),
            'map_screen_icons': self.map_screen_icons.to_json(),
            'ball_transition_resources': self.ball_transition_resources.to_json(),
            'cinematic_resources': self.cinematic_resources.to_json(),
            'unknown': self.unknown,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.auto_mapper_icons.dependencies_for, "auto_mapper_icons", "TweakPlayerRes_AutoMapperIcons"),
            (self.map_screen_icons.dependencies_for, "map_screen_icons", "TweakPlayerRes_MapScreenIcons"),
            (self.ball_transition_resources.dependencies_for, "ball_transition_resources", "TBallTransitionResources"),
            (self.cinematic_resources.dependencies_for, "cinematic_resources", "TGunResources"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for TweakPlayerRes.{field_name} ({field_type}): {e}"
                )


def _decode_instance_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x7fda1466: ('instance_name', _decode_instance_name),
    0x357741e0: ('auto_mapper_icons', TweakPlayerRes_AutoMapperIcons.from_stream),
    0xd5e02a0: ('map_screen_icons', TweakPlayerRes_MapScreenIcons.from_stream),
    0x279852ba: ('ball_transition_resources', TBallTransitionResources.from_stream),
    0x5e630608: ('cinematic_resources', TGunResources.from_stream),
    0x36ad9d19: ('unknown', _decode_unknown),
}
