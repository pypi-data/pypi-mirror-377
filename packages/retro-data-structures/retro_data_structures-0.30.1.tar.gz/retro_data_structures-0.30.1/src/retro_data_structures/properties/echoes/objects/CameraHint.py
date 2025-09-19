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
from retro_data_structures.properties.echoes.archetypes.CameraHintStructA import CameraHintStructA
from retro_data_structures.properties.echoes.archetypes.CameraHintStructB import CameraHintStructB
from retro_data_structures.properties.echoes.archetypes.CameraHintStructC import CameraHintStructC
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.UnknownStruct4 import UnknownStruct4
from retro_data_structures.properties.echoes.archetypes.UnknownStruct5 import UnknownStruct5
from retro_data_structures.properties.echoes.archetypes.UnknownStruct6 import UnknownStruct6
from retro_data_structures.properties.echoes.archetypes.UnknownStruct7 import UnknownStruct7
from retro_data_structures.properties.echoes.archetypes.UnknownStruct8 import UnknownStruct8
from retro_data_structures.properties.echoes.archetypes.UnknownStruct9 import UnknownStruct9
from retro_data_structures.properties.echoes.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class CameraHintJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        priority: int
        timer: float
        unknown_struct4: json_util.JsonObject
        flags_camera_hint: int
        camera_hint_struct_a_0x456d05c6: json_util.JsonObject
        camera_hint_struct_a_0xf5521ffa: json_util.JsonObject
        camera_hint_struct_a_0x89658a06: json_util.JsonObject
        unknown_struct5: json_util.JsonObject
        world_offset: json_util.JsonValue
        unknown_struct6: json_util.JsonObject
        camera_hint_struct_b_0x664c450a: json_util.JsonObject
        camera_hint_struct_b_0xc82395fa: json_util.JsonObject
        unknown_struct7: json_util.JsonObject
        unknown_struct8: json_util.JsonObject
        unknown_0x2ae08be1: float
        unknown_0x4361d075: float
        unknown_0xc91ef813: float
        camera_hint_struct_a1: json_util.JsonObject
        unknown_struct9: json_util.JsonObject
        camera_hint_struct_a_0x138729a7: json_util.JsonObject
    

