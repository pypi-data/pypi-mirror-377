# Generated file
import struct
import typing
import typing_extensions

from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_vector import BaseVector


class Vector(BaseVector):
    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(*struct.unpack('>fff', data.read(12)))

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack('>fff', self.x, self.y, self.z))

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION
