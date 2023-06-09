from ctypes.wintypes import BOOL, DWORD
from ctypes import c_void_p, c_int, c_float, POINTER, c_char_p, c_double
from bass.bass_types import func_type, bass_module, QWORD, \
    HMusic, HSample, HChannel, HStream, HRecord, HSync, HDsp, HFx, HPlugin, \
    Vector3D, RecordInfo, FileProcs, Sample, PluginInfo, Info, DeviceInfo, ChannelInfo, \
    StreamProc, DownloadProc, DspProc, RecordProc, SyncProc


# BOOL BASS_Init(int device, DWORD freq, DWORD flags, void *win, void *dsguid)
BASS_Init = func_type(
    BOOL,
    c_int,
    DWORD,
    DWORD,
    c_void_p,
    c_void_p,
)(('BASS_Init', bass_module))
# BOOL BASS_SetConfig(DWORD option, DWORD value)
BASS_SetConfig = func_type(
    BOOL,
    DWORD,
    DWORD,
)(('BASS_SetConfig', bass_module))
# DWORD BASS_GetConfig(DWORD option)
BASS_GetConfig = func_type(
    DWORD,
    DWORD,
)(('BASS_GetConfig', bass_module))
# BOOL BASS_SetConfigPtr(DWORD option, const void *value)
BASS_SetConfigPtr = func_type(
    BOOL,
    DWORD,
    c_void_p,
)(('BASS_SetConfigPtr', bass_module))
# void * BASS_GetConfigPtr(DWORD option)
BASS_GetConfigPtr = func_type(
    c_void_p,
    DWORD,
)(('BASS_GetConfigPtr', bass_module))
# DWORD BASS_GetVersion()
BASS_GetVersion = func_type(
    DWORD,
)(('BASS_GetVersion', bass_module))
# int BASS_ErrorGetCode()
BASS_ErrorGetCode = func_type(
    c_int,
)(('BASS_ErrorGetCode', bass_module))
# BOOL BASS_GetDeviceInfo(DWORD device, BASS_DEVICEINFO *info)
BASS_GetDeviceInfo = func_type(
    BOOL,
    DWORD,
    POINTER(DeviceInfo),
)(('BASS_GetDeviceInfo', bass_module))
# BOOL BASS_SetDevice(DWORD device)
BASS_SetDevice = func_type(
    BOOL,
    DWORD,
)(('BASS_SetDevice', bass_module))
# DWORD BASS_GetDevice()
BASS_GetDevice = func_type(
    DWORD,
)(('BASS_GetDevice', bass_module))
# BOOL BASS_Free()
BASS_Free = func_type(
    BOOL,
)(('BASS_Free', bass_module))
# void * BASS_GetDSoundObject(DWORD object)
BASS_GetDSoundObject = func_type(
    c_void_p,
    DWORD,
)(('BASS_GetDSoundObject', bass_module))
# BOOL BASS_GetInfo(BASS_INFO *info)
BASS_GetInfo = func_type(
    BOOL,
    POINTER(Info),
)(('BASS_GetInfo', bass_module))
# BOOL BASS_Update(DWORD length)
BASS_Update = func_type(
    BOOL,
    DWORD,
)(('BASS_Update', bass_module))
# float BASS_GetCPU()
BASS_GetCPU = func_type(
    c_float,
)(('BASS_GetCPU', bass_module))
# BOOL BASS_Start()
BASS_Start = func_type(
    BOOL,
)(('BASS_Start', bass_module))
# BOOL BASS_Stop()
BASS_Stop = func_type(
    BOOL,
)(('BASS_Stop', bass_module))
# BOOL BASS_Pause()
BASS_Pause = func_type(
    BOOL,
)(('BASS_Pause', bass_module))
# BOOL BASS_IsStarted()
# todo: not found
# BASS_IsStarted = func_type(
#     BOOL,
# )(('BASS_IsStarted', bass_module))
# BOOL BASS_SetVolume(float volume)
BASS_SetVolume = func_type(
    BOOL,
    c_float,
)(('BASS_SetVolume', bass_module))
# float BASS_GetVolume()
BASS_GetVolume = func_type(
    c_float,
)(('BASS_GetVolume', bass_module))
# HPLUGIN BASS_PluginLoad(const char *file, DWORD flags)
BASS_PluginLoad = func_type(
    HPlugin,
    c_char_p,
    DWORD,
)(('BASS_PluginLoad', bass_module))
# BOOL BASS_PluginFree(HPLUGIN handle)
BASS_PluginFree = func_type(
    BOOL,
    HPlugin,
)(('BASS_PluginFree', bass_module))
# const BASS_PLUGININFO * BASS_PluginGetInfo(HPLUGIN handle)
BASS_PluginGetInfo = func_type(
    POINTER(PluginInfo),
    HPlugin,
)(('BASS_PluginGetInfo', bass_module))
# BOOL BASS_Set3DFactors(float distf, float rollf, float doppf)
BASS_Set3DFactors = func_type(
    BOOL,
    c_float,
    c_float,
    c_float,
)(('BASS_Set3DFactors', bass_module))
# BOOL BASS_Get3DFactors(float *distf, float *rollf, float *doppf)
BASS_Get3DFactors = func_type(
    BOOL,
    POINTER(c_float),
    POINTER(c_float),
    POINTER(c_float),
)(('BASS_Get3DFactors', bass_module))
# BOOL BASS_Set3DPosition(
#     const BASS_3DVECTOR *pos, const BASS_3DVECTOR *vel, const BASS_3DVECTOR *front, const BASS_3DVECTOR *top)
BASS_Set3DPosition = func_type(
    BOOL,
    POINTER(Vector3D),
    POINTER(Vector3D),
    POINTER(Vector3D),
    POINTER(Vector3D),
)(('BASS_Set3DPosition', bass_module))
# BOOL BASS_Get3DPosition(BASS_3DVECTOR *pos, BASS_3DVECTOR *vel, BASS_3DVECTOR *front, BASS_3DVECTOR *top)
BASS_Get3DPosition = func_type(
    BOOL,
    POINTER(Vector3D),
    POINTER(Vector3D),
    POINTER(Vector3D),
    POINTER(Vector3D),
)(('BASS_Get3DPosition', bass_module))
# void BASS_Apply3D()
BASS_Apply3D = func_type(
    None,
)(('BASS_Apply3D', bass_module))
# BOOL BASS_SetEAXParameters(int env, float vol, float decay, float damp)
BASS_SetEAXParameters = func_type(
    BOOL,
    c_int,
    c_float,
    c_float,
    c_float,
)(('BASS_SetEAXParameters', bass_module))
# BOOL BASS_GetEAXParameters(DWORD *env, float *vol, float *decay, float *damp)
BASS_GetEAXParameters = func_type(
    BOOL,
    POINTER(DWORD),
    POINTER(c_float),
    POINTER(c_float),
    POINTER(c_float),
)(('BASS_GetEAXParameters', bass_module))
# HMUSIC BASS_MusicLoad(BOOL mem, const void *file, QWORD offset, DWORD length, DWORD flags, DWORD freq)
BASS_MusicLoad = func_type(
    HMusic,
    BOOL,
    c_void_p,
    QWORD,
    DWORD,
    DWORD,
    DWORD,
)(('BASS_MusicLoad', bass_module))
# BOOL BASS_MusicFree(HMUSIC handle)
BASS_MusicFree = func_type(
    BOOL,
    HMusic,
)(('BASS_MusicFree', bass_module))
# HSAMPLE BASS_SampleLoad(BOOL mem, const void *file, QWORD offset, DWORD length, DWORD max, DWORD flags)
BASS_SampleLoad = func_type(
    HSample,
    BOOL,
    c_void_p,
    QWORD,
    DWORD,
    DWORD,
    DWORD,
)(('BASS_SampleLoad', bass_module))
# HSAMPLE BASS_SampleCreate(DWORD length, DWORD freq, DWORD chans, DWORD max, DWORD flags)
BASS_SampleCreate = func_type(
    HSample,
    DWORD,
    DWORD,
    DWORD,
    DWORD,
    DWORD,
)(('BASS_SampleCreate', bass_module))
# BOOL BASS_SampleFree(HSAMPLE handle)
BASS_SampleFree = func_type(
    BOOL,
    HSample,
)(('BASS_SampleFree', bass_module))
# BOOL BASS_SampleSetData(HSAMPLE handle, const void *buffer)
BASS_SampleSetData = func_type(
    BOOL,
    HSample,
    c_void_p,
)(('BASS_SampleSetData', bass_module))
# BOOL BASS_SampleGetData(HSAMPLE handle, void *buffer)
BASS_SampleGetData = func_type(
    BOOL,
    HSample,
    c_void_p,
)(('BASS_SampleGetData', bass_module))
# BOOL BASS_SampleGetInfo(HSAMPLE handle, BASS_SAMPLE *info)
BASS_SampleGetInfo = func_type(
    BOOL,
    HSample,
    POINTER(Sample),
)(('BASS_SampleGetInfo', bass_module))
# BOOL BASS_SampleSetInfo(HSAMPLE handle, const BASS_SAMPLE *info)
BASS_SampleSetInfo = func_type(
    BOOL,
    HSample,
    POINTER(Sample),
)(('BASS_SampleSetInfo', bass_module))
# HCHANNEL BASS_SampleGetChannel(HSAMPLE handle, BOOL onlynew)
BASS_SampleGetChannel = func_type(
    HChannel,
    HSample,
    BOOL,
)(('BASS_SampleGetChannel', bass_module))
# DWORD BASS_SampleGetChannels(HSAMPLE handle, HCHANNEL *channels)
BASS_SampleGetChannels = func_type(
    DWORD,
    HSample,
    POINTER(HChannel),
)(('BASS_SampleGetChannels', bass_module))
# BOOL BASS_SampleStop(HSAMPLE handle)
BASS_SampleStop = func_type(
    BOOL,
    HSample,
)(('BASS_SampleStop', bass_module))
# HSTREAM BASS_StreamCreate(DWORD freq, DWORD chans, DWORD flags, STREAMPROC *proc, void *user)
BASS_StreamCreate = func_type(
    HStream,
    DWORD,
    DWORD,
    DWORD,
    POINTER(StreamProc),
    c_void_p,
)(('BASS_StreamCreate', bass_module))
# HSTREAM BASS_StreamCreateFile(BOOL mem, const void *file, QWORD offset, QWORD length, DWORD flags)
BASS_StreamCreateFile = func_type(
    HStream,
    BOOL,
    c_void_p,
    QWORD,
    QWORD,
    DWORD,
)(('BASS_StreamCreateFile', bass_module))
# HSTREAM BASS_StreamCreateURL(const char *url, DWORD offset, DWORD flags, DOWNLOADPROC *proc, void *user)
BASS_StreamCreateURL = func_type(
    HStream,
    c_char_p,
    DWORD,
    DWORD,
    POINTER(DownloadProc),
    c_void_p,
)(('BASS_StreamCreateURL', bass_module))
# HSTREAM BASS_StreamCreateFileUser(DWORD system, DWORD flags, const BASS_FILEPROCS *proc, void *user)
BASS_StreamCreateFileUser = func_type(
    HStream,
    DWORD,
    DWORD,
    POINTER(FileProcs),
    c_void_p,
)(('BASS_StreamCreateFileUser', bass_module))
# BOOL BASS_StreamFree(HSTREAM handle)
BASS_StreamFree = func_type(
    BOOL,
    HStream,
)(('BASS_StreamFree', bass_module))
# QWORD BASS_StreamGetFilePosition(HSTREAM handle, DWORD mode)
BASS_StreamGetFilePosition = func_type(
    QWORD,
    HStream,
    DWORD,
)(('BASS_StreamGetFilePosition', bass_module))
# DWORD BASS_StreamPutData(HSTREAM handle, const void *buffer, DWORD length)
BASS_StreamPutData = func_type(
    DWORD,
    HStream,
    c_void_p,
    DWORD,
)(('BASS_StreamPutData', bass_module))
# DWORD BASS_StreamPutFileData(HSTREAM handle, const void *buffer, DWORD length)
BASS_StreamPutFileData = func_type(
    DWORD,
    HStream,
    c_void_p,
    DWORD,
)(('BASS_StreamPutFileData', bass_module))
# BOOL BASS_RecordGetDeviceInfo(DWORD device, BASS_DEVICEINFO *info)
BASS_RecordGetDeviceInfo = func_type(
    BOOL,
    DWORD,
    POINTER(DeviceInfo),
)(('BASS_RecordGetDeviceInfo', bass_module))
# BOOL BASS_RecordInit(int device)
BASS_RecordInit = func_type(
    BOOL,
    c_int,
)(('BASS_RecordInit', bass_module))
# BOOL BASS_RecordSetDevice(DWORD device)
BASS_RecordSetDevice = func_type(
    BOOL,
    DWORD,
)(('BASS_RecordSetDevice', bass_module))
# DWORD BASS_RecordGetDevice()
BASS_RecordGetDevice = func_type(
    DWORD,
)(('BASS_RecordGetDevice', bass_module))
# BOOL BASS_RecordFree()
BASS_RecordFree = func_type(
    BOOL,
)(('BASS_RecordFree', bass_module))
# BOOL BASS_RecordGetInfo(BASS_RECORDINFO *info)
BASS_RecordGetInfo = func_type(
    BOOL,
    POINTER(RecordInfo),
)(('BASS_RecordGetInfo', bass_module))
# const char * BASS_RecordGetInputName(int input)
BASS_RecordGetInputName = func_type(
    c_char_p,
    c_int,
)(('BASS_RecordGetInputName', bass_module))
# BOOL BASS_RecordSetInput(int input, DWORD flags, float volume)
BASS_RecordSetInput = func_type(
    BOOL,
    c_int,
    DWORD,
    c_float,
)(('BASS_RecordSetInput', bass_module))
# DWORD BASS_RecordGetInput(int input, float *volume)
BASS_RecordGetInput = func_type(
    DWORD,
    c_int,
    POINTER(c_float),
)(('BASS_RecordGetInput', bass_module))
# HRECORD BASS_RecordStart(DWORD freq, DWORD chans, DWORD flags, RECORDPROC *proc, void *user)
BASS_RecordStart = func_type(
    HRecord,
    DWORD,
    DWORD,
    DWORD,
    POINTER(RecordProc),
    c_void_p,
)(('BASS_RecordStart', bass_module))
# double BASS_ChannelBytes2Seconds(DWORD handle, QWORD pos)
BASS_ChannelBytes2Seconds = func_type(
    c_double,
    DWORD,
    QWORD,
)(('BASS_ChannelBytes2Seconds', bass_module))
# QWORD BASS_ChannelSeconds2Bytes(DWORD handle, double pos)
BASS_ChannelSeconds2Bytes = func_type(
    QWORD,
    DWORD,
    c_double,
)(('BASS_ChannelSeconds2Bytes', bass_module))
# DWORD BASS_ChannelGetDevice(DWORD handle)
BASS_ChannelGetDevice = func_type(
    DWORD,
    DWORD,
)(('BASS_ChannelGetDevice', bass_module))
# BOOL BASS_ChannelSetDevice(DWORD handle, DWORD device)
BASS_ChannelSetDevice = func_type(
    BOOL,
    DWORD,
    DWORD,
)(('BASS_ChannelSetDevice', bass_module))
# DWORD BASS_ChannelIsActive(DWORD handle)
BASS_ChannelIsActive = func_type(
    DWORD,
    DWORD,
)(('BASS_ChannelIsActive', bass_module))
# BOOL BASS_ChannelGetInfo(DWORD handle, BASS_CHANNELINFO *info)
BASS_ChannelGetInfo = func_type(
    BOOL,
    DWORD,
    POINTER(ChannelInfo),
)(('BASS_ChannelGetInfo', bass_module))
# const char * BASS_ChannelGetTags(DWORD handle, DWORD tags)
BASS_ChannelGetTags = func_type(
    c_char_p,
    DWORD,
    DWORD,
)(('BASS_ChannelGetTags', bass_module))
# DWORD BASS_ChannelFlags(DWORD handle, DWORD flags, DWORD mask)
BASS_ChannelFlags = func_type(
    DWORD,
    DWORD,
    DWORD,
    DWORD,
)(('BASS_ChannelFlags', bass_module))
# BOOL BASS_ChannelUpdate(DWORD handle, DWORD length)
BASS_ChannelUpdate = func_type(
    BOOL,
    DWORD,
    DWORD,
)(('BASS_ChannelUpdate', bass_module))
# BOOL BASS_ChannelLock(DWORD handle, BOOL lock)
BASS_ChannelLock = func_type(
    BOOL,
    DWORD,
    BOOL,
)(('BASS_ChannelLock', bass_module))
# BOOL BASS_ChannelPlay(DWORD handle, BOOL restart)
BASS_ChannelPlay = func_type(
    BOOL,
    DWORD,
    BOOL,
)(('BASS_ChannelPlay', bass_module))
# BOOL BASS_ChannelStop(DWORD handle)
BASS_ChannelStop = func_type(
    BOOL,
    DWORD,
)(('BASS_ChannelStop', bass_module))
# BOOL BASS_ChannelPause(DWORD handle)
BASS_ChannelPause = func_type(
    BOOL,
    DWORD,
)(('BASS_ChannelPause', bass_module))
# BOOL BASS_ChannelSetAttribute(DWORD handle, DWORD attrib, float value)
BASS_ChannelSetAttribute = func_type(
    BOOL,
    DWORD,
    DWORD,
    c_float,
)(('BASS_ChannelSetAttribute', bass_module))
# BOOL BASS_ChannelGetAttribute(DWORD handle, DWORD attrib, float *value)
BASS_ChannelGetAttribute = func_type(
    BOOL,
    DWORD,
    DWORD,
    POINTER(c_float),
)(('BASS_ChannelGetAttribute', bass_module))
# BOOL BASS_ChannelSlideAttribute(DWORD handle, DWORD attrib, float value, DWORD time)
BASS_ChannelSlideAttribute = func_type(
    BOOL,
    DWORD,
    DWORD,
    c_float,
    DWORD,
)(('BASS_ChannelSlideAttribute', bass_module))
# BOOL BASS_ChannelIsSliding(DWORD handle, DWORD attrib)
BASS_ChannelIsSliding = func_type(
    BOOL,
    DWORD,
    DWORD,
)(('BASS_ChannelIsSliding', bass_module))
# BOOL BASS_ChannelSetAttributeEx(DWORD handle, DWORD attrib, void *value, DWORD size)
BASS_ChannelSetAttributeEx = func_type(
    BOOL,
    DWORD,
    DWORD,
    c_void_p,
    DWORD,
)(('BASS_ChannelSetAttributeEx', bass_module))
# DWORD BASS_ChannelGetAttributeEx(DWORD handle, DWORD attrib, void *value, DWORD size)
BASS_ChannelGetAttributeEx = func_type(
    DWORD,
    DWORD,
    DWORD,
    c_void_p,
    DWORD,
)(('BASS_ChannelGetAttributeEx', bass_module))
# BOOL BASS_ChannelSet3DAttributes(DWORD handle, int mode, float min, float max, int iangle, int oangle, float outvol)
BASS_ChannelSet3DAttributes = func_type(
    BOOL,
    DWORD,
    c_int,
    c_float,
    c_float,
    c_int,
    c_int,
    c_float,
)(('BASS_ChannelSet3DAttributes', bass_module))
# BOOL BASS_ChannelGet3DAttributes(
#     DWORD handle, DWORD *mode, float *min, float *max, DWORD *iangle, DWORD *oangle, float *outvol)
BASS_ChannelGet3DAttributes = func_type(
    BOOL,
    DWORD,
    POINTER(DWORD),
    POINTER(c_float),
    POINTER(c_float),
    POINTER(DWORD),
    POINTER(DWORD),
    POINTER(c_float),
)(('BASS_ChannelGet3DAttributes', bass_module))
# BOOL BASS_ChannelSet3DPosition(
#     DWORD handle, const BASS_3DVECTOR *pos, const BASS_3DVECTOR *orient, const BASS_3DVECTOR *vel)
BASS_ChannelSet3DPosition = func_type(
    BOOL,
    DWORD,
    POINTER(Vector3D),
    POINTER(Vector3D),
    POINTER(Vector3D),
)(('BASS_ChannelSet3DPosition', bass_module))
# BOOL BASS_ChannelGet3DPosition(DWORD handle, BASS_3DVECTOR *pos, BASS_3DVECTOR *orient, BASS_3DVECTOR *vel)
BASS_ChannelGet3DPosition = func_type(
    BOOL,
    DWORD,
    POINTER(Vector3D),
    POINTER(Vector3D),
    POINTER(Vector3D),
)(('BASS_ChannelGet3DPosition', bass_module))
# QWORD BASS_ChannelGetLength(DWORD handle, DWORD mode)
BASS_ChannelGetLength = func_type(
    QWORD,
    DWORD,
    DWORD,
)(('BASS_ChannelGetLength', bass_module))
# BOOL BASS_ChannelSetPosition(DWORD handle, QWORD pos, DWORD mode)
BASS_ChannelSetPosition = func_type(
    BOOL,
    DWORD,
    QWORD,
    DWORD,
)(('BASS_ChannelSetPosition', bass_module))
# QWORD BASS_ChannelGetPosition(DWORD handle, DWORD mode)
BASS_ChannelGetPosition = func_type(
    QWORD,
    DWORD,
    DWORD,
)(('BASS_ChannelGetPosition', bass_module))
# DWORD BASS_ChannelGetLevel(DWORD handle)
BASS_ChannelGetLevel = func_type(
    DWORD,
    DWORD,
)(('BASS_ChannelGetLevel', bass_module))
# BOOL BASS_ChannelGetLevelEx(DWORD handle, float *levels, float length, DWORD flags)
BASS_ChannelGetLevelEx = func_type(
    BOOL,
    DWORD,
    POINTER(c_float),
    c_float,
    DWORD,
)(('BASS_ChannelGetLevelEx', bass_module))
# DWORD BASS_ChannelGetData(DWORD handle, void *buffer, DWORD length)
BASS_ChannelGetData = func_type(
    DWORD,
    DWORD,
    c_void_p,
    DWORD,
)(('BASS_ChannelGetData', bass_module))
# HSYNC BASS_ChannelSetSync(DWORD handle, DWORD type, QWORD param, SYNCPROC *proc, void *user)
BASS_ChannelSetSync = func_type(
    HSync,
    DWORD,
    DWORD,
    QWORD,
    POINTER(SyncProc),
    c_void_p,
)(('BASS_ChannelSetSync', bass_module))
# BOOL BASS_ChannelRemoveSync(DWORD handle, HSYNC sync)
BASS_ChannelRemoveSync = func_type(
    BOOL,
    DWORD,
    HSync,
)(('BASS_ChannelRemoveSync', bass_module))
# HDSP BASS_ChannelSetDSP(DWORD handle, DSPPROC *proc, void *user, int priority)
BASS_ChannelSetDSP = func_type(
    HDsp,
    DWORD,
    POINTER(DspProc),
    c_void_p,
    c_int,
)(('BASS_ChannelSetDSP', bass_module))
# BOOL BASS_ChannelRemoveDSP(DWORD handle, HDSP dsp)
BASS_ChannelRemoveDSP = func_type(
    BOOL,
    DWORD,
    HDsp,
)(('BASS_ChannelRemoveDSP', bass_module))
# BOOL BASS_ChannelSetLink(DWORD handle, DWORD chan)
BASS_ChannelSetLink = func_type(
    BOOL,
    DWORD,
    DWORD,
)(('BASS_ChannelSetLink', bass_module))
# BOOL BASS_ChannelRemoveLink(DWORD handle, DWORD chan)
BASS_ChannelRemoveLink = func_type(
    BOOL,
    DWORD,
    DWORD,
)(('BASS_ChannelRemoveLink', bass_module))
# HFX BASS_ChannelSetFX(DWORD handle, DWORD type, int priority)
BASS_ChannelSetFX = func_type(
    HFx,
    DWORD,
    DWORD,
    c_int,
)(('BASS_ChannelSetFX', bass_module))
# BOOL BASS_ChannelRemoveFX(DWORD handle, HFX fx)
BASS_ChannelRemoveFX = func_type(
    BOOL,
    DWORD,
    HFx,
)(('BASS_ChannelRemoveFX', bass_module))
# BOOL BASS_FXSetParameters(HFX handle, const void *params)
BASS_FXSetParameters = func_type(
    BOOL,
    HFx,
    c_void_p,
)(('BASS_FXSetParameters', bass_module))
# BOOL BASS_FXGetParameters(HFX handle, void *params)
BASS_FXGetParameters = func_type(
    BOOL,
    HFx,
    c_void_p,
)(('BASS_FXGetParameters', bass_module))
# BOOL BASS_FXReset(HFX handle)
BASS_FXReset = func_type(
    BOOL,
    HFx,
)(('BASS_FXReset', bass_module))
# BOOL BASS_FXSetPriority(HFX handle, int priority)
BASS_FXSetPriority = func_type(
    BOOL,
    HFx,
    c_int,
)(('BASS_FXSetPriority', bass_module))
