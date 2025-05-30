# Naive implementation of square around a point. Base on <= point 1 >= point 3
# Useful links
# https://stackoverflow.com/questions/4000886/gps-coordinates-1km-square-around-a-point
# https://math.stackexchange.com/questions/256931/draw-a-square-around-a-point

import math


def calculate_square_corners(
    latitude: float, longitude: float, side: float
) -> list[tuple[float, float]]:
    """
    Calculates the four corners of a square around a central latitude/longitude point
    with geographically more accurate calculations (assuming a spherical Earth).

    Args:
        latitude (float): Central latitude in degrees.
        longitude (float): Central longitude in degrees.
        side (float): Side length of the square in meters.

    Returns:
        list[tuple[float, float]]: A list of four (latitude, longitude) tuples
                                   representing the corners of the square, in degrees.
    """

    # Approximate equatorial circumference in km
    EARTH_EQUATORIAL_CIRCUMFERENCE_KM = 40075.0  
    METERS_PER_KM = 1000.0
    DEGREES_PER_CIRCLE = 360.0

    # For latitude, 1 degree is roughly constant (approx 111.32 km or 111320 meters)
    # 40075 km / 360 degrees = 111.3194 km/degree
    KM_PER_DEGREE_LATITUDE = EARTH_EQUATORIAL_CIRCUMFERENCE_KM / DEGREES_PER_CIRCLE

    # Converting degrees to radians
    lat_in_radians = math.radians(latitude)
    long_in_radians = math.radians(longitude)

    # --- Corrected Geographical Calculations ---

    # 1. Calculate the change in Latitude for a given distance 'side' (in degrees)
    # This is constant regardless of longitude.
    # (side / METERS_PER_KM) converts side from meters to kilometers.
    # Then divide by km_per_degree_latitude to get degrees.
    delta_lat_degrees = (side / METERS_PER_KM) / KM_PER_DEGREE_LATITUDE

    # 2. Calculate the circumference of the Earth at the given latitude
    # This is crucial for calculating the change in longitude accurately.
    # Circumference at latitude = Equatorial Circumference * cos(latitude_in_radians)
    circumference_at_latitude = EARTH_EQUATORIAL_CIRCUMFERENCE_KM * math.cos(
        lat_in_radians
    )

    # Handle potential division by zero if close to poles (latitude +/-90 degrees)
    # where cos(lat_in_radians) would be 0 or very close to 0.
    # If at a pole, all longitudes converge, so a change in longitude is ill-defined.
    if circumference_at_latitude == 0:
        # At poles, longitude becomes meaningless for defining a square.
        # For a direct translation, we'll set delta_long_degrees to 0,
        # or you might want to raise an error depending on desired behavior.
        delta_long_degrees = 0.0
    else:
        # Calculate the change in Longitude for a given distance 'side' (in degrees)
        # This varies significantly with latitude.
        # (side / METERS_PER_KM) converts side from meters to kilometers.
        # Then divide by km_per_degree_longitude_at_this_latitude
        km_per_degree_longitude_at_this_latitude = (
            circumference_at_latitude / DEGREES_PER_CIRCLE
        )
        delta_long_degrees = (
            side / METERS_PER_KM
        ) / km_per_degree_longitude_at_this_latitude

    # --- Convert deltas back to radians for calculation ---
    delta_lat_radians = math.radians(delta_lat_degrees)
    delta_long_radians = math.radians(delta_long_degrees)

    # --- Calculate offsets for a square rotated by 45 degrees ---
    # The (Math.Sqrt(2) / 2) factor comes from the diagonal of a square.
    # If 'side' is the length of the square's side, then the distance from center
    # to a corner along a cardinal direction (N/S/E/W) is side / sqrt(2).
    # This is `side * (sqrt(2) / 2)`.
    # These `n_lat` and `n_long` represent the half-diagonal offsets.
    half_diagonal_factor = math.sqrt(2) / 2

    n_lat_offset = delta_lat_radians * half_diagonal_factor
    n_long_offset = delta_long_radians * half_diagonal_factor

    # --- Calculate four corner coordinates in radians ---
    # The original C# logic appears to define the corners in a specific order
    # based on these offsets.
    coord_lat1_rad = lat_in_radians + n_lat_offset
    coord_long1_rad = long_in_radians + n_long_offset

    coord_lat3_rad = lat_in_radians - n_lat_offset
    coord_long3_rad = long_in_radians - n_long_offset

    # --- Convert corner coordinates back to degrees ---
    coord_lat1_deg = math.degrees(coord_lat1_rad)
    coord_long1_deg = math.degrees(coord_long1_rad)

    coord_lat3_deg = math.degrees(coord_lat3_rad)
    coord_long3_deg = math.degrees(coord_long3_rad)

    # Return the coordinates as a list of (latitude, longitude) tuples
    return [
        (coord_lat1_deg, coord_long1_deg),
        (coord_lat3_deg, coord_long3_deg),
    ]
