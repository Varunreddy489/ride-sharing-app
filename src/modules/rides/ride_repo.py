from src.modules.rides.ride_model import RideModel
from src.modules.rides.ride_schema import RideRequestSchema


class RideRepo:
    def __init__(self, session):
        self.session = session

    async def create_ride(self, payload: RideRequestSchema) -> bool:

        new_ride = payload.model_dump()

        ride = RideModel(**new_ride)

        self.session.add(ride)
        self.session.commit()
        self.session.refresh(ride)

        return True
