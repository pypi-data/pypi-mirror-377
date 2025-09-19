# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.LayerInfo import LayerInfo
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Color import Color

if typing.TYPE_CHECKING:
    class FluidPropertiesJson(typing_extensions.TypedDict):
        fluid_type: int
        is_morph_target: bool
        render_surface: bool
        render_under_surface: bool
        unknown_0x3ddca674: bool
        unknown_0x4817eaa7: bool
        unknown_0x13013139: float
        grid_spacing: float
        unknown_0x4c60077e: float
        unknown_0x8518047a: float
        bloom: int
        base_color: json_util.JsonValue
        underwater_fog_color: json_util.JsonValue
        color_map: int
        color_warp_map: int
        gloss_map: int
        env_map: int
        light_map: int
        txtr: int
        unknown_0xdd2f6dbd: float
        unknown_0xf90deda5: float
        unknown_0x3425e83f: float
        flow_speed: float
        flow_orientation: float
        flow_color: json_util.JsonObject
        layer_info_0xe75248e4: json_util.JsonObject
        layer_info_0x385e0d43: json_util.JsonObject
        layer_info_0xd369b640: json_util.JsonObject
        layer_info_0x6ddea66d: json_util.JsonObject
        splash_color: json_util.JsonValue
        splash_effect_tiny: int
        splash_effect_small: int
        splash_effect_medium: int
        splash_effect_big: int
        splash_sound_tiny: int
        calculate_seed: int
        splash_sound_medium: int
        splash_sound_big: int
        caud_0x0efcdea0: int
        caud_0x78df0e7f: int
        unknown_0x84e241ed: float
        unknown_0xe2072799: float
        rolling_splash_effect: int
        runoff_visor_effect: int
        runoff_ball_effect: int
        slow_exit_sound: int
        fast_exit_sound: int
        fast_exit_speed: float
        unknown_0x687df7a3: float
        unknown_0xe73aad13: float
        unknown_0xac67b7d7: float
        fog_color: json_util.JsonValue
        fog_height: float
        fog_bob_height: float
        fog_bob_freq: float
        unknown_0xfe3bc8f7: bool
        freeze_radius: float
        player_freeze_radius: float
        caud_0x84927794: int
        caud_0xa6e650a0: int
        vertical_sound: int
        damage_sound: int
        damage_effect: int
        footstep_sound: int
        filter_sound_effects: bool
        volume_attenuation: float
        unknown_0x414379ea: int
        fluid_lock_string: str
    

class FluidType(enum.IntEnum):
    Unknown1 = 1425213472
    Unknown2 = 230544723
    Unknown3 = 1204522302

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


class Bloom(enum.IntEnum):
    Unknown1 = 1222417634
    Unknown2 = 759120936
    Unknown3 = 413038581
    Unknown4 = 3476137679
    Unknown5 = 1255115501
    Unknown6 = 131148223
    Unknown7 = 176197152

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


