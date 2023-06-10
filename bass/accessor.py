from ctypes import Structure, POINTER, c_ulong, c_ushort, c_ubyte, byref, c_float
from ctypes.wintypes import HWND
from pathlib import Path

from bass.constants import Pos, Active, Tag, Error, Config, Device, Music as MusicFlags, Attrib, SampleFlags, \
    MusicAttrib, MAKELONG
from bass.bass_types import HANDLE, func_type, TAG_ID3, bass_module, HMusic, NULL, Info, DeviceInfo
from bass.functions import BASS_ChannelPlay, BASS_ChannelStop, BASS_ChannelPause, BASS_ChannelIsActive, \
    BASS_ChannelGetPosition, BASS_ChannelBytes2Seconds, BASS_ChannelSetPosition, BASS_ChannelSeconds2Bytes, \
    BASS_ChannelGetLength, BASS_StreamCreateFile, BASS_StreamFree, BASS_ErrorGetCode, BASS_Init, BASS_Free, \
    BASS_GetCPU, BASS_GetVolume, BASS_SetVolume, BASS_SetConfig, BASS_GetConfig, BASS_GetVersion, BASS_GetInfo, \
    BASS_GetDevice, BASS_SetDevice, BASS_GetDeviceInfo, BASS_Pause, BASS_Start, BASS_Stop, BASS_MusicLoad, \
    BASS_MusicFree, BASS_ChannelSetAttribute, BASS_ChannelGetAttribute, BASS_ChannelFlags

P_TAG_ID3 = POINTER(TAG_ID3)
BASS_ChannelGetTagsID3v1 = func_type(P_TAG_ID3, HANDLE, c_ulong)(("BASS_ChannelGetTags", bass_module))


class GUID(Structure):
    _fields_ = [
        ('Data1', c_ulong),
        ('Data2', c_ushort),
        ('Data3', c_ushort),
        ('Data4', c_ubyte * 8),
    ]


LPGUID = POINTER(GUID)


class BassStream:
    DEBUG_BASS_STREAM = False
    DEBUG_OPEN_HANDLES = []

    @classmethod
    def create_file(cls, file: bytes, offset: int = 0, length: int = 0, flags: int = 0, mem: bool = False):
        handle = BASS_StreamCreateFile(mem, file, offset, length, flags)
        if handle == 0:
            Bass.may_raise_error(f'StreamCreateFile: file={file!r}')
        if cls.DEBUG_BASS_STREAM:
            cls.DEBUG_OPEN_HANDLES.append(handle)
        return handle

    @classmethod
    def create_from_file(cls, path: Path):
        return cls.create_file(_encode_path(path))

    @classmethod
    def free(cls, stream: HANDLE) -> bool:
        ok = BASS_StreamFree(stream)
        if cls.DEBUG_BASS_STREAM:
            cls.DEBUG_OPEN_HANDLES.remove(stream)
        return ok

    @classmethod
    def create_file_from_buffer(cls, buffer: bytes):
        return cls.create_file(buffer, mem=False)


