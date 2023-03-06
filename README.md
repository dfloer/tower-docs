# SimTower Documentation

Documentation related to Maxis published, and Yoot Saito developed, SimTower.

## License

### Documentation

[![licensebuttons by-sa](https://licensebuttons.net/l/by-sa/3.0/88x31.png)](https://creativecommons.org/licenses/by-sa/4.0)\
The documentation (markdown files) is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/).

### Code

The code (Python code) is licensed under an [AGPL 3.0 License](https://www.gnu.org/licenses/agpl-3.0.en.html).

## Contents

- [tdt_spec.md](tdt_spec.md): SimTower .TDT file format specification. It's partial, but has most of the file structure completely documented, as well as a bunch of detailis on specific items.
- `reference/read_tdt.py`: An experimental implementation of a file reader that does so in a declarative sort of way.
  - It's not done as doing non-imperative code for this is a bit more challenging.
- `reference/temp_open_tower.py`: Quick and dirty code to open tower data.
  - Useful for reverse engineering, but not much else. This is extremely rough, and has various image generating code commented out at the bottom. This is included as an example only and really shouldn't be used for much.
  - **This will likely be abandoned if I ever finish `read_tdt.py`.**
