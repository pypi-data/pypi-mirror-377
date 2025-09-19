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
from retro_data_structures.properties.echoes.archetypes.LightParameters import LightParameters
from retro_data_structures.properties.echoes.archetypes.SplineType import SplineType
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Spline import Spline

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class EffectJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        particle_effect: int
        unknown_0x3df5a489: bool
        restart_on_activate: bool
        unknown_0xee538174: bool
        unknown_0xa94b0efd: float
        unknown_0x93756968: float
        unknown_0x0b94597d: float
        unknown_0xd0e8a496: float
        unknown_0xa8bb6c61: bool
        unknown_0x7589d549: float
        unknown_0xa7d7d767: float
        unknown_0xfe69615c: float
        unknown_0x88d914a6: bool
        visible_in_dark: bool
        visible_in_echo: bool
        unknown_0x6714021c: bool
        unknown_0xbe931927: bool
        render_order: int
        lighting: json_util.JsonObject
        motion_spline_path_loops: bool
        motion_spline_type: json_util.JsonObject
        motion_control_spline: json_util.JsonObject
        motion_spline_duration: float
        unknown_0x73e63382: bool
        unknown_0x608ecac5: bool
    

@dataclasses.dataclass()
class Effect(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    particle_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART', 'ELSC', 'SRSC', 'SPSC', 'SWHC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0a479d6f, original_name='ParticleEffect'
        ),
    })
    unknown_0x3df5a489: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x3df5a489, original_name='Unknown'
        ),
    })
    restart_on_activate: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa4b9984f, original_name='RestartOnActivate'
        ),
    })
    unknown_0xee538174: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xee538174, original_name='Unknown'
        ),
    })
    unknown_0xa94b0efd: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa94b0efd, original_name='Unknown'
        ),
    })
    unknown_0x93756968: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x93756968, original_name='Unknown'
        ),
    })
    unknown_0x0b94597d: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0b94597d, original_name='Unknown'
        ),
    })
    unknown_0xd0e8a496: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd0e8a496, original_name='Unknown'
        ),
    })
    unknown_0xa8bb6c61: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa8bb6c61, original_name='Unknown'
        ),
    })
    unknown_0x7589d549: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7589d549, original_name='Unknown'
        ),
    })
    unknown_0xa7d7d767: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa7d7d767, original_name='Unknown'
        ),
    })
    unknown_0xfe69615c: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfe69615c, original_name='Unknown'
        ),
    })
    unknown_0x88d914a6: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x88d914a6, original_name='Unknown'
        ),
    })
    visible_in_dark: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc2028cc2, original_name='VisibleInDark'
        ),
    })
    visible_in_echo: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xcefa1a48, original_name='VisibleInEcho'
        ),
    })
    unknown_0x6714021c: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x6714021c, original_name='Unknown'
        ),
    })
    unknown_0xbe931927: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xbe931927, original_name='Unknown'
        ),
    })
    render_order: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x2fa4e5d7, original_name='RenderOrder'
        ),
    })
    lighting: LightParameters = dataclasses.field(default_factory=LightParameters, metadata={
        'reflection': FieldReflection[LightParameters](
            LightParameters, id=0xb028db0e, original_name='Lighting', from_json=LightParameters.from_json, to_json=LightParameters.to_json
        ),
    })
    motion_spline_path_loops: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x3d7406af, original_name='MotionSplinePathLoops'
        ),
    })
    motion_spline_type: SplineType = dataclasses.field(default_factory=SplineType, metadata={
        'reflection': FieldReflection[SplineType](
            SplineType, id=0x493d6a2d, original_name='MotionSplineType', from_json=SplineType.from_json, to_json=SplineType.to_json
        ),
    })
    motion_control_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x27e5f874, original_name='MotionControlSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    motion_spline_duration: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfd1e2f56, original_name='MotionSplineDuration'
        ),
    })
    unknown_0x73e63382: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x73e63382, original_name='Unknown'
        ),
    })
    unknown_0x608ecac5: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x608ecac5, original_name='Unknown'
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
        return 'EFCT'

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
        if property_count != 26:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0a479d6f
        particle_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3df5a489
        unknown_0x3df5a489 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa4b9984f
        restart_on_activate = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xee538174
        unknown_0xee538174 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa94b0efd
        unknown_0xa94b0efd = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x93756968
        unknown_0x93756968 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0b94597d
        unknown_0x0b94597d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd0e8a496
        unknown_0xd0e8a496 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa8bb6c61
        unknown_0xa8bb6c61 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7589d549
        unknown_0x7589d549 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa7d7d767
        unknown_0xa7d7d767 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfe69615c
        unknown_0xfe69615c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x88d914a6
        unknown_0x88d914a6 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc2028cc2
        visible_in_dark = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcefa1a48
        visible_in_echo = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6714021c
        unknown_0x6714021c = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe931927
        unknown_0xbe931927 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2fa4e5d7
        render_order = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb028db0e
        lighting = LightParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d7406af
        motion_spline_path_loops = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x493d6a2d
        motion_spline_type = SplineType.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x27e5f874
        motion_control_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd1e2f56
        motion_spline_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x73e63382
        unknown_0x73e63382 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x608ecac5
        unknown_0x608ecac5 = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, particle_effect, unknown_0x3df5a489, restart_on_activate, unknown_0xee538174, unknown_0xa94b0efd, unknown_0x93756968, unknown_0x0b94597d, unknown_0xd0e8a496, unknown_0xa8bb6c61, unknown_0x7589d549, unknown_0xa7d7d767, unknown_0xfe69615c, unknown_0x88d914a6, visible_in_dark, visible_in_echo, unknown_0x6714021c, unknown_0xbe931927, render_order, lighting, motion_spline_path_loops, motion_spline_type, motion_control_spline, motion_spline_duration, unknown_0x73e63382, unknown_0x608ecac5)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x1a')  # 26 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\nG\x9do')  # 0xa479d6f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.particle_effect))

        data.write(b'=\xf5\xa4\x89')  # 0x3df5a489
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x3df5a489))

        data.write(b'\xa4\xb9\x98O')  # 0xa4b9984f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.restart_on_activate))

        data.write(b'\xeeS\x81t')  # 0xee538174
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xee538174))

        data.write(b'\xa9K\x0e\xfd')  # 0xa94b0efd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa94b0efd))

        data.write(b'\x93uih')  # 0x93756968
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x93756968))

        data.write(b'\x0b\x94Y}')  # 0xb94597d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0b94597d))

        data.write(b'\xd0\xe8\xa4\x96')  # 0xd0e8a496
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd0e8a496))

        data.write(b'\xa8\xbbla')  # 0xa8bb6c61
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xa8bb6c61))

        data.write(b'u\x89\xd5I')  # 0x7589d549
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7589d549))

        data.write(b'\xa7\xd7\xd7g')  # 0xa7d7d767
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa7d7d767))

        data.write(b'\xfeia\\')  # 0xfe69615c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfe69615c))

        data.write(b'\x88\xd9\x14\xa6')  # 0x88d914a6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x88d914a6))

        data.write(b'\xc2\x02\x8c\xc2')  # 0xc2028cc2
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.visible_in_dark))

        data.write(b'\xce\xfa\x1aH')  # 0xcefa1a48
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.visible_in_echo))

        data.write(b'g\x14\x02\x1c')  # 0x6714021c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x6714021c))

        data.write(b"\xbe\x93\x19'")  # 0xbe931927
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xbe931927))

        data.write(b'/\xa4\xe5\xd7')  # 0x2fa4e5d7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.render_order))

        data.write(b'\xb0(\xdb\x0e')  # 0xb028db0e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.lighting.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'=t\x06\xaf')  # 0x3d7406af
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.motion_spline_path_loops))

        data.write(b'I=j-')  # 0x493d6a2d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.motion_spline_type.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"'\xe5\xf8t")  # 0x27e5f874
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.motion_control_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfd\x1e/V')  # 0xfd1e2f56
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.motion_spline_duration))

        data.write(b's\xe63\x82')  # 0x73e63382
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x73e63382))

        data.write(b'`\x8e\xca\xc5')  # 0x608ecac5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x608ecac5))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("EffectJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            particle_effect=json_data['particle_effect'],
            unknown_0x3df5a489=json_data['unknown_0x3df5a489'],
            restart_on_activate=json_data['restart_on_activate'],
            unknown_0xee538174=json_data['unknown_0xee538174'],
            unknown_0xa94b0efd=json_data['unknown_0xa94b0efd'],
            unknown_0x93756968=json_data['unknown_0x93756968'],
            unknown_0x0b94597d=json_data['unknown_0x0b94597d'],
            unknown_0xd0e8a496=json_data['unknown_0xd0e8a496'],
            unknown_0xa8bb6c61=json_data['unknown_0xa8bb6c61'],
            unknown_0x7589d549=json_data['unknown_0x7589d549'],
            unknown_0xa7d7d767=json_data['unknown_0xa7d7d767'],
            unknown_0xfe69615c=json_data['unknown_0xfe69615c'],
            unknown_0x88d914a6=json_data['unknown_0x88d914a6'],
            visible_in_dark=json_data['visible_in_dark'],
            visible_in_echo=json_data['visible_in_echo'],
            unknown_0x6714021c=json_data['unknown_0x6714021c'],
            unknown_0xbe931927=json_data['unknown_0xbe931927'],
            render_order=json_data['render_order'],
            lighting=LightParameters.from_json(json_data['lighting']),
            motion_spline_path_loops=json_data['motion_spline_path_loops'],
            motion_spline_type=SplineType.from_json(json_data['motion_spline_type']),
            motion_control_spline=Spline.from_json(json_data['motion_control_spline']),
            motion_spline_duration=json_data['motion_spline_duration'],
            unknown_0x73e63382=json_data['unknown_0x73e63382'],
            unknown_0x608ecac5=json_data['unknown_0x608ecac5'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'particle_effect': self.particle_effect,
            'unknown_0x3df5a489': self.unknown_0x3df5a489,
            'restart_on_activate': self.restart_on_activate,
            'unknown_0xee538174': self.unknown_0xee538174,
            'unknown_0xa94b0efd': self.unknown_0xa94b0efd,
            'unknown_0x93756968': self.unknown_0x93756968,
            'unknown_0x0b94597d': self.unknown_0x0b94597d,
            'unknown_0xd0e8a496': self.unknown_0xd0e8a496,
            'unknown_0xa8bb6c61': self.unknown_0xa8bb6c61,
            'unknown_0x7589d549': self.unknown_0x7589d549,
            'unknown_0xa7d7d767': self.unknown_0xa7d7d767,
            'unknown_0xfe69615c': self.unknown_0xfe69615c,
            'unknown_0x88d914a6': self.unknown_0x88d914a6,
            'visible_in_dark': self.visible_in_dark,
            'visible_in_echo': self.visible_in_echo,
            'unknown_0x6714021c': self.unknown_0x6714021c,
            'unknown_0xbe931927': self.unknown_0xbe931927,
            'render_order': self.render_order,
            'lighting': self.lighting.to_json(),
            'motion_spline_path_loops': self.motion_spline_path_loops,
            'motion_spline_type': self.motion_spline_type.to_json(),
            'motion_control_spline': self.motion_control_spline.to_json(),
            'motion_spline_duration': self.motion_spline_duration,
            'unknown_0x73e63382': self.unknown_0x73e63382,
            'unknown_0x608ecac5': self.unknown_0x608ecac5,
        }

    def _dependencies_for_particle_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle_effect)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self._dependencies_for_particle_effect, "particle_effect", "AssetId"),
            (self.lighting.dependencies_for, "lighting", "LightParameters"),
            (self.motion_spline_type.dependencies_for, "motion_spline_type", "SplineType"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Effect.{field_name} ({field_type}): {e}"
                )


