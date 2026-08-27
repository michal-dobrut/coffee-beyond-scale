# Data

## Capture

Beans are spread in a single layer on a white A4 sheet, with the whole sheet
inside the frame and its four corners unoccluded. One photograph per session.

## Ground truth

Each session records the dose on a digital scale, in grams, alongside the
photograph. The scale reading is the target; nothing in the pipeline sees it.

## What is stored

Photographs and trained weights are not committed. Sessions are tracked in
`data/manifest.csv`, which is committed, and the images it names are fetched
separately.

## Sessions

Validation sessions hold the jar constant, isolating pipeline error from
population error. Calibration sessions vary roast level and bean size, which is
what a mean bean mass must generalise across.

TODO: the split between sessions used to fit and sessions used to measure
coverage is not yet defined.