class BassChannel:
    @classmethod
    def play(cls, stream_handle: HANDLE, restart: bool = False) -> bool:
        return BASS_ChannelPlay(stream_handle, restart)

    @classmethod
    def stop(cls, stream_handle: HANDLE) -> bool:
        return BASS_ChannelStop(stream_handle)

    @classmethod
    def pause(cls, stream_handle: HANDLE) -> bool:
        status = cls.is_active(stream_handle)
        if status == Active.PAUSED:
            return cls.play(stream_handle)
        else:
            return BASS_ChannelPause(stream_handle)

    @classmethod
    def resume(cls, stream_handle: HANDLE) -> bool:
        return cls.play(stream_handle)

    @classmethod
    def is_active(cls, stream_handle: HANDLE) -> int:
        return BASS_ChannelIsActive(stream_handle)

    @classmethod
    def is_playing(cls, stream_handle: HANDLE) -> bool:
        retval = cls.is_active(stream_handle)
        return retval == Active.PLAYING.value

    @classmethod
    def is_paused(cls, stream_handle: HANDLE) -> bool:
        retval = cls.is_active(stream_handle)
        return retval == Active.PAUSED.value

    @classmethod
    def is_stopped(cls, stream_handle: HANDLE) -> bool:
        retval = cls.is_active(stream_handle)
        return retval == Active.STOPPED.value

    @classmethod
    def get_position_bytes(cls, stream_handle: HANDLE) -> int:
        return BASS_ChannelGetPosition(stream_handle, Pos.BYTE.value)

    @classmethod
    def get_position_seconds(cls, stream_handle: HANDLE) -> int:
        stream_bytes = cls.get_position_bytes(stream_handle)
        return BASS_ChannelBytes2Seconds(stream_handle, stream_bytes)

    @classmethod
    def set_position_by_seconds(cls, handle: HANDLE, seconds: float) -> bool:
        stream_bytes = BASS_ChannelSeconds2Bytes(handle, seconds)
        return bool(BASS_ChannelSetPosition(handle, stream_bytes, Pos.BYTE))

    @classmethod
    def set_position_by_bytes(cls, handle: HANDLE, bytes_: int) -> bool:
        return BASS_ChannelSetPosition(handle, bytes_, Pos.BYTE.value)

    @classmethod
    def get_length_seconds(cls, stream_handle: HANDLE, stream_bytes: int | None = None) -> float:
        if stream_bytes is NULL:
            stream_bytes = cls.get_length_bytes(stream_handle)
        return BASS_ChannelBytes2Seconds(stream_handle, stream_bytes)

    @classmethod
    def get_length_str(cls, stream_handle: HANDLE) -> str:
        value = cls.get_length_seconds(stream_handle)
        seconds = int(value % 60)
        minutes = int(value / 60)
        return f'{minutes:02}:{seconds:02}'

    @classmethod
    def get_position_str(cls, stream_handle: HANDLE) -> str:
        value = cls.get_position_seconds(stream_handle)
        seconds = int(value % 60)
        minutes = int(value / 60)
        return f"{minutes:02}:{seconds:02}"

    @classmethod
    def get_length_bytes(cls, stream_handle: HANDLE) -> int:
        return BASS_ChannelGetLength(stream_handle, Pos.BYTE.value)

    @classmethod
    def get_id3v1_tags(cls, stream_handle: HANDLE) -> P_TAG_ID3:
        return BASS_ChannelGetTagsID3v1(stream_handle, Tag.ID3.value)

    @classmethod
    def set_attribute(cls, handle: HANDLE, attrib: Attrib | int, value: float) -> bool:
        if isinstance(attrib, Attrib):
            attrib = attrib.value
        return bool(BASS_ChannelSetAttribute(handle, attrib, value))

    @classmethod
    def get_attribute(cls, handle: HANDLE, attrib: Attrib) -> float:
        res = c_float()
        ok = BASS_ChannelGetAttribute(handle, attrib, byref(res))
        if not ok:
            Bass.may_raise_error()
        return res.value

    @classmethod
    def flags(cls, handle: HANDLE, flags: SampleFlags, mask: SampleFlags) -> int:
        return BASS_ChannelFlags(handle, flags.value, mask)


class BassError:
    code: Error

    def __init__(self, code: int, desc: str | None = None):
        self.code = Error(code)
        self.desc = desc


class BassException(Exception):
    def __init__(self, code: Error, desc: str | None = None, detail: str | None = None):
        self.code = code
        self.desc = desc
        self.detail = detail

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        res = f'{self.code}'
        if self.desc is not None:
            res += f': {self.desc}'
        if self.detail is not None:
            res += f' - {self.detail=}'
        return res


class BassMusic:
    @classmethod
    def load(cls, mem: bool, file: bytes, offset: int = 0, length: int = 0, flags: MusicFlags = MusicFlags(0),
             freq: int = 44100) -> HMusic:
        return BASS_MusicLoad(mem, file, offset, length, flags.value, freq)

    @classmethod
    def free(cls, handle: HMusic) -> bool:
        return bool(BASS_MusicFree(handle))

    @classmethod
    def load_from_file(cls, path: Path):
        return cls.load(False, _encode_path(path))

    @classmethod
    def load_from_buffer(cls, buffer: bytes):
        return cls.load(True, buffer)

    @classmethod
    def set_channel_volume(cls, handle: HMusic, channel: int, volume: float) -> bool:
        return BassChannel.set_attribute(handle, MusicAttrib.VOL_CHAN.value + channel, volume)

    @classmethod
    def get_channel_volume(cls, handle: HMusic, channel: int) -> float:
        return BassChannel.get_attribute(handle, MusicAttrib.VOL_CHAN.value + channel)

    @classmethod
    def get_instrument_volume(cls, handle: HMusic, instrument_num: int) -> float:
        return BassChannel.get_attribute(handle, MusicAttrib.VOL_INST.value + instrument_num)

    @classmethod
    def set_instrument_volume(cls, handle: HANDLE, instrument_num: int, volume: float) -> bool:
        return BassChannel.set_attribute(handle, MusicAttrib.VOL_INST.value + instrument_num, volume)

    @classmethod
    def set_position(cls, handle: HANDLE, pattern_num: int, row: int = 0) -> bool:
        return BASS_ChannelSetPosition(handle, MAKELONG(pattern_num, row), Pos.MUSIC_ORDER.value)


