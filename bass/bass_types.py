import platform
from ctypes import POINTER, Structure, c_byte, c_int, c_float, c_void_p, c_char_p, c_uint64
from ctypes.wintypes import BYTE, WORD, DWORD, BOOL
from pathlib import Path

HANDLE = DWORD
NULL = HANDLE()

lib = Path(__file__).parent / 'lib' / ('x64' if platform.machine().endswith('64') else 'x86')

if platform.system().lower() == 'windows':
    from ctypes import WinDLL, WINFUNCTYPE
    bass_module = WinDLL((lib / 'bass.dll').as_posix())
    tags_module = WinDLL((lib / 'tags.dll').as_posix())
    func_type = WINFUNCTYPE
else:
    from ctypes import CDLL, CFUNCTYPE, RTLD_GLOBAL
    bass_module = CDLL((lib / 'libbass.so').as_posix(), mode=RTLD_GLOBAL)
    tags_module = CDLL((lib / 'libtags.so').as_posix(), mode=RTLD_GLOBAL)
    func_type = CFUNCTYPE

QWORD = c_uint64

HMusic = DWORD  # MOD music handle
HSample = DWORD  # sample handle
HChannel = DWORD  # playing sample's channel handle
HStream = DWORD  # sample stream handle
HRecord = DWORD  # recording handle
HSync = DWORD  # synchronizer handle
HDsp = DWORD  # DSP handle
HFx = DWORD  # DX8 effect handle
HPlugin = DWORD  # Plugin handle


class DeviceInfo(Structure):
    _fields_ = [
        ('name', c_char_p),  # description
        ('driver', c_char_p),  # driver
        ('flags', DWORD),
    ]


class Info(Structure):
    _fields_ = [
        ('flags', DWORD),  # device capabilities (DSCAPS_xxx flags)
        ('hwsize', DWORD),  # size of total device hardware memory
        ('hwfree', DWORD),  # size of free device hardware memory
        ('freesam', DWORD),  # number of free sample slots in the hardware
        ('free3d', DWORD),  # number of free 3D sample slots in the hardware
        ('minrate', DWORD),  # min sample rate supported by the hardware
        ('maxrate', DWORD),  # max sample rate supported by the hardware
        ('eax', BOOL),  # device supports EAX? (always FALSE if BASS_DEVICE_3D was not used)
        ('minbuf', DWORD),  # recommended minimum buffer length in ms (requires BASS_DEVICE_LATENCY)
        ('dsver', DWORD),  # DirectSound version
        ('latency', DWORD),  # delay (in ms) before start of playback (requires BASS_DEVICE_LATENCY)
        ('initflags', DWORD),  # BASS_Init "flags" parameter
        ('speakers', DWORD),  # number of speakers available
        ('freq', DWORD),  # current output rate
    ]


class RecordInfo(Structure):
    _fields_ = [
        ('flags', DWORD),  # device capabilities (DSCCAPS_xxx flags)
        ('formats', DWORD),  # supported standard formats (WAVE_FORMAT_xxx flags)
        ('inputs', DWORD),  # number of inputs
        ('singlein', BOOL),  # TRUE = only 1 input can be set at a time
        ('freq', DWORD),  # current input rate
    ]


class Sample(Structure):
    _fields_ = [
        ('freq', DWORD),  # default playback rate
        ('volume', c_float),  # default volume (0-1)
        ('pan', c_float),  # default pan (-1=left, 0=middle, 1=right)
        ('flags', DWORD),  # BASS_SAMPLE_xxx flags
        ('length', DWORD),  # length (in bytes)
        ('max', DWORD),  # maximum simultaneous playbacks
        ('origres', DWORD),  # original resolution
        ('chans', DWORD),  # number of channels
        ('mingap', DWORD),  # minimum gap (ms) between creating channels
        ('mode3d', DWORD),  # BASS_3DMODE_xxx mode
        ('mindist', c_float),  # minimum distance
        ('maxdist', c_float),  # maximum distance
        ('iangle', DWORD),  # angle of inside projection cone
        ('oangle', DWORD),  # angle of outside projection cone
        ('outvol', c_float),  # delta-volume outside the projection cone
        ('vam', DWORD),  # voice allocation/management flags (BASS_VAM_xxx)
        ('priority', DWORD),  # priority (0=lowest, 0xffffffff=highest)
    ]


