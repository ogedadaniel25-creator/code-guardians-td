import pygame
import math
from constantes import * # Puxa cores, resoluções e fontes

GLOW_CACHE = {}

def get_glow_surface(radius, color, alpha):
    key = (int(radius), color, alpha)
    if key not in GLOW_CACHE:
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color[:3], alpha), (radius, radius), radius)
        GLOW_CACHE[key] = surf
    return GLOW_CACHE[key]

def desenhar_texto_sombra(surface, texto, fonte, cor, pos, center=True):
    txt_sombra = fonte.render(texto, True, PRETO)
    txt_real = fonte.render(texto, True, cor)
    rect = txt_real.get_rect(center=pos) if center else txt_real.get_rect(topleft=pos)
    surface.blit(txt_sombra, (rect.x + 2, rect.y + 2))
    surface.blit(txt_real, rect)

def draw_hexagon(surface, color, center, radius, width=0, rotation=0):
    pts = []
    for i in range(6):
        angle = math.radians(i * 60 + rotation)
        pts.append((center[0] + math.cos(angle) * radius, center[1] + math.sin(angle) * radius))
    pygame.draw.polygon(surface, color, pts, width)
    return pts

def desenhar_miniatura_mapa(tela, rect, nome_mapa):
    tema = TEMAS_MAPAS[nome_mapa]
    pts = MAPAS_CHAVE[nome_mapa]
    w, h = rect.w - 14, rect.h - 35
    surf = pygame.Surface((w, h))
    surf.fill(tema["fundo"])

    scale_x, scale_y = w / 1400.0, h / 820.0
    pts_scaled = [(int((p[0] + 50) * scale_x), int((p[1] + 50) * scale_y)) for p in pts]

    if len(pts_scaled) > 1:
        pygame.draw.lines(surf, tema["borda"], False, pts_scaled, 6)
        pygame.draw.lines(surf, tema["caminho"], False, pts_scaled, 2)

    pygame.draw.rect(surf, tema["caminho"], (0, 0, w, h), 1)
    tela.blit(surf, (rect.x + 7, rect.y + 7))

def get_upgrade_desc(upg, tipo_torre):
    linhas = []
    if tipo_torre in ["overclock", "radar_quantico", "parede_holo"]:
        if upg['dano'] > 0: linhas.append(f"Força do Efeito +{upg['dano']}")
    elif tipo_torre == "minerador_cripto":
        if upg['dano'] > 0: linhas.append(f"Gera +{upg['dano']} Créditos")
    else:
        if upg['dano'] > 0: linhas.append(f"+{upg['dano']} Dano")
        if upg['dano'] < 0: linhas.append(f"{upg['dano']} Dano")

    if upg['range'] > 0: linhas.append(f"+{upg['range']} Alcance")
    if upg['rate'] < 0: linhas.append("Ação Mais Rápida")
    if upg['rate'] > 0: linhas.append("Ação Mais Lenta")
    if upg.get('camo'): linhas.append("Detecta Camuflados")
    if upg.get('ap'): linhas.append("Perfura Blindagem")
    return "\n".join(linhas) if linhas else "Efeito Especial"

def check_upgrade_allowed(p_idx, current_levels):
    if current_levels[p_idx] >= 5: return False, "NÍVEL MÁXIMO"
    test = current_levels.copy()
    test[p_idx] += 1
    if sum(1 for l in test if l > 2) > 1: return False, "APENAS 1 LINHA > NV2"
    if sum(1 for l in test if l > 0) > 2: return False, "APENAS 2 LINHAS ATIVAS"
    return True, ""

def desenhar_tooltip(tela, texto, pos, alpha):
    if alpha <= 0: return
    linhas = texto.split('\n')
    w = max(fonte_pequena.size(l)[0] for l in linhas) + 20
    h = len(linhas) * (fonte_pequena.get_height() + 2) + 10
    x, y = pos[0] + 15, pos[1] + 15
    if x + w > LARGURA: x = pos[0] - w - 10
    if y + h > ALTURA: y = pos[1] - h - 10

    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (15, 20, 30, int(alpha * 0.95)), (0, 0, w, h), border_radius=4)
    pygame.draw.rect(surf, (*AZUL_NEON[:3], int(alpha)), (0, 0, w, h), 1, border_radius=4)

    for i, l in enumerate(linhas):
        cor = AMARELO_NEON if i == 0 else BRANCO
        txt = fonte_pequena.render(l, True, cor)
        txt.set_alpha(int(alpha))
        surf.blit(txt, (10, 5 + i * (fonte_pequena.get_height() + 2)))
    tela.blit(surf, (x, y))

class Botao:
    def __init__(self, rect, texto, acao, cor_base=CINZA_METAL, fonte=fonte_media, valign="center"):
        self.rect = pygame.Rect(rect)
        self.base_x, self.base_y = rect[0], rect[1]
        self.texto, self.acao = texto, acao
        self.cor_base, self.fonte = cor_base, fonte
        self.hover, self.click_anim, self.valign = False, 0, valign

    def set_scroll(self, scroll_y, offset_x=0):
        self.rect.y, self.rect.x = self.base_y - scroll_y, self.base_x + offset_x

    def draw(self, tela, bloqueado=False, selecionado=False):
        c = VERMELHO_NEON if bloqueado else (AZUL_NEON if selecionado else self.cor_base)
        if self.hover and not bloqueado: c = (min(255, c[0] + 60), min(255, c[1] + 60), min(255, c[2] + 60))

        offset_y = 2 if self.click_anim > 0 else (-2 if self.hover and not bloqueado else 0)
        if self.click_anim > 0: self.click_anim -= 1
        rect_animado = pygame.Rect(self.rect.x, self.rect.y + offset_y, self.rect.w, self.rect.h)

        pts_main = [(rect_animado.x + 8, rect_animado.y), (rect_animado.right, rect_animado.y), (rect_animado.right, rect_animado.bottom - 8), (rect_animado.right - 8, rect_animado.bottom), (rect_animado.x, rect_animado.bottom), (rect_animado.x, rect_animado.y + 8)]
        pygame.draw.polygon(tela, FUNDO_PAINEL[:3], pts_main)
        pygame.draw.polygon(tela, c, pts_main, 2)

        linhas = self.texto.split('\n')
        total_height = len(linhas) * self.fonte.get_height()

        if self.valign == "bottom": y_pos = rect_animado.bottom - total_height - 10
        elif self.valign == "top": y_pos = rect_animado.top + 10
        else: y_pos = rect_animado.centery - total_height // 2

        cor_texto = BRANCO if not bloqueado else (100, 100, 100)
        for linha in linhas:
            if linha.strip(): desenhar_texto_sombra(tela, linha, self.fonte, cor_texto, (rect_animado.centerx, y_pos + self.fonte.get_height() // 2), center=True)
            y_pos += self.fonte.get_height()

    def update_hover(self, pos): self.hover = self.rect.collidepoint(pos)
    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.click_anim = 5
            return True
        return False