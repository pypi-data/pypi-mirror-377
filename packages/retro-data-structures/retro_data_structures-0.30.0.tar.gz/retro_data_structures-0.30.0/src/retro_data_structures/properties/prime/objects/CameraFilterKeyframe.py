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
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class CameraFilterKeyframeJson(typing_extensions.TypedDict):
        name: str
        active: bool
        filter_type: int
        filter_shape: int
        unknown_4: int
        unknown_5: int
        filter_color: json_util.JsonValue
        fade_in_duration: float
        fade_out_duration: float
        overlay_texture: int
    

@dataclasses.dataclass()
class CameraFilterKeyframe(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    active: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000001, original_name='Active'
        ),
    })
    filter_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000002, original_name='Filter Type'
        ),
    })
    filter_shape: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000003, original_name='Filter Shape'
        ),
    })
    unknown_4: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000004, original_name='Unknown 4'
        ),
    })
    unknown_5: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000005, original_name='Unknown 5'
        ),
    })
    filter_color: Color = dataclasses.field(default_factory=Color, metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x00000006, original_name='Filter Color', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    fade_in_duration: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000007, original_name='Fade-In Duration'
        ),
    })
    fade_out_duration: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000008, original_name='Fade-Out Duration'
        ),
    })
    overlay_texture: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000009, original_name='Overlay Texture'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    def get_name(self) -> str | None:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    @classmethod
    def object_type(cls) -> int:
        return 0x18

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        active = struct.unpack('>?', data.read(1))[0]
        filter_type = struct.unpack('>l', data.read(4))[0]
        filter_shape = struct.unpack('>l', data.read(4))[0]
        unknown_4 = struct.unpack('>l', data.read(4))[0]
        unknown_5 = struct.unpack('>l', data.read(4))[0]
        filter_color = Color.from_stream(data)
        fade_in_duration = struct.unpack('>f', data.read(4))[0]
        fade_out_duration = struct.unpack('>f', data.read(4))[0]
        overlay_texture = struct.unpack(">L", data.read(4))[0]
        return cls(name, active, filter_type, filter_shape, unknown_4, unknown_5, filter_color, fade_in_duration, fade_out_duration, overlay_texture)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\n')  # 10 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>?', self.active))
        data.write(struct.pack('>l', self.filter_type))
        data.write(struct.pack('>l', self.filter_shape))
        data.write(struct.pack('>l', self.unknown_4))
        data.write(struct.pack('>l', self.unknown_5))
        self.filter_color.to_stream(data)
        data.write(struct.pack('>f', self.fade_in_duration))
        data.write(struct.pack('>f', self.fade_out_duration))
        data.write(struct.pack(">L", self.overlay_texture))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CameraFilterKeyframeJson", data)
        return cls(
            name=json_data['name'],
            active=json_data['active'],
            filter_type=json_data['filter_type'],
            filter_shape=json_data['filter_shape'],
            unknown_4=json_data['unknown_4'],
            unknown_5=json_data['unknown_5'],
            filter_color=Color.from_json(json_data['filter_color']),
            fade_in_duration=json_data['fade_in_duration'],
            fade_out_duration=json_data['fade_out_duration'],
            overlay_texture=json_data['overlay_texture'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'active': self.active,
            'filter_type': self.filter_type,
            'filter_shape': self.filter_shape,
            'unknown_4': self.unknown_4,
            'unknown_5': self.unknown_5,
            'filter_color': self.filter_color.to_json(),
            'fade_in_duration': self.fade_in_duration,
            'fade_out_duration': self.fade_out_duration,
            'overlay_texture': self.overlay_texture,
        }

    def _dependencies_for_overlay_texture(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.overlay_texture)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_overlay_texture, "overlay_texture", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for CameraFilterKeyframe.{field_name} ({field_type}): {e}"
                )
