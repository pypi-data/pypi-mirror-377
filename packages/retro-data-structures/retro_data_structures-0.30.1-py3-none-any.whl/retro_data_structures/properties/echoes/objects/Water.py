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
from retro_data_structures.properties.echoes.archetypes.LayerInfo import LayerInfo
from retro_data_structures.properties.echoes.archetypes.TriggerInfo import TriggerInfo
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class WaterJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        trigger: json_util.JsonObject
        alpha_fadein_time: float
        alpha_fadeout_time: float
        unknown_0x4c60077e: float
        unknown_0x8518047a: float
        fluid_type: int
        light_map: int
        color_map: int
        color_warp_map: int
        gloss_map: int
        env_map: int
        env_map_size: float
        txtr: int
        foam_map: int
        alpha_map: int
        base_color: json_util.JsonValue
        alpha: float
        gloss_flat: float
        unknown_0xc63a0616: float
        unknown_0xdb7a3a6b: float
        unknown_0xb0259d23: float
        flow_color: json_util.JsonObject
        layer_info_0xe75248e4: json_util.JsonObject
        layer_info_0x385e0d43: json_util.JsonObject
        layer_info_0xd369b640: json_util.JsonObject
        layer_info_0x6ddea66d: json_util.JsonObject
        flow_speed: float
        flow_orientation: float
        underwater_fog_color: json_util.JsonValue
        splash_color: json_util.JsonValue
        splash_small: int
        splash_medium: int
        splash_big: int
        visor_runoff: int
        visor_runoff_ball: int
        sound_sound_runoff: int
        sound_sound_runoff_ball: int
        sound_splash_small: int
        sound_splash_medium: int
        sound_splash_big: int
        fog_color: json_util.JsonValue
        fog_height: float
        fog_bob_height: float
        fog_bob_freq: float
        unknown_0xd8521c1c: float
        unknown_0x7dce5dc2: float
        unknown_0x71819b3c: float
        unknown_0x9b96c630: float
        viscosity: float
        render_surface: bool
        unknown_0x3ddca674: bool
        unknown_0x0e791782: float
        unknown_0xc525c427: float
        unknown_0x3425e83f: float
        unknown_0x2293fdb0: float
        unknown_0xe9cf2e15: float
        unknown_0x268846d6: float
        unknown_0xedd49573: float
        unknown_0xc71c0d63: bool
        filter_sound_effects: bool
        unknown_0x414379ea: int
    

