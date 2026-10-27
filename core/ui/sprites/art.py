"""Pixel art for Jenbina, as palette-key strings.

Every layer is ``(x, y, rows)`` on a 48x48 canvas. Keys are the ones in
``palette.PALETTE``; ``"."`` is transparent and leaves what is underneath.

Layout grid (x, y): hair (10, 2) 28x16; head (12, 6) 24x22; face overlay
(16, 14) 16x10; torso + collar (14, 28) 20x14; legs (14, 40) 20x8; hand prop
(30, 30) 14x14; speech lines (2, 16) 10x10; effect (34, 2) 12x12; tear
(18, 22) 4x6.
"""

from core.ui.sprites.palette import FrameSpec, Layer

# --------------------------------------------------------------------------
# Shared body: head, collar, suit, arms and default boots. 24 wide, 42 tall.
# --------------------------------------------------------------------------
BODY: Layer = (12, 6, [
    "......KKKKKKKKKKKK......",  # y=6
    "....KKSSSSSSSSSSSSKK....",
    "...KSSSSSSSSSSSSSSSsK...",
    "..KSSSSSSSSSSSSSSSSssK..",
    ".KSSSSSSSSSSSSSSSSSSssK.",  # y=10
    ".KSSSSSSSSSSSSSSSSSSssK.",
    ".KSSSSSSSSSSSSSSSSSSssK.",
    ".KSSSSSSSSSSSSSSSSSSssK.",
    ".KSSSSSSSSSSSSSSSSSSssK.",
    ".KSSSSSSSSSSSSSSSSSSssK.",  # y=15
    ".KSSSSSSSSSSSSSSSSSSssK.",
    ".KSSSSSSSSSSSSSSSSSSssK.",
    ".KSSSSSSSSSSSSSSSSSSssK.",
    ".KSSSSSSSSSSSSSSSSSSssK.",
    ".KSSSSSSSSSSSSSSSSSSssK.",  # y=20
    ".KSSSSSSSSSSSSSSSSSSssK.",
    ".KSSSSSSSSSSSSSSSSSSssK.",
    ".KSSSSSSSSSSSSSSSSSSssK.",
    "..KSSSSSSSSSSSSSSSSssK..",  # y=24
    "...KSSSSSSSSSSSSSSSsK...",
    "....KKSSSSSSSSSSSSKK....",
    "......KKKKKKKKKKKK......",  # y=27 chin
    "......KKTTTTTTTTKK......",  # y=28 collar
    "....KKTTTTTTTTTTTTKK....",
    "..KTTTTTTTTTTTTTTTTTTK..",  # y=30 shoulders
    "..KAAAKAAAAAAAAAAKaaaK..",
    "..KAAAKAAAAAAAAaaKaaaK..",
    "..KAAAKAAABBAAAaaKaaaK..",  # y=33 badge
    "..KAAAKAAABBAAAaaKaaaK..",
    "..KAAAKAAAAAAAAaaKaaaK..",  # y=35
    "..KAAAKTTTTTTTTTTKaaaK..",  # y=36 belt
    "..KAAAKAAAAAAAAaaKaaaK..",
    "..KSSSKAAAAAAAAaaKsssK..",  # y=38 hands
    "...KKKKAAAAAAAAaaKKKK...",
    ".....KKKKKKKKKKKKKK.....",  # y=40 hip line
    ".....KAAAAAKKAAAAAK.....",
    ".....KAAAAAKKAAAAAK.....",
    ".....KAAAAAKKAAAAAK.....",
    "....KKKKKKKKKKKKKKKK....",  # y=44 boot tops
    "....KaaaaaaKKaaaaaaK....",
    "....KaaaaaaKKaaaaaaK....",
    "....KKKKKKKKKKKKKKKK....",  # y=47
])

