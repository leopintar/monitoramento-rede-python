import os
import platform
import subprocess
import smtplib
import logging
from email.message import EmailMessage
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÕES DO AMBIENTE E ATIVOS DE REDE
# ==============================================================================
ATIVOS_CRITICOS = {
    "Servidor AD / DNS Principal": "192.168.1.10",
    "Servidor de Arquivos (File Server)": "192.168.1.15",
    "Switch Core - Sala de Servidores": "192.168.1.2",
    "Gateway / Firewall Corporativo": "192.168.1.1",
    "Impressora Térmica - Expedição": "192.168.1.120"
}

# Configurações de E-mail (Utiliza variáveis de ambiente por segurança)
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
EMAIL_REMETENTE = os.getenv("MONITOR_EMAIL_USER", "alertas.ti@empresa.com.br")
EMAIL_SENHA = os.getenv("MONITOR_EMAIL_PASS", "sua_senha_de_app_aqui")
EMAIL_DESTINATARIO = "infraestrutura@empresa.com.br"

# Configuração de Logs de Auditoria
ARQUIVO_LOG = "historico_disponibilidade.log"
logging.basicConfig(
    filename=ARQUIVO_LOG,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def verificar_conectividade(ip: str) -> bool:
    """
    Executa um teste ICMP (Ping) compatível com Windows e Linux.
    Retorna True se o host responder, False caso contrário.
    """
    parametro = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    timeout_val = "1000" if platform.system().lower() == "windows" else "1"

    comando = ["ping", parametro, "2", timeout_param, timeout_val, ip]
    resposta = subprocess.run(
        comando,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return resposta.returncode == 0


def enviar_alerta_email(ativos_offline: list):
    """
    Dispara um e-mail automático para a equipe de Infraestrutura
    listando os dispositivos que apresentaram falha de comunicação.
    """
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    msg = EmailMessage()
    msg["Subject"] = f"[ALERTA CRÍTICO DE INFRAESTRUTURA] Ativos Offline - {data_hora}"
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINATARIO

    lista_formatada = "\n".join(
        [f" - {nome} (IP: {ip})" for nome, ip in ativos_offline]
    )

    corpo = f"""Prezados,

O sistema de monitoramento automático detectou falha de comunicação (ICMP Timeout) nos seguintes ativos de rede:

{lista_formatada}

Data/Hora da verificação: {data_hora}

Ação recomendada: Verificar links físicos, portas de switches correspondentes e status dos serviços nos servidores.

--
Script de Monitoramento Automatizado de Infraestrutura (Python)
"""
    msg.set_content(corpo)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(EMAIL_REMETENTE, EMAIL_SENHA)
            server.send_message(msg)
        logging.info("Alerta de e-mail enviado com sucesso para a equipe de TI.")
    except Exception as erro:
        logging.error(f"Falha ao enviar e-mail de alerta: {erro}")


def executar_monitoramento():
    """
    Percorre a lista de ativos críticos, registra logs e aciona alertas se necessário.
    """
    print("=" * 65)
    print(f"INICIANDO VERIFICAÇÃO DE ATIVOS DE REDE - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 65)

    ativos_offline = []

    for nome, ip in ATIVOS_CRITICOS.items():
        online = verificar_conectividade(ip)
        if online:
            status_msg = f"ONLINE  | {nome} ({ip})"
            print(f"[OK]   {status_msg}")
            logging.info(status_msg)
        else:
            status_msg = f"OFFLINE | {nome} ({ip}) - Sem resposta ICMP"
            print(f"[ERRO] {status_msg}")
            logging.warning(status_msg)
            ativos_offline.append((nome, ip))

    print("=" * 65)
    if ativos_offline:
        print(f"ATENÇÃO: {len(ativos_offline)} ativo(s) offline detectado(s). Acionando alerta...")
        enviar_alerta_email(ativos_offline)
    else:
        print("Status Global: Todos os ativos críticos estão operacionais (100% Online).")


if __name__ == "__main__":
    executar_monitoramento()
