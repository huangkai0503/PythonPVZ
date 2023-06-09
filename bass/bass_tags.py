from ctypes import c_char_p, c_ulong
from collections import defaultdict

from bass.bass_types import tags_module, func_type, HANDLE

TAG_VERSION = 18

TAGS_GetLastErrorDesc = func_type(c_char_p)(('TAGS_GetLastErrorDesc', tags_module))
TAGS_Read = func_type(c_char_p, c_ulong, c_char_p)(('TAGS_Read', tags_module))
TAGS_GetVersion = func_type(c_ulong)(('TAGS_GetVersion', tags_module))


class BassTags:
    @classmethod
    def GetTags(cls, handle: HANDLE, format_: bytes) -> bytes:
        return TAGS_Read(handle, format_)

    @classmethod
    def GetDefaultTags(cls, handle: HANDLE) -> defaultdict[str, str | None]:
        divider = b"|//||"
        result: defaultdict[str, str | None] = defaultdict(lambda: None)
        fmt_list = [
            b'track=%IFV1(%ITRM(%TRCK),%ITRM(%TRCK))',
            b'artist=%IFV1(%ITRM(%ARTI),%ICAP(%ITRM(%ARTI)))',
            b'title=%IFV1(%ITRM(%TITL),%ICAP(%ITRM(%TITL)))',
            b'album=%IFV1(%ITRM(%ALBM),%IUPC(%ITRM(%ALBM)))',
            b'year=%IFV1(%YEAR, %YEAR)',
            b'genre=%IFV1(%ITRM(%GNRE),%ITRM(%GNRE))',
            b'comment=%IFV1(%ITRM(%CMNT),[%ITRM(%CMNT)])'
        ]
        fmt_str = divider.join(fmt_list)
        retval = cls.GetTags(handle, fmt_str)
        if retval and len(retval) > 0:
            for element in retval.split(divider):
                name, value = element.split(b"=", 1)  # type: (bytes, bytes,)
                result[name.decode("utf-8").strip()] = \
                    value.decode("utf-8", errors="ignore").strip() if len(value) > 0 else None

        return result

    @classmethod
    def GetVersion(cls):
        return TAGS_GetVersion()

    @classmethod
    def GetLastErrorDesc(cls):
        return TAGS_GetLastErrorDesc()
