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
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Spline import Spline
from retro_data_structures.properties.echoes.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakGui_MiscJson(typing_extensions.TypedDict):
        unknown_0x2f9d48b8: bool
        unknown_0x71b475d0: float
        unknown_0x744165c4: float
        radar_world_radius: float
        unknown_0xa585c592: float
        unknown_0x04f4a6fe: float
        unknown_0x3c327181: float
        unknown_0xa581be26: float
        unknown_0x68d88e25: float
        unknown_0x889ef9ea: float
        unknown_0xb68ff81a: float
        unknown_0x04510638: float
        unknown_0x7a48c3b1: float
        unknown_0x0d257063: float
        unknown_0x2821bbca: bool
        unknown_0x5fdcf3d9: float
        unknown_0xc4dd4d5b: float
        unknown_0x6031503e: float
        unknown_0x9f5ebba2: float
        unknown_0x2930d57f: float
        unknown_0x3ac94cf1: float
        unknown_0x55b323e5: float
        unknown_0x411a705e: float
        unknown_0x0a9d701d: float
        unknown_0xf4a8e8ea: float
        unknown_0x50812f49: json_util.JsonValue
        unknown_0x7edc2474: json_util.JsonValue
        unknown_0x4f0d651c: float
        unknown_0x85c31390: float
        unknown_0xb93990e6: float
        unknown_0x4036cdb6: float
        unknown_0xa7cf8baa: float
        unknown_0x3e8e6afd: float
        unknown_0xec040d56: float
        unknown_0x236bbe14: float
        unknown_0x19f5c324: float
        unknown_0xfd559f8c: float
        unknown_0xe4702e21: float
        unknown_0x705ed5cb: int
        unknown_0x8922af69: int
        unknown_0x9b970087: int
        unknown_0x37dffbfd: float
        unknown_0xb41c7a19: float
        unknown_0xfd32e2d8: float
        unknown_0xba53888e: float
        unknown_0xcc7ae923: float
        unknown_0x8c723b8f: float
        unknown_0x1f228e64: float
        unknown_0xe34fa22c: float
        unknown_0xf4ec68ae: int
        unknown_0x4dd9d6d1: float
        unknown_0xad4d37cd: float
        unknown_0x95c78e5d: float
        threat_world_radius: float
        unknown_0x78174d4b: float
        unknown_0x3cb2115b: float
        unknown_0xfc30bb21: float
        unknown_0x86cdde75: float
        unknown_0xf3565ff4: int
        unknown_0x7d3c03eb: int
        unknown_0x72d4d899: int
        unknown_0xfb9a4cc7: int
        unknown_0xa1417b38: int
        unknown_0x71b207b4: int
        unknown_0xa2580838: float
        unknown_0x46d75fe1: float
        unknown_0x4f7cf7d8: float
        unknown_0x2bef7961: float
        unknown_0xdecc7bff: float
        unknown_0xcbff7b94: float
        unknown_0x0babf93b: float
        unknown_0xc0004f50: float
        unknown_0x4ee9c251: bool
        unknown_0xa71e83d5: float
        unknown_0x3652ef32: float
        unknown_0x4ff930a5: int
        unknown_0x1c106df3: int
        unknown_0xdaadf917: int
        unknown_0xe3d55457: int
        unknown_0xdd39f60a: int
        unknown_0x3db45f6a: str
        unknown_0x471f1217: str
        unknown_0xf8b84c58: str
        unknown_0xbc2c8de6: str
        unknown_0x54203510: str
        unknown_0xcf9fd47e: float
        unknown_0xcfb88ceb: float
        unknown_0x5e388dd0: float
        unknown_0x86bc055e: float
        unknown_0x2c412371: float
        unknown_0x3aaf2a8c: float
        unknown_0xb515dd12: float
        unknown_0xa949b037: float
        unknown_0xca9d401c: float
        unknown_0x8186e8fe: float
        unknown_0x02a2198a: float
        unknown_0x8b64dc44: bool
        unknown_0x7161446b: bool
        unknown_0xaaff9224: float
        unknown_0xfa4a836c: float
        unknown_0x23661b4f: float
        unknown_0x992b647a: float
        unknown_0x929d08cf: float
        unknown_0xffeba1f2: float
        unknown_0x13654f20: float
        unknown_0x7083faf0: float
        unknown_0x2845923c: float
        unknown_0xeb6a7f2a: float
        unknown_0xd05eb27a: float
        unknown_0xd067eaa3: float
        unknown_0x8a5a4d81: float
        unknown_0xcb816d90: float
        unknown_0x5bf27d7a: float
        unknown_0x220d60e1: float
        unknown_0xb27e700b: float
        unknown_0x5590c6ec: float
        unknown_0x8b66820d: float
        unknown_0x138f1104: float
        unknown_0xd0d1760e: float
        unknown_0xce9f5770: float
        unknown_0xeaf17d45: json_util.JsonObject
        unknown_0xd81537b6: json_util.JsonObject
        unknown_0x3ba84552: json_util.JsonObject
        unknown_0xeeb7839b: float
        unknown_0x24cf1719: float
        unknown_0xa4adf6ea: float
        unknown_0xe3755dda: float
        unknown_0xa607dfaa: float
        unknown_0xf5f7a748: float
        unknown_0x61215643: float
        unknown_0xa3f4095e: float
        unknown_0x7103ca90: bool
        unknown_0x22d4c6a3: float
        unknown_0xbe909e83: json_util.JsonValue
        unknown_0x7407e76f: json_util.JsonValue
        unknown_0x3547c23a: json_util.JsonValue
        unknown_0x577d0617: json_util.JsonValue
        unknown_0x216a5b7a: json_util.JsonValue
        unknown_0x0cd13d8b: json_util.JsonValue
        unknown_0x488e0820: json_util.JsonValue
        unknown_0xaf57fa7c: json_util.JsonValue
        unknown_0xac587cfa: json_util.JsonValue
        unknown_0x15230523: json_util.JsonValue
        unknown_0x54632076: json_util.JsonValue
        unknown_0x3659e45b: json_util.JsonValue
        unknown_0x5e617223: json_util.JsonValue
        unknown_0x43cca255: json_util.JsonValue
        unknown_0x079397fe: json_util.JsonValue
        unknown_0xe04a65a2: json_util.JsonValue
        unknown_0x70638eaa: json_util.JsonValue
        unknown_0x5b888032: float
        unknown_0xb7322d26: float
        unknown_0x79275f22: float
        unknown_0xf405af55: float
        unknown_0x3f85eb28: float
        unknown_0x19c5f88b: json_util.JsonValue
        unknown_0xd84b274b: json_util.JsonValue
        unknown_0x41a9414a: json_util.JsonValue
        unknown_0x80279e8a: json_util.JsonValue
        unknown_0x98d8e1ba: json_util.JsonValue
    

