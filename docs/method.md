# Method

A dose of beans is recovered from one photograph in two steps: rectify, then
measure.

The beans are spread on a sheet of paper whose dimensions are known — A4, ISO
216. Its four corners in the image give the homography that removes
perspective, and its known width fixes the scale in millimetres per pixel.
Everything downstream works on the rectified image, where a pixel has a
constant physical area.

From there, two routes reach a mass. The **area route** measures the
coffee-coloured area and multiplies by an area-to-mass ratio. The **count
route** counts individual beans and multiplies by a mean bean mass. The count
route is the one with a defensible error model, because the mass of a sum of
beans concentrates as the count grows — see the error budget in
`uncertainty.md`.

Three pipelines produce those measurements: coloured-area thresholding, classic
morphological segmentation, and a trained detector. They share the
rectification step and differ only after it.

TODO: mean bean mass is a per-jar constant here; predicting it from roast level
and bean size is the open problem.
