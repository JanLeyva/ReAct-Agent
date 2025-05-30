class NoPlaceFound(Exception):
    """We can perform a search to GoogleAPI with no results."""

    pass


class NoResultsFoundInVectorDB(Exception):
    """We can perform a search with filters that return 0 reusults."""

    pass
