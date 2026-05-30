_last_terms_by_user: dict[int, str] = {}


def save_user_term(user_id: int, term: str) -> None:
    _last_terms_by_user[user_id] = term


def get_user_term(user_id: int) -> str | None:
    return _last_terms_by_user.get(user_id)
