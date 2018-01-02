import uuid
from psycopg2.extras import Json
from schzd.core.pgsql import pg_cursor

import schzd.core.logg


log = schzd.core.logg.get(__name__)


def store_result(name, result, status, **kwargs):
    params = kwargs.get("params", None)
    debug_data = kwargs.get("debug_data", None)
    session_id = kwargs.get("session_id", None)

    data = dict(
        name=name,
        status=status,
        input_data=Json(params) if params else None,
        result=Json(result),
        debug_data=Json(debug_data) if debug_data else None,
        session_id=session_id,
    )

    sql = (
        "INSERT INTO runtime.actions("
        "    name, status, input_data, result, debug_data, session_id"
        ") VALUES(%(name)s, %(status)s, %(input_data)s,"
        "    %(result)s, %(debug_data)s, %(session_id)s"
        ") RETURNING id"
    )

    with pg_cursor(cursor_type=tuple) as cursor:
        cursor.execute(sql, data)
        cursor.connection.commit()
        r = cursor.fetchone()
        return r.id


def store_success(name, result, **kwargs):
    return store_result(name, result, True, **kwargs)


def store_error(name, result, **kwargs):
    return store_result(name, result, False, **kwargs)


def get(id, session_id=None):
    try:
        uuid.UUID(id)
    except ValueError:
        log.error("Invalid action_id: %s", id)
        return None

    sql = (
        "SELECT name, status, result, input_data FROM runtime.actions"
        "  WHERE id = %(id)s"
    )

    if session_id:
        sql += "  AND session_id=%(session_id)s"

    with pg_cursor(cursor_type=tuple) as cursor:
        cursor.execute(sql, dict(
            id=id,
            session_id=session_id
        ))
        r = cursor.fetchone()
        return r
