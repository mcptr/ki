def mk_slug(value, limit=0):
    if limit and len(value) > limit:
        value = value[:value.rfind(" ")]

    value = value.replace(",", " ")
    value = value.translate(
        dict.fromkeys(map(ord, ",!@#$%^&*()_+<>?\\'\"][}{`~:;"))
    )
    value = value.replace(" ", "_")
    return value
