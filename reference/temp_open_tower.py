import struct
from attrs import define, Factory, field
from typing import List
from random import randint
from collections import defaultdict

import PIL
from PIL import Image

res = None
tower_name = "path/to/TOWER.TDT"

with open(tower_name, 'rb') as f:
    res = f.read()

def floor_conv(n: int) -> str:
    x = n - 10
    e = ''
    if x < 0:
        e = 'B'
        x = abs(x)
    else:
        x += 1
    return f"{e}{x}"

def floor_dbg(n):
    return f"{floor_conv(n)}:{n}"    

def day_to_str(n: int) -> str:
    y = n // 12
    d = n % 3
    q = n % 12 // 3
    year = f"{y + 1}th Year"
    day = d % 3
    quarter = f"{q + 1}Q"
    nice_day = "WE"
    if day == 0:
        nice_day = "1st WD"
    elif day == 1:
        nice_day = "2nd WD"
    return f"counter {n}: day = {nice_day} ({day}), quarter = {quarter}, year = {year}"

def hsv_to_rgb(h, s, v):
    if s == 0.0: return (v, v, v)
    i = int(h*6.) # XXX assume int() truncates!
    f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)


header = {"magic": None,
            "level": None,
            "money": None,
            "other_income": None,
            "construction_cost": None,
            "last_quarter_money": None,
            "ticks": None,
            "day": None,
            "unk3": None,
            "lobby_height": None,
            "unk_short_1": None,
            "unk_short_2": None,
            "unk_short_3": None,
            "unk_short_4": None,
            "window_x": None,
            "window_y": None,
            "recycling_count": None,
            "unk_short_6": None,
            "commercial_count": None,
            "security_count": None,
            "parking_stall_count": None,
            "medical_count": None,
            "hall_cinema_count": None,
            "named_units": None,
            "named_people": None,
            "unk_short_13": None,
            "unk_4": None,
            "unk_5": None,
            }

header_offsets = [2, 2, 4, 4, 4, 4, 2, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 4]
offset = 0
header_extra = {}
for idx, x in enumerate(header_offsets):
    if x == 2:
        val = struct.unpack("<h", res[offset : offset + x])
    else:
        val = struct.unpack("<i", res[offset : offset + x])
    if idx < len(header):
        header[list(header.keys())[idx]] = (val[0], offset, x)
    else:
        header_extra[offset] = (val[0], offset, x)
    offset += x
print(f"Open: {tower_name}")
# print(header)
for k, v in header.items():
    x = v[1] + 0x0971020E
    print(f"offset={str(v[1]).rjust(3)} ({hex(x)}), len={v[2]}.    {k} = {v[0]}")
print(header_extra)

other = {
    "treasure_found": (0x1F0, 2),
    "parking_count_1": (50, 2),
    "parking_count_2": (50, 2),
    "parking_count_3": (50, 2),
    "parking_count_4": (50, 2),
    "parking_count_5": (50, 2),
    "parking_count_6": (50, 2),
    "parking_count_7": (50, 2),
    "parking_count_8": (50, 2),
    "population": (0x4fa, 2),
}
other_vals = {}
for k, v in other.items():
    off = v[0]
    length = v[1]
    if length == 2:
        val = struct.unpack("<h", res[off : off + length])
    else:
        val = struct.unpack("<i", res[off : off + length])
    other_vals[k] = val[0]

print(f"other_vals:\n{other_vals}")

TYPE_MAP = {0: "empty",
            1: "lobby",
}

floors = {k: None for k in range (120)}

@define
class Floor:
    unit_count: int
    start: int
    end: int
    floor_number: int = field(default=None, repr=floor_dbg)
    units: List = field(default=Factory(list), repr=False)
    remap_data: List = field(default=Factory(list), repr=False)
    _end_offset: int = field(default=None, repr=False)

    def __len__(self):
        return len(self.units)

    @classmethod
    def parse_floor(cls, raw_data, start_offset):
        count = struct.unpack("<h", raw_data[start_offset : start_offset + 2])
        start_offset += 2
        start = struct.unpack("<h", raw_data[start_offset : start_offset + 2])
        start_offset += 2
        end = struct.unpack("<h", raw_data[start_offset : start_offset + 2])
        start_offset += 2
        f = Floor(count[0], start[0], end[0])
        for c in range(f.unit_count):
            unit_data = raw_data[start_offset : start_offset + 18]
            start_offset += 18
            r = Unit.parse_units(c, unit_data)
            f.units += [r]
        f._end_offset = start_offset
        return f

    def parse_remap(self, data):
        rm = []
        for x in range(0, 188, 2):
            rm += [struct.unpack("<h", data[x : x + 2])[0]]
        self.remap_data = rm


    @property
    def nice_units(self):
        return '\n'.join([str(x) for x in self.units])

