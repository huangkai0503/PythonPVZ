from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

Words = tuple[str, ...]
Type: TypeAlias = 'FunctionType | str | StructType'


@dataclass
class FunctionType:
    ret: str
    args: str

    def format_c(self, name: str):
        return f'{self.ret} {name}({self.args})'

    def format_py(self):
        res = ['func_type(']
        res.extend(f'    {to_py_type(type_)},' for type_ in (self.ret, *self.arg_types()))
        res.append(f')')
        return '\n'.join(res)

    def arg_types(self):
        args = self.args
        if not args:
            return []
        res: list[str] = []
        for arg in args.split(','):
            arg = arg.strip()
            type_, arg = find_type_and_name(arg)
            res.append(type_)
        return res


@dataclass
class StructType:
    attrs: list[tuple[str, str, str]]
    name: str = ''

    def format_c(self):
        res = [f'struct {self.name} {{']
        for c_type, name, comment in self.attrs:
            com = f'  //{comment}' if comment else ''
            res.append(f'    {c_type} {name};{com}')
        res.append('}')
        return '\n'.join(res)

    def format_py(self, name: str, com: str):
        aliases = [n.strip() for n in name.split(',')]
        normal_name: str = ''
        starred_names: list[tuple[int, str]] = []
        for alias in aliases:
            n_pointer = alias.count('*')
            if n_pointer == 0:
                normal_name = alias
            starred_names.append((n_pointer, alias[n_pointer:]))
        assert normal_name, f'Must have a name without star (got: {name})'
        res = [f'class {normal_name}(Structure):' + (f'  #{com}' if com else ''), '    _field_ = [']
        for c_type, attr_name, comment in self.attrs:
            c = f'  #{comment}' if comment else ''
            res.append(f'        ({attr_name!r}, {to_py_type(c_type)}),{c}')
        res.append('    ]')
        other: list[str] = []
        for n_pointer, alias in starred_names:
            if alias == normal_name:
                continue
            other.append(f'{alias} = {"POINTER(" * n_pointer}{normal_name}{")" * n_pointer}')
        if other:
            res.extend(['\n\n'] + other)
        return '\n'.join(res)


@dataclass
class Function:
    type: FunctionType
    name: str

    def format_c(self):
        return self.type.format_c(self.name)

    def format_py(self, module: str):
        return f'{self.type.format_py()}(({self.name!r}, {module}))'


@dataclass
class Define:
    dst: Words
    src: str
    com: str


@dataclass
class Typedef:
    name: str
    type: Type
    com: str = ''


def _find_prefix(a: Words, b: Words):
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            return a[:i]
    return a


class TypesGenerator:
    def __init__(self, typedefs: list[Typedef]):
        self.typedefs: list[Typedef] = typedefs

        self.header = [f"""\
from ctypes import POINTER, Structure, {', '.join(c_types_table.values())}
from ctypes.wintypes import {', '.join(win_type_names)}
from pathlib import Path
import platform

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
"""]
        self.header.extend(defined_typedefs.values())
        self.footer = """
LPCWAVEFORMATEX = POINTER(WAVEFORMATEX)


class FileProcs(Structure):
    _fields_ = [
        ('close', POINTER(FILECLOSEPROC)),
        ('length', POINTER(FILELENPROC)),
        ('read', POINTER(FILEREADPROC)),
        ('seek', POINTER(FILESEEKPROC)),
    ]
"""

        self.functions: list[str] = []
        self.aliases: list[str] = []
        self.structs: list[str] = []

    def start(self):
        for typedef in self.typedefs:
            self._format_single(typedef)
        return self.output()

    def _format_single(self, typedef: Typedef):
        name, type_, com = typedef.name, typedef.type, typedef.com
        if isinstance(type_, FunctionType):
            self._format_function(name, type_, com)
        elif isinstance(type_, StructType):
            self._format_struct(name, type_, com)
        elif isinstance(type_, str):
            self._format_alias(name, type_, com)
        else:
            raise TypeError(typedef.type)

    def _format_function(self, name: str, type_: FunctionType, com: str):
        name = c2py_procs.get(name, name)
        com = f'  #{com}' if com else ''
        self.functions.append(f'# typedef {type_.format_c(name)}\n{name} = {type_.format_py()}{com}')

    def _format_struct(self, name: str, type_: StructType, com: str):
        normal_name, starred_names = self._find_struct_names(name)
        if normal_name in defined_structs:
            return
        res = [f'class {normal_name}(Structure):' + (f'  #{com}' if com else ''), '    _fields_ = [']
        for c_type, attr_name, comment in type_.attrs:
            c = f'  #{comment}' if comment else ''
            res.append(f'        ({attr_name!r}, {to_py_type(c_type)}),{c}')
        res.append('    ]')
        other: list[str] = []
        for n_pointer, alias in starred_names:
            if alias == normal_name:
                continue
            other.append(f'{alias} = {"POINTER(" * n_pointer}{normal_name}{")" * n_pointer}')
        if other:
            res.extend(['\n'] + other)
        self.structs.append('\n'.join(res))

    @staticmethod
    def _find_struct_names(name: str) -> tuple[str, list[tuple[int, str]]]:
        aliases = [n.strip() for n in name.split(',')]
        normal_name: str = ''
        starred_names: list[tuple[int, str]] = []
        for alias in aliases:
            alias = c2py_structs.get(alias, alias)
            n_pointer = alias.count('*')
            if n_pointer == 0:
                normal_name = alias
            starred_names.append((n_pointer, alias[n_pointer:]))
        assert normal_name, f'Must have a name without star (got: {name})'
        return normal_name, starred_names

    def _format_alias(self, name: str, type_: str, com: str):
        if name in win_type_names:
            return
        com = f'  #{com}' if com else ''
        self.aliases.append(f'{handle_table.get(name, name)} = {to_py_type(type_)}{com}')

    def output(self):
        res = ['\n'.join(self.header + self.aliases), '\n\n\n', '\n\n\n'.join(self.structs), '\n\n\n',
               '\n'.join(self.functions), self.footer]
        return ''.join(res)