class DeviceMissingError(Exception):
    def __init__(self, device_id: int):
        self.device_id = device_id

    def __repr__(self):
        return f"{self.device_id} device doesn't exist"


class Bass:
    LIB_INITED = False
    LAST_ERROR = None

    @classmethod
    def get_error(cls) -> BassError:
        code = BASS_ErrorGetCode()
        return BassError(code)

    @classmethod
    def may_raise_error(cls, detail: str | None = None) -> None:
        error = cls.get_error()
        if error.code != Error.OK:
            raise BassException(error.code, error.desc, detail)

    @classmethod
    def init(cls, device: int = -1, freq: int = 44100, flags: Device = Device(0), win: HWND = 0, clsid: LPGUID = 0,
             enable_ogg_prescan: bool = True) -> bool:
        """
        device: -1 = 默认
        win: 应用程序的主窗口，NULL 表示桌面。这只在使用直接声音输出时有效。
        clsid: 要创建的对象的类标识符，会被用于初始化 DirectSound。None/NULL == 默认.
        enable_ogg_prescan: 如果为 True（默认），这个函数会预扫描 ogg 文件，使它们能够被重定位。
                            否则重定位 ogg 文件会重置到位置 0。
        """
        if cls.LIB_INITED:
            return True

        ok = BASS_Init(device, freq, flags.value, win, clsid)
        if not ok:
            cls.may_raise_error()
            return False

        cls.LIB_INITED = True
        if enable_ogg_prescan:
            ok = Bass.set_config(Config.OGG_PRESCAN, True)
            if not ok:
                cls.may_raise_error()
                return False
        return True

    @classmethod
    def free(cls):
        ok = BASS_Free()
        if not ok:
            cls.may_raise_error()
        cls.LIB_INITED = False

    @classmethod
    def get_cpu(cls) -> float:
        return BASS_GetCPU()

    @classmethod
    def get_volume_level(cls) -> float:
        return BASS_GetVolume()

    @classmethod
    def set_volume_level(cls, level: float) -> bool:
        return BASS_SetVolume(level)

    @classmethod
    def get_volume_perc(cls) -> float:
        volume = cls.get_volume_level()
        return 100 * volume

    @classmethod
    def set_volume_perc(cls, perc: float) -> bool:
        assert perc >= 0
        assert perc <= 100
        volume = perc / 100
        return cls.set_volume_level(volume)

    @classmethod
    def set_config(cls, config_flag: Config, value: int) -> bool:
        return BASS_SetConfig(config_flag.value, value)

    @classmethod
    def get_config(cls, config_flag: Config) -> int:
        return BASS_GetConfig(config_flag.value)

    @classmethod
    def enable_ogg_prescan(cls) -> bool:
        return cls.set_config(Config.OGG_PRESCAN, True)

    @classmethod
    def get_version(cls) -> int:
        return BASS_GetVersion()

    @classmethod
    def get_lib_info(cls) -> Info:
        bi = Info()
        ok = BASS_GetInfo(byref(bi))
        if not ok:
            cls.may_raise_error()
        return bi

    @classmethod
    def get_device_id(cls) -> c_ulong:
        return BASS_GetDevice()

    @classmethod
    def set_current_device(cls, device_id: int) -> bool:
        return BASS_SetDevice(device_id)

    @classmethod
    def get_device_info(cls, device_id: int = None) -> DeviceInfo:
        if device_id is None:
            device_id = cls.get_device_id()
        bd = DeviceInfo()
        ok = BASS_GetDeviceInfo(device_id, byref(bd))
        if not ok:
            cls.may_raise_error()
        return bd

    @classmethod
    def pause(cls) -> bool:
        return BASS_Pause()

    @classmethod
    def start(cls) -> bool:
        return BASS_Start()

    @classmethod
    def stop(cls) -> bool:
        return BASS_Stop()


def _encode_path(path: Path):
    import locale
    return path.as_posix().encode(locale.getpreferredencoding())
