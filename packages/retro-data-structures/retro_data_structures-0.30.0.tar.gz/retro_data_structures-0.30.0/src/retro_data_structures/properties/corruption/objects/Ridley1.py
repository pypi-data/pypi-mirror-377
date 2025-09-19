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
from retro_data_structures.properties.corruption.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.corruption.archetypes.Ridley1Data import Ridley1Data
from retro_data_structures.properties.corruption.archetypes.UnknownStruct53 import UnknownStruct53

if typing.TYPE_CHECKING:
    class Ridley1Json(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        unknown_struct53: json_util.JsonObject
        ridley1_data_0x3a80d135: json_util.JsonObject
        patterned: json_util.JsonObject
        ridley1_data_0x1c1698f5: json_util.JsonObject
        patterned_ai_0x1464ae05: json_util.JsonObject
        ridley1_data_0x1cf90c26: json_util.JsonObject
        patterned_ai_0x24d00673: json_util.JsonObject
        actor_information: json_util.JsonObject
    

@dataclasses.dataclass()
class Ridley1(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    unknown_struct53: UnknownStruct53 = dataclasses.field(default_factory=UnknownStruct53, metadata={
        'reflection': FieldReflection[UnknownStruct53](
            UnknownStruct53, id=0x5fd3de4e, original_name='UnknownStruct53', from_json=UnknownStruct53.from_json, to_json=UnknownStruct53.to_json
        ),
    })
    ridley1_data_0x3a80d135: Ridley1Data = dataclasses.field(default_factory=Ridley1Data, metadata={
        'reflection': FieldReflection[Ridley1Data](
            Ridley1Data, id=0x3a80d135, original_name='Ridley1Data', from_json=Ridley1Data.from_json, to_json=Ridley1Data.to_json
        ),
    })
    patterned: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0xb3774750, original_name='Patterned', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    ridley1_data_0x1c1698f5: Ridley1Data = dataclasses.field(default_factory=Ridley1Data, metadata={
        'reflection': FieldReflection[Ridley1Data](
            Ridley1Data, id=0x1c1698f5, original_name='Ridley1Data', from_json=Ridley1Data.from_json, to_json=Ridley1Data.to_json
        ),
    })
    patterned_ai_0x1464ae05: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0x1464ae05, original_name='PatternedAI', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    ridley1_data_0x1cf90c26: Ridley1Data = dataclasses.field(default_factory=Ridley1Data, metadata={
        'reflection': FieldReflection[Ridley1Data](
            Ridley1Data, id=0x1cf90c26, original_name='Ridley1Data', from_json=Ridley1Data.from_json, to_json=Ridley1Data.to_json
        ),
    })
    patterned_ai_0x24d00673: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0x24d00673, original_name='PatternedAI', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
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
        return 'RID1'

    @classmethod
    def modules(cls) -> list[str]:
        return ['RSO_Ridley1.rso']

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
        if property_count != 9:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5fd3de4e
        unknown_struct53 = UnknownStruct53.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3a80d135
        ridley1_data_0x3a80d135 = Ridley1Data.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1c1698f5
        ridley1_data_0x1c1698f5 = Ridley1Data.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1464ae05
        patterned_ai_0x1464ae05 = PatternedAITypedef.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1cf90c26
        ridley1_data_0x1cf90c26 = Ridley1Data.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x24d00673
        patterned_ai_0x24d00673 = PatternedAITypedef.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        return cls(editor_properties, unknown_struct53, ridley1_data_0x3a80d135, patterned, ridley1_data_0x1c1698f5, patterned_ai_0x1464ae05, ridley1_data_0x1cf90c26, patterned_ai_0x24d00673, actor_information)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\t')  # 9 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'_\xd3\xdeN')  # 0x5fd3de4e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct53.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b':\x80\xd15')  # 0x3a80d135
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ridley1_data_0x3a80d135.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb3wGP')  # 0xb3774750
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1c\x16\x98\xf5')  # 0x1c1698f5
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ridley1_data_0x1c1698f5.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x14d\xae\x05')  # 0x1464ae05
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned_ai_0x1464ae05.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1c\xf9\x0c&')  # 0x1cf90c26
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ridley1_data_0x1cf90c26.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'$\xd0\x06s')  # 0x24d00673
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned_ai_0x24d00673.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'~9\x7f\xed')  # 0x7e397fed
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.actor_information.to_stream(data)
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
        json_data = typing.cast("Ridley1Json", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            unknown_struct53=UnknownStruct53.from_json(json_data['unknown_struct53']),
            ridley1_data_0x3a80d135=Ridley1Data.from_json(json_data['ridley1_data_0x3a80d135']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            ridley1_data_0x1c1698f5=Ridley1Data.from_json(json_data['ridley1_data_0x1c1698f5']),
            patterned_ai_0x1464ae05=PatternedAITypedef.from_json(json_data['patterned_ai_0x1464ae05']),
            ridley1_data_0x1cf90c26=Ridley1Data.from_json(json_data['ridley1_data_0x1cf90c26']),
            patterned_ai_0x24d00673=PatternedAITypedef.from_json(json_data['patterned_ai_0x24d00673']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'unknown_struct53': self.unknown_struct53.to_json(),
            'ridley1_data_0x3a80d135': self.ridley1_data_0x3a80d135.to_json(),
            'patterned': self.patterned.to_json(),
            'ridley1_data_0x1c1698f5': self.ridley1_data_0x1c1698f5.to_json(),
            'patterned_ai_0x1464ae05': self.patterned_ai_0x1464ae05.to_json(),
            'ridley1_data_0x1cf90c26': self.ridley1_data_0x1cf90c26.to_json(),
            'patterned_ai_0x24d00673': self.patterned_ai_0x24d00673.to_json(),
            'actor_information': self.actor_information.to_json(),
        }


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x5fd3de4e: ('unknown_struct53', UnknownStruct53.from_stream),
    0x3a80d135: ('ridley1_data_0x3a80d135', Ridley1Data.from_stream),
    0xb3774750: ('patterned', PatternedAITypedef.from_stream),
    0x1c1698f5: ('ridley1_data_0x1c1698f5', Ridley1Data.from_stream),
    0x1464ae05: ('patterned_ai_0x1464ae05', PatternedAITypedef.from_stream),
    0x1cf90c26: ('ridley1_data_0x1cf90c26', Ridley1Data.from_stream),
    0x24d00673: ('patterned_ai_0x24d00673', PatternedAITypedef.from_stream),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
}
