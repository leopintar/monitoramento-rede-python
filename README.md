# 🌐 Monitoramento Automatizado de Ativos de Rede em Python

Solução desenvolvida em **Python** para monitoramento contínuo de disponibilidade (ICMP/Ping) de switches, roteadores e servidores críticos, com persistência de estado em **JSON** para eliminação de falsos positivos, geração de logs de auditoria e alertas automáticos de queda e normalização via **SMTP**.

---

## 🎯 Problema Resolvido e Arquitetura
Em ambientes corporativos e industriais, a perda isolada de um único pacote não significa necessariamente que um switch ou servidor caiu. Para evitar alertas desnecessários (*alert fatigue*) e, ao mesmo tempo, garantir resposta rápida antes que os usuários abram chamados no Service Desk (**GLPI**), o script implementa:

1. **Controle de Estado Persistente (`estado_monitoramento.json`):** Contabiliza falhas consecutivas por endereço IP entre execuções agendadas. O alerta crítico só é disparado quando o ativo atinge o limite configurado (`LIMITE_FALHAS`).
2. **Prevenção de Spam e Notificação de Recuperação:** Após disparar o alerta de queda, o sistema marca o incidente como notificado e envia um novo e-mail automático assim que a conectividade é restabelecida.
3. **Resolução Dinâmica de Caminhos (`os.path`):** Permite execução em segundo plano no **Agendador de Tarefas do Windows (`pythonw.exe`)** ou via **Cron no Linux** sem falhas de diretório relativo.

---

## 🛠️ Tecnologias Utilizadas
* **Python 3.x** (`subprocess`, `json`, `smtplib`, `logging`, `platform`, `email`)
* **Protocolos:** ICMP (Echo Request/Reply) e SMTP sobre TLS
* **Orquestração:** Windows Task Scheduler (`pythonw.exe` para execução silenciosa) / Linux Crontab

---

## ⚙️ Como Configurar e Automatizar

1. Clone o repositório:
   ```bash
   git clone [https://github.com/leopintar/monitoramento-rede-python.git](https://github.com/leopintar/monitoramento-rede-python.git)
   ```
2. Edite o dicionário `ATIVOS_CRITICOS` e a variável `LIMITE_FALHAS` em `monitor_rede.py` conforme a topologia da sua rede.
3. Defina as variáveis de ambiente de autenticação SMTP no sistema operacional (`MONITOR_EMAIL_USER` e `MONITOR_EMAIL_PASS`).
4. **Agendamento Silencioso no Windows:**
   * Abra o **Agendador de Tarefas (`taskschd.msc`)** > **Criar Tarefa**.
   * Configure o disparador para repetir a cada **1 ou 5 minutos**.
   * Em **Ações**, aponte o programa para `pythonw.exe` (evita abertura de janela de terminal) e passe o caminho completo de `monitor_rede.py` como argumento.

---
**Desenvolvido por:** [Leonardo de Freitas Pintar](https://github.com/leopintar) — *Engenheiro de Computação | Infraestrutura, Redes & Automação*