@define
class Unit:  # Total size is 18B.
    index: int  # index of order code found it in.
    left: int  # 2B
    right: int  # 2B
    unit_type: int  # 1B
    unknown_1: int = None  # 1B
    commercial_idx: int = None  #  1B 
    unknown_3: int = None  #  1B
    unknown_4: int = None  # 4B
    # unknown_5: int = None  # 4B
    unknown_5: int = None  # 1B
    unknown_6: int = None  # 1B
    unknown_7: int = None  # 1B
    unknown_8: int = None  # 1B
    rate: int = None  # 1B
    unknown_9: int = None  # 1B
    __type_map: dict = field(default=TYPE_MAP, repr=False)

    @classmethod
    def parse_units(cls, index, unit_data):
        left = struct.unpack("<h", unit_data[0 : 2])[0]
        right = struct.unpack("<h", unit_data[2 : 4])[0]
        unit_type = struct.unpack("<b", unit_data[4 : 5])[0]
        r = Unit(index, left, right, unit_type)
        r.unknown_1: int = struct.unpack("<B", unit_data[5 : 6])[0]
        r.commercial_idx: int = struct.unpack("<B", unit_data[6 : 7])[0]
        r.unknown_3: int = struct.unpack("<B", unit_data[7 : 8])[0]
        r.unknown_4: int = struct.unpack("<i", unit_data[8 : 12])[0]
        # r.unknown_5: int = struct.unpack("<i", unit_data[12 : 16])[0]
        r.unknown_5: int = struct.unpack("<B", unit_data[12 : 13])[0]
        r.unknown_6: int = struct.unpack("<B", unit_data[13 : 14])[0]
        r.unknown_7: int = struct.unpack("<B", unit_data[14 : 15])[0]
        r.unknown_8: int = struct.unpack("<b", unit_data[15 : 16])[0]
        r.rate: int = struct.unpack("<B", unit_data[16 : 17])[0]
        r.unknown_9: int = struct.unpack("<B", unit_data[17 : 18])[0]
        return r

    @property
    def nice_rate(self):
        return {0: "Very Low", 1: "Low", 2: "Average", 3: "High", 4: "None"}.get(self.rate, f"Rate: {self.rate}")

    # def __str__(self):
    #     return f"Unit(index={self.index}, left={self.left}, right={self.right}, unit_type={self.__type_map.get(self.unit_type, self.unit_type)})"

floor = 0
offset = 560
# Actual floor data appears to start at 560.
# print("\n\n\n\n")
remap = {}
while True:
    this_floor = Floor.parse_floor(res, offset)
    offset = this_floor._end_offset
    this_floor.floor_number = floor
    # print(this_floor)
    # print(this_floor.nice_units)
    # print("~~~~~~~~~~~~~~~~~~~\n\n\n\n")
    d = res[offset : offset + 188]
    this_floor.parse_remap(d)
    floors[floor] = this_floor
    # print(floor_dbg(floor), len(this_floor))
    # print(this_floor.remap_data)
    floor += 1
    offset += 188  # Every floor has 188B of data after this part.

    if floor > 119:
        break

@define
class Person:
    _abs_index: int = field(default=None)
    floor: int = field(default=None, repr=floor_dbg)
    unit_index: int = field(default=None)
    person_index: int = field(default=None)
    stress: int = field(default=None)
    curr_floor: int = field(default=None)
    eval: int = field(default=None)
    bits: int = field(default=None)
    values: List[int] = Factory(list)

    @classmethod
    def parse_person(cls, idx, data):
        r = Person(idx)
        done = [0, 1, 2, 5, 12, 13, 14, 15]
        r.values = [struct.unpack("<B", data[x :  x + 1])[0] for x in range(16) if x not in done]
        r.floor = struct.unpack("<B", data[0 : 1])[0]
        r.unit_index = struct.unpack("<B", data[1 : 2])[0]
        r.person_index = struct.unpack("<B", data[2 : 3])[0]
        r.bits = struct.unpack("<B", data[5 : 6])[0]
        r.curr_floor = struct.unpack("<B", data[7 : 8])[0]
        r.stress = struct.unpack("<h", data[12 : 14])[0]
        r.eval = struct.unpack("<h", data[14 : 16])[0]
        return r

    @property
    def bit_flags(self):
        val = f"{self.bits:08b}"
        map = {k: val[k] for k in range(8)}
        return map


floors_s = set()
e_s = set()
floor_d = defaultdict(list)
print(f"end offset: {offset}")
person_count = struct.unpack("<i", res[offset :  offset + 4])[0]
people = {}
offset += 4
for idx in range(person_count):
    data = res[offset : offset + 16]
    prsn = Person.parse_person(idx, data)
    offset += 16
    people[idx] = prsn
    floors_s.add(prsn.floor)
    e_s.add(prsn.person_index)
    floor_d[prsn.floor] += [prsn]
    # print(prsn)
    # print()
