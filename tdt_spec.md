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

### Date Notes

A week is three days long. 2 weekdays and one weekend day. A year has 4 quarters, with each being one week long, so a year is 12 days long. This rolls over after 11,987 days (1000 years).

This is a signed integer, so negative days are not allowed, and cause issues for the game.

Examples:

| Day Counter | In Game Date |
| --- | --- |
| 0 | WD=1, Q=1, Year=1 |
| 5 | WE, Q=2, Year=1 |
| 427 | WD=2, Q=3, Year=36 |
| 1212 | WD=1, Q=1, Year=102 |
| 4292 | WE, Q=3, Year=358 |
| 11987 | WE, Q=3, Year=999 |

## Floor Data

After the first 68 bytes of the file, this is where actual tower data seems to reside. There is a 490 Byte segment that is unknown

There are 120 entries (10 underground floors, 100 normal floors and probalby 10 floors for the Cathedral and open space/padding).

Each floor has a 6 Byte floor header (which includes a count), that count * 18B with one per unit on the floor and finally a 188B data structure after that, which is for remapping the unit index on the floor, say after a unit is demolished and rebuilt.

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
| 24 | Lobby | 2 and 3 floor lobby is not stored differently. |
| 29 | Party Hall | Top Half |
| 30 | Party Hall | Bottom Half |
| 31 | Metro Station | Top Part |
| 32 | Metro Station | Middle Part |
| 33 | Metro Station | Bottom Part |
| 34 | Theatre - Screen | Top Half |
| 35 | Theatre - Screen | Bottom Half |
| 36 | Cathedral | Top Part |
| 37 | Cathedral | Top Middle Part |
| 38 | Cathedral | Middle Part |
| 39 | Cathedral | Bottom Middle Part |
| 40 | Cathedral | Bottom Part |
| 44 | Parkade Ramp | |
| 45 | Metro Tunnel | |
| 48 | Burned Area | From after a fire or a bombing. |

_Note:_ The movie theatre is actually 4 parts. It's two floors, but the screen is seperate, likely so different sprites can be loaded for the different movies.

### Remap Data

The 188B section appears to be a 94 x 2B table that has something to do with mapping a unit, because indices don't appear to change in the Unit data structure when a unit is moved.

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

## People Data

After the floor data data for people related to units in the tower. The first 4 bytes is the count of following 16 Byte entries.

| Offset | Length | Use | Notes |
| --- | --- | --- | --- |
| 0 | 1 | Floor | What floor does this entry correspond to. |
| 1 | 1 | Unit Index | Index of which unit on the floor this is for. |
| 2 | 1 | Person Index | Index inside this unit. |
| 5 | 1 | Unknown bit Flags | Has values such as 4, 16, 32. Looks like bit flags of some sort. |
| 7 | 1 | Current floor | |
| 12 | 2 | Stress | |
| 14 | 2 | Eval | |

On a floor with 10 condo units, there are 30 entries, which suggests 3 entries per condo. Similarly, two restaurants is 96 entries, suggesting 48 entries per restuarant. 19 offices have 114 entries, or 6 per office, matching the in game maximum population count. The maximum number of entries is likely higher than the actual population, because not every unit is completely full all the time.

_Note:_ People don't always seem to go back to the same condo. I named a person living in a condo and that condo, and the person was living in a condo two to the right. This may be a bug.

Deleted values units still seem to have people here, at least temporarily. This will have a duplicated Unit Index, but otherwise all value, other than the bit flags (32), will be 0.

## Commercial Data

This related to commercial/retail entities. Shops, fast food places restuarants. This is a fixed length segment, with 512 entries of 18 Bytes each.

| Offset | Length | Use | Notes |
| --- | --- | --- | --- |
| 0 | 1 | Floor | What floor is this entry for? | `0xff` (or negative if signed) is an empty entry. |
| 1 | 1 |  | | |
| 2 | 1 |  | | Generally seems to be 0, 1, 2, 3 or 255. 255 May indicate empty. 3 May indicate closed for day. |
| 1 | 1 | Variant | Which variant of the unit is this? |
| 13 | 1 | Fixed | | Always 255 |
| 14 | 1 | Empty | | Always 0 |
| 15 | 1 | Empty | | Always 0 |
| 16 | 1 |  | |  |
| 17 | 1 | Empty | | Always 0 |

Shop variants:
| Variant | Type |
| --- | --- |
| 0 | Men's Clothing |
| 1 | Pet Store |
| 2 | Flower Shop |
| 3 | Book Store |
| 4 | Drug Store |
| 5 | Boutique |
| 6 | Electronics |
| 7 | Bank |
| 8 | Hair Salon |
| 9 | Post Office |
| 10 | Sports Gear |

Fast Food variants:
| Variant | Type |
| --- | --- |
| 0 | Japanese Soba |
| 1 | Chinese Cafe |
| 2 | Hamburger Stand |
| 3 | Ice Cream |
| 4 | Coffee Shop |

Restuarant variants:
| Variant | Type |
| --- | --- |
| 0 | English Pub |
| 1 | French Restuarant |
| 2 | Chinese Restuarant |
| 3 | Sushi Bar |
| 4 | Steak House |

## Elevator Data

The next segment of data is 24 entries that are 194 Bytes long, with optional other data, summarized below. The header always exists, but for non-build elevators, it is the only thing that exists.

