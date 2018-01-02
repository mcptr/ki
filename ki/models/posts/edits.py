from schzd.core import cache


class Edits:
    def __init__(self):
        self.cache = cache.get_connection()
        self.prefix = "post-edits"

    def add(self, post_id, user):
        key = "%s:%d:%s" % (self.prefix, post_id, user.id)
        # self.cache.setex
