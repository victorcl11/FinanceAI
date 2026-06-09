import sqlite3
import os
from datetime import datetime
from google import genai
from dotenv import load_dotenv

# ─────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────
load_dotenv()  # Carrega as variáveis do arquivo .env

cliente = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
# ANÁLISE COM GEMINI
# ─────────────────────────────────────────
def analisar_manchetes(manchetes):
    """Envia as manchetes para o Gemini e retorna a análise."""

    if not manchetes:
        print("⚠️  Nenhuma manchete válida no banco. Rode o coletor.py primeiro.")
        return

    # Monta o texto com as manchetes
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

    resposta = cliente.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )

    return resposta.text


# ─────────────────────────────────────────
# EXECUÇÃO PRINCIPAL
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("       FinanceAI — Análise de Mercado")
    print("=" * 55)

    # 1. Busca manchetes do banco
    manchetes = buscar_manchetes()
    print(f"📰 {len(manchetes)} manchetes encontradas no banco.\n")

    if manchetes:
        print("Manchetes sendo analisadas:")
        for i, (titulo, fonte, _) in enumerate(manchetes, 1):
            print(f"  {i}. {titulo[:70]}...")

        print()

        # 2. Envia para o Gemini analisar
        analise = analisar_manchetes(manchetes)

        # 3. Exibe o resultado
        print("=" * 55)
        print("📊 ANÁLISE DO MERCADO")
        print("=" * 55)
        print(analise)
        print("=" * 55)
        print(f"⏱  Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")