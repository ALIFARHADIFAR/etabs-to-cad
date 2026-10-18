# Copyright (c) 2026 Ali Farhadifar. All rights reserved. Shown for viewing only.
"""Batten (lacing) plate layout for a built-up double-channel/double-I column.

Excerpt of the column elevation logic. Given one column piece (bottom and top
level in cm), the solid zones around the beams that frame into it, and the
section's radii of gyration, it places the batten plates in the free length
between the solid zones and returns closed rectangles ready to be drawn.

All levels are in centimetres; the returned spacing is in metres.
Standalone: no dependencies outside the standard library.
"""

BATTEN_THICKNESS_MM = 6


def solid_zone(beam_top, beam_depth, above=30, under=30, minimum=90):
    """Solid (fully plated) zone around a beam, in cm.

    Thirty centimetres stay above the beam. Below the beam top the zone takes
    the larger of (minimum - above) and (beam depth + under), so the zone is at
    least ninety centimetres tall and at least thirty centimetres below the beam.
    """
    down = max(minimum - above, beam_depth + under)
    return beam_top - down, beam_top + above


def _callout_number(number):
    """Integer text when whole, otherwise up to four decimals without trailing zeros."""
    value = float(number)
    if abs(value - round(value)) < 1e-6:
        return str(int(round(value)))
    return f"{value:.4f}".rstrip("0").rstrip(".")


def batten_text(bast1_cm, bast2_cm, spacing_m):
    """Leader text of a batten plate: PL<length>*<width>*<thickness> C/C <spacing>cm."""
    return "PL%s*%s*%s C/C %scm" % (
        _callout_number(bast1_cm * 10),
        _callout_number(bast2_cm * 10),
        BATTEN_THICKNESS_MM,
        _callout_number(spacing_m * 100),
    )


def batten_spacing(story_cm, rd1, rd2, rt1, rt2, above=0.3, below=0.6):
    """Centre-to-centre batten spacing in metres.

    `above` and `below` (m) are the solid zones at the two ends of the piece.
    The governing reach is the piece length over the smallest whole-section
    radius, times 0.75 and the smallest single-chord radius; the clear length
    is then split into equal bays no longer than that reach.
    """
    rs = min(rd1, rd2)
    rp = min(rt1, rt2)
    if not rs:
        raise ZeroDivisionError
    reach = story_cm / rs * 0.75 * rp
    clear = (story_cm - above * 100 - below * 100) * 0.01
    count = int(clear * 100 / reach) + 1
    return clear / count


def _end_intrusion(z0, z1, solids, tolerance=1):
    """Solid length attached to the two ends of the piece, in cm.

    A solid zone in the middle of the piece does not count.
    """
    bottom = 0.0
    top = 0.0
    for start, end in solids:
        low = max(start, z0)
        high = min(end, z1)
        if high - low <= tolerance:
            continue
        if start <= z0 + tolerance:
            bottom = max(bottom, high - z0)
        if end >= z1 - tolerance:
            top = max(top, z1 - low)
    return bottom, top


def batten_rects(z0, z1, solids, props):
    """Batten plates in the free length between the solid zones.

    The piece length stands in for the story height in the spacing formula,
    because a battened piece may not cover the whole story.
    Each plate is a closed rectangle centred on the column axis (x = 0).
    """
    bottom, top = _end_intrusion(z0, z1, solids)
    story = z1 - z0
    clear = story - bottom - top
    if clear <= 1 or props is None:
        return []
    spacing = batten_spacing(
        story, props["rd1"], props["rd2"], props["rt1"], props["rt2"],
        above=bottom / 100, below=top / 100,
    )
    reach = story / min(props["rd1"], props["rd2"]) * 0.75 * min(props["rt1"], props["rt2"])
    count = int(clear / reach) + 1
    if count < 2:
        return []
    half = props["b"] / 2
    label = batten_text(props["bast1"], props["bast2"], spacing)
    rects = []
    for index in range(1, count):
        y0 = z0 + bottom + index * spacing * 100
        y1 = y0 + props["d"]
        rects.append({
            "closed": True,
            "spacing_m": spacing,
            "text": label,
            "points": [
                (-half, y0),
                (half, y0),
                (half, y1),
                (-half, y1),
                (-half, y0),
            ],
        })
    return rects


if __name__ == "__main__":
    # Fictitious input: a 320 cm column piece with a 40 cm deep beam at each end.
    piece_bottom, piece_top = 0, 320
    solids = [
        solid_zone(beam_top=piece_bottom, beam_depth=40),
        solid_zone(beam_top=piece_top, beam_depth=40),
    ]
    section = {
        "rd1": 6.0, "rd2": 7.5,   # radii of the whole built-up section, cm
        "rt1": 6.0, "rt2": 1.7,   # radii of a single chord, cm
        "b": 14, "d": 7,          # plate size drawn in elevation, cm
        "bast1": 14, "bast2": 7,  # plate size written in the leader, cm
    }
    for rect in batten_rects(piece_bottom, piece_top, solids, section):
        y0 = rect["points"][0][1]
        print(f"plate at {y0:6.1f} cm  {rect['text']}")
