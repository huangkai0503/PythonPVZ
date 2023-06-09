from typing import Final
from enum import Enum, Flag

BASS_TRUE: Final = 1
BASS_FALSE: Final = 0
BASS_VERSION: Final = 0x204  # API version
BASS_VERSION_TEXT: Final = "2.4"
BASS_DEVICES_AIRPLAY: Final = 0x1000000
BASS_ASYNCFILE: Final = 0x40000000
BASS_UNICODE: Final = 0x80000000
BASS_ORIGRES_FLOAT: Final = 0x10000
BASS_FILEDATA_END: Final = 0  # end & close the file
BASS_SLIDE_LOG: Final = 0x1000000
BASS_NODEVICE: Final = 0x20000


def LOBYTE(a: int) -> int: return a & 0xff
def HIBYTE(a: int) -> int: return (a >> 8) & 0xff
def LOWORD(a: int) -> int: return a & 0xffff
def HIWORD(a: int) -> int: return (a >> 16) & 0xffff
def MAKEWORD(low: int, high: int) -> int: return (low & 0xff) | (high << 8)
def MAKELONG(low: int, high: int) -> int: return (low & 0xffff) | (high << 16)


class Error(Enum):
    OK: Final = 0  # all is OK
    MEM = 1  # memory error
    FILEOPEN = 2  # can't open the file
    DRIVER = 3  # can't find a free/valid driver
    BUFLOST = 4  # the sample buffer was lost
    HANDLE = 5  # invalid handle
    FORMAT = 6  # unsupported sample format
    POSITION = 7  # invalid position
    INIT = 8  # BASS_Init has not been successfully called
    START = 9  # BASS_Start has not been successfully called
    SSL = 10  # SSL/HTTPS support isn't available
    ALREADY = 14  # already initialized/paused/whatever
    NOTAUDIO = 17  # file does not contain audio
    NOCHAN = 18  # can't get a free channel
    ILLTYPE = 19  # an illegal type was specified
    ILLPARAM = 20  # an illegal parameter was specified
    NO3D = 21  # no 3D support
    NOEAX = 22  # no EAX support
    DEVICE = 23  # illegal device number
    NOPLAY = 24  # not playing
    FREQ = 25  # illegal sample rate
    NOTFILE = 27  # the stream is not a file stream
    NOHW = 29  # no hardware voices available
    EMPTY = 31  # the MOD music has no sequence data
    NONET = 32  # no internet connection could be opened
    CREATE = 33  # couldn't create the file
    NOFX = 34  # effects are not available
    NOTAVAIL = 37  # requested data/action is not available
    DECODE = 38  # the channel is/isn't a "decoding channel"
    DX = 39  # a sufficient DirectX version is not installed
    TIMEOUT = 40  # connection timedout
    FILEFORM = 41  # unsupported file format
    SPEAKER = 42  # unavailable speaker
    VERSION = 43  # invalid BASS version (used by add-ons)
    CODEC = 44  # codec is not available/supported
    ENDED = 45  # the channel/file has ended
    BUSY = 46  # the device is busy
    UNSTREAMABLE = 47  # unstreamable file
    UNKNOWN = -1  # some other mystery problem

    def __eq__(self, other: 'Error | int'):
        if isinstance(other, int):
            return self.value == other
        return self.value == other.value


