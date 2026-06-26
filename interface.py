# interface.py
import customtkinter as ctk
import tkinter as tk
import math

class InterfaceGrafica(ctk.CTk):
    def __init__(self, obd_manager):
        super().__init__()
        self.obd = obd_manager

        # Configurações da Janela Principal
        self.title("PyOBD-Dashboard Avançado")
        self.geometry("1150x650")
        ctk.set_appearance_mode("dark")

        # Sistema de Abas (Tabs)
        self.abas = ctk.CTkTabview(self)
        self.abas.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_dash = self.abas.add("Dashboard em Tempo Real")
        self.tab_testes = self.abas.add("Testes Mecânicos")
        self.tab_erros = self.abas.add("Diagnóstico de Erros (DTC)")

        self._construir_dashboard()
        self._construir_testes()
        self._construir_erros()

        # Inicia o loop de atualização da tela (20 FPS)
        self.atualizar_widgets()

    def _construir_dashboard(self):
        """Monta o layout do painel principal"""
        self.tab_dash.grid_columnconfigure((0, 1, 2), weight=1)
        self.tab_dash.grid_rowconfigure((0, 1), weight=1)

        # 1. Painel RPM (Circular Analógico + Digital)
        self.f_rpm = ctk.CTkFrame(self.tab_dash)
        self.f_rpm.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.canvas_rpm = tk.Canvas(self.f_rpm, width=200, height=200, bg="#2b2b2b", highlightthickness=0)
        self.canvas_rpm.pack(pady=10)
        self.lbl_rpm_digital = ctk.CTkLabel(self.f_rpm, text="0\nRPM", font=("Arial", 20, "bold"))
        self.lbl_rpm_digital.place(in_=self.canvas_rpm, relx=0.5, rely=0.5, anchor="center")

        # 2. Painel Velocidade Real (Barra de Progresso)
        self.f_vel = ctk.CTkFrame(self.tab_dash)
        self.f_vel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.lbl_vel = ctk.CTkLabel(self.f_vel, text="0 km/h", font=("Arial", 38, "bold"))
        self.lbl_vel.pack(pady=30)
        self.barra_vel = ctk.CTkProgressBar(self.f_vel, progress_color="#00FF00", width=250, height=15)
        self.barra_vel.set(0)
        self.barra_vel.pack(pady=10)

        # 3. Painel Coolant Temp (Circular Analógico + Digital)
        self.f_temp = ctk.CTkFrame(self.tab_dash)
        self.f_temp.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        self.canvas_temp = tk.Canvas(self.f_temp, width=200, height=200, bg="#2b2b2b", highlightthickness=0)
        self.canvas_temp.pack(pady=10)
        self.lbl_temp_digital = ctk.CTkLabel(self.f_temp, text="0 °C\nÁgua", font=("Arial", 18, "bold"))
        self.lbl_temp_digital.place(in_=self.canvas_temp, relx=0.5, rely=0.5, anchor="center")

        # 4. Dados Brutos Inferiores (Throttle)
        self.f_th = ctk.CTkFrame(self.tab_dash)
        self.f_th.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.lbl_th = ctk.CTkLabel(self.f_th, text="Abertura Borboleta: 0%", font=("Arial", 16))
        self.lbl_th.pack(expand=True)

        # 5. Módulo Voltagem
        self.f_volt = ctk.CTkFrame(self.tab_dash)
        self.f_volt.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.lbl_volt = ctk.CTkLabel(self.f_volt, text="Tensão Bateria: 0.0V", font=("Arial", 16))
        self.lbl_volt.pack(expand=True)

        # 6. Misturas (STFT e LTFT)
        self.f_mist = ctk.CTkFrame(self.tab_dash)
        self.f_mist.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        self.lbl_stft = ctk.CTkLabel(self.f_mist, text="STFT (Curto Prazo): 0%", font=("Arial", 14))
        self.lbl_stft.pack(pady=10)
        self.lbl_ltft = ctk.CTkLabel(self.f_mist, text="LTFT (Longo Prazo): 0%", font=("Arial", 14))
        self.lbl_ltft.pack(pady=10)

        # 7. Barra Lateral Direita de Cálculos Deduzidos
        self.f_side = ctk.CTkFrame(self.tab_dash, width=180)
        self.f_side.grid(row=0, column=3, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.lbl_iat = ctk.CTkLabel(self.f_side, text="Temp Ar (IAT):\n0 °C", font=("Arial", 14))
        self.lbl_iat.pack(pady=30)
        self.lbl_vent = ctk.CTkLabel(self.f_side, text="Ventoinha:\nMonitorando...", font=("Arial", 14))
        self.lbl_vent.pack(pady=30)
        self.lbl_cons = ctk.CTkLabel(self.f_side, text="Consumo:\n0.0 km/L", font=("Arial", 14))
        self.lbl_cons.pack(pady=30)

    def _desenhar_ponteiro(self, canvas, valor, valor_max, cor_arco):
        """Desenha o arco analógico dinâmico no Canvas estilo painel digital"""
        canvas.delete("all")
        # Desenha o fundo cinza do círculo completo
        canvas.create_arc(15, 15, 185, 185, start=-225, extent=-270, style="arc", outline="#444444", width=8)
        
        # Mapeia o valor atual para a extensão do arco (limita ao máximo para não quebrar)
        porcentagem = min(valor / valor_max, 1.0)
        extensao_proporcional = -(porcentagem * 270)
        
        # Desenha a linha colorida que sobe conforme o motor responde
        canvas.create_arc(15, 15, 185, 185, start=-225, extent=extensao_proporcional, style="arc", outline=cor_arco, width=10)

    def _construir_testes(self):
        """Aba para os testes específicos (como a Termostática do Fox)"""
        lbl_info = ctk.CTkLabel(self.tab_testes, text="Centro de Testes Dinâmicos", font=("Arial", 20, "bold"))
        lbl_info.pack(pady=20)
        self.btn_teste_termo = ctk.CTkButton(self.tab_testes, text="Iniciar Monitor de Válvula Termostática", command=self._executar_teste_termo)
        self.btn_teste_termo.pack(pady=15)
        self.txt_resultado_teste = ctk.CTkTextbox(self.tab_testes, width=500, height=200)
        self.txt_resultado_teste.pack(pady=10)
        self.txt_resultado_teste.insert("0.0", "Aguardando início de rotina de teste...")

    def _construir_erros(self):
        """Aba focada no diagnóstico de injeção"""
        lbl_title = ctk.CTkLabel(self.tab_erros, text="Gerenciador de Erros da ECU (DTC)", font=("Arial", 20, "bold"))
        lbl_title.pack(pady=15)
        self.btn_ler = ctk.CTkButton(self.tab_erros, text="Escanear Erros na Injeção", fg_color="blue", command=self._acao_ler_erros)
        self.btn_ler.pack(pady=10)
        self.btn_limpar = ctk.CTkButton(self.tab_erros, text="Apagar Luz da Injeção (Limpar Memória)", fg_color="red", command=self._acao_limpar_erros)
        self.btn_limpar.pack(pady=10)
        self.txt_erros = ctk.CTkTextbox(self.tab_erros, width=600, height=250)
        self.txt_erros.pack(pady=15)

    def atualizar_widgets(self):
        """Puxa dados em tempo real do gerenciador OBD e move a interface gráfica"""
        dados = self.obd.dados
        
        if dados["conectado"]:
            # Atualiza os ponteiros circulares gráficos (Valor real, Valor máximo do mostrador, Cor da linha)
            self._desenhar_ponteiro(self.canvas_rpm, dados['rpm'], 6000, "#00BFFF")
            self._desenhar_ponteiro(self.canvas_temp, dados['coolant'], 120, "#FF4500")

            # Atualiza os textos digitais internos dos círculos
            self.lbl_rpm_digital.configure(text=f"{dados['rpm']}\nRPM")
            self.lbl_temp_digital.configure(text=f"{dados['coolant']} °C\nÁgua")

            # Atualiza o restante do painel
            self.lbl_vel.configure(text=f"{dados['velocidade']} km/h")
            self.lbl_th.configure(text=f"Abertura Borboleta: {dados['throttle']}%")
            self.lbl_volt.configure(text=f"Tensão Bateria: {dados['voltage']:.1f}V")
            self.lbl_stft.configure(text=f"STFT (Curto): {dados['stft']}%")
            self.lbl_ltft.configure(text=f"LTFT (Longo): {dados['ltft']}%")
            self.lbl_iat.configure(text=f"Temp Ar (IAT):\n{dados['iat']} °C")
            self.lbl_vent.configure(text=f"Ventoinha:\n{dados['ventoinha']}")
            self.lbl_cons.configure(text=f"Consumo:\n{dados['consumo']:.1f} km/L")
            self.barra_vel.set(dados['velocidade'] / 200)
        else:
            # Mostra estado offline caso o carro seja desligado
            self._desenhar_ponteiro(self.canvas_rpm, 0, 6000, "#444444")
            self._desenhar_ponteiro(self.canvas_temp, 0, 120, "#444444")
            self.lbl_rpm_digital.configure(text="OFF\nRPM")
            self.lbl_temp_digital.configure(text="OFF\nÁgua")

        # Repete a atualização a cada 50ms (Garante ponteiros fluidos)
        self.after(50, self.atualizar_widgets)

    def _executar_teste_termo(self):
        self.txt_resultado_teste.delete("0.0", "end")
        self.txt_resultado_teste.insert("0.0", "[Executando...] Monitorando comportamento térmico na rodovia.\n")

    def _acao_ler_erros(self):
        self.txt_erros.delete("0.0", "end")
        self.txt_erros.insert("0.0", "Buscando códigos de falha na ECU...\n")
        erros = self.obd.ler_erros_dtc()
        if erros is None:
            self.txt_erros.insert("end", "[ERRO] Scanner não está conectado ao veículo.")
        elif len(erros) == 0:
            self.txt_erros.insert("end", "[NENHUM ERRO] Nenhuma falha ativa encontrada na memória.")
        else:
            for cod, desc in erros:
                self.txt_erros.insert("end", f"Código: {cod} -> Descrição: {desc}\n")

    def _acao_limpar_erros(self):
        sucesso = self.obd.apagar_erros_dtc()
        self.txt_erros.delete("0.0", "end")
        if sucesso:
            self.txt_erros.insert("0.0", "[SUCESSO] Comando enviado! Memória limpa e Luz da Injeção desligada.")
        else:
            self.txt_erros.insert("0.0", "[FALHA] Não foi possível limpar os códigos.")