@dataclasses.dataclass()
class Water(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    trigger: TriggerInfo = dataclasses.field(default_factory=TriggerInfo, metadata={
        'reflection': FieldReflection[TriggerInfo](
            TriggerInfo, id=0x77a27411, original_name='Trigger', from_json=TriggerInfo.from_json, to_json=TriggerInfo.to_json
        ),
    })
    alpha_fadein_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xde5ea267, original_name='AlphaFadeinTime'
        ),
    })
    alpha_fadeout_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x22b69324, original_name='AlphaFadeoutTime'
        ),
    })
    unknown_0x4c60077e: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4c60077e, original_name='Unknown'
        ),
    })
    unknown_0x8518047a: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8518047a, original_name='Unknown'
        ),
    })
    fluid_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7d606b78, original_name='FluidType'
        ),
    })
    light_map: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2421a2bf, original_name='LightMap'
        ),
    })
    color_map: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5e8b37dd, original_name='ColorMap'
        ),
    })
    color_warp_map: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x031d987e, original_name='ColorWarpMap'
        ),
    })
    gloss_map: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5aa79c9f, original_name='GlossMap'
        ),
    })
    env_map: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2f0645cf, original_name='EnvMap'
        ),
    })
    env_map_size: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xde054447, original_name='EnvMapSize'
        ),
    })
    txtr: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x7a4b4685, original_name='TXTR'
        ),
    })
    foam_map: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5ba7702e, original_name='FoamMap'
        ),
    })
    alpha_map: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9a3463a7, original_name='AlphaMap'
        ),
    })
    base_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.49803900718688965, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x041398d5, original_name='BaseColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    alpha: float = dataclasses.field(default=0.6000000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0f7c6fc2, original_name='Alpha'
        ),
    })
    gloss_flat: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x26382fcb, original_name='GlossFlat'
        ),
    })
    unknown_0xc63a0616: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc63a0616, original_name='Unknown'
        ),
    })
    unknown_0xdb7a3a6b: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdb7a3a6b, original_name='Unknown'
        ),
    })
    unknown_0xb0259d23: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb0259d23, original_name='Unknown'
        ),
    })
    flow_color: LayerInfo = dataclasses.field(default_factory=LayerInfo, metadata={
        'reflection': FieldReflection[LayerInfo](
            LayerInfo, id=0x244e9e6d, original_name='FlowColor', from_json=LayerInfo.from_json, to_json=LayerInfo.to_json
        ),
    })
    layer_info_0xe75248e4: LayerInfo = dataclasses.field(default_factory=LayerInfo, metadata={
        'reflection': FieldReflection[LayerInfo](
            LayerInfo, id=0xe75248e4, original_name='LayerInfo', from_json=LayerInfo.from_json, to_json=LayerInfo.to_json
        ),
    })
    layer_info_0x385e0d43: LayerInfo = dataclasses.field(default_factory=LayerInfo, metadata={
        'reflection': FieldReflection[LayerInfo](
            LayerInfo, id=0x385e0d43, original_name='LayerInfo', from_json=LayerInfo.from_json, to_json=LayerInfo.to_json
        ),
    })
    layer_info_0xd369b640: LayerInfo = dataclasses.field(default_factory=LayerInfo, metadata={
        'reflection': FieldReflection[LayerInfo](
            LayerInfo, id=0xd369b640, original_name='LayerInfo', from_json=LayerInfo.from_json, to_json=LayerInfo.to_json
        ),
    })
    layer_info_0x6ddea66d: LayerInfo = dataclasses.field(default_factory=LayerInfo, metadata={
        'reflection': FieldReflection[LayerInfo](
            LayerInfo, id=0x6ddea66d, original_name='LayerInfo', from_json=LayerInfo.from_json, to_json=LayerInfo.to_json
        ),
    })
    flow_speed: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf14e3a14, original_name='FlowSpeed'
        ),
    })
    flow_orientation: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x33eecdfd, original_name='FlowOrientation'
        ),
    })
    underwater_fog_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.49803900718688965, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x5a96218c, original_name='UnderwaterFogColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    splash_color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x13b56c22, original_name='SplashColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    splash_small: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3027043c, original_name='Splash_Small'
        ),
    })
    splash_medium: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x41c12be2, original_name='Splash_Medium'
        ),
    })
    splash_big: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd6e82200, original_name='Splash_Big'
        ),
    })
    visor_runoff: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x94a23bf9, original_name='VisorRunoff'
        ),
    })
    visor_runoff_ball: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x43a704fb, original_name='VisorRunoffBall'
        ),
    })
    sound_sound_runoff: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xba717f19, original_name='Sound_SoundRunoff'
        ),
    })
    sound_sound_runoff_ball: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xae7c7efc, original_name='Sound_SoundRunoffBall'
        ),
    })
    sound_splash_small: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xeef81e4c, original_name='Sound_Splash_Small'
        ),
    })
    sound_splash_medium: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x63c96763, original_name='Sound_Splash_Medium'
        ),
    })
    sound_splash_big: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xd36209bc, original_name='Sound_Splash_Big'
        ),
    })
    fog_color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xe578c0dd, original_name='FogColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    fog_height: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb4b0fd8d, original_name='FogHeight'
        ),
    })
    fog_bob_height: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb90dff44, original_name='FogBobHeight'
        ),
    })
    fog_bob_freq: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf608d35c, original_name='FogBobFreq'
        ),
    })
    unknown_0xd8521c1c: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd8521c1c, original_name='Unknown'
        ),
    })
    unknown_0x7dce5dc2: float = dataclasses.field(default=125.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7dce5dc2, original_name='Unknown'
        ),
    })
    unknown_0x71819b3c: float = dataclasses.field(default=150.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x71819b3c, original_name='Unknown'
        ),
    })
    unknown_0x9b96c630: float = dataclasses.field(default=300.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9b96c630, original_name='Unknown'
        ),
    })
    viscosity: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xffe26f5c, original_name='Viscosity'
        ),
    })
    render_surface: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb5e9859f, original_name='RenderSurface'
        ),
    })
    unknown_0x3ddca674: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x3ddca674, original_name='Unknown'
        ),
    })
    unknown_0x0e791782: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0e791782, original_name='Unknown'
        ),
    })
    unknown_0xc525c427: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc525c427, original_name='Unknown'
        ),
    })
    unknown_0x3425e83f: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3425e83f, original_name='Unknown'
        ),
    })
    unknown_0x2293fdb0: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2293fdb0, original_name='Unknown'
        ),
    })
    unknown_0xe9cf2e15: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe9cf2e15, original_name='Unknown'
        ),
    })
    unknown_0x268846d6: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x268846d6, original_name='Unknown'
        ),
    })
    unknown_0xedd49573: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xedd49573, original_name='Unknown'
        ),
    })
    unknown_0xc71c0d63: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc71c0d63, original_name='Unknown'
        ),
    })
    filter_sound_effects: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x822118b4, original_name='FilterSoundEffects'
        ),
    })
    unknown_0x414379ea: int = dataclasses.field(default=300, metadata={
        'reflection': FieldReflection[int](
            int, id=0x414379ea, original_name='Unknown'
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
        return 'WATR'

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
        if property_count != 62:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x77a27411
        trigger = TriggerInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xde5ea267
        alpha_fadein_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x22b69324
        alpha_fadeout_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4c60077e
        unknown_0x4c60077e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8518047a
        unknown_0x8518047a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7d606b78
        fluid_type = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2421a2bf
        light_map = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5e8b37dd
        color_map = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x031d987e
        color_warp_map = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5aa79c9f
        gloss_map = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2f0645cf
        env_map = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xde054447
        env_map_size = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7a4b4685
        txtr = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5ba7702e
        foam_map = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9a3463a7
        alpha_map = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x041398d5
        base_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0f7c6fc2
        alpha = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x26382fcb
        gloss_flat = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc63a0616
        unknown_0xc63a0616 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdb7a3a6b
        unknown_0xdb7a3a6b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb0259d23
        unknown_0xb0259d23 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x244e9e6d
        flow_color = LayerInfo.from_stream(data, property_size, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe75248e4
        layer_info_0xe75248e4 = LayerInfo.from_stream(data, property_size, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x385e0d43
        layer_info_0x385e0d43 = LayerInfo.from_stream(data, property_size, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd369b640
        layer_info_0xd369b640 = LayerInfo.from_stream(data, property_size, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6ddea66d
        layer_info_0x6ddea66d = LayerInfo.from_stream(data, property_size, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf14e3a14
        flow_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x33eecdfd
        flow_orientation = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5a96218c
        underwater_fog_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x13b56c22
        splash_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3027043c
        splash_small = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x41c12be2
        splash_medium = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd6e82200
        splash_big = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x94a23bf9
        visor_runoff = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x43a704fb
        visor_runoff_ball = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xba717f19
        sound_sound_runoff = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xae7c7efc
        sound_sound_runoff_ball = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeef81e4c
        sound_splash_small = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x63c96763
        sound_splash_medium = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd36209bc
        sound_splash_big = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe578c0dd
        fog_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb4b0fd8d
        fog_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb90dff44
        fog_bob_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf608d35c
        fog_bob_freq = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd8521c1c
        unknown_0xd8521c1c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7dce5dc2
        unknown_0x7dce5dc2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71819b3c
        unknown_0x71819b3c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9b96c630
        unknown_0x9b96c630 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xffe26f5c
        viscosity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb5e9859f
        render_surface = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3ddca674
        unknown_0x3ddca674 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0e791782
        unknown_0x0e791782 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc525c427
        unknown_0xc525c427 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3425e83f
        unknown_0x3425e83f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2293fdb0
        unknown_0x2293fdb0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe9cf2e15
        unknown_0xe9cf2e15 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x268846d6
        unknown_0x268846d6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xedd49573
        unknown_0xedd49573 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc71c0d63
        unknown_0xc71c0d63 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x822118b4
        filter_sound_effects = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x414379ea
        unknown_0x414379ea = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, trigger, alpha_fadein_time, alpha_fadeout_time, unknown_0x4c60077e, unknown_0x8518047a, fluid_type, light_map, color_map, color_warp_map, gloss_map, env_map, env_map_size, txtr, foam_map, alpha_map, base_color, alpha, gloss_flat, unknown_0xc63a0616, unknown_0xdb7a3a6b, unknown_0xb0259d23, flow_color, layer_info_0xe75248e4, layer_info_0x385e0d43, layer_info_0xd369b640, layer_info_0x6ddea66d, flow_speed, flow_orientation, underwater_fog_color, splash_color, splash_small, splash_medium, splash_big, visor_runoff, visor_runoff_ball, sound_sound_runoff, sound_sound_runoff_ball, sound_splash_small, sound_splash_medium, sound_splash_big, fog_color, fog_height, fog_bob_height, fog_bob_freq, unknown_0xd8521c1c, unknown_0x7dce5dc2, unknown_0x71819b3c, unknown_0x9b96c630, viscosity, render_surface, unknown_0x3ddca674, unknown_0x0e791782, unknown_0xc525c427, unknown_0x3425e83f, unknown_0x2293fdb0, unknown_0xe9cf2e15, unknown_0x268846d6, unknown_0xedd49573, unknown_0xc71c0d63, filter_sound_effects, unknown_0x414379ea)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00>')  # 62 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'w\xa2t\x11')  # 0x77a27411
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.trigger.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xde^\xa2g')  # 0xde5ea267
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.alpha_fadein_time))

        data.write(b'"\xb6\x93$')  # 0x22b69324
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.alpha_fadeout_time))

        data.write(b'L`\x07~')  # 0x4c60077e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4c60077e))

        data.write(b'\x85\x18\x04z')  # 0x8518047a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8518047a))

        data.write(b'}`kx')  # 0x7d606b78
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.fluid_type))

        data.write(b'$!\xa2\xbf')  # 0x2421a2bf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.light_map))

        data.write(b'^\x8b7\xdd')  # 0x5e8b37dd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.color_map))

        data.write(b'\x03\x1d\x98~')  # 0x31d987e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.color_warp_map))

        data.write(b'Z\xa7\x9c\x9f')  # 0x5aa79c9f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.gloss_map))

        data.write(b'/\x06E\xcf')  # 0x2f0645cf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.env_map))

        data.write(b'\xde\x05DG')  # 0xde054447
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.env_map_size))

        data.write(b'zKF\x85')  # 0x7a4b4685
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.txtr))

        data.write(b'[\xa7p.')  # 0x5ba7702e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.foam_map))

        data.write(b'\x9a4c\xa7')  # 0x9a3463a7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.alpha_map))

        data.write(b'\x04\x13\x98\xd5')  # 0x41398d5
        data.write(b'\x00\x10')  # size
        self.base_color.to_stream(data)

        data.write(b'\x0f|o\xc2')  # 0xf7c6fc2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.alpha))

        data.write(b'&8/\xcb')  # 0x26382fcb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.gloss_flat))

        data.write(b'\xc6:\x06\x16')  # 0xc63a0616
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc63a0616))

        data.write(b'\xdbz:k')  # 0xdb7a3a6b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xdb7a3a6b))

        data.write(b'\xb0%\x9d#')  # 0xb0259d23
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb0259d23))

        data.write(b'$N\x9em')  # 0x244e9e6d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flow_color.to_stream(data, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe7RH\xe4')  # 0xe75248e4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.layer_info_0xe75248e4.to_stream(data, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'8^\rC')  # 0x385e0d43
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.layer_info_0x385e0d43.to_stream(data, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd3i\xb6@')  # 0xd369b640
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.layer_info_0xd369b640.to_stream(data, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'm\xde\xa6m')  # 0x6ddea66d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.layer_info_0x6ddea66d.to_stream(data, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf1N:\x14')  # 0xf14e3a14
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flow_speed))

        data.write(b'3\xee\xcd\xfd')  # 0x33eecdfd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flow_orientation))

        data.write(b'Z\x96!\x8c')  # 0x5a96218c
        data.write(b'\x00\x10')  # size
        self.underwater_fog_color.to_stream(data)

        data.write(b'\x13\xb5l"')  # 0x13b56c22
        data.write(b'\x00\x10')  # size
        self.splash_color.to_stream(data)

        data.write(b"0'\x04<")  # 0x3027043c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.splash_small))

        data.write(b'A\xc1+\xe2')  # 0x41c12be2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.splash_medium))

        data.write(b'\xd6\xe8"\x00')  # 0xd6e82200
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.splash_big))

        data.write(b'\x94\xa2;\xf9')  # 0x94a23bf9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.visor_runoff))

        data.write(b'C\xa7\x04\xfb')  # 0x43a704fb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.visor_runoff_ball))

        data.write(b'\xbaq\x7f\x19')  # 0xba717f19
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_sound_runoff))

        data.write(b'\xae|~\xfc')  # 0xae7c7efc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_sound_runoff_ball))

        data.write(b'\xee\xf8\x1eL')  # 0xeef81e4c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_splash_small))

        data.write(b'c\xc9gc')  # 0x63c96763
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_splash_medium))

        data.write(b'\xd3b\t\xbc')  # 0xd36209bc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_splash_big))

        data.write(b'\xe5x\xc0\xdd')  # 0xe578c0dd
        data.write(b'\x00\x10')  # size
        self.fog_color.to_stream(data)

        data.write(b'\xb4\xb0\xfd\x8d')  # 0xb4b0fd8d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fog_height))

        data.write(b'\xb9\r\xffD')  # 0xb90dff44
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fog_bob_height))

        data.write(b'\xf6\x08\xd3\\')  # 0xf608d35c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fog_bob_freq))

        data.write(b'\xd8R\x1c\x1c')  # 0xd8521c1c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd8521c1c))

        data.write(b'}\xce]\xc2')  # 0x7dce5dc2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7dce5dc2))

        data.write(b'q\x81\x9b<')  # 0x71819b3c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x71819b3c))

        data.write(b'\x9b\x96\xc60')  # 0x9b96c630
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9b96c630))

        data.write(b'\xff\xe2o\\')  # 0xffe26f5c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.viscosity))

        data.write(b'\xb5\xe9\x85\x9f')  # 0xb5e9859f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.render_surface))

        data.write(b'=\xdc\xa6t')  # 0x3ddca674
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x3ddca674))

        data.write(b'\x0ey\x17\x82')  # 0xe791782
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0e791782))

        data.write(b"\xc5%\xc4'")  # 0xc525c427
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc525c427))

        data.write(b'4%\xe8?')  # 0x3425e83f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3425e83f))

        data.write(b'"\x93\xfd\xb0')  # 0x2293fdb0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2293fdb0))

        data.write(b'\xe9\xcf.\x15')  # 0xe9cf2e15
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe9cf2e15))

        data.write(b'&\x88F\xd6')  # 0x268846d6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x268846d6))

        data.write(b'\xed\xd4\x95s')  # 0xedd49573
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xedd49573))

        data.write(b'\xc7\x1c\rc')  # 0xc71c0d63
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xc71c0d63))

        data.write(b'\x82!\x18\xb4')  # 0x822118b4
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.filter_sound_effects))

        data.write(b'ACy\xea')  # 0x414379ea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x414379ea))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("WaterJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            trigger=TriggerInfo.from_json(json_data['trigger']),
            alpha_fadein_time=json_data['alpha_fadein_time'],
            alpha_fadeout_time=json_data['alpha_fadeout_time'],
            unknown_0x4c60077e=json_data['unknown_0x4c60077e'],
            unknown_0x8518047a=json_data['unknown_0x8518047a'],
            fluid_type=json_data['fluid_type'],
            light_map=json_data['light_map'],
            color_map=json_data['color_map'],
            color_warp_map=json_data['color_warp_map'],
            gloss_map=json_data['gloss_map'],
            env_map=json_data['env_map'],
            env_map_size=json_data['env_map_size'],
            txtr=json_data['txtr'],
            foam_map=json_data['foam_map'],
            alpha_map=json_data['alpha_map'],
            base_color=Color.from_json(json_data['base_color']),
            alpha=json_data['alpha'],
            gloss_flat=json_data['gloss_flat'],
            unknown_0xc63a0616=json_data['unknown_0xc63a0616'],
            unknown_0xdb7a3a6b=json_data['unknown_0xdb7a3a6b'],
            unknown_0xb0259d23=json_data['unknown_0xb0259d23'],
            flow_color=LayerInfo.from_json(json_data['flow_color']),
            layer_info_0xe75248e4=LayerInfo.from_json(json_data['layer_info_0xe75248e4']),
            layer_info_0x385e0d43=LayerInfo.from_json(json_data['layer_info_0x385e0d43']),
            layer_info_0xd369b640=LayerInfo.from_json(json_data['layer_info_0xd369b640']),
            layer_info_0x6ddea66d=LayerInfo.from_json(json_data['layer_info_0x6ddea66d']),
            flow_speed=json_data['flow_speed'],
            flow_orientation=json_data['flow_orientation'],
            underwater_fog_color=Color.from_json(json_data['underwater_fog_color']),
            splash_color=Color.from_json(json_data['splash_color']),
            splash_small=json_data['splash_small'],
            splash_medium=json_data['splash_medium'],
            splash_big=json_data['splash_big'],
            visor_runoff=json_data['visor_runoff'],
            visor_runoff_ball=json_data['visor_runoff_ball'],
            sound_sound_runoff=json_data['sound_sound_runoff'],
            sound_sound_runoff_ball=json_data['sound_sound_runoff_ball'],
            sound_splash_small=json_data['sound_splash_small'],
            sound_splash_medium=json_data['sound_splash_medium'],
            sound_splash_big=json_data['sound_splash_big'],
            fog_color=Color.from_json(json_data['fog_color']),
            fog_height=json_data['fog_height'],
            fog_bob_height=json_data['fog_bob_height'],
            fog_bob_freq=json_data['fog_bob_freq'],
            unknown_0xd8521c1c=json_data['unknown_0xd8521c1c'],
            unknown_0x7dce5dc2=json_data['unknown_0x7dce5dc2'],
            unknown_0x71819b3c=json_data['unknown_0x71819b3c'],
            unknown_0x9b96c630=json_data['unknown_0x9b96c630'],
            viscosity=json_data['viscosity'],
            render_surface=json_data['render_surface'],
            unknown_0x3ddca674=json_data['unknown_0x3ddca674'],
            unknown_0x0e791782=json_data['unknown_0x0e791782'],
            unknown_0xc525c427=json_data['unknown_0xc525c427'],
            unknown_0x3425e83f=json_data['unknown_0x3425e83f'],
            unknown_0x2293fdb0=json_data['unknown_0x2293fdb0'],
            unknown_0xe9cf2e15=json_data['unknown_0xe9cf2e15'],
            unknown_0x268846d6=json_data['unknown_0x268846d6'],
            unknown_0xedd49573=json_data['unknown_0xedd49573'],
            unknown_0xc71c0d63=json_data['unknown_0xc71c0d63'],
            filter_sound_effects=json_data['filter_sound_effects'],
            unknown_0x414379ea=json_data['unknown_0x414379ea'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'trigger': self.trigger.to_json(),
            'alpha_fadein_time': self.alpha_fadein_time,
            'alpha_fadeout_time': self.alpha_fadeout_time,
            'unknown_0x4c60077e': self.unknown_0x4c60077e,
            'unknown_0x8518047a': self.unknown_0x8518047a,
            'fluid_type': self.fluid_type,
            'light_map': self.light_map,
            'color_map': self.color_map,
            'color_warp_map': self.color_warp_map,
            'gloss_map': self.gloss_map,
            'env_map': self.env_map,
            'env_map_size': self.env_map_size,
            'txtr': self.txtr,
            'foam_map': self.foam_map,
            'alpha_map': self.alpha_map,
            'base_color': self.base_color.to_json(),
            'alpha': self.alpha,
            'gloss_flat': self.gloss_flat,
            'unknown_0xc63a0616': self.unknown_0xc63a0616,
            'unknown_0xdb7a3a6b': self.unknown_0xdb7a3a6b,
            'unknown_0xb0259d23': self.unknown_0xb0259d23,
            'flow_color': self.flow_color.to_json(),
            'layer_info_0xe75248e4': self.layer_info_0xe75248e4.to_json(),
            'layer_info_0x385e0d43': self.layer_info_0x385e0d43.to_json(),
            'layer_info_0xd369b640': self.layer_info_0xd369b640.to_json(),
            'layer_info_0x6ddea66d': self.layer_info_0x6ddea66d.to_json(),
            'flow_speed': self.flow_speed,
            'flow_orientation': self.flow_orientation,
            'underwater_fog_color': self.underwater_fog_color.to_json(),
            'splash_color': self.splash_color.to_json(),
            'splash_small': self.splash_small,
            'splash_medium': self.splash_medium,
            'splash_big': self.splash_big,
            'visor_runoff': self.visor_runoff,
            'visor_runoff_ball': self.visor_runoff_ball,
            'sound_sound_runoff': self.sound_sound_runoff,
            'sound_sound_runoff_ball': self.sound_sound_runoff_ball,
            'sound_splash_small': self.sound_splash_small,
            'sound_splash_medium': self.sound_splash_medium,
            'sound_splash_big': self.sound_splash_big,
            'fog_color': self.fog_color.to_json(),
            'fog_height': self.fog_height,
            'fog_bob_height': self.fog_bob_height,
            'fog_bob_freq': self.fog_bob_freq,
            'unknown_0xd8521c1c': self.unknown_0xd8521c1c,
            'unknown_0x7dce5dc2': self.unknown_0x7dce5dc2,
            'unknown_0x71819b3c': self.unknown_0x71819b3c,
            'unknown_0x9b96c630': self.unknown_0x9b96c630,
            'viscosity': self.viscosity,
            'render_surface': self.render_surface,
            'unknown_0x3ddca674': self.unknown_0x3ddca674,
            'unknown_0x0e791782': self.unknown_0x0e791782,
            'unknown_0xc525c427': self.unknown_0xc525c427,
            'unknown_0x3425e83f': self.unknown_0x3425e83f,
            'unknown_0x2293fdb0': self.unknown_0x2293fdb0,
            'unknown_0xe9cf2e15': self.unknown_0xe9cf2e15,
            'unknown_0x268846d6': self.unknown_0x268846d6,
            'unknown_0xedd49573': self.unknown_0xedd49573,
            'unknown_0xc71c0d63': self.unknown_0xc71c0d63,
            'filter_sound_effects': self.filter_sound_effects,
            'unknown_0x414379ea': self.unknown_0x414379ea,
        }

    def _dependencies_for_light_map(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.light_map)

    def _dependencies_for_color_map(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.color_map)

    def _dependencies_for_color_warp_map(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.color_warp_map)

    def _dependencies_for_gloss_map(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.gloss_map)

    def _dependencies_for_env_map(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.env_map)

    def _dependencies_for_txtr(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.txtr)

    def _dependencies_for_foam_map(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.foam_map)

    def _dependencies_for_alpha_map(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.alpha_map)

    def _dependencies_for_splash_small(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.splash_small)

    def _dependencies_for_splash_medium(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.splash_medium)

    def _dependencies_for_splash_big(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.splash_big)

    def _dependencies_for_visor_runoff(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.visor_runoff)

    def _dependencies_for_visor_runoff_ball(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.visor_runoff_ball)

    def _dependencies_for_sound_sound_runoff(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_sound_runoff)

    def _dependencies_for_sound_sound_runoff_ball(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_sound_runoff_ball)

    def _dependencies_for_sound_splash_small(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_splash_small)

    def _dependencies_for_sound_splash_medium(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_splash_medium)

    def _dependencies_for_sound_splash_big(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_splash_big)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.trigger.dependencies_for, "trigger", "TriggerInfo"),
            (self._dependencies_for_light_map, "light_map", "AssetId"),
            (self._dependencies_for_color_map, "color_map", "AssetId"),
            (self._dependencies_for_color_warp_map, "color_warp_map", "AssetId"),
            (self._dependencies_for_gloss_map, "gloss_map", "AssetId"),
            (self._dependencies_for_env_map, "env_map", "AssetId"),
            (self._dependencies_for_txtr, "txtr", "AssetId"),
            (self._dependencies_for_foam_map, "foam_map", "AssetId"),
            (self._dependencies_for_alpha_map, "alpha_map", "AssetId"),
            (self.flow_color.dependencies_for, "flow_color", "LayerInfo"),
            (self.layer_info_0xe75248e4.dependencies_for, "layer_info_0xe75248e4", "LayerInfo"),
            (self.layer_info_0x385e0d43.dependencies_for, "layer_info_0x385e0d43", "LayerInfo"),
            (self.layer_info_0xd369b640.dependencies_for, "layer_info_0xd369b640", "LayerInfo"),
            (self.layer_info_0x6ddea66d.dependencies_for, "layer_info_0x6ddea66d", "LayerInfo"),
            (self._dependencies_for_splash_small, "splash_small", "AssetId"),
            (self._dependencies_for_splash_medium, "splash_medium", "AssetId"),
            (self._dependencies_for_splash_big, "splash_big", "AssetId"),
            (self._dependencies_for_visor_runoff, "visor_runoff", "AssetId"),
            (self._dependencies_for_visor_runoff_ball, "visor_runoff_ball", "AssetId"),
            (self._dependencies_for_sound_sound_runoff, "sound_sound_runoff", "int"),
            (self._dependencies_for_sound_sound_runoff_ball, "sound_sound_runoff_ball", "int"),
            (self._dependencies_for_sound_splash_small, "sound_splash_small", "int"),
            (self._dependencies_for_sound_splash_medium, "sound_splash_medium", "int"),
            (self._dependencies_for_sound_splash_big, "sound_splash_big", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Water.{field_name} ({field_type}): {e}"
                )


