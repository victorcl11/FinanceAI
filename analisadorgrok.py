import sqlite3
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# ─────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────
load_dotenv()

cliente = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# ─────────────────────────────────────────
# BUSCA MANCHETES VÁLIDAS NO BANCO
# ─────────────────────────────────────────
def buscar_manchetes():
    """Retorna as manchetes que ainda não expiraram."""
    conn = sqlite3.connect("financeai.db")
    cursor = conn.cursor()

    agora = datetime.now().isoformat()

    cursor.execute("""
        SELECT titulo, fonte, publicado
        FROM manchetes
        WHERE expira_em > ?
        ORDER BY publicado DESC
    """, (agora,))

    manchetes = cursor.fetchall()
    conn.close()
    return manchetes


# ─────────────────────────────────────────
# ANÁLISE COM GROK
# ─────────────────────────────────────────
def analisar_manchetes(manchetes):
    """Envia as manchetes para o Grok e retorna a análise."""

    if not manchetes:
        print("⚠️  Nenhuma manchete válida no banco. Rode o coletor.py primeiro.")
        return

    lista_manchetes = ""
    for i, (titulo, fonte, publicado) in enumerate(manchetes, 1):
        lista_manchetes += f"{i}. [{fonte}] {titulo}\n"

    prompt = f"""Você é um analista financeiro especializado no mercado brasileiro.
Analise as seguintes manchetes financeiras e forneça:

1. TENDÊNCIA GERAL: (Positiva / Negativa / Neutra) com justificativa resumida
2. SETORES EM DESTAQUE: quais setores são mais mencionados e como estão
3. PONTOS DE ATENÇÃO: manchetes que merecem atenção do investidor
4. RESUMO EXECUTIVO: 2-3 frases resumindo o momento do mercado

Manchetes coletadas:
{lista_manchetes}

Seja objetivo e direto. Foque no impacto para o investidor brasileiro."""

    print("🤖 Enviando manchetes para análise...\n")

    resposta = cliente.chat.completions.create(
        model="grok-3-fast-beta",
        messages=[
            {
                "role": "system",
                "content": "Você é um analista financeiro experiente focado no mercado brasileiro. Suas análises são objetivas, claras e úteis para investidores."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return resposta.choices[0].message.content


# ─────────────────────────────────────────
# EXECUÇÃO PRINCIPAL
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("       FinanceAI — Análise de Mercado")
    print("=" * 55)

    manchetes = buscar_manchetes()
    print(f"📰 {len(manchetes)} manchetes encontradas no banco.\n")

    if manchetes:
        print("Manchetes sendo analisadas:")
        for i, (titulo, fonte, _) in enumerate(manchetes, 1):
            print(f"  {i}. {titulo[:70]}...")

        print()

        analise = analisar_manchetes(manchetes)

        print("=" * 55)
        print("📊 ANÁLISE DO MERCADO")
        print("=" * 55)
        print(analise)
        print("=" * 55)
        print(f"⏱  Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    else:
        print("⚠️  Banco vazio. Rode o coletor.py primeiro.")
