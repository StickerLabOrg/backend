import random
import requests
from typing import List

from sqlalchemy.orm import Session

from src.config import settings
from src.colecao.models import Colecao, Pacote, Figurinha, RaridadeEnum


# -----------------------------
# Times da Série A 2025 (fallback)
# -----------------------------
TIMES_SERIE_A_2025: List[str] = [
    "Flamengo",
    "Palmeiras",
    "São Paulo",
    "Corinthians",
    "Santos",
    "Botafogo",
    "Fluminense",
    "Vasco da Gama",
    "Grêmio",
    "Internacional",
    "Athletico-PR",
    "Atlético-MG",
    "Cruzeiro",
    "Bahia",
    "Fortaleza",
    "Vitória",
    "Cuiabá",
    "RB Bragantino",
    "Juventude",
    "Criciúma",
]


def fetch_times_thesportsdb() -> List[dict]:
    """
    Tenta buscar times reais da TheSportsDB (liga 4351).
    Se falhar, retorna lista vazia (cai no fallback).
    """
    api_key = settings.THESPORTSDB_API_KEY
    url = f"https://www.thesportsdb.com/api/v1/json/{api_key}/lookup_all_teams.php?id=4351"

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("teams") or []
    except Exception:
        return []


def seed_colecao(db: Session):
    # ===========================================================
    # 1) Criar coleção se não existir
    # ===========================================================
    colecao = db.query(Colecao).filter(Colecao.nome == "Brasileirão 2025").first()

    if not colecao:
        colecao = Colecao(
            nome="Brasileirão 2025",
            descricao="Álbum do Brasileirão 2025 com 685 figurinhas (160 especiais).",
            ano=2025,
            total_figurinhas=685,
            ativa=True,
        )
        db.add(colecao)
        db.commit()
        db.refresh(colecao)

    # ===========================================================
    # 2) Criar pacotes (igual UI: Bronze, Prata, Ouro, Meu Time)
    # ===========================================================
    if db.query(Pacote).count() == 0:
        pacotes = [
            Pacote(
                nome="Bronze",
                preco_moedas=100,
                quantidade_figurinhas=5,
                chances_raridade={
                    "comum": 0.90,
                    "rara": 0.08,
                    "epica": 0.015,
                    "lendaria": 0.005,
                },
            ),
            Pacote(
                nome="Prata",
                preco_moedas=250,
                quantidade_figurinhas=7,
                chances_raridade={
                    "comum": 0.75,
                    "rara": 0.18,
                    "epica": 0.06,
                    "lendaria": 0.01,
                },
            ),
            Pacote(
                nome="Ouro",
                preco_moedas=500,
                quantidade_figurinhas=10,
                chances_raridade={
                    "comum": 0.60,
                    "rara": 0.25,
                    "epica": 0.10,
                    "lendaria": 0.05,
                },
            ),
            Pacote(
                nome="Pacote do Meu Time",
                preco_moedas=200,
                quantidade_figurinhas=4,
                chances_raridade={
                    "comum": 0.75,
                    "rara": 0.20,
                    "epica": 0.04,
                    "lendaria": 0.01,
                },
            ),
        ]
        db.add_all(pacotes)
        db.commit()

    # ===========================================================
    # 3) Criar figurinhas (685 total)
    #    – 25 globais especiais (capa, taça, etc.)
    #    – 20 times × 33 figurinhas = 660 (escudo, mascote, etc.)
    # ===========================================================
    if db.query(Figurinha).count() > 0:
        return "Figurinhas já existem, seed ignorado."

    # 3.1 – tentar pegar times reais da TheSportsDB
    teams_api = fetch_times_thesportsdb()
    badge_by_name = {}  # mapa nome -> escudo

    if teams_api:
        for t in teams_api:
            name = t.get("strTeam")
            badge = t.get("strTeamBadge") or t.get("strTeamLogo")
            if name:
                badge_by_name[name.lower()] = badge

    # função auxiliar pra pegar escudo (ou None)
    def get_badge(time: str):
        return badge_by_name.get(time.lower())

    numero = 1

    # ------------------------
    # 3.1 – Figurinhas globais (25 primeiras)
    # ------------------------
    globais = [
        ("Capa do Álbum", RaridadeEnum.lendaria),
        ("Taça do Brasileirão", RaridadeEnum.lendaria),
        ("Logo Oficial da Série A", RaridadeEnum.epica),
        ("Bola Oficial 2025", RaridadeEnum.epica),
        ("Mapa dos Clubes", RaridadeEnum.epica),
    ]

    # completa até 25 com recordes / lendas
    while len(globais) < 25:
        idx = len(globais) + 1
        globais.append((f"Lendas do Brasileirão #{idx}", RaridadeEnum.epica))

    for nome_fig, raridade in globais:
        fig = Figurinha(
            colecao_id=colecao.id,
            numero=numero,
            nome=nome_fig,
            raridade=raridade,
            time=None,
            posicao=None,
            imagem_url=None,
        )
        db.add(fig)
        numero += 1

    # ------------------------
    # 3.2 – Figurinhas por time (33 por clube)
    #    Total: 33 × 20 = 660  →  25 + 660 = 685
    # ------------------------
    for time in TIMES_SERIE_A_2025:
        escudo_url = get_badge(time)

        # 1) Escudo
        fig_escudo = Figurinha(
            colecao_id=colecao.id,
            numero=numero,
            nome=f"{time} - Escudo",
            raridade=RaridadeEnum.rara,
            time=time,
            posicao=None,
            imagem_url=escudo_url,
        )
        db.add(fig_escudo)
        numero += 1

        # 2) Mascote
        fig_mascote = Figurinha(
            colecao_id=colecao.id,
            numero=numero,
            nome=f"{time} - Mascote",
            raridade=RaridadeEnum.rara,
            time=time,
            posicao=None,
            imagem_url=None,
        )
        db.add(fig_mascote)
        numero += 1

        # 3) Uniforme titular
        fig_uniforme1 = Figurinha(
            colecao_id=colecao.id,
            numero=numero,
            nome=f"{time} - Uniforme Titular",
            raridade=RaridadeEnum.rara,
            time=time,
            posicao=None,
            imagem_url=None,
        )
        db.add(fig_uniforme1)
        numero += 1

        # 4) Uniforme reserva
        fig_uniforme2 = Figurinha(
            colecao_id=colecao.id,
            numero=numero,
            nome=f"{time} - Uniforme Reserva",
            raridade=RaridadeEnum.rara,
            time=time,
            posicao=None,
            imagem_url=None,
        )
        db.add(fig_uniforme2)
        numero += 1

        # 5) Técnico
        fig_tecnico = Figurinha(
            colecao_id=colecao.id,
            numero=numero,
            nome=f"{time} - Técnico",
            raridade=RaridadeEnum.epica,
            time=time,
            posicao="Técnico",
            imagem_url=None,
        )
        db.add(fig_tecnico)
        numero += 1

        # Jogadores: preenche até 33 figurinhas no total por time
        # já temos 5 acima → faltam 28 jogadores
        for j in range(1, 29):
            # alguns jogadores especiais
            if j <= 2:
                raridade = RaridadeEnum.epica
            elif j <= 6:
                raridade = RaridadeEnum.rara
            else:
                raridade = RaridadeEnum.comum

            fig_jog = Figurinha(
                colecao_id=colecao.id,
                numero=numero,
                nome=f"{time} - Jogador {j}",
                raridade=raridade,
                time=time,
                posicao="Jogador",
                imagem_url=None,
            )
            db.add(fig_jog)
            numero += 1

    db.commit()

    return "Seed da coleção Brasileirão 2025 criado com sucesso!"
