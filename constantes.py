import pygame
import math

# ================= INICIALIZAÇÃO DO MOTOR =================
pygame.init()

# Resolução Nativa HD (720p)
LARGURA, ALTURA = 1280, 720

# ================= CORES (NEON CLÁSSICO E FUNDOS ESCUROS) =================
BRANCO = (255, 255, 255)
PRETO = (10, 10, 15)
FUNDO_ESCURO = (15, 18, 25)
FUNDO_PAINEL = (20, 25, 35, 220)
CINZA_MUITO_ESCURO = (25, 25, 30)
CIANO = (0, 255, 255)
VERDE_NEON = (57, 255, 20)
VERDE_LIMA = (180, 255, 50)
VERMELHO_NEON = (255, 49, 49)
VERMELHO_BOSS = (255, 20, 60)
AZUL_NEON = (0, 255, 255)
AZUL_ESCURO = (10, 40, 80)
AMARELO_NEON = (255, 255, 0)
AMARELO_PRINCIPAL = (255, 215, 0)
LARANJA_NEON = (255, 110, 0)
CINZA = (120, 130, 140)
CINZA_METAL = (40, 45, 55)
CINZA_CLARO = (180, 190, 200)
ROXO_NEON = (188, 19, 254)
MAGENTA = (255, 0, 255)
DOURADO = (255, 215, 0)
VERDE_ESCURO = (20, 80, 30)

# ================= FONTES =================
FONTES_SISTEMA = pygame.font.get_fonts()
FONTE_PRINCIPAL = "consolas" if "consolas" in FONTES_SISTEMA else "couriernew" if "couriernew" in FONTES_SISTEMA else "arial"
FONTE_TITULO = "impact" if "impact" in FONTES_SISTEMA else "arial"

fonte_titulo = pygame.font.SysFont(FONTE_TITULO, 75)
fonte_media = pygame.font.SysFont(FONTE_PRINCIPAL, 24, bold=True)
fonte_pequena = pygame.font.SysFont(FONTE_PRINCIPAL, 16, bold=True)
fonte_mini = pygame.font.SysFont(FONTE_PRINCIPAL, 13, bold=True)

# ================= TEMAS =================
TEMAS_MAPAS = {
    "Cyber City": {"fundo": (12, 16, 28), "borda": (20, 40, 80), "caminho": AZUL_NEON, "grid": (25, 45, 90)},
    "Mainframe": {"fundo": (10, 25, 15), "borda": (20, 80, 30), "caminho": VERDE_NEON, "grid": (30, 90, 40)},
    "Overclock": {"fundo": (30, 10, 10), "borda": (90, 20, 20), "caminho": VERMELHO_NEON, "grid": (110, 30, 30)},
    "Deep Web": {"fundo": (20, 10, 30), "borda": (80, 20, 110), "caminho": ROXO_NEON, "grid": (100, 30, 140)},
    "Quantum Grid": {"fundo": (15, 15, 15), "borda": (50, 50, 50), "caminho": BRANCO, "grid": (70, 70, 80)},
    "Circuito Solar": {"fundo": (25, 20, 5), "borda": (100, 80, 10), "caminho": AMARELO_NEON, "grid": (60, 50, 15)}
}

MAPAS_CHAVE = {
    "Cyber City": [(-50, 360), (256, 360), (256, 120), (640, 120), (640, 540), (1024, 540), (1024, 300), (1350, 300)],
    "Mainframe": [(-50, 180), (320, 180), (448, 540), (832, 540), (960, 180), (1350, 180)],
    "Overclock": [(-50, 600), (1088, 600), (1088, 120), (192, 120), (192, 420), (768, 420), (768, 770)],
    "Deep Web": [(640, -50), (640, 240), (256, 420), (1024, 540), (640, 770)],
    "Quantum Grid": [(-50, 360), (192, 120), (512, 600), (768, 120), (1088, 600), (1350, 360)],
    "Circuito Solar": [(-50, 200), (300, 200), (300, 600), (700, 600), (700, 150), (1100, 150), (1100, 770)]
}

