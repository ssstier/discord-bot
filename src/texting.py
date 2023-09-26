# Download the helper library from https://www.twilio.com/docs/python/install
# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
from twilio.rest import Client

def send_text(destination_number, message, source_number, account_sid, auth_token):
    client = Client(account_sid, auth_token)
    message = client.messages.create(body=message, from_=source_number,
                                     to= f'+1{destination_number}')