class Parser:
    def __init__(self, header: str):
        self.functions: list[Function] = []
        self.typedefs: list[Typedef] = []
        self.constants: list[Define] = []

        self.lines = header.splitlines()
        self.line_no = 0

    def parse(self):
        while self.line_no < len(self.lines):
            line = self.lines[self.line_no]
            self._parse_line(line)

    def _parse_line(self, line: str):
        com, line = self._parse_comment(line)
        self.parse_func(line)
        self.parse_define(line, com)
        self.parse_typedef(line, com)
        self.line_no += 1

    @staticmethod
    def _parse_comment(line: str):
        com_start, com_end = find_slice(line, '//')
        if com_start != -1:
            com = line[com_end:]
            line = line[:com_start].strip()
            return com, line
        return '', line.strip()

    @staticmethod
    def _parse_func_helper(func: str, name_start: str, name_end: str):
        start, end = find_slice(func, name_start)
        if start == -1:
            return
        ret = func[:start].strip()
        name_end_pos = func.find(name_end, end)
        name = func[end:name_end_pos]
        args = func[name_end_pos + 2:-1]
        return ret, name, args

    def parse_func(self, line: str):
        if not line.endswith(';'):
            return
        func = line[:-1]
        res = self._parse_func_helper(func, 'BASSDEF(', ')')
        if res is None:
            return
        ret, name, args = res
        if name in defined_functions:
            return
        self.functions.append(Function(FunctionType(ret, args), name))

    def output_functions(self, file: Path):
        res = [f"""\
from ctypes.wintypes import BOOL, DWORD
from ctypes import c_void_p, c_int, c_float, POINTER, c_char_p, c_double
from bass.bass_types import func_type, bass_module, QWORD, \\
    {", ".join(handle_table.values())}, \\
    {", ".join(c2py_structs.values())}, \\
    {", ".join(c2py_procs.values())}
""", *defined_functions.values()]
        for func in self.functions:
            res.append(f'# {func.format_c()}')
            res.append(f'{func.name} = {func.format_py("bass_module")}')
        res.append('')
        file.write_text('\n'.join(res))

    def output_constants(self, file: Path):
        gen = ConstantsGenerator(self._find_constant_prefixes())
        file.write_text(gen.start())

    def output_types(self, file: Path):
        gen = TypesGenerator(self.typedefs)
        file.write_text(gen.start())

    def parse_define(self, line: str, com: str):
        ok, define = cut_start(line, '#define ')
        if not ok:
            return
        parts = define.strip().split()
        if len(parts) != 2:
            return
        left, right = parts  # type: (str, str)
        if '(' in left or ',' in right:
            return
        dst = tuple(left.split('_'))
        if dst[0] == 'BASS':
            dst = dst[1:]
        self.constants.append(Define(dst, right, com))

    def parse_typedef(self, line: str, com: str):
        ok, rest = cut_start(line, 'typedef ')
        if not ok:
            return
        self._parse_typedef_type(rest, com)
        self._parse_typedef_func(rest, com)
        self._parse_typedef_struct(rest, com)

    def _find_constant_prefixes(self) -> dict[Words, list[Define]]:
        if not self.constants:
            return {}
        res: dict[Words, list[Define]] = {}
        now: list[Define] = []
        prefix: Words = self.constants[0].dst
        for define in self.constants + [Define((), '', '')]:
            new = _find_prefix(prefix, define.dst)
            if not new:
                res[prefix] = res.get(prefix, []) + [Define(d.dst[len(prefix):], d.src, d.com) for d in now]
                prefix = define.dst
                now = [define]
            else:
                now.append(define)
                prefix = new
        return res

    def _parse_typedef_type(self, rest: str, com: str):
        if not rest.endswith(';'):
            return
        rest = rest[:-1]
        left, right = find_type_and_name(rest)
        if '(' in left or '(' in right:
            return
        if right in defined_typedefs:
            return
        self.typedefs.append(Typedef(right, left, com))

    def _parse_typedef_func(self, rest: str, com: str):
        if not rest.endswith(';'):
            return
        res = self._parse_func_helper(rest[:-1], '(CALLBACK ', ')')
        if res is None:
            return
        ret, name, args = res
        self.typedefs.append(Typedef(name, FunctionType(ret, args), com))

    def _parse_typedef_struct(self, rest: str, com: str):
        ok, rest = cut_start(rest, 'struct')
        if not ok:
            return
        attrs: list[tuple[str, str, str]] = []
        self.line_no += 1
        while not (line := self.lines[self.line_no]).startswith('}'):
            c, line = self._parse_comment(line)
            res = self._parse_var_define(line)
            if res is not None:
                c_type, name = res
                attrs.append((c_type, name, c))
            self.line_no += 1
        _, line = self._parse_comment(line)
        typedef_name = line[2:-1]  # 去除 '} ' 和 ';'
        self.typedefs.append(Typedef(typedef_name, StructType(attrs), com))

    @staticmethod
    def _parse_var_define(line: str) -> tuple[str, str] | None:
        if not line.endswith(';'):
            return None
        type_, name = find_type_and_name(line[:-1])
        if not name or '(' in name:
            return None
        return type_, name


