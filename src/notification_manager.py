import smtplib
from flight_data import FlightData
from twilio.rest import Client
from abc import ABC, abstractmethod
import os


class Notifier(ABC):
    """This class is responsible for sending notifications
    with the flight details."""

    def __init__(self, flight: FlightData, passengers_num: str = "1"):
        self.flight = flight
        self.passengers_num = passengers_num

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
        # TODO Try except
        account_sid = os.getenv("TWILIO_SID")
        auth_token = os.getenv("TWILIO_AUTH")
        my_phone_no = os.getenv("TWILIO_PHONE")  # your phone from twilio
        to_phone_no = os.getenv("TO_PHONE")  # phone num for receiving msg
        client = Client(account_sid, auth_token)
        client.messages.create(
            to=to_phone_no, from_=my_phone_no, body=self.msg_text
        )
        return True


class EmailNotifier(Notifier):
    def send_msg(self) -> bool:
        out_email = os.getenv("FROM_EMAIL")
        forward_dep_date = self.flight.route.forward_dep_dtime.strftime("%d%m")
        backward_arr_date = self.flight.route.return_dep_dtime.strftime("%d%m")
        route = self.flight.route
        aviasales_link = (
            f"https://www.aviasales.com/search/"
            f"{route.forward_dep_airport}{forward_dep_date}"
            f"{route.forward_arr_airport}{backward_arr_date}"
            f"{self.passengers_num}"
        )
        # TODO Try except
        with smtplib.SMTP("smtp.google.com", port=587, timeout=2) as conn:
            conn.starttls()
            conn.login(user=out_email, password=os.getenv("FROM_EMAIL_PASS"))
            conn.sendmail(
                from_addr=out_email,
                to_addrs=os.getenv("TO_EMAIL"),
                msg="Subject: Cheap Flight! Hurry Up!\n\n"
                f"{self.msg_text}\n"
                f"You can book your flight using the link below:\n"
                f"{aviasales_link}",
            )
        return True


class TelegramNotifier(Notifier):
    def send_msg(self) -> bool:  # TODO
        pass
