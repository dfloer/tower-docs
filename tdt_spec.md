# SimTower TDT File Specification

## Header

| Offset | Length | Use | Notes |
| --- | --- | --- | --- |
| 0 | 2 | Magic | Seems to always be `00 24` |
| 2 | 2 | Tower Level | 1 = 1 star, 2 = 2 star, 3 = 3 star, 4 = 4 star, 5 = 5 star, 6 = tower |
| 4 | 4 | Money | This seems like it's the money balance, but it's handled strangely. |
| 8 | 4 | Other Income | Other income from finances window. |
| 12 | 4 | Construction Costs | Construction Costs from finances window. |
| 16 | 4 | Last Quarter Money | Last quarter's money from finances window. |
| 20 | 2 | Timer | Seems to increment to ~2600 every day. |
| 22 | 4 | Current Day | Current day, starting from WD1/Q1/Y1. |
| 26 | 2 | Lobby Height | Ground floor lobby height: 1 = normal lobby, 2 = 2 story lobby, 3 = 3 story lobby |
| 30 | 2 | unknown | |
| 32 | 2 | unknown | |
| 34 | 2 | unknown | |
| 36 | 2 | unknown | |
| 36 | 2 | unknown | |
| 38 | 4 | Window Location | Game loads this as 4 bytes, but is actually the Window x position, then window y position. 0,0 is the top left corner. 2897, 4181 the bottom right with the smallest possible window size, 2184, 3744 with largest. |
| 42 | 2 | Recycling Count | Total number of recycling centers in the building. |
| 44 | 2 | unknown | |
| 46 | 2 | Commercial Count | Count of commercial (fast-food, shop and restuarant) built. |
| 48 | 2 | Security Count | Count of total security offices built. Maximum is 10. |
| 50 | 2 | Parking Stall Count | Total number of parking stalls, including unconnected (red X) ones. |
| 52 | 2 | Medical Clinic Count | Total number of medical clinics. Maybe? |
| 54 | 2 | Hall/Cinema Count | Count of all cinemas and party halls. |
| 56 | 2 | unknown | |
| 58 | 2 | unknown | |
| 60 | 2 | unknown | |
| 62 | 4 | unknown | |
| 66 | 4 | unknown | |

### Timer Notes

Timer starts at 0 and runs until 2600. In terms of ticks, a day starts at 7:00AM, but the day counter rolls over at 2300 ticks, or midnight in game time. The game spends a variable amount of time simulating in game time. There are four distinct simulation speeds throughout the day, with the most time (800 ticks) spent simulating the lunch-time rush.

The day counter is incremented at midnight, which is 2300 ticks, even if a simulation day ends at 7:00AM.

| Time of Day (in 24hr) | Timer Ticks | Simulation Time |
| --- | --- | --- |
| 7:00 to 12:00 | 0 - 400 | 1 tick = 45 seconds simulated |
| 12:00 to 13:00 | 400 - 1200 | 1 tick = 4.5 seconds simulated |
| 13:00 to 1:00 | 1200 - 2400 | 1 tick = 36 seconds simulated |
| 1:00 to 7:00 | 2400 - 2600 | 1 tick = 126 seconds simulated |

## Floor Data

After the first 68 bytes of the file, this is where actual tower data seems to reside. There is a 490 Byte segment that is unknown

There are 120 entries (10 underground floors, 100 normal floors and probalby 10 floors for the Cathedral and open space/padding).

Each floor has a 6 Byte floor header (which includes a count), that count * 18B with one per unit on the floor and finally a 188B data structure after that. This last part is currently unknown.

### Floor Header

A floor in 375 tiles long.
| Offset | Length | Use | Notes |
| --- | --- | --- | --- |
| 0 | 2 | Unit Count | Total number of units on the floor |
| 2 | 2 | Start Tile | Index of the starting tile of the floor. Indexed left to right. |
| 4 | 2 | End Tile | Index of the ending tile of the floor. Indexed left to right. |

