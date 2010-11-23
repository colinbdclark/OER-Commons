MAX_FONT_SIZE = 8
MIN_FONT_SIZE = 0
AVERAGE_FONT_SIZE = 1


def get_tag_cloud(tags, max_font=MAX_FONT_SIZE,
                  min_font=MIN_FONT_SIZE, average_font=AVERAGE_FONT_SIZE):

    max_num = max(tags.values())
    min_num = min(tags.values())
    if max_num == min_num:
        # All tags have the same number
        for t in tags:
            tags[t] = average_font
    else:
        average = (max_num - min_num) / float(len(tags))
        if max_num - average > average - min_num:
            for t in tags:
                n = tags[t]
                tags[t] = int((n - average) * (max_font - average_font) / (max_num - average) + average_font)
        else:
            for t in tags:
                n = tags[t]
                tags[t] = int((n - average) * (average_font - min_font) / (average - min_num) + average_font)

    keys = tags.keys()
    keys.sort(key=lambda x: x.lower())
    tags_array = []
    for tag in keys:
        tags_array.append({"slug":tag, "number":tags[tag]})
    return tags_array
