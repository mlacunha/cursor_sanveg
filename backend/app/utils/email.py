import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from app.config.settings import get_settings

settings = get_settings()


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    html: bool = False
) -> bool:
    """Send an email using SMTP."""
    try:
        message = MIMEMultipart("alternative")
        message["From"] = settings.EMAIL_FROM
        message["To"] = to_email
        message["Subject"] = subject
        
        if html:
            part = MIMEText(body, "html")
        else:
            part = MIMEText(body, "plain")
        
        message.attach(part)
        
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


async def send_password_reset_email(
    to_email: str,
    reset_token: str,
    user_name: str = ""
) -> bool:
    """Send password reset email with token."""
    reset_link = f"http://yourfrontend.com/reset-password?token={reset_token}"
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #4CAF50; color: white; padding: 10px; text-align: center; }
            .content { padding: 20px; background-color: #f9f9f9; }
            .button { 
                display: inline-block;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }
            .footer { text-align: center; padding: 10px; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>{{ app_name }} - Redefinição de Senha</h2>
            </div>
            <div class="content">
                <p>Olá{% if user_name %} {{ user_name }}{% endif %},</p>
                <p>Você solicitou a redefinição de sua senha.</p>
                <p>Clique no botão abaixo para redefinir sua senha:</p>
                <p style="text-align: center;">
                    <a href="{{ reset_link }}" class="button">Redefinir Senha</a>
                </p>
                <p>Ou copie e cole o link abaixo em seu navegador:</p>
                <p style="word-break: break-all;">{{ reset_link }}</p>
                <p><strong>Este link expira em 1 hora.</strong></p>
                <p>Se você não solicitou esta redefinição, ignore este e-mail.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 {{ app_name }}. Todos os direitos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    template = Template(html_template)
    html_body = template.render(
        reset_link=reset_link,
        user_name=user_name,
        app_name=settings.APP_NAME
    )
    
    return await send_email(
        to_email=to_email,
        subject=f"{settings.APP_NAME} - Redefinição de Senha",
        body=html_body,
        html=True
    )
