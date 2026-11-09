# 🌐 Monitoramento Automatizado de Ativos de Rede em Python

Ferramenta desenvolvida em **Python** para verificação contínua de disponibilidade (ICMP/Ping) de ativos críticos de infraestrutura de TI (Servidores Windows/Linux, Switches, Roteadores e Impressoras de rede), com geração de logs de auditoria e disparo automático de alertas por e-mail via protocolo SMTP.

---

## 🎯 Problema de Negócio e Solução
Em ambientes corporativos e industriais, identificar rapidamente a queda de um switch, servidor ou impressora crítica é essencial para manter a disponibilidade operacional e cumprir os indicadores de **SLA** no Service Desk (**GLPI**).

Este projeto automatiza a verificação preventiva da infraestrutura:
1. Testa a conectividade de uma lista configurável de IPs críticos (compatível com **Windows** e **Linux**).
2. Registra todas as ocorrências em um arquivo de log estruturado (`historico_disponibilidade.log`) para análise de estabilidade.
3. Dispara automaticamente um **alerta por e-mail** para a equipe de Infraestrutura caso algum equipamento fique indisponível.

---

## 🛠️ Tecnologias Utilizadas
* **Python 3.x** (Bibliotecas nativas: `subprocess`, `smtplib`, `logging`, `platform`, `email`)
* **Protocolos de Rede:** ICMP (Echo Request / Echo Reply) e SMTP com criptografia TLS
* **Automação de S.O.:** Integração direta com o **Agendador de Tarefas do Windows (Task Scheduler)** ou **Cron (Linux)**

---

## ⚙️ Como Executar e Automatizar no Windows

1. Clone o repositório:
   ```bash
   git clone [https://github.com/leopintar/monitoramento-rede-python.git](https://github.com/leopintar/monitoramento-rede-python.git)

2. Configure os IPs dos ativos da sua rede no dicionário ATIVOS_CRITICOS dentro de monitor_rede.py.

3. Para execução contínua automática no Windows:

    Abra o Agendador de Tarefas (taskschd.msc) > Criar Tarefa Básica.

    Defina o disparador para repetir a cada 5 ou 10 minutos.

    Em Ação, selecione Iniciar um programa, aponte para o executável do python.exe e adicione o caminho do script monitor_rede.py nos argumentos.


Exemplo de Saída no Console / Log

=================================================================
INICIANDO VERIFICAÇÃO DE ATIVOS DE REDE - 09/11/2026 16:00:01
=================================================================
[OK]   ONLINE  | Servidor AD / DNS Principal (192.168.1.10)
[OK]   ONLINE  | Servidor de Arquivos (File Server) (192.168.1.15)
[OK]   ONLINE  | Switch Core - Sala de Servidores (192.168.1.2)
[OK]   ONLINE  | Gateway / Firewall Corporativo (192.168.1.1)
[ERRO] OFFLINE | Impressora Térmica - Expedição (192.168.1.120) - Sem resposta ICMP
=================================================================
ATENÇÃO: 1 ativo(s) offline detectado(s). Acionando alerta...


Desenvolvido por: Leonardo de Freitas Pintar — Engenheiro de Computação & Analista de Infraestrutura de TI
