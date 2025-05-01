"""
ui/avatars.py

Defines 8-bit full-body astronaut sprites for each AI agent with two frames
for a simple walking animation. Each agent is a different color (red, blue,
purple, green) wearing a space suit with a black visor.
"""

from tkinter import PhotoImage

# Each agent maps to a list of two 8×8 patterns (frame1 and frame2)
AVATAR_PATTERNS = {
    "TrendAgent": [  # Red astronaut frames
        [  # Frame 1: legs apart
            [None,   None,      "#880000", "#880000", "#880000", "#880000", None,      None],
            [None,   "#880000", "#000000", "#000000", "#000000", "#000000", "#880000", None],
            [None,   "#880000", "#FF4444", "#FF4444", "#FF4444", "#FF4444", "#880000", None],
            [None,   None,      "#880000", "#880000", "#880000", "#880000", None,      None],
            [None,   "#880000", "#880000", "#FF4444", "#FF4444", "#880000", "#880000", None],
            [None,   "#880000", "#880000", "#880000", "#880000", "#880000", "#880000", None],
            [None,   "#FF4444", None,      None,      None,      None,      "#FF4444", None],
            [None,   None,      "#880000", None,      None,      "#880000", None,      None],
        ],
        [  # Frame 2: legs together
            [None,   None,      "#880000", "#880000", "#880000", "#880000", None,      None],
            [None,   "#880000", "#000000", "#000000", "#000000", "#000000", "#880000", None],
            [None,   "#880000", "#FF4444", "#FF4444", "#FF4444", "#FF4444", "#880000", None],
            [None,   None,      "#880000", "#880000", "#880000", "#880000", None,      None],
            [None,   "#880000", "#880000", "#FF4444", "#FF4444", "#880000", "#880000", None],
            [None,   "#880000", None,      "#FF4444", "#FF4444", None,      "#880000", None],
            [None,   "#880000", None,      "#FF4444", "#FF4444", None,      "#880000", None],
            [None,   None,      "#880000", None,      None,      "#880000", None,      None],
        ],
    ],
    "ContentAgent": [  # Blue astronaut frames
        [  # Frame 1
            [None,   None,      "#000088", "#000088", "#000088", "#000088", None,      None],
            [None,   "#000088", "#000000", "#000000", "#000000", "#000000", "#000088", None],
            [None,   "#000088", "#4444FF", "#4444FF", "#4444FF", "#4444FF", "#000088", None],
            [None,   None,      "#000088", "#000088", "#000088", "#000088", None,      None],
            [None,   "#000088", "#000088", "#4444FF", "#4444FF", "#000088", "#000088", None],
            [None,   "#000088", "#000088", "#000088", "#000088", "#000088", "#000088", None],
            [None,   "#4444FF", None,      "#4444FF", None,      "#4444FF", None,      None],
            [None,   None,      "#000088", "#000088", "#000088", "#000088", None,      None],
        ],
        [  # Frame 2
            [None,   None,      "#000088", "#000088", "#000088", "#000088", None,      None],
            [None,   "#000088", "#000000", "#000000", "#000000", "#000000", "#000088", None],
            [None,   "#000088", "#4444FF", "#4444FF", "#4444FF", "#4444FF", "#000088", None],
            [None,   None,      "#000088", "#000088", "#000088", "#000088", None,      None],
            [None,   None,      "#000088", "#4444FF", "#4444FF", "#000088", "#000088", None],
            [None,   None,      "#000088", "#000088", "#000088", "#000088", "#000088", None],
            [None,   "#4444FF", "#4444FF", None,      "#4444FF", "#4444FF", None,      None],
            [None,   None,      "#000088", None,      None,      "#000088", None,      None],
        ],
    ],
    "SEOAgent": [  # Purple astronaut frames
        [  # Frame 1
            [None,   None,      "#440044", "#440044", "#440044", "#440044", None,      None],
            [None,   "#440044", "#000000", "#000000", "#000000", "#000000", "#440044", None],
            [None,   "#440044", "#884488", "#884488", "#884488", "#884488", "#440044", None],
            [None,   None,      "#440044", "#440044", "#440044", "#440044", None,      None],
            [None,   "#440044", "#440044", "#884488", "#884488", "#440044", "#440044", None],
            [None,   "#440044", "#440044", "#440044", "#440044", "#440044", "#440044", None],
            [None,   "#884488", None,      "#884488", None,      "#884488", None,      None],
            [None,   None,      "#440044", None,      None,      "#440044", None,      None],
        ],
        [  # Frame 2
            [None,   None,      "#440044", "#440044", "#440044", "#440044", None,      None],
            [None,   "#440044", "#000000", "#000000", "#000000", "#000000", "#440044", None],
            [None,   "#440044", "#884488", "#884488", "#884488", "#884488", "#440044", None],
            [None,   None,      "#440044", "#440044", "#440044", "#440044", None,      None],
            [None,   "#440044", None,      "#884488", "#884488", None,      "#440044", None],
            [None,   "#440044", None,      "#440044", "#440044", None,      "#440044", None],
            [None,   None,      "#884488", None,      None,      "#884488", None,      None],
            [None,   None,      "#440044", None,      None,      "#440044", None,      None],
        ],
    ],
    "EthicsAgent": [  # Green astronaut frames
        [  # Frame 1
            [None,   None,      "#004400", "#004400", "#004400", "#004400", None,      None],
            [None,   "#004400", "#000000", "#000000", "#000000", "#000000", "#004400", None],
            [None,   "#004400", "#44FF44", "#44FF44", "#44FF44", "#44FF44", "#004400", None],
            [None,   None,      "#004400", "#004400", "#004400", "#004400", None,      None],
            [None,   "#004400", "#004400", "#44FF44", "#44FF44", "#004400", "#004400", None],
            [None,   "#004400", "#004400", "#004400", "#004400", "#004400", "#004400", None],
            [None,   "#44FF44", None,      "#44FF44", None,      "#44FF44", None,      None],
            [None,   None,      "#004400", None,      None,      "#004400", None,      None],
        ],
        [  # Frame 2
            [None,   None,      "#004400", "#004400", "#004400", "#004400", None,      None],
            [None,   "#004400", "#000000", "#000000", "#000000", "#000000", "#004400", None],
            [None,   "#004400", "#44FF44", "#44FF44", "#44FF44", "#44FF44", "#004400", None],
            [None,   None,      "#004400", "#004400", "#004400", "#004400", None,      None],
            [None,   None,      "#004400", "#44FF44", "#44FF44", None,      None,      None],
            [None,   None,      "#004400", "#004400", None,      None,      None,      None],
            [None,   "#44FF44", None,      None,      None,      None,      None,      None],
            [None,   None,      None,      None,      None,      None,      None,      None],
        ],
    ],
}


def build_avatar_image(pattern, pixel_size=10):
    """
    Convert an 8×8 pattern into a scaled PhotoImage.
    :param pattern: One 8×8 pattern (list of lists) of colors/None.
    :param pixel_size: Size of each pixel block.
    :return: tk.PhotoImage
    """
    rows, cols = len(pattern), len(pattern[0])
    img = PhotoImage(width=cols * pixel_size, height=rows * pixel_size)
    for y, row in enumerate(pattern):
        for x, color in enumerate(row):
            if color:
                img.put(color, to=(x*pixel_size, y*pixel_size,
                                   (x+1)*pixel_size, (y+1)*pixel_size))
    return img