def _decode_alpha_fadein_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_alpha_fadeout_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4c60077e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8518047a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fluid_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_light_map(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_color_map(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_color_warp_map(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_gloss_map(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_env_map(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_env_map_size(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_txtr(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_foam_map(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_alpha_map(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_base_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_alpha(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_gloss_flat(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc63a0616(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdb7a3a6b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb0259d23(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flow_color(data: typing.BinaryIO, property_size: int) -> LayerInfo:
    return LayerInfo.from_stream(data, property_size, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})


def _decode_layer_info_0xe75248e4(data: typing.BinaryIO, property_size: int) -> LayerInfo:
    return LayerInfo.from_stream(data, property_size, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})


def _decode_layer_info_0x385e0d43(data: typing.BinaryIO, property_size: int) -> LayerInfo:
    return LayerInfo.from_stream(data, property_size, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})


def _decode_layer_info_0xd369b640(data: typing.BinaryIO, property_size: int) -> LayerInfo:
    return LayerInfo.from_stream(data, property_size, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})


def _decode_layer_info_0x6ddea66d(data: typing.BinaryIO, property_size: int) -> LayerInfo:
    return LayerInfo.from_stream(data, property_size, default_override={'motion_type': 0, 'amplitude': 0.15000000596046448, 'texture_scale': 10.0})


def _decode_flow_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flow_orientation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_underwater_fog_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_splash_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_splash_small(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_splash_medium(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_splash_big(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_visor_runoff(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_visor_runoff_ball(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_sound_sound_runoff(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_sound_runoff_ball(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_splash_small(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_splash_medium(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_splash_big(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_fog_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_fog_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fog_bob_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fog_bob_freq(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd8521c1c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7dce5dc2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x71819b3c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9b96c630(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_viscosity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_render_surface(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x3ddca674(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x0e791782(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc525c427(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3425e83f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2293fdb0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe9cf2e15(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x268846d6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xedd49573(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc71c0d63(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_filter_sound_effects(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x414379ea(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x77a27411: ('trigger', TriggerInfo.from_stream),
    0xde5ea267: ('alpha_fadein_time', _decode_alpha_fadein_time),
    0x22b69324: ('alpha_fadeout_time', _decode_alpha_fadeout_time),
    0x4c60077e: ('unknown_0x4c60077e', _decode_unknown_0x4c60077e),
    0x8518047a: ('unknown_0x8518047a', _decode_unknown_0x8518047a),
    0x7d606b78: ('fluid_type', _decode_fluid_type),
    0x2421a2bf: ('light_map', _decode_light_map),
    0x5e8b37dd: ('color_map', _decode_color_map),
    0x31d987e: ('color_warp_map', _decode_color_warp_map),
    0x5aa79c9f: ('gloss_map', _decode_gloss_map),
    0x2f0645cf: ('env_map', _decode_env_map),
    0xde054447: ('env_map_size', _decode_env_map_size),
    0x7a4b4685: ('txtr', _decode_txtr),
    0x5ba7702e: ('foam_map', _decode_foam_map),
    0x9a3463a7: ('alpha_map', _decode_alpha_map),
    0x41398d5: ('base_color', _decode_base_color),
    0xf7c6fc2: ('alpha', _decode_alpha),
    0x26382fcb: ('gloss_flat', _decode_gloss_flat),
    0xc63a0616: ('unknown_0xc63a0616', _decode_unknown_0xc63a0616),
    0xdb7a3a6b: ('unknown_0xdb7a3a6b', _decode_unknown_0xdb7a3a6b),
    0xb0259d23: ('unknown_0xb0259d23', _decode_unknown_0xb0259d23),
    0x244e9e6d: ('flow_color', _decode_flow_color),
    0xe75248e4: ('layer_info_0xe75248e4', _decode_layer_info_0xe75248e4),
    0x385e0d43: ('layer_info_0x385e0d43', _decode_layer_info_0x385e0d43),
    0xd369b640: ('layer_info_0xd369b640', _decode_layer_info_0xd369b640),
    0x6ddea66d: ('layer_info_0x6ddea66d', _decode_layer_info_0x6ddea66d),
    0xf14e3a14: ('flow_speed', _decode_flow_speed),
    0x33eecdfd: ('flow_orientation', _decode_flow_orientation),
    0x5a96218c: ('underwater_fog_color', _decode_underwater_fog_color),
    0x13b56c22: ('splash_color', _decode_splash_color),
    0x3027043c: ('splash_small', _decode_splash_small),
    0x41c12be2: ('splash_medium', _decode_splash_medium),
    0xd6e82200: ('splash_big', _decode_splash_big),
    0x94a23bf9: ('visor_runoff', _decode_visor_runoff),
    0x43a704fb: ('visor_runoff_ball', _decode_visor_runoff_ball),
    0xba717f19: ('sound_sound_runoff', _decode_sound_sound_runoff),
    0xae7c7efc: ('sound_sound_runoff_ball', _decode_sound_sound_runoff_ball),
    0xeef81e4c: ('sound_splash_small', _decode_sound_splash_small),
    0x63c96763: ('sound_splash_medium', _decode_sound_splash_medium),
    0xd36209bc: ('sound_splash_big', _decode_sound_splash_big),
    0xe578c0dd: ('fog_color', _decode_fog_color),
    0xb4b0fd8d: ('fog_height', _decode_fog_height),
    0xb90dff44: ('fog_bob_height', _decode_fog_bob_height),
    0xf608d35c: ('fog_bob_freq', _decode_fog_bob_freq),
    0xd8521c1c: ('unknown_0xd8521c1c', _decode_unknown_0xd8521c1c),
    0x7dce5dc2: ('unknown_0x7dce5dc2', _decode_unknown_0x7dce5dc2),
    0x71819b3c: ('unknown_0x71819b3c', _decode_unknown_0x71819b3c),
    0x9b96c630: ('unknown_0x9b96c630', _decode_unknown_0x9b96c630),
    0xffe26f5c: ('viscosity', _decode_viscosity),
    0xb5e9859f: ('render_surface', _decode_render_surface),
    0x3ddca674: ('unknown_0x3ddca674', _decode_unknown_0x3ddca674),
    0xe791782: ('unknown_0x0e791782', _decode_unknown_0x0e791782),
    0xc525c427: ('unknown_0xc525c427', _decode_unknown_0xc525c427),
    0x3425e83f: ('unknown_0x3425e83f', _decode_unknown_0x3425e83f),
    0x2293fdb0: ('unknown_0x2293fdb0', _decode_unknown_0x2293fdb0),
    0xe9cf2e15: ('unknown_0xe9cf2e15', _decode_unknown_0xe9cf2e15),
    0x268846d6: ('unknown_0x268846d6', _decode_unknown_0x268846d6),
    0xedd49573: ('unknown_0xedd49573', _decode_unknown_0xedd49573),
    0xc71c0d63: ('unknown_0xc71c0d63', _decode_unknown_0xc71c0d63),
    0x822118b4: ('filter_sound_effects', _decode_filter_sound_effects),
    0x414379ea: ('unknown_0x414379ea', _decode_unknown_0x414379ea),
}
