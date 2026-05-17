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

def _send_whatsapp(to_number: str, body: str):
    account_sid, auth_token, twilio_whatsapp_number = get_twilio_config()
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_=f'whatsapp:{twilio_whatsapp_number}',
        body=body,
        to=f'whatsapp:{to_number}',
    )
    return message


def send_activation_code(to_whatsapp_number: str, code: str):
    try:
        message = _send_whatsapp(to_whatsapp_number, f'Seu código de ativação é: *{code}*')
        print(f"Código de ativação enviado para {to_whatsapp_number}. SID: {message.sid}")
    except Exception as e:
        print(f"Erro ao enviar mensagem via Twilio: {e}")
        raise e


def send_password_change_code(to_whatsapp_number: str, code: str):
    try:
        message = _send_whatsapp(to_whatsapp_number, f'Seu código para troca de senha é: *{code}*. Não compartilhe com ninguém.')
        print(f"Código de troca de senha enviado para {to_whatsapp_number}. SID: {message.sid}")
    except Exception as e:
        print(f"Erro ao enviar mensagem via Twilio: {e}")
        raise e