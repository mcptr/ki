import random
import uuid
from schzd.core import cache


def create_pin(user_id, topic, expire=300):
    if not (user_id and topic):
        raise Exception("Need user id and subject for pin verification")
    conn = cache.get_connection()
    k = "verifications:pin:%s:%s" % (str(user_id), str(topic))
    pin = random.randint(100000, 999999)
    conn.setex(k, expire, pin)
    return pin


def verify_pin(user_id, topic, pin):
    if not pin:
        return False
    conn = cache.get_connection()
    k = "verifications:pin:%s:%s" % (str(user_id), str(topic))
    r = int(conn.get(k) or 0)
    return (r and pin and (r == pin))


def create_token(user_id, topic, expire=300):
    if not (user_id and topic):
        raise Exception("Need user id and subject for pin verification")
    conn = cache.get_connection()
    k = "verifications:token:%s:%s" % (str(user_id), str(topic))
    token = str(uuid.uuid4()).upper()
    conn.setex(k, expire, token)
    return token


def verify_token(user_id, topic, token):
    if not token:
        return False
    conn = cache.get_connection()
    k = "verifications:token:%s:%s" % (str(user_id), str(topic))
    r = (conn.get(k) or b"").decode("utf-8").upper()
    return (r and token and (r == token))
