# 📈 FinanceAI

Sistema de coleta e análise de manchetes financeiras com Inteligência Artificial, desenvolvido como Trabalho de Conclusão de Curso (TCC) em Análise e Desenvolvimento de Sistemas (UniCEUB).

O FinanceAI coleta manchetes de portais de notícias financeiras brasileiros em tempo real e utiliza IA (Groq/Llama 3.3) para gerar análises de tendência de mercado, identificação de setores em destaque e pontos de atenção para investidores.

---

## 🎯 Objetivo

Demonstrar a aplicação prática de Inteligência Artificial na análise de sentimento de notícias financeiras, oferecendo ao usuário um panorama rápido do "humor do mercado" a partir de manchetes públicas — sem substituir uma análise profissional, mas servindo como ferramenta de apoio à decisão.

---

## 🏗️ Arquitetura

```
┌─────────────────┐      RSS Feeds      ┌──────────────────┐
│   coletor.py     │ ───────────────────▶│  financeai.db     │
│  (feedparser)    │                      │  (SQLite, cache)  │
└─────────────────┘                      └──────────────────┘
                                                    │
                                                    ▼
┌─────────────────┐      HTTP/JSON      ┌──────────────────┐
│   index.html     │ ◀───────────────────│     app.py         │
│  (dashboard)      │                      │  (Flask + Groq)    │
└─────────────────┘                      └──────────────────┘
```

1. **`coletor.py`** acessa feeds RSS de portais financeiros e salva as manchetes no banco SQLite, com um campo de expiração para manter os dados sempre atualizados (cache temporário).
2. **`app.py`** expõe uma API Flask que busca as manchetes válidas no banco e as envia para a IA (Groq) gerar uma análise estruturada.
3. **`index.html`** é o dashboard onde o usuário pesquisa por palavra-chave e visualiza a análise, estatísticas, setores em destaque e as manchetes originais (clicáveis).

---

## 🛠️ Tecnologias

| Camada | Tecnologia |
|---|---|
| Coleta de dados | Python + `feedparser` |
| Armazenamento | SQLite (cache com expiração) |
| Backend / API | Flask + `flask-cors` |
| Inteligência Artificial | Groq API (modelo `llama-3.3-70b-versatile`) |
| Frontend | HTML + CSS + JavaScript puro |

---

## 📂 Estrutura do projeto

```
FinanceAI/
├── coletor.py          # Coleta manchetes via RSS e salva no SQLite
├── analisador.py        # Script standalone de análise via terminal (CLI)
├── app.py               # Servidor Flask que conecta frontend e IA
├── index.html            # Dashboard (frontend)
├── requirements.txt      # Dependências do projeto
├── .env                  # Variáveis de ambiente (chave de API) — não versionado
├── .gitignore
└── financeai.db          # Banco gerado automaticamente (não versionado)
```

---

## ⚙️ Como executar

### 1. Clonar o repositório
```bash
git clone https://github.com/victorcl11/FinanceAI.git
cd FinanceAI
```

### 2. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar a chave de API
Crie um arquivo `.env` na raiz do projeto com sua chave da [Groq](https://console.groq.com):
```
GROQ_API_KEY=sua_chave_aqui
```

### 4. Coletar as manchetes
```bash
python coletor.py
```

### 5. Subir o servidor
```bash
python app.py
```

### 6. Abrir o dashboard
Abra o arquivo `index.html` no navegador.

---

## 🧠 Como funciona a análise de IA

As manchetes coletadas são enviadas para o modelo de linguagem da Groq com um prompt estruturado, solicitando uma resposta em JSON contendo:

- **Tendência geral** do mercado (positiva, negativa ou neutra)
- **Resumo executivo** da situação
- **Setores em destaque** com percentual de relevância
- **Pontos de atenção** para o investidor
- **Contagem de manchetes** por sentimento (positivas, negativas, neutras)

Esse JSON é consumido pelo frontend e renderizado dinamicamente nos cards do dashboard.

---

## 🗃️ Sobre o cache de manchetes

O mercado financeiro é extremamente volátil — uma notícia de algumas horas atrás pode já estar defasada. Por isso, o SQLite é usado como um **cache temporário**: cada manchete tem um timestamp de expiração, e manchetes expiradas são automaticamente descartadas nas próximas coletas, garantindo que apenas informações relevantes e recentes sejam analisadas.

---

## 👤 Autor

Victor — Estudante de Análise e Desenvolvimento de Sistemas (UniCEUB)
Trabalho de Conclusão de Curso — disciplina de Inteligência Artificial

---

## ⚠️ Aviso legal

Este projeto tem finalidade exclusivamente acadêmica e educacional. As análises geradas pela IA **não constituem recomendação de investimento**. Decisões financeiras devem ser tomadas com base em análise profissional qualificada.