# ================= OBJETOS DE CIBERSEGURANÇA (HARDWARES DE DEFESA) =================
CATEGORIAS_LOJA = [
    ("HARDWARES BÁSICOS", ["railgun", "chaingun", "morteiro", "sniper"]),
    ("FIREWALLS ELEMENTAIS", ["emissor_solar", "prisma_estase", "injetor_viral", "bobina_neural"]),
    ("UTILITÁRIOS E AURA", ["minerador_cripto", "overclock", "radar_quantico", "parede_holo"]),
    ("SOFTWARES AVANÇADOS", ["splash_plasma", "feixe_laser", "nuvem_nanobot", "teleguiado", "ataque_orbital", "dreno_dados"])
]

# Chaves renomeadas para refletir as torres apresentadas no projeto
ATRIBUTOS_TORRE = {
    "railgun": {
        "custo": 50, "dano_base": 15, "rate_base": 30, "range_base": 140, "cor": AZUL_NEON, "nome": "Railgun Básico",
        "p1": [{"nome": "Íman Duplo", "custo": 40, "dano": 10, "rate": 0, "range": 0},
               {"nome": "Cano Duplo", "custo": 120, "dano": 5, "rate": -5, "range": 0},
               {"nome": "Desintegrador", "custo": 350, "dano": 35, "rate": 0, "range": 20}],
        "p2": [{"nome": "Sensor Lótico", "custo": 30, "dano": 0, "rate": 0, "range": 40},
               {"nome": "Radar Orbital", "custo": 80, "dano": 0, "rate": 0, "range": 50},
               {"nome": "Laser Perfurante", "custo": 250, "dano": 20, "rate": -5, "range": 20}]
    },
    "chaingun": {
        "custo": 90, "dano_base": 4, "rate_base": 8, "range_base": 130, "cor": AMARELO_NEON, "nome": "Chaingun Laser",
        "p1": [{"nome": "Fótons", "custo": 60, "dano": 3, "rate": 0, "range": 0},
               {"nome": "Feixe Quente", "custo": 150, "dano": 5, "rate": 0, "range": 0},
               {"nome": "Gatling Plasma", "custo": 400, "dano": 15, "rate": -2, "range": 0}],
        "p2": [{"nome": "Rotor Ágil", "custo": 70, "dano": 0, "rate": -2, "range": 0},
               {"nome": "Foco Longo", "custo": 120, "dano": 0, "rate": 0, "range": 40},
               {"nome": "Hyper-Burst", "custo": 450, "dano": 2, "rate": -3, "range": 30}]
    },
    "morteiro": {
        "custo": 180, "dano_base": 45, "rate_base": 55, "range_base": 190, "cor": ROXO_NEON, "nome": "Morteiro Quântico",
        "p1": [{"nome": "Massa Extra", "custo": 120, "dano": 35, "rate": 0, "range": 0},
               {"nome": "Anti-Matéria", "custo": 350, "dano": 100, "rate": 0, "range": 0},
               {"nome": "Buraco Negro", "custo": 900, "dano": 250, "rate": 15, "range": 50}], 
        "p2": [{"nome": "Mira Laser", "custo": 100, "dano": 0, "rate": 0, "range": 50},
               {"nome": "Auto-Loader", "custo": 250, "dano": 0, "rate": -20, "range": 0},
               {"nome": "Artilharia", "custo": 700, "dano": 50, "rate": -15, "range": 40}]
    },
    "sniper": {
        "custo": 320, "dano_base": 120, "rate_base": 90, "range_base": 500, "cor": CINZA_CLARO, "nome": "Ion Sniper",
        "p1": [{"nome": "Iões Densos", "custo": 200, "dano": 100, "rate": 0, "range": 0},
               {"nome": "Perfurante", "custo": 500, "dano": 150, "rate": 0, "range": 0},
               {"nome": "Raio da Morte", "custo": 1600, "dano": 600, "rate": 30, "range": 0}],
        "p2": [{"nome": "Processador", "custo": 250, "dano": 0, "rate": -25, "range": 0},
               {"nome": "Semi-Auto", "custo": 600, "dano": -30, "rate": -35, "range": 0},
               {"nome": "Sentinela", "custo": 2100, "dano": 50, "rate": -15, "range": 0}]
    },
    "emissor_solar": {
        "custo": 130, "dano_base": 4, "rate_base": 4, "range_base": 125, "cor": LARANJA_NEON, "nome": "Emissor Solar",
        "p1": [{"nome": "Núcleo Quente", "custo": 100, "dano": 4, "rate": 0, "range": 0},
               {"nome": "Plasma Instável", "custo": 250, "dano": 8, "rate": 0, "range": 0},
               {"nome": "Supernova", "custo": 600, "dano": 20, "rate": 0, "range": 20}], 
        "p2": [{"nome": "Lente Ampla", "custo": 80, "dano": 0, "rate": 0, "range": 30},
               {"nome": "Onda Contínua", "custo": 200, "dano": 0, "rate": -2, "range": 20},
               {"nome": "Erupção", "custo": 500, "dano": 10, "rate": -1, "range": 40}]
    },
    "prisma_estase": {
        "custo": 200, "dano_base": 8, "rate_base": 40, "range_base": 170, "cor": BRANCO, "nome": "Prisma Estase",
        "p1": [{"nome": "Zero Absoluto", "custo": 120, "dano": 15, "rate": 0, "range": 0},
               {"nome": "Cristais", "custo": 250, "dano": 30, "rate": -5, "range": 0},
               {"nome": "Sub-Zero", "custo": 750, "dano": 60, "rate": -10, "range": 20}],
        "p2": [{"nome": "Onda Gélida", "custo": 150, "dano": 0, "rate": 0, "range": 40},
               {"nome": "Ressonância", "custo": 300, "dano": 0, "rate": -10, "range": 40},
               {"nome": "Era Glacial", "custo": 800, "dano": 10, "rate": -15, "range": 70}]
    },
    "injetor_viral": {
        "custo": 180, "dano_base": 10, "rate_base": 45, "range_base": 160, "cor": VERDE_NEON, "nome": "Injetor Viral",
        "p1": [{"nome": "Malware", "custo": 140, "dano": 8, "rate": 0, "range": 0},
               {"nome": "Corrupção", "custo": 300, "dano": 20, "rate": 0, "range": 0},
               {"nome": "Trojan Fatal", "custo": 850, "dano": 70, "rate": -5, "range": 20}],
        "p2": [{"nome": "Antena Larga", "custo": 120, "dano": 0, "rate": 0, "range": 30},
               {"nome": "Ping Rápido", "custo": 280, "dano": 0, "rate": -10, "range": 30},
               {"nome": "Pandemia", "custo": 700, "dano": 10, "rate": -15, "range": 50}]
    },
    "bobina_neural": {
        "custo": 250, "dano_base": 20, "rate_base": 50, "range_base": 145, "cor": MAGENTA, "nome": "Bobina Neural",
        "p1": [{"nome": "Voltagem Extra", "custo": 180, "dano": 15, "rate": 0, "range": 0},
               {"nome": "Arco Voltaico", "custo": 400, "dano": 40, "rate": 0, "range": 0},
               {"nome": "Tempestade", "custo": 1200, "dano": 100, "rate": -10, "range": 30}],
        "p2": [{"nome": "Super Condutor", "custo": 160, "dano": 0, "rate": 0, "range": 40},
               {"nome": "Frequência", "custo": 350, "dano": 0, "rate": -15, "range": 20},
               {"nome": "Pulso EMP", "custo": 900, "dano": 20, "rate": -15, "range": 60}]
    },
    "minerador_cripto": {
        "custo": 350, "dano_base": 15, "rate_base": 180, "range_base": 0, "cor": DOURADO, "nome": "Minerador Cripto",
        "p1": [{"nome": "Algoritmo", "custo": 250, "dano": 10, "rate": 0, "range": 0},
               {"nome": "Blockchain", "custo": 600, "dano": 25, "rate": 0, "range": 0},
               {"nome": "Monopólio", "custo": 1800, "dano": 80, "rate": 0, "range": 0}],
        "p2": [{"nome": "CPU Rápido", "custo": 200, "dano": 0, "rate": -20, "range": 0},
               {"nome": "Quantum", "custo": 500, "dano": 0, "rate": -30, "range": 0},
               {"nome": "Farm Gigante", "custo": 1500, "dano": 0, "rate": -40, "range": 0}]
    },
    "overclock": {
        "custo": 200, "dano_base": 0, "rate_base": 0, "range_base": 100, "cor": CIANO, "nome": "Torre Overclock",
        "p1": [{"nome": "Cabos Novos", "custo": 150, "dano": 1, "rate": 0, "range": 0},
               {"nome": "Nitrogénio", "custo": 400, "dano": 2, "rate": 0, "range": 0},
               {"nome": "Mod Deus", "custo": 1200, "dano": 4, "rate": 0, "range": 0}],
        "p2": [{"nome": "Bluetooth", "custo": 100, "dano": 0, "rate": 0, "range": 30},
               {"nome": "Wi-Fi 6", "custo": 300, "dano": 0, "rate": 0, "range": 40},
               {"nome": "Rede Global", "custo": 900, "dano": 0, "rate": 0, "range": 60}]
    },
    "radar_quantico": {
        "custo": 180, "dano_base": 0, "rate_base": 0, "range_base": 120, "cor": AZUL_ESCURO, "nome": "Sensor Quântico",
        "p1": [{"nome": "Lente Larga", "custo": 120, "dano": 1, "rate": 0, "range": 0},
               {"nome": "Satélite", "custo": 350, "dano": 2, "rate": 0, "range": 0},
               {"nome": "Omnisciência", "custo": 1000, "dano": 4, "rate": 0, "range": 0}],
        "p2": [{"nome": "Onda Longa", "custo": 100, "dano": 0, "rate": 0, "range": 40},
               {"nome": "Frequência", "custo": 250, "dano": 0, "rate": 0, "range": 50},
               {"nome": "Eco Global", "custo": 800, "dano": 0, "rate": 0, "range": 80}]
    },
    "parede_holo": {
        "custo": 250, "dano_base": 0, "rate_base": 0, "range_base": 90, "cor": (0, 150, 255), "nome": "Parede Holográfica",
        "p1": [{"nome": "Lag Visível", "custo": 180, "dano": 1, "rate": 0, "range": 0},
               {"nome": "Travar PC", "custo": 400, "dano": 2, "rate": 0, "range": 0},
               {"nome": "Tela Azul", "custo": 1100, "dano": 5, "rate": 0, "range": 0}],
        "p2": [{"nome": "Projetor", "custo": 150, "dano": 0, "rate": 0, "range": 30},
               {"nome": "Área Larga", "custo": 350, "dano": 0, "rate": 0, "range": 40},
               {"nome": "Labirinto", "custo": 950, "dano": 0, "rate": 0, "range": 60}]
    },
    "splash_plasma": {
        "custo": 350, "dano_base": 30, "rate_base": 70, "range_base": 140, "cor": (255, 80, 0), "nome": "Morteiro Splash",
        "p1": [{"nome": "Carga Extra", "custo": 250, "dano": 20, "rate": 0, "range": 0},
               {"nome": "Estrela Anã", "custo": 600, "dano": 60, "rate": 0, "range": 0},
               {"nome": "Big Bang", "custo": 1800, "dano": 150, "rate": 0, "range": 0}],
        "p2": [{"nome": "Raio Ação", "custo": 200, "dano": 0, "rate": 0, "range": 20},
               {"nome": "Impacto", "custo": 500, "dano": 0, "rate": 0, "range": 30},
               {"nome": "Devastação", "custo": 1400, "dano": 0, "rate": -15, "range": 50}]
    },
    "feixe_laser": {
        "custo": 250, "dano_base": 1.5, "rate_base": 2, "range_base": 150, "cor": VERMELHO_NEON, "nome": "Feixe Derretedor",
        "p1": [{"nome": "Foco Fino", "custo": 180, "dano": 1, "rate": 0, "range": 0},
               {"nome": "Maçarico", "custo": 450, "dano": 3, "rate": 0, "range": 0},
               {"nome": "Sabre de Luz", "custo": 1300, "dano": 10, "rate": 0, "range": 0}],
        "p2": [{"nome": "Lente Limpa", "custo": 150, "dano": 0, "rate": 0, "range": 30},
               {"nome": "Fibra Ótica", "custo": 350, "dano": 0, "rate": 0, "range": 40},
               {"nome": "Longo Alcance", "custo": 1000, "dano": 0, "rate": 0, "range": 70}]
    },
    "nuvem_nanobot": {
        "custo": 320, "dano_base": 4, "rate_base": 12, "range_base": 120, "cor": VERDE_ESCURO, "nome": "Nuvem Nanobot",
        "p1": [{"nome": "Dentes Afiados", "custo": 200, "dano": 2, "rate": 0, "range": 0},
               {"nome": "Enxame", "custo": 450, "dano": 5, "rate": 0, "range": 0},
               {"nome": "Praga Cinza", "custo": 1500, "dano": 20, "rate": 0, "range": 0}],
        "p2": [{"nome": "Mais Nanos", "custo": 180, "dano": 0, "rate": 0, "range": 20},
               {"nome": "Vento Tóxico", "custo": 400, "dano": 0, "rate": 0, "range": 30},
               {"nome": "Atmosfera", "custo": 1200, "dano": 0, "rate": 0, "range": 60}]
    },
    "teleguiado": {
        "custo": 480, "dano_base": 80, "rate_base": 100, "range_base": 250, "cor": CINZA, "nome": "Teleguiado V2",
        "p1": [{"nome": "Ogiva Maior", "custo": 300, "dano": 50, "rate": 0, "range": 0},
               {"nome": "Uranio", "custo": 800, "dano": 120, "rate": 0, "range": 0},
               {"nome": "Juízo Final", "custo": 2200, "dano": 300, "rate": 0, "range": 0}],
        "p2": [{"nome": "Recarga", "custo": 250, "dano": 0, "rate": -20, "range": 0},
               {"nome": "Auto-Fábrica", "custo": 600, "dano": 0, "rate": -30, "range": 0},
               {"nome": "Chuva Mísseis", "custo": 1800, "dano": 0, "rate": -35, "range": 0}]
    },
    "ataque_orbital": {
        "custo": 1500, "dano_base": 600, "rate_base": 300, "range_base": 2000, "cor": (150, 0, 255), "nome": "Ataque Orbital",
        "p1": [{"nome": "Bateria Larga", "custo": 800, "dano": 300, "rate": 0, "range": 0},
               {"nome": "Foco Sol", "custo": 1800, "dano": 800, "rate": 0, "range": 0},
               {"nome": "Ira de Deus", "custo": 4000, "dano": 1500, "rate": 0, "range": 0}],
        "p2": [{"nome": "Órbita Baixa", "custo": 600, "dano": 0, "rate": -40, "range": 0},
               {"nome": "Dois Satélites", "custo": 1500, "dano": 0, "rate": -60, "range": 0},
               {"nome": "Constelação", "custo": 3500, "dano": 0, "rate": -100, "range": 0}]
    },
    "dreno_dados": {
        "custo": 550, "dano_base": 12, "rate_base": 50, "range_base": 130, "cor": (255, 20, 147), "nome": "Dreno de Dados",
        "p1": [{"nome": "Cabo Grosso", "custo": 400, "dano": 8, "rate": 0, "range": 0},
               {"nome": "Sanguessuga", "custo": 900, "dano": 20, "rate": 0, "range": 0},
               {"nome": "Imortalidade", "custo": 2500, "dano": 50, "rate": 0, "range": 0}],
        "p2": [{"nome": "Sede Sangue", "custo": 350, "dano": 0, "rate": -10, "range": 0},
               {"nome": "Frenesi", "custo": 800, "dano": 0, "rate": -15, "range": 0},
               {"nome": "Dreno Global", "custo": 2200, "dano": 0, "rate": -15, "range": 60}]
    }
}

