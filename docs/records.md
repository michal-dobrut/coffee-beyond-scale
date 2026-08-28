# Data

Conventions that hold across every campaign. What a campaign captures, and
under what conditions, belongs to its own protocol.

## Raw captures are immutable

Photographs and balance readings are written once and never edited. Rectified
images, masks, crops and derived tables are regenerated from them rather than
repaired. The originals and their EXIF are the record.

Images move from the camera by cable. Messaging apps and some cloud syncs
recompress and strip EXIF, and the focal length does not come back.

## What is committed

Photographs, balance logs and trained weights are not. A manifest naming the
sessions is, and the files it names are fetched separately.

A session leaves two records. The filled protocol sheet is the one a person
reads, and it carries the conditions and the anomalies that no instrument
logged. The manifest is the one the pipeline reads.

## Synthetic scenes are derived, not recorded

Rendered ellipses and composited bean cutouts carry ground truth with no error
bar of its own, which is what makes them useful for measuring a pipeline
against a known answer. They are stored as derived artifacts, never enter the
record of measured sessions, and a result quoted on them says so.
