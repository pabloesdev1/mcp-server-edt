from fastmcp import FastMCP
from fastapi import FastAPI
from fastmcp.server.auth import StaticTokenVerifier
from dotenv import load_dotenv
import smtplib
import email
from email.mime.text import MIMEText
import os

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


tokens = {
    "my-secret-token": {
        "client_id": "client_123",
        "scopes": ["read:data"]
    },
}

verifier = StaticTokenVerifier(tokens=tokens)

mcp = FastMCP("MCP Server", auth=verifier)
mcp_app = mcp.http_app()
api = FastAPI(lifespan=mcp_app.lifespan)

@api.get("/api/status")
def status():
    return {"status": "ok"}

@mcp.tool(
    name="send_email",
    description="Send an email using SMTP",
)
def send_email(
    to: str,
    subject: str,
    body: str):
    msg = MIMEText(body, "html")
    msg["From"] = EMAIL_USER
    msg["To"] = to
    msg["Subject"] = subject

    with smtplib.SMTP(SMTP_SERVER, 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, [to], msg.as_string())

    return {"status": "success", "to": to, "subject": subject}


@mcp.prompt(
    name="detect_action",
    description="Detecta la accion del usuario",
)
def detect_action(message: str) -> str:
    return f"""
    Detecta la accion que el usuario quiere realizar:
    Existen dos tipos de acciones posibles: 'saludo', 'informacion_productos'.
    - Si el usuario esta saludando, la accion es 'saludo'.
    - Si el usuario esta pidiendo informacion sobre productos, la accion es 'informacion_productos'.

    El mensaje del usuario es:
    '{message}'

    Responde con un json con los siguientes campos:
    - action: el nombre de la accion a realizar, puede ser 'saludo', 'informacion_productos'
    """


@mcp.prompt(
    name="client_info",
    description="Comprueba si el usuario proporciona su nombre y correo electronico",
)
def client_info(message: str) -> str:
    return f"""
    Comprueba si el usuario proporciona su email y nombre.
    El mensaje del usuario es:
    '{message}'

    Responde con un json con los siguientes campos:
    - name (str | null): el nombre del cliente
    - email (str | null): el email del cliente
    """

@mcp.prompt(
    name="welcome_email",
    description="Genera un email de bienvenida para un nuevo cliente"
)
def welcome_email(name: str, products: str):
    #products_list = ""
    #for product in products:
    #    products_list += f"{product['name']}, Price: {product['price']}\n"
    
    return f"""
    Genera un email de bienvenida para un nuevo cliente.
    El nombre del cliente es: {name}
    Los productos disponibles son:
    {products}

    El email debe tener un saludo inicial, una presentacion de los productos en formato lista HTML,
    y una despedida cordial.

    Responde con el contenido del email en formato HTML.
    Devuelve tambien el subject del email.
    La respuesta debe tener el siguiente formato JSON:

    - subject (str): "Asunto del email",
    - body (str): "Contenido del email en HTML"
    """

api.mount("/api", mcp_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
# mcp.run(transport="http", host="0.0.0.0", port=8000)
