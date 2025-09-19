from ambipy_utils.email_sender import EmailSender

ALERTS_EMAIL_SENDER = "alertas@ambiparcarbon.solutions"
ALERTS_NAME_SENDER = "Sistema de Alertas Ambipar"

email_sender = EmailSender(
    aws_access_key_id="AKIA5GQFDN6GNN23ITNJ",
    aws_secret_access_key="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",
    aws_region="us-east-2",
)

response = email_sender.send(
    content="teste",
    subject="Teste de envio de email",
    receivers=["wendellmorais.dev@gmail.com"],
    from_email=ALERTS_EMAIL_SENDER,
    from_name=ALERTS_NAME_SENDER,
)

print(response)
