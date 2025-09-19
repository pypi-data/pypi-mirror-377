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
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.archetypes.LightParameters import LightParameters
from retro_data_structures.properties.corruption.archetypes.SplineType import SplineType
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class EffectJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        particle_effect: int
        auto_start: bool
        unknown_0x3df5a489: bool
        unknown_0x08349bd6: bool
        unknown_0xee538174: bool
        unknown_0xa94b0efd: float
        unknown_0x93756968: float
        unknown_0x0b94597d: float
        unknown_0xd0e8a496: float
        unknown_0xa8bb6c61: bool
        unknown_0x7589d549: float
        unknown_0xa7d7d767: float
        unknown_0xfe69615c: float
        unknown_0x84368d03: float
        unknown_0xa559c066: float
        visible_in_normal: bool
        visible_in_x_ray: bool
        unknown_0x6714021c: bool
        unknown_0xbe931927: bool
        render_order: int
        lighting: json_util.JsonObject
        unknown_0x4d55f7d4: bool
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
        'asset_types': ['PART', 'ELSC', 'SPSC', 'SWHC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0a479d6f, original_name='ParticleEffect'
        ),
    })
    auto_start: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x3217dff8, original_name='AutoStart'
        ),
    })
    unknown_0x3df5a489: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x3df5a489, original_name='Unknown'
        ),
    })
    unknown_0x08349bd6: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x08349bd6, original_name='Unknown'
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
    unknown_0x84368d03: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x84368d03, original_name='Unknown'
        ),
    })
    unknown_0xa559c066: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa559c066, original_name='Unknown'
        ),
    })
    visible_in_normal: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x368bf245, original_name='VisibleInNormal'
        ),
    })
    visible_in_x_ray: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xefffa3be, original_name='VisibleInXRay'
        ),
    })
    unknown_0x6714021c: bool = dataclasses.field(default=True, metadata={
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
    unknown_0x4d55f7d4: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x4d55f7d4, original_name='Unknown'
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
        return Game.CORRUPTION

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
        if property_count != 29:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0a479d6f
        particle_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3217dff8
        auto_start = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3df5a489
        unknown_0x3df5a489 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x08349bd6
        unknown_0x08349bd6 = struct.unpack('>?', data.read(1))[0]
    
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
        assert property_id == 0x84368d03
        unknown_0x84368d03 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa559c066
        unknown_0xa559c066 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x368bf245
        visible_in_normal = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xefffa3be
        visible_in_x_ray = struct.unpack('>?', data.read(1))[0]
    
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
        assert property_id == 0x4d55f7d4
        unknown_0x4d55f7d4 = struct.unpack('>?', data.read(1))[0]
    
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
    
        return cls(editor_properties, particle_effect, auto_start, unknown_0x3df5a489, unknown_0x08349bd6, unknown_0xee538174, unknown_0xa94b0efd, unknown_0x93756968, unknown_0x0b94597d, unknown_0xd0e8a496, unknown_0xa8bb6c61, unknown_0x7589d549, unknown_0xa7d7d767, unknown_0xfe69615c, unknown_0x84368d03, unknown_0xa559c066, visible_in_normal, visible_in_x_ray, unknown_0x6714021c, unknown_0xbe931927, render_order, lighting, unknown_0x4d55f7d4, motion_spline_path_loops, motion_spline_type, motion_control_spline, motion_spline_duration, unknown_0x73e63382, unknown_0x608ecac5)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x1d')  # 29 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\nG\x9do')  # 0xa479d6f
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.particle_effect))

        data.write(b'2\x17\xdf\xf8')  # 0x3217dff8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.auto_start))

        data.write(b'=\xf5\xa4\x89')  # 0x3df5a489
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x3df5a489))

        data.write(b'\x084\x9b\xd6')  # 0x8349bd6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x08349bd6))

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

        data.write(b'\x846\x8d\x03')  # 0x84368d03
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x84368d03))

        data.write(b'\xa5Y\xc0f')  # 0xa559c066
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa559c066))

        data.write(b'6\x8b\xf2E')  # 0x368bf245
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.visible_in_normal))

        data.write(b'\xef\xff\xa3\xbe')  # 0xefffa3be
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.visible_in_x_ray))

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

        data.write(b'MU\xf7\xd4')  # 0x4d55f7d4
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x4d55f7d4))

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
            auto_start=json_data['auto_start'],
            unknown_0x3df5a489=json_data['unknown_0x3df5a489'],
            unknown_0x08349bd6=json_data['unknown_0x08349bd6'],
            unknown_0xee538174=json_data['unknown_0xee538174'],
            unknown_0xa94b0efd=json_data['unknown_0xa94b0efd'],
            unknown_0x93756968=json_data['unknown_0x93756968'],
            unknown_0x0b94597d=json_data['unknown_0x0b94597d'],
            unknown_0xd0e8a496=json_data['unknown_0xd0e8a496'],
            unknown_0xa8bb6c61=json_data['unknown_0xa8bb6c61'],
            unknown_0x7589d549=json_data['unknown_0x7589d549'],
            unknown_0xa7d7d767=json_data['unknown_0xa7d7d767'],
            unknown_0xfe69615c=json_data['unknown_0xfe69615c'],
            unknown_0x84368d03=json_data['unknown_0x84368d03'],
            unknown_0xa559c066=json_data['unknown_0xa559c066'],
            visible_in_normal=json_data['visible_in_normal'],
            visible_in_x_ray=json_data['visible_in_x_ray'],
            unknown_0x6714021c=json_data['unknown_0x6714021c'],
            unknown_0xbe931927=json_data['unknown_0xbe931927'],
            render_order=json_data['render_order'],
            lighting=LightParameters.from_json(json_data['lighting']),
            unknown_0x4d55f7d4=json_data['unknown_0x4d55f7d4'],
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
            'auto_start': self.auto_start,
            'unknown_0x3df5a489': self.unknown_0x3df5a489,
            'unknown_0x08349bd6': self.unknown_0x08349bd6,
            'unknown_0xee538174': self.unknown_0xee538174,
            'unknown_0xa94b0efd': self.unknown_0xa94b0efd,
            'unknown_0x93756968': self.unknown_0x93756968,
            'unknown_0x0b94597d': self.unknown_0x0b94597d,
            'unknown_0xd0e8a496': self.unknown_0xd0e8a496,
            'unknown_0xa8bb6c61': self.unknown_0xa8bb6c61,
            'unknown_0x7589d549': self.unknown_0x7589d549,
            'unknown_0xa7d7d767': self.unknown_0xa7d7d767,
            'unknown_0xfe69615c': self.unknown_0xfe69615c,
            'unknown_0x84368d03': self.unknown_0x84368d03,
            'unknown_0xa559c066': self.unknown_0xa559c066,
            'visible_in_normal': self.visible_in_normal,
            'visible_in_x_ray': self.visible_in_x_ray,
            'unknown_0x6714021c': self.unknown_0x6714021c,
            'unknown_0xbe931927': self.unknown_0xbe931927,
            'render_order': self.render_order,
            'lighting': self.lighting.to_json(),
            'unknown_0x4d55f7d4': self.unknown_0x4d55f7d4,
            'motion_spline_path_loops': self.motion_spline_path_loops,
            'motion_spline_type': self.motion_spline_type.to_json(),
            'motion_control_spline': self.motion_control_spline.to_json(),
            'motion_spline_duration': self.motion_spline_duration,
            'unknown_0x73e63382': self.unknown_0x73e63382,
            'unknown_0x608ecac5': self.unknown_0x608ecac5,
        }