print(f"Found {len(people)} entries, expected {person_count}.")
print(f"floor end offset: {offset}")
# print(floors_s)
# print(e_s)
# for k, v in floor_d.items():
    # print(k, len(v))
    # if k == 80:
    #     print(f"floor: {k} ({floor_conv(k)}), # entries: {len(v)}")
    #     print('\n'.join([str(x) for x in v]))



@define
class Commercial:
    _abs_index: int = field(default=None)
    floor: int = field(default=None, repr=floor_dbg)
    variant: int = field(default=None)
    values: List[int] = Factory(list)

    @classmethod
    def parse_commercial(cls, idx, data):
        c = Commercial(idx)
        c.floor = struct.unpack("<b", data[0 : 1])[0]
        c.values = [struct.unpack("<B", data[x :  x + 1])[0] for x in range(18)]
        c.variant = struct.unpack("<b", data[11 : 12])[0]
        return c

    @property
    def empty(self) -> bool:
        return True if self.floor < 0 else False


commercial_info = {}
values = [defaultdict(int) for _ in range(18)]
for idx in range(512):
    data = res[offset : offset + 18]
    comm = Commercial.parse_commercial(idx, data)
    commercial_info[idx] = comm
    offset += 18
    if comm.values[0] == 255:
        continue
    for i in range(18):
        values[i][comm.values[i]] += 1

print(f"Commercial entries: {len(commercial_info)}, expected=512.")
a = 0
for k, v in commercial_info.items():
    if v.values[0] == 255:
        continue
    # print(v)
    if not v.empty:
        a += 1

# for i, e in enumerate(values):
#     print(f"{i} ({len(e)}):")
#     print(', '.join([f"{k}: {v}" for k, v in e.items()]))
    # print(', '.join([str(k) for k in sorted(e.keys())]))
# for i, s in enumerate(values):
#     print()
#     print(f"offset={i}: ", end='')
#     for k, v in s.items():
#         print(f"val={k}, count={v}, ", end='')
        # print(f"i={i}: {', '.join(list(v))}")
print(f"Used commercial entries: {a}, expected={header['commercial_count'][0]}.")
print(f"Commercial end offset: {offset}")

elevators = {}

