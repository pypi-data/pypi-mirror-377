# Fix items of breadcrumb that can be reused

example = {
    "name": "Example",
    "slug": "example",
    "url_name": "example_name",
}


def make_details(url_name, url_params=[], get_params={}):
    """Make details breadcrumb item."""
    return {
        "name": "Detalhes",
        "slug": "detalhes",
        "url_name": url_name,
        "url_params": url_params,
        "get_params": get_params,
    }
