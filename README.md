# etabs-to-cad

Early-stage tool that turns ETABS models (e2k) into standardized, code-aware structural shop drawings in AutoCAD.

## The gap
ETABS gives analysis results, but the drawings that reach the site are often prepared by hand and omit details such as weld lengths, rebar lap lengths and execution notes.

## Status
Working: bracing, steel columns and shear-wall reinforcement drawings. Planned next: beams (with cover plates and a schedule), base plates and foundations. Not deployed; no public releases yet.

## What is in this repo
- docs/images: sample drawings generated from a fictional model
- samples: a small fictional ETABS model and its output
- examples: a short excerpt of the column module (an excerpt, not a complete program)

The full source is not published.

## Approach
A shared drawing standard plus a local knowledge base (rules, lessons and reference drawings) that grows with each project.

## License
All rights reserved. Shown for viewing only. See LICENSE.