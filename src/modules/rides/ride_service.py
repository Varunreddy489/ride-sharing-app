import pendulum

from src.modules.rides.ride_schema import RideLocationSchema, RideRequestSchema
from src.modules.ws.ws_manager import WebSocketManager
from src.shared.integrations.google_maps import get_distance
from src.shared.utils.exceptions import ResourceNotFoundException
from src.shared.utils.ride_utils import RideUtils


class RideService:
    def __init__(self, ride_repo, user_repo, driver_repo):
        self.ride_repo = ride_repo
        self.user_repo = user_repo
        self.driver_repo = driver_repo
        self.ride_utils = RideUtils()
        self.ws_manager = WebSocketManager()

    async def book_ride(self, payload: RideRequestSchema):
        """
        1.  Check Valid User
        2.  Calculate Distance ( use google_maps )
        3.  Calculate Fare
        4.  Get Nearby Drivers ( 2km )
                a. If not found ( is_online &  is_available NOT true ) extend the search to 4 then 6 till 10
                b. Search max for 10 mins5.  If any drivers found nearby send them the request containing
            (rider_name,pickup and drop locations,distance,fare,estimated time to reach the destination)
        5.  Driver ride acceptance workflow
                a. Only 1 Driver must accept
                b. If Driver Rejects move on to another driver
        6.  Driver Comes to pickup ( Ride Event updates from  DRIVER_ARRIVING to DRIVER_ARRIVED  )
        7.  Driver Picks up Rider
        8.  Ride Starts
        9. Location is updated Every 30 Seconds
        10. Ride is completed
        11. Rider transfers money to Driver in his Wallet
        """

        requested_time = pendulum.now("UTC")

        # Validate User
        valid_user = await self.user_repo.get_user_by_id(payload.id)

        if not valid_user:
            raise ResourceNotFoundException("User does not exist")

        # Calculate Distance
        distance = await get_distance(
            RideLocationSchema.model_validate(payload.model_dump())
        )

        # calculate fare
        fare = self.ride_utils.calculate_ride_fare(distance)

        # get nearby drivers
        drivers = await self.driver_repo.get_nearby_drivers(payload.pickup_point, 2000)

        ride_payload = {
            "pickup": payload.pickup_point,
            "dropoff": payload.dropoff_point,
            "fare": fare,
            distance: distance,
        }

        for driver in drivers:
            await self.ws_manager.send_event(
                driver_id=driver.id,
                event="ride.request",
                data=ride_payload,
            )

        # Todo: Lock the db so that only one driver can accept the ride
