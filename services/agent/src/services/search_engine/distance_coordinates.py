import math

# useful links
# https://stackoverflow.com/questions/4000886/gps-coordinates-1km-square-around-a-point
# https://math.stackexchange.com/questions/256931/draw-a-square-around-a-point


def calculate_square_corners(
    latitude: float, longitude: float, side: float = 1000
) -> list[tuple[float, float]]:
    """
    Translates C# code to Python to calculate the four corners of a square
    around a given central latitude and longitude.

    Note: The original C# logic for calculating `lineOfLat` using `Math.Cos(longitude)`
    appears to be a potential mathematical error for geographical calculations.
    It should typically use `math.cos(latitude)` when calculating circumference
    along a parallel of latitude. This translation keeps the original logic intact.

    Args:
        latitude (float): Central latitude in degrees.
        longitude (float): Central longitude in degrees.
        side (float): Side length of the square in meters.

    Returns:
        list[tuple[float, float]]: A list of four (latitude, longitude) tuples
                                   representing the corners of the square, in degrees.
    """

    # Converting degrees to radians
    lat_in_decimals = math.radians(latitude)  # Using math.radians for clarity
    long_in_decimals = math.radians(longitude)  # Using math.radians for clarity

    # Equivalent to List<string> lstStrCoords = new List<string>();
    # This list is declared in C# but not used in the provided snippet.
    # If it's meant to store results, the return type should be adjusted.
    # For now, it's omitted as unused in the calculation logic.

    change_in_lat: float
    change_in_long: float
    line_of_lat: float

    # Calculating change in longitude for square of side 'side' (in meters)
    # 40075 km is approx Earth's equatorial circumference.
    # (side / 1000) converts meters to kilometers.
    change_in_long = (side / 1000) * (360.0 / 40075)

    # Calculating length of longitude at that point of latitude
    # WARNING: Original C# uses `longitude` for Math.Cos, which is likely a bug.
    # For a parallel of latitude's circumference, it should be `latitude`.
    # Translating literally based on C# code.
    line_of_lat = math.cos(long_in_decimals) * 40075  # C# used Math.Cos(longitude)
    # where longitude was in degrees,
    # but math.cos expects radians.
    # So it must be `long_in_decimals`.

    # Calculating change in latitude for square of side 'side'
    # This assumes line_of_lat is a circumference along which a `side` distance
    # corresponds to `change_in_lat` degrees.
    if line_of_lat == 0:
        # This occurs if long_in_decimals is +/- PI/2 (e.g., longitude 90 or -90 degrees).
        # In this specific scenario, division by zero would occur.
        # Handling it by setting change_in_lat to 0, or you might want to raise an error
        # or return a specific value depending on desired behavior for such edge cases.
        # For a direct translation, floating point division might yield 'inf' or 'NaN'.
        change_in_lat = (
            0.0  # Or handle as an error if this state is invalid for your application
        )
    else:
        change_in_lat = (side / 1000) * (360.0 / line_of_lat)

    # Converting changes into radians
    change_in_lat = math.radians(change_in_lat)
    change_in_long = math.radians(change_in_long)

    # Calculate offsets for the four corners
    # (Math.Sqrt(2) / 2) is equivalent to 1 / sqrt(2) or cos(45 degrees) / sin(45 degrees)
    n_lat = change_in_lat * (math.sqrt(2) / 2)
    n_long = change_in_long * (math.sqrt(2) / 2)

    # Calculate corner coordinates in radians
    coord_lat1 = lat_in_decimals + n_lat
    coord_long1 = long_in_decimals + n_long

    coord_lat2 = lat_in_decimals + n_lat
    coord_long2 = long_in_decimals - n_long

    coord_lat3 = lat_in_decimals - n_lat
    coord_long3 = long_in_decimals - n_long

    coord_lat4 = lat_in_decimals - n_lat
    coord_long4 = long_in_decimals + n_long

    # Converting coords back to degrees
    coord_lat1 = math.degrees(coord_lat1)
    coord_lat2 = math.degrees(coord_lat2)
    coord_lat3 = math.degrees(coord_lat3)
    coord_lat4 = math.degrees(coord_lat4)

    coord_long1 = math.degrees(coord_long1)
    coord_long2 = math.degrees(coord_long2)
    coord_long3 = math.degrees(coord_long3)
    coord_long4 = math.degrees(coord_long4)

    # Returning the coordinates as a list of (latitude, longitude) tuples
    return [
        (coord_lat1, coord_long1),
        (coord_lat2, coord_long2),
        (coord_lat3, coord_long3),
        (coord_lat4, coord_long4),
    ]


# Example Usage:
# Assume latitude = 48.1351 (Munich) and longitude = 11.5820 (Munich)
# Assume side = 1000 meters (1 km)
latitude_ex = 41.40543946577699
longitude_ex = 2.174160275086914
side_ex = 1000  # meters

corners = calculate_square_corners(latitude_ex, longitude_ex, side_ex)

print(f"Original Latitude: {latitude_ex}, Longitude: {longitude_ex}")
print(f"Side Length: {side_ex} meters")
print("\nCalculated Corners (Latitude, Longitude):")
for i, (lat, long) in enumerate(corners):
    print(f"  Corner {i+1}: ({lat:.6f}, {long:.6f})")

# Test with a problematic longitude (where cos(longitude) is 0)
# For example, if longitude is 90 degrees or -90 degrees.
# This will trigger the `line_of_lat == 0` handling.
# latitude_problem_test = 0.0
# longitude_problem_test = 90.0
# side_problem_test = 1000
# corners_problem = calculate_square_corners(latitude_problem_test, longitude_problem_test, side_problem_test)
# print(f"\n--- Test with problematic Longitude (Lat: {latitude_problem_test}, Long: {longitude_problem_test}) ---")
# for i, (lat, long) in enumerate(corners_problem):
#     print(f"  Corner {i+1}: ({lat:.6f}, {long:.6f})")
