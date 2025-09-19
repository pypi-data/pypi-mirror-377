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
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Spline import Spline

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class FrontEndDataNetworkJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        is_root: bool
        unknown_0x77f59f4a: bool
        unknown_0x29c0cb7f: bool
        can_be_selected: bool
        is_proxy: bool
        is_locked: bool
        unknown_0x8b8fa0fe: bool
        unknown_0xd0f2d612: bool
        connection_radius: float
        hot_dot_texture: int
        txtr_0x547fffc3: int
        txtr_0xcdaaba00: int
        selected_color: json_util.JsonValue
        unselected_min_color: json_util.JsonValue
        unselected_max_color: json_util.JsonValue
        disabled_color: json_util.JsonValue
        rotation_sound: int
        transition_shrink_spline: json_util.JsonObject
        transition_shrink_time: float
        transition_move_spline: json_util.JsonObject
        transition_move_time: float
        transition_expand_spline: json_util.JsonObject
        transition_expand_time: float
        transition_move_in_spline: json_util.JsonObject
        transition_move_in_time: float
        rotation_sound_volume: int
    

@dataclasses.dataclass()
class FrontEndDataNetwork(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    is_root: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x5c3c9e4a, original_name='IsRoot'
        ),
    })
    unknown_0x77f59f4a: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x77f59f4a, original_name='Unknown'
        ),
    })
    unknown_0x29c0cb7f: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x29c0cb7f, original_name='Unknown'
        ),
    })
    can_be_selected: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x02e74cba, original_name='CanBeSelected'
        ),
    })
    is_proxy: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa2ac58e9, original_name='IsProxy'
        ),
    })
    is_locked: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xdee730f5, original_name='IsLocked'
        ),
    })
    unknown_0x8b8fa0fe: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x8b8fa0fe, original_name='Unknown'
        ),
    })
    unknown_0xd0f2d612: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xd0f2d612, original_name='Unknown'
        ),
    })
    connection_radius: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5ebc97fd, original_name='ConnectionRadius'
        ),
    })
    hot_dot_texture: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x3e5727aa, original_name='HotDotTexture'
        ),
    })
    txtr_0x547fffc3: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x547fffc3, original_name='TXTR'
        ),
    })
    txtr_0xcdaaba00: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xcdaaba00, original_name='TXTR'
        ),
    })
    selected_color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x7f62da5b, original_name='SelectedColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unselected_min_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.49803900718688965, g=0.49803900718688965, b=0.49803900718688965, a=0.749019980430603), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xed286ce4, original_name='UnselectedMinColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unselected_max_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.800000011920929, g=0.800000011920929, b=0.800000011920929, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xad671492, original_name='UnselectedMaxColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    disabled_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.24705900251865387, g=0.24705900251865387, b=0.24705900251865387, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xb44d4c70, original_name='DisabledColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    rotation_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x2d23720f, original_name='RotationSound'
        ),
    })
    transition_shrink_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xec45879e, original_name='TransitionShrinkSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    transition_shrink_time: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfa20775d, original_name='TransitionShrinkTime'
        ),
    })
    transition_move_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x5e30354a, original_name='TransitionMoveSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    transition_move_time: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3c1fa2ca, original_name='TransitionMoveTime'
        ),
    })
    transition_expand_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xb492c2af, original_name='TransitionExpandSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    transition_expand_time: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6d5198b4, original_name='TransitionExpandTime'
        ),
    })
    transition_move_in_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xdf1b312c, original_name='TransitionMoveInSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    transition_move_in_time: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbac12ca0, original_name='TransitionMoveInTime'
        ),
    })
    rotation_sound_volume: int = dataclasses.field(default=127, metadata={
        'reflection': FieldReflection[int](
            int, id=0x4da90d36, original_name='RotationSoundVolume'
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
        return 'FNWK'

    @classmethod
    def modules(cls) -> list[str]:
        return ['ScriptFrontEndDataNetwork.rel']

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
        if property_count != 27:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5c3c9e4a
        is_root = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x77f59f4a
        unknown_0x77f59f4a = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x29c0cb7f
        unknown_0x29c0cb7f = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x02e74cba
        can_be_selected = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa2ac58e9
        is_proxy = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdee730f5
        is_locked = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8b8fa0fe
        unknown_0x8b8fa0fe = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd0f2d612
        unknown_0xd0f2d612 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5ebc97fd
        connection_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3e5727aa
        hot_dot_texture = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x547fffc3
        txtr_0x547fffc3 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcdaaba00
        txtr_0xcdaaba00 = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7f62da5b
        selected_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed286ce4
        unselected_min_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad671492
        unselected_max_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb44d4c70
        disabled_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2d23720f
        rotation_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xec45879e
        transition_shrink_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfa20775d
        transition_shrink_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5e30354a
        transition_move_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3c1fa2ca
        transition_move_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb492c2af
        transition_expand_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d5198b4
        transition_expand_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdf1b312c
        transition_move_in_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbac12ca0
        transition_move_in_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4da90d36
        rotation_sound_volume = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, is_root, unknown_0x77f59f4a, unknown_0x29c0cb7f, can_be_selected, is_proxy, is_locked, unknown_0x8b8fa0fe, unknown_0xd0f2d612, connection_radius, hot_dot_texture, txtr_0x547fffc3, txtr_0xcdaaba00, selected_color, unselected_min_color, unselected_max_color, disabled_color, rotation_sound, transition_shrink_spline, transition_shrink_time, transition_move_spline, transition_move_time, transition_expand_spline, transition_expand_time, transition_move_in_spline, transition_move_in_time, rotation_sound_volume)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x1b')  # 27 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\\<\x9eJ')  # 0x5c3c9e4a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_root))

        data.write(b'w\xf5\x9fJ')  # 0x77f59f4a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x77f59f4a))

        data.write(b')\xc0\xcb\x7f')  # 0x29c0cb7f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x29c0cb7f))

        data.write(b'\x02\xe7L\xba')  # 0x2e74cba
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.can_be_selected))

        data.write(b'\xa2\xacX\xe9')  # 0xa2ac58e9
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_proxy))

        data.write(b'\xde\xe70\xf5')  # 0xdee730f5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_locked))

        data.write(b'\x8b\x8f\xa0\xfe')  # 0x8b8fa0fe
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x8b8fa0fe))

        data.write(b'\xd0\xf2\xd6\x12')  # 0xd0f2d612
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xd0f2d612))

        data.write(b'^\xbc\x97\xfd')  # 0x5ebc97fd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.connection_radius))

        data.write(b">W'\xaa")  # 0x3e5727aa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.hot_dot_texture))

        data.write(b'T\x7f\xff\xc3')  # 0x547fffc3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.txtr_0x547fffc3))

        data.write(b'\xcd\xaa\xba\x00')  # 0xcdaaba00
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.txtr_0xcdaaba00))

        data.write(b'\x7fb\xda[')  # 0x7f62da5b
        data.write(b'\x00\x10')  # size
        self.selected_color.to_stream(data)

        data.write(b'\xed(l\xe4')  # 0xed286ce4
        data.write(b'\x00\x10')  # size
        self.unselected_min_color.to_stream(data)

        data.write(b'\xadg\x14\x92')  # 0xad671492
        data.write(b'\x00\x10')  # size
        self.unselected_max_color.to_stream(data)

        data.write(b'\xb4MLp')  # 0xb44d4c70
        data.write(b'\x00\x10')  # size
        self.disabled_color.to_stream(data)

        data.write(b'-#r\x0f')  # 0x2d23720f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.rotation_sound))

        data.write(b'\xecE\x87\x9e')  # 0xec45879e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.transition_shrink_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfa w]')  # 0xfa20775d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.transition_shrink_time))

        data.write(b'^05J')  # 0x5e30354a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.transition_move_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'<\x1f\xa2\xca')  # 0x3c1fa2ca
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.transition_move_time))

        data.write(b'\xb4\x92\xc2\xaf')  # 0xb492c2af
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.transition_expand_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'mQ\x98\xb4')  # 0x6d5198b4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.transition_expand_time))

        data.write(b'\xdf\x1b1,')  # 0xdf1b312c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.transition_move_in_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xba\xc1,\xa0')  # 0xbac12ca0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.transition_move_in_time))

        data.write(b'M\xa9\r6')  # 0x4da90d36
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.rotation_sound_volume))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("FrontEndDataNetworkJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            is_root=json_data['is_root'],
            unknown_0x77f59f4a=json_data['unknown_0x77f59f4a'],
            unknown_0x29c0cb7f=json_data['unknown_0x29c0cb7f'],
            can_be_selected=json_data['can_be_selected'],
            is_proxy=json_data['is_proxy'],
            is_locked=json_data['is_locked'],
            unknown_0x8b8fa0fe=json_data['unknown_0x8b8fa0fe'],
            unknown_0xd0f2d612=json_data['unknown_0xd0f2d612'],
            connection_radius=json_data['connection_radius'],
            hot_dot_texture=json_data['hot_dot_texture'],
            txtr_0x547fffc3=json_data['txtr_0x547fffc3'],
            txtr_0xcdaaba00=json_data['txtr_0xcdaaba00'],
            selected_color=Color.from_json(json_data['selected_color']),
            unselected_min_color=Color.from_json(json_data['unselected_min_color']),
            unselected_max_color=Color.from_json(json_data['unselected_max_color']),
            disabled_color=Color.from_json(json_data['disabled_color']),
            rotation_sound=json_data['rotation_sound'],
            transition_shrink_spline=Spline.from_json(json_data['transition_shrink_spline']),
            transition_shrink_time=json_data['transition_shrink_time'],
            transition_move_spline=Spline.from_json(json_data['transition_move_spline']),
            transition_move_time=json_data['transition_move_time'],
            transition_expand_spline=Spline.from_json(json_data['transition_expand_spline']),
            transition_expand_time=json_data['transition_expand_time'],
            transition_move_in_spline=Spline.from_json(json_data['transition_move_in_spline']),
            transition_move_in_time=json_data['transition_move_in_time'],
            rotation_sound_volume=json_data['rotation_sound_volume'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'is_root': self.is_root,
            'unknown_0x77f59f4a': self.unknown_0x77f59f4a,
            'unknown_0x29c0cb7f': self.unknown_0x29c0cb7f,
            'can_be_selected': self.can_be_selected,
            'is_proxy': self.is_proxy,
            'is_locked': self.is_locked,
            'unknown_0x8b8fa0fe': self.unknown_0x8b8fa0fe,
            'unknown_0xd0f2d612': self.unknown_0xd0f2d612,
            'connection_radius': self.connection_radius,
            'hot_dot_texture': self.hot_dot_texture,
            'txtr_0x547fffc3': self.txtr_0x547fffc3,
            'txtr_0xcdaaba00': self.txtr_0xcdaaba00,
            'selected_color': self.selected_color.to_json(),
            'unselected_min_color': self.unselected_min_color.to_json(),
            'unselected_max_color': self.unselected_max_color.to_json(),
            'disabled_color': self.disabled_color.to_json(),
            'rotation_sound': self.rotation_sound,
            'transition_shrink_spline': self.transition_shrink_spline.to_json(),
            'transition_shrink_time': self.transition_shrink_time,
            'transition_move_spline': self.transition_move_spline.to_json(),
            'transition_move_time': self.transition_move_time,
            'transition_expand_spline': self.transition_expand_spline.to_json(),
            'transition_expand_time': self.transition_expand_time,
            'transition_move_in_spline': self.transition_move_in_spline.to_json(),
            'transition_move_in_time': self.transition_move_in_time,
            'rotation_sound_volume': self.rotation_sound_volume,
        }

    def _dependencies_for_hot_dot_texture(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.hot_dot_texture)

    def _dependencies_for_txtr_0x547fffc3(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.txtr_0x547fffc3)

    def _dependencies_for_txtr_0xcdaaba00(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.txtr_0xcdaaba00)

    def _dependencies_for_rotation_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.rotation_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self._dependencies_for_hot_dot_texture, "hot_dot_texture", "AssetId"),
            (self._dependencies_for_txtr_0x547fffc3, "txtr_0x547fffc3", "AssetId"),
            (self._dependencies_for_txtr_0xcdaaba00, "txtr_0xcdaaba00", "AssetId"),
            (self._dependencies_for_rotation_sound, "rotation_sound", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for FrontEndDataNetwork.{field_name} ({field_type}): {e}"
                )


