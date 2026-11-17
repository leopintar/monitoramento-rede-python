import os
import json
import platform
import subprocess
import smtplib
import logging
from email.message import EmailMessage
from datetime import datetime

# ==============================================================================
# PROJETO: MONITORAMENTO AUTOMATIZADO DE ATIVOS DE REDE (PYTHON + JSON STATE)
# Autor: Leonardo de Freitas Pintar
# Descrição: Verifica disponibilidade ICMP de switches, roteadores e servidores,
#            controla falhas consecutivas via JSON para evitar falsos positivos
#            e dispara alertas SMTP de queda e normalização.
# ==============================================================================

ATIVOS_CRITICOS = {
    "Roteador Principal / Gateway": "192.168.1.1",
    "Switch Core": "192.168.1.10",
    "Switch de Acesso - Setor Operacional": "192.168.1.11",
    "Servidor de Arquivos & AD": "192.168.1.20",
    "Servidor ERP / Banco de Dados": "192.168.1.25"
}

# Tolerância de falhas consecutivas antes de disparar alerta crítico
LIMITE_FALHAS = 3

# Caminhos absolutos baseados no diretório do script (ideal para Task Scheduler)
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_ESTADO = os.path.join(DIRETORIO_BASE, "estado_monitoramento.json")
ARQUIVO_LOG = os.path.join(DIRETORIO_BASE, "historico_disponibilidade.log")

# Configurações de E-mail via variáveis de ambiente (boa prática de segurança)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_REMETENTE = os.getenv("MONITOR_EMAIL_USER", "alertas.infra@empresa.com.br")
EMAIL_SENHA = os.getenv("MONITOR_EMAIL_PASS", "sua_senha_de_app_aqui")
EMAIL_DESTINATARIO = "equipe.ti@empresa.com.br"

logging.basicConfig(
    filename=ARQUIVO_LOG,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def carregar_estado() -> dict:
    """Carrega o histórico de falhas consecutivas salvo em JSON."""
    if os.path.exists(ARQUIVO_ESTADO):
        try:
            with open(ARQUIVO_ESTADO, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def salvar_estado(estado: dict) -> None:
    """Persiste o estado atual de disponibilidade dos ativos em JSON."""
    with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=4, ensure_ascii=False)


def verificar_ping(ip: str) -> bool:
    """Executa teste ICMP compatível com Windows e Linux."""
    sistema = platform.system().lower()
    param_count = "-n" if sistema == "windows" else "-c"
    param_timeout = "-w" if sistema == "windows" else "-W"
    valor_timeout = "1000" if sistema == "windows" else "1"

    comando = ["ping", param_count, "2", param_timeout, valor_timeout, ip]
    resultado = subprocess.run(
        comando,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return resultado.returncode == 0


def enviar_notificacao(assunto: str, corpo: str) -> None:
    """Envia alerta por e-mail via SMTP com criptografia TLS."""
    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINATARIO
    msg.set_content(corpo)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(EMAIL_REMETENTE, EMAIL_SENHA)
            server.send_message(msg)
        logging.info(f"Notificação enviada: {assunto}")
    except Exception as erro:
        logging.error(f"Erro ao enviar e-mail ({assunto}): {erro}")


def executar_verificacao() -> None:
    """Rotina principal de monitoramento com controle de estado e histerese."""
    estado = carregar_estado()
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    quedas_confirmadas = []
    ativos_recuperados = []

    print(f"[{agora}] Iniciando varredura de {len(ATIVOS_CRITICOS)} ativos...")

    for nome, ip in ATIVOS_CRITICOS.items():
        if ip not in estado:
            estado[ip] = {"nome": nome, "falhas_consecutivas": 0, "alerta_enviado": False}

        online = verificar_ping(ip)

        if online:
            # Se estava em alerta e voltou a responder, notifica normalização
            if estado[ip]["alerta_enviado"]:
                ativos_recuperados.append((nome, ip))
                logging.info(f"RECUPERADO | {nome} ({ip}) voltou a responder.")

            estado[ip]["falhas_consecutivas"] = 0
            estado[ip]["alerta_enviado"] = False
            print(f"[OK]     {nome} ({ip})")
        else:
            estado[ip]["falhas_consecutivas"] += 1
            qtd_falhas = estado[ip]["falhas_consecutivas"]
            print(f"[FALHA]  {nome} ({ip}) - Falha {qtd_falhas}/{LIMITE_FALHAS}")
            logging.warning(f"TIMEOUT | {nome} ({ip}) - Tentativa {qtd_falhas}/{LIMITE_FALHAS}")

            # Dispara alerta apenas ao atingir o limite e evita spam nas execuções seguintes
            if qtd_falhas >= LIMITE_FALHAS and not estado[ip]["alerta_enviado"]:
                quedas_confirmadas.append((nome, ip, qtd_falhas))
                estado[ip]["alerta_enviado"] = True

    salvar_estado(estado)

    if quedas_confirmadas:
        lista_quedas = "\n".join(
            [f" - {nome} (IP: {ip}) | {falhas} verificações sem resposta" for nome, ip, falhas in quedas_confirmadas]
        )
        corpo_alerta = (
            f"ALERTA CRÍTICO DE INFRAESTRUTURA ({agora})\n\n"
            f"Os seguintes ativos atingiram o limite de indisponibilidade:\n\n"
            f"{lista_quedas}\n\n"
            f"Ação recomendada: Verificar link físico, portas de uplink e alimentação."
        )
        enviar_notificacao(f"[CRÍTICO] Indisponibilidade de Rede Detectada - {agora}", corpo_alerta)

    if ativos_recuperados:
        lista_rec = "\n".join([f" - {nome} (IP: {ip})" for nome, ip in ativos_recuperados])
        corpo_rec = (
            f"NORMALIZAÇÃO DE SERVIÇO ({agora})\n\n"
            f"Os seguintes ativos restabeleceram comunicação ICMP:\n\n"
            f"{lista_rec}"
        )
        enviar_notificacao(f"[NORMALIZADO] Ativos de Rede Online - {agora}", corpo_rec)


if __name__ == "__main__":
    executar_verificacao()