# Dark bob with highlights, bangs ending in three points, side locks.
HAIR: Layer = (10, 2, [
    "..........KKKKKKKK..........",  # y=2
    ".......KKKHHHHHHHHKKK.......",
    ".....KKHHHhhHHHHHHHHHKK.....",
    "....KHHHHhhhHHHHHHHHHHHK....",
    "...KHHHHHhhhHHHHHHHHHHHHK...",  # y=6
    "..KHHHHHHHhhHHHHHHHHHHHHHK..",
    ".KHHHHHHHHHhHHHHHHHHHHHHHHK.",
    "KHHHHHHHHHHHHHHHHHHHHHHHHHHK",
    "KHHHHHHHHHHHHHHHHHHHHHHHHHHK",  # y=10
    "KHHHHHHHHHHHHHHHHHHHHHHHHHHK",
    "KHHHHHHHHHHHHHHHHHHHHHHHHHHK",
    "KHHHKKKHHKKKHHHHKKKHHKKKHHHK",  # y=13 bang edge
    "KHHHK..KK...KKKK...KK..KHHHK",  # y=14 bang points
    "KHHHK..................KHHHK",
    "KHHHK..................KHHHK",  # y=16
    ".KKKK..................KKKK.",  # y=17
])

# --------------------------------------------------------------------------
# Faces: 16x10 overlays at (16, 14). Eyes in rows 2-4, mouth in rows 7-9.
# --------------------------------------------------------------------------
_FACE_ROWS = {
    "neutral": [
        "................",
        "................",
        "...KK......KK...",
        "..KEWK....KEWK..",
        "...KK......KK...",
        ".BB.........BB..",
        "................",
        "................",
        ".......KK.......",
        "................",
    ],
    "smile": [
        "................",
        "................",
        "...KK......KK...",
        "..KEWK....KEWK..",
        "...KK......KK...",
        ".BB.........BB..",
        "................",
        ".....K....K.....",
        "......KKKK......",
        "................",
    ],
    "sad": [
        "................",
        "....KK....KK....",
        "...KK......KK...",
        "..KEWK....KEWK..",
        "...KK......KK...",
        ".BB.........BB..",
        "................",
        ".......KK.......",
        "......K..K......",
        "................",
    ],
    "angry": [
        "................",
        "..KK........KK..",
        "....KK....KK....",
        "..KEWK....KEWK..",
        "...KK......KK...",
        ".BB.........BB..",
        "................",
        "................",
        ".....KKKKKK.....",
        "................",
    ],
    "fear": [
        "................",
        "................",
        "..KKKK....KKKK..",
        "..KWEK....KWEK..",
        "..KKKK....KKKK..",
        ".BB.........BB..",
        "................",
        "......K..K......",
        ".....K.KK.K.....",
        "................",
    ],
    "surprised": [
        "...KK......KK...",
        "................",
        "...KK......KK...",
        "..KEWK....KEWK..",
        "...KK......KK...",
        ".BB.........BB..",
        "................",
        ".......KK.......",
        "......KMMK......",
        ".......KK.......",
    ],
    "thinking": [
        "................",
        "...........KK...",
        "...KK......KK...",
        "..KWEK....KWEK..",
        "...KK......KK...",
        ".BB.........BB..",
        "................",
        "................",
        "........KK......",
        "................",
    ],
    "reading": [
        "................",
        "................",
        "..KKKK....KKKK..",
        "..KEWK....KEWK..",
        "...KK......KK...",
        ".BB.........BB..",
        "................",
        "................",
        ".......KK.......",
        "................",
    ],
    "asleep": [
        "................",
        "................",
        "................",
        "..K..K....K..K..",
        "...KK......KK...",
        "................",
        "................",
        "................",
        ".......K........",
        "................",
    ],
    "blink": [
        "................",
        "................",
        "................",
        "..KKKK....KKKK..",
        "................",
        ".BB.........BB..",
        "................",
        "................",
        ".......KK.......",
        "................",
    ],
    "talk_open": [
        "................",
        "................",
        "...KK......KK...",
        "..KEWK....KEWK..",
        "...KK......KK...",
        ".BB.........BB..",
        "................",
        "......KKKK......",
        "......KMMK......",
        "......KKKK......",
    ],
}
FACES: dict[str, Layer] = {name: (16, 14, rows) for name, rows in _FACE_ROWS.items()}