### Unit List

There is a "Unit Count" number of 18 Byte units next.
| Offset | Length | Use | Notes |
| --- | --- | --- | --- |
| 0 | 2 | Start Tile | Index of the starting tile of the floor. Indexed left to right. |
| 2 | 2 | End Tile | Index of the ending tile of the floor. Indexed left to right. |
| 4 | 1 | Unit Type | Unit Type. See Unit Type table below. |
| 5 | 1 | Unknown 1B - 1 | Unknown |
| 6 | 1 | Unknown 1B - 2 | Unknown |
| 7 | 1 | Unknown 1B - 3 | Unknown |
| 8 | 4 | Unknown 4B - 1 | Unknown |
| 12 | 4 | Unknown 1B - 4 | Unknown |
| 13 | 4 | Unknown 1B - 5 | Unknown |
| 14 | 4 | Unknown 1B - 6 | Unknown |
| 15 | 4 | Unknown 1B - 7 | Unknown |
| 16 | 1 | Rent/Lease Rate | 0 = Very low, 1 = Low, 2 = Average, 3 = High, 4 = No Rate |
| 17 | 1 | Unknown 1B - 8 | Unknown |

#### Unit Type

| Index | Unit Type | Notes |
| --- | --- | --- |
| 0 | Empty Floor | |
| 3 | Single Hotel Room | |
| 4 | Double Hotel Room | |
| 5 | Suite Hotel Room | |
| 6 | Restuarant | |
| 7 | Office | |
| 9 | Condo | |
| 10 | Shop | |
| 11 | Parking Stall | |
| 12 | Fast Food | |
| 13 | Medical | |
| 14 | Security Office | |
| 15 | Housekeeping | |
| 18 | Theatre | Top Half |
| 19 | Theatre | Bottom Half |
| 20 | Recycling Depot | Top half |
| 21 | Recycling Depot | Bottom half |
| 24 | Lobby (1F) | |
| 29 | Party Hall | Top Half |
| 30 | Party Hall | Bottom Half |
| 31 | Metro Station | Top Part |
| 32 | Metro Station | Middle Part |
| 33 | Metro Station | Bottom Part |
| 36 | Cathedral | Top Part |
| 37 | Cathedral | Top Middle Part |
| 38 | Cathedral | Middle Part |
| 39 | Cathedral | Bottom Middle Part |
| 40 | Cathedral | Bottom Part |
| 44 | Parkade Ramp | |
| 45 | Metro Tunnel | |
| 45 | Burned Area | From after a fire or a bombing. |

#### Hotel Room Specific Values

The last byte (at offset 17) seems to be the count of days a hotel room has been dirty for. (Keeping in mind 3 days means it gets infested and needs to be demolished.)

Byte at offset 5 seems to be bit flags:

| 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Unused? | Bug infested | Dirty | Occupied at Night | Booked but empty | Unused? | Count | Count |

Examples:
| Integer | Bits | Condition |
| --- | --- | --- |
| 1 | 0000 0001 | Morning, one occupant |
| 2 | 0000 0010  | Morning, two occupants |
| 8 | 0000 1000 | Booked, but empty room |
| 9 | 0000 1001 | Room with one occupant |
| 10 | 0000 1010 | Room with two occupants |
| 16 | 0001 0000 | Overnight sleeping |
| 24 | 0001 1000 | Newly contructed/clean |
| 32 | 0010 0000 | Empty at night |
| 40 | 0010 0000 | Dirty |
| 64 | 0100 0000 | Bug Infested |

#### Shop Specific Value

The byte at offset 15 seems to be either 0, 1, 2 or 255 (or perhaps -1), with 255 indicating that the shop is empty (in this case, freshly built).

## Unknown 16B Structure

After the floor data is some unknown data. The first 4 bytes is the count of following 16 Byte entries.
