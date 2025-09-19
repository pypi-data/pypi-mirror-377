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
from retro_data_structures.properties.corruption.archetypes.HoverThenHomeProjectile import HoverThenHomeProjectile
from retro_data_structures.properties.corruption.archetypes.HyperModeData import HyperModeData
from retro_data_structures.properties.corruption.archetypes.LaunchProjectileData import LaunchProjectileData
from retro_data_structures.properties.corruption.archetypes.ModIncaData import ModIncaData
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Spline import Spline
from retro_data_structures.properties.corruption.core.Vector import Vector

if typing.TYPE_CHECKING:
    class SteamBotDataJson(typing_extensions.TypedDict):
        char: json_util.JsonObject
        unknown_0xf4f4a01d: float
        unknown_0x12940ffc: float
        unknown_0x303b4954: float
        rocket: json_util.JsonObject
        rocket_range_max: float
        rocket_range_min: float
        unknown_0x0588c742: float
        unknown_0x15793154: json_util.JsonValue
        unknown_0xe8fc0acd: float
        hover_then_home_projectile: json_util.JsonObject
        ray_gun: json_util.JsonObject
        unknown_0xdde5dccd: float
        unknown_0x3b85732c: float
        unknown_0x296b1195: float
        unknown_0xcf0bbe74: float
        unknown_0xa0d2af02: float
        unknown_0xd7b53cdb: int
        claw_damage: json_util.JsonObject
        claw_range_max: float
        claw_range_min: float
        claw_delay: float
        steam_blast: json_util.JsonObject
        steam_texture: int
        steam_alpha: float
        steam_fade_in: float
        steam_fade_out: float
        unknown_0xa296206a: float
        unknown_0x10c7fd02: float
        unknown_0xf6a752e3: float
        unknown_0x802b706e: float
        unknown_0xc80ac7db: float
        unknown_0x2e6a683a: float
        unknown_0x3e9f0188: float
        unknown_0xd8ffae69: float
        xy_scale: json_util.JsonObject
        z_scale: json_util.JsonObject
        model_alpha: json_util.JsonObject
        model_red: json_util.JsonObject
        model_green: json_util.JsonObject
        model_blue: json_util.JsonObject
        effects_alpha: json_util.JsonObject
        recheck_path_time: float
        recheck_path_distance: float
        avoidance_range: float
        scan_delay: float
        unknown_0x699da662: float
        unknown_0x8ffd0983: float
        unknown_0xdedd30a4: bool
        unknown_0xf8243d17: bool
        unknown_0xc6943950: int
        unknown_0x83967ad2: int
        unknown_0x6c8ae89f: float
        unknown_0x8aea477e: float
        unknown_0x5f1a7dd8: bool
        hyper_mode: json_util.JsonObject
        hyper_mode_hard: json_util.JsonObject
        hyper_mode_elite: json_util.JsonObject
        hurl_lerp: float
        hurl_knock_back_multiplier: float
        hurl_knock_back_resistance: float
        unknown_0x6cf3636f: float
        unknown_0x85d4691c: bool
        mod_inca_data: json_util.JsonObject
    

