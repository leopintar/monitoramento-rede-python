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