class ChannelInfo(Structure):
    _fields_ = [
        ('freq', DWORD),  # default playback rate
        ('chans', DWORD),  # channels
        ('flags', DWORD),  # BASS_SAMPLE/STREAM/MUSIC/SPEAKER flags
        ('ctype', DWORD),  # type of channel
        ('origres', DWORD),  # original resolution
        ('plugin', HPlugin),  # plugin
        ('sample', HSample),  # sample
        ('filename', c_char_p),  # filename
    ]


class BASS_PLUGINFORM(Structure):
    _fields_ = [
        ('ctype', DWORD),  # channel type
        ('name', c_char_p),  # format description
        ('exts', c_char_p),  # file extension filter (*.ext1;*.ext2;etc...)
    ]


class PluginInfo(Structure):
    _fields_ = [
        ('version', DWORD),  # version (same form as BASS_GetVersion)
        ('formatc', DWORD),  # number of formats
        ('formats', POINTER(BASS_PLUGINFORM)),  # the array of formats
    ]


class Vector3D(Structure):
    _fields_ = [
        ('x', c_float),  # +=right, -=left
        ('y', c_float),  # +=up, -=down
        ('z', c_float),  # +=front, -=behind
    ]


class TAG_ID3(Structure):
    _fields_ = [
        ('id', c_byte * 3),
        ('title', c_byte * 30),
        ('artist', c_byte * 30),
        ('album', c_byte * 30),
        ('year', c_byte * 4),
        ('comment', c_byte * 30),
        ('genre', BYTE),
    ]


class TAG_APE_BINARY(Structure):
    _fields_ = [
        ('key', c_char_p),
        ('data', c_void_p),
        ('length', DWORD),
    ]


class TAG_BEXT(Structure):
    _fields_ = [
        ('Description', c_byte * 256),  # description
        ('Originator', c_byte * 32),  # name of the originator
        ('OriginatorReference', c_byte * 32),  # reference of the originator
        ('OriginationDate', c_byte * 10),  # date of creation (yyyy-mm-dd)
        ('OriginationTime', c_byte * 8),  # time of creation (hh-mm-ss)
        ('TimeReference', QWORD),  # first sample count since midnight (little-endian)
        ('Version', WORD),  # BWF version (little-endian)
        ('UMID', BYTE * 64),  # SMPTE UMID
        ('Reserved', BYTE * 190),
        ('CodingHistory', POINTER(c_byte)),  # history
    ]


class TAG_CART_TIMER(Structure):
    _fields_ = [
        ('dwUsage', DWORD),  # FOURCC timer usage ID
        ('dwValue', DWORD),  # timer value in samples from head
    ]


class TAG_CART(Structure):
    _fields_ = [
        ('Version', c_byte * 4),  # version of the data structure
        ('Title', c_byte * 64),  # title of cart audio sequence
        ('Artist', c_byte * 64),  # artist or creator name
        ('CutID', c_byte * 64),  # cut number identification
        ('ClientID', c_byte * 64),  # client identification
        ('Category', c_byte * 64),  # category ID, PSA, NEWS, etc
        ('Classification', c_byte * 64),  # classification or auxiliary key
        ('OutCue', c_byte * 64),  # out cue text
        ('StartDate', c_byte * 10),  # yyyy-mm-dd
        ('StartTime', c_byte * 8),  # hh:mm:ss
        ('EndDate', c_byte * 10),  # yyyy-mm-dd
        ('EndTime', c_byte * 8),  # hh:mm:ss
        ('ProducerAppID', c_byte * 64),  # name of vendor or application
        ('ProducerAppVersion', c_byte * 64),  # version of producer application
        ('UserDef', c_byte * 64),  # user defined text
        ('dwLevelReference', DWORD),  # sample value for 0 dB reference
        ('PostTimer', TAG_CART_TIMER * 8),  # 8 time markers after head
        ('Reserved', c_byte * 276),
        ('URL', c_byte * 1024),  # uniform resource locator
        ('TagText', POINTER(c_byte)),  # free form text for scripts or tags
    ]


