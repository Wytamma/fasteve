from fastapi.core import config
from datetime import datetime
import hashlib
from json import dumps


def document_etag(value, ignore_fields=None):
    """ Computes and returns a valid ETag for the input value.
    """
    h = hashlib.sha1()
    h.update(dumps(value_, sort_keys=True).encode("utf-8"))
    return h.hexdigest()


class ParsedRequest:
    """ This class, by means of its attributes, describes a client request.
    """

    # `where` value of the query string (?where). Defaults to None.
    where: str = None

    # `projection` value of the query string (?projection). Defaults to None.
    projection: str = None

    # `sort` value of the query string (?sort). Defaults to None.
    sort: str = None

    # `page` value of the query string (?page). Defaults to 1.
    page: int = 1

    # `max_result` value of the query string (?max_results). Defaults to
    # `PAGINATION_DEFAULT` unless pagination is disabled.
    max_results: int = 0

    # `If-Modified-Since` request header value. Defaults to None.
    if_modified_since: str = None

    # `If-None_match` request header value. Defaults to None.
    if_none_match: str = None

    # `If-Match` request header value. Default to None.
    if_match: str = None

    # `embedded` value of the query string (?embedded). Defaults to None.
    embedded: str = None

    # `show_deleted` True when the SHOW_DELETED_PARAM is included in query.
    # Only relevant when soft delete is enabled. Defaults to False.
    show_deleted: bool = False

    # `aggregation` value of the query string (?aggregation). Defaults to None.
    aggregation: str = None

    # `args` value of the original request. Defaults to None.
    args = None


def parse_request(request: Request, resource: Resource) -> ParsedRequest:
    """ Parses a client request, returning instance of :class:`ParsedRequest`
    containing relevant request data.
    :param resource: the resource currently being accessed by the client.
    """
    print(dir(request))
    args = request.args
    headers = request.headers

    r = ParsedRequest()
    r.args = args

    if resource.allowed_filters:
        r.where = args.get(config.QUERY_WHERE)
    if resource.projection:
        r.projection = args.get(config.QUERY_PROJECTION)
    if resource.sorting:
        r.sort = args.get(config.QUERY_SORT)
    if resource.embedding:
        r.embedded = args.get(config.QUERY_EMBEDDED)
    # if resource.datasource["aggregation"]:
    #    r.aggregation = args.get(config.QUERY_AGGREGATION)

    r.show_deleted = config.SHOW_DELETED_PARAM in args

    config.PAGINATION_DEFAULT if resource.pagination else 0
    r.max_results = int(float(args[config.QUERY_MAX_RESULTS]))

    if resource.pagination:
        # TODO should probably return a 400 if 'page' is < 1 or non-numeric
        if config.QUERY_PAGE in args:
            try:
                r.page = abs(int(args.get(config.QUERY_PAGE))) or 1
            except ValueError:
                pass

        # TODO should probably return a 400 if 'max_results' < 1 or
        # non-numeric
        if r.max_results > config.PAGINATION_LIMIT:
            r.max_results = config.PAGINATION_LIMIT

    def etag_parse(challenge):
        if challenge in headers:
            etag = headers[challenge]
            # allow weak etags (Eve does not support byte-range requests)
            if etag.startswith('W/"'):
                etag = etag.lstrip("W/")
            # remove double quotes from challenge etag format to allow direct
            # string comparison with stored values
            return etag.replace('"', "")
        else:
            return None

    if headers:
        r.if_modified_since = weak_date(headers.get("If-Modified-Since"))
        r.if_none_match = etag_parse("If-None-Match")
        r.if_match = etag_parse("If-Match")

    return r


def weak_date(date):
    """ Returns a RFC-1123 string corresponding to a datetime value plus
    a 1 second timedelta. This is needed because when saved, documents
    LAST_UPDATED values have higher resolution than If-Modified-Since's, which
    is limited to seconds.
    :param date: the date to be adjusted.
    """
    return (
        datetime.strptime(date, RFC1123_DATE_FORMAT) + timedelta(seconds=1)
        if date
        else None
    )
