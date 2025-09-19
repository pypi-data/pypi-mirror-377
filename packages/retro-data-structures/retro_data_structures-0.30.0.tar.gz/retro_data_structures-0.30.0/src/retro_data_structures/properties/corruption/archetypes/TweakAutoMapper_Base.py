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
from retro_data_structures.properties.corruption.core.Color import Color
from retro_data_structures.properties.corruption.core.Spline import Spline
from retro_data_structures.properties.corruption.core.Vector import Vector

if typing.TYPE_CHECKING:
    class TweakAutoMapper_BaseJson(typing_extensions.TypedDict):
        unknown_0xcbe595d8: bool
        unknown_0x8ecb53a6: bool
        scale_move_speed_with_camera_distance: bool
        unknown_0x6bea9324: float
        unknown_0x065dd754: float
        unknown_0x57a46c09: float
        unknown_0xc87f5379: float
        unknown_0xbcc758c2: float
        unknown_0x8a4e16e4: bool
        unknown_0x2aae6322: int
        unknown_0x0c939a90: json_util.JsonObject
        unknown_0xb54255b5: float
        unknown_0x0c64cec4: float
        unknown_0xd33eb347: json_util.JsonObject
        unknown_0x335ebc7e: float
        map_screen_compass_size: float
        map_screen_compass_position: json_util.JsonValue
        map_screen_area_opacity: float
        unknown_0x533c5684: json_util.JsonValue
        unknown_0xeb383668: float
        unknown_0x27151ede: float
        unknown_0x434172c3: float
        unknown_0x68097036: float
        unknown_0x03adcf46: json_util.JsonValue
        unknown_0xd3fae283: json_util.JsonValue
        unknown_0x65d2cf45: json_util.JsonValue
        unknown_0xb5752c08: json_util.JsonValue
        unknown_0x035d01ce: json_util.JsonValue
        unknown_0x805d5fa3: json_util.JsonValue
        unknown_0x36757265: json_util.JsonValue
        unknown_0x7bdb0edf: float
        unknown_0x12221909: float
        unknown_0x38dbbc09: float
        unknown_0x30610062: float
        unknown_0xb6acea88: float
        unknown_0x73de4110: float
        unknown_0x2920db55: float
        map_screen_zoom_speed: float
        map_screen_circle_speed: float
        map_screen_move_speed: float
        unknown_0xd69f6b5c: float
        unknown_0xab82e268: json_util.JsonValue
        unknown_0x1daacfae: json_util.JsonValue
        unknown_0x47967404: float
        unknown_0x0ece1950: float
        unknown_0x9ac1bdde: float
        unknown_0x97a19386: float
        unknown_0xcb9e3a54: float
        unknown_0x2511a49b: float
        unknown_0x16c9f38e: float
        unknown_0xbc7e2e4d: float
        unknown_0x15564d32: float
        unknown_0xf5479260: float
        unknown_0x271b644e: float
        unknown_0x52dc08c1: float
        unknown_0x9980db64: float
        unknown_0x23f59057: float
        unknown_0xad3d5a3f: float
        unknown_0x3315d22b: float
        unknown_0x9e4007b6: float
        unknown_0x7a8d3d46: float
        unknown_0x2b97d64c: bool
        unknown_0xbdc57ce0: float
        unknown_0x7d59c854: float
        unknown_0x3c4ef7d2: float
        unknown_0x2b483e9f: float
        unknown_0x706f52fe: float
        unknown_0x62f9ebf6: float
        unknown_0xa9a53853: float
        unknown_0x722b1bc0: float
        unknown_0xf8252bca: float
        unknown_0xd1997970: float
        player_model_color: json_util.JsonValue
        unknown_0x5a87c156: json_util.JsonValue
        player_surface_color: json_util.JsonValue
        player_outline_color: json_util.JsonValue
        text_color: json_util.JsonValue
        text_outline_color: json_util.JsonValue
        unknown_0x1a4b8068: json_util.JsonValue
        frame_color: json_util.JsonValue
        title_color: json_util.JsonValue
        legend_background_color: json_util.JsonValue
        legend_gradient_color: json_util.JsonValue
    

