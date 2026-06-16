import sqlite3
import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# ─────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────
load_dotenv()

app = Flask(__name__)
CORS(app)  # Permite o frontend chamar o backend sem bloqueio

cliente = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# ─────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────
def buscar_manchetes(keyword=None):
    """Retorna manchetes válidas do banco, filtrando por keyword se informada."""
    conn = sqlite3.connect("financeai.db")
    cursor = conn.cursor()

    agora = datetime.now().isoformat()

    if keyword:
        cursor.execute("""
            SELECT titulo, fonte, publicado, link
            FROM manchetes
            WHERE expira_em > ?
            AND titulo LIKE ?
            ORDER BY publicado DESC
        """, (agora, f"%{keyword}%"))
    else:
        cursor.execute("""
            SELECT titulo, fonte, publicado, link
            FROM manchetes
            WHERE expira_em > ?
            ORDER BY publicado DESC
        """, (agora,))

    manchetes = cursor.fetchall()
    conn.close()
    return manchetes


def analisar_com_grok(manchetes, keyword):
    """Envia as manchetes para o Grok e retorna a análise estruturada em JSON."""

    lista_manchetes = ""
    for i, (titulo, fonte, publicado, link) in enumerate(manchetes, 1):
        lista_manchetes += f"{i}. [{fonte}] {titulo}\n"

    prompt = f"""Você é um analista financeiro especializado no mercado brasileiro.
Analise as manchetes abaixo sobre "{keyword}" e responda APENAS com um JSON válido, sem texto adicional.

Formato exato:
{{
  "tendencia": "positiva" ou "negativa" ou "neutra",
  "resumo": "2-3 frases resumindo o momento do mercado",
  "setores": [
    {{"nome": "Nome do setor", "percentual": 0-100}},
    ...
  ],
  "pontos_atencao": [
    "ponto 1",
    "ponto 2",
    "ponto 3"
  ],
  "contagem": {{
    "positivas": número,
    "negativas": número,
    "neutras": número
  }}
}}

Manchetes:
{lista_manchetes}"""

    resposta = cliente.chat.completions.create(
        model="grok-3-fast-beta",
        messages=[
            {
                "role": "system",
                "content": "Você é um analista financeiro. Responda SOMENTE com JSON válido, sem markdown, sem texto antes ou depois."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    import json
    texto = resposta.choices[0].message.content.strip()
    # Remove possíveis blocos de markdown caso venham
    texto = texto.replace("```json", "").replace("```", "").strip()
    return json.loads(texto)


# ─────────────────────────────────────────
# ROTAS
# ─────────────────────────────────────────

@app.route("/")
def index():
    return jsonify({"status": "FinanceAI backend rodando ✅"})


@app.route("/analisar", methods=["POST"])
def analisar():
    """Recebe keyword do frontend, busca manchetes e retorna análise da IA."""
    try:
        data = request.get_json()
        keyword = data.get("keyword", "").strip()

        if not keyword:
            return jsonify({"erro": "Palavra-chave não informada."}), 400

        # 1. Busca manchetes do banco
        manchetes = buscar_manchetes(keyword)

        # Se não achou com o filtro, pega todas as válidas
        if not manchetes:
            manchetes = buscar_manchetes()

        if not manchetes:
            return jsonify({
                "erro": "Nenhuma manchete no banco. Rode o coletor.py primeiro."
            }), 404

        # 2. Analisa com o Grok
        analise = analisar_com_grok(manchetes, keyword)

        # 3. Adiciona as manchetes ao retorno para o frontend exibir
        analise["manchetes"] = [
            {
                "titulo": titulo,
                "fonte": fonte,
                "publicado": publicado,
                "link": link
            }
            for titulo, fonte, publicado, link in manchetes[:10]  # máximo 10
        ]

        return jsonify(analise)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/manchetes", methods=["GET"])
def listar_manchetes():
    """Retorna todas as manchetes válidas no banco."""
    manchetes = buscar_manchetes()
    return jsonify({
        "total": len(manchetes),
        "manchetes": [
            {"titulo": t, "fonte": f, "publicado": p, "link": l}
            for t, f, p, l in manchetes
        ]
    })


# ─────────────────────────────────────────
# INICIALIZAÇÃO
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  FinanceAI — Backend rodando")
    print("  Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
