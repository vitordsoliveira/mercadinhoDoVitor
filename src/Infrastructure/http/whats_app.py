import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

def get_twilio_config():
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')

    if not all([account_sid, auth_token, twilio_whatsapp_number]):
        raise ValueError(
            "As variaveis de ambiente da Twilio não foram configuradas."
        )

    return account_sid, auth_token, twilio_whatsapp_number

def send_activation_code(to_whatsapp_number: str, code: str):
    try:
        account_sid, auth_token, twilio_whatsapp_number = get_twilio_config()
        client = Client(account_sid, auth_token)
        message_body = f'Seu código de ativação é: *{code}*'
        message = client.messages.create(
            from_=f'whatsapp:{twilio_whatsapp_number}',
            body=message_body,
            to=f'whatsapp:{to_whatsapp_number}'
        )
        print(f"Mensagem de ativação enviada para {to_whatsapp_number}. SID: {message.sid}")
    except Exception as e:
        print(f"Erro ao enviar mensagem via Twilio: {e}")
        raise e