@dataclasses.dataclass()
class SteamBotData(BaseProperty):
    char: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xbe5e86b9, original_name='CHAR', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    unknown_0xf4f4a01d: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf4f4a01d, original_name='Unknown'
        ),
    })
    unknown_0x12940ffc: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x12940ffc, original_name='Unknown'
        ),
    })
    unknown_0x303b4954: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x303b4954, original_name='Unknown'
        ),
    })
    rocket: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0xab247451, original_name='Rocket', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    rocket_range_max: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x55c19435, original_name='RocketRangeMax'
        ),
    })
    rocket_range_min: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb3a13bd4, original_name='RocketRangeMin'
        ),
    })
    unknown_0x0588c742: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0588c742, original_name='Unknown'
        ),
    })
    unknown_0x15793154: Vector = dataclasses.field(default_factory=lambda: Vector(x=1.0, y=1.0, z=1.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x15793154, original_name='Unknown', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_0xe8fc0acd: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe8fc0acd, original_name='Unknown'
        ),
    })
    hover_then_home_projectile: HoverThenHomeProjectile = dataclasses.field(default_factory=HoverThenHomeProjectile, metadata={
        'reflection': FieldReflection[HoverThenHomeProjectile](
            HoverThenHomeProjectile, id=0x7039fb9f, original_name='HoverThenHomeProjectile', from_json=HoverThenHomeProjectile.from_json, to_json=HoverThenHomeProjectile.to_json
        ),
    })
    ray_gun: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0xb98cba47, original_name='RayGun', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    unknown_0xdde5dccd: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdde5dccd, original_name='Unknown'
        ),
    })
    unknown_0x3b85732c: float = dataclasses.field(default=0.014999999664723873, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3b85732c, original_name='Unknown'
        ),
    })
    unknown_0x296b1195: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x296b1195, original_name='Unknown'
        ),
    })
    unknown_0xcf0bbe74: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcf0bbe74, original_name='Unknown'
        ),
    })
    unknown_0xa0d2af02: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa0d2af02, original_name='Unknown'
        ),
    })
    unknown_0xd7b53cdb: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0xd7b53cdb, original_name='Unknown'
        ),
    })
    claw_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x8dbaeef2, original_name='ClawDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    claw_range_max: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x582b9b3b, original_name='ClawRangeMax'
        ),
    })
    claw_range_min: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbe4b34da, original_name='ClawRangeMin'
        ),
    })
    claw_delay: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xebb134b5, original_name='ClawDelay'
        ),
    })
    steam_blast: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0xca91ecb0, original_name='SteamBlast', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    steam_texture: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x58a21824, original_name='SteamTexture'
        ),
    })
    steam_alpha: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6c692453, original_name='SteamAlpha'
        ),
    })
    steam_fade_in: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x66a5cd17, original_name='SteamFadeIn'
        ),
    })
    steam_fade_out: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5c5b8b5d, original_name='SteamFadeOut'
        ),
    })
    unknown_0xa296206a: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa296206a, original_name='Unknown'
        ),
    })
    unknown_0x10c7fd02: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x10c7fd02, original_name='Unknown'
        ),
    })
    unknown_0xf6a752e3: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf6a752e3, original_name='Unknown'
        ),
    })
    unknown_0x802b706e: float = dataclasses.field(default=0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0x802b706e, original_name='Unknown'
        ),
    })
    unknown_0xc80ac7db: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc80ac7db, original_name='Unknown'
        ),
    })
    unknown_0x2e6a683a: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2e6a683a, original_name='Unknown'
        ),
    })
    unknown_0x3e9f0188: float = dataclasses.field(default=1.100000023841858, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3e9f0188, original_name='Unknown'
        ),
    })
    unknown_0xd8ffae69: float = dataclasses.field(default=0.8999999761581421, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd8ffae69, original_name='Unknown'
        ),
    })
    xy_scale: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x48ba8eb1, original_name='XYScale', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    z_scale: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x180c38b0, original_name='ZScale', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    model_alpha: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x0f762790, original_name='ModelAlpha', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    model_red: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x0feadc99, original_name='ModelRed', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    model_green: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x55be3e8e, original_name='ModelGreen', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    model_blue: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x79f7cc48, original_name='ModelBlue', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    effects_alpha: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x564bd8cd, original_name='EffectsAlpha', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    recheck_path_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9aa90b6b, original_name='RecheckPathTime'
        ),
    })
    recheck_path_distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7626ec89, original_name='RecheckPathDistance'
        ),
    })
    avoidance_range: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x50a9bd0d, original_name='AvoidanceRange'
        ),
    })
    scan_delay: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7fc827a2, original_name='ScanDelay'
        ),
    })
    unknown_0x699da662: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x699da662, original_name='Unknown'
        ),
    })
    unknown_0x8ffd0983: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8ffd0983, original_name='Unknown'
        ),
    })
    unknown_0xdedd30a4: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xdedd30a4, original_name='Unknown'
        ),
    })
    unknown_0xf8243d17: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf8243d17, original_name='Unknown'
        ),
    })
    unknown_0xc6943950: int = dataclasses.field(default=5, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc6943950, original_name='Unknown'
        ),
    })
    unknown_0x83967ad2: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0x83967ad2, original_name='Unknown'
        ),
    })
    unknown_0x6c8ae89f: float = dataclasses.field(default=2.0999999046325684, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6c8ae89f, original_name='Unknown'
        ),
    })
    unknown_0x8aea477e: float = dataclasses.field(default=1.899999976158142, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8aea477e, original_name='Unknown'
        ),
    })
    unknown_0x5f1a7dd8: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5f1a7dd8, original_name='Unknown'
        ),
    })
    hyper_mode: HyperModeData = dataclasses.field(default_factory=HyperModeData, metadata={
        'reflection': FieldReflection[HyperModeData](
            HyperModeData, id=0xb0a9b728, original_name='HyperMode', from_json=HyperModeData.from_json, to_json=HyperModeData.to_json
        ),
    })
    hyper_mode_hard: HyperModeData = dataclasses.field(default_factory=HyperModeData, metadata={
        'reflection': FieldReflection[HyperModeData](
            HyperModeData, id=0x14499fcb, original_name='HyperModeHard', from_json=HyperModeData.from_json, to_json=HyperModeData.to_json
        ),
    })
    hyper_mode_elite: HyperModeData = dataclasses.field(default_factory=HyperModeData, metadata={
        'reflection': FieldReflection[HyperModeData](
            HyperModeData, id=0xcd02221c, original_name='HyperModeElite', from_json=HyperModeData.from_json, to_json=HyperModeData.to_json
        ),
    })
    hurl_lerp: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x19863914, original_name='HurlLerp'
        ),
    })
    hurl_knock_back_multiplier: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x04ab182a, original_name='HurlKnockBackMultiplier'
        ),
    })
    hurl_knock_back_resistance: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb008320b, original_name='HurlKnockBackResistance'
        ),
    })
    unknown_0x6cf3636f: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6cf3636f, original_name='Unknown'
        ),
    })
    unknown_0x85d4691c: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x85d4691c, original_name='Unknown'
        ),
    })
    mod_inca_data: ModIncaData = dataclasses.field(default_factory=ModIncaData, metadata={
        'reflection': FieldReflection[ModIncaData](
            ModIncaData, id=0xb4c02854, original_name='ModIncaData', from_json=ModIncaData.from_json, to_json=ModIncaData.to_json
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
        if property_count != 64:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe5e86b9
        char = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf4f4a01d
        unknown_0xf4f4a01d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x12940ffc
        unknown_0x12940ffc = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x303b4954
        unknown_0x303b4954 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xab247451
        rocket = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x55c19435
        rocket_range_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3a13bd4
        rocket_range_min = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0588c742
        unknown_0x0588c742 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x15793154
        unknown_0x15793154 = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8fc0acd
        unknown_0xe8fc0acd = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7039fb9f
        hover_then_home_projectile = HoverThenHomeProjectile.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb98cba47
        ray_gun = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdde5dccd
        unknown_0xdde5dccd = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3b85732c
        unknown_0x3b85732c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x296b1195
        unknown_0x296b1195 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf0bbe74
        unknown_0xcf0bbe74 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa0d2af02
        unknown_0xa0d2af02 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd7b53cdb
        unknown_0xd7b53cdb = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8dbaeef2
        claw_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x582b9b3b
        claw_range_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe4b34da
        claw_range_min = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xebb134b5
        claw_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xca91ecb0
        steam_blast = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x58a21824
        steam_texture = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c692453
        steam_alpha = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x66a5cd17
        steam_fade_in = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5c5b8b5d
        steam_fade_out = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa296206a
        unknown_0xa296206a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x10c7fd02
        unknown_0x10c7fd02 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf6a752e3
        unknown_0xf6a752e3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x802b706e
        unknown_0x802b706e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc80ac7db
        unknown_0xc80ac7db = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2e6a683a
        unknown_0x2e6a683a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3e9f0188
        unknown_0x3e9f0188 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd8ffae69
        unknown_0xd8ffae69 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x48ba8eb1
        xy_scale = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x180c38b0
        z_scale = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0f762790
        model_alpha = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0feadc99
        model_red = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x55be3e8e
        model_green = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x79f7cc48
        model_blue = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x564bd8cd
        effects_alpha = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9aa90b6b
        recheck_path_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7626ec89
        recheck_path_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x50a9bd0d
        avoidance_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fc827a2
        scan_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x699da662
        unknown_0x699da662 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8ffd0983
        unknown_0x8ffd0983 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdedd30a4
        unknown_0xdedd30a4 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf8243d17
        unknown_0xf8243d17 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6943950
        unknown_0xc6943950 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x83967ad2
        unknown_0x83967ad2 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c8ae89f
        unknown_0x6c8ae89f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8aea477e
        unknown_0x8aea477e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5f1a7dd8
        unknown_0x5f1a7dd8 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb0a9b728
        hyper_mode = HyperModeData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x14499fcb
        hyper_mode_hard = HyperModeData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcd02221c
        hyper_mode_elite = HyperModeData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x19863914
        hurl_lerp = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x04ab182a
        hurl_knock_back_multiplier = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb008320b
        hurl_knock_back_resistance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6cf3636f
        unknown_0x6cf3636f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x85d4691c
        unknown_0x85d4691c = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb4c02854
        mod_inca_data = ModIncaData.from_stream(data, property_size)
    
        return cls(char, unknown_0xf4f4a01d, unknown_0x12940ffc, unknown_0x303b4954, rocket, rocket_range_max, rocket_range_min, unknown_0x0588c742, unknown_0x15793154, unknown_0xe8fc0acd, hover_then_home_projectile, ray_gun, unknown_0xdde5dccd, unknown_0x3b85732c, unknown_0x296b1195, unknown_0xcf0bbe74, unknown_0xa0d2af02, unknown_0xd7b53cdb, claw_damage, claw_range_max, claw_range_min, claw_delay, steam_blast, steam_texture, steam_alpha, steam_fade_in, steam_fade_out, unknown_0xa296206a, unknown_0x10c7fd02, unknown_0xf6a752e3, unknown_0x802b706e, unknown_0xc80ac7db, unknown_0x2e6a683a, unknown_0x3e9f0188, unknown_0xd8ffae69, xy_scale, z_scale, model_alpha, model_red, model_green, model_blue, effects_alpha, recheck_path_time, recheck_path_distance, avoidance_range, scan_delay, unknown_0x699da662, unknown_0x8ffd0983, unknown_0xdedd30a4, unknown_0xf8243d17, unknown_0xc6943950, unknown_0x83967ad2, unknown_0x6c8ae89f, unknown_0x8aea477e, unknown_0x5f1a7dd8, hyper_mode, hyper_mode_hard, hyper_mode_elite, hurl_lerp, hurl_knock_back_multiplier, hurl_knock_back_resistance, unknown_0x6cf3636f, unknown_0x85d4691c, mod_inca_data)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00@')  # 64 properties

        data.write(b'\xbe^\x86\xb9')  # 0xbe5e86b9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.char.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf4\xf4\xa0\x1d')  # 0xf4f4a01d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf4f4a01d))

        data.write(b'\x12\x94\x0f\xfc')  # 0x12940ffc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x12940ffc))

        data.write(b'0;IT')  # 0x303b4954
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x303b4954))

        data.write(b'\xab$tQ')  # 0xab247451
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.rocket.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'U\xc1\x945')  # 0x55c19435
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.rocket_range_max))

        data.write(b'\xb3\xa1;\xd4')  # 0xb3a13bd4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.rocket_range_min))

        data.write(b'\x05\x88\xc7B')  # 0x588c742
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0588c742))

        data.write(b'\x15y1T')  # 0x15793154
        data.write(b'\x00\x0c')  # size
        self.unknown_0x15793154.to_stream(data)

        data.write(b'\xe8\xfc\n\xcd')  # 0xe8fc0acd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe8fc0acd))

        data.write(b'p9\xfb\x9f')  # 0x7039fb9f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hover_then_home_projectile.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb9\x8c\xbaG')  # 0xb98cba47
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ray_gun.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdd\xe5\xdc\xcd')  # 0xdde5dccd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xdde5dccd))

        data.write(b';\x85s,')  # 0x3b85732c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3b85732c))

        data.write(b')k\x11\x95')  # 0x296b1195
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x296b1195))

        data.write(b'\xcf\x0b\xbet')  # 0xcf0bbe74
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcf0bbe74))

        data.write(b'\xa0\xd2\xaf\x02')  # 0xa0d2af02
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa0d2af02))

        data.write(b'\xd7\xb5<\xdb')  # 0xd7b53cdb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xd7b53cdb))

        data.write(b'\x8d\xba\xee\xf2')  # 0x8dbaeef2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.claw_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'X+\x9b;')  # 0x582b9b3b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.claw_range_max))

        data.write(b'\xbeK4\xda')  # 0xbe4b34da
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.claw_range_min))

        data.write(b'\xeb\xb14\xb5')  # 0xebb134b5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.claw_delay))

        data.write(b'\xca\x91\xec\xb0')  # 0xca91ecb0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.steam_blast.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'X\xa2\x18$')  # 0x58a21824
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.steam_texture))

        data.write(b'li$S')  # 0x6c692453
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.steam_alpha))

        data.write(b'f\xa5\xcd\x17')  # 0x66a5cd17
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.steam_fade_in))

        data.write(b'\\[\x8b]')  # 0x5c5b8b5d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.steam_fade_out))

        data.write(b'\xa2\x96 j')  # 0xa296206a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa296206a))

        data.write(b'\x10\xc7\xfd\x02')  # 0x10c7fd02
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x10c7fd02))

        data.write(b'\xf6\xa7R\xe3')  # 0xf6a752e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf6a752e3))

        data.write(b'\x80+pn')  # 0x802b706e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x802b706e))

        data.write(b'\xc8\n\xc7\xdb')  # 0xc80ac7db
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc80ac7db))

        data.write(b'.jh:')  # 0x2e6a683a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2e6a683a))

        data.write(b'>\x9f\x01\x88')  # 0x3e9f0188
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3e9f0188))

        data.write(b'\xd8\xff\xaei')  # 0xd8ffae69
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd8ffae69))

        data.write(b'H\xba\x8e\xb1')  # 0x48ba8eb1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.xy_scale.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x18\x0c8\xb0')  # 0x180c38b0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.z_scale.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"\x0fv'\x90")  # 0xf762790
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.model_alpha.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x0f\xea\xdc\x99')  # 0xfeadc99
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.model_red.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'U\xbe>\x8e')  # 0x55be3e8e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.model_green.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'y\xf7\xccH')  # 0x79f7cc48
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.model_blue.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'VK\xd8\xcd')  # 0x564bd8cd
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.effects_alpha.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9a\xa9\x0bk')  # 0x9aa90b6b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.recheck_path_time))

        data.write(b'v&\xec\x89')  # 0x7626ec89
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.recheck_path_distance))

        data.write(b'P\xa9\xbd\r')  # 0x50a9bd0d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.avoidance_range))

        data.write(b"\x7f\xc8'\xa2")  # 0x7fc827a2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scan_delay))

        data.write(b'i\x9d\xa6b')  # 0x699da662
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x699da662))

        data.write(b'\x8f\xfd\t\x83')  # 0x8ffd0983
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8ffd0983))

        data.write(b'\xde\xdd0\xa4')  # 0xdedd30a4
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xdedd30a4))

        data.write(b'\xf8$=\x17')  # 0xf8243d17
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xf8243d17))

        data.write(b'\xc6\x949P')  # 0xc6943950
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xc6943950))

        data.write(b'\x83\x96z\xd2')  # 0x83967ad2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x83967ad2))

        data.write(b'l\x8a\xe8\x9f')  # 0x6c8ae89f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6c8ae89f))

        data.write(b'\x8a\xeaG~')  # 0x8aea477e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8aea477e))

        data.write(b'_\x1a}\xd8')  # 0x5f1a7dd8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x5f1a7dd8))

        data.write(b'\xb0\xa9\xb7(')  # 0xb0a9b728
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hyper_mode.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x14I\x9f\xcb')  # 0x14499fcb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hyper_mode_hard.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xcd\x02"\x1c')  # 0xcd02221c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hyper_mode_elite.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x19\x869\x14')  # 0x19863914
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hurl_lerp))

        data.write(b'\x04\xab\x18*')  # 0x4ab182a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hurl_knock_back_multiplier))

        data.write(b'\xb0\x082\x0b')  # 0xb008320b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hurl_knock_back_resistance))

        data.write(b'l\xf3co')  # 0x6cf3636f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6cf3636f))

        data.write(b'\x85\xd4i\x1c')  # 0x85d4691c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x85d4691c))

        data.write(b'\xb4\xc0(T')  # 0xb4c02854
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.mod_inca_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SteamBotDataJson", data)
        return cls(
            char=AnimationParameters.from_json(json_data['char']),
            unknown_0xf4f4a01d=json_data['unknown_0xf4f4a01d'],
            unknown_0x12940ffc=json_data['unknown_0x12940ffc'],
            unknown_0x303b4954=json_data['unknown_0x303b4954'],
            rocket=LaunchProjectileData.from_json(json_data['rocket']),
            rocket_range_max=json_data['rocket_range_max'],
            rocket_range_min=json_data['rocket_range_min'],
            unknown_0x0588c742=json_data['unknown_0x0588c742'],
            unknown_0x15793154=Vector.from_json(json_data['unknown_0x15793154']),
            unknown_0xe8fc0acd=json_data['unknown_0xe8fc0acd'],
            hover_then_home_projectile=HoverThenHomeProjectile.from_json(json_data['hover_then_home_projectile']),
            ray_gun=LaunchProjectileData.from_json(json_data['ray_gun']),
            unknown_0xdde5dccd=json_data['unknown_0xdde5dccd'],
            unknown_0x3b85732c=json_data['unknown_0x3b85732c'],
            unknown_0x296b1195=json_data['unknown_0x296b1195'],
            unknown_0xcf0bbe74=json_data['unknown_0xcf0bbe74'],
            unknown_0xa0d2af02=json_data['unknown_0xa0d2af02'],
            unknown_0xd7b53cdb=json_data['unknown_0xd7b53cdb'],
            claw_damage=DamageInfo.from_json(json_data['claw_damage']),
            claw_range_max=json_data['claw_range_max'],
            claw_range_min=json_data['claw_range_min'],
            claw_delay=json_data['claw_delay'],
            steam_blast=LaunchProjectileData.from_json(json_data['steam_blast']),
            steam_texture=json_data['steam_texture'],
            steam_alpha=json_data['steam_alpha'],
            steam_fade_in=json_data['steam_fade_in'],
            steam_fade_out=json_data['steam_fade_out'],
            unknown_0xa296206a=json_data['unknown_0xa296206a'],
            unknown_0x10c7fd02=json_data['unknown_0x10c7fd02'],
            unknown_0xf6a752e3=json_data['unknown_0xf6a752e3'],
            unknown_0x802b706e=json_data['unknown_0x802b706e'],
            unknown_0xc80ac7db=json_data['unknown_0xc80ac7db'],
            unknown_0x2e6a683a=json_data['unknown_0x2e6a683a'],
            unknown_0x3e9f0188=json_data['unknown_0x3e9f0188'],
            unknown_0xd8ffae69=json_data['unknown_0xd8ffae69'],
            xy_scale=Spline.from_json(json_data['xy_scale']),
            z_scale=Spline.from_json(json_data['z_scale']),
            model_alpha=Spline.from_json(json_data['model_alpha']),
            model_red=Spline.from_json(json_data['model_red']),
            model_green=Spline.from_json(json_data['model_green']),
            model_blue=Spline.from_json(json_data['model_blue']),
            effects_alpha=Spline.from_json(json_data['effects_alpha']),
            recheck_path_time=json_data['recheck_path_time'],
            recheck_path_distance=json_data['recheck_path_distance'],
            avoidance_range=json_data['avoidance_range'],
            scan_delay=json_data['scan_delay'],
            unknown_0x699da662=json_data['unknown_0x699da662'],
            unknown_0x8ffd0983=json_data['unknown_0x8ffd0983'],
            unknown_0xdedd30a4=json_data['unknown_0xdedd30a4'],
            unknown_0xf8243d17=json_data['unknown_0xf8243d17'],
            unknown_0xc6943950=json_data['unknown_0xc6943950'],
            unknown_0x83967ad2=json_data['unknown_0x83967ad2'],
            unknown_0x6c8ae89f=json_data['unknown_0x6c8ae89f'],
            unknown_0x8aea477e=json_data['unknown_0x8aea477e'],
            unknown_0x5f1a7dd8=json_data['unknown_0x5f1a7dd8'],
            hyper_mode=HyperModeData.from_json(json_data['hyper_mode']),
            hyper_mode_hard=HyperModeData.from_json(json_data['hyper_mode_hard']),
            hyper_mode_elite=HyperModeData.from_json(json_data['hyper_mode_elite']),
            hurl_lerp=json_data['hurl_lerp'],
            hurl_knock_back_multiplier=json_data['hurl_knock_back_multiplier'],
            hurl_knock_back_resistance=json_data['hurl_knock_back_resistance'],
            unknown_0x6cf3636f=json_data['unknown_0x6cf3636f'],
            unknown_0x85d4691c=json_data['unknown_0x85d4691c'],
            mod_inca_data=ModIncaData.from_json(json_data['mod_inca_data']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'char': self.char.to_json(),
            'unknown_0xf4f4a01d': self.unknown_0xf4f4a01d,
            'unknown_0x12940ffc': self.unknown_0x12940ffc,
            'unknown_0x303b4954': self.unknown_0x303b4954,
            'rocket': self.rocket.to_json(),
            'rocket_range_max': self.rocket_range_max,
            'rocket_range_min': self.rocket_range_min,
            'unknown_0x0588c742': self.unknown_0x0588c742,
            'unknown_0x15793154': self.unknown_0x15793154.to_json(),
            'unknown_0xe8fc0acd': self.unknown_0xe8fc0acd,
            'hover_then_home_projectile': self.hover_then_home_projectile.to_json(),
            'ray_gun': self.ray_gun.to_json(),
            'unknown_0xdde5dccd': self.unknown_0xdde5dccd,
            'unknown_0x3b85732c': self.unknown_0x3b85732c,
            'unknown_0x296b1195': self.unknown_0x296b1195,
            'unknown_0xcf0bbe74': self.unknown_0xcf0bbe74,
            'unknown_0xa0d2af02': self.unknown_0xa0d2af02,
            'unknown_0xd7b53cdb': self.unknown_0xd7b53cdb,
            'claw_damage': self.claw_damage.to_json(),
            'claw_range_max': self.claw_range_max,
            'claw_range_min': self.claw_range_min,
            'claw_delay': self.claw_delay,
            'steam_blast': self.steam_blast.to_json(),
            'steam_texture': self.steam_texture,
            'steam_alpha': self.steam_alpha,
            'steam_fade_in': self.steam_fade_in,
            'steam_fade_out': self.steam_fade_out,
            'unknown_0xa296206a': self.unknown_0xa296206a,
            'unknown_0x10c7fd02': self.unknown_0x10c7fd02,
            'unknown_0xf6a752e3': self.unknown_0xf6a752e3,
            'unknown_0x802b706e': self.unknown_0x802b706e,
            'unknown_0xc80ac7db': self.unknown_0xc80ac7db,
            'unknown_0x2e6a683a': self.unknown_0x2e6a683a,
            'unknown_0x3e9f0188': self.unknown_0x3e9f0188,
            'unknown_0xd8ffae69': self.unknown_0xd8ffae69,
            'xy_scale': self.xy_scale.to_json(),
            'z_scale': self.z_scale.to_json(),
            'model_alpha': self.model_alpha.to_json(),
            'model_red': self.model_red.to_json(),
            'model_green': self.model_green.to_json(),
            'model_blue': self.model_blue.to_json(),
            'effects_alpha': self.effects_alpha.to_json(),
            'recheck_path_time': self.recheck_path_time,
            'recheck_path_distance': self.recheck_path_distance,
            'avoidance_range': self.avoidance_range,
            'scan_delay': self.scan_delay,
            'unknown_0x699da662': self.unknown_0x699da662,
            'unknown_0x8ffd0983': self.unknown_0x8ffd0983,
            'unknown_0xdedd30a4': self.unknown_0xdedd30a4,
            'unknown_0xf8243d17': self.unknown_0xf8243d17,
            'unknown_0xc6943950': self.unknown_0xc6943950,
            'unknown_0x83967ad2': self.unknown_0x83967ad2,
            'unknown_0x6c8ae89f': self.unknown_0x6c8ae89f,
            'unknown_0x8aea477e': self.unknown_0x8aea477e,
            'unknown_0x5f1a7dd8': self.unknown_0x5f1a7dd8,
            'hyper_mode': self.hyper_mode.to_json(),
            'hyper_mode_hard': self.hyper_mode_hard.to_json(),
            'hyper_mode_elite': self.hyper_mode_elite.to_json(),
            'hurl_lerp': self.hurl_lerp,
            'hurl_knock_back_multiplier': self.hurl_knock_back_multiplier,
            'hurl_knock_back_resistance': self.hurl_knock_back_resistance,
            'unknown_0x6cf3636f': self.unknown_0x6cf3636f,
            'unknown_0x85d4691c': self.unknown_0x85d4691c,
            'mod_inca_data': self.mod_inca_data.to_json(),
        }


def _decode_unknown_0xf4f4a01d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x12940ffc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x303b4954(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_rocket_range_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_rocket_range_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0588c742(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x15793154(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_unknown_0xe8fc0acd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdde5dccd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3b85732c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x296b1195(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcf0bbe74(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa0d2af02(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd7b53cdb(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_claw_range_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_claw_range_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_claw_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_steam_texture(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_steam_alpha(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_steam_fade_in(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_steam_fade_out(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa296206a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x10c7fd02(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf6a752e3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x802b706e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc80ac7db(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2e6a683a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3e9f0188(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd8ffae69(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_recheck_path_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_recheck_path_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_avoidance_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scan_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x699da662(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8ffd0983(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdedd30a4(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xf8243d17(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xc6943950(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x83967ad2(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x6c8ae89f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8aea477e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5f1a7dd8(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_hurl_lerp(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hurl_knock_back_multiplier(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hurl_knock_back_resistance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6cf3636f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x85d4691c(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xbe5e86b9: ('char', AnimationParameters.from_stream),
    0xf4f4a01d: ('unknown_0xf4f4a01d', _decode_unknown_0xf4f4a01d),
    0x12940ffc: ('unknown_0x12940ffc', _decode_unknown_0x12940ffc),
    0x303b4954: ('unknown_0x303b4954', _decode_unknown_0x303b4954),
    0xab247451: ('rocket', LaunchProjectileData.from_stream),
    0x55c19435: ('rocket_range_max', _decode_rocket_range_max),
    0xb3a13bd4: ('rocket_range_min', _decode_rocket_range_min),
    0x588c742: ('unknown_0x0588c742', _decode_unknown_0x0588c742),
    0x15793154: ('unknown_0x15793154', _decode_unknown_0x15793154),
    0xe8fc0acd: ('unknown_0xe8fc0acd', _decode_unknown_0xe8fc0acd),
    0x7039fb9f: ('hover_then_home_projectile', HoverThenHomeProjectile.from_stream),
    0xb98cba47: ('ray_gun', LaunchProjectileData.from_stream),
    0xdde5dccd: ('unknown_0xdde5dccd', _decode_unknown_0xdde5dccd),
    0x3b85732c: ('unknown_0x3b85732c', _decode_unknown_0x3b85732c),
    0x296b1195: ('unknown_0x296b1195', _decode_unknown_0x296b1195),
    0xcf0bbe74: ('unknown_0xcf0bbe74', _decode_unknown_0xcf0bbe74),
    0xa0d2af02: ('unknown_0xa0d2af02', _decode_unknown_0xa0d2af02),
    0xd7b53cdb: ('unknown_0xd7b53cdb', _decode_unknown_0xd7b53cdb),
    0x8dbaeef2: ('claw_damage', DamageInfo.from_stream),
    0x582b9b3b: ('claw_range_max', _decode_claw_range_max),
    0xbe4b34da: ('claw_range_min', _decode_claw_range_min),
    0xebb134b5: ('claw_delay', _decode_claw_delay),
    0xca91ecb0: ('steam_blast', LaunchProjectileData.from_stream),
    0x58a21824: ('steam_texture', _decode_steam_texture),
    0x6c692453: ('steam_alpha', _decode_steam_alpha),
    0x66a5cd17: ('steam_fade_in', _decode_steam_fade_in),
    0x5c5b8b5d: ('steam_fade_out', _decode_steam_fade_out),
    0xa296206a: ('unknown_0xa296206a', _decode_unknown_0xa296206a),
    0x10c7fd02: ('unknown_0x10c7fd02', _decode_unknown_0x10c7fd02),
    0xf6a752e3: ('unknown_0xf6a752e3', _decode_unknown_0xf6a752e3),
    0x802b706e: ('unknown_0x802b706e', _decode_unknown_0x802b706e),
    0xc80ac7db: ('unknown_0xc80ac7db', _decode_unknown_0xc80ac7db),
    0x2e6a683a: ('unknown_0x2e6a683a', _decode_unknown_0x2e6a683a),
    0x3e9f0188: ('unknown_0x3e9f0188', _decode_unknown_0x3e9f0188),
    0xd8ffae69: ('unknown_0xd8ffae69', _decode_unknown_0xd8ffae69),
    0x48ba8eb1: ('xy_scale', Spline.from_stream),
    0x180c38b0: ('z_scale', Spline.from_stream),
    0xf762790: ('model_alpha', Spline.from_stream),
    0xfeadc99: ('model_red', Spline.from_stream),
    0x55be3e8e: ('model_green', Spline.from_stream),
    0x79f7cc48: ('model_blue', Spline.from_stream),
    0x564bd8cd: ('effects_alpha', Spline.from_stream),
    0x9aa90b6b: ('recheck_path_time', _decode_recheck_path_time),
    0x7626ec89: ('recheck_path_distance', _decode_recheck_path_distance),
    0x50a9bd0d: ('avoidance_range', _decode_avoidance_range),
    0x7fc827a2: ('scan_delay', _decode_scan_delay),
    0x699da662: ('unknown_0x699da662', _decode_unknown_0x699da662),
    0x8ffd0983: ('unknown_0x8ffd0983', _decode_unknown_0x8ffd0983),
    0xdedd30a4: ('unknown_0xdedd30a4', _decode_unknown_0xdedd30a4),
    0xf8243d17: ('unknown_0xf8243d17', _decode_unknown_0xf8243d17),
    0xc6943950: ('unknown_0xc6943950', _decode_unknown_0xc6943950),
    0x83967ad2: ('unknown_0x83967ad2', _decode_unknown_0x83967ad2),
    0x6c8ae89f: ('unknown_0x6c8ae89f', _decode_unknown_0x6c8ae89f),
    0x8aea477e: ('unknown_0x8aea477e', _decode_unknown_0x8aea477e),
    0x5f1a7dd8: ('unknown_0x5f1a7dd8', _decode_unknown_0x5f1a7dd8),
    0xb0a9b728: ('hyper_mode', HyperModeData.from_stream),
    0x14499fcb: ('hyper_mode_hard', HyperModeData.from_stream),
    0xcd02221c: ('hyper_mode_elite', HyperModeData.from_stream),
    0x19863914: ('hurl_lerp', _decode_hurl_lerp),
    0x4ab182a: ('hurl_knock_back_multiplier', _decode_hurl_knock_back_multiplier),
    0xb008320b: ('hurl_knock_back_resistance', _decode_hurl_knock_back_resistance),
    0x6cf3636f: ('unknown_0x6cf3636f', _decode_unknown_0x6cf3636f),
    0x85d4691c: ('unknown_0x85d4691c', _decode_unknown_0x85d4691c),
    0xb4c02854: ('mod_inca_data', ModIncaData.from_stream),
}
