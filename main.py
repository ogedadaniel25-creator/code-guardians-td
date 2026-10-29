import pygame
import sys
import random
from pathlib import Path

# PRIMEIRO: Importa tudo dos outros arquivos (incluindo as constantes)
from constantes import *
from interface import *
from entidades import *

# Renderização em resolução lógica 1280x720, saída nativa Full HD.
# Preserva todas as coordenadas originais e evita quebrar a interface.
RESOLUCAO_SAIDA = (1920, 1080)
is_fullscreen = False
janela = pygame.display.set_mode(RESOLUCAO_SAIDA, pygame.RESIZABLE)
tela = pygame.Surface((LARGURA, ALTURA)).convert_alpha()
pygame.display.set_caption("Code Guardians TD | Full HD Edition")
relogio = pygame.time.Clock()

def posicao_mouse():
    mx, my = pygame.mouse.get_pos()
    w, h = janela.get_size()
    escala = min(w / LARGURA, h / ALTURA)
    ox = (w - LARGURA * escala) / 2
    oy = (h - ALTURA * escala) / 2
    return (int((mx - ox) / escala), int((my - oy) / escala))

def apresentar():
    w, h = janela.get_size()
    escala = min(w / LARGURA, h / ALTURA)
    sw, sh = max(1, int(LARGURA * escala)), max(1, int(ALTURA * escala))
    janela.fill((5, 8, 15))
    frame = pygame.transform.smoothscale(tela, (sw, sh))
    janela.blit(frame, ((w - sw) // 2, (h - sh) // 2))
    pygame.display.flip()

def alternar_tela_cheia():
    global is_fullscreen, janela
    is_fullscreen = not is_fullscreen
    flags = pygame.FULLSCREEN if is_fullscreen else pygame.RESIZABLE
    janela = pygame.display.set_mode(RESOLUCAO_SAIDA, flags)

class Game:
    def __init__(self):
        self.estado = "MENU"
        self.lista_mapas = list(MAPAS_CHAVE.keys())
        self.tema_atual = TEMAS_MAPAS["Cyber City"]
        self.caminho_atual = gerar_caminho_suave(MAPAS_CHAVE["Cyber City"])

        self.anim_alpha = 255
        self.hardwares, self.malwares, self.pacotes = [], [], []
        self.particulas, self.textos_flutuantes = [], []

        self.dinheiro, self.vida, self.vida_max, self.fase = 800, 100, 100, 1
        self.fase_maxima = 30

        self.hardware_selecionado, self.hardware_foco = None, None
        self.mapa_temp = None
        self.mult_dificuldade = 1.0
        self.modo_infinito_ativado = False
        self.dificuldade_atual = "medio"
        self.auto_play = True
        self.esperando_proxima_onda = False

        self.bg_nodes = [(random.randint(0, LARGURA), random.randint(0, ALTURA), random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5)) for _ in range(60)]

        self.loja_aberta = True
        self.loja_x_offset = 0.0
        self.scroll_y, self.max_scroll = 0, 0
        self.tooltip_text, self.tooltip_alpha, self.target_tooltip_alpha = "", 0, 0

        self.emp_cooldown = 0
        self.emp_flash = 0
        self.show_help = False
        self.gerar_botoes()
        self.gerar_mapa_texturizado()

    def gerar_botoes(self):
        cx, cy = LARGURA // 2, ALTURA // 2
        self.b_jogar = Botao((cx - 140, cy - 60, 280, 50), "INICIAR SISTEMA", "ir_mapas", AMARELO_NEON, fonte_media)
        self.b_sair = Botao((cx - 140, cy + 30, 280, 50), "DESCONECTAR", "sair", VERMELHO_NEON, fonte_media)
        self.b_fullscreen_menu = Botao((15, 15, 200, 40), f"TELA CHEIA: OFF", "toggle_fullscreen", AMARELO_NEON, fonte=fonte_pequena)

        self.botoes_mapas = []
        for i, mapa in enumerate(self.lista_mapas):
            x, y = 240 + (i % 3) * 280, 150 + (i // 3) * 200
            self.botoes_mapas.append(Botao((x, y, 220, 150), mapa, f"mapa_{mapa}", AMARELO_NEON, fonte=fonte_pequena, valign="bottom"))
        self.b_voltar_menu = Botao((cx - 100, ALTURA - 80, 200, 50), "MENU PRINCIPAL", "menu", VERMELHO_NEON, fonte=fonte_media)

        # GRADE 3x2 DE SELEÇÃO DE DIFICULDADE E MODOS
        self.b_dif_facil = Botao((cx - 360, cy - 150, 220, 130), "PROTOCOLO: FÁCIL\n(200 Vida)", "facil", VERDE_NEON, fonte=fonte_pequena)
        self.b_dif_medio = Botao((cx - 110, cy - 150, 220, 130), "PROTOCOLO: NORMAL\n(100 Vida)", "medio", AMARELO_NEON, fonte=fonte_pequena)
        self.b_dif_dificil = Botao((cx + 140, cy - 150, 220, 130), "PROTOCOLO: DIFÍCIL\n(50 Vida)", "dificil", LARANJA_NEON, fonte=fonte_pequena)
        
        self.b_dif_perfeita = Botao((cx - 360, cy + 10, 220, 130), "DEFESA PERFEITA\n(1 Vida)", "perfeita", VERMELHO_NEON, fonte=fonte_pequena)
        self.b_dif_desafio = Botao((cx - 110, cy + 10, 220, 130), "MODO DESAFIO\n(1 Vida | Sem Renda)", "desafio", ROXO_NEON, fonte=fonte_pequena)
        self.b_dif_raid = Botao((cx + 140, cy + 10, 220, 130), "MODO RAID\n(Boss a cada 10 ondas)", "raid", VERMELHO_BOSS, fonte=fonte_pequena)
        
        self.b_continuar = Botao((cx - 180, cy, 360, 60), "CONTINUAR", "continuar", AMARELO_NEON, fonte=fonte_media)

        self.botoes_compra = []
        self.headers_loja = []
        cursor_y = 110

        for cat_nome, hardwares in CATEGORIAS_LOJA:
            self.headers_loja.append((cat_nome, cursor_y))
            cursor_y += 30
            for i, k in enumerate(hardwares):
                v = ATRIBUTOS_TORRE[k]
                col = i % 2
                x = LARGURA - 235 + col * 115
                linhas_nome = v['nome'].split(" ")
                nome_fmt = "\n".join(linhas_nome)
                texto = f"{nome_fmt}\n \n \n{v['custo']} CR"
                btn = Botao((x, cursor_y, 105, 135), texto, k, v['cor'], fonte=fonte_mini)
                self.botoes_compra.append(btn)
                if col == 1 or i == len(hardwares) - 1: cursor_y += 145
            cursor_y += 15

        self.max_scroll = max(0, cursor_y - ALTURA + 20)
        self.scroll_y = 0

        # Ajuste nas posições e larguras dos botões para liberar espaço para o texto à esquerda
        self.b_up1 = Botao((250, ALTURA - 130, 200, 110), "", "up1", AMARELO_NEON, fonte=fonte_pequena)
        self.b_up2 = Botao((460, ALTURA - 130, 200, 110), "", "up2", AMARELO_NEON, fonte=fonte_pequena)
        self.b_up3 = Botao((670, ALTURA - 130, 200, 110), "", "up3", AMARELO_NEON, fonte=fonte_pequena)
        self.b_vender = Botao((880, ALTURA - 105, 130, 60), "", "vender", VERMELHO_NEON, fonte=fonte_pequena)

        self.b_pausa = Botao((LARGURA - 230, 15, 100, 45), "PAUSAR", "pausa", AMARELO_NEON, fonte=fonte_pequena)
        self.b_velocidade = Botao((LARGURA - 120, 15, 100, 45), "> INICIAR", "velocidade", AMARELO_PRINCIPAL, fonte=fonte_pequena)
        self.b_toggle_loja = Botao((LARGURA - 250 - 32, ALTURA // 2 - 30, 32, 60), ">", "toggle_loja", AMARELO_NEON, fonte=fonte_pequena)
        self.b_retomar = Botao((cx - 150, cy - 80, 300, 60), "RETOMAR", "retomar", AMARELO_NEON, fonte_media)
        self.b_autoplay = Botao((cx - 150, cy, 300, 60), "AUTO-START: ON", "toggle_autoplay", AMARELO_NEON, fonte_media)

    def gerar_mapa_texturizado(self):
        self.fundo = pygame.Surface((LARGURA, ALTURA))
        self.fundo.fill(self.tema_atual["fundo"])
        # Microtexturas determinísticas: circuitos e placas sem assets externos.
        rng = random.Random(self.lista_mapas.index(next((n for n, t in TEMAS_MAPAS.items() if t == self.tema_atual), "Cyber City")) + 417)
        cor_grid = self.tema_atual["grid"]
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for _ in range(115):
            x = rng.randrange(10, LARGURA - 10, 20)
            y = rng.randrange(10, ALTURA - 10, 20)
            largura = rng.choice((20, 40, 60, 100))
            altura = rng.choice((20, 40, 60))
            cor = (*cor_grid[:3], rng.randint(40, 95))
            pygame.draw.line(camada, cor, (x, y), (min(x + largura, LARGURA), y), 2)
            pygame.draw.line(camada, cor, (min(x + largura, LARGURA), y), (min(x + largura, LARGURA), min(y + altura, ALTURA)), 2)
            pygame.draw.circle(camada, (*self.tema_atual["caminho"][:3], 65), (x, y), rng.choice((2, 3, 4)))
        self.fundo.blit(camada, (0, 0))
        for x in range(0, LARGURA, 60):
            pygame.draw.line(self.fundo, self.tema_atual["grid"], (x, 0), (x, ALTURA), 1)
            for y in range(0, ALTURA, 60):
                if random.random() > 0.8: pygame.draw.circle(self.fundo, self.tema_atual["grid"], (x, y), 3)
        for y in range(0, ALTURA, 60):
            pygame.draw.line(self.fundo, self.tema_atual["grid"], (0, y), (LARGURA, y), 1)
        pygame.draw.lines(self.fundo, self.tema_atual["borda"], False, self.caminho_atual, 80)
        for pt in self.caminho_atual: pygame.draw.circle(self.fundo, self.tema_atual["borda"], pt, 40)
        cor_neon = (*self.tema_atual["caminho"][:3], 150)
        pygame.draw.lines(self.fundo, cor_neon, False, self.caminho_atual, 50)
        for pt in self.caminho_atual: pygame.draw.circle(self.fundo, cor_neon, pt, 25)
        pygame.draw.lines(self.fundo, BRANCO, False, self.caminho_atual, 10)
        for pt in self.caminho_atual: pygame.draw.circle(self.fundo, BRANCO, pt, 5)
        # Faixa interna pontilhada, sugerindo fluxo de dados.
        for idx, pt in enumerate(self.caminho_atual[::14]):
            if idx % 2 == 0:
                pygame.draw.circle(self.fundo, self.tema_atual["borda"], (int(pt[0]), int(pt[1])), 3)

    def iniciar_partida(self, mapa, dificuldade):
        self.tema_atual = TEMAS_MAPAS[mapa]
        self.caminho_atual = gerar_caminho_suave(MAPAS_CHAVE[mapa])
        self.gerar_mapa_texturizado()
        self.hardwares, self.malwares, self.pacotes = [], [], []
        self.particulas, self.textos_flutuantes = [], []
        self.fase = 1
        self.estado = "JOGANDO"
        self.modo_infinito_ativado = False
        self.esperando_proxima_onda = False
        self.hardware_foco = None
        self.scroll_y, self.loja_x_offset = 0, 0.0
        self.loja_aberta = True
        self.game_speed = 0

        self.b_velocidade.texto = "> INICIAR"
        self.b_velocidade.cor_base = AMARELO_PRINCIPAL
        self.b_autoplay.texto = "AUTO-START: ON" if self.auto_play else "AUTO-START: OFF"
        self.dificuldade_atual = dificuldade

        if dificuldade == "facil": self.dinheiro, self.vida, self.mult_dificuldade, self.fase_maxima = 1200, 200, 0.8, 20
        elif dificuldade == "medio": self.dinheiro, self.vida, self.mult_dificuldade, self.fase_maxima = 1000, 100, 1.0, 25
        elif dificuldade == "dificil": self.dinheiro, self.vida, self.mult_dificuldade, self.fase_maxima = 850, 50, 1.2, 30
        elif dificuldade == "perfeita": self.dinheiro, self.vida, self.mult_dificuldade, self.fase_maxima = 1000, 1, 1.2, 30
        elif dificuldade == "desafio": self.dinheiro, self.vida, self.mult_dificuldade, self.fase_maxima = 4200, 1, 1.8, "∞"
        elif dificuldade == "raid": self.dinheiro, self.vida, self.mult_dificuldade, self.fase_maxima = 1000, 100, 1.0, 100

        self.vida_max = self.vida
        self.gerar_wave()
        self.anim_alpha = 255

    def gerar_wave(self):
        self.inimigos_para_spawnar = []
        
        if self.dificuldade_atual == "desafio":
            horda_bruta = (["trojan_basico"] * 15 + ["worm_rapido"] * 20 + ["adware_enxame"] * 25 + ["ransomware_tanque"] * 12 + ["rootkit_escudo"] * 15 + ["botnet_cura"] * 12 + ["stealth_fantasma"] * 15 + ["spyware_boss"] * 5 + ["ddos_zeppelin"] * 3)
            random.shuffle(horda_bruta)
            self.inimigos_para_spawnar = horda_bruta
            self.timer_spawn = 60
            return

        if self.dificuldade_atual == "raid" and self.fase > 0 and self.fase % 10 == 0:
            self.inimigos_para_spawnar.append("virus_primordial")
            self.inimigos_para_spawnar.extend(["botnet_cura", "ransomware_tanque", "rootkit_escudo", "botnet_cura"])
            self.timer_spawn = 120
            return

        qtd = 10 + int(self.fase * 6)
        for i in range(qtd):
            if self.fase >= 10 and i % 25 == 0: self.inimigos_para_spawnar.append("ddos_zeppelin")
            elif self.fase >= 8 and i % 12 == 0: self.inimigos_para_spawnar.append("stealth_fantasma")
            elif self.fase >= 5 and i % 10 == 0: self.inimigos_para_spawnar.append("botnet_cura")
            elif self.fase > 4 and i % 15 == 0: self.inimigos_para_spawnar.append("spyware_boss")
            elif self.fase > 2 and i % 8 == 0: self.inimigos_para_spawnar.append("rootkit_escudo")
            elif self.fase > 1 and i % 6 == 0: self.inimigos_para_spawnar.extend(["adware_enxame"] * 4)
            elif i % 4 == 0: self.inimigos_para_spawnar.append("worm_rapido" if self.fase % 2 == 0 else "ransomware_tanque")
            else: self.inimigos_para_spawnar.append("trojan_basico")
        self.timer_spawn = 60

    def trigger_boss_skull(self, boss):
        boss.skulls_ativados += 1
        self.textos_flutuantes.append(TextoFlutuante(boss.x, boss.y - 50, "PULSO E.M.P ATIVADO!", VERMELHO_BOSS, fonte_media))
        
        raio_stun = 250 + (boss.boss_tier * 50)
        glow = get_glow_surface(raio_stun, VERMELHO_BOSS, 100)
        self.particulas.append(Particula(boss.x, boss.y, VERMELHO_BOSS, vel_base=10)) 
        for t in self.hardwares:
            if math.hypot(t.x - boss.x, t.y - boss.y) <= raio_stun:
                t.stun_timer = 180 + (boss.boss_tier * 60)

        qtd_enxame = 10 * boss.boss_tier
        for _ in range(qtd_enxame):
            novo = Malware(self.fase, "worm_rapido" if boss.boss_tier > 2 else "adware_enxame", self.caminho_atual, self.mult_dificuldade, recompensa_ativa=False, dificuldade_atual=self.dificuldade_atual)
            novo.x = boss.x + random.randint(-40, 40)
            novo.y = boss.y + random.randint(-40, 40)
            novo.alvo = boss.alvo
            self.malwares.append(novo)

    def ativar_emp(self):
        """Pulso tático: paralisa temporariamente as ameaças por 200 créditos."""
        if self.estado != "JOGANDO" or self.emp_cooldown > 0 or self.dinheiro < 200 or not self.malwares:
            return
        self.dinheiro -= 200
        self.emp_cooldown = 25 * 60
        self.emp_flash = 22
        for malware in self.malwares:
            malware.stun_timer = max(malware.stun_timer, 120)
        self.textos_flutuantes.append(TextoFlutuante(LARGURA // 2, 100, "PULSO EMP: AMEACAS BLOQUEADAS", AZUL_NEON, fonte_media))

    def desenhar_hud_tatico(self, superficie):
        if self.estado not in ("JOGANDO", "PAUSA"):
            return
        x, y, w, h = 360, 12, 330, 46
        painel = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(painel, (10, 20, 32, 225), (0, 0, w, h), border_radius=10)
        pygame.draw.rect(painel, (35, 165, 205, 140), (0, 0, w, h), 2, border_radius=10)
        superficie.blit(painel, (x, y))
        if self.emp_cooldown:
            estado = f"RECARGA {self.emp_cooldown // 60 + 1}s"
            cor = CINZA_CLARO
        elif self.dinheiro < 200:
            estado = "SEM CREDITOS"
            cor = VERMELHO_NEON
        else:
            estado = "PRONTO - 200 CR"
            cor = VERDE_NEON
        desenhar_texto_sombra(superficie, f"[E] PULSO EMP | {estado}", fonte_pequena, cor, (x + 12, y + 12), center=False)
        if self.emp_flash:
            camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            camada.fill((25, 180, 240, min(90, self.emp_flash * 4)))
            superficie.blit(camada, (0, 0))
        if self.show_help:
            ajuda = pygame.Surface((480, 155), pygame.SRCALPHA)
            pygame.draw.rect(ajuda, (10, 18, 30, 240), ajuda.get_rect(), border_radius=12)
            pygame.draw.rect(ajuda, (50, 185, 225), ajuda.get_rect(), 2, border_radius=12)
            superficie.blit(ajuda, (LARGURA // 2 - 240, ALTURA // 2 - 78))
            for i, linha in enumerate(("CONTROLES", "E - Pulso EMP (200 CR)", "F11 - Tela cheia | F12 - Captura", "H - Ocultar ajuda | ESC - Pausa")):
                desenhar_texto_sombra(superficie, linha, fonte_pequena, BRANCO, (LARGURA // 2 - 218, ALTURA // 2 - 61 + i * 35), center=False)

    def update(self):
        if self.estado == "JOGANDO":
            self.emp_cooldown = max(0, self.emp_cooldown - 1)
            self.emp_flash = max(0, self.emp_flash - 1)
        if self.anim_alpha > 0: self.anim_alpha -= 10
        pos = posicao_mouse()

        if self.estado in ["MENU", "MAP_SELECT", "DIFICULDADE", "PAUSA"]:
            self.b_fullscreen_menu.texto = f"TELA CHEIA: {'ON' if is_fullscreen else 'OFF'}"
            self.b_fullscreen_menu.update_hover(pos)

        if self.estado == "MENU":
            self.b_jogar.update_hover(pos)
            self.b_sair.update_hover(pos)
            for i in range(len(self.bg_nodes)):
                x, y, vx, vy = self.bg_nodes[i]
                x = (x + vx) % LARGURA
                y = (y + vy) % ALTURA
                self.bg_nodes[i] = (x, y, vx, vy)

        elif self.estado == "MAP_SELECT":
            for b in self.botoes_mapas: b.update_hover(pos)
            self.b_voltar_menu.update_hover(pos)

        elif self.estado == "DIFICULDADE":
            self.b_dif_facil.update_hover(pos)
            self.b_dif_medio.update_hover(pos)
            self.b_dif_dificil.update_hover(pos)
            self.b_dif_perfeita.update_hover(pos)
            self.b_dif_desafio.update_hover(pos)
            self.b_dif_raid.update_hover(pos)
            self.b_voltar_menu.update_hover(pos)

        elif self.estado == "PAUSA":
            self.b_retomar.update_hover(pos)
            self.b_autoplay.update_hover(pos)
            self.b_voltar_menu.update_hover(pos)

        elif self.estado == "JOGANDO":
            target_offset = 0.0 if self.loja_aberta else 250.0
            self.loja_x_offset += (target_offset - self.loja_x_offset) * 0.15
            if abs(self.loja_x_offset - target_offset) < 0.1: self.loja_x_offset = target_offset

            self.b_toggle_loja.rect.x = self.b_toggle_loja.base_x + self.loja_x_offset
            self.b_pausa.rect.x = self.b_pausa.base_x + self.loja_x_offset
            self.b_velocidade.rect.x = self.b_velocidade.base_x + self.loja_x_offset
            self.b_toggle_loja.texto = ">" if self.loja_aberta else "<"

            self.b_toggle_loja.update_hover(pos)
            self.b_pausa.update_hover(pos)
            self.b_velocidade.update_hover(pos)

            novo_tooltip = ""
            limit_loja_x = LARGURA - 250 + self.loja_x_offset

            for b in self.botoes_compra:
                b.set_scroll(self.scroll_y, self.loja_x_offset)
                if pos[0] > limit_loja_x and pos[1] > 95: b.update_hover(pos)
                if b.hover:
                    novo_tooltip = f"{ATRIBUTOS_TORRE[b.acao]['nome']}\n{DESCRICOES_TORRES[b.acao]}"
                else: b.hover = False

            if self.hardware_foco:
                self.b_up1.update_hover(pos)
                self.b_up2.update_hover(pos)
                self.b_up3.update_hover(pos)
                self.b_vender.update_hover(pos)

                base = ATRIBUTOS_TORRE[self.hardware_foco.tipo]
                p_levels = [self.hardware_foco.p1, self.hardware_foco.p2, self.hardware_foco.p3]

                for idx, (btn, btn_attr) in enumerate([(self.b_up1, "p1"), (self.b_up2, "p2"), (self.b_up3, "p3")]):
                    if btn.hover:
                        lvl = p_levels[idx]
                        pode, razao = check_upgrade_allowed(idx, p_levels)
                        if lvl < 5:
                            upg = base[btn_attr][lvl]
                            if pode: novo_tooltip = f"Atualização L{idx + 1} - {upg['nome']}\n{get_upgrade_desc(upg, self.hardware_foco.tipo)}"
                            else: novo_tooltip = f"Bloqueado pela Arquitetura 5-2-0.\n{razao}"
                        else: novo_tooltip = f"Atualização L{idx + 1}\nPotência Máxima Atingida."

                if self.b_vender.hover:
                    if self.dificuldade_atual != "desafio": novo_tooltip = "DESINSTALAR HARDWARE\nRemove a estrutura de segurança\ne recupera parte dos\ncréditos investidos."
                    else: novo_tooltip = "DELETAR HARDWARE (0 CR)\nNo modo desafio, desinstalar\nhardwares libera espaço no mapa,\nmas retorna 0 Créditos."

            if novo_tooltip != "":
                if self.tooltip_text != novo_tooltip:
                    self.tooltip_text = novo_tooltip
                    self.target_tooltip_alpha = 255
            else: self.target_tooltip_alpha = 0

            self.tooltip_alpha += (self.target_tooltip_alpha - self.tooltip_alpha) * 0.15
            if self.tooltip_alpha < 1: self.tooltip_alpha = 0
            if self.tooltip_alpha > 255: self.tooltip_alpha = 255

            for _ in range(self.game_speed):
                if self.estado != "JOGANDO": break

                if not self.inimigos_para_spawnar and not self.malwares and not self.esperando_proxima_onda:
                    if self.dificuldade_atual == "desafio":
                        self.estado = "VITORIA"
                        self.anim_alpha = 255
                        break
                    elif self.fase == self.fase_maxima and not self.modo_infinito_ativado:
                        self.estado = "VITORIA"
                        self.anim_alpha = 255
                        break
                    else:
                        if self.auto_play:
                            self.fase += 1
                            recompensa_fase = 100 + (self.fase * 2)
                            self.dinheiro += recompensa_fase
                            self.textos_flutuantes.append(TextoFlutuante(LARGURA // 2, ALTURA // 2, f"+{recompensa_fase} CR - HACKERS REPELIDOS", AZUL_NEON, fonte_media))
                            self.gerar_wave()
                        else:
                            self.esperando_proxima_onda = True
                            self.game_speed = 0
                            self.b_velocidade.texto = "> INICIAR"
                            self.b_velocidade.cor_base = AMARELO_PRINCIPAL

                if self.inimigos_para_spawnar:
                    self.timer_spawn -= 1
                    if self.timer_spawn <= 0:
                        tipo = self.inimigos_para_spawnar.pop(0)
                        self.malwares.append(Malware(self.fase, tipo, self.caminho_atual, self.mult_dificuldade, dificuldade_atual=self.dificuldade_atual))
                        self.timer_spawn = 6 if tipo == "adware_enxame" else max(10, 35 - self.fase * 1.5)

                for t in self.hardwares: t.mod_rate, t.mod_range, t.aura_camo = 1.0, 1.0, False

                # OTIMIZAÇÃO: Usando a distância ao quadrado para auras
                for t in self.hardwares:
                    if t.tipo == "overclock":
                        raio_sq = (t.range + (t.p2 * 10)) ** 2
                        for alvo in self.hardwares:
                            if alvo != t and (alvo.x - t.x)**2 + (alvo.y - t.y)**2 <= raio_sq:
                                alvo.mod_rate *= (0.8 - (t.p1 * 0.05))
                    elif t.tipo == "radar_quantico":
                        raio_sq = (t.range + (t.p2 * 15)) ** 2
                        for alvo in self.hardwares:
                            if (alvo.x - t.x)**2 + (alvo.y - t.y)**2 <= raio_sq: alvo.mod_range *= (1.2 + (t.p1 * 0.1))
                            if t.detecta_camuflado: alvo.aura_camo = True

                for t in self.hardwares: t.atacar(self)
                for p in self.pacotes[:]:
                    p.update(self)
                    if not p.ativo: self.pacotes.remove(p)

                for pt in self.particulas[:]:
                    pt.update()
                    if pt.vida <= 0: self.particulas.remove(pt)

                for tf in self.textos_flutuantes[:]:
                    tf.update()
                    if tf.vida <= 0: self.textos_flutuantes.remove(tf)

                for m in self.malwares[:]:
                    m.processar_veneno()
                    
                    if m.is_raid_boss:
                        perc_hp = m.vida / m.maxvida
                        if perc_hp <= 0.75 and m.skulls_ativados == 0: self.trigger_boss_skull(m)
                        elif perc_hp <= 0.50 and m.skulls_ativados == 1: self.trigger_boss_skull(m)
                        elif perc_hp <= 0.25 and m.skulls_ativados == 2: self.trigger_boss_skull(m)

                    slow_holograma = 1.0
                    for t in self.hardwares:
                        if t.tipo == "parede_holo":
                            if (m.x - t.x)**2 + (m.y - t.y)**2 <= (t.range + (t.p2 * 15))**2:
                                slow_holograma = min(slow_holograma, 0.4 - (t.p1 * 0.05))

                    if m.mover(self.fase, slow_holograma):
                        if m.is_raid_boss:
                            self.vida = 0
                            self.textos_flutuantes.append(TextoFlutuante(100, 100, "VÍRUS FATAL NO NÚCLEO", VERMELHO_BOSS, fonte_media))
                        else:
                            dano_vida = 25 if m.tipo == "ddos_zeppelin" else 5 if m.tipo == "spyware_boss" else 1
                            self.vida -= dano_vida
                            self.textos_flutuantes.append(TextoFlutuante(100, 100, f"INTEGRIDADE: -{dano_vida}", VERMELHO_NEON, fonte_media))
                        
                        self.malwares.remove(m)
                        
                        if self.vida <= 0:
                            self.vida = 0
                            self.estado, self.anim_alpha = "GAME_OVER", 255
                            break
                            
                    elif m.vida <= 0:
                        m.ativo = False
                        if self.dificuldade_atual != "desafio":
                            self.dinheiro += m.reward
                            self.textos_flutuantes.append(TextoFlutuante(m.x, m.y, f"+{m.reward} CR", AMARELO_NEON, fonte_pequena))
                        else:
                            self.textos_flutuantes.append(TextoFlutuante(m.x, m.y, "ARQUIVO EXCLUÍDO", AZUL_NEON, fonte_pequena))

                        if self.hardware_foco: self.hardware_foco.kills += 1
                        for _ in range(12): self.particulas.append(Particula(m.x, m.y, m.cor, vel_base=6))

                        if m.tipo == "ddos_zeppelin":
                            for _ in range(4):
                                novo = Malware(self.fase, "worm_rapido", self.caminho_atual, self.mult_dificuldade, recompensa_ativa=False, dificuldade_atual=self.dificuldade_atual)
                                novo.x, novo.y, novo.alvo = m.x + random.randint(-15, 15), m.y + random.randint(-15, 15), m.alvo
                                self.malwares.append(novo)
                        
                        self.malwares.remove(m)

        elif self.estado == "VITORIA":
            self.b_continuar.update_hover(pos)
            self.b_voltar_menu.update_hover(pos)

    def draw(self, tela):
        if self.estado == "MENU":
            gradient_rect(tela, FUNDO_ESCURO, CINZA_MUITO_ESCURO, tela.get_rect())
            for x, y, vx, vy in self.bg_nodes:
                pygame.draw.circle(tela, AMARELO_NEON, (int(x), int(y)), 2)
                for ox, oy, _, _ in self.bg_nodes:
                    if abs(x - ox) < 150 and abs(y - oy) < 150:
                        dist_sq = (x - ox) ** 2 + (y - oy) ** 2
                        if dist_sq < 22500:
                            dist = math.sqrt(dist_sq)
                            pygame.draw.line(tela, (*AMARELO_PRINCIPAL[:3], int(100 * (1 - dist / 150))), (int(x), int(y)), (int(ox), int(oy)), 2)
            desenhar_texto_sombra(tela, "CODE GUARDIANS", fonte_titulo, BRANCO, (LARGURA // 2, 120))
            desenhar_texto_sombra(tela, "TD", fonte_titulo, AMARELO_NEON, (LARGURA // 2, 190))
            self.b_jogar.draw(tela)
            self.b_sair.draw(tela)
            self.b_fullscreen_menu.draw(tela)

        elif self.estado == "MAP_SELECT":
            gradient_rect(tela, FUNDO_ESCURO, CINZA_MUITO_ESCURO, tela.get_rect())
            desenhar_texto_sombra(tela, "MAPAS:", fonte_titulo, AMARELO_NEON, (LARGURA // 2, 60))
            for b in self.botoes_mapas:
                b.draw(tela)
                mapa_nome = b.acao.split("_")[1]
                desenhar_miniatura_mapa(tela, b.rect, mapa_nome)
            self.b_voltar_menu.draw(tela)
            self.b_fullscreen_menu.draw(tela)

        elif self.estado == "DIFICULDADE":
            gradient_rect(tela, FUNDO_ESCURO, CINZA_MUITO_ESCURO, tela.get_rect())
            desenhar_texto_sombra(tela, "DIFICULDADES:", fonte_titulo, AMARELO_NEON, (LARGURA // 2, 60))
            self.b_dif_facil.draw(tela)
            self.b_dif_medio.draw(tela)
            self.b_dif_dificil.draw(tela)
            self.b_dif_perfeita.draw(tela)
            self.b_dif_desafio.draw(tela)
            self.b_dif_raid.draw(tela) 
            self.b_voltar_menu.draw(tela)
            self.b_fullscreen_menu.draw(tela)

        elif self.estado in ["JOGANDO", "PAUSA", "GAME_OVER", "VITORIA"]:
            tela.blit(self.fundo, (0, 0))

            y_stat = 20

            if self.dificuldade_atual == "desafio": texto_onda = "ATAQUE OVERLOAD"
            elif self.modo_infinito_ativado: texto_onda = f"ONDA: {self.fase} (LOOP INFINITO)"
            else: texto_onda = f"ONDA: {self.fase}/{self.fase_maxima}"

            desenhar_texto_sombra(tela, texto_onda, fonte_pequena, BRANCO, (20, y_stat), center=False)
            desenhar_texto_sombra(tela, f"CR: {self.dinheiro}", fonte_media, AMARELO_NEON, (20, y_stat + 25), center=False)
            desenhar_texto_sombra(tela, f"VIDA: {int(self.vida)}", fonte_media, VERMELHO_NEON, (160, y_stat + 25), center=False)

            for t in self.hardwares:
                if t.tipo in ["overclock", "radar_quantico", "parede_holo"]:
                    glow = get_glow_surface(t.range, t.cor, 15)
                    tela.blit(glow, (t.x - t.range, t.y - t.range))

            for t in self.hardwares: t.desenhar(tela)
            for m in self.malwares: m.desenhar(tela)
            for pt in self.particulas: pt.draw(tela)
            for p in self.pacotes: p.desenhar(tela)
            for tf in self.textos_flutuantes: tf.draw(tela)

            boss_ativo = next((m for m in self.malwares if getattr(m, 'is_raid_boss', False)), None)
            if boss_ativo:
                hud_w, hud_h = 600, 40
                hud_x, hud_y = (LARGURA - hud_w) // 2, 20
                
                pygame.draw.rect(tela, FUNDO_PAINEL, (hud_x - 10, hud_y - 10, hud_w + 20, hud_h + 40), border_radius=5)
                pygame.draw.rect(tela, VERMELHO_BOSS, (hud_x - 10, hud_y - 10, hud_w + 20, hud_h + 40), 2, border_radius=5)
                
                desenhar_texto_sombra(tela, f"VÍRUS PRIMORDIAL - TIER {boss_ativo.boss_tier}", fonte_media, VERMELHO_BOSS, (LARGURA // 2, hud_y + 10))
                
                barra_y = hud_y + 30
                pygame.draw.rect(tela, CINZA_METAL, (hud_x, barra_y, hud_w, 20))
                
                perc = max(0.0, boss_ativo.vida / boss_ativo.maxvida)
                pygame.draw.rect(tela, VERMELHO_NEON, (hud_x, barra_y, int(hud_w * perc), 20))
                
                for i in range(1, 4):
                    skull_x = hud_x + int(hud_w * (i * 0.25))
                    color_skull = PRETO if perc < (i * 0.25) else AMARELO_NEON
                    pygame.draw.circle(tela, color_skull, (skull_x, barra_y + 10), 6)
                    pygame.draw.circle(tela, BRANCO, (skull_x, barra_y + 10), 6, 1)

            # LOJA LATERAL
            panel_x = LARGURA - 250 + self.loja_x_offset
            painel_lat = pygame.Surface((250, ALTURA), pygame.SRCALPHA)
            pygame.draw.rect(painel_lat, FUNDO_PAINEL, (0, 0, 250, ALTURA))
            pygame.draw.line(painel_lat, AMARELO_NEON, (0, 0), (0, ALTURA), 3)
            tela.blit(painel_lat, (panel_x, 0))

            self.b_toggle_loja.draw(tela)
            self.b_pausa.draw(tela)
            self.b_velocidade.draw(tela)

            x_centro_loja = LARGURA - 125 + self.loja_x_offset
            desenhar_texto_sombra(tela, "PORTAL DE SOFTWARES", fonte_media, AMARELO_NEON, (x_centro_loja, 75), center=True)

            clip_rect = pygame.Rect(LARGURA - 245 + self.loja_x_offset, 95, 245, ALTURA - 95)
            tela.set_clip(clip_rect)

            for nome_cat, y_cat in self.headers_loja:
                y_draw = y_cat - self.scroll_y
                if 80 < y_draw < ALTURA:
                    desenhar_texto_sombra(tela, nome_cat, fonte_pequena, AMARELO_NEON, (x_centro_loja, y_draw), center=True)
                    pygame.draw.line(tela, CINZA_METAL, (int(LARGURA - 230 + self.loja_x_offset), y_draw + 12), (int(LARGURA - 20 + self.loja_x_offset), y_draw + 12), 2)

            for b in self.botoes_compra:
                if b.rect.bottom > 95 and b.rect.top < ALTURA:
                    bloqueado = self.dinheiro < ATRIBUTOS_TORRE[b.acao]["custo"]
                    b.draw(tela, bloqueado, selecionado=(self.hardware_selecionado == b.acao))

                    cor = ATRIBUTOS_TORRE[b.acao]["cor"]
                    cx, cy = b.rect.centerx, b.rect.centery + 10
                    draw_hexagon(tela, CINZA_METAL, (cx, cy), 12)
                    pygame.draw.circle(tela, cor, (cx, cy), 6)

                    if bloqueado:
                        filtro = pygame.Surface((b.rect.w, b.rect.h), pygame.SRCALPHA)
                        pygame.draw.rect(filtro, (0, 0, 0, 150), (0, 0, b.rect.w, b.rect.h), border_radius=0)
                        tela.blit(filtro, (b.rect.x, b.rect.y))

            sb_h = max(20, (ALTURA - 95) * ((ALTURA - 95) / (self.max_scroll + ALTURA - 95)))
            sb_y = 95 + (self.scroll_y / max(1, self.max_scroll)) * ((ALTURA - 95) - sb_h)
            pygame.draw.rect(tela, CINZA_METAL, (LARGURA - 6 + self.loja_x_offset, sb_y, 4, sb_h))
            tela.set_clip(None)

            pos = posicao_mouse()
            limit_loja_x = LARGURA - 250 + self.loja_x_offset
            if self.hardware_selecionado and pos[0] < limit_loja_x and pos[1] < ALTURA - (150 if self.hardware_foco else 0):
                rng = ATRIBUTOS_TORRE[self.hardware_selecionado]["range_base"]
                cor = ATRIBUTOS_TORRE[self.hardware_selecionado]["cor"]
                valido = self.posicao_valida(pos[0], pos[1])

                glow = get_glow_surface(rng, AZUL_NEON, 30)
                tela.blit(glow, (pos[0] - rng, pos[1] - rng))
                pygame.draw.circle(tela, AZUL_NEON, pos, rng, 2)

                draw_hexagon(tela, (0, 0, 0, 100), (pos[0] + 4, pos[1] + 4), 22)
                draw_hexagon(tela, cor if valido else VERMELHO_NEON, pos, 22)
                draw_hexagon(tela, BRANCO if valido else PRETO, pos, 22, 3)

            if self.hardware_foco:
                painel_inf_w = LARGURA - 250 if self.loja_aberta else LARGURA
                painel_inf = pygame.Surface((painel_inf_w, 150), pygame.SRCALPHA)
                pygame.draw.rect(painel_inf, FUNDO_PAINEL, (0, 0, painel_inf_w, 150))
                pygame.draw.line(painel_inf, AMARELO_NEON, (0, 0), (painel_inf_w, 0), 3)
                tela.blit(painel_inf, (0, ALTURA - 150))

                pygame.draw.circle(tela, BRANCO, (int(self.hardware_foco.x), int(self.hardware_foco.y)), int(self.hardware_foco.range * self.hardware_foco.mod_range), 1)

                base = ATRIBUTOS_TORRE[self.hardware_foco.tipo]
                desenhar_texto_sombra(tela, base["nome"].upper(), fonte_media, AMARELO_NEON, (20, ALTURA - 130), center=False)
                desenhar_texto_sombra(tela, f"Ameaças Deletadas: {self.hardware_foco.kills}", fonte_pequena, BRANCO, (20, ALTURA - 90), center=False)

                p_levels = [self.hardware_foco.p1, self.hardware_foco.p2, self.hardware_foco.p3]

                for idx, (btn, btn_attr) in enumerate([(self.b_up1, "p1"), (self.b_up2, "p2"), (self.b_up3, "p3")]):
                    lvl = p_levels[idx]
                    pode, razao = check_upgrade_allowed(idx, p_levels)

                    if lvl < 5:
                        upg = base[btn_attr][lvl]
                        if pode:
                            btn.texto = f"UPDATE L{idx + 1}\n{upg['nome']}\n{upg['custo']} CR\n(Versão {lvl + 1}/5)"
                            bloq = self.dinheiro < upg["custo"]

                            if btn.hover and not bloq and upg.get("range", 0) > 0:
                                futuro_range = (self.hardware_foco.range + upg["range"]) * self.hardware_foco.mod_range
                                pygame.draw.circle(tela, VERDE_NEON, (int(self.hardware_foco.x), int(self.hardware_foco.y)), int(futuro_range), 2)
                        else:
                            btn.texto = f"PROTOCOLO {idx + 1}\nBLOQUEADO\n\n({razao})"
                            bloq = True
                    else:
                        btn.texto = f"PROTOCOLO {idx + 1}\nVERSÃO MÁXIMA (5/5)"
                        bloq = True

                    btn.draw(tela, bloqueado=bloq)

                if self.dificuldade_atual != "desafio":
                    val_venda = int(base["custo"] * 0.7)
                    for idx, path in enumerate(["p1", "p2", "p3"]):
                        for i in range(p_levels[idx]): val_venda += int(base[path][i]["custo"] * 0.7)
                    self.b_vender.texto = f"DESINSTALAR\n+{val_venda} CR"
                else: self.b_vender.texto = "DELETAR\n(0 CR)"

                self.b_vender.draw(tela)

            if self.estado == "PAUSA":
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                overlay.fill((0, 10, 20, 200))
                tela.blit(overlay, (0, 0))
                desenhar_texto_sombra(tela, "SISTEMA EM MODO DE ESPERA", fonte_titulo, AMARELO_NEON, (LARGURA // 2, 120))
                self.b_retomar.draw(tela)
                self.b_autoplay.draw(tela)
                self.b_voltar_menu.draw(tela)
                self.b_fullscreen_menu.draw(tela)

            elif self.estado == "GAME_OVER":
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                overlay.fill((100, 0, 0, 220))
                tela.blit(overlay, (0, 0))
                desenhar_texto_sombra(tela, "FALHA CRÍTICA DO SISTEMA", fonte_titulo, BRANCO, (LARGURA // 2, 120))
                if self.dificuldade_atual == "desafio": desenhar_texto_sombra(tela, "A Horda Brutal destruiu o Firewall!", fonte_media, AMARELO_NEON, (LARGURA // 2, 200))
                elif self.dificuldade_atual == "raid": desenhar_texto_sombra(tela, "O Vírus Primordial hackeou seu núcleo...", fonte_media, VERMELHO_BOSS, (LARGURA // 2, 200))
                else: desenhar_texto_sombra(tela, f"O Firewall resistiu até A ONDA {self.fase}", fonte_media, AMARELO_NEON, (LARGURA // 2, 200))
                self.b_voltar_menu.draw(tela)

            elif self.estado == "VITORIA":
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                overlay.fill((0, 100, 50, 220))
                tela.blit(overlay, (0, 0))
                desenhar_texto_sombra(tela, "SISTEMA 100% SEGURO", fonte_titulo, BRANCO, (LARGURA // 2, 120))
                texto_vitoria = f"Malwares deletados após {self.fase_maxima} ataques!" if self.dificuldade_atual not in ["desafio", "raid"] else "Ameaça Neutralizada, Núcleo Intacto!"
                desenhar_texto_sombra(tela, texto_vitoria, fonte_media, VERDE_NEON, (LARGURA // 2, 200))
                if self.dificuldade_atual not in ["desafio", "raid"]: self.b_continuar.draw(tela)
                self.b_voltar_menu.draw(tela)

        if self.estado == "JOGANDO" and self.tooltip_alpha > 0:
            desenhar_tooltip(tela, self.tooltip_text, posicao_mouse(), self.tooltip_alpha)

        if self.anim_alpha > 0:
            fade = pygame.Surface((LARGURA, ALTURA))
            fade.fill(PRETO)
            fade.set_alpha(self.anim_alpha)
            tela.blit(fade, (0, 0))

    def posicao_valida(self, x, y):
        limit_loja_x = LARGURA - 250 + self.loja_x_offset
        if x >= limit_loja_x: return False

        for i in range(len(self.caminho_atual) - 1):
            x1, y1 = self.caminho_atual[i]
            x2, y2 = self.caminho_atual[i + 1]
            if calcular_distancia_segmento_sq(x, y, x1, y1, x2, y2) < 3025: return False
        
        # OTIMIZAÇÃO: Calculando a distância ao quadrado entre torres
        for t in self.hardwares:
            if (t.x - x) ** 2 + (t.y - y) ** 2 < 2025: return False
        return True

    def handle_event(self, evento):
        pos = posicao_mouse()
        if evento.type == pygame.MOUSEWHEEL and self.estado == "JOGANDO":
            limit_loja_x = LARGURA - 250 + self.loja_x_offset
            if pos[0] > limit_loja_x:
                self.scroll_y -= evento.y * 35
                self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.handle_click(pos)

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.handle_drop(pos)    
            
    def handle_drop(self, pos):
        # Verifica se o jogo está a decorrer e se há alguma torre selecionada a ser arrastada
        if self.estado == "JOGANDO" and self.hardware_selecionado:
            limit_loja_x = LARGURA - 250 + self.loja_x_offset
            zona_mapa = pos[0] < limit_loja_x and pos[1] < (ALTURA - 150 if self.hardware_foco else ALTURA)
            
            # Se largou a torre numa zona válida do mapa
            if zona_mapa and self.posicao_valida(pos[0], pos[1]):
                custo = ATRIBUTOS_TORRE[self.hardware_selecionado]["custo"]
                if self.dinheiro >= custo:
                    self.dinheiro -= custo
                    self.hardwares.append(HardwareDefesa(pos[0], pos[1], self.hardware_selecionado))
                    # Limpa a seleção após colocar
                    self.hardware_selecionado = None

    def handle_click(self, pos):
        if self.estado in ["MENU", "MAP_SELECT", "DIFICULDADE", "PAUSA"]:
            if self.b_fullscreen_menu.click(pos):
                alternar_tela_cheia()
                return

        if self.estado == "MENU":
            if self.b_jogar.click(pos): self.estado = "MAP_SELECT"
            elif self.b_sair.click(pos): pygame.quit(); sys.exit()

        elif self.estado == "MAP_SELECT":
            for b in self.botoes_mapas:
                if b.click(pos):
                    self.mapa_temp = b.acao.split("_")[1]
                    self.estado = "DIFICULDADE"
            if self.b_voltar_menu.click(pos): self.estado = "MENU"

        elif self.estado == "DIFICULDADE":
            if self.b_dif_facil.click(pos): self.iniciar_partida(self.mapa_temp, "facil")
            elif self.b_dif_medio.click(pos): self.iniciar_partida(self.mapa_temp, "medio")
            elif self.b_dif_dificil.click(pos): self.iniciar_partida(self.mapa_temp, "dificil")
            elif self.b_dif_perfeita.click(pos): self.iniciar_partida(self.mapa_temp, "perfeita")
            elif self.b_dif_desafio.click(pos): self.iniciar_partida(self.mapa_temp, "desafio")
            elif self.b_dif_raid.click(pos): self.iniciar_partida(self.mapa_temp, "raid")
            elif self.b_voltar_menu.click(pos): self.estado = "MAP_SELECT"

        elif self.estado == "PAUSA":
            if self.b_retomar.click(pos): self.estado = "JOGANDO"
            elif self.b_autoplay.click(pos):
                self.auto_play = not self.auto_play
                self.b_autoplay.texto = "AUTO-START: ON" if self.auto_play else "AUTO-START: OFF"
                self.b_autoplay.cor_base = AMARELO_NEON
            elif self.b_voltar_menu.click(pos):
                self.estado = "MENU"
                self.anim_alpha = 255

        elif self.estado == "JOGANDO":
            if self.b_toggle_loja.click(pos):
                self.loja_aberta = not self.loja_aberta
                return

            if self.b_pausa.click(pos):
                self.estado = "PAUSA"
                return

            if self.b_velocidade.click(pos):
                if self.esperando_proxima_onda:
                    self.esperando_proxima_onda = False
                    self.fase += 1
                    recompensa_fase = 100 + (self.fase * 2)
                    self.dinheiro += recompensa_fase
                    self.textos_flutuantes.append(TextoFlutuante(LARGURA // 2, ALTURA // 2, f"+{recompensa_fase} CR - ATAQUE REPELIDO", AZUL_NEON, fonte_media))
                    self.gerar_wave()
                    self.game_speed = 1
                    self.b_velocidade.texto = ">> 2X"
                    self.b_velocidade.cor_base = AMARELO_NEON
                else:
                    if self.game_speed == 0: self.game_speed, self.b_velocidade.texto, self.b_velocidade.cor_base = 1, "> 1X", AMARELO_NEON
                    elif self.game_speed == 1: self.game_speed, self.b_velocidade.texto, self.b_velocidade.cor_base = 2, ">> 2X", AMARELO_NEON
                    elif self.game_speed == 2: self.game_speed, self.b_velocidade.texto, self.b_velocidade.cor_base = 3, ">>> 3X", AMARELO_NEON
                    else: self.game_speed, self.b_velocidade.texto, self.b_velocidade.cor_base = 1, "> 1X", AMARELO_NEON
                return

            limit_loja_x = LARGURA - 250 + self.loja_x_offset
            if pos[0] > limit_loja_x and pos[1] > 95:
                for b in self.botoes_compra:
                    if b.click(pos):
                        self.hardware_selecionado = b.acao if self.hardware_selecionado != b.acao else None
                        self.hardware_foco = None
                return

            zona_mapa = pos[0] < limit_loja_x and pos[1] < (ALTURA - 150 if self.hardware_foco else ALTURA)

            if zona_mapa:
                clicou_hardware = False
                for t in self.hardwares:
                    if (t.x - pos[0]) ** 2 + (t.y - pos[1]) ** 2 < 900:
                        self.hardware_foco = t
                        self.hardware_selecionado = None
                        clicou_hardware = True
                        break

                if not clicou_hardware:
                    if self.hardware_selecionado and self.dinheiro >= ATRIBUTOS_TORRE[self.hardware_selecionado]["custo"]:
                        if self.posicao_valida(pos[0], pos[1]):
                            self.dinheiro -= ATRIBUTOS_TORRE[self.hardware_selecionado]["custo"]
                            self.hardwares.append(HardwareDefesa(pos[0], pos[1], self.hardware_selecionado))
                            self.hardware_selecionado = None
                    else:
                        self.hardware_foco = None

            if self.hardware_foco and pos[1] > ALTURA - 150 and pos[0] < (LARGURA - 250 if self.loja_aberta else LARGURA):
                base = ATRIBUTOS_TORRE[self.hardware_foco.tipo]
                p_levels = [self.hardware_foco.p1, self.hardware_foco.p2, self.hardware_foco.p3]

                for idx, (btn, btn_attr) in enumerate([(self.b_up1, "p1"), (self.b_up2, "p2"), (self.b_up3, "p3")]):
                    if btn.click(pos):
                        lvl = p_levels[idx]
                        pode, _ = check_upgrade_allowed(idx, p_levels)

                        if lvl < 5 and pode:
                            custo = base[btn_attr][lvl]["custo"]
                            if self.dinheiro >= custo:
                                self.dinheiro -= custo
                                if idx == 0: self.hardware_foco.p1 += 1
                                elif idx == 1: self.hardware_foco.p2 += 1
                                elif idx == 2: self.hardware_foco.p3 += 1
                                self.hardware_foco.atualizar_atributos()
                                self.textos_flutuantes.append(TextoFlutuante(self.hardware_foco.x, self.hardware_foco.y - 20, "ATUALIZADO", AZUL_NEON, fonte_pequena))

                if self.b_vender.click(pos):
                    if self.dificuldade_atual != "desafio":
                        val_venda = int(base["custo"] * 0.7)
                        for idx, path in enumerate(["p1", "p2", "p3"]):
                            for i in range(p_levels[idx]): val_venda += int(base[path][i]["custo"] * 0.7)
                        self.dinheiro += val_venda
                        self.textos_flutuantes.append(TextoFlutuante(self.hardware_foco.x, self.hardware_foco.y, f"+{val_venda} CR", AMARELO_NEON, fonte_media))
                    else:
                        self.textos_flutuantes.append(TextoFlutuante(self.hardware_foco.x, self.hardware_foco.y, "ARQUIVO DELETADO", VERMELHO_NEON, fonte_pequena))
                    self.hardwares.remove(self.hardware_foco)
                    self.hardware_foco = None

        elif self.estado in ["GAME_OVER", "VITORIA"]:
            if self.estado == "VITORIA" and self.dificuldade_atual not in ["desafio", "raid"] and self.b_continuar.click(pos):
                self.modo_infinito_ativado = True
                self.fase += 1
                self.dinheiro += 150 + self.fase * 25
                self.gerar_wave()
                self.estado = "JOGANDO"
            elif self.b_voltar_menu.click(pos):
                self.estado = "MENU"
                self.anim_alpha = 255

def main():
    global tela
    game = Game()
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: rodando = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                if game.estado == "JOGANDO": game.estado = "PAUSA"
                elif game.estado == "PAUSA": game.estado = "JOGANDO"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_e:
                    game.ativar_emp()
                elif evento.key == pygame.K_h:
                    game.show_help = not game.show_help
                elif evento.key == pygame.K_F11:
                    alternar_tela_cheia()
                elif evento.key == pygame.K_F12:
                    pasta = Path(__file__).resolve().parent / "capturas"
                    pasta.mkdir(exist_ok=True)
                    pygame.image.save(janela, str(pasta / f"captura_{pygame.time.get_ticks()}.png"))
            game.handle_event(evento)
        game.update()
        game.draw(tela)
        game.desenhar_hud_tatico(tela)
        apresentar()
        relogio.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
