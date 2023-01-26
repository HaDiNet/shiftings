def calc_text_color(hex_str: str):
    if not hex_str.startswith('#') and len(hex_str) != 7:
        raise ValueError('HTML color string starts with # and is 7 chars long')
    (r, g, b) = (hex_str[1:3], hex_str[3:5], hex_str[5:])
    return '#000' if 1 - (int(r, 16) * 0.299 + int(g, 16) * 0.587 + int(b, 16) * 0.114) / 255 < 0.5 else '#fff'
