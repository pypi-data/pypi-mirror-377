from newsdata_client.newsdata_exception import NewsDataException


def add_id(p: dict, id: list[str] = None):
    if id == None:
        return
    if len(id) > 50:
        raise NewsDataException("more than 50 ids not allowed")
    p["id"] = ",".join(id)


def add_q(p: dict, q: str = None):
    if q == None:
        return
    if len(q) > 512:
        raise NewsDataException("more that 512 characters not allowed")
    p["q"] = q


def add_q_in_title(p: dict, q: str = None):
    if q == None:
        return
    if len(q) > 512:
        raise NewsDataException("more that 512 characters not allowed")
    p["qInTitle"] = q


def add_q_in_meta(p: dict, q: str = None):
    if q == None:
        return
    if len(q) > 512:
        raise NewsDataException("more that 512 characters not allowed")
    p["qInMeta"] = q


def add_timeframe(p: dict, t: str = None):
    if t == None:
        return
    p["timeframe"] = t


def add_country(p: dict, c: list[str] = None):
    if c is None:
        return
    p["country"] = ",".join(c)


def add_category(p: dict, c: list[str] = None):
    if c is None:
        return
    if len(c) > 5:
        raise NewsDataException("cannot exceed more than 5 categories")
    p["category"] = ",".join(c)


def add_exclude_category(p: dict, e: list[str] = None):
    if e is None:
        return
    if p.get("category") is not None:
        raise NewsDataException(
            "cannot use category and exclude category parameter simultaneously"
        )
    if len(e) > 5:
        raise NewsDataException("cannot exceed more than 5 exclude categories")
    p["excludecategory"] = ",".join(e)


def add_language(p: dict, l: list[str] = None):
    if l is None:
        return
    if len(l) > 5:
        raise NewsDataException("cannot exceed more than 5 languages")
    p["language"] = ",".join(l)


def add_tag(p: dict, t: list[str] = None):
    if t is None:
        return
    if len(t) > 5:
        raise NewsDataException("cannot exceed more than 5 tags")
    p["tag"] = ",".join(t)


def add_sentiment(p: dict, s: str = None):
    if s is None:
        return
    p["sentiment"] = s


def add_region(p: dict, r: list[str] = None):
    if r is None:
        return
    if len(r) > 5:
        raise NewsDataException("cannot exceed more than 5 regions")
    p["region"] = ",".join(r)


def add_domain(p: dict, d: list[str] = None):
    if d is None:
        return
    if len(d) > 5:
        raise NewsDataException("cannot exceed more than 5 domain")
    p["domain"] = ",".join(d)


def add_domain_url(p: dict, d: list[str] = None):
    if d is None:
        return
    if len(d) > 5:
        raise NewsDataException("cannot exceed more than 5 domain url")
    p["domainurl"] = ",".join(d)


def add_exclude_domain(p: dict, e: list[str] = None):
    if e is None:
        return
    if len(e) > 5:
        raise NewsDataException("cannot exceed more than 5 domain url")
    p["excludedomain"] = ",".join(e)


def add_exclude_field(p: dict, e: list[str] = None):
    if e is None:
        return
    p["excludefield"] = ",".join(e)


def add_priority_domain(p: dict, pr: str = None):
    if pr is None:
        return
    p["prioritydomain"] = pr


def add_timezone(p: dict, t: str = None):
    if t is None:
        return
    p["timezone"] = t


def add_full_content(p: dict, f: bool = None):
    if f is None:
        return
    if f:
        p["full_content"] = "1"
    else:
        p["full_content"] = "0"


def add_image(p: dict, i: bool = None):
    if i is None:
        return
    if i:
        p["image"] = "1"
    else:
        p["image"] = "0"


def add_video(p: dict, v: bool = None):
    if v is None:
        return
    if v:
        p["video"] = "1"
    else:
        p["video"] = "0"


def add_remove_duplicate(p: dict, r: bool = None):
    if r is None:
        return
    if r:
        p["removeduplicate"] = "1"


def add_size(p: dict, s: int = None):
    if s is None:
        return
    if s < 1 or s > 50:
        raise NewsDataException("size should be between 1 to 50")
    p["size"] = s


def add_page(p: dict, page: str = None):
    if page is None:
        return
    p["page"] = page


def add_from_date(p: dict, from_date: str = None):
    if from_date is None:
        return
    p["from_date"] = from_date


def add_to_date(p: dict, to_date: str = None):
    if to_date is None:
        return
    p["to_date"] = to_date


def add_coin(p: dict, coin: list[str] = None):
    if coin is None:
        return
    if len(coin) > 5:
        raise NewsDataException("coins should be less than 5")
    p["coin"] = ",".join(coin)
