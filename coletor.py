import feedparser
import sqlite3
from datetime import datetime, timedelta

# ─────────────────────────────────────────
# FONTES RSS FINANCEIRAS
# ─────────────────────────────────────────
FEEDS = [
    {"nome": "InfoMoney",         "url": "https://www.infomoney.com.br/feed/"},
    {"nome": "Valor Econômico",   "url": "https://valor.globo.com/rss/home"},
    {"nome": "Reuters Brasil",    "url": "https://br.reuters.com/rssFeed/businessNews"},
    {"nome": "InfoMoney Mercados","url": "https://www.infomoney.com.br/mercados/feed/"},
    {"nome": "InfoMoney Negócios","url": "https://www.infomoney.com.br/negocios/feed/"},
    {"nome": "CNN Brasil Economia","url": "https://www.cnnbrasil.com.br/economia/feed/"},
    {"nome": "Estadão Economia",  "url": "https://www.estadao.com.br/economia/rss"},
    {"nome": "Money Times",       "url": "https://www.moneytimes.com.br/feed/"},
]

# Quanto tempo cada manchete fica válida no banco
HORAS_VALIDADE = 6

# ─────────────────────────────────────────
# BANCO DE DADOS
# ─────────────────────────────────────────
def conectar_banco():
    """Cria (ou abre) o arquivo financeai.db e garante que a tabela existe."""
    conn = sqlite3.connect("financeai.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manchetes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo     TEXT NOT NULL,
            link       TEXT NOT NULL UNIQUE,   -- UNIQUE evita duplicatas pelo link
            fonte      TEXT,
            publicado  TEXT,
            expira_em  TEXT
        )
    """)
    conn.commit()
    return conn, cursor


# ─────────────────────────────────────────
# COLETA
# ─────────────────────────────────────────
def coletar_manchetes(cursor, conn):
    """Percorre cada feed RSS e salva as manchetes novas no banco."""
    total_novas = 0

    for feed_info in FEEDS:
        print(f"\n📡 Coletando: {feed_info['nome']}...")

        feed = feedparser.parse(feed_info["url"])

        if feed.bozo:
            # bozo=True significa que o feedparser encontrou algum problema no XML
            print(f"   ⚠️  Problema ao ler o feed (pode ser bloqueio ou URL inválida)")
            continue

        for noticia in feed.entries:
            titulo    = noticia.get("title",     "Sem título")
            link      = noticia.get("link",      "")
            publicado = noticia.get("published") or noticia.get("updated", "")
            expira_em = (datetime.now() + timedelta(hours=HORAS_VALIDADE)).isoformat()

            if not link:
                continue  # sem link não tem como identificar a notícia

            try:
                cursor.execute("""
                    INSERT INTO manchetes (titulo, link, fonte, publicado, expira_em)
                    VALUES (?, ?, ?, ?, ?)
                """, (titulo, link, feed_info["nome"], publicado, expira_em))
                conn.commit()
                total_novas += 1
                print(f"   ✅ {titulo[:80]}...")

            except sqlite3.IntegrityError:
                # Link já existe no banco (UNIQUE constraint) — ignora silenciosamente
                pass

    print(f"\n💾 {total_novas} manchetes novas salvas no banco.")


# ─────────────────────────────────────────
# CONSULTA — só manchetes ainda válidas
# ─────────────────────────────────────────
def buscar_manchetes_validas(cursor):
    """Retorna apenas manchetes cujo prazo de validade ainda não expirou."""
    agora = datetime.now().isoformat()

    cursor.execute("""
        SELECT titulo, fonte, publicado, link
        FROM manchetes
        WHERE expira_em > ?
        ORDER BY publicado DESC
    """, (agora,))

    return cursor.fetchall()


def limpar_expiradas(cursor, conn):
    """Remove do banco as manchetes que já expiraram."""
    agora = datetime.now().isoformat()
    cursor.execute("DELETE FROM manchetes WHERE expira_em <= ?", (agora,))
    removidas = cursor.rowcount
    conn.commit()
    if removidas:
        print(f"🗑️  {removidas} manchetes expiradas removidas.")


# ─────────────────────────────────────────
# EXECUÇÃO PRINCIPAL
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("       FinanceAI — Coletor de Manchetes")
    print("=" * 55)

    conn, cursor = conectar_banco()

    # 1. Remove manchetes velhas antes de coletar
    limpar_expiradas(cursor, conn)

    # 2. Coleta manchetes novas dos feeds
    coletar_manchetes(cursor, conn)

    # 3. Exibe o que está válido no banco agora
    manchetes = buscar_manchetes_validas(cursor)

    print(f"\n{'=' * 55}")
    print(f"📰 {len(manchetes)} manchetes válidas no banco agora:")
    print(f"{'=' * 55}")

    for i, (titulo, fonte, publicado, link) in enumerate(manchetes, 1):
        print(f"\n[{i}] {titulo}")
        print(f"    Fonte: {fonte} | {publicado}")
        print(f"    Link:  {link}")

    conn.close()
    print(f"\n{'=' * 55}")
    print("✔  Coleta finalizada.")