# --------------------------------------------------------------------------
# Props (hand prop at (30, 30), speech lines at (2, 16), legs at (14, 40)).
# --------------------------------------------------------------------------
PROPS: dict[str, Layer] = {
    # Bowl of food held at the right hand, fork raised.
    "bowl_fork_up": (30, 30, [
        "......K.K.....",
        "......KKK.....",
        ".......K......",
        ".......K......",
        ".......K......",
        "..............",
        "...KRRRRRRK...",
        "..KRRRRRRRRK..",
        ".KWWWWWWWWWWK.",
        ".KWWWWWWWWWWK.",
        "..KWWWWWWWWK..",
        "...KWWWWWWK...",
        "....KKKKKK....",
        "..............",
    ]),
    # Same bowl, fork dipped into the food.
    "bowl_fork_down": (30, 30, [
        "..............",
        "..............",
        ".......K......",
        ".......K......",
        ".......K......",
        "......KKK.....",
        "...KRRK.KRRK..",
        "..KRRRRRRRRK..",
        ".KWWWWWWWWWWK.",
        ".KWWWWWWWWWWK.",
        "..KWWWWWWWWK..",
        "...KWWWWWWK...",
        "....KKKKKK....",
        "..............",
    ]),
    # Mug with teal drink, upright at the hand.
    "cup": (30, 30, [
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "...KKKKKKK....",
        "...KTTTTTK....",
        "...KTTTTTKKK..",
        "...KWWWWWK.K..",
        "...KWWWWWKKK..",
        "...KWWWWWK....",
        "....KKKKK.....",
        "..............",
    ]),
    # Mug raised and tipped.
    "cup_tilt": (30, 30, [
        "..............",
        "...KKKKKKK....",
        "...KTTTTTK....",
        "...KWTTTTKKK..",
        "...KWWTTTK.K..",
        "...KWWWWWKKK..",
        "...KWWWWWK....",
        "....KKKKK.....",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
    ]),
    # Open book, brown cover, white pages with text lines.
    "book": (30, 30, [
        "..............",
        "..............",
        "..............",
        ".KKKKKKKKKKKK.",
        ".KNWWWWNWWWWNK",
        ".KNWWWWNWWWWNK",
        ".KNWKWWNWWKWNK",
        ".KNWWWWNWWWWNK",
        ".KNWKWWNWWKWNK",
        ".KNWWWWNWWWWNK",
        ".KNNNNNNNNNNNK",
        ".KKKKKKKKKKKK.",
        "..............",
        "..............",
    ]),
    # Three short dashes left of the face.
    "speech_lines": (2, 16, [
        "..........",
        ".....WWW..",
        "..........",
        "...WWWWW..",
        "..........",
        ".....WWW..",
        "..........",
        "..........",
        "..........",
        "..........",
    ]),
    # Walking: left boot forward (wider, lit), right boot planted.
    "legs_a": (14, 40, [
        "...KKKKKKKKKKKKKK...",
        "...KAAAAAKKAAAAAK...",
        "...KAAAAAKKAAAAAK...",
        "..KKAAAAAKKAAAAAK...",
        ".KKKKKKKKKKKKKKKKK..",
        ".KAAAAAAAKKaaaaaaK..",
        ".KaaaaaaaKKaaaaaaK..",
        ".KKKKKKKKKKKKKKKKK..",
    ]),
    # Walking: right boot forward.
    "legs_b": (14, 40, [
        "...KKKKKKKKKKKKKK...",
        "...KAAAAAKKAAAAAK...",
        "...KAAAAAKKAAAAAK...",
        "...KAAAAAKKAAAAAKK..",
        "..KKKKKKKKKKKKKKKKK.",
        "..KaaaaaaKKAAAAAAAK.",
        "..KaaaaaaKKaaaaaaaK.",
        "..KKKKKKKKKKKKKKKKK.",
    ]),
}