# Aplicando upgrades automáticos (Path 3 oculto) e otimizando base_rate
for k, v in ATRIBUTOS_TORRE.items():
    base_dano, base_custo, base_rate, base_range = max(1, v["dano_base"]), v["custo"], v["rate_base"], v["range_base"]

    for path in ["p1", "p2"]:
        for upg in v[path]:
            upg.setdefault("camo", False)
            upg.setdefault("ap", False)

    v["p1"].append({"nome": "Modo Sobrecarga", "custo": int(base_custo * 4), "dano": int(base_dano * 2.5), "rate": 0, "range": 0, "camo": False, "ap": False})
    v["p1"].append({"nome": "Aniquilador Apex", "custo": int(base_custo * 10), "dano": int(base_dano * 6), "rate": 0, "range": int(base_range * 0.1), "camo": False, "ap": False})

    v["p2"].append({"nome": "Servomotores", "custo": int(base_custo * 3.5), "dano": int(base_dano * 0.3), "rate": -max(1, int(base_rate * 0.25)), "range": int(base_range * 0.2), "camo": False, "ap": False})
    v["p2"].append({"nome": "Feixe Quântico", "custo": int(base_custo * 8), "dano": int(base_dano * 0.8), "rate": -max(2, int(base_rate * 0.40)), "range": int(base_range * 0.4), "camo": False, "ap": False})

    v["p3"] = [
        {"nome": "Sensores Rápidos", "custo": int(base_custo * 0.8), "dano": 0, "rate": -max(1, int(base_rate * 0.10)), "range": 0, "camo": False, "ap": False},
        {"nome": "Scanner Thermal", "custo": int(base_custo * 1.5), "dano": 0, "rate": -max(1, int(base_rate * 0.10)), "range": 0, "camo": True, "ap": False},
        {"nome": "Tiros Perfurantes", "custo": int(base_custo * 3), "dano": int(base_dano * 0.3), "rate": -max(1, int(base_rate * 0.15)), "range": 0, "camo": True, "ap": True},
        {"nome": "Gatilho Acelerado", "custo": int(base_custo * 6), "dano": int(base_dano * 0.8), "rate": -max(2, int(base_rate * 0.20)), "range": 0, "camo": True, "ap": True},
        {"nome": "Frenesi Tático", "custo": int(base_custo * 12), "dano": int(base_dano * 2.0), "rate": -max(3, int(base_rate * 0.30)), "range": 0, "camo": True, "ap": True}
    ]