class ConstantsGenerator:
    def __init__(self, preprocessed: dict[Words, list[Define]]):
        self.preprocessed = preprocessed

        self.header: list[str] = []
        self.res: list[str] = []

        self.now_class: Words = ()
        self.created_classes: list[Words] = []

    def start(self) -> str:
        for prefix, suffixes in self.preprocessed.items():
            self._enum_or_flag(prefix, suffixes)
        header = ['from typing import Final\nfrom enum import Enum, Flag']
        if self.header:
            header.append('')
            header.extend(self.header)
        return '\n'.join(header) + '\n\n\n' + '\n'.join(self.res)

    def _enum_or_flag(self, prefix: Words, suffixes: list[Define]):
        if len(suffixes) == 1:
            self._single_define(prefix, suffixes[0])
            return
        self.now_class = prefix
        base_cls = 'Enum' if self._is_enum(prefix, suffixes) else 'Flag'
        cls_name = self._translate_class_name(prefix)
        self.res.append(f'class {cls_name}({base_cls}):')
        self._make_elements(suffixes)
        self.res.append('\n')
        self.created_classes.append(self.now_class)

    def _single_define(self, prefix: Words, suffix: Define):
        com = f'  #{suffix.com}' if suffix.com else ''
        self.header.append(f'{"_".join(("BASS",) + prefix + suffix.dst)}: Final = {suffix.src}{com}')

    def _is_enum(self, prefix: Words, suffixes: list[Define]):
        cls_name = self._translate_class_name(prefix)
        if cls_name in flag_classes:
            return False
        if cls_name in enum_classes:
            return True
        hex_count = 0
        for suffix in suffixes:
            if '0x' in suffix.src:
                print(suffix.src)
                hex_count += 1
                if hex_count >= 3:
                    return False
        return True

    def _make_elements(self, suffixes: list[Define]):
        for suffix in suffixes:
            com = f'  #{suffix.com}' if suffix.com else ''
            self.res.append(f'    {self._translate_element_name(suffix.dst)} = {self._translate_src(suffix.src)}{com}')

    @staticmethod
    def _translate_element_name(words: Words):
        if words[0][0] == '3':
            return '_'.join(word.upper() for word in ('THREE', words[0][1:], *words[1:]))
        joined = ''.join(words)
        if joined == '8BITS':
            return 'BITS8'
        if joined == '16BITS':
            return 'BITS16'
        if joined == '90':
            return 'P90'
        if joined == '180':
            return 'P180'
        return '_'.join(word.upper() for word in words)

    @staticmethod
    def _translate_class_name(name: Words):
        if name[0][0] == '3':
            first = 'Three' + name[0][1].upper() + name[0][1:].lower()
            return first + ''.join(word[0].upper() + word[1:].lower() for word in name)
        return ''.join(word[0].upper() + word[1:].lower() for word in name)

    def _translate_src(self, src: str):
        if self.now_class:
            src = self._replace(src, self.now_class, '')
        for cls in self.created_classes:
            src = self._replace(src, cls, f'{self._translate_class_name(cls)}.')
        return cut_start(src, '(STREAMPROC*)')[1]

    @staticmethod
    def _replace(src: str, cls_name: Words, new: str):
        src = src.replace('_'.join(('BASS',) + cls_name) + '_' + '3D', new + 'THREE_D')
        src = src.replace('_'.join(('BASS',) + cls_name) + '_', new).replace('_'.join(cls_name) + '_', new)
        return src


