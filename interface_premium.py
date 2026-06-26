# interface_premium.py
import pygame
import sys

# Inicialização do Pygame e Fontes
pygame.init()
pygame.font.init()

# Janela estendida para os 4 gauges grandes
LARGURA, ALTURA = 1300, 720
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("PyOBD Professional Cockpit Dashboard")
relogio = pygame.time.Clock()

# Paleta de Cores
COR_FUNDO = (20, 20, 20)
COR_TEXTO = (240, 240, 240)
COR_DIGITAL_V = (255, 0, 0)     # Vermelho sólido puro para leitura rápida
COR_GRAFITE = (40, 40, 40)
COR_BORBOLETA = (0, 191, 255)  
COR_STFT = (255, 140, 0)       
COR_LTFT = (255, 69, 0)        
COR_VALORES = (0, 255, 0)       # Verde para os textos simples abaixo

# Definição das Fontes
fonte_digital = pygame.font.SysFont("Consolas", 26, bold=True)
fonte_labels = pygame.font.SysFont("Arial", 16, bold=True)
fonte_valores = pygame.font.SysFont("Arial", 20, bold=False)

# --- MATERIAL GRÁFICO (ASSETS) ---
def carregar_imagem(caminho, tamanho):
    img = pygame.image.load(caminho).convert_alpha()
    return pygame.transform.scale(img, tamanho)

# Todos os 4 gauges simétricos (240x240)
gauge_rpm = carregar_imagem("assets/gauge_rpm.png", (240, 240))
gauge_vel = carregar_imagem("assets/gauge_velocidade.png", (240, 240))
gauge_temp = carregar_imagem("assets/gauge_coolant.png", (240, 240))
gauge_bat = carregar_imagem("assets/gauge_bateria.png", (240, 240))
agulha_img = carregar_imagem("assets/ponteiro.png", (20, 110))

def renderizar_ponteiro(surface_tela, img_agulha, angulo, centro):
    img_rotacionada = pygame.transform.rotate(img_agulha, -angulo)
    retangulo_rotacionado = img_rotacionada.get_rect(center=centro)
    surface_tela.blit(img_rotacionada, retangulo_rotacionado)

# --- BARRAS VERTICAIS LOGITECH G29 ---
def desenhar_barra_segmentada_vertical(surface, x, y, w, h, valor, valor_max, cor_ativa, total_linhas=45):
    espessura_linha = 2
    espacamento = (h / total_linhas)
    for i in range(total_linhas):
        porcentagem_linha = ((total_linhas - i) / total_linhas) * valor_max
        cor = cor_ativa if valor >= porcentagem_linha else COR_GRAFITE
        pos_y = y + (i * espacamento)
        pygame.draw.line(surface, cor, (x, pos_y), (x + w, pos_y), espessura_linha)

# Dados de Teste Dinâmico
dados_carro = {
    "rpm": 0, "velocidade": 0, "coolant": 0,
    "throttle": 0, "voltage": 12.0, "stft": 0, "ltft": 0,
    "iat": 24, "ventoinha": "Desligada", "consumo": 11.4
}
subindo = True

