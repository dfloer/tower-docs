import struct
from attrs import define, Factory, field
from typing import List, Any
from random import randint
from collections import defaultdict
from pathlib import Path

from tower_helpers import *

struct_lens = {'b': 1, 'B': 2, 'H': 2, 'h': 2, 'I': 4, 'i': 4, '?': 1}

@define
class UnknownValues:
    __start_offset: int = field(default=None, repr=False)
    __end_offset: int = field(default=None, repr=False)
    __length: int = field(default=None, repr=False)
    __values: int = field(default=None, repr=False)

    @classmethod
    def _parse(cls, start_offset: int, raw_data: Any, length: int = 0) -> "UnknownValues":
        res = cls()
        res.__start_offset = start_offset
        values = [struct.unpack("<B", raw_data[res.__start_offset + x :  res.__start_offset + x + 1])[0] for x in range(length)]
        res.__values = values
        res.__end_offset = res.__start_offset + length
        res.__length = len(res.values)
        return res

    @property
    def start_offset(self) -> int:
        return self.__start_offset

    @property
    def end_offset(self) -> int:
        return self.__end_offset

    def __len__(self) -> int:
        return self.__length

    def __str__(self) -> str:
        return f"UnknownValues(values=[{', '.join([str(x) for x in self.__values])}])"

@define
class GenericEntry:
    __start_offset: int = field(default=None, repr=False)
    __end_offset: int = field(default=None, repr=False)
    __length: int = field(default=0, repr=False)

    @classmethod
    def _parse(cls, start_offset: int, raw_data: Any) -> "GenericEntry":
        res = cls()
        res.__start_offset = start_offset
        offset = start_offset
        # Use __slots__ over dir() because the latter sorts, and this breaks ordering.
        for attr in [x for x in res.__slots__ if not x.startswith("_")]:
            parse_val = getattr(res, attr)
            val_len = struct_lens[parse_val[-1]]
            val = struct.unpack(parse_val, raw_data[offset : offset + val_len])[0]
            setattr(res, attr, val)
            offset += val_len
            res.__length += val_len
        res.__end_offset = offset
        return res

    @property
    def start_offset(self) -> int:
        return self.__start_offset

    @property
    def end_offset(self) -> int:
        return self.__end_offset

    def __len__(self) -> int:
        return self.__length

@define
class TowerMeta(GenericEntry):
    magic: int = "<h"
    level: int = "<h"
    money: int = field(default="<i", repr=nice_money)
    other_income: int = "<i"
    construction_cost: int = "<i"
    last_quarter_money: int = "<i"
    ticks: int = field(default="<h", repr=ticks_dbg)
    day: int = field(default="<i", repr=day_to_str)
    unk_short_1: int = "<h"
    lobby_height: int = "<h"
    unk_short_2: int = "<h"
    unk_short_3: int = "<h"
    unk_short_4: int = "<h"
    unk_short_5: int = "<h"
    window_x: int = "<h"
    window_y: int = "<h"
    recycling_count: int = "<h"
    unk_short_6: int = "<h"
    commercial_count: int = "<h"
    security_count: int = "<h"
    parking_stall_count: int = "<h"
    medical_count: int = "<h"
    hall_cinema_count: int = "<h"
    named_units: int = "<h"
    named_people: int = "<h"
    unk_short_7: int = "<h"
    unknown_1: int = "<i"
    unknown_2: int = "<i"