class TAG_CUE_POINT(Structure):
    _fields_ = [
        ('dwName', DWORD),
        ('dwPosition', DWORD),
        ('fccChunk', DWORD),
        ('dwChunkStart', DWORD),
        ('dwBlockStart', DWORD),
        ('dwSampleOffset', DWORD),
    ]


class TAG_CUE(Structure):
    _fields_ = [
        ('dwCuePoints', DWORD),
        ('CuePoints', POINTER(TAG_CUE_POINT)),
    ]


class TAG_SMPL_LOOP(Structure):
    _fields_ = [
        ('dwIdentifier', DWORD),
        ('dwType', DWORD),
        ('dwStart', DWORD),
        ('dwEnd', DWORD),
        ('dwFraction', DWORD),
        ('dwPlayCount', DWORD),
    ]


class TAG_SMPL(Structure):
    _fields_ = [
        ('dwManufacturer', DWORD),
        ('dwProduct', DWORD),
        ('dwSamplePeriod', DWORD),
        ('dwMIDIUnityNote', DWORD),
        ('dwMIDIPitchFraction', DWORD),
        ('dwSMPTEFormat', DWORD),
        ('dwSMPTEOffset', DWORD),
        ('cSampleLoops', DWORD),
        ('cbSamplerData', DWORD),
        ('SampleLoops', POINTER(TAG_SMPL_LOOP)),
    ]


class TAG_CA_CODEC(Structure):
    _fields_ = [
        ('ftype', DWORD),  # file format
        ('atype', DWORD),  # audio format
        ('name', c_char_p),  # description
    ]


class WAVEFORMATEX(Structure):
    _fields_ = [
        ('wFormatTag', WORD),
        ('nChannels', WORD),
        ('nSamplesPerSec', DWORD),
        ('nAvgBytesPerSec', DWORD),
        ('nBlockAlign', WORD),
        ('wBitsPerSample', WORD),
        ('cbSize', WORD),
    ]


PWAVEFORMATEX = POINTER(WAVEFORMATEX)
LPWAVEFORMATEX = POINTER(WAVEFORMATEX)


class BASS_DX8_CHORUS(Structure):
    _fields_ = [
        ('fWetDryMix', c_float),
        ('fDepth', c_float),
        ('fFeedback', c_float),
        ('fFrequency', c_float),
        ('lWaveform', DWORD),  # 0=triangle, 1=sine
        ('fDelay', c_float),
        ('lPhase', DWORD),  # BASS_DX8_PHASE_xxx
    ]


class BASS_DX8_COMPRESSOR(Structure):
    _fields_ = [
        ('fGain', c_float),
        ('fAttack', c_float),
        ('fRelease', c_float),
        ('fThreshold', c_float),
        ('fRatio', c_float),
        ('fPredelay', c_float),
    ]


class BASS_DX8_DISTORTION(Structure):
    _fields_ = [
        ('fGain', c_float),
        ('fEdge', c_float),
        ('fPostEQCenterFrequency', c_float),
        ('fPostEQBandwidth', c_float),
        ('fPreLowpassCutoff', c_float),
    ]


class BASS_DX8_ECHO(Structure):
    _fields_ = [
        ('fWetDryMix', c_float),
        ('fFeedback', c_float),
        ('fLeftDelay', c_float),
        ('fRightDelay', c_float),
        ('lPanDelay', BOOL),
    ]


class BASS_DX8_FLANGER(Structure):
    _fields_ = [
        ('fWetDryMix', c_float),
        ('fDepth', c_float),
        ('fFeedback', c_float),
        ('fFrequency', c_float),
        ('lWaveform', DWORD),  # 0=triangle, 1=sine
        ('fDelay', c_float),
        ('lPhase', DWORD),  # BASS_DX8_PHASE_xxx
    ]


class BASS_DX8_GARGLE(Structure):
    _fields_ = [
        ('dwRateHz', DWORD),  # Rate of modulation in hz
        ('dwWaveShape', DWORD),  # 0=triangle, 1=square
    ]


