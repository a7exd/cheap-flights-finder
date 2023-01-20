from flight_data import FlightData
from twilio.rest import Client
from abc import ABC, abstractmethod
import os


class Notifier(ABC):
    """This class is responsible for sending notifications
    with the flight details."""

    def __init__(self, flight: FlightData):
        self.flight = flight

    @abstractmethod
    def send_msg(self) -> bool:
        pass

    @property
    def msg_text(self) -> str:
        fl = self.flight
        forward_dep_date = fl.route.forward_dep_dtime.strftime("%Y-%m-%d")
        backward_arr_date = fl.route.return_arr_dtime.strftime("%Y-%m-%d")
        text = (
            f"Cheap flight! Only ${fl.price} to fly"
            f" from {fl.from_city}-{fl.route.forward_dep_airport}"
            f" to {fl.to_city}-{fl.route.forward_arr_airport},"
            f" from {forward_dep_date} to {backward_arr_date}."
        )
        if (count := fl.route.stopovers_count) > 0:
            text += (
                f"Flight has {count} stopover, forward via"
                f" {', '.join(fl.route.forward_stopovers)},"
                f" backward via"
                f" {', '.join(fl.route.backward_stopovers)}."
            )
        return text


class TwilioNotifier(Notifier):
    def send_msg(self) -> bool:
        account_sid = os.getenv("TWILIO_SID")
        auth_token = os.getenv("TWILIO_AUTH")
        my_phone_no = os.getenv("TWILIO_PHONE")  # your phone from twilio
        to_phone_no = os.getenv("TO_PHONE")  # phone num for receiving msg
        client = Client(account_sid, auth_token)
        client.messages.create(
            to=to_phone_no, from_=my_phone_no, body=self.msg_text
        )
        return True