@dataclasses.dataclass()
class TweakGui_Misc(BaseProperty):
    unknown_0x2f9d48b8: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2f9d48b8, original_name='Unknown'
        ),
    })
    unknown_0x71b475d0: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x71b475d0, original_name='Unknown'
        ),
    })
    unknown_0x744165c4: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x744165c4, original_name='Unknown'
        ),
    })
    radar_world_radius: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xee1ba439, original_name='RadarWorldRadius'
        ),
    })
    unknown_0xa585c592: float = dataclasses.field(default=200.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa585c592, original_name='Unknown'
        ),
    })
    unknown_0x04f4a6fe: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x04f4a6fe, original_name='Unknown'
        ),
    })
    unknown_0x3c327181: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3c327181, original_name='Unknown'
        ),
    })
    unknown_0xa581be26: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa581be26, original_name='Unknown'
        ),
    })
    unknown_0x68d88e25: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x68d88e25, original_name='Unknown'
        ),
    })
    unknown_0x889ef9ea: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x889ef9ea, original_name='Unknown'
        ),
    })
    unknown_0xb68ff81a: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb68ff81a, original_name='Unknown'
        ),
    })
    unknown_0x04510638: float = dataclasses.field(default=99.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x04510638, original_name='Unknown'
        ),
    })
    unknown_0x7a48c3b1: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7a48c3b1, original_name='Unknown'
        ),
    })
    unknown_0x0d257063: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0d257063, original_name='Unknown'
        ),
    })
    unknown_0x2821bbca: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2821bbca, original_name='Unknown'
        ),
    })
    unknown_0x5fdcf3d9: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5fdcf3d9, original_name='Unknown'
        ),
    })
    unknown_0xc4dd4d5b: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc4dd4d5b, original_name='Unknown'
        ),
    })
    unknown_0x6031503e: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6031503e, original_name='Unknown'
        ),
    })
    unknown_0x9f5ebba2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9f5ebba2, original_name='Unknown'
        ),
    })
    unknown_0x2930d57f: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2930d57f, original_name='Unknown'
        ),
    })
    unknown_0x3ac94cf1: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3ac94cf1, original_name='Unknown'
        ),
    })
    unknown_0x55b323e5: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x55b323e5, original_name='Unknown'
        ),
    })
    unknown_0x411a705e: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x411a705e, original_name='Unknown'
        ),
    })
    unknown_0x0a9d701d: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0a9d701d, original_name='Unknown'
        ),
    })
    unknown_0xf4a8e8ea: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf4a8e8ea, original_name='Unknown'
        ),
    })
    unknown_0x50812f49: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x50812f49, original_name='Unknown', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_0x7edc2474: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x7edc2474, original_name='Unknown', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_0x4f0d651c: float = dataclasses.field(default=70.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4f0d651c, original_name='Unknown'
        ),
    })
    unknown_0x85c31390: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x85c31390, original_name='Unknown'
        ),
    })
    unknown_0xb93990e6: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb93990e6, original_name='Unknown'
        ),
    })
    unknown_0x4036cdb6: float = dataclasses.field(default=0.009999999776482582, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4036cdb6, original_name='Unknown'
        ),
    })
    unknown_0xa7cf8baa: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa7cf8baa, original_name='Unknown'
        ),
    })
    unknown_0x3e8e6afd: float = dataclasses.field(default=0.004999999888241291, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3e8e6afd, original_name='Unknown'
        ),
    })
    unknown_0xec040d56: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xec040d56, original_name='Unknown'
        ),
    })
    unknown_0x236bbe14: float = dataclasses.field(default=0.009999999776482582, metadata={
        'reflection': FieldReflection[float](
            float, id=0x236bbe14, original_name='Unknown'
        ),
    })
    unknown_0x19f5c324: float = dataclasses.field(default=0.019999999552965164, metadata={
        'reflection': FieldReflection[float](
            float, id=0x19f5c324, original_name='Unknown'
        ),
    })
    unknown_0xfd559f8c: float = dataclasses.field(default=0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfd559f8c, original_name='Unknown'
        ),
    })
    unknown_0xe4702e21: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe4702e21, original_name='Unknown'
        ),
    })
    unknown_0x705ed5cb: int = dataclasses.field(default=5, metadata={
        'reflection': FieldReflection[int](
            int, id=0x705ed5cb, original_name='Unknown'
        ),
    })
    unknown_0x8922af69: int = dataclasses.field(default=40, metadata={
        'reflection': FieldReflection[int](
            int, id=0x8922af69, original_name='Unknown'
        ),
    })
    unknown_0x9b970087: int = dataclasses.field(default=16, metadata={
        'reflection': FieldReflection[int](
            int, id=0x9b970087, original_name='Unknown'
        ),
    })
    unknown_0x37dffbfd: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x37dffbfd, original_name='Unknown'
        ),
    })
    unknown_0xb41c7a19: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb41c7a19, original_name='Unknown'
        ),
    })
    unknown_0xfd32e2d8: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfd32e2d8, original_name='Unknown'
        ),
    })
    unknown_0xba53888e: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xba53888e, original_name='Unknown'
        ),
    })
    unknown_0xcc7ae923: float = dataclasses.field(default=1.7000000476837158, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcc7ae923, original_name='Unknown'
        ),
    })
    unknown_0x8c723b8f: float = dataclasses.field(default=1.2000000476837158, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8c723b8f, original_name='Unknown'
        ),
    })
    unknown_0x1f228e64: float = dataclasses.field(default=1.7999999523162842, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1f228e64, original_name='Unknown'
        ),
    })
    unknown_0xe34fa22c: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe34fa22c, original_name='Unknown'
        ),
    })
    unknown_0xf4ec68ae: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xf4ec68ae, original_name='Unknown'
        ),
    })
    unknown_0x4dd9d6d1: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4dd9d6d1, original_name='Unknown'
        ),
    })
    unknown_0xad4d37cd: float = dataclasses.field(default=77.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xad4d37cd, original_name='Unknown'
        ),
    })
    unknown_0x95c78e5d: float = dataclasses.field(default=0.8999999761581421, metadata={
        'reflection': FieldReflection[float](
            float, id=0x95c78e5d, original_name='Unknown'
        ),
    })
    threat_world_radius: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1a8dc454, original_name='ThreatWorldRadius'
        ),
    })
    unknown_0x78174d4b: float = dataclasses.field(default=1.649999976158142, metadata={
        'reflection': FieldReflection[float](
            float, id=0x78174d4b, original_name='Unknown'
        ),
    })
    unknown_0x3cb2115b: float = dataclasses.field(default=0.03999999910593033, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3cb2115b, original_name='Unknown'
        ),
    })
    unknown_0xfc30bb21: float = dataclasses.field(default=0.03999999910593033, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfc30bb21, original_name='Unknown'
        ),
    })
    unknown_0x86cdde75: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x86cdde75, original_name='Unknown'
        ),
    })
    unknown_0xf3565ff4: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0xf3565ff4, original_name='Unknown'
        ),
    })
    unknown_0x7d3c03eb: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7d3c03eb, original_name='Unknown'
        ),
    })
    unknown_0x72d4d899: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x72d4d899, original_name='Unknown'
        ),
    })
    unknown_0xfb9a4cc7: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xfb9a4cc7, original_name='Unknown'
        ),
    })
    unknown_0xa1417b38: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa1417b38, original_name='Unknown'
        ),
    })
    unknown_0x71b207b4: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x71b207b4, original_name='Unknown'
        ),
    })
    unknown_0xa2580838: float = dataclasses.field(default=0.800000011920929, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa2580838, original_name='Unknown'
        ),
    })
    unknown_0x46d75fe1: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x46d75fe1, original_name='Unknown'
        ),
    })
    unknown_0x4f7cf7d8: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4f7cf7d8, original_name='Unknown'
        ),
    })
    unknown_0x2bef7961: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2bef7961, original_name='Unknown'
        ),
    })
    unknown_0xdecc7bff: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdecc7bff, original_name='Unknown'
        ),
    })
    unknown_0xcbff7b94: float = dataclasses.field(default=-2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcbff7b94, original_name='Unknown'
        ),
    })
    unknown_0x0babf93b: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0babf93b, original_name='Unknown'
        ),
    })
    unknown_0xc0004f50: float = dataclasses.field(default=3000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc0004f50, original_name='Unknown'
        ),
    })
    unknown_0x4ee9c251: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x4ee9c251, original_name='Unknown'
        ),
    })
    unknown_0xa71e83d5: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa71e83d5, original_name='Unknown'
        ),
    })
    unknown_0x3652ef32: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3652ef32, original_name='Unknown'
        ),
    })
    unknown_0x4ff930a5: int = dataclasses.field(default=15, metadata={
        'reflection': FieldReflection[int](
            int, id=0x4ff930a5, original_name='Unknown'
        ),
    })
    unknown_0x1c106df3: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1c106df3, original_name='Unknown'
        ),
    })
    unknown_0xdaadf917: int = dataclasses.field(default=6, metadata={
        'reflection': FieldReflection[int](
            int, id=0xdaadf917, original_name='Unknown'
        ),
    })
    unknown_0xe3d55457: int = dataclasses.field(default=9, metadata={
        'reflection': FieldReflection[int](
            int, id=0xe3d55457, original_name='Unknown'
        ),
    })
    unknown_0xdd39f60a: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0xdd39f60a, original_name='Unknown'
        ),
    })
    unknown_0x3db45f6a: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x3db45f6a, original_name='Unknown'
        ),
    })
    unknown_0x471f1217: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x471f1217, original_name='Unknown'
        ),
    })
    unknown_0xf8b84c58: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xf8b84c58, original_name='Unknown'
        ),
    })
    unknown_0xbc2c8de6: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xbc2c8de6, original_name='Unknown'
        ),
    })
    unknown_0x54203510: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x54203510, original_name='Unknown'
        ),
    })
    unknown_0xcf9fd47e: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcf9fd47e, original_name='Unknown'
        ),
    })
    unknown_0xcfb88ceb: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcfb88ceb, original_name='Unknown'
        ),
    })
    unknown_0x5e388dd0: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5e388dd0, original_name='Unknown'
        ),
    })
    unknown_0x86bc055e: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x86bc055e, original_name='Unknown'
        ),
    })
    unknown_0x2c412371: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2c412371, original_name='Unknown'
        ),
    })
    unknown_0x3aaf2a8c: float = dataclasses.field(default=0.800000011920929, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3aaf2a8c, original_name='Unknown'
        ),
    })
    unknown_0xb515dd12: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb515dd12, original_name='Unknown'
        ),
    })
    unknown_0xa949b037: float = dataclasses.field(default=0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa949b037, original_name='Unknown'
        ),
    })
    unknown_0xca9d401c: float = dataclasses.field(default=0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0xca9d401c, original_name='Unknown'
        ),
    })
    unknown_0x8186e8fe: float = dataclasses.field(default=0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8186e8fe, original_name='Unknown'
        ),
    })
    unknown_0x02a2198a: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x02a2198a, original_name='Unknown'
        ),
    })
    unknown_0x8b64dc44: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x8b64dc44, original_name='Unknown'
        ),
    })
    unknown_0x7161446b: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7161446b, original_name='Unknown'
        ),
    })
    unknown_0xaaff9224: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xaaff9224, original_name='Unknown'
        ),
    })
    unknown_0xfa4a836c: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfa4a836c, original_name='Unknown'
        ),
    })
    unknown_0x23661b4f: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x23661b4f, original_name='Unknown'
        ),
    })
    unknown_0x992b647a: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x992b647a, original_name='Unknown'
        ),
    })
    unknown_0x929d08cf: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x929d08cf, original_name='Unknown'
        ),
    })
    unknown_0xffeba1f2: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xffeba1f2, original_name='Unknown'
        ),
    })
    unknown_0x13654f20: float = dataclasses.field(default=0.800000011920929, metadata={
        'reflection': FieldReflection[float](
            float, id=0x13654f20, original_name='Unknown'
        ),
    })
    unknown_0x7083faf0: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7083faf0, original_name='Unknown'
        ),
    })
    unknown_0x2845923c: float = dataclasses.field(default=0.8999999761581421, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2845923c, original_name='Unknown'
        ),
    })
    unknown_0xeb6a7f2a: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0xeb6a7f2a, original_name='Unknown'
        ),
    })
    unknown_0xd05eb27a: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd05eb27a, original_name='Unknown'
        ),
    })
    unknown_0xd067eaa3: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd067eaa3, original_name='Unknown'
        ),
    })
    unknown_0x8a5a4d81: float = dataclasses.field(default=144.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8a5a4d81, original_name='Unknown'
        ),
    })
    unknown_0xcb816d90: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcb816d90, original_name='Unknown'
        ),
    })
    unknown_0x5bf27d7a: float = dataclasses.field(default=0.800000011920929, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5bf27d7a, original_name='Unknown'
        ),
    })
    unknown_0x220d60e1: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x220d60e1, original_name='Unknown'
        ),
    })
    unknown_0xb27e700b: float = dataclasses.field(default=0.800000011920929, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb27e700b, original_name='Unknown'
        ),
    })
    unknown_0x5590c6ec: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5590c6ec, original_name='Unknown'
        ),
    })
    unknown_0x8b66820d: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8b66820d, original_name='Unknown'
        ),
    })
    unknown_0x138f1104: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x138f1104, original_name='Unknown'
        ),
    })
    unknown_0xd0d1760e: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd0d1760e, original_name='Unknown'
        ),
    })
    unknown_0xce9f5770: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xce9f5770, original_name='Unknown'
        ),
    })
    unknown_0xeaf17d45: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xeaf17d45, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0xd81537b6: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xd81537b6, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0x3ba84552: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x3ba84552, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    unknown_0xeeb7839b: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0xeeb7839b, original_name='Unknown'
        ),
    })
    unknown_0x24cf1719: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x24cf1719, original_name='Unknown'
        ),
    })
    unknown_0xa4adf6ea: float = dataclasses.field(default=0.800000011920929, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa4adf6ea, original_name='Unknown'
        ),
    })
    unknown_0xe3755dda: float = dataclasses.field(default=1.100000023841858, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe3755dda, original_name='Unknown'
        ),
    })
    unknown_0xa607dfaa: float = dataclasses.field(default=1.100000023841858, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa607dfaa, original_name='Unknown'
        ),
    })
    unknown_0xf5f7a748: float = dataclasses.field(default=1.350000023841858, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf5f7a748, original_name='Unknown'
        ),
    })
    unknown_0x61215643: float = dataclasses.field(default=1.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0x61215643, original_name='Unknown'
        ),
    })
    unknown_0xa3f4095e: float = dataclasses.field(default=-10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa3f4095e, original_name='Unknown'
        ),
    })
    unknown_0x7103ca90: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7103ca90, original_name='Unknown'
        ),
    })
    unknown_0x22d4c6a3: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x22d4c6a3, original_name='Unknown'
        ),
    })
    unknown_0xbe909e83: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xbe909e83, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x7407e76f: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x7407e76f, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x3547c23a: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x3547c23a, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x577d0617: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x577d0617, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x216a5b7a: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x216a5b7a, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x0cd13d8b: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x0cd13d8b, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x488e0820: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x488e0820, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xaf57fa7c: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xaf57fa7c, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xac587cfa: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xac587cfa, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x15230523: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x15230523, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x54632076: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x54632076, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x3659e45b: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x3659e45b, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x5e617223: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x5e617223, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x43cca255: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x43cca255, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x079397fe: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x079397fe, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xe04a65a2: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xe04a65a2, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x70638eaa: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x70638eaa, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x5b888032: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5b888032, original_name='Unknown'
        ),
    })
    unknown_0xb7322d26: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb7322d26, original_name='Unknown'
        ),
    })
    unknown_0x79275f22: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x79275f22, original_name='Unknown'
        ),
    })
    unknown_0xf405af55: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf405af55, original_name='Unknown'
        ),
    })
    unknown_0x3f85eb28: float = dataclasses.field(default=4.699999809265137, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3f85eb28, original_name='Unknown'
        ),
    })
    unknown_0x19c5f88b: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x19c5f88b, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xd84b274b: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xd84b274b, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x41a9414a: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x41a9414a, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x80279e8a: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x80279e8a, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x98d8e1ba: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x98d8e1ba, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

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
        if property_count != 160:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2f9d48b8
        unknown_0x2f9d48b8 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71b475d0
        unknown_0x71b475d0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x744165c4
        unknown_0x744165c4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xee1ba439
        radar_world_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa585c592
        unknown_0xa585c592 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x04f4a6fe
        unknown_0x04f4a6fe = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3c327181
        unknown_0x3c327181 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa581be26
        unknown_0xa581be26 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x68d88e25
        unknown_0x68d88e25 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x889ef9ea
        unknown_0x889ef9ea = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb68ff81a
        unknown_0xb68ff81a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x04510638
        unknown_0x04510638 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7a48c3b1
        unknown_0x7a48c3b1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0d257063
        unknown_0x0d257063 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2821bbca
        unknown_0x2821bbca = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5fdcf3d9
        unknown_0x5fdcf3d9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc4dd4d5b
        unknown_0xc4dd4d5b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6031503e
        unknown_0x6031503e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9f5ebba2
        unknown_0x9f5ebba2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2930d57f
        unknown_0x2930d57f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3ac94cf1
        unknown_0x3ac94cf1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x55b323e5
        unknown_0x55b323e5 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x411a705e
        unknown_0x411a705e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0a9d701d
        unknown_0x0a9d701d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf4a8e8ea
        unknown_0xf4a8e8ea = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x50812f49
        unknown_0x50812f49 = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7edc2474
        unknown_0x7edc2474 = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4f0d651c
        unknown_0x4f0d651c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x85c31390
        unknown_0x85c31390 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb93990e6
        unknown_0xb93990e6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4036cdb6
        unknown_0x4036cdb6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa7cf8baa
        unknown_0xa7cf8baa = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3e8e6afd
        unknown_0x3e8e6afd = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xec040d56
        unknown_0xec040d56 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x236bbe14
        unknown_0x236bbe14 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x19f5c324
        unknown_0x19f5c324 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd559f8c
        unknown_0xfd559f8c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe4702e21
        unknown_0xe4702e21 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x705ed5cb
        unknown_0x705ed5cb = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8922af69
        unknown_0x8922af69 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9b970087
        unknown_0x9b970087 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x37dffbfd
        unknown_0x37dffbfd = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb41c7a19
        unknown_0xb41c7a19 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd32e2d8
        unknown_0xfd32e2d8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xba53888e
        unknown_0xba53888e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcc7ae923
        unknown_0xcc7ae923 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8c723b8f
        unknown_0x8c723b8f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1f228e64
        unknown_0x1f228e64 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe34fa22c
        unknown_0xe34fa22c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf4ec68ae
        unknown_0xf4ec68ae = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4dd9d6d1
        unknown_0x4dd9d6d1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad4d37cd
        unknown_0xad4d37cd = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x95c78e5d
        unknown_0x95c78e5d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a8dc454
        threat_world_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x78174d4b
        unknown_0x78174d4b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3cb2115b
        unknown_0x3cb2115b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfc30bb21
        unknown_0xfc30bb21 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x86cdde75
        unknown_0x86cdde75 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf3565ff4
        unknown_0xf3565ff4 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7d3c03eb
        unknown_0x7d3c03eb = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x72d4d899
        unknown_0x72d4d899 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfb9a4cc7
        unknown_0xfb9a4cc7 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa1417b38
        unknown_0xa1417b38 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71b207b4
        unknown_0x71b207b4 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa2580838
        unknown_0xa2580838 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x46d75fe1
        unknown_0x46d75fe1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4f7cf7d8
        unknown_0x4f7cf7d8 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2bef7961
        unknown_0x2bef7961 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdecc7bff
        unknown_0xdecc7bff = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcbff7b94
        unknown_0xcbff7b94 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0babf93b
        unknown_0x0babf93b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc0004f50
        unknown_0xc0004f50 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ee9c251
        unknown_0x4ee9c251 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa71e83d5
        unknown_0xa71e83d5 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3652ef32
        unknown_0x3652ef32 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4ff930a5
        unknown_0x4ff930a5 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1c106df3
        unknown_0x1c106df3 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdaadf917
        unknown_0xdaadf917 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe3d55457
        unknown_0xe3d55457 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdd39f60a
        unknown_0xdd39f60a = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3db45f6a
        unknown_0x3db45f6a = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x471f1217
        unknown_0x471f1217 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf8b84c58
        unknown_0xf8b84c58 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbc2c8de6
        unknown_0xbc2c8de6 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x54203510
        unknown_0x54203510 = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf9fd47e
        unknown_0xcf9fd47e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcfb88ceb
        unknown_0xcfb88ceb = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5e388dd0
        unknown_0x5e388dd0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x86bc055e
        unknown_0x86bc055e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2c412371
        unknown_0x2c412371 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3aaf2a8c
        unknown_0x3aaf2a8c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb515dd12
        unknown_0xb515dd12 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa949b037
        unknown_0xa949b037 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xca9d401c
        unknown_0xca9d401c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8186e8fe
        unknown_0x8186e8fe = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x02a2198a
        unknown_0x02a2198a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b64dc44
        unknown_0x8b64dc44 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7161446b
        unknown_0x7161446b = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaaff9224
        unknown_0xaaff9224 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfa4a836c
        unknown_0xfa4a836c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x23661b4f
        unknown_0x23661b4f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x992b647a
        unknown_0x992b647a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x929d08cf
        unknown_0x929d08cf = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xffeba1f2
        unknown_0xffeba1f2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x13654f20
        unknown_0x13654f20 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7083faf0
        unknown_0x7083faf0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2845923c
        unknown_0x2845923c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeb6a7f2a
        unknown_0xeb6a7f2a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd05eb27a
        unknown_0xd05eb27a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd067eaa3
        unknown_0xd067eaa3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8a5a4d81
        unknown_0x8a5a4d81 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcb816d90
        unknown_0xcb816d90 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5bf27d7a
        unknown_0x5bf27d7a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x220d60e1
        unknown_0x220d60e1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb27e700b
        unknown_0xb27e700b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5590c6ec
        unknown_0x5590c6ec = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b66820d
        unknown_0x8b66820d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x138f1104
        unknown_0x138f1104 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd0d1760e
        unknown_0xd0d1760e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xce9f5770
        unknown_0xce9f5770 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeaf17d45
        unknown_0xeaf17d45 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd81537b6
        unknown_0xd81537b6 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3ba84552
        unknown_0x3ba84552 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeeb7839b
        unknown_0xeeb7839b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x24cf1719
        unknown_0x24cf1719 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa4adf6ea
        unknown_0xa4adf6ea = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe3755dda
        unknown_0xe3755dda = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa607dfaa
        unknown_0xa607dfaa = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf5f7a748
        unknown_0xf5f7a748 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x61215643
        unknown_0x61215643 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa3f4095e
        unknown_0xa3f4095e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7103ca90
        unknown_0x7103ca90 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x22d4c6a3
        unknown_0x22d4c6a3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe909e83
        unknown_0xbe909e83 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7407e76f
        unknown_0x7407e76f = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3547c23a
        unknown_0x3547c23a = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x577d0617
        unknown_0x577d0617 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x216a5b7a
        unknown_0x216a5b7a = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0cd13d8b
        unknown_0x0cd13d8b = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x488e0820
        unknown_0x488e0820 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaf57fa7c
        unknown_0xaf57fa7c = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xac587cfa
        unknown_0xac587cfa = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x15230523
        unknown_0x15230523 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x54632076
        unknown_0x54632076 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3659e45b
        unknown_0x3659e45b = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5e617223
        unknown_0x5e617223 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x43cca255
        unknown_0x43cca255 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x079397fe
        unknown_0x079397fe = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe04a65a2
        unknown_0xe04a65a2 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x70638eaa
        unknown_0x70638eaa = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5b888032
        unknown_0x5b888032 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb7322d26
        unknown_0xb7322d26 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x79275f22
        unknown_0x79275f22 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf405af55
        unknown_0xf405af55 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3f85eb28
        unknown_0x3f85eb28 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x19c5f88b
        unknown_0x19c5f88b = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd84b274b
        unknown_0xd84b274b = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x41a9414a
        unknown_0x41a9414a = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80279e8a
        unknown_0x80279e8a = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x98d8e1ba
        unknown_0x98d8e1ba = Color.from_stream(data)
    
        return cls(unknown_0x2f9d48b8, unknown_0x71b475d0, unknown_0x744165c4, radar_world_radius, unknown_0xa585c592, unknown_0x04f4a6fe, unknown_0x3c327181, unknown_0xa581be26, unknown_0x68d88e25, unknown_0x889ef9ea, unknown_0xb68ff81a, unknown_0x04510638, unknown_0x7a48c3b1, unknown_0x0d257063, unknown_0x2821bbca, unknown_0x5fdcf3d9, unknown_0xc4dd4d5b, unknown_0x6031503e, unknown_0x9f5ebba2, unknown_0x2930d57f, unknown_0x3ac94cf1, unknown_0x55b323e5, unknown_0x411a705e, unknown_0x0a9d701d, unknown_0xf4a8e8ea, unknown_0x50812f49, unknown_0x7edc2474, unknown_0x4f0d651c, unknown_0x85c31390, unknown_0xb93990e6, unknown_0x4036cdb6, unknown_0xa7cf8baa, unknown_0x3e8e6afd, unknown_0xec040d56, unknown_0x236bbe14, unknown_0x19f5c324, unknown_0xfd559f8c, unknown_0xe4702e21, unknown_0x705ed5cb, unknown_0x8922af69, unknown_0x9b970087, unknown_0x37dffbfd, unknown_0xb41c7a19, unknown_0xfd32e2d8, unknown_0xba53888e, unknown_0xcc7ae923, unknown_0x8c723b8f, unknown_0x1f228e64, unknown_0xe34fa22c, unknown_0xf4ec68ae, unknown_0x4dd9d6d1, unknown_0xad4d37cd, unknown_0x95c78e5d, threat_world_radius, unknown_0x78174d4b, unknown_0x3cb2115b, unknown_0xfc30bb21, unknown_0x86cdde75, unknown_0xf3565ff4, unknown_0x7d3c03eb, unknown_0x72d4d899, unknown_0xfb9a4cc7, unknown_0xa1417b38, unknown_0x71b207b4, unknown_0xa2580838, unknown_0x46d75fe1, unknown_0x4f7cf7d8, unknown_0x2bef7961, unknown_0xdecc7bff, unknown_0xcbff7b94, unknown_0x0babf93b, unknown_0xc0004f50, unknown_0x4ee9c251, unknown_0xa71e83d5, unknown_0x3652ef32, unknown_0x4ff930a5, unknown_0x1c106df3, unknown_0xdaadf917, unknown_0xe3d55457, unknown_0xdd39f60a, unknown_0x3db45f6a, unknown_0x471f1217, unknown_0xf8b84c58, unknown_0xbc2c8de6, unknown_0x54203510, unknown_0xcf9fd47e, unknown_0xcfb88ceb, unknown_0x5e388dd0, unknown_0x86bc055e, unknown_0x2c412371, unknown_0x3aaf2a8c, unknown_0xb515dd12, unknown_0xa949b037, unknown_0xca9d401c, unknown_0x8186e8fe, unknown_0x02a2198a, unknown_0x8b64dc44, unknown_0x7161446b, unknown_0xaaff9224, unknown_0xfa4a836c, unknown_0x23661b4f, unknown_0x992b647a, unknown_0x929d08cf, unknown_0xffeba1f2, unknown_0x13654f20, unknown_0x7083faf0, unknown_0x2845923c, unknown_0xeb6a7f2a, unknown_0xd05eb27a, unknown_0xd067eaa3, unknown_0x8a5a4d81, unknown_0xcb816d90, unknown_0x5bf27d7a, unknown_0x220d60e1, unknown_0xb27e700b, unknown_0x5590c6ec, unknown_0x8b66820d, unknown_0x138f1104, unknown_0xd0d1760e, unknown_0xce9f5770, unknown_0xeaf17d45, unknown_0xd81537b6, unknown_0x3ba84552, unknown_0xeeb7839b, unknown_0x24cf1719, unknown_0xa4adf6ea, unknown_0xe3755dda, unknown_0xa607dfaa, unknown_0xf5f7a748, unknown_0x61215643, unknown_0xa3f4095e, unknown_0x7103ca90, unknown_0x22d4c6a3, unknown_0xbe909e83, unknown_0x7407e76f, unknown_0x3547c23a, unknown_0x577d0617, unknown_0x216a5b7a, unknown_0x0cd13d8b, unknown_0x488e0820, unknown_0xaf57fa7c, unknown_0xac587cfa, unknown_0x15230523, unknown_0x54632076, unknown_0x3659e45b, unknown_0x5e617223, unknown_0x43cca255, unknown_0x079397fe, unknown_0xe04a65a2, unknown_0x70638eaa, unknown_0x5b888032, unknown_0xb7322d26, unknown_0x79275f22, unknown_0xf405af55, unknown_0x3f85eb28, unknown_0x19c5f88b, unknown_0xd84b274b, unknown_0x41a9414a, unknown_0x80279e8a, unknown_0x98d8e1ba)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\xa0')  # 160 properties

        data.write(b'/\x9dH\xb8')  # 0x2f9d48b8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x2f9d48b8))

        data.write(b'q\xb4u\xd0')  # 0x71b475d0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x71b475d0))

        data.write(b'tAe\xc4')  # 0x744165c4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x744165c4))

        data.write(b'\xee\x1b\xa49')  # 0xee1ba439
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.radar_world_radius))

        data.write(b'\xa5\x85\xc5\x92')  # 0xa585c592
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa585c592))

        data.write(b'\x04\xf4\xa6\xfe')  # 0x4f4a6fe
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x04f4a6fe))

        data.write(b'<2q\x81')  # 0x3c327181
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3c327181))

        data.write(b'\xa5\x81\xbe&')  # 0xa581be26
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa581be26))

        data.write(b'h\xd8\x8e%')  # 0x68d88e25
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x68d88e25))

        data.write(b'\x88\x9e\xf9\xea')  # 0x889ef9ea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x889ef9ea))

        data.write(b'\xb6\x8f\xf8\x1a')  # 0xb68ff81a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb68ff81a))

        data.write(b'\x04Q\x068')  # 0x4510638
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x04510638))

        data.write(b'zH\xc3\xb1')  # 0x7a48c3b1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7a48c3b1))

        data.write(b'\r%pc')  # 0xd257063
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0d257063))

        data.write(b'(!\xbb\xca')  # 0x2821bbca
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x2821bbca))

        data.write(b'_\xdc\xf3\xd9')  # 0x5fdcf3d9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5fdcf3d9))

        data.write(b'\xc4\xddM[')  # 0xc4dd4d5b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc4dd4d5b))

        data.write(b'`1P>')  # 0x6031503e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6031503e))

        data.write(b'\x9f^\xbb\xa2')  # 0x9f5ebba2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9f5ebba2))

        data.write(b')0\xd5\x7f')  # 0x2930d57f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2930d57f))

        data.write(b':\xc9L\xf1')  # 0x3ac94cf1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3ac94cf1))

        data.write(b'U\xb3#\xe5')  # 0x55b323e5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x55b323e5))

        data.write(b'A\x1ap^')  # 0x411a705e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x411a705e))

        data.write(b'\n\x9dp\x1d')  # 0xa9d701d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0a9d701d))

        data.write(b'\xf4\xa8\xe8\xea')  # 0xf4a8e8ea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf4a8e8ea))

        data.write(b'P\x81/I')  # 0x50812f49
        data.write(b'\x00\x0c')  # size
        self.unknown_0x50812f49.to_stream(data)

        data.write(b'~\xdc$t')  # 0x7edc2474
        data.write(b'\x00\x0c')  # size
        self.unknown_0x7edc2474.to_stream(data)

        data.write(b'O\re\x1c')  # 0x4f0d651c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4f0d651c))

        data.write(b'\x85\xc3\x13\x90')  # 0x85c31390
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x85c31390))

        data.write(b'\xb99\x90\xe6')  # 0xb93990e6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb93990e6))

        data.write(b'@6\xcd\xb6')  # 0x4036cdb6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4036cdb6))

        data.write(b'\xa7\xcf\x8b\xaa')  # 0xa7cf8baa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa7cf8baa))

        data.write(b'>\x8ej\xfd')  # 0x3e8e6afd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3e8e6afd))

        data.write(b'\xec\x04\rV')  # 0xec040d56
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xec040d56))

        data.write(b'#k\xbe\x14')  # 0x236bbe14
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x236bbe14))

        data.write(b'\x19\xf5\xc3$')  # 0x19f5c324
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x19f5c324))

        data.write(b'\xfdU\x9f\x8c')  # 0xfd559f8c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfd559f8c))

        data.write(b'\xe4p.!')  # 0xe4702e21
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe4702e21))

        data.write(b'p^\xd5\xcb')  # 0x705ed5cb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x705ed5cb))

        data.write(b'\x89"\xafi')  # 0x8922af69
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x8922af69))

        data.write(b'\x9b\x97\x00\x87')  # 0x9b970087
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x9b970087))

        data.write(b'7\xdf\xfb\xfd')  # 0x37dffbfd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x37dffbfd))

        data.write(b'\xb4\x1cz\x19')  # 0xb41c7a19
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb41c7a19))

        data.write(b'\xfd2\xe2\xd8')  # 0xfd32e2d8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfd32e2d8))

        data.write(b'\xbaS\x88\x8e')  # 0xba53888e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xba53888e))

        data.write(b'\xccz\xe9#')  # 0xcc7ae923
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcc7ae923))

        data.write(b'\x8cr;\x8f')  # 0x8c723b8f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8c723b8f))

        data.write(b'\x1f"\x8ed')  # 0x1f228e64
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1f228e64))

        data.write(b'\xe3O\xa2,')  # 0xe34fa22c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe34fa22c))

        data.write(b'\xf4\xech\xae')  # 0xf4ec68ae
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xf4ec68ae))

        data.write(b'M\xd9\xd6\xd1')  # 0x4dd9d6d1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4dd9d6d1))

        data.write(b'\xadM7\xcd')  # 0xad4d37cd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xad4d37cd))

        data.write(b'\x95\xc7\x8e]')  # 0x95c78e5d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x95c78e5d))

        data.write(b'\x1a\x8d\xc4T')  # 0x1a8dc454
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.threat_world_radius))

        data.write(b'x\x17MK')  # 0x78174d4b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x78174d4b))

        data.write(b'<\xb2\x11[')  # 0x3cb2115b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3cb2115b))

        data.write(b'\xfc0\xbb!')  # 0xfc30bb21
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfc30bb21))

        data.write(b'\x86\xcd\xdeu')  # 0x86cdde75
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x86cdde75))

        data.write(b'\xf3V_\xf4')  # 0xf3565ff4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xf3565ff4))

        data.write(b'}<\x03\xeb')  # 0x7d3c03eb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x7d3c03eb))

        data.write(b'r\xd4\xd8\x99')  # 0x72d4d899
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x72d4d899))

        data.write(b'\xfb\x9aL\xc7')  # 0xfb9a4cc7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xfb9a4cc7))

        data.write(b'\xa1A{8')  # 0xa1417b38
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xa1417b38))

        data.write(b'q\xb2\x07\xb4')  # 0x71b207b4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x71b207b4))

        data.write(b'\xa2X\x088')  # 0xa2580838
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa2580838))

        data.write(b'F\xd7_\xe1')  # 0x46d75fe1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x46d75fe1))

        data.write(b'O|\xf7\xd8')  # 0x4f7cf7d8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4f7cf7d8))

        data.write(b'+\xefya')  # 0x2bef7961
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2bef7961))

        data.write(b'\xde\xcc{\xff')  # 0xdecc7bff
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xdecc7bff))

        data.write(b'\xcb\xff{\x94')  # 0xcbff7b94
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcbff7b94))

        data.write(b'\x0b\xab\xf9;')  # 0xbabf93b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0babf93b))

        data.write(b'\xc0\x00OP')  # 0xc0004f50
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc0004f50))

        data.write(b'N\xe9\xc2Q')  # 0x4ee9c251
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x4ee9c251))

        data.write(b'\xa7\x1e\x83\xd5')  # 0xa71e83d5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa71e83d5))

        data.write(b'6R\xef2')  # 0x3652ef32
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3652ef32))

        data.write(b'O\xf90\xa5')  # 0x4ff930a5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x4ff930a5))

        data.write(b'\x1c\x10m\xf3')  # 0x1c106df3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x1c106df3))

        data.write(b'\xda\xad\xf9\x17')  # 0xdaadf917
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xdaadf917))

        data.write(b'\xe3\xd5TW')  # 0xe3d55457
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xe3d55457))

        data.write(b'\xdd9\xf6\n')  # 0xdd39f60a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xdd39f60a))

        data.write(b'=\xb4_j')  # 0x3db45f6a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0x3db45f6a.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'G\x1f\x12\x17')  # 0x471f1217
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0x471f1217.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf8\xb8LX')  # 0xf8b84c58
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0xf8b84c58.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbc,\x8d\xe6')  # 0xbc2c8de6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0xbc2c8de6.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'T 5\x10')  # 0x54203510
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0x54203510.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xcf\x9f\xd4~')  # 0xcf9fd47e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcf9fd47e))

        data.write(b'\xcf\xb8\x8c\xeb')  # 0xcfb88ceb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcfb88ceb))

        data.write(b'^8\x8d\xd0')  # 0x5e388dd0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5e388dd0))

        data.write(b'\x86\xbc\x05^')  # 0x86bc055e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x86bc055e))

        data.write(b',A#q')  # 0x2c412371
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2c412371))

        data.write(b':\xaf*\x8c')  # 0x3aaf2a8c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3aaf2a8c))

        data.write(b'\xb5\x15\xdd\x12')  # 0xb515dd12
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb515dd12))

        data.write(b'\xa9I\xb07')  # 0xa949b037
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa949b037))

        data.write(b'\xca\x9d@\x1c')  # 0xca9d401c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xca9d401c))

        data.write(b'\x81\x86\xe8\xfe')  # 0x8186e8fe
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8186e8fe))

        data.write(b'\x02\xa2\x19\x8a')  # 0x2a2198a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x02a2198a))

        data.write(b'\x8bd\xdcD')  # 0x8b64dc44
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x8b64dc44))

        data.write(b'qaDk')  # 0x7161446b
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x7161446b))

        data.write(b'\xaa\xff\x92$')  # 0xaaff9224
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xaaff9224))

        data.write(b'\xfaJ\x83l')  # 0xfa4a836c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfa4a836c))

        data.write(b'#f\x1bO')  # 0x23661b4f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x23661b4f))

        data.write(b'\x99+dz')  # 0x992b647a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x992b647a))

        data.write(b'\x92\x9d\x08\xcf')  # 0x929d08cf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x929d08cf))

        data.write(b'\xff\xeb\xa1\xf2')  # 0xffeba1f2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xffeba1f2))

        data.write(b'\x13eO ')  # 0x13654f20
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x13654f20))

        data.write(b'p\x83\xfa\xf0')  # 0x7083faf0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7083faf0))

        data.write(b'(E\x92<')  # 0x2845923c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2845923c))

        data.write(b'\xebj\x7f*')  # 0xeb6a7f2a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xeb6a7f2a))

        data.write(b'\xd0^\xb2z')  # 0xd05eb27a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd05eb27a))

        data.write(b'\xd0g\xea\xa3')  # 0xd067eaa3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd067eaa3))

        data.write(b'\x8aZM\x81')  # 0x8a5a4d81
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8a5a4d81))

        data.write(b'\xcb\x81m\x90')  # 0xcb816d90
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcb816d90))

        data.write(b'[\xf2}z')  # 0x5bf27d7a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5bf27d7a))

        data.write(b'"\r`\xe1')  # 0x220d60e1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x220d60e1))

        data.write(b'\xb2~p\x0b')  # 0xb27e700b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb27e700b))

        data.write(b'U\x90\xc6\xec')  # 0x5590c6ec
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5590c6ec))

        data.write(b'\x8bf\x82\r')  # 0x8b66820d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8b66820d))

        data.write(b'\x13\x8f\x11\x04')  # 0x138f1104
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x138f1104))

        data.write(b'\xd0\xd1v\x0e')  # 0xd0d1760e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd0d1760e))

        data.write(b'\xce\x9fWp')  # 0xce9f5770
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xce9f5770))

        data.write(b'\xea\xf1}E')  # 0xeaf17d45
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xeaf17d45.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd8\x157\xb6')  # 0xd81537b6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xd81537b6.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b';\xa8ER')  # 0x3ba84552
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0x3ba84552.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xee\xb7\x83\x9b')  # 0xeeb7839b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xeeb7839b))

        data.write(b'$\xcf\x17\x19')  # 0x24cf1719
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x24cf1719))

        data.write(b'\xa4\xad\xf6\xea')  # 0xa4adf6ea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa4adf6ea))

        data.write(b'\xe3u]\xda')  # 0xe3755dda
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe3755dda))

        data.write(b'\xa6\x07\xdf\xaa')  # 0xa607dfaa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa607dfaa))

        data.write(b'\xf5\xf7\xa7H')  # 0xf5f7a748
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf5f7a748))

        data.write(b'a!VC')  # 0x61215643
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x61215643))

        data.write(b'\xa3\xf4\t^')  # 0xa3f4095e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa3f4095e))

        data.write(b'q\x03\xca\x90')  # 0x7103ca90
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x7103ca90))

        data.write(b'"\xd4\xc6\xa3')  # 0x22d4c6a3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x22d4c6a3))

        data.write(b'\xbe\x90\x9e\x83')  # 0xbe909e83
        data.write(b'\x00\x10')  # size
        self.unknown_0xbe909e83.to_stream(data)

        data.write(b't\x07\xe7o')  # 0x7407e76f
        data.write(b'\x00\x10')  # size
        self.unknown_0x7407e76f.to_stream(data)

        data.write(b'5G\xc2:')  # 0x3547c23a
        data.write(b'\x00\x10')  # size
        self.unknown_0x3547c23a.to_stream(data)

        data.write(b'W}\x06\x17')  # 0x577d0617
        data.write(b'\x00\x10')  # size
        self.unknown_0x577d0617.to_stream(data)

        data.write(b'!j[z')  # 0x216a5b7a
        data.write(b'\x00\x10')  # size
        self.unknown_0x216a5b7a.to_stream(data)

        data.write(b'\x0c\xd1=\x8b')  # 0xcd13d8b
        data.write(b'\x00\x10')  # size
        self.unknown_0x0cd13d8b.to_stream(data)

        data.write(b'H\x8e\x08 ')  # 0x488e0820
        data.write(b'\x00\x10')  # size
        self.unknown_0x488e0820.to_stream(data)

        data.write(b'\xafW\xfa|')  # 0xaf57fa7c
        data.write(b'\x00\x10')  # size
        self.unknown_0xaf57fa7c.to_stream(data)

        data.write(b'\xacX|\xfa')  # 0xac587cfa
        data.write(b'\x00\x10')  # size
        self.unknown_0xac587cfa.to_stream(data)

        data.write(b'\x15#\x05#')  # 0x15230523
        data.write(b'\x00\x10')  # size
        self.unknown_0x15230523.to_stream(data)

        data.write(b'Tc v')  # 0x54632076
        data.write(b'\x00\x10')  # size
        self.unknown_0x54632076.to_stream(data)

        data.write(b'6Y\xe4[')  # 0x3659e45b
        data.write(b'\x00\x10')  # size
        self.unknown_0x3659e45b.to_stream(data)

        data.write(b'^ar#')  # 0x5e617223
        data.write(b'\x00\x10')  # size
        self.unknown_0x5e617223.to_stream(data)

        data.write(b'C\xcc\xa2U')  # 0x43cca255
        data.write(b'\x00\x10')  # size
        self.unknown_0x43cca255.to_stream(data)

        data.write(b'\x07\x93\x97\xfe')  # 0x79397fe
        data.write(b'\x00\x10')  # size
        self.unknown_0x079397fe.to_stream(data)

        data.write(b'\xe0Je\xa2')  # 0xe04a65a2
        data.write(b'\x00\x10')  # size
        self.unknown_0xe04a65a2.to_stream(data)

        data.write(b'pc\x8e\xaa')  # 0x70638eaa
        data.write(b'\x00\x10')  # size
        self.unknown_0x70638eaa.to_stream(data)

        data.write(b'[\x88\x802')  # 0x5b888032
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5b888032))

        data.write(b'\xb72-&')  # 0xb7322d26
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb7322d26))

        data.write(b'y\'_"')  # 0x79275f22
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x79275f22))

        data.write(b'\xf4\x05\xafU')  # 0xf405af55
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf405af55))

        data.write(b'?\x85\xeb(')  # 0x3f85eb28
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3f85eb28))

        data.write(b'\x19\xc5\xf8\x8b')  # 0x19c5f88b
        data.write(b'\x00\x10')  # size
        self.unknown_0x19c5f88b.to_stream(data)

        data.write(b"\xd8K'K")  # 0xd84b274b
        data.write(b'\x00\x10')  # size
        self.unknown_0xd84b274b.to_stream(data)

        data.write(b'A\xa9AJ')  # 0x41a9414a
        data.write(b'\x00\x10')  # size
        self.unknown_0x41a9414a.to_stream(data)

        data.write(b"\x80'\x9e\x8a")  # 0x80279e8a
        data.write(b'\x00\x10')  # size
        self.unknown_0x80279e8a.to_stream(data)

        data.write(b'\x98\xd8\xe1\xba')  # 0x98d8e1ba
        data.write(b'\x00\x10')  # size
        self.unknown_0x98d8e1ba.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakGui_MiscJson", data)
        return cls(
            unknown_0x2f9d48b8=json_data['unknown_0x2f9d48b8'],
            unknown_0x71b475d0=json_data['unknown_0x71b475d0'],
            unknown_0x744165c4=json_data['unknown_0x744165c4'],
            radar_world_radius=json_data['radar_world_radius'],
            unknown_0xa585c592=json_data['unknown_0xa585c592'],
            unknown_0x04f4a6fe=json_data['unknown_0x04f4a6fe'],
            unknown_0x3c327181=json_data['unknown_0x3c327181'],
            unknown_0xa581be26=json_data['unknown_0xa581be26'],
            unknown_0x68d88e25=json_data['unknown_0x68d88e25'],
            unknown_0x889ef9ea=json_data['unknown_0x889ef9ea'],
            unknown_0xb68ff81a=json_data['unknown_0xb68ff81a'],
            unknown_0x04510638=json_data['unknown_0x04510638'],
            unknown_0x7a48c3b1=json_data['unknown_0x7a48c3b1'],
            unknown_0x0d257063=json_data['unknown_0x0d257063'],
            unknown_0x2821bbca=json_data['unknown_0x2821bbca'],
            unknown_0x5fdcf3d9=json_data['unknown_0x5fdcf3d9'],
            unknown_0xc4dd4d5b=json_data['unknown_0xc4dd4d5b'],
            unknown_0x6031503e=json_data['unknown_0x6031503e'],
            unknown_0x9f5ebba2=json_data['unknown_0x9f5ebba2'],
            unknown_0x2930d57f=json_data['unknown_0x2930d57f'],
            unknown_0x3ac94cf1=json_data['unknown_0x3ac94cf1'],
            unknown_0x55b323e5=json_data['unknown_0x55b323e5'],
            unknown_0x411a705e=json_data['unknown_0x411a705e'],
            unknown_0x0a9d701d=json_data['unknown_0x0a9d701d'],
            unknown_0xf4a8e8ea=json_data['unknown_0xf4a8e8ea'],
            unknown_0x50812f49=Vector.from_json(json_data['unknown_0x50812f49']),
            unknown_0x7edc2474=Vector.from_json(json_data['unknown_0x7edc2474']),
            unknown_0x4f0d651c=json_data['unknown_0x4f0d651c'],
            unknown_0x85c31390=json_data['unknown_0x85c31390'],
            unknown_0xb93990e6=json_data['unknown_0xb93990e6'],
            unknown_0x4036cdb6=json_data['unknown_0x4036cdb6'],
            unknown_0xa7cf8baa=json_data['unknown_0xa7cf8baa'],
            unknown_0x3e8e6afd=json_data['unknown_0x3e8e6afd'],
            unknown_0xec040d56=json_data['unknown_0xec040d56'],
            unknown_0x236bbe14=json_data['unknown_0x236bbe14'],
            unknown_0x19f5c324=json_data['unknown_0x19f5c324'],
            unknown_0xfd559f8c=json_data['unknown_0xfd559f8c'],
            unknown_0xe4702e21=json_data['unknown_0xe4702e21'],
            unknown_0x705ed5cb=json_data['unknown_0x705ed5cb'],
            unknown_0x8922af69=json_data['unknown_0x8922af69'],
            unknown_0x9b970087=json_data['unknown_0x9b970087'],
            unknown_0x37dffbfd=json_data['unknown_0x37dffbfd'],
            unknown_0xb41c7a19=json_data['unknown_0xb41c7a19'],
            unknown_0xfd32e2d8=json_data['unknown_0xfd32e2d8'],
            unknown_0xba53888e=json_data['unknown_0xba53888e'],
            unknown_0xcc7ae923=json_data['unknown_0xcc7ae923'],
            unknown_0x8c723b8f=json_data['unknown_0x8c723b8f'],
            unknown_0x1f228e64=json_data['unknown_0x1f228e64'],
            unknown_0xe34fa22c=json_data['unknown_0xe34fa22c'],
            unknown_0xf4ec68ae=json_data['unknown_0xf4ec68ae'],
            unknown_0x4dd9d6d1=json_data['unknown_0x4dd9d6d1'],
            unknown_0xad4d37cd=json_data['unknown_0xad4d37cd'],
            unknown_0x95c78e5d=json_data['unknown_0x95c78e5d'],
            threat_world_radius=json_data['threat_world_radius'],
            unknown_0x78174d4b=json_data['unknown_0x78174d4b'],
            unknown_0x3cb2115b=json_data['unknown_0x3cb2115b'],
            unknown_0xfc30bb21=json_data['unknown_0xfc30bb21'],
            unknown_0x86cdde75=json_data['unknown_0x86cdde75'],
            unknown_0xf3565ff4=json_data['unknown_0xf3565ff4'],
            unknown_0x7d3c03eb=json_data['unknown_0x7d3c03eb'],
            unknown_0x72d4d899=json_data['unknown_0x72d4d899'],
            unknown_0xfb9a4cc7=json_data['unknown_0xfb9a4cc7'],
            unknown_0xa1417b38=json_data['unknown_0xa1417b38'],
            unknown_0x71b207b4=json_data['unknown_0x71b207b4'],
            unknown_0xa2580838=json_data['unknown_0xa2580838'],
            unknown_0x46d75fe1=json_data['unknown_0x46d75fe1'],
            unknown_0x4f7cf7d8=json_data['unknown_0x4f7cf7d8'],
            unknown_0x2bef7961=json_data['unknown_0x2bef7961'],
            unknown_0xdecc7bff=json_data['unknown_0xdecc7bff'],
            unknown_0xcbff7b94=json_data['unknown_0xcbff7b94'],
            unknown_0x0babf93b=json_data['unknown_0x0babf93b'],
            unknown_0xc0004f50=json_data['unknown_0xc0004f50'],
            unknown_0x4ee9c251=json_data['unknown_0x4ee9c251'],
            unknown_0xa71e83d5=json_data['unknown_0xa71e83d5'],
            unknown_0x3652ef32=json_data['unknown_0x3652ef32'],
            unknown_0x4ff930a5=json_data['unknown_0x4ff930a5'],
            unknown_0x1c106df3=json_data['unknown_0x1c106df3'],
            unknown_0xdaadf917=json_data['unknown_0xdaadf917'],
            unknown_0xe3d55457=json_data['unknown_0xe3d55457'],
            unknown_0xdd39f60a=json_data['unknown_0xdd39f60a'],
            unknown_0x3db45f6a=json_data['unknown_0x3db45f6a'],
            unknown_0x471f1217=json_data['unknown_0x471f1217'],
            unknown_0xf8b84c58=json_data['unknown_0xf8b84c58'],
            unknown_0xbc2c8de6=json_data['unknown_0xbc2c8de6'],
            unknown_0x54203510=json_data['unknown_0x54203510'],
            unknown_0xcf9fd47e=json_data['unknown_0xcf9fd47e'],
            unknown_0xcfb88ceb=json_data['unknown_0xcfb88ceb'],
            unknown_0x5e388dd0=json_data['unknown_0x5e388dd0'],
            unknown_0x86bc055e=json_data['unknown_0x86bc055e'],
            unknown_0x2c412371=json_data['unknown_0x2c412371'],
            unknown_0x3aaf2a8c=json_data['unknown_0x3aaf2a8c'],
            unknown_0xb515dd12=json_data['unknown_0xb515dd12'],
            unknown_0xa949b037=json_data['unknown_0xa949b037'],
            unknown_0xca9d401c=json_data['unknown_0xca9d401c'],
            unknown_0x8186e8fe=json_data['unknown_0x8186e8fe'],
            unknown_0x02a2198a=json_data['unknown_0x02a2198a'],
            unknown_0x8b64dc44=json_data['unknown_0x8b64dc44'],
            unknown_0x7161446b=json_data['unknown_0x7161446b'],
            unknown_0xaaff9224=json_data['unknown_0xaaff9224'],
            unknown_0xfa4a836c=json_data['unknown_0xfa4a836c'],
            unknown_0x23661b4f=json_data['unknown_0x23661b4f'],
            unknown_0x992b647a=json_data['unknown_0x992b647a'],
            unknown_0x929d08cf=json_data['unknown_0x929d08cf'],
            unknown_0xffeba1f2=json_data['unknown_0xffeba1f2'],
            unknown_0x13654f20=json_data['unknown_0x13654f20'],
            unknown_0x7083faf0=json_data['unknown_0x7083faf0'],
            unknown_0x2845923c=json_data['unknown_0x2845923c'],
            unknown_0xeb6a7f2a=json_data['unknown_0xeb6a7f2a'],
            unknown_0xd05eb27a=json_data['unknown_0xd05eb27a'],
            unknown_0xd067eaa3=json_data['unknown_0xd067eaa3'],
            unknown_0x8a5a4d81=json_data['unknown_0x8a5a4d81'],
            unknown_0xcb816d90=json_data['unknown_0xcb816d90'],
            unknown_0x5bf27d7a=json_data['unknown_0x5bf27d7a'],
            unknown_0x220d60e1=json_data['unknown_0x220d60e1'],
            unknown_0xb27e700b=json_data['unknown_0xb27e700b'],
            unknown_0x5590c6ec=json_data['unknown_0x5590c6ec'],
            unknown_0x8b66820d=json_data['unknown_0x8b66820d'],
            unknown_0x138f1104=json_data['unknown_0x138f1104'],
            unknown_0xd0d1760e=json_data['unknown_0xd0d1760e'],
            unknown_0xce9f5770=json_data['unknown_0xce9f5770'],
            unknown_0xeaf17d45=Spline.from_json(json_data['unknown_0xeaf17d45']),
            unknown_0xd81537b6=Spline.from_json(json_data['unknown_0xd81537b6']),
            unknown_0x3ba84552=Spline.from_json(json_data['unknown_0x3ba84552']),
            unknown_0xeeb7839b=json_data['unknown_0xeeb7839b'],
            unknown_0x24cf1719=json_data['unknown_0x24cf1719'],
            unknown_0xa4adf6ea=json_data['unknown_0xa4adf6ea'],
            unknown_0xe3755dda=json_data['unknown_0xe3755dda'],
            unknown_0xa607dfaa=json_data['unknown_0xa607dfaa'],
            unknown_0xf5f7a748=json_data['unknown_0xf5f7a748'],
            unknown_0x61215643=json_data['unknown_0x61215643'],
            unknown_0xa3f4095e=json_data['unknown_0xa3f4095e'],
            unknown_0x7103ca90=json_data['unknown_0x7103ca90'],
            unknown_0x22d4c6a3=json_data['unknown_0x22d4c6a3'],
            unknown_0xbe909e83=Color.from_json(json_data['unknown_0xbe909e83']),
            unknown_0x7407e76f=Color.from_json(json_data['unknown_0x7407e76f']),
            unknown_0x3547c23a=Color.from_json(json_data['unknown_0x3547c23a']),
            unknown_0x577d0617=Color.from_json(json_data['unknown_0x577d0617']),
            unknown_0x216a5b7a=Color.from_json(json_data['unknown_0x216a5b7a']),
            unknown_0x0cd13d8b=Color.from_json(json_data['unknown_0x0cd13d8b']),
            unknown_0x488e0820=Color.from_json(json_data['unknown_0x488e0820']),
            unknown_0xaf57fa7c=Color.from_json(json_data['unknown_0xaf57fa7c']),
            unknown_0xac587cfa=Color.from_json(json_data['unknown_0xac587cfa']),
            unknown_0x15230523=Color.from_json(json_data['unknown_0x15230523']),
            unknown_0x54632076=Color.from_json(json_data['unknown_0x54632076']),
            unknown_0x3659e45b=Color.from_json(json_data['unknown_0x3659e45b']),
            unknown_0x5e617223=Color.from_json(json_data['unknown_0x5e617223']),
            unknown_0x43cca255=Color.from_json(json_data['unknown_0x43cca255']),
            unknown_0x079397fe=Color.from_json(json_data['unknown_0x079397fe']),
            unknown_0xe04a65a2=Color.from_json(json_data['unknown_0xe04a65a2']),
            unknown_0x70638eaa=Color.from_json(json_data['unknown_0x70638eaa']),
            unknown_0x5b888032=json_data['unknown_0x5b888032'],
            unknown_0xb7322d26=json_data['unknown_0xb7322d26'],
            unknown_0x79275f22=json_data['unknown_0x79275f22'],
            unknown_0xf405af55=json_data['unknown_0xf405af55'],
            unknown_0x3f85eb28=json_data['unknown_0x3f85eb28'],
            unknown_0x19c5f88b=Color.from_json(json_data['unknown_0x19c5f88b']),
            unknown_0xd84b274b=Color.from_json(json_data['unknown_0xd84b274b']),
            unknown_0x41a9414a=Color.from_json(json_data['unknown_0x41a9414a']),
            unknown_0x80279e8a=Color.from_json(json_data['unknown_0x80279e8a']),
            unknown_0x98d8e1ba=Color.from_json(json_data['unknown_0x98d8e1ba']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x2f9d48b8': self.unknown_0x2f9d48b8,
            'unknown_0x71b475d0': self.unknown_0x71b475d0,
            'unknown_0x744165c4': self.unknown_0x744165c4,
            'radar_world_radius': self.radar_world_radius,
            'unknown_0xa585c592': self.unknown_0xa585c592,
            'unknown_0x04f4a6fe': self.unknown_0x04f4a6fe,
            'unknown_0x3c327181': self.unknown_0x3c327181,
            'unknown_0xa581be26': self.unknown_0xa581be26,
            'unknown_0x68d88e25': self.unknown_0x68d88e25,
            'unknown_0x889ef9ea': self.unknown_0x889ef9ea,
            'unknown_0xb68ff81a': self.unknown_0xb68ff81a,
            'unknown_0x04510638': self.unknown_0x04510638,
            'unknown_0x7a48c3b1': self.unknown_0x7a48c3b1,
            'unknown_0x0d257063': self.unknown_0x0d257063,
            'unknown_0x2821bbca': self.unknown_0x2821bbca,
            'unknown_0x5fdcf3d9': self.unknown_0x5fdcf3d9,
            'unknown_0xc4dd4d5b': self.unknown_0xc4dd4d5b,
            'unknown_0x6031503e': self.unknown_0x6031503e,
            'unknown_0x9f5ebba2': self.unknown_0x9f5ebba2,
            'unknown_0x2930d57f': self.unknown_0x2930d57f,
            'unknown_0x3ac94cf1': self.unknown_0x3ac94cf1,
            'unknown_0x55b323e5': self.unknown_0x55b323e5,
            'unknown_0x411a705e': self.unknown_0x411a705e,
            'unknown_0x0a9d701d': self.unknown_0x0a9d701d,
            'unknown_0xf4a8e8ea': self.unknown_0xf4a8e8ea,
            'unknown_0x50812f49': self.unknown_0x50812f49.to_json(),
            'unknown_0x7edc2474': self.unknown_0x7edc2474.to_json(),
            'unknown_0x4f0d651c': self.unknown_0x4f0d651c,
            'unknown_0x85c31390': self.unknown_0x85c31390,
            'unknown_0xb93990e6': self.unknown_0xb93990e6,
            'unknown_0x4036cdb6': self.unknown_0x4036cdb6,
            'unknown_0xa7cf8baa': self.unknown_0xa7cf8baa,
            'unknown_0x3e8e6afd': self.unknown_0x3e8e6afd,
            'unknown_0xec040d56': self.unknown_0xec040d56,
            'unknown_0x236bbe14': self.unknown_0x236bbe14,
            'unknown_0x19f5c324': self.unknown_0x19f5c324,
            'unknown_0xfd559f8c': self.unknown_0xfd559f8c,
            'unknown_0xe4702e21': self.unknown_0xe4702e21,
            'unknown_0x705ed5cb': self.unknown_0x705ed5cb,
            'unknown_0x8922af69': self.unknown_0x8922af69,
            'unknown_0x9b970087': self.unknown_0x9b970087,
            'unknown_0x37dffbfd': self.unknown_0x37dffbfd,
            'unknown_0xb41c7a19': self.unknown_0xb41c7a19,
            'unknown_0xfd32e2d8': self.unknown_0xfd32e2d8,
            'unknown_0xba53888e': self.unknown_0xba53888e,
            'unknown_0xcc7ae923': self.unknown_0xcc7ae923,
            'unknown_0x8c723b8f': self.unknown_0x8c723b8f,
            'unknown_0x1f228e64': self.unknown_0x1f228e64,
            'unknown_0xe34fa22c': self.unknown_0xe34fa22c,
            'unknown_0xf4ec68ae': self.unknown_0xf4ec68ae,
            'unknown_0x4dd9d6d1': self.unknown_0x4dd9d6d1,
            'unknown_0xad4d37cd': self.unknown_0xad4d37cd,
            'unknown_0x95c78e5d': self.unknown_0x95c78e5d,
            'threat_world_radius': self.threat_world_radius,
            'unknown_0x78174d4b': self.unknown_0x78174d4b,
            'unknown_0x3cb2115b': self.unknown_0x3cb2115b,
            'unknown_0xfc30bb21': self.unknown_0xfc30bb21,
            'unknown_0x86cdde75': self.unknown_0x86cdde75,
            'unknown_0xf3565ff4': self.unknown_0xf3565ff4,
            'unknown_0x7d3c03eb': self.unknown_0x7d3c03eb,
            'unknown_0x72d4d899': self.unknown_0x72d4d899,
            'unknown_0xfb9a4cc7': self.unknown_0xfb9a4cc7,
            'unknown_0xa1417b38': self.unknown_0xa1417b38,
            'unknown_0x71b207b4': self.unknown_0x71b207b4,
            'unknown_0xa2580838': self.unknown_0xa2580838,
            'unknown_0x46d75fe1': self.unknown_0x46d75fe1,
            'unknown_0x4f7cf7d8': self.unknown_0x4f7cf7d8,
            'unknown_0x2bef7961': self.unknown_0x2bef7961,
            'unknown_0xdecc7bff': self.unknown_0xdecc7bff,
            'unknown_0xcbff7b94': self.unknown_0xcbff7b94,
            'unknown_0x0babf93b': self.unknown_0x0babf93b,
            'unknown_0xc0004f50': self.unknown_0xc0004f50,
            'unknown_0x4ee9c251': self.unknown_0x4ee9c251,
            'unknown_0xa71e83d5': self.unknown_0xa71e83d5,
            'unknown_0x3652ef32': self.unknown_0x3652ef32,
            'unknown_0x4ff930a5': self.unknown_0x4ff930a5,
            'unknown_0x1c106df3': self.unknown_0x1c106df3,
            'unknown_0xdaadf917': self.unknown_0xdaadf917,
            'unknown_0xe3d55457': self.unknown_0xe3d55457,
            'unknown_0xdd39f60a': self.unknown_0xdd39f60a,
            'unknown_0x3db45f6a': self.unknown_0x3db45f6a,
            'unknown_0x471f1217': self.unknown_0x471f1217,
            'unknown_0xf8b84c58': self.unknown_0xf8b84c58,
            'unknown_0xbc2c8de6': self.unknown_0xbc2c8de6,
            'unknown_0x54203510': self.unknown_0x54203510,
            'unknown_0xcf9fd47e': self.unknown_0xcf9fd47e,
            'unknown_0xcfb88ceb': self.unknown_0xcfb88ceb,
            'unknown_0x5e388dd0': self.unknown_0x5e388dd0,
            'unknown_0x86bc055e': self.unknown_0x86bc055e,
            'unknown_0x2c412371': self.unknown_0x2c412371,
            'unknown_0x3aaf2a8c': self.unknown_0x3aaf2a8c,
            'unknown_0xb515dd12': self.unknown_0xb515dd12,
            'unknown_0xa949b037': self.unknown_0xa949b037,
            'unknown_0xca9d401c': self.unknown_0xca9d401c,
            'unknown_0x8186e8fe': self.unknown_0x8186e8fe,
            'unknown_0x02a2198a': self.unknown_0x02a2198a,
            'unknown_0x8b64dc44': self.unknown_0x8b64dc44,
            'unknown_0x7161446b': self.unknown_0x7161446b,
            'unknown_0xaaff9224': self.unknown_0xaaff9224,
            'unknown_0xfa4a836c': self.unknown_0xfa4a836c,
            'unknown_0x23661b4f': self.unknown_0x23661b4f,
            'unknown_0x992b647a': self.unknown_0x992b647a,
            'unknown_0x929d08cf': self.unknown_0x929d08cf,
            'unknown_0xffeba1f2': self.unknown_0xffeba1f2,
            'unknown_0x13654f20': self.unknown_0x13654f20,
            'unknown_0x7083faf0': self.unknown_0x7083faf0,
            'unknown_0x2845923c': self.unknown_0x2845923c,
            'unknown_0xeb6a7f2a': self.unknown_0xeb6a7f2a,
            'unknown_0xd05eb27a': self.unknown_0xd05eb27a,
            'unknown_0xd067eaa3': self.unknown_0xd067eaa3,
            'unknown_0x8a5a4d81': self.unknown_0x8a5a4d81,
            'unknown_0xcb816d90': self.unknown_0xcb816d90,
            'unknown_0x5bf27d7a': self.unknown_0x5bf27d7a,
            'unknown_0x220d60e1': self.unknown_0x220d60e1,
            'unknown_0xb27e700b': self.unknown_0xb27e700b,
            'unknown_0x5590c6ec': self.unknown_0x5590c6ec,
            'unknown_0x8b66820d': self.unknown_0x8b66820d,
            'unknown_0x138f1104': self.unknown_0x138f1104,
            'unknown_0xd0d1760e': self.unknown_0xd0d1760e,
            'unknown_0xce9f5770': self.unknown_0xce9f5770,
            'unknown_0xeaf17d45': self.unknown_0xeaf17d45.to_json(),
            'unknown_0xd81537b6': self.unknown_0xd81537b6.to_json(),
            'unknown_0x3ba84552': self.unknown_0x3ba84552.to_json(),
            'unknown_0xeeb7839b': self.unknown_0xeeb7839b,
            'unknown_0x24cf1719': self.unknown_0x24cf1719,
            'unknown_0xa4adf6ea': self.unknown_0xa4adf6ea,
            'unknown_0xe3755dda': self.unknown_0xe3755dda,
            'unknown_0xa607dfaa': self.unknown_0xa607dfaa,
            'unknown_0xf5f7a748': self.unknown_0xf5f7a748,
            'unknown_0x61215643': self.unknown_0x61215643,
            'unknown_0xa3f4095e': self.unknown_0xa3f4095e,
            'unknown_0x7103ca90': self.unknown_0x7103ca90,
            'unknown_0x22d4c6a3': self.unknown_0x22d4c6a3,
            'unknown_0xbe909e83': self.unknown_0xbe909e83.to_json(),
            'unknown_0x7407e76f': self.unknown_0x7407e76f.to_json(),
            'unknown_0x3547c23a': self.unknown_0x3547c23a.to_json(),
            'unknown_0x577d0617': self.unknown_0x577d0617.to_json(),
            'unknown_0x216a5b7a': self.unknown_0x216a5b7a.to_json(),
            'unknown_0x0cd13d8b': self.unknown_0x0cd13d8b.to_json(),
            'unknown_0x488e0820': self.unknown_0x488e0820.to_json(),
            'unknown_0xaf57fa7c': self.unknown_0xaf57fa7c.to_json(),
            'unknown_0xac587cfa': self.unknown_0xac587cfa.to_json(),
            'unknown_0x15230523': self.unknown_0x15230523.to_json(),
            'unknown_0x54632076': self.unknown_0x54632076.to_json(),
            'unknown_0x3659e45b': self.unknown_0x3659e45b.to_json(),
            'unknown_0x5e617223': self.unknown_0x5e617223.to_json(),
            'unknown_0x43cca255': self.unknown_0x43cca255.to_json(),
            'unknown_0x079397fe': self.unknown_0x079397fe.to_json(),
            'unknown_0xe04a65a2': self.unknown_0xe04a65a2.to_json(),
            'unknown_0x70638eaa': self.unknown_0x70638eaa.to_json(),
            'unknown_0x5b888032': self.unknown_0x5b888032,
            'unknown_0xb7322d26': self.unknown_0xb7322d26,
            'unknown_0x79275f22': self.unknown_0x79275f22,
            'unknown_0xf405af55': self.unknown_0xf405af55,
            'unknown_0x3f85eb28': self.unknown_0x3f85eb28,
            'unknown_0x19c5f88b': self.unknown_0x19c5f88b.to_json(),
            'unknown_0xd84b274b': self.unknown_0xd84b274b.to_json(),
            'unknown_0x41a9414a': self.unknown_0x41a9414a.to_json(),
            'unknown_0x80279e8a': self.unknown_0x80279e8a.to_json(),
            'unknown_0x98d8e1ba': self.unknown_0x98d8e1ba.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_unknown_0x2f9d48b8(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x71b475d0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x744165c4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_radar_world_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa585c592(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x04f4a6fe(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3c327181(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa581be26(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x68d88e25(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x889ef9ea(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb68ff81a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x04510638(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7a48c3b1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0d257063(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2821bbca(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x5fdcf3d9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc4dd4d5b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6031503e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9f5ebba2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2930d57f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3ac94cf1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x55b323e5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x411a705e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0a9d701d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf4a8e8ea(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x50812f49(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_unknown_0x7edc2474(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_unknown_0x4f0d651c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x85c31390(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb93990e6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4036cdb6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa7cf8baa(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3e8e6afd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xec040d56(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x236bbe14(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x19f5c324(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfd559f8c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe4702e21(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x705ed5cb(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x8922af69(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x9b970087(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x37dffbfd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb41c7a19(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfd32e2d8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xba53888e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcc7ae923(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8c723b8f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1f228e64(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe34fa22c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf4ec68ae(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x4dd9d6d1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xad4d37cd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x95c78e5d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_threat_world_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x78174d4b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3cb2115b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfc30bb21(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x86cdde75(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf3565ff4(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x7d3c03eb(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x72d4d899(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xfb9a4cc7(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xa1417b38(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x71b207b4(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xa2580838(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x46d75fe1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4f7cf7d8(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2bef7961(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdecc7bff(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcbff7b94(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0babf93b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc0004f50(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4ee9c251(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xa71e83d5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3652ef32(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4ff930a5(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x1c106df3(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xdaadf917(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xe3d55457(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xdd39f60a(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x3db45f6a(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0x471f1217(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0xf8b84c58(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0xbc2c8de6(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0x54203510(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0xcf9fd47e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcfb88ceb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5e388dd0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x86bc055e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2c412371(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3aaf2a8c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb515dd12(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa949b037(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xca9d401c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8186e8fe(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x02a2198a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8b64dc44(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x7161446b(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xaaff9224(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfa4a836c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x23661b4f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x992b647a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x929d08cf(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xffeba1f2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x13654f20(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7083faf0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2845923c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xeb6a7f2a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd05eb27a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd067eaa3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8a5a4d81(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcb816d90(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5bf27d7a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x220d60e1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb27e700b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5590c6ec(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8b66820d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x138f1104(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd0d1760e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xce9f5770(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xeeb7839b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x24cf1719(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa4adf6ea(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe3755dda(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa607dfaa(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf5f7a748(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x61215643(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa3f4095e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7103ca90(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x22d4c6a3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbe909e83(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x7407e76f(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x3547c23a(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x577d0617(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x216a5b7a(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x0cd13d8b(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x488e0820(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xaf57fa7c(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xac587cfa(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x15230523(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x54632076(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x3659e45b(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x5e617223(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x43cca255(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x079397fe(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xe04a65a2(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x70638eaa(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x5b888032(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb7322d26(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x79275f22(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf405af55(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3f85eb28(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x19c5f88b(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xd84b274b(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x41a9414a(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x80279e8a(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x98d8e1ba(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x2f9d48b8: ('unknown_0x2f9d48b8', _decode_unknown_0x2f9d48b8),
    0x71b475d0: ('unknown_0x71b475d0', _decode_unknown_0x71b475d0),
    0x744165c4: ('unknown_0x744165c4', _decode_unknown_0x744165c4),
    0xee1ba439: ('radar_world_radius', _decode_radar_world_radius),
    0xa585c592: ('unknown_0xa585c592', _decode_unknown_0xa585c592),
    0x4f4a6fe: ('unknown_0x04f4a6fe', _decode_unknown_0x04f4a6fe),
    0x3c327181: ('unknown_0x3c327181', _decode_unknown_0x3c327181),
    0xa581be26: ('unknown_0xa581be26', _decode_unknown_0xa581be26),
    0x68d88e25: ('unknown_0x68d88e25', _decode_unknown_0x68d88e25),
    0x889ef9ea: ('unknown_0x889ef9ea', _decode_unknown_0x889ef9ea),
    0xb68ff81a: ('unknown_0xb68ff81a', _decode_unknown_0xb68ff81a),
    0x4510638: ('unknown_0x04510638', _decode_unknown_0x04510638),
    0x7a48c3b1: ('unknown_0x7a48c3b1', _decode_unknown_0x7a48c3b1),
    0xd257063: ('unknown_0x0d257063', _decode_unknown_0x0d257063),
    0x2821bbca: ('unknown_0x2821bbca', _decode_unknown_0x2821bbca),
    0x5fdcf3d9: ('unknown_0x5fdcf3d9', _decode_unknown_0x5fdcf3d9),
    0xc4dd4d5b: ('unknown_0xc4dd4d5b', _decode_unknown_0xc4dd4d5b),
    0x6031503e: ('unknown_0x6031503e', _decode_unknown_0x6031503e),
    0x9f5ebba2: ('unknown_0x9f5ebba2', _decode_unknown_0x9f5ebba2),
    0x2930d57f: ('unknown_0x2930d57f', _decode_unknown_0x2930d57f),
    0x3ac94cf1: ('unknown_0x3ac94cf1', _decode_unknown_0x3ac94cf1),
    0x55b323e5: ('unknown_0x55b323e5', _decode_unknown_0x55b323e5),
    0x411a705e: ('unknown_0x411a705e', _decode_unknown_0x411a705e),
    0xa9d701d: ('unknown_0x0a9d701d', _decode_unknown_0x0a9d701d),
    0xf4a8e8ea: ('unknown_0xf4a8e8ea', _decode_unknown_0xf4a8e8ea),
    0x50812f49: ('unknown_0x50812f49', _decode_unknown_0x50812f49),
    0x7edc2474: ('unknown_0x7edc2474', _decode_unknown_0x7edc2474),
    0x4f0d651c: ('unknown_0x4f0d651c', _decode_unknown_0x4f0d651c),
    0x85c31390: ('unknown_0x85c31390', _decode_unknown_0x85c31390),
    0xb93990e6: ('unknown_0xb93990e6', _decode_unknown_0xb93990e6),
    0x4036cdb6: ('unknown_0x4036cdb6', _decode_unknown_0x4036cdb6),
    0xa7cf8baa: ('unknown_0xa7cf8baa', _decode_unknown_0xa7cf8baa),
    0x3e8e6afd: ('unknown_0x3e8e6afd', _decode_unknown_0x3e8e6afd),
    0xec040d56: ('unknown_0xec040d56', _decode_unknown_0xec040d56),
    0x236bbe14: ('unknown_0x236bbe14', _decode_unknown_0x236bbe14),
    0x19f5c324: ('unknown_0x19f5c324', _decode_unknown_0x19f5c324),
    0xfd559f8c: ('unknown_0xfd559f8c', _decode_unknown_0xfd559f8c),
    0xe4702e21: ('unknown_0xe4702e21', _decode_unknown_0xe4702e21),
    0x705ed5cb: ('unknown_0x705ed5cb', _decode_unknown_0x705ed5cb),
    0x8922af69: ('unknown_0x8922af69', _decode_unknown_0x8922af69),
    0x9b970087: ('unknown_0x9b970087', _decode_unknown_0x9b970087),
    0x37dffbfd: ('unknown_0x37dffbfd', _decode_unknown_0x37dffbfd),
    0xb41c7a19: ('unknown_0xb41c7a19', _decode_unknown_0xb41c7a19),
    0xfd32e2d8: ('unknown_0xfd32e2d8', _decode_unknown_0xfd32e2d8),
    0xba53888e: ('unknown_0xba53888e', _decode_unknown_0xba53888e),
    0xcc7ae923: ('unknown_0xcc7ae923', _decode_unknown_0xcc7ae923),
    0x8c723b8f: ('unknown_0x8c723b8f', _decode_unknown_0x8c723b8f),
    0x1f228e64: ('unknown_0x1f228e64', _decode_unknown_0x1f228e64),
    0xe34fa22c: ('unknown_0xe34fa22c', _decode_unknown_0xe34fa22c),
    0xf4ec68ae: ('unknown_0xf4ec68ae', _decode_unknown_0xf4ec68ae),
    0x4dd9d6d1: ('unknown_0x4dd9d6d1', _decode_unknown_0x4dd9d6d1),
    0xad4d37cd: ('unknown_0xad4d37cd', _decode_unknown_0xad4d37cd),
    0x95c78e5d: ('unknown_0x95c78e5d', _decode_unknown_0x95c78e5d),
    0x1a8dc454: ('threat_world_radius', _decode_threat_world_radius),
    0x78174d4b: ('unknown_0x78174d4b', _decode_unknown_0x78174d4b),
    0x3cb2115b: ('unknown_0x3cb2115b', _decode_unknown_0x3cb2115b),
    0xfc30bb21: ('unknown_0xfc30bb21', _decode_unknown_0xfc30bb21),
    0x86cdde75: ('unknown_0x86cdde75', _decode_unknown_0x86cdde75),
    0xf3565ff4: ('unknown_0xf3565ff4', _decode_unknown_0xf3565ff4),
    0x7d3c03eb: ('unknown_0x7d3c03eb', _decode_unknown_0x7d3c03eb),
    0x72d4d899: ('unknown_0x72d4d899', _decode_unknown_0x72d4d899),
    0xfb9a4cc7: ('unknown_0xfb9a4cc7', _decode_unknown_0xfb9a4cc7),
    0xa1417b38: ('unknown_0xa1417b38', _decode_unknown_0xa1417b38),
    0x71b207b4: ('unknown_0x71b207b4', _decode_unknown_0x71b207b4),
    0xa2580838: ('unknown_0xa2580838', _decode_unknown_0xa2580838),
    0x46d75fe1: ('unknown_0x46d75fe1', _decode_unknown_0x46d75fe1),
    0x4f7cf7d8: ('unknown_0x4f7cf7d8', _decode_unknown_0x4f7cf7d8),
    0x2bef7961: ('unknown_0x2bef7961', _decode_unknown_0x2bef7961),
    0xdecc7bff: ('unknown_0xdecc7bff', _decode_unknown_0xdecc7bff),
    0xcbff7b94: ('unknown_0xcbff7b94', _decode_unknown_0xcbff7b94),
    0xbabf93b: ('unknown_0x0babf93b', _decode_unknown_0x0babf93b),
    0xc0004f50: ('unknown_0xc0004f50', _decode_unknown_0xc0004f50),
    0x4ee9c251: ('unknown_0x4ee9c251', _decode_unknown_0x4ee9c251),
    0xa71e83d5: ('unknown_0xa71e83d5', _decode_unknown_0xa71e83d5),
    0x3652ef32: ('unknown_0x3652ef32', _decode_unknown_0x3652ef32),
    0x4ff930a5: ('unknown_0x4ff930a5', _decode_unknown_0x4ff930a5),
    0x1c106df3: ('unknown_0x1c106df3', _decode_unknown_0x1c106df3),
    0xdaadf917: ('unknown_0xdaadf917', _decode_unknown_0xdaadf917),
    0xe3d55457: ('unknown_0xe3d55457', _decode_unknown_0xe3d55457),
    0xdd39f60a: ('unknown_0xdd39f60a', _decode_unknown_0xdd39f60a),
    0x3db45f6a: ('unknown_0x3db45f6a', _decode_unknown_0x3db45f6a),
    0x471f1217: ('unknown_0x471f1217', _decode_unknown_0x471f1217),
    0xf8b84c58: ('unknown_0xf8b84c58', _decode_unknown_0xf8b84c58),
    0xbc2c8de6: ('unknown_0xbc2c8de6', _decode_unknown_0xbc2c8de6),
    0x54203510: ('unknown_0x54203510', _decode_unknown_0x54203510),
    0xcf9fd47e: ('unknown_0xcf9fd47e', _decode_unknown_0xcf9fd47e),
    0xcfb88ceb: ('unknown_0xcfb88ceb', _decode_unknown_0xcfb88ceb),
    0x5e388dd0: ('unknown_0x5e388dd0', _decode_unknown_0x5e388dd0),
    0x86bc055e: ('unknown_0x86bc055e', _decode_unknown_0x86bc055e),
    0x2c412371: ('unknown_0x2c412371', _decode_unknown_0x2c412371),
    0x3aaf2a8c: ('unknown_0x3aaf2a8c', _decode_unknown_0x3aaf2a8c),
    0xb515dd12: ('unknown_0xb515dd12', _decode_unknown_0xb515dd12),
    0xa949b037: ('unknown_0xa949b037', _decode_unknown_0xa949b037),
    0xca9d401c: ('unknown_0xca9d401c', _decode_unknown_0xca9d401c),
    0x8186e8fe: ('unknown_0x8186e8fe', _decode_unknown_0x8186e8fe),
    0x2a2198a: ('unknown_0x02a2198a', _decode_unknown_0x02a2198a),
    0x8b64dc44: ('unknown_0x8b64dc44', _decode_unknown_0x8b64dc44),
    0x7161446b: ('unknown_0x7161446b', _decode_unknown_0x7161446b),
    0xaaff9224: ('unknown_0xaaff9224', _decode_unknown_0xaaff9224),
    0xfa4a836c: ('unknown_0xfa4a836c', _decode_unknown_0xfa4a836c),
    0x23661b4f: ('unknown_0x23661b4f', _decode_unknown_0x23661b4f),
    0x992b647a: ('unknown_0x992b647a', _decode_unknown_0x992b647a),
    0x929d08cf: ('unknown_0x929d08cf', _decode_unknown_0x929d08cf),
    0xffeba1f2: ('unknown_0xffeba1f2', _decode_unknown_0xffeba1f2),
    0x13654f20: ('unknown_0x13654f20', _decode_unknown_0x13654f20),
    0x7083faf0: ('unknown_0x7083faf0', _decode_unknown_0x7083faf0),
    0x2845923c: ('unknown_0x2845923c', _decode_unknown_0x2845923c),
    0xeb6a7f2a: ('unknown_0xeb6a7f2a', _decode_unknown_0xeb6a7f2a),
    0xd05eb27a: ('unknown_0xd05eb27a', _decode_unknown_0xd05eb27a),
    0xd067eaa3: ('unknown_0xd067eaa3', _decode_unknown_0xd067eaa3),
    0x8a5a4d81: ('unknown_0x8a5a4d81', _decode_unknown_0x8a5a4d81),
    0xcb816d90: ('unknown_0xcb816d90', _decode_unknown_0xcb816d90),
    0x5bf27d7a: ('unknown_0x5bf27d7a', _decode_unknown_0x5bf27d7a),
    0x220d60e1: ('unknown_0x220d60e1', _decode_unknown_0x220d60e1),
    0xb27e700b: ('unknown_0xb27e700b', _decode_unknown_0xb27e700b),
    0x5590c6ec: ('unknown_0x5590c6ec', _decode_unknown_0x5590c6ec),
    0x8b66820d: ('unknown_0x8b66820d', _decode_unknown_0x8b66820d),
    0x138f1104: ('unknown_0x138f1104', _decode_unknown_0x138f1104),
    0xd0d1760e: ('unknown_0xd0d1760e', _decode_unknown_0xd0d1760e),
    0xce9f5770: ('unknown_0xce9f5770', _decode_unknown_0xce9f5770),
    0xeaf17d45: ('unknown_0xeaf17d45', Spline.from_stream),
    0xd81537b6: ('unknown_0xd81537b6', Spline.from_stream),
    0x3ba84552: ('unknown_0x3ba84552', Spline.from_stream),
    0xeeb7839b: ('unknown_0xeeb7839b', _decode_unknown_0xeeb7839b),
    0x24cf1719: ('unknown_0x24cf1719', _decode_unknown_0x24cf1719),
    0xa4adf6ea: ('unknown_0xa4adf6ea', _decode_unknown_0xa4adf6ea),
    0xe3755dda: ('unknown_0xe3755dda', _decode_unknown_0xe3755dda),
    0xa607dfaa: ('unknown_0xa607dfaa', _decode_unknown_0xa607dfaa),
    0xf5f7a748: ('unknown_0xf5f7a748', _decode_unknown_0xf5f7a748),
    0x61215643: ('unknown_0x61215643', _decode_unknown_0x61215643),
    0xa3f4095e: ('unknown_0xa3f4095e', _decode_unknown_0xa3f4095e),
    0x7103ca90: ('unknown_0x7103ca90', _decode_unknown_0x7103ca90),
    0x22d4c6a3: ('unknown_0x22d4c6a3', _decode_unknown_0x22d4c6a3),
    0xbe909e83: ('unknown_0xbe909e83', _decode_unknown_0xbe909e83),
    0x7407e76f: ('unknown_0x7407e76f', _decode_unknown_0x7407e76f),
    0x3547c23a: ('unknown_0x3547c23a', _decode_unknown_0x3547c23a),
    0x577d0617: ('unknown_0x577d0617', _decode_unknown_0x577d0617),
    0x216a5b7a: ('unknown_0x216a5b7a', _decode_unknown_0x216a5b7a),
    0xcd13d8b: ('unknown_0x0cd13d8b', _decode_unknown_0x0cd13d8b),
    0x488e0820: ('unknown_0x488e0820', _decode_unknown_0x488e0820),
    0xaf57fa7c: ('unknown_0xaf57fa7c', _decode_unknown_0xaf57fa7c),
    0xac587cfa: ('unknown_0xac587cfa', _decode_unknown_0xac587cfa),
    0x15230523: ('unknown_0x15230523', _decode_unknown_0x15230523),
    0x54632076: ('unknown_0x54632076', _decode_unknown_0x54632076),
    0x3659e45b: ('unknown_0x3659e45b', _decode_unknown_0x3659e45b),
    0x5e617223: ('unknown_0x5e617223', _decode_unknown_0x5e617223),
    0x43cca255: ('unknown_0x43cca255', _decode_unknown_0x43cca255),
    0x79397fe: ('unknown_0x079397fe', _decode_unknown_0x079397fe),
    0xe04a65a2: ('unknown_0xe04a65a2', _decode_unknown_0xe04a65a2),
    0x70638eaa: ('unknown_0x70638eaa', _decode_unknown_0x70638eaa),
    0x5b888032: ('unknown_0x5b888032', _decode_unknown_0x5b888032),
    0xb7322d26: ('unknown_0xb7322d26', _decode_unknown_0xb7322d26),
    0x79275f22: ('unknown_0x79275f22', _decode_unknown_0x79275f22),
    0xf405af55: ('unknown_0xf405af55', _decode_unknown_0xf405af55),
    0x3f85eb28: ('unknown_0x3f85eb28', _decode_unknown_0x3f85eb28),
    0x19c5f88b: ('unknown_0x19c5f88b', _decode_unknown_0x19c5f88b),
    0xd84b274b: ('unknown_0xd84b274b', _decode_unknown_0xd84b274b),
    0x41a9414a: ('unknown_0x41a9414a', _decode_unknown_0x41a9414a),
    0x80279e8a: ('unknown_0x80279e8a', _decode_unknown_0x80279e8a),
    0x98d8e1ba: ('unknown_0x98d8e1ba', _decode_unknown_0x98d8e1ba),
}
