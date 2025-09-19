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
from retro_data_structures.properties.corruption.archetypes.CircleLineMode import CircleLineMode
from retro_data_structures.properties.corruption.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.corruption.archetypes.GhorStructB import GhorStructB
from retro_data_structures.properties.corruption.archetypes.GhorStructC import GhorStructC
from retro_data_structures.properties.corruption.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.corruption.archetypes.UnknownStruct38 import UnknownStruct38
from retro_data_structures.properties.corruption.archetypes.UnknownStruct39 import UnknownStruct39
from retro_data_structures.properties.corruption.archetypes.UnknownStruct40 import UnknownStruct40
from retro_data_structures.properties.corruption.archetypes.UnknownStruct41 import UnknownStruct41
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Color import Color

if typing.TYPE_CHECKING:
    class UnknownStruct42Json(typing_extensions.TypedDict):
        is_gandrayda: bool
        unknown_struct38: json_util.JsonObject
        unknown_struct39: json_util.JsonObject
        circle_line_mode: json_util.JsonObject
        ghor_struct_c_0xd345f07f: json_util.JsonObject
        face_effect: str
        ghor_struct_c_0x391a32ae: json_util.JsonObject
        ghor_struct_c_0xafb9313a: json_util.JsonObject
        damage_vulnerability: json_util.JsonObject
        unknown_struct40: json_util.JsonObject
        ghor_struct_c_0x810ec49a: json_util.JsonObject
        unknown_struct41: json_util.JsonObject
        ghor_struct_b_0x0e07b299: json_util.JsonObject
        ghor_struct_b_0x73e98b8f: json_util.JsonObject
        rotate_body_sound: int
        lock_on_locator: str
        energy_bar_string: str
        health_info_0x3d43820c: json_util.JsonObject
        health_info_0x6ed9d988: json_util.JsonObject
        health_info_0xe97f12cb: json_util.JsonObject
        unknown_0xd16b54f9: float
        unknown_0xb40c6fbf: float
        unknown_0x2443e8ec: json_util.JsonValue
        unknown_0x888049bd: json_util.JsonValue
    