@define
class RepeatedGenericEntry(GenericEntry):
    __start_offset: int = field(default=None, repr=False)
    __end_offset: int = field(default=None, repr=False)
    __entry_count: int = field(default=0, init=True)
    # __entry_contents: List = field(init=False, repr=False)

    @classmethod
    def _parse(cls, start_offset: int, raw_data: Any, entry_count: int = 0) -> "RepeatedGenericEntry":
        res = cls()
        res.__entry_count = entry_count
        res.__start_offset = start_offset
        offset = start_offset
        # The list of ("ClassName", entry_count) values to look up.
        # entry_count can either be a number for hard-coded counts, or a lookup on a previously parsed header.
        # This is pretty limited right now, but it works for the simplicity of the TDT files.
        contents = getattr(res, f"_{res.__class__.__name__}__entry_contents")
        print("Entry contents:", contents)
        for cls_name, count in contents:
            # The list *has* to be named "classnamelower_entries".
            data_attr = f"{cls_name.lower()}_entries"
            print(cls_name, count, type(cls_name), type(count))
            # If we've got a bare count, we don't need to do a lookup first.
            if isinstance(count, int):
                pass
            elif isinstance(count, str):
                data_attr_name, data_attr_count = count.split('.')
                print("str version", count)
                for lookup in getattr(res, data_attr_name):
                    print(lookup)
                    count = getattr(lookup, data_attr_count)
                    print(count)
            for e_idx in range(count):
                entry_cls = globals()[cls_name]
                print(e_idx, type(entry_cls))
                entry = entry_cls()._parse(offset, raw_data)
                print(entry)
                offset = entry.end_offset
                l = getattr(res, data_attr)
                l += [entry]
                setattr(res, data_attr, l)


                # count_lookup = 
        # for attr in [x for x in res.__slots__ if not x.startswith("_")]:
        #     parse_val = getattr(res, attr)
        #     print(attr, parse_val)

    @property
    def start_offset(self) -> int:
        return self.__start_offset

    @property
    def end_offset(self) -> int:
        return self.__end_offset

    def __len__(self) -> int:
        return self.__length


@define
class FloorsData(RepeatedGenericEntry):
    floor_entries: List = field(default=Factory(list), repr=False)
    unit_entries: List = field(default=Factory(list), repr=False)
    unknownvalues_entries: List = field(default=Factory(list), repr=False)
    __entry_contents: List = field(default=(("Floor", 120), ("Unit", "floor_entries.unit_count"), ("UnknownValues", 188)), repr=False)

@define
class Floor(GenericEntry):
    unit_count: int = field(default="<h")
    start: int = field(default="<h")
    end: int = field(default="<h")

@define
class Unit(GenericEntry):
    # index: int  # index of order code found it in.
    left: int = "<h"
    right: int = "<h"
    unit_type: int = "<b"
    unknown_1: int = "<b"
    commercial_idx: int = "<b"
    unknown_3: int = "<b"
    unknown_4: int = "<I"
    unknown_5: int = "<b"
    unknown_6: int = "<b"
    unknown_7: int = "<b"
    unknown_8: int = "<b"
    rate: int = "<b"
    unknown_9: int = "<b"

@define
class Tower:
    tower_path: Path
    _tower_raw_data: List[int] = field(default=Factory(list), init=False)
    tower_name: str = field(default='', init=False)
    tower_metadata: "TowerMeta" = field(default=None, init=False)
    tower_header: "TowerMeta" = field(default=None, init=False)
    floors: "FloorsData" = field(default=None, init=False)


    def __init__(self, tower_path: Path) -> None:
        print(f"Opening tower at {tower_path}")
        self.__attrs_init__(tower_path)
        try:
            with open(tower_path, 'rb') as f:
                self._tower_raw_data = f.read()
                self.tower_name = tower_path.name[: -4]
        except Exception as e:
            print("Tower opening failed with error:", e)

        if self._tower_raw_data:
            self.parse_tower()

    def parse_tower(self):
        start_offset = 0
        self.tower_metadata = TowerMeta._parse(start_offset, self._tower_raw_data)
        start_offset = self.tower_metadata.end_offset
        print(self.tower_metadata)
        print(f"Tower meta final offset: {start_offset}")
        self.tower_header = UnknownValues._parse(start_offset, self._tower_raw_data, 490)
        start_offset = self.tower_header.end_offset
        # print(self.tower_header)
        print(f"Tower header final offset: {start_offset}")
        self.floors = FloorsData._parse(start_offset, self._tower_raw_data, 120)





if __name__ == "__main__":
    tower_path = Path(r"G:\games\Maxis\SIMTWR1\BOB3.TDT")

    tower = Tower(tower_path=tower_path)