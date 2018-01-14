import flask
import sys


def calc_page_idx(page_idx):
    try:
        page_idx = int(page_idx)
    except Exception:
        page_idx = 1
    if page_idx <= 1 or page_idx > sys.maxsize:
        page_idx = 1
    return page_idx


def mk_urls(view, page_idx, items_size, limit, **kwargs):
    prev_page_url = None
    next_page_url = None

    prev_page_number = 0
    next_page_number = 0

    prev_page_number = page_idx - 1 if page_idx > 0 else 0
    if prev_page_number:
        prev_page_url = flask.url_for(view, page=prev_page_number, **kwargs)

    if items_size >= limit:
        next_page_number = page_idx + 1
        next_page_url = flask.url_for(view, page=next_page_number, **kwargs)

    return dict(
        prev_page_url=prev_page_url,
        next_page_url=next_page_url,
        prev_page_number=prev_page_number,
        next_page_number=next_page_number,
    )
