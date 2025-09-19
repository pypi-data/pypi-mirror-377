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
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.archetypes.EchoParameters import EchoParameters
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.SafeZoneStructA import SafeZoneStructA
from retro_data_structures.properties.echoes.archetypes.SafeZoneStructB import SafeZoneStructB
from retro_data_structures.properties.echoes.archetypes.TriggerInfo import TriggerInfo
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class SafeZoneJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        trigger: json_util.JsonObject
        deactivate_on_enter: bool
        deactivate_on_exit: bool
        activation_time: float
        deactivation_time: float
        lifetime: float
        random_lifetime_offset: float
        impact_effect: int
        filter_sound_effects: bool
        unknown_0x414379ea: int
        ignore_cinematic_camera: bool
        normal_safe_zone_struct: json_util.JsonObject
        energized_safe_zone_struct: json_util.JsonObject
        supercharged_safe_zone_struct: json_util.JsonObject
        normal_damage: json_util.JsonObject
        damage_info: json_util.JsonObject
        inside_fade_start: float
        inside_fade_time: float
        unknown_0x6c14904c: float
        flash_time: float
        flash_brightness: float
        flash_sound: int
        safezone_shape: int
        mobile: bool
        generate_mobile_light: bool
        mobile_light_offset: json_util.JsonValue
        unknown_0xe71b43e1: json_util.JsonValue
        unknown_0x9f638987: float
        safe_zone_struct_a_0x8a09f99a: json_util.JsonObject
        safe_zone_struct_a_0xafb855b8: json_util.JsonObject
        echo_parameters: json_util.JsonObject
    