@dataclasses.dataclass()
class CameraHint(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    priority: int = dataclasses.field(default=50, metadata={
        'reflection': FieldReflection[int](
            int, id=0x42087650, original_name='Priority'
        ),
    })
    timer: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8747552e, original_name='Timer'
        ),
    })
    unknown_struct4: UnknownStruct4 = dataclasses.field(default_factory=UnknownStruct4, metadata={
        'reflection': FieldReflection[UnknownStruct4](
            UnknownStruct4, id=0x380585ec, original_name='UnknownStruct4', from_json=UnknownStruct4.from_json, to_json=UnknownStruct4.to_json
        ),
    })
    flags_camera_hint: int = dataclasses.field(default=286, metadata={
        'reflection': FieldReflection[int](
            int, id=0x21d720a9, original_name='FlagsCameraHint'
        ),
    })
    camera_hint_struct_a_0x456d05c6: CameraHintStructB = dataclasses.field(default_factory=CameraHintStructB, metadata={
        'reflection': FieldReflection[CameraHintStructB](
            CameraHintStructB, id=0x456d05c6, original_name='CameraHintStructA', from_json=CameraHintStructB.from_json, to_json=CameraHintStructB.to_json
        ),
    })
    camera_hint_struct_a_0xf5521ffa: CameraHintStructB = dataclasses.field(default_factory=CameraHintStructB, metadata={
        'reflection': FieldReflection[CameraHintStructB](
            CameraHintStructB, id=0xf5521ffa, original_name='CameraHintStructA', from_json=CameraHintStructB.from_json, to_json=CameraHintStructB.to_json
        ),
    })
    camera_hint_struct_a_0x89658a06: CameraHintStructB = dataclasses.field(default_factory=CameraHintStructB, metadata={
        'reflection': FieldReflection[CameraHintStructB](
            CameraHintStructB, id=0x89658a06, original_name='CameraHintStructA', from_json=CameraHintStructB.from_json, to_json=CameraHintStructB.to_json
        ),
    })
    unknown_struct5: UnknownStruct5 = dataclasses.field(default_factory=UnknownStruct5, metadata={
        'reflection': FieldReflection[UnknownStruct5](
            UnknownStruct5, id=0x8d0a9113, original_name='UnknownStruct5', from_json=UnknownStruct5.from_json, to_json=UnknownStruct5.to_json
        ),
    })
    world_offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=1.0, y=1.0, z=1.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0xefebe838, original_name='WorldOffset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_struct6: UnknownStruct6 = dataclasses.field(default_factory=UnknownStruct6, metadata={
        'reflection': FieldReflection[UnknownStruct6](
            UnknownStruct6, id=0xf71c36f2, original_name='UnknownStruct6', from_json=UnknownStruct6.from_json, to_json=UnknownStruct6.to_json
        ),
    })
    camera_hint_struct_b_0x664c450a: CameraHintStructC = dataclasses.field(default_factory=CameraHintStructC, metadata={
        'reflection': FieldReflection[CameraHintStructC](
            CameraHintStructC, id=0x664c450a, original_name='CameraHintStructB', from_json=CameraHintStructC.from_json, to_json=CameraHintStructC.to_json
        ),
    })
    camera_hint_struct_b_0xc82395fa: CameraHintStructC = dataclasses.field(default_factory=CameraHintStructC, metadata={
        'reflection': FieldReflection[CameraHintStructC](
            CameraHintStructC, id=0xc82395fa, original_name='CameraHintStructB', from_json=CameraHintStructC.from_json, to_json=CameraHintStructC.to_json
        ),
    })
    unknown_struct7: UnknownStruct7 = dataclasses.field(default_factory=UnknownStruct7, metadata={
        'reflection': FieldReflection[UnknownStruct7](
            UnknownStruct7, id=0x645eb009, original_name='UnknownStruct7', from_json=UnknownStruct7.from_json, to_json=UnknownStruct7.to_json
        ),
    })
    unknown_struct8: UnknownStruct8 = dataclasses.field(default_factory=UnknownStruct8, metadata={
        'reflection': FieldReflection[UnknownStruct8](
            UnknownStruct8, id=0x80cfbb54, original_name='UnknownStruct8', from_json=UnknownStruct8.from_json, to_json=UnknownStruct8.to_json
        ),
    })
    unknown_0x2ae08be1: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2ae08be1, original_name='Unknown'
        ),
    })
    unknown_0x4361d075: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4361d075, original_name='Unknown'
        ),
    })
    unknown_0xc91ef813: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc91ef813, original_name='Unknown'
        ),
    })
    camera_hint_struct_a1: CameraHintStructA = dataclasses.field(default_factory=CameraHintStructA, metadata={
        'reflection': FieldReflection[CameraHintStructA](
            CameraHintStructA, id=0x934e392c, original_name='CameraHintStructA1', from_json=CameraHintStructA.from_json, to_json=CameraHintStructA.to_json
        ),
    })
    unknown_struct9: UnknownStruct9 = dataclasses.field(default_factory=UnknownStruct9, metadata={
        'reflection': FieldReflection[UnknownStruct9](
            UnknownStruct9, id=0x9e8631f1, original_name='UnknownStruct9', from_json=UnknownStruct9.from_json, to_json=UnknownStruct9.to_json
        ),
    })
    camera_hint_struct_a_0x138729a7: CameraHintStructA = dataclasses.field(default_factory=CameraHintStructA, metadata={
        'reflection': FieldReflection[CameraHintStructA](
            CameraHintStructA, id=0x138729a7, original_name='CameraHintStructA', from_json=CameraHintStructA.from_json, to_json=CameraHintStructA.to_json
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
        return 'CAMH'

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
        if property_count != 21:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x42087650
        priority = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8747552e
        timer = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x380585ec
        unknown_struct4 = UnknownStruct4.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x21d720a9
        flags_camera_hint = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x456d05c6
        camera_hint_struct_a_0x456d05c6 = CameraHintStructB.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf5521ffa
        camera_hint_struct_a_0xf5521ffa = CameraHintStructB.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x89658a06
        camera_hint_struct_a_0x89658a06 = CameraHintStructB.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8d0a9113
        unknown_struct5 = UnknownStruct5.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xefebe838
        world_offset = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf71c36f2
        unknown_struct6 = UnknownStruct6.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x664c450a
        camera_hint_struct_b_0x664c450a = CameraHintStructC.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc82395fa
        camera_hint_struct_b_0xc82395fa = CameraHintStructC.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x645eb009
        unknown_struct7 = UnknownStruct7.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80cfbb54
        unknown_struct8 = UnknownStruct8.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2ae08be1
        unknown_0x2ae08be1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4361d075
        unknown_0x4361d075 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc91ef813
        unknown_0xc91ef813 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x934e392c
        camera_hint_struct_a1 = CameraHintStructA.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9e8631f1
        unknown_struct9 = UnknownStruct9.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x138729a7
        camera_hint_struct_a_0x138729a7 = CameraHintStructA.from_stream(data, property_size)
    
        return cls(editor_properties, priority, timer, unknown_struct4, flags_camera_hint, camera_hint_struct_a_0x456d05c6, camera_hint_struct_a_0xf5521ffa, camera_hint_struct_a_0x89658a06, unknown_struct5, world_offset, unknown_struct6, camera_hint_struct_b_0x664c450a, camera_hint_struct_b_0xc82395fa, unknown_struct7, unknown_struct8, unknown_0x2ae08be1, unknown_0x4361d075, unknown_0xc91ef813, camera_hint_struct_a1, unknown_struct9, camera_hint_struct_a_0x138729a7)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x15')  # 21 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'B\x08vP')  # 0x42087650
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.priority))

        data.write(b'\x87GU.')  # 0x8747552e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.timer))

        data.write(b'8\x05\x85\xec')  # 0x380585ec
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct4.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'!\xd7 \xa9')  # 0x21d720a9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.flags_camera_hint))

        data.write(b'Em\x05\xc6')  # 0x456d05c6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.camera_hint_struct_a_0x456d05c6.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf5R\x1f\xfa')  # 0xf5521ffa
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.camera_hint_struct_a_0xf5521ffa.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x89e\x8a\x06')  # 0x89658a06
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.camera_hint_struct_a_0x89658a06.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8d\n\x91\x13')  # 0x8d0a9113
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct5.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xef\xeb\xe88')  # 0xefebe838
        data.write(b'\x00\x0c')  # size
        self.world_offset.to_stream(data)

        data.write(b'\xf7\x1c6\xf2')  # 0xf71c36f2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct6.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'fLE\n')  # 0x664c450a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.camera_hint_struct_b_0x664c450a.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc8#\x95\xfa')  # 0xc82395fa
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.camera_hint_struct_b_0xc82395fa.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'd^\xb0\t')  # 0x645eb009
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct7.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x80\xcf\xbbT')  # 0x80cfbb54
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct8.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'*\xe0\x8b\xe1')  # 0x2ae08be1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2ae08be1))

        data.write(b'Ca\xd0u')  # 0x4361d075
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4361d075))

        data.write(b'\xc9\x1e\xf8\x13')  # 0xc91ef813
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc91ef813))

        data.write(b'\x93N9,')  # 0x934e392c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.camera_hint_struct_a1.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9e\x861\xf1')  # 0x9e8631f1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct9.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x13\x87)\xa7')  # 0x138729a7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.camera_hint_struct_a_0x138729a7.to_stream(data)
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
        json_data = typing.cast("CameraHintJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            priority=json_data['priority'],
            timer=json_data['timer'],
            unknown_struct4=UnknownStruct4.from_json(json_data['unknown_struct4']),
            flags_camera_hint=json_data['flags_camera_hint'],
            camera_hint_struct_a_0x456d05c6=CameraHintStructB.from_json(json_data['camera_hint_struct_a_0x456d05c6']),
            camera_hint_struct_a_0xf5521ffa=CameraHintStructB.from_json(json_data['camera_hint_struct_a_0xf5521ffa']),
            camera_hint_struct_a_0x89658a06=CameraHintStructB.from_json(json_data['camera_hint_struct_a_0x89658a06']),
            unknown_struct5=UnknownStruct5.from_json(json_data['unknown_struct5']),
            world_offset=Vector.from_json(json_data['world_offset']),
            unknown_struct6=UnknownStruct6.from_json(json_data['unknown_struct6']),
            camera_hint_struct_b_0x664c450a=CameraHintStructC.from_json(json_data['camera_hint_struct_b_0x664c450a']),
            camera_hint_struct_b_0xc82395fa=CameraHintStructC.from_json(json_data['camera_hint_struct_b_0xc82395fa']),
            unknown_struct7=UnknownStruct7.from_json(json_data['unknown_struct7']),
            unknown_struct8=UnknownStruct8.from_json(json_data['unknown_struct8']),
            unknown_0x2ae08be1=json_data['unknown_0x2ae08be1'],
            unknown_0x4361d075=json_data['unknown_0x4361d075'],
            unknown_0xc91ef813=json_data['unknown_0xc91ef813'],
            camera_hint_struct_a1=CameraHintStructA.from_json(json_data['camera_hint_struct_a1']),
            unknown_struct9=UnknownStruct9.from_json(json_data['unknown_struct9']),
            camera_hint_struct_a_0x138729a7=CameraHintStructA.from_json(json_data['camera_hint_struct_a_0x138729a7']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'priority': self.priority,
            'timer': self.timer,
            'unknown_struct4': self.unknown_struct4.to_json(),
            'flags_camera_hint': self.flags_camera_hint,
            'camera_hint_struct_a_0x456d05c6': self.camera_hint_struct_a_0x456d05c6.to_json(),
            'camera_hint_struct_a_0xf5521ffa': self.camera_hint_struct_a_0xf5521ffa.to_json(),
            'camera_hint_struct_a_0x89658a06': self.camera_hint_struct_a_0x89658a06.to_json(),
            'unknown_struct5': self.unknown_struct5.to_json(),
            'world_offset': self.world_offset.to_json(),
            'unknown_struct6': self.unknown_struct6.to_json(),
            'camera_hint_struct_b_0x664c450a': self.camera_hint_struct_b_0x664c450a.to_json(),
            'camera_hint_struct_b_0xc82395fa': self.camera_hint_struct_b_0xc82395fa.to_json(),
            'unknown_struct7': self.unknown_struct7.to_json(),
            'unknown_struct8': self.unknown_struct8.to_json(),
            'unknown_0x2ae08be1': self.unknown_0x2ae08be1,
            'unknown_0x4361d075': self.unknown_0x4361d075,
            'unknown_0xc91ef813': self.unknown_0xc91ef813,
            'camera_hint_struct_a1': self.camera_hint_struct_a1.to_json(),
            'unknown_struct9': self.unknown_struct9.to_json(),
            'camera_hint_struct_a_0x138729a7': self.camera_hint_struct_a_0x138729a7.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.unknown_struct4.dependencies_for, "unknown_struct4", "UnknownStruct4"),
            (self.camera_hint_struct_a_0x456d05c6.dependencies_for, "camera_hint_struct_a_0x456d05c6", "CameraHintStructB"),
            (self.camera_hint_struct_a_0xf5521ffa.dependencies_for, "camera_hint_struct_a_0xf5521ffa", "CameraHintStructB"),
            (self.camera_hint_struct_a_0x89658a06.dependencies_for, "camera_hint_struct_a_0x89658a06", "CameraHintStructB"),
            (self.unknown_struct5.dependencies_for, "unknown_struct5", "UnknownStruct5"),
            (self.unknown_struct6.dependencies_for, "unknown_struct6", "UnknownStruct6"),
            (self.camera_hint_struct_b_0x664c450a.dependencies_for, "camera_hint_struct_b_0x664c450a", "CameraHintStructC"),
            (self.camera_hint_struct_b_0xc82395fa.dependencies_for, "camera_hint_struct_b_0xc82395fa", "CameraHintStructC"),
            (self.unknown_struct7.dependencies_for, "unknown_struct7", "UnknownStruct7"),
            (self.unknown_struct8.dependencies_for, "unknown_struct8", "UnknownStruct8"),
            (self.camera_hint_struct_a1.dependencies_for, "camera_hint_struct_a1", "CameraHintStructA"),
            (self.unknown_struct9.dependencies_for, "unknown_struct9", "UnknownStruct9"),
            (self.camera_hint_struct_a_0x138729a7.dependencies_for, "camera_hint_struct_a_0x138729a7", "CameraHintStructA"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for CameraHint.{field_name} ({field_type}): {e}"
                )


def _decode_priority(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flags_camera_hint(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_world_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_unknown_0x2ae08be1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4361d075(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc91ef813(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x42087650: ('priority', _decode_priority),
    0x8747552e: ('timer', _decode_timer),
    0x380585ec: ('unknown_struct4', UnknownStruct4.from_stream),
    0x21d720a9: ('flags_camera_hint', _decode_flags_camera_hint),
    0x456d05c6: ('camera_hint_struct_a_0x456d05c6', CameraHintStructB.from_stream),
    0xf5521ffa: ('camera_hint_struct_a_0xf5521ffa', CameraHintStructB.from_stream),
    0x89658a06: ('camera_hint_struct_a_0x89658a06', CameraHintStructB.from_stream),
    0x8d0a9113: ('unknown_struct5', UnknownStruct5.from_stream),
    0xefebe838: ('world_offset', _decode_world_offset),
    0xf71c36f2: ('unknown_struct6', UnknownStruct6.from_stream),
    0x664c450a: ('camera_hint_struct_b_0x664c450a', CameraHintStructC.from_stream),
    0xc82395fa: ('camera_hint_struct_b_0xc82395fa', CameraHintStructC.from_stream),
    0x645eb009: ('unknown_struct7', UnknownStruct7.from_stream),
    0x80cfbb54: ('unknown_struct8', UnknownStruct8.from_stream),
    0x2ae08be1: ('unknown_0x2ae08be1', _decode_unknown_0x2ae08be1),
    0x4361d075: ('unknown_0x4361d075', _decode_unknown_0x4361d075),
    0xc91ef813: ('unknown_0xc91ef813', _decode_unknown_0xc91ef813),
    0x934e392c: ('camera_hint_struct_a1', CameraHintStructA.from_stream),
    0x9e8631f1: ('unknown_struct9', UnknownStruct9.from_stream),
    0x138729a7: ('camera_hint_struct_a_0x138729a7', CameraHintStructA.from_stream),
}