| Length | Usage | Count | Notes |
| --- | --- | --- | --- |
| 194 | Elevator Data Header | 1 | Always exists. |
| 480 | Unknown Elevator Data | 1 | Only exists for elevators that have been built. |
| 120 | Elevator Floor Data? | 2 | Only exists for elevators that have been built. 120 entries is the number of floors, so this is probably related. |
| 324 | Elevator Floor Data | 1 to 29 | Only exists for elevators that have been built. One entry per floor. A minimum height elevator has 1 entry, a max height elevator has 29. Express elevators have one entry per floor they stop at, so seem to have a maximum of 16 entries. |
| 348 | Elevator Car Data | 1 to 8 | Only exists for elevators that have been built. One entry per floor. An elevator with 1 car has one entry, an elevator with 8 cars has 8 entries. |

_Note:_ Elevators have an entry for floor data for each floor they could stop on, even if it's disabled. This means that an express elevator extending from floor B9 (floor index: 1) for floor 100 (floor index: 109) will have 16 entries, because it can't stop at any floors except the 9 below-ground and the 7 sky lobby floors (1, 15, 30, 45, 60, 75 and 90).

### Elevator Header

| Offset | Length | Use | Notes |
| --- | --- | --- | --- |
| 0 | 1 | Used | 1 if there's an elevator, 0 otherwise. |
| 1 | 1 | Elevator Type | 0 is express, 1 is standard, 2 is service. |
| 2 | 1 | Capacity | How many people can a car hold? 42 for express, 21 for standard, 10 for service. |
| 3 | 1 | Cars count | Number of cars, between 1 and 8 inclusive. |
| 4 | 56 | Elevator Schedule | Controls the schedule for the elevator. Details below. |
| 60 | 1 | Show Elevator | 0 if hidden, 1 if shown. |
| 61 | 1 | Unknown | Seems to be unused and 0. |
| 62 | 2 | Floor Start Index | How far from the left side does this elevator start at? |
| 64 | 1 | Top Floor | |
| 65 | 1 | Bottom Floor | |
| 66 | 120 | Serviced Floors | If this elevator stops at a floor 1, else 0. One entry per floor. |
| 186 | 1 | Car 1 Home Floor | |
| 187 | 1 | Car 2 Home Floor | |
| 188 | 1 | Car 3 Home Floor | |
| 189 | 1 | Car 4 Home Floor | |
| 190 | 1 | Car 5 Home Floor | |
| 191 | 1 | Car 6 Home Floor | |
| 192 | 1 | Car 7 Home Floor | |
| 193 | 1 | Car 8 Home Floor | |

#### Elevator Header - Schedule

This section details the scheduler values set in the elevator's properties window.

| Offset | Length | Use |
| --- | --- | --- |
| 0 | 14 | Unknown (probably unused) |
| 14 | 6 | Weekday Waiting Car Response |
| 20 | 1 | Unused |
| 21 | 6 | Weekend Waiting Car Response |
| 27 | 1 | Unused |
| 28 | 6 | Weekday Priority |
| 34 | 1 | Unused |
| 35 | 6 | Weekend Priority |
| 41 | 1 | Unused |
| 42 | 6 | Weekday Standard Floor Departure |
| 38 | 1 | Unused |
| 49 | 6 | Weekend Standard Floor Departure
| 56 | 1 | Unused |

All 14 initial entries are 1, and no settings changes in the elevator window seem to affect them.

The unused single entries appear to have the same default values as the rest, so perhaps there were 7 periods at some point in the game's development, but this was later changed to 6.

For priority: 0 is normal priority, 1 is priority up and 2 is priority down.

### Elevator Floor Data

Format appears to be a 4 Byte header and 80 4B entries.

| Offset | Length | Use | Notes |
| --- | --- | --- | --- |
| 0 | 1 | Waiting - Up | Total number of people waiting at this floor to go up. |
| 1 | 1 | Unknown |  |
| 2 | 1 | Waiting - Down | Total number of people waiting at this floor to go down. |
| 3 | 1 | Unknown | |
| 4 | 160 | Person Index - Down | 40 * 4B indices to the person data segment, for people going down. |
| 164 | 160 | Person Index - Up | 40 * 4B indices to the person data segment, for people going up. |

The 2 x 40 passenger sections appear to be either all full or all empty, so it could be that old values aren't always cleared out properly. This would also indicate that at most 40 people can wait for an elevator on a floor each direction, which the game seems to cap at.

### Elevator Car Data

| Offset | Length | Use | Notes |
| --- | --- | --- | --- |
| 0 | 1 | Current Floor |  |
| 1 | 1 | Unknown |  |
| 2 | 1 | Unknown |  |
| 3 | 1 | Number of Passengers |  |
| 4 | 1 | Unknown | |
| 5 | 1 | Unknown | |
| 6 | 1 | Unknown | |
| 7 | 1 | Unknown | |
| 8 | 1 | Unknown | Looks like it could be bit flags? |
| 9 | 1 | Unknown | |
| 10 | 1 | Unknown | |
| 11 | 1 | Unknown | |
| 12 | 1 | Unknown | |
| 13 | 1 | Turnaround Floor | Floor showing u-turn symbol. |
| 14 | 1 | Unknown | |
| 15 | 1 | Built | 1 if the car exists, 0 otherwise. |
| 16 | 168 | Passenger Index | 42 entries, one 4B entry that points to an entry in the People Data segment, or `FF FF FF FF` if empty. |
| 184 | 42 | Passenger Destination Floor | What floor is a passenger getting off at? `0xff` for empty entry. Same ordering as shown in car properties. |
| 226 | 120 | Floors Destination Count | One entry per floor, containing a count of passengers going to that floor. |

Note that after a car is deleted, not all of the data structure is properly cleaned up by the game.

