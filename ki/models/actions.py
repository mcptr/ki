import uuid
from psycopg2.extras import Json

import ki.logg


log = ki.logg.get(__name__)


def store(tx, name, status, result=None, **kwargs):
    input_params = kwargs.get("input_params", None)
    debug_data = kwargs.get("debug_data", None)
    session_id = kwargs.get("session_id", None)
    result = kwargs.get("result", None)
    message = kwargs.get("message", None)

    data = dict(
        name=name,
        status=bool(status),
        input_data=Json(input_params) if input_params else None,
        message=str(message),
        result=Json(result) if result else None,
        debug_data=Json(debug_data) if debug_data else None,
        session_id=session_id,
    )

    sql = (
        "INSERT INTO runtime.actions("
        "    name, status, input_data, message, result, debug_data, session_id"
        ") VALUES(%(name)s, %(status)s, %(input_data)s,"
        "    %(message)s, %(result)s, %(debug_data)s, %(session_id)s"
        ") RETURNING id"
    )

    tx.execute(sql, data)
    r = tx.fetchone()
    return r.id


# def store_success(tx, name, result=None, **kwargs):
#     return store(tx, name, True, result, **kwargs)


# def store_error(tx, name, result=None, **kwargs):
#     return store(tx, name, False, result, **kwargs)


def get(tx, id, session_id=None):
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

    tx.execute(sql, dict(
        id=id,
        session_id=session_id
    ))
    r = tx.fetchone()
    return r
