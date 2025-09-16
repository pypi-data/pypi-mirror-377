from asgiref.sync import sync_to_async

from django.utils import timezone

from utils.locking import global_lock
from .models import FlightSession


class FlightService:
    @classmethod
    def _lock(cls):
        # Convenience method to create a lock object, as it is not reusable
        return global_lock("flight_management_lock")

    @classmethod
    @sync_to_async
    def start_flight_session(cls):
        """
        Start a new flight session.

        This method initiates a flight session, triggering any registered
        callbacks or actions associated with the flight start event.

        Raises:
            ValueError: If a flight session is already in progress.

        Returns:make
            FlightSession: The newly created flight session.
        """
        with cls._lock():
            current = FlightSession.objects.current()
            if current:
                raise ValueError("A flight session is already in progress.")

            session = FlightSession.objects.create()

        return session

    @classmethod
    @sync_to_async
    def end_flight_session(cls):
        """
        End the current flight session.

        This method concludes the flight session, marking it as ended and
        triggering any registered callbacks or actions associated with the
        flight end event.

        Raises:
            ValueError: If no flight session is currently in progress.

        Returns:
            FlightSession: The ended flight session.
        """
        with cls._lock():
            current = FlightSession.objects.current()
            if not current:
                raise ValueError("No flight session is currently in progress.")

            current.ended_at = timezone.now()
            current.asave()

        return current

    @classmethod
    @sync_to_async
    def get_current_flight_session(cls):
        """
        Retrieve the current flight session.

        Returns:
            FlightSession: The current flight session if it exists, otherwise None.
        """
        with cls._lock():
            return FlightSession.objects.current()

    @classmethod
    async def get_flight_session_by_id(cls, session_id):
        """
        Retrieve a flight session by its ID.

        Args:
            session_id (int): The ID of the flight session to retrieve.

        Returns:
            FlightSession: The flight session with the specified ID, or None if not found.
        """
        return await FlightSession.objects.filter(id=session_id).afirst()