@dataclasses.dataclass()
class FluidProperties(BaseProperty):
    fluid_type: FluidType = dataclasses.field(default=FluidType.Unknown1, metadata={
        'reflection': FieldReflection[FluidType](
            FluidType, id=0xbe253b54, original_name='FluidType', from_json=FluidType.from_json, to_json=FluidType.to_json
        ),
    })
    is_morph_target: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7f2a8353, original_name='IsMorphTarget'
        ),
    })
    render_surface: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb5e9859f, original_name='RenderSurface'
        ),
    })
    render_under_surface: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x1f5e78c2, original_name='RenderUnderSurface'
        ),
    })
    unknown_0x3ddca674: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x3ddca674, original_name='Unknown'
        ),
    })
    unknown_0x4817eaa7: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x4817eaa7, original_name='Unknown'
        ),
    })
    unknown_0x13013139: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x13013139, original_name='Unknown'
        ),
    })
    grid_spacing: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x628f03db, original_name='GridSpacing'
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
    bloom: Bloom = dataclasses.field(default=Bloom.Unknown1, metadata={
        'reflection': FieldReflection[Bloom](
            Bloom, id=0xa4d23616, original_name='Bloom', from_json=Bloom.from_json, to_json=Bloom.to_json
        ),
    })
    base_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.49803900718688965, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x041398d5, original_name='BaseColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    underwater_fog_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.49803900718688965, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x5a96218c, original_name='UnderwaterFogColor', from_json=Color.from_json, to_json=Color.to_json
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
    light_map: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2421a2bf, original_name='LightMap'
        ),
    })
    txtr: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x7a4b4685, original_name='TXTR'
        ),
    })
    unknown_0xdd2f6dbd: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdd2f6dbd, original_name='Unknown'
        ),
    })
    unknown_0xf90deda5: float = dataclasses.field(default=0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf90deda5, original_name='Unknown'
        ),
    })
    unknown_0x3425e83f: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3425e83f, original_name='Unknown'
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
    splash_color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x13b56c22, original_name='SplashColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    splash_effect_tiny: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3da16854, original_name='SplashEffectTiny'
        ),
    })
    splash_effect_small: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x856941fe, original_name='SplashEffectSmall'
        ),
    })
    splash_effect_medium: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x341ec63b, original_name='SplashEffectMedium'
        ),
    })
    splash_effect_big: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x388e3c07, original_name='SplashEffectBig'
        ),
    })
    splash_sound_tiny: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x418643c2, original_name='SplashSoundTiny'
        ),
    })
    calculate_seed: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9c7950a4, original_name='CalculateSeed'
        ),
    })
    splash_sound_medium: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xbfb96ec0, original_name='SplashSoundMedium'
        ),
    })
    splash_sound_big: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc34a1dc9, original_name='SplashSoundBig'
        ),
    })
    caud_0x0efcdea0: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0efcdea0, original_name='CAUD'
        ),
    })
    caud_0x78df0e7f: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x78df0e7f, original_name='CAUD'
        ),
    })
    unknown_0x84e241ed: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x84e241ed, original_name='Unknown'
        ),
    })
    unknown_0xe2072799: float = dataclasses.field(default=45000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe2072799, original_name='Unknown'
        ),
    })
    rolling_splash_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xab463f9a, original_name='RollingSplashEffect'
        ),
    })
    runoff_visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x66d466b5, original_name='RunoffVisorEffect'
        ),
    })
    runoff_ball_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb97ccede, original_name='RunoffBallEffect'
        ),
    })
    slow_exit_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4d82bb1e, original_name='SlowExitSound'
        ),
    })
    fast_exit_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc51da2dc, original_name='FastExitSound'
        ),
    })
    fast_exit_speed: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x03d24e64, original_name='FastExitSpeed'
        ),
    })
    unknown_0x687df7a3: float = dataclasses.field(default=-0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x687df7a3, original_name='Unknown'
        ),
    })
    unknown_0xe73aad13: float = dataclasses.field(default=-1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe73aad13, original_name='Unknown'
        ),
    })
    unknown_0xac67b7d7: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xac67b7d7, original_name='Unknown'
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
    unknown_0xfe3bc8f7: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xfe3bc8f7, original_name='Unknown'
        ),
    })
    freeze_radius: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x318418aa, original_name='FreezeRadius'
        ),
    })
    player_freeze_radius: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7b77e31d, original_name='PlayerFreezeRadius'
        ),
    })
    caud_0x84927794: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x84927794, original_name='CAUD'
        ),
    })
    caud_0xa6e650a0: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa6e650a0, original_name='CAUD'
        ),
    })
    vertical_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x90b8eb66, original_name='VerticalSound'
        ),
    })
    damage_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3eede8f7, original_name='DamageSound'
        ),
    })
    damage_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc110ed44, original_name='DamageEffect'
        ),
    })
    footstep_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb9413fe6, original_name='FootstepSound'
        ),
    })
    filter_sound_effects: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x822118b4, original_name='FilterSoundEffects'
        ),
    })
    volume_attenuation: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfe89b6e4, original_name='VolumeAttenuation'
        ),
    })
    unknown_0x414379ea: int = dataclasses.field(default=300, metadata={
        'reflection': FieldReflection[int](
            int, id=0x414379ea, original_name='Unknown'
        ),
    })
    fluid_lock_string: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x3c764739, original_name='FluidLockString'
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
        if property_count != 68:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe253b54
        fluid_type = FluidType.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7f2a8353
        is_morph_target = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb5e9859f
        render_surface = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1f5e78c2
        render_under_surface = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3ddca674
        unknown_0x3ddca674 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4817eaa7
        unknown_0x4817eaa7 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x13013139
        unknown_0x13013139 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x628f03db
        grid_spacing = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4c60077e
        unknown_0x4c60077e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8518047a
        unknown_0x8518047a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa4d23616
        bloom = Bloom.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x041398d5
        base_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5a96218c
        underwater_fog_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5e8b37dd
        color_map = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x031d987e
        color_warp_map = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5aa79c9f
        gloss_map = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2f0645cf
        env_map = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2421a2bf
        light_map = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7a4b4685
        txtr = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdd2f6dbd
        unknown_0xdd2f6dbd = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf90deda5
        unknown_0xf90deda5 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3425e83f
        unknown_0x3425e83f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf14e3a14
        flow_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x33eecdfd
        flow_orientation = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x244e9e6d
        flow_color = LayerInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe75248e4
        layer_info_0xe75248e4 = LayerInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x385e0d43
        layer_info_0x385e0d43 = LayerInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd369b640
        layer_info_0xd369b640 = LayerInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6ddea66d
        layer_info_0x6ddea66d = LayerInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x13b56c22
        splash_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3da16854
        splash_effect_tiny = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x856941fe
        splash_effect_small = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x341ec63b
        splash_effect_medium = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x388e3c07
        splash_effect_big = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x418643c2
        splash_sound_tiny = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9c7950a4
        calculate_seed = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbfb96ec0
        splash_sound_medium = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc34a1dc9
        splash_sound_big = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0efcdea0
        caud_0x0efcdea0 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x78df0e7f
        caud_0x78df0e7f = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x84e241ed
        unknown_0x84e241ed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe2072799
        unknown_0xe2072799 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xab463f9a
        rolling_splash_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x66d466b5
        runoff_visor_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb97ccede
        runoff_ball_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d82bb1e
        slow_exit_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc51da2dc
        fast_exit_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x03d24e64
        fast_exit_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x687df7a3
        unknown_0x687df7a3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe73aad13
        unknown_0xe73aad13 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xac67b7d7
        unknown_0xac67b7d7 = struct.unpack('>f', data.read(4))[0]
    
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
        assert property_id == 0xfe3bc8f7
        unknown_0xfe3bc8f7 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x318418aa
        freeze_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b77e31d
        player_freeze_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x84927794
        caud_0x84927794 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa6e650a0
        caud_0xa6e650a0 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x90b8eb66
        vertical_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3eede8f7
        damage_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc110ed44
        damage_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb9413fe6
        footstep_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x822118b4
        filter_sound_effects = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfe89b6e4
        volume_attenuation = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x414379ea
        unknown_0x414379ea = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3c764739
        fluid_lock_string = data.read(property_size)[:-1].decode("utf-8")
    
        return cls(fluid_type, is_morph_target, render_surface, render_under_surface, unknown_0x3ddca674, unknown_0x4817eaa7, unknown_0x13013139, grid_spacing, unknown_0x4c60077e, unknown_0x8518047a, bloom, base_color, underwater_fog_color, color_map, color_warp_map, gloss_map, env_map, light_map, txtr, unknown_0xdd2f6dbd, unknown_0xf90deda5, unknown_0x3425e83f, flow_speed, flow_orientation, flow_color, layer_info_0xe75248e4, layer_info_0x385e0d43, layer_info_0xd369b640, layer_info_0x6ddea66d, splash_color, splash_effect_tiny, splash_effect_small, splash_effect_medium, splash_effect_big, splash_sound_tiny, calculate_seed, splash_sound_medium, splash_sound_big, caud_0x0efcdea0, caud_0x78df0e7f, unknown_0x84e241ed, unknown_0xe2072799, rolling_splash_effect, runoff_visor_effect, runoff_ball_effect, slow_exit_sound, fast_exit_sound, fast_exit_speed, unknown_0x687df7a3, unknown_0xe73aad13, unknown_0xac67b7d7, fog_color, fog_height, fog_bob_height, fog_bob_freq, unknown_0xfe3bc8f7, freeze_radius, player_freeze_radius, caud_0x84927794, caud_0xa6e650a0, vertical_sound, damage_sound, damage_effect, footstep_sound, filter_sound_effects, volume_attenuation, unknown_0x414379ea, fluid_lock_string)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00D')  # 68 properties

        data.write(b'\xbe%;T')  # 0xbe253b54
        data.write(b'\x00\x04')  # size
        self.fluid_type.to_stream(data)

        data.write(b'\x7f*\x83S')  # 0x7f2a8353
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_morph_target))

        data.write(b'\xb5\xe9\x85\x9f')  # 0xb5e9859f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.render_surface))

        data.write(b'\x1f^x\xc2')  # 0x1f5e78c2
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.render_under_surface))

        data.write(b'=\xdc\xa6t')  # 0x3ddca674
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x3ddca674))

        data.write(b'H\x17\xea\xa7')  # 0x4817eaa7
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x4817eaa7))

        data.write(b'\x13\x0119')  # 0x13013139
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x13013139))

        data.write(b'b\x8f\x03\xdb')  # 0x628f03db
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grid_spacing))

        data.write(b'L`\x07~')  # 0x4c60077e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4c60077e))

        data.write(b'\x85\x18\x04z')  # 0x8518047a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8518047a))

        data.write(b'\xa4\xd26\x16')  # 0xa4d23616
        data.write(b'\x00\x04')  # size
        self.bloom.to_stream(data)

        data.write(b'\x04\x13\x98\xd5')  # 0x41398d5
        data.write(b'\x00\x10')  # size
        self.base_color.to_stream(data)

        data.write(b'Z\x96!\x8c')  # 0x5a96218c
        data.write(b'\x00\x10')  # size
        self.underwater_fog_color.to_stream(data)

        data.write(b'^\x8b7\xdd')  # 0x5e8b37dd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.color_map))

        data.write(b'\x03\x1d\x98~')  # 0x31d987e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.color_warp_map))

        data.write(b'Z\xa7\x9c\x9f')  # 0x5aa79c9f
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.gloss_map))

        data.write(b'/\x06E\xcf')  # 0x2f0645cf
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.env_map))

        data.write(b'$!\xa2\xbf')  # 0x2421a2bf
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.light_map))

        data.write(b'zKF\x85')  # 0x7a4b4685
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.txtr))

        data.write(b'\xdd/m\xbd')  # 0xdd2f6dbd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xdd2f6dbd))

        data.write(b'\xf9\r\xed\xa5')  # 0xf90deda5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf90deda5))

        data.write(b'4%\xe8?')  # 0x3425e83f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3425e83f))

        data.write(b'\xf1N:\x14')  # 0xf14e3a14
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flow_speed))

        data.write(b'3\xee\xcd\xfd')  # 0x33eecdfd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flow_orientation))

        data.write(b'$N\x9em')  # 0x244e9e6d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flow_color.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe7RH\xe4')  # 0xe75248e4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.layer_info_0xe75248e4.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'8^\rC')  # 0x385e0d43
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.layer_info_0x385e0d43.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd3i\xb6@')  # 0xd369b640
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.layer_info_0xd369b640.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'm\xde\xa6m')  # 0x6ddea66d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.layer_info_0x6ddea66d.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x13\xb5l"')  # 0x13b56c22
        data.write(b'\x00\x10')  # size
        self.splash_color.to_stream(data)

        data.write(b'=\xa1hT')  # 0x3da16854
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.splash_effect_tiny))

        data.write(b'\x85iA\xfe')  # 0x856941fe
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.splash_effect_small))

        data.write(b'4\x1e\xc6;')  # 0x341ec63b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.splash_effect_medium))

        data.write(b'8\x8e<\x07')  # 0x388e3c07
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.splash_effect_big))

        data.write(b'A\x86C\xc2')  # 0x418643c2
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.splash_sound_tiny))

        data.write(b'\x9cyP\xa4')  # 0x9c7950a4
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.calculate_seed))

        data.write(b'\xbf\xb9n\xc0')  # 0xbfb96ec0
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.splash_sound_medium))

        data.write(b'\xc3J\x1d\xc9')  # 0xc34a1dc9
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.splash_sound_big))

        data.write(b'\x0e\xfc\xde\xa0')  # 0xefcdea0
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud_0x0efcdea0))

        data.write(b'x\xdf\x0e\x7f')  # 0x78df0e7f
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud_0x78df0e7f))

        data.write(b'\x84\xe2A\xed')  # 0x84e241ed
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x84e241ed))

        data.write(b"\xe2\x07'\x99")  # 0xe2072799
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe2072799))

        data.write(b'\xabF?\x9a')  # 0xab463f9a
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.rolling_splash_effect))

        data.write(b'f\xd4f\xb5')  # 0x66d466b5
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.runoff_visor_effect))

        data.write(b'\xb9|\xce\xde')  # 0xb97ccede
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.runoff_ball_effect))

        data.write(b'M\x82\xbb\x1e')  # 0x4d82bb1e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.slow_exit_sound))

        data.write(b'\xc5\x1d\xa2\xdc')  # 0xc51da2dc
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.fast_exit_sound))

        data.write(b'\x03\xd2Nd')  # 0x3d24e64
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fast_exit_speed))

        data.write(b'h}\xf7\xa3')  # 0x687df7a3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x687df7a3))

        data.write(b'\xe7:\xad\x13')  # 0xe73aad13
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe73aad13))

        data.write(b'\xacg\xb7\xd7')  # 0xac67b7d7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xac67b7d7))

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

        data.write(b'\xfe;\xc8\xf7')  # 0xfe3bc8f7
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xfe3bc8f7))

        data.write(b'1\x84\x18\xaa')  # 0x318418aa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.freeze_radius))

        data.write(b'{w\xe3\x1d')  # 0x7b77e31d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.player_freeze_radius))

        data.write(b'\x84\x92w\x94')  # 0x84927794
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud_0x84927794))

        data.write(b'\xa6\xe6P\xa0')  # 0xa6e650a0
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.caud_0xa6e650a0))

        data.write(b'\x90\xb8\xebf')  # 0x90b8eb66
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.vertical_sound))

        data.write(b'>\xed\xe8\xf7')  # 0x3eede8f7
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.damage_sound))

        data.write(b'\xc1\x10\xedD')  # 0xc110ed44
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.damage_effect))

        data.write(b'\xb9A?\xe6')  # 0xb9413fe6
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.footstep_sound))

        data.write(b'\x82!\x18\xb4')  # 0x822118b4
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.filter_sound_effects))

        data.write(b'\xfe\x89\xb6\xe4')  # 0xfe89b6e4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.volume_attenuation))

        data.write(b'ACy\xea')  # 0x414379ea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x414379ea))

        data.write(b'<vG9')  # 0x3c764739
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.fluid_lock_string.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("FluidPropertiesJson", data)
        return cls(
            fluid_type=FluidType.from_json(json_data['fluid_type']),
            is_morph_target=json_data['is_morph_target'],
            render_surface=json_data['render_surface'],
            render_under_surface=json_data['render_under_surface'],
            unknown_0x3ddca674=json_data['unknown_0x3ddca674'],
            unknown_0x4817eaa7=json_data['unknown_0x4817eaa7'],
            unknown_0x13013139=json_data['unknown_0x13013139'],
            grid_spacing=json_data['grid_spacing'],
            unknown_0x4c60077e=json_data['unknown_0x4c60077e'],
            unknown_0x8518047a=json_data['unknown_0x8518047a'],
            bloom=Bloom.from_json(json_data['bloom']),
            base_color=Color.from_json(json_data['base_color']),
            underwater_fog_color=Color.from_json(json_data['underwater_fog_color']),
            color_map=json_data['color_map'],
            color_warp_map=json_data['color_warp_map'],
            gloss_map=json_data['gloss_map'],
            env_map=json_data['env_map'],
            light_map=json_data['light_map'],
            txtr=json_data['txtr'],
            unknown_0xdd2f6dbd=json_data['unknown_0xdd2f6dbd'],
            unknown_0xf90deda5=json_data['unknown_0xf90deda5'],
            unknown_0x3425e83f=json_data['unknown_0x3425e83f'],
            flow_speed=json_data['flow_speed'],
            flow_orientation=json_data['flow_orientation'],
            flow_color=LayerInfo.from_json(json_data['flow_color']),
            layer_info_0xe75248e4=LayerInfo.from_json(json_data['layer_info_0xe75248e4']),
            layer_info_0x385e0d43=LayerInfo.from_json(json_data['layer_info_0x385e0d43']),
            layer_info_0xd369b640=LayerInfo.from_json(json_data['layer_info_0xd369b640']),
            layer_info_0x6ddea66d=LayerInfo.from_json(json_data['layer_info_0x6ddea66d']),
            splash_color=Color.from_json(json_data['splash_color']),
            splash_effect_tiny=json_data['splash_effect_tiny'],
            splash_effect_small=json_data['splash_effect_small'],
            splash_effect_medium=json_data['splash_effect_medium'],
            splash_effect_big=json_data['splash_effect_big'],
            splash_sound_tiny=json_data['splash_sound_tiny'],
            calculate_seed=json_data['calculate_seed'],
            splash_sound_medium=json_data['splash_sound_medium'],
            splash_sound_big=json_data['splash_sound_big'],
            caud_0x0efcdea0=json_data['caud_0x0efcdea0'],
            caud_0x78df0e7f=json_data['caud_0x78df0e7f'],
            unknown_0x84e241ed=json_data['unknown_0x84e241ed'],
            unknown_0xe2072799=json_data['unknown_0xe2072799'],
            rolling_splash_effect=json_data['rolling_splash_effect'],
            runoff_visor_effect=json_data['runoff_visor_effect'],
            runoff_ball_effect=json_data['runoff_ball_effect'],
            slow_exit_sound=json_data['slow_exit_sound'],
            fast_exit_sound=json_data['fast_exit_sound'],
            fast_exit_speed=json_data['fast_exit_speed'],
            unknown_0x687df7a3=json_data['unknown_0x687df7a3'],
            unknown_0xe73aad13=json_data['unknown_0xe73aad13'],
            unknown_0xac67b7d7=json_data['unknown_0xac67b7d7'],
            fog_color=Color.from_json(json_data['fog_color']),
            fog_height=json_data['fog_height'],
            fog_bob_height=json_data['fog_bob_height'],
            fog_bob_freq=json_data['fog_bob_freq'],
            unknown_0xfe3bc8f7=json_data['unknown_0xfe3bc8f7'],
            freeze_radius=json_data['freeze_radius'],
            player_freeze_radius=json_data['player_freeze_radius'],
            caud_0x84927794=json_data['caud_0x84927794'],
            caud_0xa6e650a0=json_data['caud_0xa6e650a0'],
            vertical_sound=json_data['vertical_sound'],
            damage_sound=json_data['damage_sound'],
            damage_effect=json_data['damage_effect'],
            footstep_sound=json_data['footstep_sound'],
            filter_sound_effects=json_data['filter_sound_effects'],
            volume_attenuation=json_data['volume_attenuation'],
            unknown_0x414379ea=json_data['unknown_0x414379ea'],
            fluid_lock_string=json_data['fluid_lock_string'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'fluid_type': self.fluid_type.to_json(),
            'is_morph_target': self.is_morph_target,
            'render_surface': self.render_surface,
            'render_under_surface': self.render_under_surface,
            'unknown_0x3ddca674': self.unknown_0x3ddca674,
            'unknown_0x4817eaa7': self.unknown_0x4817eaa7,
            'unknown_0x13013139': self.unknown_0x13013139,
            'grid_spacing': self.grid_spacing,
            'unknown_0x4c60077e': self.unknown_0x4c60077e,
            'unknown_0x8518047a': self.unknown_0x8518047a,
            'bloom': self.bloom.to_json(),
            'base_color': self.base_color.to_json(),
            'underwater_fog_color': self.underwater_fog_color.to_json(),
            'color_map': self.color_map,
            'color_warp_map': self.color_warp_map,
            'gloss_map': self.gloss_map,
            'env_map': self.env_map,
            'light_map': self.light_map,
            'txtr': self.txtr,
            'unknown_0xdd2f6dbd': self.unknown_0xdd2f6dbd,
            'unknown_0xf90deda5': self.unknown_0xf90deda5,
            'unknown_0x3425e83f': self.unknown_0x3425e83f,
            'flow_speed': self.flow_speed,
            'flow_orientation': self.flow_orientation,
            'flow_color': self.flow_color.to_json(),
            'layer_info_0xe75248e4': self.layer_info_0xe75248e4.to_json(),
            'layer_info_0x385e0d43': self.layer_info_0x385e0d43.to_json(),
            'layer_info_0xd369b640': self.layer_info_0xd369b640.to_json(),
            'layer_info_0x6ddea66d': self.layer_info_0x6ddea66d.to_json(),
            'splash_color': self.splash_color.to_json(),
            'splash_effect_tiny': self.splash_effect_tiny,
            'splash_effect_small': self.splash_effect_small,
            'splash_effect_medium': self.splash_effect_medium,
            'splash_effect_big': self.splash_effect_big,
            'splash_sound_tiny': self.splash_sound_tiny,
            'calculate_seed': self.calculate_seed,
            'splash_sound_medium': self.splash_sound_medium,
            'splash_sound_big': self.splash_sound_big,
            'caud_0x0efcdea0': self.caud_0x0efcdea0,
            'caud_0x78df0e7f': self.caud_0x78df0e7f,
            'unknown_0x84e241ed': self.unknown_0x84e241ed,
            'unknown_0xe2072799': self.unknown_0xe2072799,
            'rolling_splash_effect': self.rolling_splash_effect,
            'runoff_visor_effect': self.runoff_visor_effect,
            'runoff_ball_effect': self.runoff_ball_effect,
            'slow_exit_sound': self.slow_exit_sound,
            'fast_exit_sound': self.fast_exit_sound,
            'fast_exit_speed': self.fast_exit_speed,
            'unknown_0x687df7a3': self.unknown_0x687df7a3,
            'unknown_0xe73aad13': self.unknown_0xe73aad13,
            'unknown_0xac67b7d7': self.unknown_0xac67b7d7,
            'fog_color': self.fog_color.to_json(),
            'fog_height': self.fog_height,
            'fog_bob_height': self.fog_bob_height,
            'fog_bob_freq': self.fog_bob_freq,
            'unknown_0xfe3bc8f7': self.unknown_0xfe3bc8f7,
            'freeze_radius': self.freeze_radius,
            'player_freeze_radius': self.player_freeze_radius,
            'caud_0x84927794': self.caud_0x84927794,
            'caud_0xa6e650a0': self.caud_0xa6e650a0,
            'vertical_sound': self.vertical_sound,
            'damage_sound': self.damage_sound,
            'damage_effect': self.damage_effect,
            'footstep_sound': self.footstep_sound,
            'filter_sound_effects': self.filter_sound_effects,
            'volume_attenuation': self.volume_attenuation,
            'unknown_0x414379ea': self.unknown_0x414379ea,
            'fluid_lock_string': self.fluid_lock_string,
        }


def _decode_fluid_type(data: typing.BinaryIO, property_size: int) -> FluidType:
    return FluidType.from_stream(data)


def _decode_is_morph_target(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_render_surface(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_render_under_surface(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x3ddca674(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x4817eaa7(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x13013139(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grid_spacing(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4c60077e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8518047a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_bloom(data: typing.BinaryIO, property_size: int) -> Bloom:
    return Bloom.from_stream(data)


def _decode_base_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_underwater_fog_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_color_map(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_color_warp_map(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_gloss_map(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_env_map(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_light_map(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_txtr(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0xdd2f6dbd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf90deda5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3425e83f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flow_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flow_orientation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_splash_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_splash_effect_tiny(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_splash_effect_small(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_splash_effect_medium(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_splash_effect_big(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_splash_sound_tiny(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_calculate_seed(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_splash_sound_medium(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_splash_sound_big(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud_0x0efcdea0(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud_0x78df0e7f(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x84e241ed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe2072799(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_rolling_splash_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_runoff_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_runoff_ball_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_slow_exit_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_fast_exit_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_fast_exit_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x687df7a3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe73aad13(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xac67b7d7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fog_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_fog_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fog_bob_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fog_bob_freq(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfe3bc8f7(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_freeze_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_player_freeze_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_caud_0x84927794(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_caud_0xa6e650a0(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_vertical_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_damage_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_damage_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_footstep_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_filter_sound_effects(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_volume_attenuation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x414379ea(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_fluid_lock_string(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xbe253b54: ('fluid_type', _decode_fluid_type),
    0x7f2a8353: ('is_morph_target', _decode_is_morph_target),
    0xb5e9859f: ('render_surface', _decode_render_surface),
    0x1f5e78c2: ('render_under_surface', _decode_render_under_surface),
    0x3ddca674: ('unknown_0x3ddca674', _decode_unknown_0x3ddca674),
    0x4817eaa7: ('unknown_0x4817eaa7', _decode_unknown_0x4817eaa7),
    0x13013139: ('unknown_0x13013139', _decode_unknown_0x13013139),
    0x628f03db: ('grid_spacing', _decode_grid_spacing),
    0x4c60077e: ('unknown_0x4c60077e', _decode_unknown_0x4c60077e),
    0x8518047a: ('unknown_0x8518047a', _decode_unknown_0x8518047a),
    0xa4d23616: ('bloom', _decode_bloom),
    0x41398d5: ('base_color', _decode_base_color),
    0x5a96218c: ('underwater_fog_color', _decode_underwater_fog_color),
    0x5e8b37dd: ('color_map', _decode_color_map),
    0x31d987e: ('color_warp_map', _decode_color_warp_map),
    0x5aa79c9f: ('gloss_map', _decode_gloss_map),
    0x2f0645cf: ('env_map', _decode_env_map),
    0x2421a2bf: ('light_map', _decode_light_map),
    0x7a4b4685: ('txtr', _decode_txtr),
    0xdd2f6dbd: ('unknown_0xdd2f6dbd', _decode_unknown_0xdd2f6dbd),
    0xf90deda5: ('unknown_0xf90deda5', _decode_unknown_0xf90deda5),
    0x3425e83f: ('unknown_0x3425e83f', _decode_unknown_0x3425e83f),
    0xf14e3a14: ('flow_speed', _decode_flow_speed),
    0x33eecdfd: ('flow_orientation', _decode_flow_orientation),
    0x244e9e6d: ('flow_color', LayerInfo.from_stream),
    0xe75248e4: ('layer_info_0xe75248e4', LayerInfo.from_stream),
    0x385e0d43: ('layer_info_0x385e0d43', LayerInfo.from_stream),
    0xd369b640: ('layer_info_0xd369b640', LayerInfo.from_stream),
    0x6ddea66d: ('layer_info_0x6ddea66d', LayerInfo.from_stream),
    0x13b56c22: ('splash_color', _decode_splash_color),
    0x3da16854: ('splash_effect_tiny', _decode_splash_effect_tiny),
    0x856941fe: ('splash_effect_small', _decode_splash_effect_small),
    0x341ec63b: ('splash_effect_medium', _decode_splash_effect_medium),
    0x388e3c07: ('splash_effect_big', _decode_splash_effect_big),
    0x418643c2: ('splash_sound_tiny', _decode_splash_sound_tiny),
    0x9c7950a4: ('calculate_seed', _decode_calculate_seed),
    0xbfb96ec0: ('splash_sound_medium', _decode_splash_sound_medium),
    0xc34a1dc9: ('splash_sound_big', _decode_splash_sound_big),
    0xefcdea0: ('caud_0x0efcdea0', _decode_caud_0x0efcdea0),
    0x78df0e7f: ('caud_0x78df0e7f', _decode_caud_0x78df0e7f),
    0x84e241ed: ('unknown_0x84e241ed', _decode_unknown_0x84e241ed),
    0xe2072799: ('unknown_0xe2072799', _decode_unknown_0xe2072799),
    0xab463f9a: ('rolling_splash_effect', _decode_rolling_splash_effect),
    0x66d466b5: ('runoff_visor_effect', _decode_runoff_visor_effect),
    0xb97ccede: ('runoff_ball_effect', _decode_runoff_ball_effect),
    0x4d82bb1e: ('slow_exit_sound', _decode_slow_exit_sound),
    0xc51da2dc: ('fast_exit_sound', _decode_fast_exit_sound),
    0x3d24e64: ('fast_exit_speed', _decode_fast_exit_speed),
    0x687df7a3: ('unknown_0x687df7a3', _decode_unknown_0x687df7a3),
    0xe73aad13: ('unknown_0xe73aad13', _decode_unknown_0xe73aad13),
    0xac67b7d7: ('unknown_0xac67b7d7', _decode_unknown_0xac67b7d7),
    0xe578c0dd: ('fog_color', _decode_fog_color),
    0xb4b0fd8d: ('fog_height', _decode_fog_height),
    0xb90dff44: ('fog_bob_height', _decode_fog_bob_height),
    0xf608d35c: ('fog_bob_freq', _decode_fog_bob_freq),
    0xfe3bc8f7: ('unknown_0xfe3bc8f7', _decode_unknown_0xfe3bc8f7),
    0x318418aa: ('freeze_radius', _decode_freeze_radius),
    0x7b77e31d: ('player_freeze_radius', _decode_player_freeze_radius),
    0x84927794: ('caud_0x84927794', _decode_caud_0x84927794),
    0xa6e650a0: ('caud_0xa6e650a0', _decode_caud_0xa6e650a0),
    0x90b8eb66: ('vertical_sound', _decode_vertical_sound),
    0x3eede8f7: ('damage_sound', _decode_damage_sound),
    0xc110ed44: ('damage_effect', _decode_damage_effect),
    0xb9413fe6: ('footstep_sound', _decode_footstep_sound),
    0x822118b4: ('filter_sound_effects', _decode_filter_sound_effects),
    0xfe89b6e4: ('volume_attenuation', _decode_volume_attenuation),
    0x414379ea: ('unknown_0x414379ea', _decode_unknown_0x414379ea),
    0x3c764739: ('fluid_lock_string', _decode_fluid_lock_string),
}
