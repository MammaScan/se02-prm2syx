# SE-02 PRM → SYX Converter (prm2syx)

## Download

For non-technical users, the easiest way to get this tool is via the **Releases** page:

https://github.com/MammaScan/se02-prm2syx/releases

If you just want the current CLI script directly, download:

https://raw.githubusercontent.com/MammaScan/se02-prm2syx/main/bin/prm2syx

This project solves a practical gap in the Roland SE-02 workflow.

The SE-02 can export patches as **PRM files** through its USB mass-storage backup mode, while most librarians and editors (for example **KnobKraft Orm**) work with **SysEx (.syx)** patch dumps.

Roland does not provide an official way to convert PRM files into SysEx.

**prm2syx** fills that gap by converting a Roland SE-02 **PRM parameter file** into a valid **SE-02 SysEx patch dump** (4 × Roland DT1 messages).

---

## Status

- Version: **2.0.0**
- Canonical CLI tool: `bin/prm2syx`

---

## What's new in v2

This release establishes the **canonical PRM → SYX converter** and introduces the first graphical prototype.

New in this version:

- Canonical CLI converter: `bin/prm2syx`
- First GUI prototype: `dev/gui_v1.py`
- Clean project structure
- Dedicated test directory with reference patches

Planned next steps:

- Patch **Evolve** mode
- GUI improvements
- Possible integration with SE‑02 librarian workflows (e.g. KnobKraft Orm)

---

---

## Quick start

From the project root:

```bash
cd bin
./prm2syx --version
```

---

## Usage

### Convert a single PRM file

```bash
./prm2syx SE02_PATCH60.PRM
```

The patch slot is automatically detected from filenames such as:

```text
SE02_PATCH60.PRM
PATCH60.PRM
PATCH_60.PRM
PATCH 60.PRM
60.PRM
060.PRM
```

If the filename does not contain a slot number, you can specify it manually:

```bash
./prm2syx MySound.PRM --slot 60
```

---

## Batch conversion

Convert all PRM files in a folder (non-recursive):

```bash
./prm2syx /path/to/PATCH/
```

Convert multiple files:

```bash
./prm2syx *.PRM
```

---

## Output behavior

**Single file conversion**

Output is written next to the input PRM file by default.

**Batch conversion**

Output files are written to:

```text
out_sysex/
```

in the directory where the command is executed.

You can choose a custom output folder:

```bash
./prm2syx PATCH/ --outdir /path/to/out_sysex
```

For single-file conversion you may specify an explicit output file:

```bash
./prm2syx SE02_PATCH60.PRM --out output.syx
```

---

## Optional template

The converter contains an embedded default patch template.

If you want to base the conversion on a specific patch dump instead, you can supply a template SysEx file:

```bash
./prm2syx SE02_PATCH60.PRM --template some_patch_dump.syx
```

---

## Known limitations

The following parameters appear **not to be stored in the SE-02 patch payload** and are therefore ignored during conversion:

```text
COM_OCT
COM_TRNS
COM_PWM_DEPTH
COM_PWM_RATE
```

These behave more like UI or performance parameters rather than stored patch data.

---

## Test files

Example test files are available in the `test/` directory.

Example:

```bash
cd bin
./prm2syx ../test/TEST.PRM --slot 60
```

---

## Project goal

The long-term goal of this project is to make SE-02 patch data more accessible for:

- librarian software
- patch analysis
- automated patch generation
- integration with SE-02 tooling (for example KnobKraft Orm adaptations)

Future directions may include:

- a graphical version of the converter
- direct integration with editor/librarian workflows
- patch morphing tools

---

## License

See the `LICENSE` file included in this repository.
