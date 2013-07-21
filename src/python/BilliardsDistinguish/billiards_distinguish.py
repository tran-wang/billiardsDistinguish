import colorsys



DEFAULT_WHITE_BILLIARDS_WHITE_COLOR_RATIO = [0.90, 1.0]
DEFAULT_BIG_BILLIARDS_WHITE_COLOR_RATIO = [0.20, 0.90]
DEFAULT_LITTLE_BILLIARDS_WHITE_COLOR_RATIO = [0, 0.20]

DEFAULT_HUE_1_3_5_H = 0.166667
DEFAULT_HUE_2_6_H = 0.500000
DEFAULT_HUE_4_7_8_H = 0.833333


class BilliardsType(object):
    White = -1
    Little = 0
    Big = 8


def _get_billiardsType(white_color_ratio):
    if _is_in_range(white_color_ratio, DEFAULT_WHITE_BILLIARDS_WHITE_COLOR_RATIO):
        return BilliardsType.White
    elif _is_in_range(white_color_ratio, DEFAULT_BIG_BILLIARDS_WHITE_COLOR_RATIO):
        return BilliardsType.Big
    elif _is_in_range(white_color_ratio, DEFAULT_LITTLE_BILLIARDS_WHITE_COLOR_RATIO):
        return BilliardsType.Little
    else:
        return BilliardsType.White

def _is_in_range(value_, range_):
    assert len(range_) == 2
    if value_ >= range_[0] and value_ <= range_[1]:
        return True
    else:
        return False

def _get_max_band(r, g, b):
    if r > g and r > b:
        return "R"
    if g > r and g > b:
        return "G"
    if b > r and b > g:
        return "B"

def _is_black(r, g, b):
    max_ = max(r, g, b)
    min_ = min(r, g, b)

    if max_ < 75 and max_ - min_ < 20:
        return True
    else:
        return False

def get_billiards_number(white_color_ratio, r, g, b):
    billiards_type = _get_billiardsType(white_color_ratio)
    if billiards_type == BilliardsType.White:
        return 0
    if billiards_type == BilliardsType.Little and _is_black(r, g, b):
        return 8
    if _get_max_band(r, g, b) == "G":
        return 6 + billiards_type
    if _get_max_band(r, g, b) == "B":
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        if abs(h - 0.5) < abs(h - 0.833333):
            return 2 + billiards_type
        else:
            return 4 + billiards_type
    if _get_max_band(r, g, b) == "R":
        if r - g < g - b :  # yellow color
            return 1 + billiards_type
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        if abs(h - 0.166667) < abs(h - 0.833333):
            if _is_black(0, g, b):  # pure red color
                return 3 + billiards_type
            else:
                return 5 + billiards_type
        else:
            return 7 + billiards_type
