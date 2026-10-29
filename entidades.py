import pygame
import math
import random
from constantes import * # Puxa atributos das torres, ondas, etc.
from interface import * # Puxa draw_hexagon, get_glow_surface, etc.

def lerp_angle(current, target, factor=0.15):
    diff = (target - current + 180) % 360 - 180
    return (current + diff * factor) % 360

def gradient_rect(surface, left_colour, right_colour, target_rect, vertical=True):
    color_rect = pygame.Surface((2, 2))
    if vertical:
        pygame.draw.line(color_rect, left_colour, (0, 0), (1, 0))
        pygame.draw.line(color_rect, right_colour, (0, 1), (1, 1))
    else:
        pygame.draw.line(color_rect, left_colour, (0, 0), (0, 1))
        pygame.draw.line(color_rect, right_colour, (1, 0), (1, 1))
    color_rect = pygame.transform.smoothscale(color_rect, (target_rect.width, target_rect.height))
    surface.blit(color_rect, target_rect)

def catmull_rom(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
    y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
    return (x, y)

def gerar_caminho_suave(pontos_chave):
    caminho = []
    pts = [pontos_chave[0]] + pontos_chave + [pontos_chave[-1]]
    for i in range(1, len(pts) - 2):
        dist = math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        num_pontos = max(5, int(dist / 12))
        for t in range(num_pontos):
            pt = catmull_rom(pts[i - 1], pts[i], pts[i + 1], pts[i + 2], t / num_pontos)
            caminho.append((int(pt[0]), int(pt[1])))
    caminho.append(pontos_chave[-1])
    return caminho

def calcular_distancia_segmento_sq(px, py, x1, y1, x2, y2):
    l2 = (x2 - x1) ** 2 + (y2 - y1) ** 2
    if l2 == 0: return (px - x1) ** 2 + (py - y1) ** 2
    t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2))
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    return (px - proj_x) ** 2 + (py - proj_y) ** 2
class Particula:
    def __init__(self, x, y, cor, vel_base=4):
        self.x, self.y = x, y
        angulo = random.uniform(0, math.pi * 2)
        velocidade = random.uniform(vel_base * 0.5, vel_base * 1.5)
        self.vx = math.cos(angulo) * velocidade
        self.vy = math.sin(angulo) * velocidade
        self.vida = 255
        self.cor = cor
        self.tamanho = int(random.uniform(2, 6))
        self.tipo = random.choice(["cruz", "quadrado", "ponto"])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.85
        self.vy *= 0.85
        self.vida -= 15

    def draw(self, tela):
        if self.vida > 0:
            cx, cy = int(self.x), int(self.y)
            if self.tipo == "ponto":
                glow = get_glow_surface(self.tamanho, self.cor, int(self.vida))
                tela.blit(glow, (cx - self.tamanho, cy - self.tamanho))
            else:
                if self.tipo == "quadrado":
                    pygame.draw.rect(tela, self.cor, (cx - self.tamanho, cy - self.tamanho, self.tamanho * 2, self.tamanho * 2), 1)
                elif self.tipo == "cruz":
                    pygame.draw.line(tela, self.cor, (cx - self.tamanho, cy), (cx + self.tamanho, cy), 2)
                    pygame.draw.line(tela, self.cor, (cx, cy - self.tamanho), (cx, cy + self.tamanho), 2)


class TextoFlutuante:
    def __init__(self, x, y, texto, cor, fonte):
        self.x, self.y = x, y
        self.texto = texto
        self.cor = cor
        self.fonte = fonte
        self.vida = 255
        self.vy = -1.5
        self.txt_sombra = self.fonte.render(self.texto, True, PRETO)
        self.txt_real = self.fonte.render(self.texto, True, self.cor)

    def update(self):
        self.y += self.vy
        self.vida -= 4

    def draw(self, tela):
        if self.vida > 0:
            alpha = max(0, int(self.vida))
            self.txt_sombra.set_alpha(alpha)
            self.txt_real.set_alpha(alpha)
            tela.blit(self.txt_sombra, (int(self.x + 1), int(self.y + 1)))
            tela.blit(self.txt_real, (int(self.x), int(self.y)))