@define
class ElevatorShaft:
    _abs_index: int = field(default=None)
    _end_offset: int = field(default=None)
    elevator_type: int = field(default=None)
    used: bool = field(default=False)
    show: bool = field(default=False)
    unk: int = field(default=None)
    capacity: int = field(default=None)
    left: int = field(default=None)
    top_floor: int = field(default=None)
    bottom_floor: int = field(default=None)
    num_cars: int = field(default=None)
    values: List[int] = Factory(list)

    scheduler: "ElevatorScheduler" = field(default=None)

    floors_serviced: List[int] = Factory(list)
    elevator_extra: List[int] = Factory(list)
    block_1: List[int] = Factory(list)
    block_2: List[int] = Factory(list)

    floor_data: List[int] = Factory(list)
    car_data: List[int] = Factory(list)
    

    @classmethod
    def parse_shaft(cls, idx, raw_data, offset):
        es = ElevatorShaft(idx)
        es._end_offset = offset
        v_data = raw_data[es._end_offset : es._end_offset + 194]
        es._end_offset += 194
        es.values = [struct.unpack("<B", v_data[x :  x + 1])[0] for x in range(194)]
        es.used = struct.unpack("<?", v_data[0 : 1])[0]
        es.elevator_type = struct.unpack("<B", v_data[1 : 2])[0]
        es.capacity = struct.unpack("<B", v_data[2 : 3])[0]
        es.num_cars = struct.unpack("<B", v_data[3 : 4])[0]
        es.scheduler = ElevatorScheduler.parse_scheduler(v_data[4 : 60])
        es.show = struct.unpack("<?", v_data[60 : 61])[0]
        es.unk = struct.unpack("<B", v_data[61 : 62])[0]
        es.left = struct.unpack("<H", v_data[62 : 64])[0]
        es.top_floor = struct.unpack("<B", v_data[64 : 65])[0]
        es.bottom_floor = struct.unpack("<B", v_data[65 : 66])[0]
        es.floors_serviced = [struct.unpack("<B", v_data[x : x + 1])[0] for x in range(66, 66 + 120)]

        if not es.used:  # No elevator, so none of the following data.
            return es

        if es.elevator_type not in (0, 1, 2):
            assert False, f"elevator type {es.elevator_type} is invalid."

        if es.bottom_floor < 0 or es.bottom_floor > 120:
            assert False, f"elevator bottom {es.bottom_floor} is invalid."
        if es.top_floor < 0 or es.top_floor > 120:
            assert False, f"elevator top {es.top_floor} is invalid."
        if es.top_floor < es.bottom_floor:
            assert False, f"elevator top {es.top_floor} > {es.bottom_floor}"
        if es.num_cars <= 0 or es.num_cars > 8:
            assert False, f"elevator num cars {es.num_cars} invalid."
        if es.num_floors > 30 or es.num_floors <= 0:
            assert False, f"elevator num floors {es.num_floors} invalid."

        b_data = raw_data[es._end_offset : es._end_offset + 480]
        es._end_offset += 480
        es.elevator_extra = [struct.unpack("<B", b_data[x :  x + 1])[0] for x in range(0, 480, 1)]

        block_1_data = raw_data[es._end_offset : es._end_offset + 120]
        es._end_offset += 120
        es.block_1 = [struct.unpack("<B", block_1_data[x :  x + 1])[0] for x in range(120)]

        block_2_data = raw_data[es._end_offset : es._end_offset + 120]
        es._end_offset += 120
        es.block_2 = [struct.unpack("<B", block_2_data[x :  x + 1])[0] for x in range(120)]

        elev_cnt = es._express_floor_count if es.elevator_type == 0 else es.height_floors
        for floor_idx in range(elev_cnt):
            floor_data = raw_data[es._end_offset : es._end_offset + 324]
            es._end_offset += 324
            es.floor_data += [ElevatorFloor.parse_floor(floor_idx, floor_data)]

        for car_idx in range(8):
            car_data = raw_data[es._end_offset : es._end_offset + 346]
            es._end_offset += 346
            es.car_data += [ElevatorCar.parse_car(car_idx, car_data)]
        return es

    @property
    def height_floors(self) -> int:
        return 1 + self.top_floor - self.bottom_floor
    
    @property
    def num_floors(self) -> int:
        return sum(self.floors_serviced)

    @property
    def stop_floors(self) -> List[int]:
        return [i for i, a in enumerate(self.floors_serviced) if a == 1]

    @property
    def stop_floors_nice(self) -> List[int]:
        return [floor_dbg(x) for x in self.stop_floors]

    @property
    def _express_floor_count(self) -> int:
        """
        Express elevators don't stop at every floor, but there's an entry for each potential floor they may stop at.
        So we need to calculate how many there are, even if some are disabled in the floors_serviced section.
        """
        top = self.top_floor
        bottom = self.bottom_floor
        possible = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 24, 39, 54, 69, 84, 99)
        stops = [1 for x in possible if bottom <= x <= top]
        return sum(stops)

    @property
    def nice_type(self) -> str:
        return {0: "Express", 1: "Normal", 2: "Service"}[self.elevator_type]

    @property
    def summary(self) -> str:
        s = f"ElevatorShaft(idx={self._abs_index}, used={self.used}"
        if not self.used:
            return s + ")"
        s += f", type={self.nice_type}, left={self.left}, bottom={floor_dbg(self.bottom_floor)}, top={floor_dbg(self.top_floor)}, "
        s += f"cars={self.num_cars}, cap={self.capacity}, show={self.show}, unknown={self.unk})"
        return s

    @property
    def extra_half(self):
        new_extra = []
        for e in self.elevator_extra:
            b = f"{e:08b}"
            ba, bb = int(b[ : 4], 2), int(b[4 : ], 2)
            new_extra += [ba, bb]
        return new_extra

@define
class ElevatorScheduler:
    values: List[int] = Factory(list)

    @classmethod
    def parse_scheduler(cls, data):
        s = ElevatorScheduler()
        s.values = [struct.unpack("<B", data[x :  x + 1])[0] for x in range(len(data))]
        return s

    def __str__(self):
        wd_wait = [x for x in self.values[14 : 20]]
        we_wait = [x for x in self.values[21 : 27]]
        wd_prio = [x for x in self.values[28 : 34]]
        we_prio = [x for x in self.values[35 : 41]]
        wd_dep = [x * 30 for x in self.values[42 : 48]]
        we_dep = [x * 30 for x in self.values[49 : 55]]
        d = {k : v for k, v in enumerate(self.values)}
        s = f"{d}\n"
        s += f"Priorities: WD {wd_prio}. WE: {we_prio}\n"
        s += f"Waiting Car Response: WD: {wd_wait}. WE: {we_wait}\n"
        s += f"Standard Floor Departures: WD: {wd_dep}. WE: {we_dep}\n"
        return s


@define
class ElevatorFloor:
    _abs_index: int = field(default=None)
    person_idx: List[int] = Factory(list)
    h: int = field(default=None)
        
    @classmethod
    def parse_floor(cls, idx, floor_data):
        ef = ElevatorFloor(idx)
        lfd = len(floor_data)
        ef.person_idx = [struct.unpack("<i", floor_data[x :  x + 4])[0] for x in range(4, lfd, 4)]
        ef.h = [struct.unpack("<B", floor_data[x :  x + 1])[0] for x in range(4)]
        return ef

    def passenger_info_lookup(self, people_data):
        res = []
        for p in self.person_idx:
            if p == 0:
                continue
            res += [people_data[p]]
        return res


