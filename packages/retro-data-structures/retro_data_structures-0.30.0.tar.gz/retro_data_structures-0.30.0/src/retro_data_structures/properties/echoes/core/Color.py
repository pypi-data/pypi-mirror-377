# Generated file
import struct
import typing
import typing_extensions

from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_color import BaseColor


class Color(BaseColor):
    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(*struct.unpack('>ffff', data.read(16)))

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack('>ffff', self.r, self.g, self.b, self.a))


    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES
