DEFAULT_LIMIT = 10


class Node:
    def __init__(self, comment=None, path=None):
        comment = (comment or dict())
        self.id = comment.get("id", None)
        self.parent_id = comment.get("parent_id", None)
        self.value = comment
        self.children = {}
        self.order = []

    def _find(self, path):
        ref = self
        for id in path:
            ref = ref.children.get(id, None)
            if not ref:
                return None
        return ref

    def insert(self, node):
        ref = None
        if not node.value["path"]:
            ref = self
        elif (len(node.value["path"]) == 1
              and node.value["path"][0] == self.id):
            ref = self
        else:
            ref = self._find(node.value["path"])
        assert ref
        ref.children[node.value["id"]] = node
        ref.order.append(node.value["id"])

    def as_dict(self, dest=None):
        dest = dict() if dest is None else dest
        dest[self.id] = dict(
            comment=self.value,
            children={},
        )
        for child_id in self.order:
            self.children[child_id].as_dict(dest[self.id]["children"])
        return dest


def create(tx, post_id, content, **kwargs):
    sql = (
        "INSERT INTO posts.comments ("
        "    post_id, user_id, parent_id, content"
        "  ) VALUES(%(post_id)s, %(user_id)s, "
        "         %(parent_id)s, %(content)s"
        "  ) RETURNING id"
    )

    tx.execute(sql, dict(
        post_id=post_id,
        user_id=kwargs.get("user_id", None),
        parent_id=kwargs.get("parent_id", None),
        content=content,
    ))

    r = tx.fetchone()
    return r.id if r else None


def update(tx, comment_id, content, **kwargs):
    sql = (
        "UPDATE posts.comments SET content = %s, mtime=NOW()"
        "   WHERE id = %s"
        "   RETURNING id"
    )

    tx.execute(sql, (content, comment_id))
    r = tx.fetchone()
    return r.id if r else None


def delete(tx, comment_id):
    sql = (
        "UPDATE posts.comments SET content = NULL, mtime=NOW(), deleted=true"
        "   WHERE id = %s"
        "   RETURNING id"
    )

    tx.execute(sql, (comment_id,))
    return tx.fetchone()


def get_comments_tree(tx, post_id):
    sql = (
        "SELECT * FROM posts.get_comments_tree(%s) AS ("
        "  id integer, username varchar, parent_id integer,"
        "  post_id integer, content text, deleted boolean, "
        "  user_id uuid,"
        "  ctime integer, mtime integer,"
        "  depth integer, path integer[])"
    )

    threads = {}
    threads_order = []
    last_thread = None

    tx.execute(sql, (post_id,))

    for c in tx.fetchall():
        if not c.path:
            threads[c.id] = Node(c._asdict())
            threads_order.append(c.id)
        else:
            thread_id = c.path[0]
            data = c._asdict()
            data.update(path=c.path[1:])
            threads[thread_id].insert(Node(data))
    return dict(
        children=threads,
        order=threads_order
    )


def get(tx, comment_id):
    sql = (
        "SELECT id, parent_id, content, deleted,"
        "    ctime, mtime, user_id, post_id"
        "  FROM posts.comments"
        " WHERE id=%s"
    )

    tx.execute(sql, (comment_id,))
    return tx.fetchone()


def get_page(tx, page_idx=0, **kwargs):
    limit = kwargs.get("limit", DEFAULT_LIMIT)
    offset = page_idx * limit

    sql = (
        "SELECT u.name as author, p.title as post_title,"
        "    c.id, c.content, c.post_id,"
        "    EXTRACT('EPOCH' FROM c.ctime)::INTEGER as ctime,"
        "    EXTRACT('EPOCH' FROM c.mtime)::INTEGER as mtime"
        "  FROM posts.comments c"
        "  JOIN auth.users u ON u.id = c.user_id"
        "  JOIN posts.posts p ON p.id = c.post_id"
        "  WHERE parent_id is null and not deleted"
        "  ORDER BY c.id desc"
        "  LIMIT %s OFFSET %s"
    )

    # TODO: order by score. We need score.

    tx.execute(sql, (limit, offset,))
    return tx.fetchall()