@define
class ElevatorCar:
    _abs_index: int = field(default=None)
    curr_floor: int = field(default=None)
    num_passengers: int = field(default=None)
    passenger_info: List[int] = Factory(list)
    passenger_dest: List[int] = Factory(list)
    floor_dest_count: List[int] = Factory(list)
    unk_flag: str = field(default='0000000')# List[int] = Factory(list)
    built: bool = field(default=False)
    stat: int = field(default=False)
    up: bool = field(default=False)
    home: int = field(default=False)
    last: int = field(default=False)
    next: int = field(default=False)
    num_passengers: int = field(default=None)
    values: List[int] = Factory(list)#, repr=None)
        
    @classmethod
    def parse_car(cls, idx, car_data):
        car = ElevatorCar(idx)
        lcd = len(car_data)
        car.values = [struct.unpack("<B", car_data[x :  x + 1])[0] for x in range(16)]
        car.curr_floor = struct.unpack("<B", car_data[0 : 1])[0]
        car.num_passengers = struct.unpack("<B", car_data[3 : 4])[0]
        car.stat = struct.unpack("<B", car_data[2 : 3])[0]
        car.up = struct.unpack("<?", car_data[4 : 5])[0]
        car.next = struct.unpack("<B", car_data[5 : 6])[0]
        car.last = struct.unpack("<B", car_data[6 : 7])[0]
        car.unk_flag = f"{struct.unpack('<B', car_data[8 : 9])[0]:08b}"
        car.built = struct.unpack("<?", car_data[15 : 16])[0]
        info = [struct.unpack("<i", car_data[x :  x + 4])[0] for x in range(16, 16 + 42 * 4, 4)]
        car.passenger_info = [x if x != -1 else None for x in info]
        dest = [struct.unpack("<b", car_data[x :  x + 1])[0] for x in range(184, 184 + 42)]
        car.passenger_dest = [x if x != -1 else None for x in dest]
        car.floor_dest_count = [struct.unpack("<B", car_data[x :  x + 1])[0] for x in range(226, 226 + 120)]
        return car

    def __str__(self):
        s = f"ElevatorCar(idx={self._abs_index}, curr_floor={self.curr_floor}, num_passengers={self.num_passengers}, "
        s += f"built={self.built}, flag={self.unk_flag}"
        s += f"floor_dest_count={self.nice_floor_dest_count}, pax_meta={self.nice_pax_meta}, values={self.values})"
        return s

    @property
    def nice_pax_meta(self):
        res = []
        for a, b in zip(self.passenger_info, self.passenger_dest):
            if a and b:
                res += [f"id: {a} -> {floor_dbg(b)}"]
        return "[" + ", ".join(res) + "]"

    @property
    def nice_floor_dest_count(self):
        return {floor_dbg(k): v for k, v in enumerate(self.floor_dest_count) if v != 0}


    def passenger_info_lookup(self, people_data):
        for p in self.passenger_info:
            if not p:
                continue
            return people_data[p]