@dataclasses.dataclass()
class TweakAutoMapper_Base(BaseProperty):
    unknown_0xcbe595d8: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xcbe595d8, original_name='Unknown'
        ),
    })
    unknown_0x8ecb53a6: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x8ecb53a6, original_name='Unknown'
        ),
    })
    scale_move_speed_with_camera_distance: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x30b13740, original_name='ScaleMoveSpeedWithCameraDistance'
        ),
    })
    unknown_0x6bea9324: float = dataclasses.field(default=120.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6bea9324, original_name='Unknown'
        ),
    })
    unknown_0x065dd754: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x065dd754, original_name='Unknown'
        ),
    })
    unknown_0x57a46c09: float = dataclasses.field(default=1000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x57a46c09, original_name='Unknown'
        ),
    })
    unknown_0xc87f5379: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc87f5379, original_name='Unknown'
        ),
    })
    unknown_0xbcc758c2: float = dataclasses.field(default=250.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbcc758c2, original_name='Unknown'
        ),
    })
    unknown_0x8a4e16e4: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x8a4e16e4, original_name='Unknown'
        ),
    })
    unknown_0x2aae6322: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0x2aae6322, original_name='Unknown'
        ),
    })
    unknown_0x0c939a90: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x0c939a90, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0xb54255b5: float = dataclasses.field(default=-89.9000015258789, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb54255b5, original_name='Unknown'
        ),
    })
    unknown_0x0c64cec4: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0c64cec4, original_name='Unknown'
        ),
    })
    unknown_0xd33eb347: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xd33eb347, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0x335ebc7e: float = dataclasses.field(default=75.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x335ebc7e, original_name='Unknown'
        ),
    })
    map_screen_compass_size: float = dataclasses.field(default=32.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6119d07f, original_name='MapScreenCompassSize'
        ),
    })
    map_screen_compass_position: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0xdbc799a4, original_name='MapScreenCompassPosition', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    map_screen_area_opacity: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x45be3f6b, original_name='MapScreenAreaOpacity'
        ),
    })
    unknown_0x533c5684: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x533c5684, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xeb383668: float = dataclasses.field(default=120.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xeb383668, original_name='Unknown'
        ),
    })
    unknown_0x27151ede: float = dataclasses.field(default=-45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x27151ede, original_name='Unknown'
        ),
    })
    unknown_0x434172c3: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x434172c3, original_name='Unknown'
        ),
    })
    unknown_0x68097036: float = dataclasses.field(default=0.6000000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0x68097036, original_name='Unknown'
        ),
    })
    unknown_0x03adcf46: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x03adcf46, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xd3fae283: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xd3fae283, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x65d2cf45: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x65d2cf45, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xb5752c08: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xb5752c08, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x035d01ce: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x035d01ce, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x805d5fa3: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x805d5fa3, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x36757265: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x36757265, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x7bdb0edf: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7bdb0edf, original_name='Unknown'
        ),
    })
    unknown_0x12221909: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0x12221909, original_name='Unknown'
        ),
    })
    unknown_0x38dbbc09: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x38dbbc09, original_name='Unknown'
        ),
    })
    unknown_0x30610062: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x30610062, original_name='Unknown'
        ),
    })
    unknown_0xb6acea88: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb6acea88, original_name='Unknown'
        ),
    })
    unknown_0x73de4110: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x73de4110, original_name='Unknown'
        ),
    })
    unknown_0x2920db55: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2920db55, original_name='Unknown'
        ),
    })
    map_screen_zoom_speed: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x19069725, original_name='MapScreenZoomSpeed'
        ),
    })
    map_screen_circle_speed: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5ba0de1e, original_name='MapScreenCircleSpeed'
        ),
    })
    map_screen_move_speed: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x310b37a1, original_name='MapScreenMoveSpeed'
        ),
    })
    unknown_0xd69f6b5c: float = dataclasses.field(default=2.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd69f6b5c, original_name='Unknown'
        ),
    })
    unknown_0xab82e268: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xab82e268, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x1daacfae: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x1daacfae, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x47967404: float = dataclasses.field(default=0.6000000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0x47967404, original_name='Unknown'
        ),
    })
    unknown_0x0ece1950: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0ece1950, original_name='Unknown'
        ),
    })
    unknown_0x9ac1bdde: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9ac1bdde, original_name='Unknown'
        ),
    })
    unknown_0x97a19386: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x97a19386, original_name='Unknown'
        ),
    })
    unknown_0xcb9e3a54: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcb9e3a54, original_name='Unknown'
        ),
    })
    unknown_0x2511a49b: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2511a49b, original_name='Unknown'
        ),
    })
    unknown_0x16c9f38e: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x16c9f38e, original_name='Unknown'
        ),
    })
    unknown_0xbc7e2e4d: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbc7e2e4d, original_name='Unknown'
        ),
    })
    unknown_0x15564d32: float = dataclasses.field(default=3.569999933242798, metadata={
        'reflection': FieldReflection[float](
            float, id=0x15564d32, original_name='Unknown'
        ),
    })
    unknown_0xf5479260: float = dataclasses.field(default=3.569999933242798, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf5479260, original_name='Unknown'
        ),
    })
    unknown_0x271b644e: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x271b644e, original_name='Unknown'
        ),
    })
    unknown_0x52dc08c1: float = dataclasses.field(default=24.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x52dc08c1, original_name='Unknown'
        ),
    })
    unknown_0x9980db64: float = dataclasses.field(default=348.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9980db64, original_name='Unknown'
        ),
    })
    unknown_0x23f59057: float = dataclasses.field(default=152.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x23f59057, original_name='Unknown'
        ),
    })
    unknown_0xad3d5a3f: float = dataclasses.field(default=114.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xad3d5a3f, original_name='Unknown'
        ),
    })
    unknown_0x3315d22b: float = dataclasses.field(default=0.8500000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3315d22b, original_name='Unknown'
        ),
    })
    unknown_0x9e4007b6: float = dataclasses.field(default=1.850000023841858, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9e4007b6, original_name='Unknown'
        ),
    })
    unknown_0x7a8d3d46: float = dataclasses.field(default=1.3600000143051147, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7a8d3d46, original_name='Unknown'
        ),
    })
    unknown_0x2b97d64c: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2b97d64c, original_name='Unknown'
        ),
    })
    unknown_0xbdc57ce0: float = dataclasses.field(default=800.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbdc57ce0, original_name='Unknown'
        ),
    })
    unknown_0x7d59c854: float = dataclasses.field(default=400.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7d59c854, original_name='Unknown'
        ),
    })
    unknown_0x3c4ef7d2: float = dataclasses.field(default=2000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3c4ef7d2, original_name='Unknown'
        ),
    })
    unknown_0x2b483e9f: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2b483e9f, original_name='Unknown'
        ),
    })
    unknown_0x706f52fe: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x706f52fe, original_name='Unknown'
        ),
    })
    unknown_0x62f9ebf6: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x62f9ebf6, original_name='Unknown'
        ),
    })
    unknown_0xa9a53853: float = dataclasses.field(default=0.6349999904632568, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa9a53853, original_name='Unknown'
        ),
    })
    unknown_0x722b1bc0: float = dataclasses.field(default=-0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0x722b1bc0, original_name='Unknown'
        ),
    })
    unknown_0xf8252bca: float = dataclasses.field(default=1.600000023841858, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf8252bca, original_name='Unknown'
        ),
    })
    unknown_0xd1997970: float = dataclasses.field(default=1.2000000476837158, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd1997970, original_name='Unknown'
        ),
    })
    player_model_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x4c3fc933, original_name='PlayerModelColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x5a87c156: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x5a87c156, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    player_surface_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x9c0c5318, original_name='PlayerSurfaceColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    player_outline_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x2a247ede, original_name='PlayerOutlineColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    text_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x44303a9c, original_name='TextColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    text_outline_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xf2e13506, original_name='TextOutlineColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x1a4b8068: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x1a4b8068, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    frame_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xa485372c, original_name='FrameColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    title_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x536647d5, original_name='TitleColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    legend_background_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xa6b633fa, original_name='LegendBackgroundColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    legend_gradient_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x01cea7f9, original_name='LegendGradientColor', from_json=Color.from_json, to_json=Color.to_json
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
        if property_count != 83:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcbe595d8
        unknown_0xcbe595d8 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8ecb53a6
        unknown_0x8ecb53a6 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x30b13740
        scale_move_speed_with_camera_distance = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6bea9324
        unknown_0x6bea9324 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x065dd754
        unknown_0x065dd754 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x57a46c09
        unknown_0x57a46c09 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc87f5379
        unknown_0xc87f5379 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbcc758c2
        unknown_0xbcc758c2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8a4e16e4
        unknown_0x8a4e16e4 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2aae6322
        unknown_0x2aae6322 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0c939a90
        unknown_0x0c939a90 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb54255b5
        unknown_0xb54255b5 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0c64cec4
        unknown_0x0c64cec4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd33eb347
        unknown_0xd33eb347 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x335ebc7e
        unknown_0x335ebc7e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6119d07f
        map_screen_compass_size = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdbc799a4
        map_screen_compass_position = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x45be3f6b
        map_screen_area_opacity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x533c5684
        unknown_0x533c5684 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeb383668
        unknown_0xeb383668 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x27151ede
        unknown_0x27151ede = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x434172c3
        unknown_0x434172c3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x68097036
        unknown_0x68097036 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x03adcf46
        unknown_0x03adcf46 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd3fae283
        unknown_0xd3fae283 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x65d2cf45
        unknown_0x65d2cf45 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb5752c08
        unknown_0xb5752c08 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x035d01ce
        unknown_0x035d01ce = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x805d5fa3
        unknown_0x805d5fa3 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x36757265
        unknown_0x36757265 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7bdb0edf
        unknown_0x7bdb0edf = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x12221909
        unknown_0x12221909 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x38dbbc09
        unknown_0x38dbbc09 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x30610062
        unknown_0x30610062 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb6acea88
        unknown_0xb6acea88 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x73de4110
        unknown_0x73de4110 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2920db55
        unknown_0x2920db55 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x19069725
        map_screen_zoom_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5ba0de1e
        map_screen_circle_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x310b37a1
        map_screen_move_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd69f6b5c
        unknown_0xd69f6b5c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xab82e268
        unknown_0xab82e268 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1daacfae
        unknown_0x1daacfae = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x47967404
        unknown_0x47967404 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0ece1950
        unknown_0x0ece1950 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9ac1bdde
        unknown_0x9ac1bdde = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x97a19386
        unknown_0x97a19386 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcb9e3a54
        unknown_0xcb9e3a54 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2511a49b
        unknown_0x2511a49b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x16c9f38e
        unknown_0x16c9f38e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbc7e2e4d
        unknown_0xbc7e2e4d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x15564d32
        unknown_0x15564d32 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf5479260
        unknown_0xf5479260 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x271b644e
        unknown_0x271b644e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x52dc08c1
        unknown_0x52dc08c1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9980db64
        unknown_0x9980db64 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x23f59057
        unknown_0x23f59057 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad3d5a3f
        unknown_0xad3d5a3f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3315d22b
        unknown_0x3315d22b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9e4007b6
        unknown_0x9e4007b6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7a8d3d46
        unknown_0x7a8d3d46 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b97d64c
        unknown_0x2b97d64c = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbdc57ce0
        unknown_0xbdc57ce0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7d59c854
        unknown_0x7d59c854 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3c4ef7d2
        unknown_0x3c4ef7d2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b483e9f
        unknown_0x2b483e9f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x706f52fe
        unknown_0x706f52fe = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x62f9ebf6
        unknown_0x62f9ebf6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa9a53853
        unknown_0xa9a53853 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x722b1bc0
        unknown_0x722b1bc0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf8252bca
        unknown_0xf8252bca = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd1997970
        unknown_0xd1997970 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4c3fc933
        player_model_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5a87c156
        unknown_0x5a87c156 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9c0c5318
        player_surface_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2a247ede
        player_outline_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x44303a9c
        text_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf2e13506
        text_outline_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a4b8068
        unknown_0x1a4b8068 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa485372c
        frame_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x536647d5
        title_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa6b633fa
        legend_background_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x01cea7f9
        legend_gradient_color = Color.from_stream(data)
    
        return cls(unknown_0xcbe595d8, unknown_0x8ecb53a6, scale_move_speed_with_camera_distance, unknown_0x6bea9324, unknown_0x065dd754, unknown_0x57a46c09, unknown_0xc87f5379, unknown_0xbcc758c2, unknown_0x8a4e16e4, unknown_0x2aae6322, unknown_0x0c939a90, unknown_0xb54255b5, unknown_0x0c64cec4, unknown_0xd33eb347, unknown_0x335ebc7e, map_screen_compass_size, map_screen_compass_position, map_screen_area_opacity, unknown_0x533c5684, unknown_0xeb383668, unknown_0x27151ede, unknown_0x434172c3, unknown_0x68097036, unknown_0x03adcf46, unknown_0xd3fae283, unknown_0x65d2cf45, unknown_0xb5752c08, unknown_0x035d01ce, unknown_0x805d5fa3, unknown_0x36757265, unknown_0x7bdb0edf, unknown_0x12221909, unknown_0x38dbbc09, unknown_0x30610062, unknown_0xb6acea88, unknown_0x73de4110, unknown_0x2920db55, map_screen_zoom_speed, map_screen_circle_speed, map_screen_move_speed, unknown_0xd69f6b5c, unknown_0xab82e268, unknown_0x1daacfae, unknown_0x47967404, unknown_0x0ece1950, unknown_0x9ac1bdde, unknown_0x97a19386, unknown_0xcb9e3a54, unknown_0x2511a49b, unknown_0x16c9f38e, unknown_0xbc7e2e4d, unknown_0x15564d32, unknown_0xf5479260, unknown_0x271b644e, unknown_0x52dc08c1, unknown_0x9980db64, unknown_0x23f59057, unknown_0xad3d5a3f, unknown_0x3315d22b, unknown_0x9e4007b6, unknown_0x7a8d3d46, unknown_0x2b97d64c, unknown_0xbdc57ce0, unknown_0x7d59c854, unknown_0x3c4ef7d2, unknown_0x2b483e9f, unknown_0x706f52fe, unknown_0x62f9ebf6, unknown_0xa9a53853, unknown_0x722b1bc0, unknown_0xf8252bca, unknown_0xd1997970, player_model_color, unknown_0x5a87c156, player_surface_color, player_outline_color, text_color, text_outline_color, unknown_0x1a4b8068, frame_color, title_color, legend_background_color, legend_gradient_color)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00S')  # 83 properties

        data.write(b'\xcb\xe5\x95\xd8')  # 0xcbe595d8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xcbe595d8))

        data.write(b'\x8e\xcbS\xa6')  # 0x8ecb53a6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x8ecb53a6))

        data.write(b'0\xb17@')  # 0x30b13740
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.scale_move_speed_with_camera_distance))

        data.write(b'k\xea\x93$')  # 0x6bea9324
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6bea9324))

        data.write(b'\x06]\xd7T')  # 0x65dd754
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x065dd754))

        data.write(b'W\xa4l\t')  # 0x57a46c09
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x57a46c09))

        data.write(b'\xc8\x7fSy')  # 0xc87f5379
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc87f5379))

        data.write(b'\xbc\xc7X\xc2')  # 0xbcc758c2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbcc758c2))

        data.write(b'\x8aN\x16\xe4')  # 0x8a4e16e4
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x8a4e16e4))

        data.write(b'*\xaec"')  # 0x2aae6322
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x2aae6322))

        data.write(b'\x0c\x93\x9a\x90')  # 0xc939a90
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x0c939a90.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb5BU\xb5')  # 0xb54255b5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb54255b5))

        data.write(b'\x0cd\xce\xc4')  # 0xc64cec4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0c64cec4))

        data.write(b'\xd3>\xb3G')  # 0xd33eb347
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xd33eb347.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'3^\xbc~')  # 0x335ebc7e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x335ebc7e))

        data.write(b'a\x19\xd0\x7f')  # 0x6119d07f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.map_screen_compass_size))

        data.write(b'\xdb\xc7\x99\xa4')  # 0xdbc799a4
        data.write(b'\x00\x0c')  # size
        self.map_screen_compass_position.to_stream(data)

        data.write(b'E\xbe?k')  # 0x45be3f6b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.map_screen_area_opacity))

        data.write(b'S<V\x84')  # 0x533c5684
        data.write(b'\x00\x10')  # size
        self.unknown_0x533c5684.to_stream(data)

        data.write(b'\xeb86h')  # 0xeb383668
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xeb383668))

        data.write(b"'\x15\x1e\xde")  # 0x27151ede
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x27151ede))

        data.write(b'CAr\xc3')  # 0x434172c3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x434172c3))

        data.write(b'h\tp6')  # 0x68097036
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x68097036))

        data.write(b'\x03\xad\xcfF')  # 0x3adcf46
        data.write(b'\x00\x10')  # size
        self.unknown_0x03adcf46.to_stream(data)

        data.write(b'\xd3\xfa\xe2\x83')  # 0xd3fae283
        data.write(b'\x00\x10')  # size
        self.unknown_0xd3fae283.to_stream(data)

        data.write(b'e\xd2\xcfE')  # 0x65d2cf45
        data.write(b'\x00\x10')  # size
        self.unknown_0x65d2cf45.to_stream(data)

        data.write(b'\xb5u,\x08')  # 0xb5752c08
        data.write(b'\x00\x10')  # size
        self.unknown_0xb5752c08.to_stream(data)

        data.write(b'\x03]\x01\xce')  # 0x35d01ce
        data.write(b'\x00\x10')  # size
        self.unknown_0x035d01ce.to_stream(data)

        data.write(b'\x80]_\xa3')  # 0x805d5fa3
        data.write(b'\x00\x10')  # size
        self.unknown_0x805d5fa3.to_stream(data)

        data.write(b'6ure')  # 0x36757265
        data.write(b'\x00\x10')  # size
        self.unknown_0x36757265.to_stream(data)

        data.write(b'{\xdb\x0e\xdf')  # 0x7bdb0edf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7bdb0edf))

        data.write(b'\x12"\x19\t')  # 0x12221909
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x12221909))

        data.write(b'8\xdb\xbc\t')  # 0x38dbbc09
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x38dbbc09))

        data.write(b'0a\x00b')  # 0x30610062
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x30610062))

        data.write(b'\xb6\xac\xea\x88')  # 0xb6acea88
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb6acea88))

        data.write(b's\xdeA\x10')  # 0x73de4110
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x73de4110))

        data.write(b') \xdbU')  # 0x2920db55
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2920db55))

        data.write(b'\x19\x06\x97%')  # 0x19069725
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.map_screen_zoom_speed))

        data.write(b'[\xa0\xde\x1e')  # 0x5ba0de1e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.map_screen_circle_speed))

        data.write(b'1\x0b7\xa1')  # 0x310b37a1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.map_screen_move_speed))

        data.write(b'\xd6\x9fk\\')  # 0xd69f6b5c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd69f6b5c))

        data.write(b'\xab\x82\xe2h')  # 0xab82e268
        data.write(b'\x00\x10')  # size
        self.unknown_0xab82e268.to_stream(data)

        data.write(b'\x1d\xaa\xcf\xae')  # 0x1daacfae
        data.write(b'\x00\x10')  # size
        self.unknown_0x1daacfae.to_stream(data)

        data.write(b'G\x96t\x04')  # 0x47967404
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x47967404))

        data.write(b'\x0e\xce\x19P')  # 0xece1950
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0ece1950))

        data.write(b'\x9a\xc1\xbd\xde')  # 0x9ac1bdde
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9ac1bdde))

        data.write(b'\x97\xa1\x93\x86')  # 0x97a19386
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x97a19386))

        data.write(b'\xcb\x9e:T')  # 0xcb9e3a54
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcb9e3a54))

        data.write(b'%\x11\xa4\x9b')  # 0x2511a49b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2511a49b))

        data.write(b'\x16\xc9\xf3\x8e')  # 0x16c9f38e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x16c9f38e))

        data.write(b'\xbc~.M')  # 0xbc7e2e4d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbc7e2e4d))

        data.write(b'\x15VM2')  # 0x15564d32
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x15564d32))

        data.write(b'\xf5G\x92`')  # 0xf5479260
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf5479260))

        data.write(b"'\x1bdN")  # 0x271b644e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x271b644e))

        data.write(b'R\xdc\x08\xc1')  # 0x52dc08c1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x52dc08c1))

        data.write(b'\x99\x80\xdbd')  # 0x9980db64
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9980db64))

        data.write(b'#\xf5\x90W')  # 0x23f59057
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x23f59057))

        data.write(b'\xad=Z?')  # 0xad3d5a3f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xad3d5a3f))

        data.write(b'3\x15\xd2+')  # 0x3315d22b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3315d22b))

        data.write(b'\x9e@\x07\xb6')  # 0x9e4007b6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9e4007b6))

        data.write(b'z\x8d=F')  # 0x7a8d3d46
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7a8d3d46))

        data.write(b'+\x97\xd6L')  # 0x2b97d64c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x2b97d64c))

        data.write(b'\xbd\xc5|\xe0')  # 0xbdc57ce0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbdc57ce0))

        data.write(b'}Y\xc8T')  # 0x7d59c854
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7d59c854))

        data.write(b'<N\xf7\xd2')  # 0x3c4ef7d2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3c4ef7d2))

        data.write(b'+H>\x9f')  # 0x2b483e9f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2b483e9f))

        data.write(b'poR\xfe')  # 0x706f52fe
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x706f52fe))

        data.write(b'b\xf9\xeb\xf6')  # 0x62f9ebf6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x62f9ebf6))

        data.write(b'\xa9\xa58S')  # 0xa9a53853
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa9a53853))

        data.write(b'r+\x1b\xc0')  # 0x722b1bc0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x722b1bc0))

        data.write(b'\xf8%+\xca')  # 0xf8252bca
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf8252bca))

        data.write(b'\xd1\x99yp')  # 0xd1997970
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd1997970))

        data.write(b'L?\xc93')  # 0x4c3fc933
        data.write(b'\x00\x10')  # size
        self.player_model_color.to_stream(data)

        data.write(b'Z\x87\xc1V')  # 0x5a87c156
        data.write(b'\x00\x10')  # size
        self.unknown_0x5a87c156.to_stream(data)

        data.write(b'\x9c\x0cS\x18')  # 0x9c0c5318
        data.write(b'\x00\x10')  # size
        self.player_surface_color.to_stream(data)

        data.write(b'*$~\xde')  # 0x2a247ede
        data.write(b'\x00\x10')  # size
        self.player_outline_color.to_stream(data)

        data.write(b'D0:\x9c')  # 0x44303a9c
        data.write(b'\x00\x10')  # size
        self.text_color.to_stream(data)

        data.write(b'\xf2\xe15\x06')  # 0xf2e13506
        data.write(b'\x00\x10')  # size
        self.text_outline_color.to_stream(data)

        data.write(b'\x1aK\x80h')  # 0x1a4b8068
        data.write(b'\x00\x10')  # size
        self.unknown_0x1a4b8068.to_stream(data)

        data.write(b'\xa4\x857,')  # 0xa485372c
        data.write(b'\x00\x10')  # size
        self.frame_color.to_stream(data)

        data.write(b'SfG\xd5')  # 0x536647d5
        data.write(b'\x00\x10')  # size
        self.title_color.to_stream(data)

        data.write(b'\xa6\xb63\xfa')  # 0xa6b633fa
        data.write(b'\x00\x10')  # size
        self.legend_background_color.to_stream(data)

        data.write(b'\x01\xce\xa7\xf9')  # 0x1cea7f9
        data.write(b'\x00\x10')  # size
        self.legend_gradient_color.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakAutoMapper_BaseJson", data)
        return cls(
            unknown_0xcbe595d8=json_data['unknown_0xcbe595d8'],
            unknown_0x8ecb53a6=json_data['unknown_0x8ecb53a6'],
            scale_move_speed_with_camera_distance=json_data['scale_move_speed_with_camera_distance'],
            unknown_0x6bea9324=json_data['unknown_0x6bea9324'],
            unknown_0x065dd754=json_data['unknown_0x065dd754'],
            unknown_0x57a46c09=json_data['unknown_0x57a46c09'],
            unknown_0xc87f5379=json_data['unknown_0xc87f5379'],
            unknown_0xbcc758c2=json_data['unknown_0xbcc758c2'],
            unknown_0x8a4e16e4=json_data['unknown_0x8a4e16e4'],
            unknown_0x2aae6322=json_data['unknown_0x2aae6322'],
            unknown_0x0c939a90=Spline.from_json(json_data['unknown_0x0c939a90']),
            unknown_0xb54255b5=json_data['unknown_0xb54255b5'],
            unknown_0x0c64cec4=json_data['unknown_0x0c64cec4'],
            unknown_0xd33eb347=Spline.from_json(json_data['unknown_0xd33eb347']),
            unknown_0x335ebc7e=json_data['unknown_0x335ebc7e'],
            map_screen_compass_size=json_data['map_screen_compass_size'],
            map_screen_compass_position=Vector.from_json(json_data['map_screen_compass_position']),
            map_screen_area_opacity=json_data['map_screen_area_opacity'],
            unknown_0x533c5684=Color.from_json(json_data['unknown_0x533c5684']),
            unknown_0xeb383668=json_data['unknown_0xeb383668'],
            unknown_0x27151ede=json_data['unknown_0x27151ede'],
            unknown_0x434172c3=json_data['unknown_0x434172c3'],
            unknown_0x68097036=json_data['unknown_0x68097036'],
            unknown_0x03adcf46=Color.from_json(json_data['unknown_0x03adcf46']),
            unknown_0xd3fae283=Color.from_json(json_data['unknown_0xd3fae283']),
            unknown_0x65d2cf45=Color.from_json(json_data['unknown_0x65d2cf45']),
            unknown_0xb5752c08=Color.from_json(json_data['unknown_0xb5752c08']),
            unknown_0x035d01ce=Color.from_json(json_data['unknown_0x035d01ce']),
            unknown_0x805d5fa3=Color.from_json(json_data['unknown_0x805d5fa3']),
            unknown_0x36757265=Color.from_json(json_data['unknown_0x36757265']),
            unknown_0x7bdb0edf=json_data['unknown_0x7bdb0edf'],
            unknown_0x12221909=json_data['unknown_0x12221909'],
            unknown_0x38dbbc09=json_data['unknown_0x38dbbc09'],
            unknown_0x30610062=json_data['unknown_0x30610062'],
            unknown_0xb6acea88=json_data['unknown_0xb6acea88'],
            unknown_0x73de4110=json_data['unknown_0x73de4110'],
            unknown_0x2920db55=json_data['unknown_0x2920db55'],
            map_screen_zoom_speed=json_data['map_screen_zoom_speed'],
            map_screen_circle_speed=json_data['map_screen_circle_speed'],
            map_screen_move_speed=json_data['map_screen_move_speed'],
            unknown_0xd69f6b5c=json_data['unknown_0xd69f6b5c'],
            unknown_0xab82e268=Color.from_json(json_data['unknown_0xab82e268']),
            unknown_0x1daacfae=Color.from_json(json_data['unknown_0x1daacfae']),
            unknown_0x47967404=json_data['unknown_0x47967404'],
            unknown_0x0ece1950=json_data['unknown_0x0ece1950'],
            unknown_0x9ac1bdde=json_data['unknown_0x9ac1bdde'],
            unknown_0x97a19386=json_data['unknown_0x97a19386'],
            unknown_0xcb9e3a54=json_data['unknown_0xcb9e3a54'],
            unknown_0x2511a49b=json_data['unknown_0x2511a49b'],
            unknown_0x16c9f38e=json_data['unknown_0x16c9f38e'],
            unknown_0xbc7e2e4d=json_data['unknown_0xbc7e2e4d'],
            unknown_0x15564d32=json_data['unknown_0x15564d32'],
            unknown_0xf5479260=json_data['unknown_0xf5479260'],
            unknown_0x271b644e=json_data['unknown_0x271b644e'],
            unknown_0x52dc08c1=json_data['unknown_0x52dc08c1'],
            unknown_0x9980db64=json_data['unknown_0x9980db64'],
            unknown_0x23f59057=json_data['unknown_0x23f59057'],
            unknown_0xad3d5a3f=json_data['unknown_0xad3d5a3f'],
            unknown_0x3315d22b=json_data['unknown_0x3315d22b'],
            unknown_0x9e4007b6=json_data['unknown_0x9e4007b6'],
            unknown_0x7a8d3d46=json_data['unknown_0x7a8d3d46'],
            unknown_0x2b97d64c=json_data['unknown_0x2b97d64c'],
            unknown_0xbdc57ce0=json_data['unknown_0xbdc57ce0'],
            unknown_0x7d59c854=json_data['unknown_0x7d59c854'],
            unknown_0x3c4ef7d2=json_data['unknown_0x3c4ef7d2'],
            unknown_0x2b483e9f=json_data['unknown_0x2b483e9f'],
            unknown_0x706f52fe=json_data['unknown_0x706f52fe'],
            unknown_0x62f9ebf6=json_data['unknown_0x62f9ebf6'],
            unknown_0xa9a53853=json_data['unknown_0xa9a53853'],
            unknown_0x722b1bc0=json_data['unknown_0x722b1bc0'],
            unknown_0xf8252bca=json_data['unknown_0xf8252bca'],
            unknown_0xd1997970=json_data['unknown_0xd1997970'],
            player_model_color=Color.from_json(json_data['player_model_color']),
            unknown_0x5a87c156=Color.from_json(json_data['unknown_0x5a87c156']),
            player_surface_color=Color.from_json(json_data['player_surface_color']),
            player_outline_color=Color.from_json(json_data['player_outline_color']),
            text_color=Color.from_json(json_data['text_color']),
            text_outline_color=Color.from_json(json_data['text_outline_color']),
            unknown_0x1a4b8068=Color.from_json(json_data['unknown_0x1a4b8068']),
            frame_color=Color.from_json(json_data['frame_color']),
            title_color=Color.from_json(json_data['title_color']),
            legend_background_color=Color.from_json(json_data['legend_background_color']),
            legend_gradient_color=Color.from_json(json_data['legend_gradient_color']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xcbe595d8': self.unknown_0xcbe595d8,
            'unknown_0x8ecb53a6': self.unknown_0x8ecb53a6,
            'scale_move_speed_with_camera_distance': self.scale_move_speed_with_camera_distance,
            'unknown_0x6bea9324': self.unknown_0x6bea9324,
            'unknown_0x065dd754': self.unknown_0x065dd754,
            'unknown_0x57a46c09': self.unknown_0x57a46c09,
            'unknown_0xc87f5379': self.unknown_0xc87f5379,
            'unknown_0xbcc758c2': self.unknown_0xbcc758c2,
            'unknown_0x8a4e16e4': self.unknown_0x8a4e16e4,
            'unknown_0x2aae6322': self.unknown_0x2aae6322,
            'unknown_0x0c939a90': self.unknown_0x0c939a90.to_json(),
            'unknown_0xb54255b5': self.unknown_0xb54255b5,
            'unknown_0x0c64cec4': self.unknown_0x0c64cec4,
            'unknown_0xd33eb347': self.unknown_0xd33eb347.to_json(),
            'unknown_0x335ebc7e': self.unknown_0x335ebc7e,
            'map_screen_compass_size': self.map_screen_compass_size,
            'map_screen_compass_position': self.map_screen_compass_position.to_json(),
            'map_screen_area_opacity': self.map_screen_area_opacity,
            'unknown_0x533c5684': self.unknown_0x533c5684.to_json(),
            'unknown_0xeb383668': self.unknown_0xeb383668,
            'unknown_0x27151ede': self.unknown_0x27151ede,
            'unknown_0x434172c3': self.unknown_0x434172c3,
            'unknown_0x68097036': self.unknown_0x68097036,
            'unknown_0x03adcf46': self.unknown_0x03adcf46.to_json(),
            'unknown_0xd3fae283': self.unknown_0xd3fae283.to_json(),
            'unknown_0x65d2cf45': self.unknown_0x65d2cf45.to_json(),
            'unknown_0xb5752c08': self.unknown_0xb5752c08.to_json(),
            'unknown_0x035d01ce': self.unknown_0x035d01ce.to_json(),
            'unknown_0x805d5fa3': self.unknown_0x805d5fa3.to_json(),
            'unknown_0x36757265': self.unknown_0x36757265.to_json(),
            'unknown_0x7bdb0edf': self.unknown_0x7bdb0edf,
            'unknown_0x12221909': self.unknown_0x12221909,
            'unknown_0x38dbbc09': self.unknown_0x38dbbc09,
            'unknown_0x30610062': self.unknown_0x30610062,
            'unknown_0xb6acea88': self.unknown_0xb6acea88,
            'unknown_0x73de4110': self.unknown_0x73de4110,
            'unknown_0x2920db55': self.unknown_0x2920db55,
            'map_screen_zoom_speed': self.map_screen_zoom_speed,
            'map_screen_circle_speed': self.map_screen_circle_speed,
            'map_screen_move_speed': self.map_screen_move_speed,
            'unknown_0xd69f6b5c': self.unknown_0xd69f6b5c,
            'unknown_0xab82e268': self.unknown_0xab82e268.to_json(),
            'unknown_0x1daacfae': self.unknown_0x1daacfae.to_json(),
            'unknown_0x47967404': self.unknown_0x47967404,
            'unknown_0x0ece1950': self.unknown_0x0ece1950,
            'unknown_0x9ac1bdde': self.unknown_0x9ac1bdde,
            'unknown_0x97a19386': self.unknown_0x97a19386,
            'unknown_0xcb9e3a54': self.unknown_0xcb9e3a54,
            'unknown_0x2511a49b': self.unknown_0x2511a49b,
            'unknown_0x16c9f38e': self.unknown_0x16c9f38e,
            'unknown_0xbc7e2e4d': self.unknown_0xbc7e2e4d,
            'unknown_0x15564d32': self.unknown_0x15564d32,
            'unknown_0xf5479260': self.unknown_0xf5479260,
            'unknown_0x271b644e': self.unknown_0x271b644e,
            'unknown_0x52dc08c1': self.unknown_0x52dc08c1,
            'unknown_0x9980db64': self.unknown_0x9980db64,
            'unknown_0x23f59057': self.unknown_0x23f59057,
            'unknown_0xad3d5a3f': self.unknown_0xad3d5a3f,
            'unknown_0x3315d22b': self.unknown_0x3315d22b,
            'unknown_0x9e4007b6': self.unknown_0x9e4007b6,
            'unknown_0x7a8d3d46': self.unknown_0x7a8d3d46,
            'unknown_0x2b97d64c': self.unknown_0x2b97d64c,
            'unknown_0xbdc57ce0': self.unknown_0xbdc57ce0,
            'unknown_0x7d59c854': self.unknown_0x7d59c854,
            'unknown_0x3c4ef7d2': self.unknown_0x3c4ef7d2,
            'unknown_0x2b483e9f': self.unknown_0x2b483e9f,
            'unknown_0x706f52fe': self.unknown_0x706f52fe,
            'unknown_0x62f9ebf6': self.unknown_0x62f9ebf6,
            'unknown_0xa9a53853': self.unknown_0xa9a53853,
            'unknown_0x722b1bc0': self.unknown_0x722b1bc0,
            'unknown_0xf8252bca': self.unknown_0xf8252bca,
            'unknown_0xd1997970': self.unknown_0xd1997970,
            'player_model_color': self.player_model_color.to_json(),
            'unknown_0x5a87c156': self.unknown_0x5a87c156.to_json(),
            'player_surface_color': self.player_surface_color.to_json(),
            'player_outline_color': self.player_outline_color.to_json(),
            'text_color': self.text_color.to_json(),
            'text_outline_color': self.text_outline_color.to_json(),
            'unknown_0x1a4b8068': self.unknown_0x1a4b8068.to_json(),
            'frame_color': self.frame_color.to_json(),
            'title_color': self.title_color.to_json(),
            'legend_background_color': self.legend_background_color.to_json(),
            'legend_gradient_color': self.legend_gradient_color.to_json(),
        }


def _decode_unknown_0xcbe595d8(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x8ecb53a6(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_scale_move_speed_with_camera_distance(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x6bea9324(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x065dd754(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x57a46c09(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc87f5379(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbcc758c2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8a4e16e4(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x2aae6322(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xb54255b5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0c64cec4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x335ebc7e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_map_screen_compass_size(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_map_screen_compass_position(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_map_screen_area_opacity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x533c5684(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xeb383668(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x27151ede(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x434172c3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x68097036(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x03adcf46(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xd3fae283(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x65d2cf45(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xb5752c08(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x035d01ce(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x805d5fa3(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x36757265(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x7bdb0edf(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x12221909(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x38dbbc09(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x30610062(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb6acea88(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x73de4110(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2920db55(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_map_screen_zoom_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_map_screen_circle_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_map_screen_move_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd69f6b5c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xab82e268(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x1daacfae(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x47967404(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0ece1950(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9ac1bdde(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x97a19386(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcb9e3a54(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2511a49b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x16c9f38e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbc7e2e4d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x15564d32(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf5479260(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x271b644e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x52dc08c1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9980db64(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x23f59057(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xad3d5a3f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3315d22b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9e4007b6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7a8d3d46(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2b97d64c(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xbdc57ce0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7d59c854(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3c4ef7d2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2b483e9f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x706f52fe(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x62f9ebf6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa9a53853(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x722b1bc0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf8252bca(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd1997970(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_player_model_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x5a87c156(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_player_surface_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_player_outline_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_text_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_text_outline_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x1a4b8068(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_frame_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_title_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_legend_background_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_legend_gradient_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xcbe595d8: ('unknown_0xcbe595d8', _decode_unknown_0xcbe595d8),
    0x8ecb53a6: ('unknown_0x8ecb53a6', _decode_unknown_0x8ecb53a6),
    0x30b13740: ('scale_move_speed_with_camera_distance', _decode_scale_move_speed_with_camera_distance),
    0x6bea9324: ('unknown_0x6bea9324', _decode_unknown_0x6bea9324),
    0x65dd754: ('unknown_0x065dd754', _decode_unknown_0x065dd754),
    0x57a46c09: ('unknown_0x57a46c09', _decode_unknown_0x57a46c09),
    0xc87f5379: ('unknown_0xc87f5379', _decode_unknown_0xc87f5379),
    0xbcc758c2: ('unknown_0xbcc758c2', _decode_unknown_0xbcc758c2),
    0x8a4e16e4: ('unknown_0x8a4e16e4', _decode_unknown_0x8a4e16e4),
    0x2aae6322: ('unknown_0x2aae6322', _decode_unknown_0x2aae6322),
    0xc939a90: ('unknown_0x0c939a90', Spline.from_stream),
    0xb54255b5: ('unknown_0xb54255b5', _decode_unknown_0xb54255b5),
    0xc64cec4: ('unknown_0x0c64cec4', _decode_unknown_0x0c64cec4),
    0xd33eb347: ('unknown_0xd33eb347', Spline.from_stream),
    0x335ebc7e: ('unknown_0x335ebc7e', _decode_unknown_0x335ebc7e),
    0x6119d07f: ('map_screen_compass_size', _decode_map_screen_compass_size),
    0xdbc799a4: ('map_screen_compass_position', _decode_map_screen_compass_position),
    0x45be3f6b: ('map_screen_area_opacity', _decode_map_screen_area_opacity),
    0x533c5684: ('unknown_0x533c5684', _decode_unknown_0x533c5684),
    0xeb383668: ('unknown_0xeb383668', _decode_unknown_0xeb383668),
    0x27151ede: ('unknown_0x27151ede', _decode_unknown_0x27151ede),
    0x434172c3: ('unknown_0x434172c3', _decode_unknown_0x434172c3),
    0x68097036: ('unknown_0x68097036', _decode_unknown_0x68097036),
    0x3adcf46: ('unknown_0x03adcf46', _decode_unknown_0x03adcf46),
    0xd3fae283: ('unknown_0xd3fae283', _decode_unknown_0xd3fae283),
    0x65d2cf45: ('unknown_0x65d2cf45', _decode_unknown_0x65d2cf45),
    0xb5752c08: ('unknown_0xb5752c08', _decode_unknown_0xb5752c08),
    0x35d01ce: ('unknown_0x035d01ce', _decode_unknown_0x035d01ce),
    0x805d5fa3: ('unknown_0x805d5fa3', _decode_unknown_0x805d5fa3),
    0x36757265: ('unknown_0x36757265', _decode_unknown_0x36757265),
    0x7bdb0edf: ('unknown_0x7bdb0edf', _decode_unknown_0x7bdb0edf),
    0x12221909: ('unknown_0x12221909', _decode_unknown_0x12221909),
    0x38dbbc09: ('unknown_0x38dbbc09', _decode_unknown_0x38dbbc09),
    0x30610062: ('unknown_0x30610062', _decode_unknown_0x30610062),
    0xb6acea88: ('unknown_0xb6acea88', _decode_unknown_0xb6acea88),
    0x73de4110: ('unknown_0x73de4110', _decode_unknown_0x73de4110),
    0x2920db55: ('unknown_0x2920db55', _decode_unknown_0x2920db55),
    0x19069725: ('map_screen_zoom_speed', _decode_map_screen_zoom_speed),
    0x5ba0de1e: ('map_screen_circle_speed', _decode_map_screen_circle_speed),
    0x310b37a1: ('map_screen_move_speed', _decode_map_screen_move_speed),
    0xd69f6b5c: ('unknown_0xd69f6b5c', _decode_unknown_0xd69f6b5c),
    0xab82e268: ('unknown_0xab82e268', _decode_unknown_0xab82e268),
    0x1daacfae: ('unknown_0x1daacfae', _decode_unknown_0x1daacfae),
    0x47967404: ('unknown_0x47967404', _decode_unknown_0x47967404),
    0xece1950: ('unknown_0x0ece1950', _decode_unknown_0x0ece1950),
    0x9ac1bdde: ('unknown_0x9ac1bdde', _decode_unknown_0x9ac1bdde),
    0x97a19386: ('unknown_0x97a19386', _decode_unknown_0x97a19386),
    0xcb9e3a54: ('unknown_0xcb9e3a54', _decode_unknown_0xcb9e3a54),
    0x2511a49b: ('unknown_0x2511a49b', _decode_unknown_0x2511a49b),
    0x16c9f38e: ('unknown_0x16c9f38e', _decode_unknown_0x16c9f38e),
    0xbc7e2e4d: ('unknown_0xbc7e2e4d', _decode_unknown_0xbc7e2e4d),
    0x15564d32: ('unknown_0x15564d32', _decode_unknown_0x15564d32),
    0xf5479260: ('unknown_0xf5479260', _decode_unknown_0xf5479260),
    0x271b644e: ('unknown_0x271b644e', _decode_unknown_0x271b644e),
    0x52dc08c1: ('unknown_0x52dc08c1', _decode_unknown_0x52dc08c1),
    0x9980db64: ('unknown_0x9980db64', _decode_unknown_0x9980db64),
    0x23f59057: ('unknown_0x23f59057', _decode_unknown_0x23f59057),
    0xad3d5a3f: ('unknown_0xad3d5a3f', _decode_unknown_0xad3d5a3f),
    0x3315d22b: ('unknown_0x3315d22b', _decode_unknown_0x3315d22b),
    0x9e4007b6: ('unknown_0x9e4007b6', _decode_unknown_0x9e4007b6),
    0x7a8d3d46: ('unknown_0x7a8d3d46', _decode_unknown_0x7a8d3d46),
    0x2b97d64c: ('unknown_0x2b97d64c', _decode_unknown_0x2b97d64c),
    0xbdc57ce0: ('unknown_0xbdc57ce0', _decode_unknown_0xbdc57ce0),
    0x7d59c854: ('unknown_0x7d59c854', _decode_unknown_0x7d59c854),
    0x3c4ef7d2: ('unknown_0x3c4ef7d2', _decode_unknown_0x3c4ef7d2),
    0x2b483e9f: ('unknown_0x2b483e9f', _decode_unknown_0x2b483e9f),
    0x706f52fe: ('unknown_0x706f52fe', _decode_unknown_0x706f52fe),
    0x62f9ebf6: ('unknown_0x62f9ebf6', _decode_unknown_0x62f9ebf6),
    0xa9a53853: ('unknown_0xa9a53853', _decode_unknown_0xa9a53853),
    0x722b1bc0: ('unknown_0x722b1bc0', _decode_unknown_0x722b1bc0),
    0xf8252bca: ('unknown_0xf8252bca', _decode_unknown_0xf8252bca),
    0xd1997970: ('unknown_0xd1997970', _decode_unknown_0xd1997970),
    0x4c3fc933: ('player_model_color', _decode_player_model_color),
    0x5a87c156: ('unknown_0x5a87c156', _decode_unknown_0x5a87c156),
    0x9c0c5318: ('player_surface_color', _decode_player_surface_color),
    0x2a247ede: ('player_outline_color', _decode_player_outline_color),
    0x44303a9c: ('text_color', _decode_text_color),
    0xf2e13506: ('text_outline_color', _decode_text_outline_color),
    0x1a4b8068: ('unknown_0x1a4b8068', _decode_unknown_0x1a4b8068),
    0xa485372c: ('frame_color', _decode_frame_color),
    0x536647d5: ('title_color', _decode_title_color),
    0xa6b633fa: ('legend_background_color', _decode_legend_background_color),
    0x1cea7f9: ('legend_gradient_color', _decode_legend_gradient_color),
}