# ===== LOOP PRINCIPAL DE EXECUÇÃO =====
while True:
    tela.fill(COR_FUNDO)
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Simulador Mecânico
    if subindo:
        dados_carro["rpm"] += 45
        dados_carro["velocidade"] += 1
        dados_carro["coolant"] = min(dados_carro["coolant"] + 1, 95)
        dados_carro["throttle"] = min(dados_carro["throttle"] + 1, 100)
        dados_carro["voltage"] = min(dados_carro["voltage"] + 0.02, 14.2)
        dados_carro["stft"] = min(dados_carro['stft'] + 1, 15)
        dados_carro["ltft"] = min(dados_carro['ltft'] + 1, 8)
        if dados_carro["velocidade"] >= 180: subindo = False
    else:
        dados_carro["rpm"] -= 60
        dados_carro["velocidade"] -= 1.5
        dados_carro["throttle"] = max(dados_carro["throttle"] - 2, 12)
        dados_carro["voltage"] = max(dados_carro["voltage"] - 0.03, 12.4)
        if dados_carro["velocidade"] <= 0: subindo = True

    # =========================================================================
    # LINHA 1: MANÔMETROS ANALÓGICOS (VALORES ENQUADRADOS NAS CAIXAS)
    # =========================================================================
    y_linha1 = 160
    
    # 1. RPM (0 a 9000)
    c_rpm = (160, y_linha1)
    ang_rpm = -135 + (dados_carro["rpm"] / 9000.0) * 270.0
    tela.blit(gauge_rpm, gauge_rpm.get_rect(center=c_rpm))
    renderizar_ponteiro(tela, agulha_img, ang_rpm, c_rpm)
    
    txt_rpm = fonte_digital.render(f"{dados_carro['rpm']}", True, COR_DIGITAL_V)
    tela.blit(txt_rpm, txt_rpm.get_rect(center=(c_rpm[0], c_rpm[1] + 62)))

    # 2. VELOCIDADE (0 a 200)
    c_vel = (490, y_linha1)
    ang_vel = -135 + (dados_carro["velocidade"] / 200.0) * 270.0
    tela.blit(gauge_vel, gauge_vel.get_rect(center=c_vel))
    renderizar_ponteiro(tela, agulha_img, ang_vel, c_vel)
    
    txt_vel = fonte_digital.render(f"{int(dados_carro['velocidade'])}", True, COR_DIGITAL_V)
    tela.blit(txt_vel, txt_vel.get_rect(center=(c_vel[0], c_vel[1] + 62)))

    # 3. TEMPERATURA DA ÁGUA (0 a 180)
    c_temp = (820, y_linha1)
    ang_temp = -135 + (dados_carro["coolant"] / 180.0) * 270.0
    tela.blit(gauge_temp, gauge_temp.get_rect(center=c_temp))
    renderizar_ponteiro(tela, agulha_img, ang_temp, c_temp)
    
    txt_temp = fonte_digital.render(f"{dados_carro['coolant']}", True, COR_DIGITAL_V)
    tela.blit(txt_temp, txt_temp.get_rect(center=(c_temp[0], c_temp[1] + 62)))

    # 4. TENSÃO DA BATERIA (0 a 16V)
    c_bat = (1140, y_linha1)
    ang_bat = -135 + (dados_carro["voltage"] / 16.0) * 270.0
    tela.blit(gauge_bat, gauge_bat.get_rect(center=c_bat))
    renderizar_ponteiro(tela, agulha_img, ang_bat, c_bat)
    
    txt_bat = fonte_digital.render(f"{dados_carro['voltage']:.1f}", True, COR_DIGITAL_V)
    tela.blit(txt_bat, txt_bat.get_rect(center=(c_bat[0], c_bat[1] + 62)))


    # =========================================================================
    # LINHA 2: COLUNAS VERTICIAIS (LOGITECH G29) LADO A LADO
    # =========================================================================
    y_linha2 = 450
    h_barras = 180
    w_barras = 55
    
    # Abertura da Borboleta
    x_borb = 100
    desenhar_barra_segmentada_vertical(tela, x_borb, y_linha2, w_barras, h_barras, dados_carro["throttle"], 100, COR_BORBOLETA)
    tela.blit(fonte_labels.render("Borboleta", True, COR_TEXTO), (x_borb - 5, y_linha2 - 30))
    val_th = fonte_valores.render(f"{dados_carro['throttle']}%", True, COR_TEXTO)
    tela.blit(val_th, val_th.get_rect(center=(x_borb + (w_barras // 2), y_linha2 + h_barras + 20)))

    # STF Curto Prazo
    x_stft = 290
    desenhar_barra_segmentada_vertical(tela, x_stft, y_linha2, w_barras, h_barras, dados_carro["stft"], 30, COR_STFT)
    tela.blit(fonte_labels.render("STF Curto", True, COR_TEXTO), (x_stft - 3, y_linha2 - 30))
    val_stft = fonte_valores.render(f"{dados_carro['stft']}%", True, COR_TEXTO)
    tela.blit(val_stft, val_stft.get_rect(center=(x_stft + (w_barras // 2), y_linha2 + h_barras + 20)))

    # STF Longo Prazo
    x_ltft = 480
    desenhar_barra_segmentada_vertical(tela, x_ltft, y_linha2, w_barras, h_barras, dados_carro["ltft"], 30, COR_LTFT)
    tela.blit(fonte_labels.render("STF Longo", True, COR_TEXTO), (x_ltft - 5, y_linha2 - 30))
    val_ltft = fonte_valores.render(f"{dados_carro['ltft']}%", True, COR_TEXTO)
    tela.blit(val_ltft, val_ltft.get_rect(center=(x_ltft + (w_barras // 2), y_linha2 + h_barras + 20)))


    # =========================================================================
    # INFORMAÇÕES DIGITAIS DE TEXTO (BASE INFERIOR DIREITA)
    # =========================================================================
    x_info = 820
    
    # Caixa Temp Ar
    tela.blit(fonte_labels.render("🌡️ Temp Ar", True, COR_TEXTO), (x_info, y_linha2))
    tela.blit(fonte_valores.render(f"{dados_carro['iat']} °C", True, COR_VALORES), (x_info, y_linha2 + 25))

    # Caixa Ventoinha
    tela.blit(fonte_labels.render("🌀 Ventoinha", True, COR_TEXTO), (x_info + 160, y_linha2))
    tela.blit(fonte_valores.render(f"{dados_carro['ventoinha']}", True, COR_VALORES), (x_info + 160, y_linha2 + 25))

    # Caixa Consumo
    tela.blit(fonte_labels.render("⛽ Consumo", True, COR_TEXTO), (x_info + 320, y_linha2))
    tela.blit(fonte_valores.render(f"{dados_carro['consumo']:.1f} Km/l", True, COR_VALORES), (x_info + 320, y_linha2 + 25))

    # Atualização da Tela
    pygame.display.flip()
    relogio.tick(60)