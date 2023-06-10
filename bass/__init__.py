__all__ = (
    'Song',
    'Music',
    'SoundEffect',
)

import logging
from collections import defaultdict
from ctypes import c_float, byref
from hashlib import sha1
from pathlib import Path

from bass.accessor import Bass, BassStream, BassChannel, BassMusic, BassException
from bass.bass_tags import BassTags
from bass.bass_types import NULL, HMusic, HANDLE
from bass.constants import Error, MusicAttrib
from bass.functions import BASS_ChannelGetAttribute

log = logging.getLogger(__name__)
HMusicNULL = HMusic()


DEBUG_BASS = False

MUSIC_SUFFIXES = ('.xm', '.mod', '.mo3', '.it')


class Song:
    _handle: HANDLE
    _length_seconds: float
    _length_bytes: int

    _position_seconds: float
    file_path: Path
    tags: dict[str, str | None] | None

    def __init__(self, file_path: str | Path, length_seconds: float | None = None, length_bytes: int = None,
                 tags: dict[str, str | None] | None = None):
        Bass.init()  # TODO: 不要在这里初始化 bass？
        self.file_path = Path(file_path)
        # self._id = uuid4().hex
        self._id = sha1(str(self.file_path.as_posix()).encode("utf-8")).hexdigest()
        if not self.file_path.exists():
            raise ValueError(f"{file_path} doesn't exist")
        if not self.file_path.is_file():
            raise ValueError(f"{file_path=} is not a valid file")

        self._handle = NULL
        self._length_seconds = length_seconds
        self._length_bytes = length_bytes
        self._position_seconds = 0
        self.tags = tags

    def __del__(self):
        self.free_stream()

    @property
    def id(self):
        return self._id

    def _create_stream(self):
        self._handle = self._create_handle()
        Bass.may_raise_error(f'{self.file_path=}')
        if self._length_bytes is None:
            self._length_bytes = BassChannel.get_length_bytes(self._handle)
            self._length_seconds = BassChannel.get_length_seconds(self._handle, self._length_bytes)
        if self.tags is None:
            self.tags = BassTags.GetDefaultTags(self._handle)

    def free_stream(self, direct_stop: bool = False) -> None:
        if self._handle is NULL:
            return
        if self.playing or self.paused:
            if direct_stop:
                BassChannel.stop(self._handle)
            else:
                self.stop()
        ok = self._free_handle()
        if not ok:
            Bass.may_raise_error()
        self._handle = NULL

    def _free_handle(self):
        return BassStream.free(self._handle)

    def touch(self) -> None:
        self._create_stream()
        self.free_stream()

    @property
    def position(self) -> float:
        return BassChannel.get_position_seconds(self.handle)

    @property
    def position_bytes(self) -> int:
        return BassChannel.get_position_bytes(self.handle)

    @property
    def position_time(self):
        seconds = int(self.position % 60)
        minutes = int(self.position // 60)
        return f"{minutes:02}:{seconds:02}"

    @property
    def duration(self) -> float:
        if self._length_seconds is None and self._handle is NULL:
            self.touch()
        return self._length_seconds

    @property
    def duration_bytes(self) -> int:
        if self._length_bytes is None and self._handle is NULL:
            self.touch()
        return self._length_bytes

    @property
    def duration_time(self):
        seconds = int(self.duration % 60)
        minutes = int(self.duration // 60)
        return f"{minutes:02}:{seconds:02}"

    @property
    def remaining_seconds(self):
        return self.duration - self.position

    @property
    def remaining_bytes(self):
        return self.duration_bytes - self.position_bytes

    @property
    def remaining_time(self):
        seconds = int(self.remaining_seconds % 60)
        minutes = int(self.remaining_seconds // 60)
        return f"{minutes:02}:{seconds:02}"

    @property
    def handle(self) -> HANDLE:
        if self._handle is NULL:
            self._create_stream()
        return self._handle

    @handle.deleter
    def handle(self):
        self.free_stream()

    @property
    def playing(self):
        return BassChannel.is_playing(self.handle)

    @property
    def paused(self):
        return BassChannel.is_paused(self.handle)

    @property
    def stopped(self):
        return BassChannel.is_stopped(self.handle)

    def set_position_seconds(self, seconds: float) -> bool:
        ok = BassChannel.set_position_by_seconds(self.handle, seconds)
        if not ok:
            Bass.may_raise_error()
        return ok

    def set_position_bytes(self, bytes_: int) -> None:
        ok = BassChannel.set_position_by_bytes(self.handle, bytes_)
        if not ok:
            Bass.may_raise_error()

    def play(self):
        ok = BassChannel.play(self.handle, restart=False)
        if not ok:
            Bass.may_raise_error()

    def stop(self):
        ok = BassChannel.stop(self.handle)
        if not ok:
            Bass.may_raise_error()

    def pause(self):
        ok = BassChannel.pause(self.handle)
        if not ok:
            Bass.may_raise_error()

    def resume(self):
        ok = BassChannel.pause(self.handle)
        if not ok:
            Bass.may_raise_error()

    def __hash__(self):
        return hash(self.file_path)

    def __repr__(self):
        return f"<{type(self).__name__} {self.file_path=!r}>"

    def _create_handle(self) -> HANDLE:
        return BassStream.create_from_file(self.file_path)


class _MusicChannel:
    music_handle: HMusic
    channel_num: int

    def __init__(self, handle: HMusic, num: int):
        self.music_handle = handle
        self.channel_num = num

    @property
    def volume(self):
        return BassMusic.get_channel_volume(self.music_handle, self.channel_num)

    @volume.setter
    def volume(self, new: float):
        ok = BassMusic.set_channel_volume(self.music_handle, self.channel_num, new)
        if not ok:
            Bass.may_raise_error(f'Setting volume of channel {self.channel_num}, handle {self.music_handle} to {new}')


class _MusicInstrument:
    def __init__(self, handle: HMusic, pos: int):
        self.music_handle = handle
        self.instrument_num = pos

    @property
    def volume(self):
        return BassMusic.get_instrument_volume(self.music_handle, self.instrument_num)

    @volume.setter
    def volume(self, new: float):
        ok = BassMusic.set_instrument_volume(self.music_handle, self.instrument_num, new)
        if not ok:
            Bass.may_raise_error(f'Setting volume of instrument {self.instrument_num}, '
                                 f'handle {self.music_handle} to {new}')


class Music(Song):
    _handle: HMusic

    def _create_handle(self) -> HANDLE:
        return BassMusic.load_from_file(self.file_path)

    def _free_handle(self):
        return BassMusic.free(self._handle)

    def instrument(self, pos: int):
        return _MusicInstrument(self.handle, pos)

    def instruments(self) -> list[_MusicInstrument]:
        res: list[_MusicInstrument] = []
        index = 0
        dummy = c_float()
        while BASS_ChannelGetAttribute(self.handle, MusicAttrib.VOL_INST.value + index, byref(dummy)):
            res.append(_MusicInstrument(self._handle, index))
            index += 1
        return res

    def set_pos(self, patten_num: int, row: int = 0):
        if not BassMusic.set_position(self.handle, patten_num, row):
            Bass.may_raise_error(f'set position of music {self.handle} to {patten_num=}, {row=}')

    def __getitem__(self, item: int):
        return _MusicChannel(self.handle, item)

    def __iter__(self):
        res: list[_MusicChannel] = []
        index = 0
        dummy = c_float()
        while BASS_ChannelGetAttribute(self.handle, MusicAttrib.VOL_CHAN.value + index, byref(dummy)):
            res.append(_MusicChannel(self._handle, index))
            index += 1
        return iter(res)

    def __len__(self):
        index = 0
        dummy = c_float()
        while BASS_ChannelGetAttribute(self.handle, MusicAttrib.VOL_CHAN.value + index, byref(dummy)):
            index += 1
        return index


class SoundEffect:
    _handle: HANDLE
    file_path: Path

    def __init__(self, file_path: Path):
        # assert file_path.is_file()
        self.file_path = file_path
        self._handle = NULL

    def _create_stream(self):
        if not self.file_path.is_file():
            return
        self._handle = BassStream.create_from_file(self.file_path)
        Bass.may_raise_error(f'{self.file_path=}')

    def free_stream(self, direct_stop: bool = False) -> None:
        if self._handle is NULL:
            return
        if self.playing:
            if direct_stop:
                BassChannel.stop(self._handle)
            else:
                self.stop()
        ok = BassStream.free(self._handle)
        if not ok:
            Bass.may_raise_error()
        self._handle = NULL

    def touch(self) -> None:
        self._create_stream()
        self.free_stream()

    @property
    def handle(self) -> HANDLE:
        if self._handle is NULL:
            self._create_stream()
        return self._handle

    @handle.deleter
    def handle(self):
        self.free_stream()

    def __len__(self):
        if self.handle is NULL:
            raise ValueError('handle is NULL')
        return BassChannel.get_length_bytes(self.handle)

    @property
    def playing(self):
        return BassChannel.is_playing(self.handle)

    @property
    def stopped(self):
        return BassChannel.is_stopped(self.handle)

    def play(self, restart: bool = True):
        if self.handle is NULL:
            return
        ok = BassChannel.play(self.handle, restart)
        if not ok:
            Bass.may_raise_error()

    def stop(self):
        ok = BassChannel.stop(self.handle)
        if not ok:
            Bass.may_raise_error()

    def __hash__(self):
        return hash(self.file_path)

    def __repr__(self):
        return f"{type(self).__name__}({self.file_path})"