# Classe Malware (Antigo Inimigo) representa as ameaças virtuais
class Malware:
    def __init__(self, fase, tipo, caminho, mult_dificuldade=1.0, recompensa_ativa=True, dificuldade_atual="medio"):
        self.caminho = caminho
        self.x, self.y = self.caminho[0]
        self.alvo = 1
        self.tipo = tipo
        self.dificuldade_atual = dificuldade_atual
        self.progresso = 0 # OTIMIZAÇÃO: Cache de Progresso para as Torres

        self.slow_timer = 0
        self.stun_timer = 0
        self.veneno_timer = 0
        self.veneno_dano = 0
        self.escudo = 0
        self.anim_tick = random.randint(0, 100)

        self.camuflado = False
        self.blindado = False
        
        self.is_raid_boss = False
        self.boss_tier = 0
        self.skulls = 0
        self.skulls_ativados = 0

        # BALANCEAMENTO E ESCALA DE DIFICULDADE (Linear -> Moderado -> Exponencial)
        if fase <= 20: mult_fase = 1.0 + (fase * 0.05)
        elif fase <= 50: mult_fase = 2.0 + (fase * 0.15)
        else: mult_fase = 5.0 + (fase * 0.3)
            
        base_hp = fase * 10 * mult_fase * mult_dificuldade
        
        # Ajustes de atributos pelo tipo de Malware
        if tipo == "trojan_basico":
            self.vida, self.vel, self.tam, self.reward, self.cor = 50 + base_hp, 2.0, 14, 3, VERMELHO_NEON
        elif tipo == "worm_rapido":
            self.vida, self.vel, self.tam, self.reward, self.cor = 25 + base_hp * 0.7, 4.5, 14, 2, AMARELO_NEON
        elif tipo == "ransomware_tanque":
            self.vida, self.vel, self.tam, self.reward, self.cor = 220 + base_hp * 4.0, 1.3, 20, 8, LARANJA_NEON
        elif tipo == "spyware_boss":
            self.vida, self.vel, self.tam, self.reward, self.cor = 1500 + fase * 350, 1.0, 30, 80, ROXO_NEON
        elif tipo == "adware_enxame":
            self.vida, self.vel, self.tam, self.reward, self.cor = 20 + base_hp * 0.4, 5.0, 10, 1, VERDE_NEON
        elif tipo == "rootkit_escudo":
            self.vida, self.vel, self.tam, self.reward, self.cor = 80 + base_hp, 1.8, 16, 5, AZUL_NEON
            self.escudo = 250 + base_hp * 3.0
        elif tipo == "botnet_cura":
            self.vida, self.vel, self.tam, self.reward, self.cor = 130 + base_hp * 1.8, 1.5, 18, 6, BRANCO
        elif tipo == "stealth_fantasma":
            self.vida, self.vel, self.tam, self.reward, self.cor = 70 + base_hp * 1.0, 3.2, 16, 4, (150, 255, 255, 120)
        elif tipo == "ddos_zeppelin":
            self.vida, self.vel, self.tam, self.reward, self.cor = 3500 + base_hp * 10.0, 0.7, 50, 120, MAGENTA
        
        # MODO RAID: VÍRUS PRIMORDIAL
        elif tipo == "virus_primordial":
            self.is_raid_boss = True
            self.boss_tier = max(1, fase // 20)
            self.skulls = 3 
            self.vida = 8000 * (self.boss_tier ** 2.5) * mult_dificuldade
            self.vel = 0.4 + (self.boss_tier * 0.05)
            self.tam = 50 + (self.boss_tier * 8)
            self.reward = 1500 * self.boss_tier
            self.cor = VERMELHO_BOSS
            self.blindado = True 

        # Mutantes e Camuflagem
        if not self.is_raid_boss and (self.dificuldade_atual == "desafio" or fase >= 10):
            chance_mutacao = 0.50 if self.dificuldade_atual == "desafio" else min(0.7, (fase - 9) * 0.06)
            if random.random() < chance_mutacao: self.camuflado = True
            if random.random() < chance_mutacao and tipo not in ["adware_enxame", "stealth_fantasma", "botnet_cura"]:
                self.blindado = True
                self.vida *= 1.5
                self.vel *= 0.85

        if self.dificuldade_atual in ["desafio", "raid"]:
            self.vel *= 1.1
            self.vida *= 1.15

        self.max_escudo = self.escudo
        if not recompensa_ativa: self.reward = 0
        self.maxvida = self.vida
        self.ativo, self.angulo = True, 0

    def mover(self, fase, slow_externo=1.0):
        self.anim_tick += 1
        if self.alvo >= len(self.caminho):
            self.ativo = False
            return True

        if self.stun_timer > 0:
            self.stun_timer -= 1
            return False

        if self.tipo == "botnet_cura":
            cura_amount = max(0.5, fase * 0.2)
            self.vida = min(self.maxvida, self.vida + cura_amount)

        vel_atual = self.vel
        if self.slow_timer > 0:
            if self.tipo != "stealth_fantasma" and not self.is_raid_boss:
                vel_atual = self.vel * 0.5
            self.slow_timer -= 1

        vel_atual *= slow_externo

        tx, ty = self.caminho[self.alvo]
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        
        # OTIMIZAÇÃO: Cache de progresso para as torres mirarem mais rápido
        self.progresso = self.alvo * 1000 - d

        if d > 0: self.angulo = math.degrees(math.atan2(-dy, dx))

        if d < vel_atual:
            self.alvo += 1
        else:
            self.x += dx / d * vel_atual 
            self.y += dy / d * vel_atual
        return False

    def processar_veneno(self):
        if self.veneno_timer > 0:
            self.vida -= self.veneno_dano
            self.veneno_timer -= 1

    def desenhar(self, tela):
        cx, cy = int(self.x), int(self.y)

        if self.tipo != "stealth_fantasma" and not self.camuflado:
            pygame.draw.circle(tela, (0, 0, 0, 100), (cx + 4, cy + 4), self.tam)
            glow = get_glow_surface(int(self.tam * 1.5), self.cor, 30)
            tela.blit(glow, (cx - int(self.tam * 1.5), cy - int(self.tam * 1.5)))

        if self.is_raid_boss:
            pulso = math.sin(self.anim_tick * 0.1) * 10
            draw_hexagon(tela, (20, 0, 0), (cx, cy), self.tam + pulso, rotation=self.anim_tick)
            draw_hexagon(tela, self.cor, (cx, cy), self.tam, width=5, rotation=-self.anim_tick)
            draw_hexagon(tela, BRANCO, (cx, cy), self.tam * 0.6, width=2, rotation=self.anim_tick*2)
            pygame.draw.circle(tela, PRETO, (cx, cy), int(self.tam * 0.4))
            pygame.draw.circle(tela, self.cor, (cx, cy), int(self.tam * 0.2))
        elif self.tipo == "stealth_fantasma":
            glow = get_glow_surface(self.tam, self.cor, 120)
            tela.blit(glow, (cx - self.tam, cy - self.tam))
            pygame.draw.circle(tela, BRANCO, (cx, cy), int(self.tam * 0.5), 1)
        elif self.tipo == "ddos_zeppelin":
            surf = pygame.Surface((self.tam * 3, self.tam * 3), pygame.SRCALPHA)
            px, py = self.tam * 1.5, self.tam * 1.5
            pygame.draw.polygon(surf, CINZA_METAL, [(px - self.tam * 1.2, py - self.tam * 0.8), (px + self.tam * 1.2, py - self.tam * 0.8), (px + self.tam * 1.5, py), (px + self.tam * 1.2, py + self.tam * 0.8), (px - self.tam * 1.2, py + self.tam * 0.8)])
            pygame.draw.polygon(surf, self.cor, [(px - self.tam * 1.2, py - self.tam * 0.8), (px + self.tam * 1.2, py - self.tam * 0.8), (px + self.tam * 1.5, py), (px + self.tam * 1.2, py + self.tam * 0.8), (px - self.tam * 1.2, py + self.tam * 0.8)], 3)
            pygame.draw.rect(surf, FUNDO_ESCURO, (px - self.tam * 0.5, py - self.tam * 0.3, self.tam, self.tam * 0.6))
            pygame.draw.line(surf, AZUL_NEON, (px, py), (px - self.tam, py), 4)
            rot = pygame.transform.rotate(surf, self.angulo)
            tela.blit(rot, rot.get_rect(center=(cx, cy)))
        elif self.tipo == "worm_rapido":
            rad = math.radians(self.angulo)
            rad140 = math.radians(self.angulo + 140)
            rad_140 = math.radians(self.angulo - 140)
            pts = [(cx + math.cos(rad) * self.tam * 1.5, cy - math.sin(rad) * self.tam * 1.5), (cx + math.cos(rad140) * self.tam, cy - math.sin(rad140) * self.tam), (cx, cy), (cx + math.cos(rad_140) * self.tam, cy - math.sin(rad_140) * self.tam)]
            pygame.draw.polygon(tela, FUNDO_ESCURO, pts)
            pygame.draw.polygon(tela, self.cor, pts, 2)
            pygame.draw.circle(tela, BRANCO, pts[0], 2)
        elif self.tipo == "ransomware_tanque":
            rot_angle = self.anim_tick * 2
            draw_hexagon(tela, CINZA_METAL, (cx, cy), self.tam, rotation=rot_angle)
            draw_hexagon(tela, self.cor, (cx, cy), self.tam, width=3, rotation=rot_angle)
            draw_hexagon(tela, FUNDO_ESCURO, (cx, cy), self.tam * 0.6, rotation=-rot_angle)
            draw_hexagon(tela, BRANCO, (cx, cy), self.tam * 0.6, width=1, rotation=-rot_angle)
        elif self.tipo == "spyware_boss":
            for i in range(3, 7):
                rot = self.anim_tick * (8 - i)
                pts = []
                for j in range(i):
                    angle = math.radians(rot + j * (360 / i))
                    pts.append((cx + math.cos(angle) * (self.tam * (i / 6)), cy - math.sin(angle) * (self.tam * (i / 6))))
                pygame.draw.polygon(tela, (*self.cor[:3], 150), pts, 2)
            pygame.draw.circle(tela, PRETO, (cx, cy), self.tam * 0.5)
            pygame.draw.circle(tela, BRANCO, (cx, cy), self.tam * 0.3)
        elif self.tipo == "rootkit_escudo":
            pts = [(cx, cy - self.tam * 1.2), (cx + self.tam * 1.2, cy), (cx, cy + self.tam * 1.2), (cx - self.tam * 1.2, cy)]
            pygame.draw.polygon(tela, FUNDO_ESCURO, pts)
            pygame.draw.polygon(tela, self.cor, pts, 3)
            pygame.draw.line(tela, AZUL_NEON, (cx, cy - self.tam), (cx, cy + self.tam), 2)
        elif self.tipo == "adware_enxame":
            pts = []
            for i in range(3):
                angle = math.radians(self.anim_tick * 5 + i * 120)
                pts.append((cx + math.cos(angle) * self.tam, cy - math.sin(angle) * self.tam))
            pygame.draw.polygon(tela, self.cor, pts)
        else:
            draw_hexagon(tela, FUNDO_ESCURO, (cx, cy), self.tam, rotation=22.5)
            draw_hexagon(tela, self.cor, (cx, cy), self.tam, width=2, rotation=22.5)
            pygame.draw.circle(tela, BRANCO, (cx, cy), 3)

        if self.tipo == "botnet_cura":
            pygame.draw.line(tela, VERDE_NEON, (cx, cy - 8), (cx, cy + 8), 3)
            pygame.draw.line(tela, VERDE_NEON, (cx - 8, cy), (cx + 8, cy), 3)

        if self.camuflado and not self.is_raid_boss:
            raio_camo = self.tam + 4 + (self.anim_tick % 10) * 0.5
            pygame.draw.circle(tela, (60, 60, 60), (cx, cy), int(raio_camo), 2)
        if self.blindado and not self.is_raid_boss:
            draw_hexagon(tela, CINZA_CLARO, (cx, cy), self.tam + 6, width=4, rotation=self.anim_tick)

        if self.stun_timer > 0:
            for _ in range(2):
                px = cx + random.randint(-self.tam, self.tam)
                py = cy + random.randint(-self.tam, self.tam)
                pygame.draw.line(tela, AZUL_NEON, (cx, cy), (px, py), 2)
        elif self.veneno_timer > 0:
            pygame.draw.circle(tela, VERDE_LIMA, (cx, cy), self.tam + 4, 1)

        if not self.is_raid_boss:
            hp = max(0, min(1, self.vida / self.maxvida))
            w = max(30, self.tam * 2.2)
            by = int(self.y - self.tam - 16)
            pygame.draw.line(tela, CINZA_METAL, (int(self.x - w / 2), by), (int(self.x + w / 2), by), 4)
            cor_hp = VERDE_NEON if hp > 0.5 else (AMARELO_NEON if hp > 0.2 else VERMELHO_NEON)
            if hp > 0: pygame.draw.line(tela, cor_hp, (int(self.x - w / 2), by), (int(self.x - w / 2 + w * hp), by), 4)
            if self.escudo > 0:
                ep = max(0, min(1, self.escudo / self.max_escudo))
                pygame.draw.line(tela, AZUL_NEON, (int(self.x - w / 2), by - 4), (int(self.x - w / 2 + w * ep), by - 4), 2)


# Classe PacoteDados (Antigo Projetil) representa o ataque (dados enviados contra o vírus)
class PacoteDados:
    def __init__(self, x, y, alvo, dano, cor, tipo_torre, ignora_blindagem):
        self.x, self.y, self.alvo = x, y, alvo
        self.dano, self.cor, self.tipo_torre = dano, cor, tipo_torre
        self.ignora_blindagem = ignora_blindagem
        self.ativo = True

        if tipo_torre in ["sniper", "bobina_neural"]: self.vel = 80
        elif tipo_torre == "teleguiado": self.vel = 22
        elif tipo_torre == "injetor_viral": self.vel = 20
        else: self.vel = 35

    def update(self, game):
        if not self.alvo or not self.alvo.ativo:
            self.ativo = False
            return

        dx, dy = self.alvo.x - self.x, self.alvo.y - self.y
        d = math.hypot(dx, dy)

        if d < self.vel:
            for _ in range(random.randint(4, 8)):
                game.particulas.append(Particula(self.alvo.x, self.alvo.y, self.cor))

            if self.tipo_torre == "prisma_estase": self.alvo.slow_timer = 120
            elif self.tipo_torre == "bobina_neural": self.alvo.stun_timer = 20
            elif self.tipo_torre == "injetor_viral":
                self.alvo.veneno_timer = 200
                self.alvo.veneno_dano = self.dano * 0.15
            elif self.tipo_torre == "dreno_dados":
                cura = 1
                if game.vida < game.vida_max:
                    game.vida = min(game.vida_max, game.vida + cura)
                    game.textos_flutuantes.append(TextoFlutuante(self.alvo.x, self.alvo.y - 20, f"+{cura} HP", MAGENTA, fonte_mini))

            if self.tipo_torre in ["splash_plasma", "teleguiado"]:
                raio_sq = 90 ** 2 # OTIMIZAÇÃO: Usa o raio ao quadrado para cálculo rápido
                game.particulas.append(Particula(self.alvo.x, self.alvo.y, self.cor, vel_base=8))
                for m in game.malwares:
                    if (m.x - self.alvo.x)**2 + (m.y - self.alvo.y)**2 <= raio_sq:
                        self.aplicar_dano(m)
            else:
                self.aplicar_dano(self.alvo)

            self.ativo = False
        else:
            self.x += dx / d * self.vel
            self.y += dy / d * self.vel

    def aplicar_dano(self, alvo):
        dano_restante = self.dano

        if alvo.escudo > 0:
            if dano_restante >= alvo.escudo:
                dano_restante -= alvo.escudo
                alvo.escudo = 0
            else:
                alvo.escudo -= dano_restante
                dano_restante = 0

        is_heavy_tower = self.tipo_torre in ["morteiro", "sniper", "teleguiado", "ataque_orbital", "splash_plasma"]
        if alvo.blindado and not (self.ignora_blindagem or is_heavy_tower):
            dano_restante *= 0.25

        alvo.vida -= dano_restante

    def desenhar(self, tela):
        if self.tipo_torre == "sniper":
            ex = int(self.x - math.cos(math.atan2(self.alvo.y - self.y, self.alvo.x - self.x)) * 60)
            ey = int(self.y - math.sin(math.atan2(self.alvo.y - self.y, self.alvo.x - self.x)) * 60)
            pygame.draw.line(tela, (*self.cor[:3], 100), (int(self.x), int(self.y)), (ex, ey), 10)
            pygame.draw.line(tela, BRANCO, (int(self.x), int(self.y)), (ex, ey), 2)
        elif self.tipo_torre == "bobina_neural":
            ex = int(self.x - math.cos(math.atan2(self.alvo.y - self.y, self.alvo.x - self.x)) * 40)
            ey = int(self.y - math.sin(math.atan2(self.alvo.y - self.y, self.alvo.x - self.x)) * 40)
            mx = (self.x + ex) / 2 + random.randint(-15, 15)
            my = (self.y + ey) / 2 + random.randint(-15, 15)
            pygame.draw.line(tela, self.cor, (int(self.x), int(self.y)), (int(mx), int(my)), 3)
            pygame.draw.line(tela, BRANCO, (int(mx), int(my)), (ex, ey), 2)
        elif self.tipo_torre in ["injetor_viral", "dreno_dados"]:
            pygame.draw.rect(tela, self.cor, (int(self.x - 4), int(self.y - 4), 8, 8), 2)
            pygame.draw.circle(tela, BRANCO, (int(self.x), int(self.y)), 2)
        elif self.tipo_torre == "teleguiado":
            rad = math.atan2(self.alvo.y - self.y, self.alvo.x - self.x)
            pts = [(self.x + math.cos(rad) * 10, self.y + math.sin(rad) * 10), (self.x + math.cos(rad + 2.5) * 6, self.y + math.sin(rad + 2.5) * 6), (self.x + math.cos(rad - 2.5) * 6, self.y + math.sin(rad - 2.5) * 6)]
            pygame.draw.polygon(tela, self.cor, pts)
            pygame.draw.circle(tela, LARANJA_NEON, (int(self.x - math.cos(rad) * 5), int(self.y - math.sin(rad) * 5)), 3)
        else:
            glow = get_glow_surface(10, self.cor, 120)
            tela.blit(glow, (int(self.x - 10), int(self.y - 10)))
            pygame.draw.circle(tela, BRANCO, (int(self.x), int(self.y)), 3)


# Classe HardwareDefesa (Antigo Torre) representa os sistemas anti-malware do computador
class HardwareDefesa:
    def __init__(self, x, y, tipo):
        self.x, self.y, self.tipo = x, y, tipo
        self.p1, self.p2, self.p3 = 0, 0, 0
        self.cooldown = 0
        self.angulos = [0]
        self.angulos_alvo = [0]
        self.kills = 0
        self.anim_tick = 0
        self.mod_rate = 1.0
        self.mod_range = 1.0
        self.aura_camo = False
        self.stun_timer = 0
        self.alvo_laser = None
        self.atualizar_atributos()

    def atualizar_atributos(self):
        base = ATRIBUTOS_TORRE[self.tipo]
        self.dano, self.rate, self.range, self.cor = base["dano_base"], base["rate_base"], base["range_base"], base["cor"]
        self.detecta_camuflado, self.ignora_blindagem = False, False

        for path, lvl in [("p1", self.p1), ("p2", self.p2), ("p3", self.p3)]:
            for i in range(lvl):
                upg = base[path][i]
                self.dano += upg.get("dano", 0)
                self.rate += upg.get("rate", 0)
                self.range += upg.get("range", 0)
                if upg.get("camo"): self.detecta_camuflado = True
                if upg.get("ap"): self.ignora_blindagem = True

        self.rate = max(1, self.rate)
        
        # OTIMIZAÇÃO: Pré-cálculo do raio ao quadrado
        self.range_sq = self.range ** 2 
        
        velhos_angulos = self.angulos.copy()
        new_len = 3 if self.tipo == "railgun" and self.p1 >= 2 else (2 if self.tipo == "morteiro" and self.p2 >= 3 else (5 if self.tipo == "chaingun" and self.p1 >= 3 else 1))
        self.angulos = velhos_angulos[:new_len] + [0] * max(0, new_len - len(velhos_angulos))
        self.angulos_alvo = self.angulos.copy()
        self.gerar_textura_cano()

    def gerar_textura_cano(self):
        self.img_cano = pygame.Surface((90, 90), pygame.SRCALPHA)
        c = 45
        escala = 1.0 + (self.p1 + self.p2 + self.p3) * 0.05

        if self.tipo in ["overclock", "radar_quantico", "parede_holo", "minerador_cripto", "nuvem_nanobot"]: pass
        elif self.tipo == "railgun":
            pygame.draw.rect(self.img_cano, CINZA_METAL, (c - 5, c - 8, 35, 16), border_radius=3)
            pygame.draw.rect(self.img_cano, PRETO, (c + 5, c - 6, 25, 12))
            pygame.draw.line(self.img_cano, self.cor, (c + 5, c), (c + 30, c), 2)
        elif self.tipo == "chaingun":
            pygame.draw.rect(self.img_cano, CINZA_METAL, (c, c - 12, 35, 6), border_radius=2)
            pygame.draw.rect(self.img_cano, CINZA_METAL, (c, c + 6, 35, 6), border_radius=2)
            pygame.draw.rect(self.img_cano, PRETO, (c - 5, c - 14, 15, 28), border_radius=2)
        elif self.tipo in ["emissor_solar", "splash_plasma"]:
            pygame.draw.polygon(self.img_cano, CINZA_METAL, [(c - 5, c - 10), (c + 25, c - 12), (c + 35, c - 5), (c + 35, c + 5), (c + 25, c + 12), (c - 5, c + 10)])
            pygame.draw.polygon(self.img_cano, self.cor, [(c + 20, c - 8), (c + 32, c - 4), (c + 32, c + 4), (c + 20, c + 8)], 2)
            pygame.draw.circle(self.img_cano, BRANCO, (c + 28, c), 4)
        elif self.tipo in ["morteiro", "ataque_orbital"]:
            draw_hexagon(self.img_cano, PRETO, (c + 15, c), 18)
            draw_hexagon(self.img_cano, self.cor, (c + 15, c), 18, 2)
            pygame.draw.rect(self.img_cano, CINZA_METAL, (c - 10, c - 12, 20, 24), border_radius=4)
        elif self.tipo == "prisma_estase":
            pygame.draw.polygon(self.img_cano, BRANCO, [(c - 8, c), (c + 10, c - 15), (c + 40, c), (c + 10, c + 15)], 2)
            pygame.draw.polygon(self.img_cano, CINZA_METAL, [(c - 8, c), (c + 10, c - 10), (c + 30, c), (c + 10, c + 10)])
        elif self.tipo in ["sniper", "feixe_laser"]:
            pygame.draw.rect(self.img_cano, CINZA_METAL, (c - 10, c - 4, 55, 8), border_radius=2)
            pygame.draw.line(self.img_cano, self.cor, (c, c), (c + 50, c), 2)
            pygame.draw.circle(self.img_cano, CIANO, (c, c), 4)
        elif self.tipo in ["injetor_viral", "dreno_dados"]:
            pygame.draw.rect(self.img_cano, CINZA_METAL, (c, c - 12, 28, 24), border_radius=6)
            pygame.draw.rect(self.img_cano, self.cor, (c + 6, c - 6, 16, 12))
            pygame.draw.line(self.img_cano, PRETO, (c + 14, c - 6), (c + 14, c + 6), 2)
        elif self.tipo == "bobina_neural":
            pygame.draw.rect(self.img_cano, CINZA_METAL, (c - 8, c - 6, 16, 12), border_radius=2)
            pygame.draw.circle(self.img_cano, self.cor, (c + 20, c), 14, 2)
            pygame.draw.line(self.img_cano, self.cor, (c, c), (c + 16, c), 2)
        elif self.tipo == "teleguiado":
            pygame.draw.rect(self.img_cano, CINZA_METAL, (c - 10, c - 12, 20, 24), border_radius=4)
            pygame.draw.polygon(self.img_cano, self.cor, [(c + 5, c - 8), (c + 25, c), (c + 5, c + 8)])

        self.img_cano = pygame.transform.smoothscale(self.img_cano, (int(90 * escala), int(90 * escala)))

    def atacar(self, game):
        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.alvo_laser = None
            return
            
        if self.tipo == "minerador_cripto":
            if self.cooldown <= 0:
                if game.dificuldade_atual != "desafio":
                    game.dinheiro += self.dano
                    game.textos_flutuantes.append(TextoFlutuante(self.x, self.y - 20, f"+{self.dano} CR", DOURADO, fonte_pequena))
                else:
                    game.textos_flutuantes.append(TextoFlutuante(self.x, self.y - 20, "OFFLINE (0 CR)", VERMELHO_NEON, fonte_pequena))
                self.cooldown = self.rate * self.mod_rate
            if self.cooldown > 0: self.cooldown -= 1
            return

        if self.tipo in ["overclock", "radar_quantico", "parede_holo"]: return

        # OTIMIZAÇÃO: Usando valores pré-calculados e multiplicadores
        range_efetivo_sq = self.range_sq * (self.mod_range ** 2)
        rate_efetiva = self.rate * self.mod_rate
        alvos = []

        if self.tipo == "ataque_orbital":
            if self.cooldown <= 0 and game.malwares:
                mais_forte = max(game.malwares, key=lambda i: i.vida)
                game.pacotes.append(PacoteDados(self.x, self.y, mais_forte, self.dano, self.cor, self.tipo, self.ignora_blindagem))
                self.cooldown = rate_efetiva
            if self.cooldown > 0: self.cooldown -= 1
            return

        pode_ver_camo = self.detecta_camuflado or self.aura_camo

        for m in game.malwares:
            if m.alvo >= len(game.caminho_atual) or not m.ativo: continue
            if m.camuflado and not pode_ver_camo and not m.is_raid_boss: continue 

            # OTIMIZAÇÃO: Cálculo rápido de distância ao quadrado em vez de usar raiz
            dist_sq = (m.x - self.x)**2 + (m.y - self.y)**2
            if dist_sq <= range_efetivo_sq:
                progresso_calc = m.progresso
                if m.is_raid_boss: progresso_calc += 10000 # Prioriza o Raid Boss
                alvos.append((progresso_calc, m))

        alvos.sort(key=lambda x: x[0], reverse=True)
        alvos_validos = [item[1] for item in alvos[:len(self.angulos)]]
        
        if not alvos_validos:
            self.alvo_laser = None

        if alvos_validos:
            for idx, alvo in enumerate(alvos_validos):
                self.angulos_alvo[idx] = math.degrees(math.atan2(-(alvo.y - self.y), alvo.x - self.x))

        for i in range(len(self.angulos)):
            self.angulos[i] = lerp_angle(self.angulos[i], self.angulos_alvo[i], factor=0.25)

        if self.cooldown <= 0:
            atirou = False
            self.alvo_laser = None
            for idx, alvo in enumerate(alvos_validos):
                diff = abs((self.angulos_alvo[idx] - self.angulos[idx] + 180) % 360 - 180)
                if self.tipo == "feixe_laser":
                    if diff < 25:
                        if alvo.blindado and not self.ignora_blindagem: alvo.vida -= self.dano * 0.25
                        else: alvo.vida -= self.dano
                        self.alvo_laser = alvo
                        atirou = True
                elif self.tipo == "nuvem_nanobot":
                    if diff < 20:
                        game.pacotes.append(PacoteDados(self.x, self.y, alvo, self.dano, self.cor, self.tipo, self.ignora_blindagem))
                        atirou = True
                else:
                    if diff < 15:
                        game.pacotes.append(PacoteDados(self.x, self.y, alvo, self.dano, self.cor, self.tipo, self.ignora_blindagem))
                        atirou = True
            if atirou: self.cooldown = rate_efetiva

        if self.cooldown > 0: self.cooldown -= 1

    def desenhar(self, tela):
        self.anim_tick += 1
        escala = 1.0 + (self.p1 + self.p2 + self.p3) * 0.05
        r_base = int(24 * escala)

        if self.stun_timer > 0:
            pygame.draw.circle(tela, (255, 50, 50, 150), (int(self.x), int(self.y)), r_base + 5, 2)
            cor_atual = (100, 100, 100)
        else:
            cor_atual = self.cor

        draw_hexagon(tela, (0, 0, 0, 120), (int(self.x + 6), int(self.y + 6)), r_base)
        draw_hexagon(tela, CINZA_METAL, (int(self.x), int(self.y)), r_base)
        draw_hexagon(tela, CINZA, (int(self.x), int(self.y - 4)), r_base - 4)

        pygame.draw.circle(tela, cor_atual, (int(self.x), int(self.y - 4)), int(14 * escala), max(1, int(3 * escala)))
        pygame.draw.circle(tela, BRANCO, (int(self.x), int(self.y - 4)), int(6 * escala))

        if self.detecta_camuflado or self.aura_camo:
            pygame.draw.circle(tela, (50, 255, 50), (int(self.x), int(self.y)), int(r_base + 2), 1)

        if self.tipo in ["overclock", "radar_quantico", "parede_holo", "minerador_cripto", "nuvem_nanobot"]:
            rot = self.anim_tick * (2 if self.tipo != "minerador_cripto" else -1)
            draw_hexagon(tela, cor_atual, (int(self.x), int(self.y - 4)), int(18 * escala), 2, rotation=rot)
            if self.tipo == "minerador_cripto": desenhar_texto_sombra(tela, "CR", fonte_mini, DOURADO, (self.x, self.y - 4))
            elif self.tipo == "overclock": pygame.draw.circle(tela, BRANCO, (int(self.x), int(self.y - 4)), int(8 * escala), 1)
        else:
            for i in range(len(self.angulos)):
                rot = pygame.transform.rotozoom(self.img_cano, self.angulos[i], 1.0)
                if self.stun_timer > 0: rot.fill((100, 100, 100, 255), special_flags=pygame.BLEND_RGBA_MULT)
                tela.blit(rot, rot.get_rect(center=(int(self.x), int(self.y - 8))))