def _decode_particle_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_auto_start(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x3df5a489(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x08349bd6(data: typing.BinaryIO, property_size: int) -> bool:
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


def _decode_unknown_0x84368d03(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa559c066(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_visible_in_normal(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_visible_in_x_ray(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x6714021c(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xbe931927(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_render_order(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x4d55f7d4(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


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
    0x3217dff8: ('auto_start', _decode_auto_start),
    0x3df5a489: ('unknown_0x3df5a489', _decode_unknown_0x3df5a489),
    0x8349bd6: ('unknown_0x08349bd6', _decode_unknown_0x08349bd6),
    0xee538174: ('unknown_0xee538174', _decode_unknown_0xee538174),
    0xa94b0efd: ('unknown_0xa94b0efd', _decode_unknown_0xa94b0efd),
    0x93756968: ('unknown_0x93756968', _decode_unknown_0x93756968),
    0xb94597d: ('unknown_0x0b94597d', _decode_unknown_0x0b94597d),
    0xd0e8a496: ('unknown_0xd0e8a496', _decode_unknown_0xd0e8a496),
    0xa8bb6c61: ('unknown_0xa8bb6c61', _decode_unknown_0xa8bb6c61),
    0x7589d549: ('unknown_0x7589d549', _decode_unknown_0x7589d549),
    0xa7d7d767: ('unknown_0xa7d7d767', _decode_unknown_0xa7d7d767),
    0xfe69615c: ('unknown_0xfe69615c', _decode_unknown_0xfe69615c),
    0x84368d03: ('unknown_0x84368d03', _decode_unknown_0x84368d03),
    0xa559c066: ('unknown_0xa559c066', _decode_unknown_0xa559c066),
    0x368bf245: ('visible_in_normal', _decode_visible_in_normal),
    0xefffa3be: ('visible_in_x_ray', _decode_visible_in_x_ray),
    0x6714021c: ('unknown_0x6714021c', _decode_unknown_0x6714021c),
    0xbe931927: ('unknown_0xbe931927', _decode_unknown_0xbe931927),
    0x2fa4e5d7: ('render_order', _decode_render_order),
    0xb028db0e: ('lighting', LightParameters.from_stream),
    0x4d55f7d4: ('unknown_0x4d55f7d4', _decode_unknown_0x4d55f7d4),
    0x3d7406af: ('motion_spline_path_loops', _decode_motion_spline_path_loops),
    0x493d6a2d: ('motion_spline_type', SplineType.from_stream),
    0x27e5f874: ('motion_control_spline', Spline.from_stream),
    0xfd1e2f56: ('motion_spline_duration', _decode_motion_spline_duration),
    0x73e63382: ('unknown_0x73e63382', _decode_unknown_0x73e63382),
    0x608ecac5: ('unknown_0x608ecac5', _decode_unknown_0x608ecac5),
}
