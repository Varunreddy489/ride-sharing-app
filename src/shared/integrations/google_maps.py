from src.modules.rides.ride_schema import RideLocationSchema
from src.shared.api.rest import make_http_call
from src.shared.utils.config import get_settings


async def get_distance(ride_coordinates: RideLocationSchema) -> float:
    settings = get_settings()

    url = f"{settings.google_maps_settings.google_maps_base_url}/distancematrix/json?origins={ride_coordinates.pickup_latitude, ride_coordinates.pickup_longitude}&destination={ride_coordinates.dropoff_latitude, ride_coordinates.dropoff_longitude}&units=metric&key={settings.google_maps_api_key}"

    resp = await make_http_call(
        url=url, method="GET", timeout=settings.google_maps_settings.maps_timeout
    )
    return resp.json()