def to_py_type(c_type: str):
    c_type = c_type.strip()
    c_type = cut_start(c_type, 'const ')[1]
    has_size, size_start = find_slice(c_type, '[')
    if has_size != -1:
        size_end = c_type.find(']', size_start)
        assert size_end != -1
        item_type = c_type[:has_size]
        size = c_type[size_start:size_end]
        return f'{to_py_type(item_type)} * {size}' if size else f'POINTER({to_py_type(item_type)})'
    c_type = normalize(c_type)
    if '*' in c_type:
        if c_type in c2py_type_table:
            return c2py_type_table[c_type]
        return f'POINTER({to_py_type(c_type[:-1])})'
    return c2py_type_table.get(c_type, c_type)


def normalize(s: str) -> str:
    return ' '.join(s.split()).replace(' *', '*')


def find_slice(s: str, expect: str) -> tuple[int, int]:
    start = s.find(expect)
    return start, start + len(expect)


def cut_start(s: str, expect: str) -> tuple[bool, str]:
    if s.startswith(expect):
        return True, s[len(expect):]
    return False, s


def find_type_and_name(s: str) -> tuple[str, str]:
    s = s.strip()
    has_size, size_start = find_slice(s, '[')
    if has_size != -1:
        size_end = s.find(']', size_start)
        assert size_end != -1
        type_, name = find_type_and_name(s[:has_size])
        return f'{type_}[{s[size_start:size_end]}]', name
    for i, char in enumerate(reversed(s)):
        if not (char.isidentifier() or char.isdigit()):
            return s[:-i].strip(), s[-i:]
    return s, ''


def main():
    HERE = Path(__file__).parent
    bass_header = HERE / 'lib' / 'bass.h'

    parser = Parser(bass_header.read_text('utf-8'))
    parser.parse()

    # parser.output_functions(Path('./functions.py'))
    # parser.output_constants(Path('./../constants.py'))
    parser.output_types(Path('./../bass_types.py'))


bass_struct_names = ('RecordInfo', 'FileProcs', 'Sample', 'PluginInfo', 'Info', 'DeviceInfo', 'ChannelInfo')
proc_names = ('Stream', 'Download', 'Dsp', 'Record', 'Sync')
handle_names = ('Music', 'Sample', 'Channel', 'Stream', 'Record', 'Sync', 'Dsp', 'Fx', 'Plugin')
win_type_names = ('BYTE', 'WORD', 'DWORD', 'BOOL')

handle_table = {'H' + k.upper(): 'H' + k for k in handle_names}
c_types_table = {
    '_Bool': 'c_bool',
    'char': 'c_byte',
    'wchar_t': 'c_wchar',
    'unsigned char': 'c_ubyte',
    'short': 'c_short',
    'unsigned short': 'c_ushort',
    'int': 'c_int',
    'unsigned int': 'c_uint',
    'long': 'c_long',
    'unsigned long': 'c_ulong',
    'size_t': 'c_size_t',
    'float': 'c_float',
    'double': 'c_double',
    'long double': 'c_longdouble',
    'void*': 'c_void_p',
    '__int64': 'c_longlong',
    'long long': 'c_longlong',
    'unsigned __int64': 'c_ulonglong',
    'unsigned long long': 'c_ulonglong',
    'ssize_t': 'c_ssize_t',
    'Py_ssize_t': 'c_ssize_t',
    'char*': 'c_char_p',
    'wchar_t*': 'c_wchar_p',
    **{f'uint{k}_t': f'c_uint{k}' for k in (8, 16, 32, 64)},
}
c2py_procs = {f'{k.upper()}PROC': f'{k}Proc' for k in proc_names}
c2py_structs = {
    'BASS_3DVECTOR': 'Vector3D',
    **{f'BASS_{k.upper()}': k for k in bass_struct_names},
}
c2py_type_table = {
    **c_types_table,
    **c2py_structs,
    **c2py_procs,
    **handle_table,
    'void': 'None',
}

defined_functions = {
    'BASS_Init': """
# BOOL BASS_Init(int device, DWORD freq, DWORD flags, void *win, void *dsguid)
BASS_Init = func_type(
    BOOL,
    c_int,
    DWORD,
    DWORD,
    c_void_p,
    c_void_p,
)(('BASS_Init', bass_module))""",
}
defined_typedefs = {
    'QWORD': 'QWORD = c_uint64',
    'LPCWAVEFORMATEX': ''
}
defined_structs = {'FileProcs': ''}

flag_classes = set()
enum_classes = {'Attrib'}

if __name__ == '__main__':
    main()