def _decode_is_root(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x77f59f4a(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x29c0cb7f(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_can_be_selected(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_is_proxy(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_is_locked(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x8b8fa0fe(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xd0f2d612(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_connection_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hot_dot_texture(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_txtr_0x547fffc3(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_txtr_0xcdaaba00(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_selected_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unselected_min_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unselected_max_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_disabled_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_rotation_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_transition_shrink_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_transition_move_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_transition_expand_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_transition_move_in_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_rotation_sound_volume(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x5c3c9e4a: ('is_root', _decode_is_root),
    0x77f59f4a: ('unknown_0x77f59f4a', _decode_unknown_0x77f59f4a),
    0x29c0cb7f: ('unknown_0x29c0cb7f', _decode_unknown_0x29c0cb7f),
    0x2e74cba: ('can_be_selected', _decode_can_be_selected),
    0xa2ac58e9: ('is_proxy', _decode_is_proxy),
    0xdee730f5: ('is_locked', _decode_is_locked),
    0x8b8fa0fe: ('unknown_0x8b8fa0fe', _decode_unknown_0x8b8fa0fe),
    0xd0f2d612: ('unknown_0xd0f2d612', _decode_unknown_0xd0f2d612),
    0x5ebc97fd: ('connection_radius', _decode_connection_radius),
    0x3e5727aa: ('hot_dot_texture', _decode_hot_dot_texture),
    0x547fffc3: ('txtr_0x547fffc3', _decode_txtr_0x547fffc3),
    0xcdaaba00: ('txtr_0xcdaaba00', _decode_txtr_0xcdaaba00),
    0x7f62da5b: ('selected_color', _decode_selected_color),
    0xed286ce4: ('unselected_min_color', _decode_unselected_min_color),
    0xad671492: ('unselected_max_color', _decode_unselected_max_color),
    0xb44d4c70: ('disabled_color', _decode_disabled_color),
    0x2d23720f: ('rotation_sound', _decode_rotation_sound),
    0xec45879e: ('transition_shrink_spline', Spline.from_stream),
    0xfa20775d: ('transition_shrink_time', _decode_transition_shrink_time),
    0x5e30354a: ('transition_move_spline', Spline.from_stream),
    0x3c1fa2ca: ('transition_move_time', _decode_transition_move_time),
    0xb492c2af: ('transition_expand_spline', Spline.from_stream),
    0x6d5198b4: ('transition_expand_time', _decode_transition_expand_time),
    0xdf1b312c: ('transition_move_in_spline', Spline.from_stream),
    0xbac12ca0: ('transition_move_in_time', _decode_transition_move_in_time),
    0x4da90d36: ('rotation_sound_volume', _decode_rotation_sound_volume),
}
