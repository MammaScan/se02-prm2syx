# SE-02 PRM → SYX Converter (prm2syx)

Detta projekt löser ett konkret glapp i Roland SE-02-flödet:

- SE-02 kan göra USB-backup i PRM-format (Mass Storage).
- Librarians/editors (t.ex. Orm) jobbar med SysEx (SYX).
- Roland erbjuder ingen officiell PRM → SYX-konvertering.

prm2syx konverterar därför SE-02 PRM (text/parameterlista) till en valid SE-02 patch SysEx dump (4 × Roland DT1).

## Status

- Version: 2.0.0
- Canonical CLI: bin/prm2syx

## Snabbstart

  cd bin
  ./prm2syx --version

## Användning

Konvertera en PRM-fil:
  ./prm2syx SE02_PATCH60.PRM

Slot autodetekteras från filnamn som t.ex.:
  SE02_PATCH60.PRM
  PATCH60.PRM
  PATCH_60.PRM
  PATCH 60.PRM
  60.PRM / 060.PRM

Om filnamnet inte innehåller slot, ange manuellt:
  ./prm2syx MySound.PRM --slot 60

Batch (mapp, icke-rekursivt):
  ./prm2syx /path/to/PATCH/

Batch (många filer):
  ./prm2syx *.PRM

## Output-regler

- Single-file: output skrivs bredvid PRM-filen (default).
- Batch (flera filer eller folder-input): output skrivs i out_sysex/ (default) i den mapp där du kör kommandot.

Välj egen output-folder:
  ./prm2syx PATCH/ --outdir /path/to/out_sysex

--out används bara vid single-file:
  ./prm2syx SE02_PATCH60.PRM --out out.syx

## Template (valfritt)

  ./prm2syx SE02_PATCH60.PRM --template some_patch_dump.syx

## Begränsningar / kända not stored

- COM_OCT
- COM_TRNS
- COM_PWM_DEPTH
- COM_PWM_RATE

## Testdata

Testfiler finns i `test/`.

Exempel:

  cd bin
  ./prm2syx ../test/TEST.PRM --slot 60
