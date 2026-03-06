# SE-02 PROJECT MAP

Orientation document for the SE-02 project.

This file is not forensic.
For verified technical truth, use the forensic log.

## Purpose

This file explains how the project is organized and where the important parts live.

## Main components

The SE-02 project currently has three main parts:

1. PRM to SYX converter
2. ORM adaptation work
3. Reverse engineering research

## Converter

Canonical converter:

bin/prm2syx

Current role:

- convert Roland SE-02 PRM files into SysEx patch dumps
- act as the stable technical base for future tools

Current version:

- CLI v2.0.0

Future directions:

- GUI version
- ORM integration
- patch morphing
- patch analysis

## ORM adaptation work

Purpose:

- librarian integration
- patch browsing
- SysEx import and export
- communication with hardware

Relationship to converter:

ORM works primarily with SysEx.
The converter allows PRM backup files to be turned into SysEx so they can be used in ORM workflows.

## Research

Location:

research/

Contains:

- reverse engineering notes
- algorithm ideas
- format experiments
- future tools such as patch morphing

## Archive

Location:

archive_v1/

Contains:

- older scripts
- historical datasets
- early reverse engineering material

Archive is kept locally for reference but is not part of the main GitHub repo.

## Project structure

Typical structure:

- bin/        canonical converter
- test/       test PRM and SYX files
- research/   ongoing experiments and future tools
- archive_v1/ historical material
- README.md   public project documentation
- PROJECT_MAP.md  this file

## Canonical sources

Converter:
- bin/prm2syx

Technical ground truth:
- forensic log

Project orientation:
- PROJECT_MAP.md

## Development direction

Near-term priorities:

1. GUI version of the converter
2. possible ORM integration
3. patch morphing and other patch tools later

The converter is currently the foundation for all future development.