class Config(Enum):
    BUFFER = 0
    UPDATEPERIOD = 1
    GVOL_SAMPLE = 4
    GVOL_STREAM = 5
    GVOL_MUSIC = 6
    CURVE_VOL = 7
    CURVE_PAN = 8
    FLOATDSP = 9
    THREE_DALGORITHM = 10
    NET_TIMEOUT = 11
    NET_BUFFER = 12
    PAUSE_NOPLAY = 13
    NET_PREBUF = 15
    NET_PASSIVE = 18
    REC_BUFFER = 19
    NET_PLAYLIST = 21
    MUSIC_VIRTUAL = 22
    VERIFY = 23
    UPDATETHREADS = 24
    DEV_BUFFER = 27
    REC_LOOPBACK = 28
    VISTA_TRUEPOS = 30
    IOS_SESSION = 34
    IOS_MIXAUDIO = 34
    DEV_DEFAULT = 36
    NET_READTIMEOUT = 37
    VISTA_SPEAKERS = 38
    IOS_SPEAKER = 39
    MF_DISABLE = 40
    HANDLES = 41
    UNICODE = 42
    SRC = 43
    SRC_SAMPLE = 44
    ASYNCFILE_BUFFER = 45
    OGG_PRESCAN = 47
    MF_VIDEO = 48
    AIRPLAY = 49
    DEV_NONSTOP = 50
    IOS_NOCATEGORY = 51
    VERIFY_NET = 52
    DEV_PERIOD = 53
    FLOAT = 54
    NET_SEEK = 56
    AM_DISABLE = 58
    NET_PLAYLIST_DEPTH = 59
    NET_PREBUF_WAIT = 60
    ANDROID_SESSIONID = 62
    WASAPI_PERSIST = 65
    REC_WASAPI = 66
    ANDROID_AAUDIO = 67
    NET_AGENT = 16
    NET_PROXY = 17
    IOS_NOTIFY = 46
    LIBSSL = 64


class IosSession(Enum):
    MIX = 1
    DUCK = 2
    AMBIENT = 4
    SPEAKER = 8
    DISABLE = 16


class Device(Flag):
    BITS8 = 1  # 8 bit
    MONO = 2  # mono
    THREE_D = 4  # enable 3D functionality
    BITS16 = 8  # limit output to 16 bit
    LATENCY = 0x100  # calculate device latency (BASS_INFO struct)
    CPSPEAKERS = 0x400  # detect speakers via Windows control panel
    SPEAKERS = 0x800  # force enabling of speaker assignment
    NOSPEAKER = 0x1000  # ignore speaker arrangement
    DMIX = 0x2000  # use ALSA "dmix" plugin
    FREQ = 0x4000  # set device sample rate
    STEREO = 0x8000  # limit output to stereo
    HOG = 0x10000  # hog/exclusive mode
    AUDIOTRACK = 0x20000  # use AudioTrack output
    DSOUND = 0x40000  # use DirectSound output
    ENABLED = 1
    DEFAULT = 2
    INIT = 4
    LOOPBACK = 8
    TYPE_MASK = 0xff000000
    TYPE_NETWORK = 0x01000000
    TYPE_SPEAKERS = 0x02000000
    TYPE_LINE = 0x03000000
    TYPE_HEADPHONES = 0x04000000
    TYPE_MICROPHONE = 0x05000000
    TYPE_HEADSET = 0x06000000
    TYPE_HANDSET = 0x07000000
    TYPE_DIGITAL = 0x08000000
    TYPE_SPDIF = 0x09000000
    TYPE_HDMI = 0x0a000000
    TYPE_DISPLAYPORT = 0x40000000


class Object(Enum):
    DS = 1  # IDirectSound
    DS3DL = 2  # IDirectSound3DListener


class Dscaps(Flag):
    CONTINUOUSRATE = 0x00000010  # supports all sample rates between min/maxrate
    EMULDRIVER = 0x00000020  # device does NOT have hardware DirectSound support
    CERTIFIED = 0x00000040  # device driver has been certified by Microsoft
    SECONDARYMONO = 0x00000100  # mono
    SECONDARYSTEREO = 0x00000200  # stereo
    SECONDARY8BIT = 0x00000400  # 8 bit
    SECONDARY16BIT = 0x00000800  # 16 bit


class Dsccaps(Enum):
    EMULDRIVER = Dscaps.EMULDRIVER  # device does NOT have hardware DirectSound recording support
    CERTIFIED = Dscaps.CERTIFIED  # device driver has been certified by Microsoft


class SampleFlags(Flag):
    BITS8 = 1  # 8 bit
    FLOAT = 256  # 32 bit floating-point
    MONO = 2  # mono
    LOOP = 4  # looped
    THREE_D = 8  # 3D functionality
    SOFTWARE = 16  # not using hardware mixing
    MUTEMAX = 32  # mute at max distance (3D only)
    VAM = 64  # DX7 voice allocation & management
    FX = 128  # old implementation of DX8 effects
    OVER_VOL = 0x10000  # override lowest volume
    OVER_POS = 0x20000  # override longest playing
    OVER_DIST = 0x30000  # override furthest from listener (3D only)