@dataclasses.dataclass()
class SafeZone(BaseObjectType):
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
    deactivate_on_enter: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x8d33465f, original_name='DeactivateOnEnter'
        ),
    })
    deactivate_on_exit: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x1c453986, original_name='DeactivateOnExit'
        ),
    })
    activation_time: float = dataclasses.field(default=0.15000000596046448, metadata={
        'reflection': FieldReflection[float](
            float, id=0xead3e22e, original_name='ActivationTime'
        ),
    })
    deactivation_time: float = dataclasses.field(default=0.15000000596046448, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb5cdf196, original_name='DeactivationTime'
        ),
    })
    lifetime: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x32dc67f6, original_name='Lifetime'
        ),
    })
    random_lifetime_offset: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xde169db0, original_name='RandomLifetimeOffset'
        ),
    })
    impact_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9be4bbd8, original_name='ImpactEffect'
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
    ignore_cinematic_camera: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x62bac460, original_name='IgnoreCinematicCamera'
        ),
    })
    normal_safe_zone_struct: SafeZoneStructB = dataclasses.field(default_factory=SafeZoneStructB, metadata={
        'reflection': FieldReflection[SafeZoneStructB](
            SafeZoneStructB, id=0xb4a293c7, original_name='Normal Safe Zone Struct', from_json=SafeZoneStructB.from_json, to_json=SafeZoneStructB.to_json
        ),
    })
    energized_safe_zone_struct: SafeZoneStructB = dataclasses.field(default_factory=SafeZoneStructB, metadata={
        'reflection': FieldReflection[SafeZoneStructB](
            SafeZoneStructB, id=0xdae8c14e, original_name='Energized Safe Zone Struct', from_json=SafeZoneStructB.from_json, to_json=SafeZoneStructB.to_json
        ),
    })
    supercharged_safe_zone_struct: SafeZoneStructB = dataclasses.field(default_factory=SafeZoneStructB, metadata={
        'reflection': FieldReflection[SafeZoneStructB](
            SafeZoneStructB, id=0x6471d643, original_name='Supercharged Safe Zone Struct', from_json=SafeZoneStructB.from_json, to_json=SafeZoneStructB.to_json
        ),
    })
    normal_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xeee2b188, original_name='NormalDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_info: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x78a13ca0, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    inside_fade_start: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x08ccffd0, original_name='InsideFadeStart'
        ),
    })
    inside_fade_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7febbfe7, original_name='InsideFadeTime'
        ),
    })
    unknown_0x6c14904c: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6c14904c, original_name='Unknown'
        ),
    })
    flash_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x48b4b865, original_name='FlashTime'
        ),
    })
    flash_brightness: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x452f7876, original_name='FlashBrightness'
        ),
    })
    flash_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x4faac896, original_name='FlashSound'
        ),
    })
    safezone_shape: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xd5869b0b, original_name='SafezoneShape'
        ),
    })
    mobile: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x222a258e, original_name='Mobile'
        ),
    })
    generate_mobile_light: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x6c90e396, original_name='GenerateMobileLight'
        ),
    })
    mobile_light_offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0xa7963e03, original_name='MobileLightOffset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_0xe71b43e1: Color = dataclasses.field(default_factory=lambda: Color(r=0.7372549772262573, g=1.0, b=1.0, a=0.24705900251865387), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xe71b43e1, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x9f638987: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9f638987, original_name='Unknown'
        ),
    })
    safe_zone_struct_a_0x8a09f99a: SafeZoneStructA = dataclasses.field(default_factory=SafeZoneStructA, metadata={
        'reflection': FieldReflection[SafeZoneStructA](
            SafeZoneStructA, id=0x8a09f99a, original_name='SafeZoneStructA', from_json=SafeZoneStructA.from_json, to_json=SafeZoneStructA.to_json
        ),
    })
    safe_zone_struct_a_0xafb855b8: SafeZoneStructA = dataclasses.field(default_factory=SafeZoneStructA, metadata={
        'reflection': FieldReflection[SafeZoneStructA](
            SafeZoneStructA, id=0xafb855b8, original_name='SafeZoneStructA', from_json=SafeZoneStructA.from_json, to_json=SafeZoneStructA.to_json
        ),
    })
    echo_parameters: EchoParameters = dataclasses.field(default_factory=EchoParameters, metadata={
        'reflection': FieldReflection[EchoParameters](
            EchoParameters, id=0x4476bed8, original_name='EchoParameters', from_json=EchoParameters.from_json, to_json=EchoParameters.to_json
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
        return 'SAFE'

    @classmethod
    def modules(cls) -> list[str]:
        return ['ScriptSafeZone.rel']

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
        if property_count != 32:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x77a27411
        trigger = TriggerInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8d33465f
        deactivate_on_enter = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1c453986
        deactivate_on_exit = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xead3e22e
        activation_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb5cdf196
        deactivation_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x32dc67f6
        lifetime = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xde169db0
        random_lifetime_offset = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9be4bbd8
        impact_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x822118b4
        filter_sound_effects = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x414379ea
        unknown_0x414379ea = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x62bac460
        ignore_cinematic_camera = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb4a293c7
        normal_safe_zone_struct = SafeZoneStructB.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdae8c14e
        energized_safe_zone_struct = SafeZoneStructB.from_stream(data, property_size, default_override={'shell1_animated_horiz_rate': 0.03999999910593033, 'shell1_animated_vert_rate': 0.0, 'shell1_scale_horiz': 4.0, 'shell1_scale_vert': 2.0, 'shell2_scale_horiz': 10.0, 'shell2_scale_vert': 12.0, 'shell_color': Color(r=1.0, g=0.7372549772262573, b=0.3921569883823395, a=0.0)})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6471d643
        supercharged_safe_zone_struct = SafeZoneStructB.from_stream(data, property_size, default_override={'shell1_animated_horiz_rate': 0.03999999910593033, 'shell1_animated_vert_rate': 0.0, 'shell1_scale_horiz': 4.0, 'shell1_scale_vert': 2.0, 'shell2_scale_horiz': 10.0, 'shell2_scale_vert': 12.0, 'shell_color': Color(r=1.0, g=0.0, b=0.0, a=0.0)})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeee2b188
        normal_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 20})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x78a13ca0
        damage_info = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 18})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x08ccffd0
        inside_fade_start = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7febbfe7
        inside_fade_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c14904c
        unknown_0x6c14904c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x48b4b865
        flash_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x452f7876
        flash_brightness = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4faac896
        flash_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd5869b0b
        safezone_shape = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x222a258e
        mobile = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6c90e396
        generate_mobile_light = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa7963e03
        mobile_light_offset = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe71b43e1
        unknown_0xe71b43e1 = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9f638987
        unknown_0x9f638987 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8a09f99a
        safe_zone_struct_a_0x8a09f99a = SafeZoneStructA.from_stream(data, property_size, default_override={'enabled': False, 'mode': 1, 'color': Color(r=0.7372549772262573, g=1.0, b=1.0, a=0.0), 'color_rate': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xafb855b8
        safe_zone_struct_a_0xafb855b8 = SafeZoneStructA.from_stream(data, property_size, default_override={'enabled': False, 'mode': 1, 'color': Color(r=0.0, g=0.09803900122642517, b=0.0, a=0.0), 'color_rate': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4476bed8
        echo_parameters = EchoParameters.from_stream(data, property_size)
    
        return cls(editor_properties, trigger, deactivate_on_enter, deactivate_on_exit, activation_time, deactivation_time, lifetime, random_lifetime_offset, impact_effect, filter_sound_effects, unknown_0x414379ea, ignore_cinematic_camera, normal_safe_zone_struct, energized_safe_zone_struct, supercharged_safe_zone_struct, normal_damage, damage_info, inside_fade_start, inside_fade_time, unknown_0x6c14904c, flash_time, flash_brightness, flash_sound, safezone_shape, mobile, generate_mobile_light, mobile_light_offset, unknown_0xe71b43e1, unknown_0x9f638987, safe_zone_struct_a_0x8a09f99a, safe_zone_struct_a_0xafb855b8, echo_parameters)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00 ')  # 32 properties

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

        data.write(b'\x8d3F_')  # 0x8d33465f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.deactivate_on_enter))

        data.write(b'\x1cE9\x86')  # 0x1c453986
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.deactivate_on_exit))

        data.write(b'\xea\xd3\xe2.')  # 0xead3e22e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.activation_time))

        data.write(b'\xb5\xcd\xf1\x96')  # 0xb5cdf196
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.deactivation_time))

        data.write(b'2\xdcg\xf6')  # 0x32dc67f6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.lifetime))

        data.write(b'\xde\x16\x9d\xb0')  # 0xde169db0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.random_lifetime_offset))

        data.write(b'\x9b\xe4\xbb\xd8')  # 0x9be4bbd8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.impact_effect))

        data.write(b'\x82!\x18\xb4')  # 0x822118b4
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.filter_sound_effects))

        data.write(b'ACy\xea')  # 0x414379ea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x414379ea))

        data.write(b'b\xba\xc4`')  # 0x62bac460
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.ignore_cinematic_camera))

        data.write(b'\xb4\xa2\x93\xc7')  # 0xb4a293c7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.normal_safe_zone_struct.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xda\xe8\xc1N')  # 0xdae8c14e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.energized_safe_zone_struct.to_stream(data, default_override={'shell1_animated_horiz_rate': 0.03999999910593033, 'shell1_animated_vert_rate': 0.0, 'shell1_scale_horiz': 4.0, 'shell1_scale_vert': 2.0, 'shell2_scale_horiz': 10.0, 'shell2_scale_vert': 12.0, 'shell_color': Color(r=1.0, g=0.7372549772262573, b=0.3921569883823395, a=0.0)})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'dq\xd6C')  # 0x6471d643
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.supercharged_safe_zone_struct.to_stream(data, default_override={'shell1_animated_horiz_rate': 0.03999999910593033, 'shell1_animated_vert_rate': 0.0, 'shell1_scale_horiz': 4.0, 'shell1_scale_vert': 2.0, 'shell2_scale_horiz': 10.0, 'shell2_scale_vert': 12.0, 'shell_color': Color(r=1.0, g=0.0, b=0.0, a=0.0)})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xee\xe2\xb1\x88')  # 0xeee2b188
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.normal_damage.to_stream(data, default_override={'di_weapon_type': 20})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'x\xa1<\xa0')  # 0x78a13ca0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info.to_stream(data, default_override={'di_weapon_type': 18})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x08\xcc\xff\xd0')  # 0x8ccffd0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.inside_fade_start))

        data.write(b'\x7f\xeb\xbf\xe7')  # 0x7febbfe7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.inside_fade_time))

        data.write(b'l\x14\x90L')  # 0x6c14904c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6c14904c))

        data.write(b'H\xb4\xb8e')  # 0x48b4b865
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flash_time))

        data.write(b'E/xv')  # 0x452f7876
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flash_brightness))

        data.write(b'O\xaa\xc8\x96')  # 0x4faac896
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.flash_sound))

        data.write(b'\xd5\x86\x9b\x0b')  # 0xd5869b0b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.safezone_shape))

        data.write(b'"*%\x8e')  # 0x222a258e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.mobile))

        data.write(b'l\x90\xe3\x96')  # 0x6c90e396
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.generate_mobile_light))

        data.write(b'\xa7\x96>\x03')  # 0xa7963e03
        data.write(b'\x00\x0c')  # size
        self.mobile_light_offset.to_stream(data)

        data.write(b'\xe7\x1bC\xe1')  # 0xe71b43e1
        data.write(b'\x00\x10')  # size
        self.unknown_0xe71b43e1.to_stream(data)

        data.write(b'\x9fc\x89\x87')  # 0x9f638987
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9f638987))

        data.write(b'\x8a\t\xf9\x9a')  # 0x8a09f99a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.safe_zone_struct_a_0x8a09f99a.to_stream(data, default_override={'enabled': False, 'mode': 1, 'color': Color(r=0.7372549772262573, g=1.0, b=1.0, a=0.0), 'color_rate': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xaf\xb8U\xb8')  # 0xafb855b8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.safe_zone_struct_a_0xafb855b8.to_stream(data, default_override={'enabled': False, 'mode': 1, 'color': Color(r=0.0, g=0.09803900122642517, b=0.0, a=0.0), 'color_rate': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'Dv\xbe\xd8')  # 0x4476bed8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.echo_parameters.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SafeZoneJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            trigger=TriggerInfo.from_json(json_data['trigger']),
            deactivate_on_enter=json_data['deactivate_on_enter'],
            deactivate_on_exit=json_data['deactivate_on_exit'],
            activation_time=json_data['activation_time'],
            deactivation_time=json_data['deactivation_time'],
            lifetime=json_data['lifetime'],
            random_lifetime_offset=json_data['random_lifetime_offset'],
            impact_effect=json_data['impact_effect'],
            filter_sound_effects=json_data['filter_sound_effects'],
            unknown_0x414379ea=json_data['unknown_0x414379ea'],
            ignore_cinematic_camera=json_data['ignore_cinematic_camera'],
            normal_safe_zone_struct=SafeZoneStructB.from_json(json_data['normal_safe_zone_struct']),
            energized_safe_zone_struct=SafeZoneStructB.from_json(json_data['energized_safe_zone_struct']),
            supercharged_safe_zone_struct=SafeZoneStructB.from_json(json_data['supercharged_safe_zone_struct']),
            normal_damage=DamageInfo.from_json(json_data['normal_damage']),
            damage_info=DamageInfo.from_json(json_data['damage_info']),
            inside_fade_start=json_data['inside_fade_start'],
            inside_fade_time=json_data['inside_fade_time'],
            unknown_0x6c14904c=json_data['unknown_0x6c14904c'],
            flash_time=json_data['flash_time'],
            flash_brightness=json_data['flash_brightness'],
            flash_sound=json_data['flash_sound'],
            safezone_shape=json_data['safezone_shape'],
            mobile=json_data['mobile'],
            generate_mobile_light=json_data['generate_mobile_light'],
            mobile_light_offset=Vector.from_json(json_data['mobile_light_offset']),
            unknown_0xe71b43e1=Color.from_json(json_data['unknown_0xe71b43e1']),
            unknown_0x9f638987=json_data['unknown_0x9f638987'],
            safe_zone_struct_a_0x8a09f99a=SafeZoneStructA.from_json(json_data['safe_zone_struct_a_0x8a09f99a']),
            safe_zone_struct_a_0xafb855b8=SafeZoneStructA.from_json(json_data['safe_zone_struct_a_0xafb855b8']),
            echo_parameters=EchoParameters.from_json(json_data['echo_parameters']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'trigger': self.trigger.to_json(),
            'deactivate_on_enter': self.deactivate_on_enter,
            'deactivate_on_exit': self.deactivate_on_exit,
            'activation_time': self.activation_time,
            'deactivation_time': self.deactivation_time,
            'lifetime': self.lifetime,
            'random_lifetime_offset': self.random_lifetime_offset,
            'impact_effect': self.impact_effect,
            'filter_sound_effects': self.filter_sound_effects,
            'unknown_0x414379ea': self.unknown_0x414379ea,
            'ignore_cinematic_camera': self.ignore_cinematic_camera,
            'normal_safe_zone_struct': self.normal_safe_zone_struct.to_json(),
            'energized_safe_zone_struct': self.energized_safe_zone_struct.to_json(),
            'supercharged_safe_zone_struct': self.supercharged_safe_zone_struct.to_json(),
            'normal_damage': self.normal_damage.to_json(),
            'damage_info': self.damage_info.to_json(),
            'inside_fade_start': self.inside_fade_start,
            'inside_fade_time': self.inside_fade_time,
            'unknown_0x6c14904c': self.unknown_0x6c14904c,
            'flash_time': self.flash_time,
            'flash_brightness': self.flash_brightness,
            'flash_sound': self.flash_sound,
            'safezone_shape': self.safezone_shape,
            'mobile': self.mobile,
            'generate_mobile_light': self.generate_mobile_light,
            'mobile_light_offset': self.mobile_light_offset.to_json(),
            'unknown_0xe71b43e1': self.unknown_0xe71b43e1.to_json(),
            'unknown_0x9f638987': self.unknown_0x9f638987,
            'safe_zone_struct_a_0x8a09f99a': self.safe_zone_struct_a_0x8a09f99a.to_json(),
            'safe_zone_struct_a_0xafb855b8': self.safe_zone_struct_a_0xafb855b8.to_json(),
            'echo_parameters': self.echo_parameters.to_json(),
        }

    def _dependencies_for_impact_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.impact_effect)

    def _dependencies_for_flash_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.flash_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.trigger.dependencies_for, "trigger", "TriggerInfo"),
            (self._dependencies_for_impact_effect, "impact_effect", "AssetId"),
            (self.normal_safe_zone_struct.dependencies_for, "normal_safe_zone_struct", "SafeZoneStructB"),
            (self.energized_safe_zone_struct.dependencies_for, "energized_safe_zone_struct", "SafeZoneStructB"),
            (self.supercharged_safe_zone_struct.dependencies_for, "supercharged_safe_zone_struct", "SafeZoneStructB"),
            (self.normal_damage.dependencies_for, "normal_damage", "DamageInfo"),
            (self.damage_info.dependencies_for, "damage_info", "DamageInfo"),
            (self._dependencies_for_flash_sound, "flash_sound", "int"),
            (self.safe_zone_struct_a_0x8a09f99a.dependencies_for, "safe_zone_struct_a_0x8a09f99a", "SafeZoneStructA"),
            (self.safe_zone_struct_a_0xafb855b8.dependencies_for, "safe_zone_struct_a_0xafb855b8", "SafeZoneStructA"),
            (self.echo_parameters.dependencies_for, "echo_parameters", "EchoParameters"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for SafeZone.{field_name} ({field_type}): {e}"
                )


