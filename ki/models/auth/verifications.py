import random
import uuid
import ki.errors


def create(tx, user_id, topic, max_age_sec=3600, **kwargs):
    verification_data = kwargs.pop("verification_data", None)
    allow_multiple = kwargs.pop("_allow_multiple", False)

    if not allow_multiple:
        if not topic:
            raise ki.errors.Error("Missing topic")
        sql = (
            "DELETE FROM auth.verifications WHERE user_id = %s"
            "  AND topic = %s"
        )
        tx.execute(sql, (user_id, topic))

    sql = (
        "INSERT INTO auth.verifications("
        "  user_id, max_age_sec, topic, verification_data)"
        "  VALUES(%s, %s, %s, %s) RETURNING id"
    )
    tx.execute(sql, (user_id, max_age_sec, topic, verification_data))
    r = tx.fetchone()
    return r.id if r else None


def use(tx, verification_id, user_id, **kwargs):
    if not (verification_id and user_id):
        return None
    sql = (
        "DELETE FROM auth.verifications"
        "  WHERE id=%s AND user_id=%s"
        "  AND ((EXTRACT('EPOCH' FROM NOW() AT TIME ZONE 'UTC'"
        "      - ctime))::INTEGER < max_age_sec)"
        "  RETURNING *"
    )
    tx.execute(sql, (verification_id, user_id))
    return tx.fetchone()


def use_no_user(tx, verification_id, **kwargs):
    if not verification_id:
        return None
    sql = (
        "DELETE FROM auth.verifications"
        "  WHERE id=%s"
        "  AND ((EXTRACT('EPOCH' FROM NOW() AT TIME ZONE 'UTC'"
        "      - ctime))::INTEGER < max_age_sec)"
        "  RETURNING *"
    )
    print(tx.mogrify(sql, (verification_id, )))
    tx.execute(sql, (verification_id, ))
    return tx.fetchone()
