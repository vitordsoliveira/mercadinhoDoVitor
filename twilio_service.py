import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

#validação de dados
if not all([ACCOUNT_SID, AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER]):
    raise ValueError("As variáveis de ambiente da Twilio (ACCOUNT_SID, AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER) não foram configuradas corretamente. Verifique seu arquivo .env")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_activation_code(to_whatsapp_number: str, code: str):
    try:
        message_body = f'Seu código de ativação para o Gestão de Estoque é: *{code}*'
        message = client.messages.create(
            from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
            body=message_body,
            to=f'whatsapp:{to_whatsapp_number}'
        )
        print(f"Mensagem de ativação enviada para {to_whatsapp_number}. SID: {message.sid}")
    except Exception as e:
        print(f"Erro ao enviar mensagem via Twilio: {e}")
        raise e