class Stream(Flag):
    PRESCAN = 0x20000  # enable pin-point seeking/length (MP3/MP2/MP1)
    AUTOFREE = 0x40000  # automatically free the stream when it stop/ends
    RESTRATE = 0x80000  # restrict the download rate of internet file streams
    BLOCK = 0x100000  # download/play internet file stream in small blocks
    DECODE = 0x200000  # don't play the stream, only decode (BASS_ChannelGetData)
    STATUS = 0x800000  # give server status info (HTTP/ICY tags) in DOWNLOADPROC


class Mp3(Enum):
    IGNOREDELAY = 0x200  # ignore LAME/Xing/VBRI/iTunes delay & padding info
    SETPOS = Stream.PRESCAN


class Music(Flag):
    FLOAT = SampleFlags.FLOAT
    MONO = SampleFlags.MONO
    LOOP = SampleFlags.LOOP
    THREE_D = SampleFlags.THREE_D
    FX = SampleFlags.FX
    AUTOFREE = Stream.AUTOFREE
    DECODE = Stream.DECODE
    PRESCAN = Stream.PRESCAN  # calculate playback length
    CALCLEN = PRESCAN
    RAMP = 0x200  # normal ramping
    RAMPS = 0x400  # sensitive ramping
    SURROUND = 0x800  # surround sound
    SURROUND2 = 0x1000  # surround sound (mode 2)
    FT2PAN = 0x2000  # apply FastTracker 2 panning to XM files
    FT2MOD = 0x2000  # play .MOD as FastTracker 2 does
    PT1MOD = 0x4000  # play .MOD as ProTracker 1 does
    NONINTER = 0x10000  # non-interpolated sample mixing
    SINCINTER = 0x800000  # sinc interpolated sample mixing
    POSRESET = 0x8000  # stop all notes when moving position
    POSRESETEX = 0x400000  # stop all notes and reset bmp/etc when moving position
    STOPBACK = 0x80000  # stop the music on a backwards jump effect
    NOSAMPLE = 0x100000  # don't load the samples

    NONE = 0


class Speaker(Flag):
    FRONT = 0x1000000  # front speakers
    REAR = 0x2000000  # rear/side speakers
    CENLFE = 0x3000000  # center & LFE speakers (5.1)
    REAR2 = 0x4000000  # rear center speakers (7.1)
    LEFT = 0x10000000  # modifier: left
    RIGHT = 0x20000000  # modifier: right
    FRONTLEFT = FRONT | LEFT
    FRONTRIGHT = FRONT | RIGHT
    REARLEFT = REAR | LEFT
    REARRIGHT = REAR | RIGHT
    CENTER = CENLFE | LEFT
    LFE = CENLFE | RIGHT
    REAR2LEFT = REAR2 | LEFT
    REAR2RIGHT = REAR2 | RIGHT


class Record(Flag):
    PAUSE = 0x8000  # start recording paused
    ECHOCANCEL = 0x2000
    AGC = 0x4000


class Vam(Enum):
    HARDWARE = 1
    SOFTWARE = 2
    TERM_TIME = 4
    TERM_DIST = 8
    TERM_PRIO = 16


class Ctype(Flag):
    SAMPLE = 1
    RECORD = 2
    STREAM = 0x10000
    STREAM_VORBIS = 0x10002
    STREAM_OGG = 0x10002
    STREAM_MP1 = 0x10003
    STREAM_MP2 = 0x10004
    STREAM_MP3 = 0x10005
    STREAM_AIFF = 0x10006
    STREAM_CA = 0x10007
    STREAM_MF = 0x10008
    STREAM_AM = 0x10009
    STREAM_DUMMY = 0x18000
    STREAM_DEVICE = 0x18001
    STREAM_WAV = 0x40000  # WAVE flag, LOWORD=codec
    STREAM_WAV_PCM = 0x50001
    STREAM_WAV_FLOAT = 0x50003
    MUSIC_MOD = 0x20000
    MUSIC_MTM = 0x20001
    MUSIC_S3M = 0x20002
    MUSIC_XM = 0x20003
    MUSIC_IT = 0x20004
    MUSIC_MO3 = 0x00100  # MO3 flag