@dataclasses.dataclass()
class UnknownStruct42(BaseProperty):
    is_gandrayda: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x531a8c85, original_name='IsGandrayda'
        ),
    })
    unknown_struct38: UnknownStruct38 = dataclasses.field(default_factory=UnknownStruct38, metadata={
        'reflection': FieldReflection[UnknownStruct38](
            UnknownStruct38, id=0x832c442e, original_name='UnknownStruct38', from_json=UnknownStruct38.from_json, to_json=UnknownStruct38.to_json
        ),
    })
    unknown_struct39: UnknownStruct39 = dataclasses.field(default_factory=UnknownStruct39, metadata={
        'reflection': FieldReflection[UnknownStruct39](
            UnknownStruct39, id=0xa0d0963b, original_name='UnknownStruct39', from_json=UnknownStruct39.from_json, to_json=UnknownStruct39.to_json
        ),
    })
    circle_line_mode: CircleLineMode = dataclasses.field(default_factory=CircleLineMode, metadata={
        'reflection': FieldReflection[CircleLineMode](
            CircleLineMode, id=0x81cc0d22, original_name='CircleLineMode', from_json=CircleLineMode.from_json, to_json=CircleLineMode.to_json
        ),
    })
    ghor_struct_c_0xd345f07f: GhorStructC = dataclasses.field(default_factory=GhorStructC, metadata={
        'reflection': FieldReflection[GhorStructC](
            GhorStructC, id=0xd345f07f, original_name='GhorStructC', from_json=GhorStructC.from_json, to_json=GhorStructC.to_json
        ),
    })
    face_effect: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xc59d1a2d, original_name='FaceEffect'
        ),
    })
    ghor_struct_c_0x391a32ae: GhorStructC = dataclasses.field(default_factory=GhorStructC, metadata={
        'reflection': FieldReflection[GhorStructC](
            GhorStructC, id=0x391a32ae, original_name='GhorStructC', from_json=GhorStructC.from_json, to_json=GhorStructC.to_json
        ),
    })
    ghor_struct_c_0xafb9313a: GhorStructC = dataclasses.field(default_factory=GhorStructC, metadata={
        'reflection': FieldReflection[GhorStructC](
            GhorStructC, id=0xafb9313a, original_name='GhorStructC', from_json=GhorStructC.from_json, to_json=GhorStructC.to_json
        ),
    })
    damage_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xba4ad147, original_name='DamageVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    unknown_struct40: UnknownStruct40 = dataclasses.field(default_factory=UnknownStruct40, metadata={
        'reflection': FieldReflection[UnknownStruct40](
            UnknownStruct40, id=0x305cdad2, original_name='UnknownStruct40', from_json=UnknownStruct40.from_json, to_json=UnknownStruct40.to_json
        ),
    })
    ghor_struct_c_0x810ec49a: GhorStructC = dataclasses.field(default_factory=GhorStructC, metadata={
        'reflection': FieldReflection[GhorStructC](
            GhorStructC, id=0x810ec49a, original_name='GhorStructC', from_json=GhorStructC.from_json, to_json=GhorStructC.to_json
        ),
    })
    unknown_struct41: UnknownStruct41 = dataclasses.field(default_factory=UnknownStruct41, metadata={
        'reflection': FieldReflection[UnknownStruct41](
            UnknownStruct41, id=0x5b772f6d, original_name='UnknownStruct41', from_json=UnknownStruct41.from_json, to_json=UnknownStruct41.to_json
        ),
    })
    ghor_struct_b_0x0e07b299: GhorStructB = dataclasses.field(default_factory=GhorStructB, metadata={
        'reflection': FieldReflection[GhorStructB](
            GhorStructB, id=0x0e07b299, original_name='GhorStructB', from_json=GhorStructB.from_json, to_json=GhorStructB.to_json
        ),
    })
    ghor_struct_b_0x73e98b8f: GhorStructB = dataclasses.field(default_factory=GhorStructB, metadata={
        'reflection': FieldReflection[GhorStructB](
            GhorStructB, id=0x73e98b8f, original_name='GhorStructB', from_json=GhorStructB.from_json, to_json=GhorStructB.to_json
        ),
    })
    rotate_body_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x15e3f283, original_name='RotateBodySound'
        ),
    })
    lock_on_locator: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x79bfd886, original_name='LockOnLocator'
        ),
    })
    energy_bar_string: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x337c4056, original_name='EnergyBarString'
        ),
    })
    health_info_0x3d43820c: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0x3d43820c, original_name='HealthInfo', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    health_info_0x6ed9d988: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0x6ed9d988, original_name='HealthInfo', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    health_info_0xe97f12cb: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0xe97f12cb, original_name='HealthInfo', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    unknown_0xd16b54f9: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd16b54f9, original_name='Unknown'
        ),
    })
    unknown_0xb40c6fbf: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb40c6fbf, original_name='Unknown'
        ),
    })
    unknown_0x2443e8ec: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x2443e8ec, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x888049bd: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x888049bd, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
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
        if property_count != 24:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x531a8c85
        is_gandrayda = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x832c442e
        unknown_struct38 = UnknownStruct38.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa0d0963b
        unknown_struct39 = UnknownStruct39.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x81cc0d22
        circle_line_mode = CircleLineMode.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd345f07f
        ghor_struct_c_0xd345f07f = GhorStructC.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc59d1a2d
        face_effect = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x391a32ae
        ghor_struct_c_0x391a32ae = GhorStructC.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xafb9313a
        ghor_struct_c_0xafb9313a = GhorStructC.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xba4ad147
        damage_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x305cdad2
        unknown_struct40 = UnknownStruct40.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x810ec49a
        ghor_struct_c_0x810ec49a = GhorStructC.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5b772f6d
        unknown_struct41 = UnknownStruct41.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0e07b299
        ghor_struct_b_0x0e07b299 = GhorStructB.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x73e98b8f
        ghor_struct_b_0x73e98b8f = GhorStructB.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x15e3f283
        rotate_body_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x79bfd886
        lock_on_locator = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x337c4056
        energy_bar_string = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d43820c
        health_info_0x3d43820c = HealthInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6ed9d988
        health_info_0x6ed9d988 = HealthInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe97f12cb
        health_info_0xe97f12cb = HealthInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd16b54f9
        unknown_0xd16b54f9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb40c6fbf
        unknown_0xb40c6fbf = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2443e8ec
        unknown_0x2443e8ec = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x888049bd
        unknown_0x888049bd = Color.from_stream(data)
    
        return cls(is_gandrayda, unknown_struct38, unknown_struct39, circle_line_mode, ghor_struct_c_0xd345f07f, face_effect, ghor_struct_c_0x391a32ae, ghor_struct_c_0xafb9313a, damage_vulnerability, unknown_struct40, ghor_struct_c_0x810ec49a, unknown_struct41, ghor_struct_b_0x0e07b299, ghor_struct_b_0x73e98b8f, rotate_body_sound, lock_on_locator, energy_bar_string, health_info_0x3d43820c, health_info_0x6ed9d988, health_info_0xe97f12cb, unknown_0xd16b54f9, unknown_0xb40c6fbf, unknown_0x2443e8ec, unknown_0x888049bd)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x18')  # 24 properties

        data.write(b'S\x1a\x8c\x85')  # 0x531a8c85
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_gandrayda))

        data.write(b'\x83,D.')  # 0x832c442e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct38.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa0\xd0\x96;')  # 0xa0d0963b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct39.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x81\xcc\r"')  # 0x81cc0d22
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.circle_line_mode.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd3E\xf0\x7f')  # 0xd345f07f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_c_0xd345f07f.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc5\x9d\x1a-')  # 0xc59d1a2d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.face_effect.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'9\x1a2\xae')  # 0x391a32ae
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_c_0x391a32ae.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xaf\xb91:')  # 0xafb9313a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_c_0xafb9313a.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbaJ\xd1G')  # 0xba4ad147
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'0\\\xda\xd2')  # 0x305cdad2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct40.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x81\x0e\xc4\x9a')  # 0x810ec49a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_c_0x810ec49a.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'[w/m')  # 0x5b772f6d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct41.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x0e\x07\xb2\x99')  # 0xe07b299
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_b_0x0e07b299.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b's\xe9\x8b\x8f')  # 0x73e98b8f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_b_0x73e98b8f.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x15\xe3\xf2\x83')  # 0x15e3f283
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.rotate_body_sound))

        data.write(b'y\xbf\xd8\x86')  # 0x79bfd886
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.lock_on_locator.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'3|@V')  # 0x337c4056
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.energy_bar_string.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'=C\x82\x0c')  # 0x3d43820c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.health_info_0x3d43820c.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'n\xd9\xd9\x88')  # 0x6ed9d988
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.health_info_0x6ed9d988.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe9\x7f\x12\xcb')  # 0xe97f12cb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.health_info_0xe97f12cb.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd1kT\xf9')  # 0xd16b54f9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd16b54f9))

        data.write(b'\xb4\x0co\xbf')  # 0xb40c6fbf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb40c6fbf))

        data.write(b'$C\xe8\xec')  # 0x2443e8ec
        data.write(b'\x00\x10')  # size
        self.unknown_0x2443e8ec.to_stream(data)

        data.write(b'\x88\x80I\xbd')  # 0x888049bd
        data.write(b'\x00\x10')  # size
        self.unknown_0x888049bd.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct42Json", data)
        return cls(
            is_gandrayda=json_data['is_gandrayda'],
            unknown_struct38=UnknownStruct38.from_json(json_data['unknown_struct38']),
            unknown_struct39=UnknownStruct39.from_json(json_data['unknown_struct39']),
            circle_line_mode=CircleLineMode.from_json(json_data['circle_line_mode']),
            ghor_struct_c_0xd345f07f=GhorStructC.from_json(json_data['ghor_struct_c_0xd345f07f']),
            face_effect=json_data['face_effect'],
            ghor_struct_c_0x391a32ae=GhorStructC.from_json(json_data['ghor_struct_c_0x391a32ae']),
            ghor_struct_c_0xafb9313a=GhorStructC.from_json(json_data['ghor_struct_c_0xafb9313a']),
            damage_vulnerability=DamageVulnerability.from_json(json_data['damage_vulnerability']),
            unknown_struct40=UnknownStruct40.from_json(json_data['unknown_struct40']),
            ghor_struct_c_0x810ec49a=GhorStructC.from_json(json_data['ghor_struct_c_0x810ec49a']),
            unknown_struct41=UnknownStruct41.from_json(json_data['unknown_struct41']),
            ghor_struct_b_0x0e07b299=GhorStructB.from_json(json_data['ghor_struct_b_0x0e07b299']),
            ghor_struct_b_0x73e98b8f=GhorStructB.from_json(json_data['ghor_struct_b_0x73e98b8f']),
            rotate_body_sound=json_data['rotate_body_sound'],
            lock_on_locator=json_data['lock_on_locator'],
            energy_bar_string=json_data['energy_bar_string'],
            health_info_0x3d43820c=HealthInfo.from_json(json_data['health_info_0x3d43820c']),
            health_info_0x6ed9d988=HealthInfo.from_json(json_data['health_info_0x6ed9d988']),
            health_info_0xe97f12cb=HealthInfo.from_json(json_data['health_info_0xe97f12cb']),
            unknown_0xd16b54f9=json_data['unknown_0xd16b54f9'],
            unknown_0xb40c6fbf=json_data['unknown_0xb40c6fbf'],
            unknown_0x2443e8ec=Color.from_json(json_data['unknown_0x2443e8ec']),
            unknown_0x888049bd=Color.from_json(json_data['unknown_0x888049bd']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'is_gandrayda': self.is_gandrayda,
            'unknown_struct38': self.unknown_struct38.to_json(),
            'unknown_struct39': self.unknown_struct39.to_json(),
            'circle_line_mode': self.circle_line_mode.to_json(),
            'ghor_struct_c_0xd345f07f': self.ghor_struct_c_0xd345f07f.to_json(),
            'face_effect': self.face_effect,
            'ghor_struct_c_0x391a32ae': self.ghor_struct_c_0x391a32ae.to_json(),
            'ghor_struct_c_0xafb9313a': self.ghor_struct_c_0xafb9313a.to_json(),
            'damage_vulnerability': self.damage_vulnerability.to_json(),
            'unknown_struct40': self.unknown_struct40.to_json(),
            'ghor_struct_c_0x810ec49a': self.ghor_struct_c_0x810ec49a.to_json(),
            'unknown_struct41': self.unknown_struct41.to_json(),
            'ghor_struct_b_0x0e07b299': self.ghor_struct_b_0x0e07b299.to_json(),
            'ghor_struct_b_0x73e98b8f': self.ghor_struct_b_0x73e98b8f.to_json(),
            'rotate_body_sound': self.rotate_body_sound,
            'lock_on_locator': self.lock_on_locator,
            'energy_bar_string': self.energy_bar_string,
            'health_info_0x3d43820c': self.health_info_0x3d43820c.to_json(),
            'health_info_0x6ed9d988': self.health_info_0x6ed9d988.to_json(),
            'health_info_0xe97f12cb': self.health_info_0xe97f12cb.to_json(),
            'unknown_0xd16b54f9': self.unknown_0xd16b54f9,
            'unknown_0xb40c6fbf': self.unknown_0xb40c6fbf,
            'unknown_0x2443e8ec': self.unknown_0x2443e8ec.to_json(),
            'unknown_0x888049bd': self.unknown_0x888049bd.to_json(),
        }


def _decode_is_gandrayda(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_face_effect(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_rotate_body_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_lock_on_locator(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_energy_bar_string(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_unknown_0xd16b54f9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb40c6fbf(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2443e8ec(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x888049bd(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x531a8c85: ('is_gandrayda', _decode_is_gandrayda),
    0x832c442e: ('unknown_struct38', UnknownStruct38.from_stream),
    0xa0d0963b: ('unknown_struct39', UnknownStruct39.from_stream),
    0x81cc0d22: ('circle_line_mode', CircleLineMode.from_stream),
    0xd345f07f: ('ghor_struct_c_0xd345f07f', GhorStructC.from_stream),
    0xc59d1a2d: ('face_effect', _decode_face_effect),
    0x391a32ae: ('ghor_struct_c_0x391a32ae', GhorStructC.from_stream),
    0xafb9313a: ('ghor_struct_c_0xafb9313a', GhorStructC.from_stream),
    0xba4ad147: ('damage_vulnerability', DamageVulnerability.from_stream),
    0x305cdad2: ('unknown_struct40', UnknownStruct40.from_stream),
    0x810ec49a: ('ghor_struct_c_0x810ec49a', GhorStructC.from_stream),
    0x5b772f6d: ('unknown_struct41', UnknownStruct41.from_stream),
    0xe07b299: ('ghor_struct_b_0x0e07b299', GhorStructB.from_stream),
    0x73e98b8f: ('ghor_struct_b_0x73e98b8f', GhorStructB.from_stream),
    0x15e3f283: ('rotate_body_sound', _decode_rotate_body_sound),
    0x79bfd886: ('lock_on_locator', _decode_lock_on_locator),
    0x337c4056: ('energy_bar_string', _decode_energy_bar_string),
    0x3d43820c: ('health_info_0x3d43820c', HealthInfo.from_stream),
    0x6ed9d988: ('health_info_0x6ed9d988', HealthInfo.from_stream),
    0xe97f12cb: ('health_info_0xe97f12cb', HealthInfo.from_stream),
    0xd16b54f9: ('unknown_0xd16b54f9', _decode_unknown_0xd16b54f9),
    0xb40c6fbf: ('unknown_0xb40c6fbf', _decode_unknown_0xb40c6fbf),
    0x2443e8ec: ('unknown_0x2443e8ec', _decode_unknown_0x2443e8ec),
    0x888049bd: ('unknown_0x888049bd', _decode_unknown_0x888049bd),
}