ATRIBUTOS_TORRE["minerador_cripto"]["p2"][3]["dano"] = 0
ATRIBUTOS_TORRE["minerador_cripto"]["p2"][3]["rate"] = -30
ATRIBUTOS_TORRE["minerador_cripto"]["p2"][4]["dano"] = 0
ATRIBUTOS_TORRE["minerador_cripto"]["p2"][4]["rate"] = -40
ATRIBUTOS_TORRE["minerador_cripto"]["p3"][2]["dano"] = 0
ATRIBUTOS_TORRE["minerador_cripto"]["p3"][3]["dano"] = 0
ATRIBUTOS_TORRE["minerador_cripto"]["p3"][4]["dano"] = 0

DESCRICOES_TORRES = {
    "railgun": "Disparo cinético básico e equilibrado.",
    "chaingun": "Dispara lasers em alta velocidade.",
    "morteiro": "Tiros lentos que causam grande dano.\nIgnora parcialmente blindagem.",
    "sniper": "Alcance extremo e dano massivo.\nIgnora totalmente blindagem.",
    "emissor_solar": "Projéteis que superaquecem o malware.",
    "prisma_estase": "Projéteis congelantes que causam lentidão.",
    "injetor_viral": "Injeta script causando dano contínuo.",
    "bobina_neural": "Raios EMP que atordoam ameaças.",
    "minerador_cripto": "Gera Créditos (CR) periodicamente.",
    "overclock": "Aumenta a velocidade de torres próximas.",
    "radar_quantico": "Aumenta o alcance.\nDá deteção de camuflados.",
    "parede_holo": "Atrasa malwares em sua área de efeito.",
    "splash_plasma": "Tiros explosivos com dano em área.\nPerfurante contra blindados.",
    "feixe_laser": "Feixe contínuo letal a curtas distâncias.",
    "nuvem_nanobot": "Dispara nuvem persistente antivírus.",
    "teleguiado": "Mísseis lentos mas devastadores.\nPerfurante contra blindados.",
    "ataque_orbital": "Chama um laser orbital aniquilador.\nDestrói blindagem instantaneamente.",
    "dreno_dados": "Drena energia vital para o sistema (Cura)."
}