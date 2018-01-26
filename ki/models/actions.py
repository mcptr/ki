import uuid
import json
from psycopg2.extras import Json
import ki.logg


log = ki.logg.get(__name__)


class LoggedAction:
    url_param = "action"

    def __init__(self, name=None, **kwargs):
        self.name = name

    def _from_dict(self, d):
        self.status = kwargs.pop("status", False)
        self.params = kwargs.pop("input_data", None)
        self.debug_data = kwargs.pop("debug_data", None)
        self.session_id = kwargs.pop("session_id", None)
        self.result = kwargs.pop("result", None)
        self.message = kwargs.get("message", None)

    def to_dict(self):
        return dict(
            name=name,
            status=bool(status),
            input_data=Json(input_params) if input_params else None,
            message=str(message),
            result=Json(result) if result else None,
            debug_data=Json(debug_data) if debug_data else None,
            session_id=session_id,
        )

    def save(self, tx):
        self.to_dict()
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


    def load(self, tx, id, session_id=None):
        try:
            uuid.UUID(id)
        except ValueError:
            log.error("Invalid action_id: %s", id)
            return None

        sql = (
            "SELECT name, status, result, input_data FROM runtime.actions"
            "  WHERE id = %(id)s"
        )

        session_id = (session_id or self.session_id)
        if session_id:
            sql += "  AND session_id=%(session_id)s"

        tx.execute(sql, dict(
            id=id,
            session_id=session_id
        ))
        r = tx.fetchone()
        if r:
            self._from_dict(r._asdict())


class Action:
    url_param = "action"

    def __init__(self, id=None, **kwargs):
        self.id = (id or str(uuid.uuid4()))
        self._cache_key = "formaction:%s" % self.id
        self.session_id = kwargs.pop("session_id", None)
        self.values = dict()
        self.field_errors = dict()
        self.errors = []
        self.messages = []

    def to_dict(self):
        return self.__dict__

    def add_field_error(self, field, msg):
        self.field_errors[field] = self.field_errors.get(field, [])
        self.field_errors[field].append(msg)

    def add_error(self, msg):
        self.errors.append(msg)

    def add_message(self, msg):
        self.messages.append(msg)

    def set_values(self, values):
        self.values = (values or dict())

    def get_value(self, field, default=None):
        return self.values.get(field, default)

    def save(self, api, ttl=600):
        conn = api.cache.get_connection()
        data = json.dumps(dict(
            session_id=self.session_id,
            field_errors=self.field_errors,
            errors=self.errors,
            messages=self.messages,
            values=self.values,
        ))
        conn.setex(self._cache_key, ttl, data)

    def load(self, api, id):
        conn = api.cache.get_connection()
        data = conn.get(self._cache_key)
        data = json.loads(data.decode("utf-8")) if data else None
        if not data:
            return
        loaded_session_id = data.get("session_id", None)
        if loaded_session_id and loaded_session_id != self.session_id:
            log.error(
                "Cannot retrieve form action: %s for session %s",
                id, self.session_id
            )
        else:
            self.session_id = data.get("session_id", None)
            self.field_errors = data.get("field_errors", dict())
            self.errors = data.get("errors", [])
            self.messages = data.get("messages", [])
            self.values = data.get("values", dict())