def _decode_particle_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_unknown_0x3df5a489(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_restart_on_activate(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xee538174(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xa94b0efd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x93756968(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0b94597d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd0e8a496(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa8bb6c61(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x7589d549(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa7d7d767(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfe69615c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x88d914a6(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_visible_in_dark(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_visible_in_echo(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x6714021c(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xbe931927(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_render_order(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_motion_spline_path_loops(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_motion_spline_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x73e63382(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x608ecac5(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xa479d6f: ('particle_effect', _decode_particle_effect),
    0x3df5a489: ('unknown_0x3df5a489', _decode_unknown_0x3df5a489),
    0xa4b9984f: ('restart_on_activate', _decode_restart_on_activate),
    0xee538174: ('unknown_0xee538174', _decode_unknown_0xee538174),
    0xa94b0efd: ('unknown_0xa94b0efd', _decode_unknown_0xa94b0efd),
    0x93756968: ('unknown_0x93756968', _decode_unknown_0x93756968),
    0xb94597d: ('unknown_0x0b94597d', _decode_unknown_0x0b94597d),
    0xd0e8a496: ('unknown_0xd0e8a496', _decode_unknown_0xd0e8a496),
    0xa8bb6c61: ('unknown_0xa8bb6c61', _decode_unknown_0xa8bb6c61),
    0x7589d549: ('unknown_0x7589d549', _decode_unknown_0x7589d549),
    0xa7d7d767: ('unknown_0xa7d7d767', _decode_unknown_0xa7d7d767),
    0xfe69615c: ('unknown_0xfe69615c', _decode_unknown_0xfe69615c),
    0x88d914a6: ('unknown_0x88d914a6', _decode_unknown_0x88d914a6),
    0xc2028cc2: ('visible_in_dark', _decode_visible_in_dark),
    0xcefa1a48: ('visible_in_echo', _decode_visible_in_echo),
    0x6714021c: ('unknown_0x6714021c', _decode_unknown_0x6714021c),
    0xbe931927: ('unknown_0xbe931927', _decode_unknown_0xbe931927),
    0x2fa4e5d7: ('render_order', _decode_render_order),
    0xb028db0e: ('lighting', LightParameters.from_stream),
    0x3d7406af: ('motion_spline_path_loops', _decode_motion_spline_path_loops),
    0x493d6a2d: ('motion_spline_type', SplineType.from_stream),
    0x27e5f874: ('motion_control_spline', Spline.from_stream),
    0xfd1e2f56: ('motion_spline_duration', _decode_motion_spline_duration),
    0x73e63382: ('unknown_0x73e63382', _decode_unknown_0x73e63382),
    0x608ecac5: ('unknown_0x608ecac5', _decode_unknown_0x608ecac5),
}