# --------------------------------------------------------------------------
# Effects: top-right at (34, 2) 12x12, tear at (18, 22) 4x6.
# --------------------------------------------------------------------------
EFFECTS: dict[str, Layer] = {
    "tear": (18, 22, [
        ".E..",
        ".E..",
        ".EE.",
        "EWE.",
        ".EE.",
        "....",
    ]),
    "anger_mark": (34, 2, [
        "............",
        "......R.....",
        "......R.....",
        "......R.....",
        "............",
        "..RRR...RRR.",
        "............",
        "......R.....",
        "......R.....",
        "......R.....",
        "............",
        "............",
    ]),
    "sweat_drop_a": (34, 2, [
        "............",
        "............",
        "....E.......",
        "...EEE......",
        "...EWE......",
        "..EEEEE.....",
        "...EEE......",
        "............",
        "............",
        "............",
        "............",
        "............",
    ]),
    "sweat_drop_b": (34, 2, [
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "....E.......",
        "...EEE......",
        "...EWE......",
        "..EEEEE.....",
        "...EEE......",
        "............",
    ]),
    "question_a": (34, 2, [
        "............",
        ".....YYY....",
        "....Y...Y...",
        "........Y...",
        ".......Y....",
        "......Y.....",
        "......Y.....",
        "............",
        "......Y.....",
        "............",
        "............",
        "............",
    ]),
    "question_b": (34, 2, [
        "............",
        "............",
        "......YYY...",
        ".....Y...Y..",
        ".........Y..",
        "........Y...",
        ".......Y....",
        ".......Y....",
        "............",
        ".......Y....",
        "............",
        "............",
    ]),
    "zzz_a": (34, 2, [
        "............",
        ".......WWWW.",
        ".........W..",
        "........W...",
        ".......WWWW.",
        "............",
        "...WWW......",
        "....W.......",
        "...WWW......",
        "............",
        "............",
        "............",
    ]),
    "zzz_b": (34, 2, [
        ".......WWWW.",
        ".........W..",
        "........W...",
        ".......WWWW.",
        "............",
        "....WWW.....",
        ".....W......",
        "....WWW.....",
        "............",
        "............",
        "............",
        "............",
    ]),
}


def _frame(face: str, props: tuple[str, ...] = (), effects: tuple[str, ...] = (), dy: int = 0) -> FrameSpec:
    return {"face": face, "props": list(props), "effects": list(effects), "dy": dy}


# State -> (frame 0, frame 1), in the spec's order.
STATE_FRAMES: dict[str, tuple[FrameSpec, FrameSpec]] = {
    "base": (_frame("neutral"), _frame("blink")),
    "smile": (_frame("smile"), _frame("blink")),
    "sad": (_frame("sad", effects=("tear",)), _frame("blink", effects=("tear",))),
    "angry": (_frame("angry", effects=("anger_mark",)), _frame("blink", effects=("anger_mark",))),
    "scary": (_frame("fear", effects=("sweat_drop_a",)), _frame("fear", effects=("sweat_drop_b",))),
    "surprised": (_frame("surprised"), _frame("blink")),
    "thinking": (_frame("thinking", effects=("question_a",)), _frame("thinking", effects=("question_b",))),
    "eat": (_frame("smile", props=("bowl_fork_up",)), _frame("smile", props=("bowl_fork_down",))),
    "drink": (_frame("neutral", props=("cup",)), _frame("neutral", props=("cup_tilt",))),
    "read": (_frame("reading", props=("book",)), _frame("blink", props=("book",))),
    "sleep": (_frame("asleep", effects=("zzz_a",)), _frame("asleep", effects=("zzz_b",))),
    "talk": (_frame("talk_open", props=("speech_lines",)), _frame("smile")),
    "walks": (_frame("neutral", props=("legs_a",)), _frame("neutral", props=("legs_b",), dy=-1)),
}