class BASS_DX8_I3DL2REVERB(Structure):
    _fields_ = [
        ('lRoom', c_int),  # [-10000, 0]      default: -1000 mB
        ('lRoomHF', c_int),  # [-10000, 0]      default: 0 mB
        ('flRoomRolloffFactor', c_float),  # [0.0, 10.0]      default: 0.0
        ('flDecayTime', c_float),  # [0.1, 20.0]      default: 1.49s
        ('flDecayHFRatio', c_float),  # [0.1, 2.0]       default: 0.83
        ('lReflections', c_int),  # [-10000, 1000]   default: -2602 mB
        ('flReflectionsDelay', c_float),  # [0.0, 0.3]       default: 0.007 s
        ('lReverb', c_int),  # [-10000, 2000]   default: 200 mB
        ('flReverbDelay', c_float),  # [0.0, 0.1]       default: 0.011 s
        ('flDiffusion', c_float),  # [0.0, 100.0]     default: 100.0 %
        ('flDensity', c_float),  # [0.0, 100.0]     default: 100.0 %
        ('flHFReference', c_float),  # [20.0, 20000.0]  default: 5000.0 Hz
    ]


class BASS_DX8_PARAMEQ(Structure):
    _fields_ = [
        ('fCenter', c_float),
        ('fBandwidth', c_float),
        ('fGain', c_float),
    ]


class BASS_DX8_REVERB(Structure):
    _fields_ = [
        ('fInGain', c_float),  # [-96.0,0.0]            default: 0.0 dB
        ('fReverbMix', c_float),  # [-96.0,0.0]            default: 0.0 db
        ('fReverbTime', c_float),  # [0.001,3000.0]         default: 1000.0 ms
        ('fHighFreqRTRatio', c_float),  # [0.001,0.999]          default: 0.001
    ]


class BASS_FX_VOLUME_PARAM(Structure):
    _fields_ = [
        ('fTarget', c_float),
        ('fCurrent', c_float),
        ('fTime', c_float),
        ('lCurve', DWORD),
    ]


# typedef DWORD StreamProc(HSTREAM handle, void *buffer, DWORD length, void *user)
StreamProc = func_type(
    DWORD,
    HStream,
    c_void_p,
    DWORD,
    c_void_p,
)
# typedef void FILECLOSEPROC(void *user)
FILECLOSEPROC = func_type(
    None,
    c_void_p,
)
# typedef QWORD FILELENPROC(void *user)
FILELENPROC = func_type(
    QWORD,
    c_void_p,
)
# typedef DWORD FILEREADPROC(void *buffer, DWORD length, void *user)
FILEREADPROC = func_type(
    DWORD,
    c_void_p,
    DWORD,
    c_void_p,
)
# typedef BOOL FILESEEKPROC(QWORD offset, void *user)
FILESEEKPROC = func_type(
    BOOL,
    QWORD,
    c_void_p,
)
# typedef void DownloadProc(const void *buffer, DWORD length, void *user)
DownloadProc = func_type(
    None,
    c_void_p,
    DWORD,
    c_void_p,
)
# typedef void SyncProc(HSYNC handle, DWORD channel, DWORD data, void *user)
SyncProc = func_type(
    None,
    HSync,
    DWORD,
    DWORD,
    c_void_p,
)
# typedef void DspProc(HDSP handle, DWORD channel, void *buffer, DWORD length, void *user)
DspProc = func_type(
    None,
    HDsp,
    DWORD,
    c_void_p,
    DWORD,
    c_void_p,
)
# typedef BOOL RecordProc(HRECORD handle, const void *buffer, DWORD length, void *user)
RecordProc = func_type(
    BOOL,
    HRecord,
    c_void_p,
    DWORD,
    c_void_p,
)
# typedef void IOSNOTIFYPROC(DWORD status)
IOSNOTIFYPROC = func_type(
    None,
    DWORD,
)
LPCWAVEFORMATEX = POINTER(WAVEFORMATEX)


class FileProcs(Structure):
    _fields_ = [
        ('close', POINTER(FILECLOSEPROC)),
        ('length', POINTER(FILELENPROC)),
        ('read', POINTER(FILEREADPROC)),
        ('seek', POINTER(FILESEEKPROC)),
    ]