class ThreeDdmode3dmode(Enum):
    NORMAL = 0  # normal 3D processing
    RELATIVE = 1  # position is relative to the listener
    OFF = 2  # no 3D processing


class ThreeDdalg3dalg(Enum):
    DEFAULT = 0
    OFF = 1
    FULL = 2
    LIGHT = 3


class Streamproc(Enum):
    END = 0x80000000  # end of user stream flag
    DUMMY = 0  # "dummy" stream
    PUSH = -1  # push stream
    DEVICE = -2  # device mix stream
    DEVICE_3D = -3  # device 3D mix stream


class Streamfile(Enum):
    NOBUFFER = 0
    BUFFER = 1
    BUFFERPUSH = 2


class Filepos(Enum):
    CURRENT = 0
    DECODE = CURRENT
    DOWNLOAD = 1
    END = 2
    START = 3
    CONNECTED = 4
    BUFFER = 5
    SOCKET = 6
    ASYNCBUF = 7
    SIZE = 8
    BUFFERING = 9


class Sync(Flag):
    POS = 0
    END = 2
    META = 4
    SLIDE = 5
    STALL = 6
    DOWNLOAD = 7
    FREE = 8
    SETPOS = 11
    MUSICPOS = 10
    MUSICINST = 1
    MUSICFX = 3
    OGG_CHANGE = 12
    DEV_FAIL = 14
    DEV_FORMAT = 15
    THREAD = 0x20000000  # flag: call sync in other thread
    MIXTIME = 0x40000000  # flag: sync at mixtime, else at playtime
    ONETIME = 0x80000000  # flag: sync only once, else continuously


class Active(Enum):
    STOPPED = 0
    PLAYING = 1
    STALLED = 2
    PAUSED = 3
    PAUSED_DEVICE = 4


class Attrib(Enum):
    FREQ = 1
    VOL = 2
    PAN = 3  # 相位
    EAXMIX = 4
    NOBUFFER = 5
    VBR = 6
    CPU = 7
    SRC = 8
    NET_RESUME = 9
    SCANINFO = 10
    NORAMP = 11
    BITRATE = 12
    BUFFER = 13
    GRANULE = 14


class MusicAttrib(Enum):
    AMPLIFY = 0x100
    PANSEP = 0x101
    PSCALER = 0x102
    BPM = 0x103
    SPEED = 0x104
    VOL_GLOBAL = 0x105
    ACTIVE = 0x106
    VOL_CHAN = 0x200  # + channel #
    VOL_INST = 0x300  # + instrument #


class Data(Flag):
    AVAILABLE = 0  # query how much data is buffered
    FIXED = 0x20000000  # flag: return 8.24 fixed-point data
    FLOAT = 0x40000000  # flag: return floating-point sample data
    FFT256 = 0x80000000  # 256 sample FFT
    FFT512 = 0x80000001  # 512 FFT
    FFT1024 = 0x80000002  # 1024 FFT
    FFT2048 = 0x80000003  # 2048 FFT
    FFT4096 = 0x80000004  # 4096 FFT
    FFT8192 = 0x80000005  # 8192 FFT
    FFT16384 = 0x80000006  # 16384 FFT
    FFT32768 = 0x80000007  # 32768 FFT
    FFT_INDIVIDUAL = 0x10  # FFT flag: FFT for each channel, else all combined
    FFT_NOWINDOW = 0x20  # FFT flag: no Hanning window
    FFT_REMOVEDC = 0x40  # FFT flag: pre-remove DC bias
    FFT_COMPLEX = 0x80  # FFT flag: return complex data
    FFT_NYQUIST = 0x100  # FFT flag: return extra Nyquist value


class Level(Enum):
    MONO = 1
    STEREO = 2
    RMS = 4
    VOLPAN = 8