for idx in range(24):
    elev = ElevatorShaft.parse_shaft(idx, res, offset)
    offset = elev._end_offset
    elevators[idx] = elev
    # if idx == 19:
    #     print(elev.summary)
    #     # print(elev.floor_data)
    #     print('\n\n'.join([', '.join([str(a).rjust(8) for a in x.person_idx]) for x in elev.floor_data]))
    #     # print([x.h for x in elev.floor_data])
    #     for e in elev.floor_data:
    #         print(f"header: {e.h}")
    #         print(len([x for x in e.person_idx if x != 0]))
        # print('\n'.join([', '.join([str(a).rjust(3) for a in x.values] + [x.unk_flag]) for x in elev.car_data]))
    
    # ee = {floor_dbg(i): x for i, x in enumerate(elev.elevator_extra) if x != 0}
    # he = {floor_dbg(i): x for i, x in enumerate(elev.extra_half) if x != 0}
    # print(f"extra ({len(ee)}) :", ee)
    # print(f"half extra ({len(he)}) :", he)
    # print("block 1:", {floor_dbg(i): x for i, x in enumerate(elev.block_1) if x != 0})
    # print("block 2:", {floor_dbg(i): x for i, x in enumerate(elev.block_2) if x != 0})
    #     print(elev.scheduler)
    # img = Image.new('RGB', (10, 120), (0, 0, 0))

    # cols = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
    # cols += [(255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255)]
    # cols += [ (255, 127, 0), (127, 0, 0), (0, 127, 0), (0, 0, 127)]
    # cols += [ (127, 127, 0), (127, 0, 127), (0, 127, 127), (127, 127, 127),]
    # for j in range(120):
    #     if j < 10:  # underground
    #         colour = (0, 127, 255)
    #     elif j in (10, 24, 39, 54, 69, 84, 99):
    #         colour = (0, 255, 127)
    #     elif j > 109:
    #         colour = (255, 0, 127)
    #     else:
    #         colour = (0, 0, 0)
    #     img.putpixel((0, j), colour)
    #     img.putpixel((1, j), (0, 0, 0))

    # for i, e in {y: x for y, x in enumerate(elev.extra_half)}.items():
    #     xxx = i % 8
    #     yyy = i // 8
    #     colour = cols[e]
    #     img.putpixel((xxx + 2, yyy), colour)
    # # img = img.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)
    # fn = tower_name.split('\\')[-1][:-4] + f"_elev-extra_half_{idx}-{elev.elevator_type}.png"
    # img = img.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)
    # img = img.resize((8 * 8, 120 * 8), resample=PIL.Image.NEAREST)
    # img.save(fn)
    # print(f"saving preview image to {fn}")

    # hsv_col = list(range(0, 360, 360 // 128))
    # rgb_col = [tuple(int(a * 255) for a in hsv_to_rgb(x / 360, 1, 1)) for x in hsv_col]

    # img = Image.new('RGB', (6, 120), (0, 0, 0))
    # for j in range(120):
    #     if j < 10:  # underground
    #         colour = (0, 127, 255)
    #     elif j in (10, 24, 39, 54, 69, 84, 99):
    #         colour = (0, 255, 127)
    #     elif j > 109:
    #         colour = (255, 0, 127)
    #     else:
    #         colour = (0, 0, 0)
    #     img.putpixel((0, j), colour)
    #     img.putpixel((1, j), (0, 0, 0))
    # for i, e in {y: x for y, x in enumerate(elev.elevator_extra)}.items():
    #     xxx = i % 4
    #     yyy = i // 4
    #     colour = rgb_col[e]
    #     if e == 0:
    #         colour = (0, 0, 0)
    #     img.putpixel((xxx + 2, yyy), colour)
    # # img = img.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)
    # fn = tower_name.split('\\')[-1][:-4] + f"_elev-extra_{idx}-{elev.elevator_type}.png"
    # img = img.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)
    # img = img.resize((4 * 8, 120 * 8), resample=PIL.Image.NEAREST)
    # img.save(fn)
    # print(f"saving preview image to {fn}")
    # print("------------------------------\n")

print(f"Elevator entries: {len(elevators)}, expected: 24")
print(f"Elevator section final offset: {offset}")

@define
class Finance:
    values: List[int] = Factory(list)

    @classmethod
    def parse_finance(cls, raw_data):
        fi = Finance()
        fi.values = [struct.unpack("<i", raw_data[x :  x + 4])[0] for x in range(0, len(raw_data), 4)]
        return fi

    @property
    def summary(self):
        income_gen = ("Office", "Single Room", "Double Room", "Suite", "Shops", "Fast Food", "Restuarant", "Party Hall", "Theater", "Condo")
        v = self.values
        s = f"Total income: {v[21]}. Total expenses: {v[32]}. Population: {v[10]}. Other: {v[20]}\n"
        s += ' '.join([f"{k} pop: {v[idx]}, income: {v[idx + 10]}." for idx, k in enumerate(income_gen)])
        expenses = ("Lobby", "Elevator", "Express Elevator", "Service Elevator", "Escalator", "Parking Ramp", "Recycling Center", "Metro Station", "Housekeeping", "Security")
        s += '\n'
        s += ' '.join([f"{k} cost: {v[21 + idx]}." for idx, k in enumerate(expenses)])
        return s


unknown_1 = [struct.unpack("<I", res[x :  x + 4])[0] for x in range(offset, offset + 88, 4)]
offset += 88
print("unknown_1:", unknown_1)
finance_data = Finance.parse_finance(res[offset : offset + 132])
offset += 132
print("Finance:", finance_data.summary)
unknown_3 = [struct.unpack("<B", res[x :  x + 1])[0] for x in range(offset, offset + 12)]
offset += 12
print("unknown_3:", unknown_3)
unknown_4 = [struct.unpack("<B", res[x :  x + 1])[0] for x in range(offset, offset + 42)]
offset += 42
print("unknown_4:", unknown_4)

print(f"Unknown 4x sections final offset: {offset}")

@define
class Parking:
    connected_count: int = field(default=None)
    values: List[int] = Factory(list)

    @classmethod
    def parse_parking(cls, raw_data):
        fi = Parking()
        fi.connected_count = struct.unpack("<H", raw_data[0 : 2])[0]
        fi.values = [struct.unpack("<H", raw_data[x :  x + 2])[0] for x in range(4, len(raw_data), 4)]
        return fi

parking_data = Parking.parse_parking(res[offset : offset + 1026])
offset += 1026
print("parking_data:", parking_data)
ec = [x for x in parking_data.values if x != 0]
print(f"entries ({len(ec)}): {ec}")

