# internal libs
from src.services.search_engine.distance_coordinates import calculate_square_corners

# 3rd party
import pytest


@pytest.mark.parametrize(
    ("lat", "long", "side"),
    [
        (41.40756379142826, 2.1724575744522867, 1000),
        (41.3923748496093, 2.165014450939276, 2000),
        (41.39158729352277, 2.1810083039519226, 3000),
        (41.37462111637922, 2.1487091814408585, 100),
    ],
)
def test_calculate_square_corners(lat, long, side):
    square_corners = calculate_square_corners(lat, long, side)
    assert len(square_corners) == 2
    assert isinstance(square_corners, list)
    assert isinstance(square_corners[0], tuple)
    assert len(square_corners[0]) == 2
    # naive - general test
    assert 41 <= square_corners[0][0] <= 42
    assert 2 <= square_corners[0][1] <= 3
    # exact test- is included in area
    ## test less equal than right point
    assert lat <= square_corners[0][0]
    assert long <= square_corners[0][1]
    ## test less equal than left point
    assert lat >= square_corners[1][0]
    assert long >= square_corners[1][1]