class Tag(Flag):
    ID3 = 0  # ID3v1 tags : TAG_ID3 structure
    ID3V2 = 1  # ID3v2 tags : variable length block
    OGG = 2  # OGG comments : series of null-terminated UTF-8 strings
    HTTP = 3  # HTTP headers : series of null-terminated ANSI strings
    ICY = 4  # ICY headers : series of null-terminated ANSI strings
    META = 5  # ICY metadata : ANSI string
    APE = 6  # APE tags : series of null-terminated UTF-8 strings
    MP4 = 7  # MP4/iTunes metadata : series of null-terminated UTF-8 strings
    WMA = 8  # WMA tags : series of null-terminated UTF-8 strings
    VENDOR = 9  # OGG encoder : UTF-8 string
    LYRICS3 = 10  # Lyric3v2 tag : ASCII string
    CA_CODEC = 11  # CoreAudio codec info : TAG_CA_CODEC structure
    MF = 13  # Media Foundation tags : series of null-terminated UTF-8 strings
    WAVEFORMAT = 14  # WAVE format : WAVEFORMATEEX structure
    AM_MIME = 15  # Android Media MIME type : ASCII string
    AM_NAME = 16  # Android Media codec name : ASCII string
    RIFF_INFO = 0x100  # RIFF "INFO" tags : series of null-terminated ANSI strings
    RIFF_BEXT = 0x101  # RIFF/BWF "bext" tags : TAG_BEXT structure
    RIFF_CART = 0x102  # RIFF/BWF "cart" tags : TAG_CART structure
    RIFF_DISP = 0x103  # RIFF "DISP" text tag : ANSI string
    RIFF_CUE = 0x104  # RIFF "cue " chunk : TAG_CUE structure
    RIFF_SMPL = 0x105  # RIFF "smpl" chunk : TAG_SMPL structure
    APE_BINARY = 0x1000  # + index #, binary APE tag : TAG_APE_BINARY structure
    MUSIC_NAME = 0x10000  # MOD music name : ANSI string
    MUSIC_MESSAGE = 0x10001  # MOD message : ANSI string
    MUSIC_ORDERS = 0x10002  # MOD order list : BYTE array of pattern numbers
    MUSIC_AUTH = 0x10003  # MOD author : UTF-8 string
    MUSIC_INST = 0x10100  # + instrument #, MOD instrument name : ANSI string
    MUSIC_SAMPLE = 0x10300  # + sample #, MOD sample name : ANSI string


class Pos(Flag):
    BYTE = 0  # byte position
    MUSIC_ORDER = 1  # order.row position, MAKELONG(order,row)
    OGG = 3  # OGG bitstream number
    RESET = 0x2000000  # flag: reset user file buffers
    RELATIVE = 0x4000000  # flag: seek relative to the current position
    INEXACT = 0x8000000  # flag: allow seeking to inexact position
    DECODE = 0x10000000  # flag: get the decoding (not playing) position
    DECODETO = 0x20000000  # flag: decode to the position instead of seeking
    SCAN = 0x40000000  # flag: scan to the position


class Input(Flag):
    OFF = 0x10000
    ON = 0x20000
    TYPE_MASK = 0xff000000
    TYPE_UNDEF = 0x00000000
    TYPE_DIGITAL = 0x01000000
    TYPE_LINE = 0x02000000
    TYPE_MIC = 0x03000000
    TYPE_SYNTH = 0x04000000
    TYPE_CD = 0x05000000
    TYPE_PHONE = 0x06000000
    TYPE_SPEAKER = 0x07000000
    TYPE_WAVE = 0x08000000
    TYPE_AUX = 0x09000000
    TYPE_ANALOG = 0x0a000000


class Fx(Enum):
    DX8_CHORUS = 0
    DX8_COMPRESSOR = 1
    DX8_DISTORTION = 2
    DX8_ECHO = 3
    DX8_FLANGER = 4
    DX8_GARGLE = 5
    DX8_I3DL2REVERB = 6
    DX8_PARAMEQ = 7
    DX8_REVERB = 8
    VOLUME = 9


class Dx8Phase(Enum):
    NEG_180 = 0
    NEG_90 = 1
    ZERO = 2
    P90 = 3
    P180 = 4