print(f"Parking section final offset: {offset}")

unknown_5 = [struct.unpack("<B", res[x :  x + 1])[0] for x in range(offset, offset + 22)]
offset += 22
print("unknown_5:", unknown_5)
print(f"Unknown 5 section final offset: {offset}")

@define
class Stair:
    _abs_index: int = field(default=None)
    built: bool = field(default=False)
    type_id: int = field(default=None)
    left: int = field(default=None)
    floor: int = field(default=None)
    people_up: int = field(default=None)
    people_down: int = field(default=None)

    @classmethod
    def parse_stair(cls, idx, raw_data):
        st = Stair(idx)
        st.built = struct.unpack("<?", raw_data[0 : 1])[0]
        st.type_id = struct.unpack("<B", raw_data[1 : 2])[0]
        st.left = struct.unpack("<H", raw_data[2 : 4])[0]
        st.floor = struct.unpack("<H", raw_data[4 : 6])[0]
        st.people_up = struct.unpack("<H", raw_data[6 : 8])[0]
        st.people_down = struct.unpack("<H", raw_data[8 : 10])[0]
        return st

    @property
    def type_name(self) -> str:
        return ["Escalator", "Stair", "2F Escalator", "2F Stair", "3F Escalator", "3F Stair"][st.type_id]

stairs_data = []
for idx in range(64):
    d = res[offset : offset + 10]
    offset += 10
    st = Stair.parse_stair(idx, d)
    if st.built:
        print(st)
    stairs_data += [st]

floor_start = set()
for st in stairs_data:
    floor_start = st.floor
print("floor_start:", floor_start)


print(f"Stairs/Escalator section final offset: {offset}")

unk_484 = []
for x in range(8):
    unk_h = [struct.unpack("<B", res[x :  x + 1])[0] for x in range(offset, offset + 4)]
    # unk = [struct.unpack("<I", res[x :  x + 4])[0] for x in range(offset + 4, (offset + 4) + 120 * 4, 4)]
    unk = [struct.unpack("<B", res[x :  x + 1])[0] for x in range(offset + 4, (offset + 4) + 120 * 4)]
    offset += 484
    # print(f"unknown_484 {x}:", unk_h)
    # print(len([x for x in unk if x != 0]), unk)

print(f"Unknown 8 x 484B section final offset: {offset}")

unknown_120 = [struct.unpack("<B", res[x :  x + 1])[0] for x in range(offset, offset + 120)]
offset += 120
# print("unknown_120:", [f"{floor_dbg(i)}={x}" for i, x in enumerate(unknown_120)])
a_t = [i for i, x in enumerate(unknown_120) if x]
print(f"unknown_120 ({len(a_t)}):", a_t)

security_floors = [struct.unpack("<h", res[x :  x + 2])[0] for x in range(offset, offset + 20, 2)]
offset += 20
print("Security Floors:", [floor_dbg(x) if x >0 else x for x in security_floors])

print(f"Security section final offset: {offset}")

for i, x in enumerate(range(offset, offset + (528 * 6), 6)):
    # six = [struct.unpack("<H", res[x :  x + 2])[0] for x in range(x, x + 6, 2)]
    # six = [struct.unpack("<B", res[x :  x + 1])[0] for x in range(x, x + 6, 1)]
    if x < 512:
        six = [struct.unpack("<B", res[x : x + 1])[0]]
        six += [struct.unpack("<B", res[ x + 1 : x + 2])[0]]
        six += [struct.unpack("<I", res[x + 2 : x + 6])[0]]
    else:
        six = [struct.unpack("<B", res[x :  x + 1])[0] for x in range(x, x + 6, 1)]
        # six = [struct.unpack("<I", res[x : x + 4])[0]]
        # six += [struct.unpack("<B", res[ x + 4 : x + 5])[0]]
        # six += [struct.unpack("<B", res[ x + 5 : x + 6])[0]]
    print(str(i).ljust(4), six)

offset += 528 * 6

print(f"Unknown Nx6B section final offset: {offset}")

# img = Image.new('RGB', (375, 120 * 5))

# c_map = {}

# unit_types = set()
# for k, v in floors.items():
#     for r in v.units:
#         left = r.left
#         right = r.right
#         t = r.unit_type
#         unit_types.add(t)
#         if t not in c_map:
#             colour = (randint(16, 239), randint(16, 239), randint(16, 239))
#             c_map[t] = colour
#         if t in (10,) and k == 12:
#             print(r)
#             print()
#         colour = c_map[t]
#         for a in range(left, right):
#             for b in range(5):
#                 img.putpixel((a, k * 5 + b), colour)
# img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)
# fn = tower_name.split('\\')[-1][:-4] + ".png"
# img.save(fn)
# print(f"saving preview image to {fn}")
# print(f"Unit types observed: {unit_types}")