def _decode_deactivate_on_enter(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_deactivate_on_exit(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_activation_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_deactivation_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_lifetime(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_random_lifetime_offset(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_impact_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_filter_sound_effects(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x414379ea(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_ignore_cinematic_camera(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_energized_safe_zone_struct(data: typing.BinaryIO, property_size: int) -> SafeZoneStructB:
    return SafeZoneStructB.from_stream(data, property_size, default_override={'shell1_animated_horiz_rate': 0.03999999910593033, 'shell1_animated_vert_rate': 0.0, 'shell1_scale_horiz': 4.0, 'shell1_scale_vert': 2.0, 'shell2_scale_horiz': 10.0, 'shell2_scale_vert': 12.0, 'shell_color': Color(r=1.0, g=0.7372549772262573, b=0.3921569883823395, a=0.0)})


def _decode_supercharged_safe_zone_struct(data: typing.BinaryIO, property_size: int) -> SafeZoneStructB:
    return SafeZoneStructB.from_stream(data, property_size, default_override={'shell1_animated_horiz_rate': 0.03999999910593033, 'shell1_animated_vert_rate': 0.0, 'shell1_scale_horiz': 4.0, 'shell1_scale_vert': 2.0, 'shell2_scale_horiz': 10.0, 'shell2_scale_vert': 12.0, 'shell_color': Color(r=1.0, g=0.0, b=0.0, a=0.0)})


def _decode_normal_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 20})


def _decode_damage_info(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 18})


def _decode_inside_fade_start(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_inside_fade_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6c14904c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flash_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flash_brightness(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flash_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_safezone_shape(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_mobile(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_generate_mobile_light(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_mobile_light_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_unknown_0xe71b43e1(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x9f638987(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_safe_zone_struct_a_0x8a09f99a(data: typing.BinaryIO, property_size: int) -> SafeZoneStructA:
    return SafeZoneStructA.from_stream(data, property_size, default_override={'enabled': False, 'mode': 1, 'color': Color(r=0.7372549772262573, g=1.0, b=1.0, a=0.0), 'color_rate': 5.0})


def _decode_safe_zone_struct_a_0xafb855b8(data: typing.BinaryIO, property_size: int) -> SafeZoneStructA:
    return SafeZoneStructA.from_stream(data, property_size, default_override={'enabled': False, 'mode': 1, 'color': Color(r=0.0, g=0.09803900122642517, b=0.0, a=0.0), 'color_rate': 5.0})


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x77a27411: ('trigger', TriggerInfo.from_stream),
    0x8d33465f: ('deactivate_on_enter', _decode_deactivate_on_enter),
    0x1c453986: ('deactivate_on_exit', _decode_deactivate_on_exit),
    0xead3e22e: ('activation_time', _decode_activation_time),
    0xb5cdf196: ('deactivation_time', _decode_deactivation_time),
    0x32dc67f6: ('lifetime', _decode_lifetime),
    0xde169db0: ('random_lifetime_offset', _decode_random_lifetime_offset),
    0x9be4bbd8: ('impact_effect', _decode_impact_effect),
    0x822118b4: ('filter_sound_effects', _decode_filter_sound_effects),
    0x414379ea: ('unknown_0x414379ea', _decode_unknown_0x414379ea),
    0x62bac460: ('ignore_cinematic_camera', _decode_ignore_cinematic_camera),
    0xb4a293c7: ('normal_safe_zone_struct', SafeZoneStructB.from_stream),
    0xdae8c14e: ('energized_safe_zone_struct', _decode_energized_safe_zone_struct),
    0x6471d643: ('supercharged_safe_zone_struct', _decode_supercharged_safe_zone_struct),
    0xeee2b188: ('normal_damage', _decode_normal_damage),
    0x78a13ca0: ('damage_info', _decode_damage_info),
    0x8ccffd0: ('inside_fade_start', _decode_inside_fade_start),
    0x7febbfe7: ('inside_fade_time', _decode_inside_fade_time),
    0x6c14904c: ('unknown_0x6c14904c', _decode_unknown_0x6c14904c),
    0x48b4b865: ('flash_time', _decode_flash_time),
    0x452f7876: ('flash_brightness', _decode_flash_brightness),
    0x4faac896: ('flash_sound', _decode_flash_sound),
    0xd5869b0b: ('safezone_shape', _decode_safezone_shape),
    0x222a258e: ('mobile', _decode_mobile),
    0x6c90e396: ('generate_mobile_light', _decode_generate_mobile_light),
    0xa7963e03: ('mobile_light_offset', _decode_mobile_light_offset),
    0xe71b43e1: ('unknown_0xe71b43e1', _decode_unknown_0xe71b43e1),
    0x9f638987: ('unknown_0x9f638987', _decode_unknown_0x9f638987),
    0x8a09f99a: ('safe_zone_struct_a_0x8a09f99a', _decode_safe_zone_struct_a_0x8a09f99a),
    0xafb855b8: ('safe_zone_struct_a_0xafb855b8', _decode_safe_zone_struct_a_0xafb855b8),
    0x4476bed8: ('echo_parameters', EchoParameters.from_stream),
}
