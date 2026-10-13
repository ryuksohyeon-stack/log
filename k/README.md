Map files for star-rail-map.html (widget 16, built by maps/widget16.py): the
maps in maps/kremlin/ with the shop markers and numbered banner spots drawn in
(python3 maps/bake.py maps/kremlin k 34; r1 and r2 come from
python3 maps/build.py --theme ash), plus b1.svg, a stand-in banner.
n1 and n2 hold both Norilsk palettes side by side, white night on the left and
polar night on the right; the widget shows one half. o2 is the modern quarter's
2nd floor (the company). on.svg holds the picked markers in red-orange.
r2 carries draft A of the B1 rooms 12 and 13; r2b and r2c are drafts B and C
(python3 maps/build.py --theme ash r2b r2c), not linked from the widget.
Every map runs a quarter past its 1280x1000 core on each side (viewBox
-320 -250 1920 1500), so the widget's map can be dragged past the core's edge.
They sit in a short folder so the widget's image links stay short.