# hsv_col = list(range(0, 360, 360 // 12))
# rgb_col = [tuple(int(a * 255) for a in hsv_to_rgb(x / 360, 1, 1)) for x in hsv_col]
# # print(rgb_col)
# for var_x in range(11):
#     img = Image.new('RGB', (375, 120 * 5))
#     for k, v in floors.items():
#         floor_comm = [x for x in commercial_info.values() if x.floor == k]
#         i = 0
#         rd = v.remap_data
#         for r in v.units:
#             left = r.left
#             right = r.right
#             t = r.unit_type
#             colour = (128, 128, 128)
#             if t in (6, 10, 12):
#                 # remap_i = rd[i]
#                 # print(f"floor: {floor_dbg(k)}")
#                 # print(i, remap_i, r.commercial_idx, len(floor_comm))
#                 # cd = floor_comm[remap_i]
#                 # comm_data = floor_comm[i]
#                 try:
#                     cdc = [x for x in floor_comm if x._abs_index == r.commercial_idx][0].variant
#                 except IndexError:
#                     cdc = None
                    

#                 # print(cd.variant, comm_data.variant, cdc.variant)
#                 # colour = rgb_col[comm_data.variant]
#                 if cdc == var_x:
#                     if t == 6:
#                         colour = (255, 0, 0)
#                     elif t == 10:
#                         colour = (0, 255, 0)
#                     else:
#                         colour = (0, 0, 255)
#                 else:
#                     if t == 6:
#                         colour = (128, 0, 0)
#                     elif t == 10:
#                         colour = (0, 128, 0)
#                     else:
#                         colour = (0, 0, 128)
#                 i += 1
#             for a in range(left, right):
#                 for b in range(5):
#                     img.putpixel((a, k * 5 + b), colour)
#     img = img.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)
#     fn = tower_name.split('\\')[-1][:-4] + f"_comm_variants_{var_x}.png"
#     img.save(fn)

# c_map = {0: (255, 0, 0), 1: (255, 255, 0), 2: (0, 255, 0), 3: (0, 255, 255), 4: (128, 128, 128)}
# img = Image.new('RGB', (375, 120 * 5))
# rate_s = set()
# for k, v in floors.items():
#     for r in v.units:
#         left = r.left
#         right = r.right
#         t = r.rate
#         rate_s.add(t)
#         colour = c_map.get(t, (255, 0, 255))
#         for a in range(left, right):
#             for b in range(5):
#                 img.putpixel((a, k * 5 + b), colour)
# img = img.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)
# fn = tower_name.split('\\')[-1][:-4] + "_rate.png"
# img.save(fn)
# print(f"rate set: {rate_s}")

# for i in (1, 2, 3, 5, 6, 7, 8, 9):
#     type_check = 10
#     attr = f"unknown_{i}"
#     u_vals = set()
#     u_cnt = 0
#     c_map = {}
#     img = Image.new('RGB', (375, 120 * 5))
#     for k, v in floors.items():
#         for r in v.units:
#             left = r.left
#             right = r.right
#             t = r.unit_type
#             u = getattr(r, attr)
#             if t == type_check:
#                 u_vals.add(u)
#                 u_cnt += 1
#                 if u not in c_map:
#                     colour = (randint(16, 239), randint(16, 239), randint(16, 239))
#                     c_map[u] = colour
#                 colour = c_map[u]
#             else:
#                 colour = (128, 128, 128)
#             for a in range(left, right):
#                 for b in range(5):
#                     img.putpixel((a, k * 5 + b), colour)
#     img = img.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)
#     fn = tower_name.split('\\')[-1][:-4] + f"_type-{type_check}_{attr}.png"
#     img.save(fn)
#     print(f"{attr} count: {u_cnt}, unique: {len(u_vals)}, vals: {u_vals}")

# img = Image.new('RGB', (375, 120 * 5))

# sizes = [6, 4, 4]
# colours = [(0, 0, 255), (0,0,0), (255, 0, 0)]

# for k, v in floors.items():
#     for r in v.units:
#         left = r.left
#         right = r.right
#         t = r.unit_type
#         colour = (128, 128, 128)
#         for a in range(left, right):
#             for b in range(5):
#                 img.putpixel((a, k * 5 + b), colour)

# for k, v in elevators.items():
#     left = v.left
#     top = v.top_floor
#     bottom = v.bottom_floor
#     t = v.elevator_type
#     for f in range(bottom, top + 1):  # +2 to draw the way the game overshoots.
#         for b in range(5):
#             for a in range(left, left + sizes[t]):
#                 img.putpixel((a, f * 5 + b), colours[t])
# img = img.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)
# fn = tower_name.split('\\')[-1][:-4] + "_elevators.png"
# img.save(fn)
# print(f"saving preview image to {fn}")