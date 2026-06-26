# obd_manager.py
import obd
import threading
import time

class OBDManager:
    def __init__(self):
        self.connection = None
        self.is_running = False
        # Dicionário global de dados compartilhados
        self.dados = {
            "rpm": 0, "velocidade": 0, "coolant": 0,
            "throttle": 0, "voltage": 0.0, "stft": 0, "ltft": 0,
            "iat": 0, "ventoinha": "Desligada", "consumo": 0.0,
            "conectado": False
        }
        self.temperatura_anterior = 90

    def conectar(self, porta_com):
        """Inicia a conexão com o scanner em uma Thread separada"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._loop_leitura, args=(porta_com,), daemon=True)
            self.thread.start()

    def _loop_leitura(self, porta_com):
        print(f"[OBD] Tentando conectar na porta {porta_com}...")
        # Em testes reais com o carro, mude para fast=True para mais velocidade
        self.connection = obd.OBD(porta_com, fast=True) 
        
        if not self.connection.is_connected():
            print("[OBD] Falha na conexão física.")
            self.is_running = False
            return

        self.dados["conectado"] = True
        print("[OBD] Conectado à ECU com sucesso!")

        while self.is_running:
            try:
                # Consultas nativas da ECU
                res_rpm = self.connection.query(obd.commands.RPM)
                res_vel = self.connection.query(obd.commands.SPEED)
                res_temp = self.connection.query(obd.commands.COOLANT_TEMP)
                res_th = self.connection.query(obd.commands.THROTTLE_POS)
                res_volt = self.connection.query(obd.commands.CONTROL_MODULE_VOLTAGE)
                res_stft = self.connection.query(obd.commands.SHORT_TERM_FUEL_TRIM_1)
                res_ltft = self.connection.query(obd.commands.LONG_TERM_FUEL_TRIM_1)
                res_iat = self.connection.query(obd.commands.INTAKE_AIR_TEMP)

                # Atualiza os dados brutos se não forem nulos
                self.dados["rpm"] = int(res_rpm.value.magnitude) if not res_rpm.is_null() else 0
                self.dados["velocidade"] = int(res_vel.value.magnitude) if not res_vel.is_null() else 0
                self.dados["coolant"] = int(res_temp.value.magnitude) if not res_temp.is_null() else 0
                self.dados["throttle"] = int(res_th.value.magnitude) if not res_th.is_null() else 0
                self.dados["voltage"] = float(res_volt.value.magnitude) if not res_volt.is_null() else 0.0
                self.dados["stft"] = int(res_stft.value.magnitude) if not res_stft.is_null() else 0
                self.dados["ltft"] = int(res_ltft.value.magnitude) if not res_ltft.is_null() else 0
                self.dados["iat"] = int(res_iat.value.magnitude) if not res_iat.is_null() else 0

                # --- ENGENHARIA DE SOFTWARE: CÁLCULO DA VENTOINHA ---
                variacao = self.dados["coolant"] - self.temperatura_anterior
                if self.dados["velocidade"] == 0:
                    if variacao < -0.4:
                        self.dados["ventoinha"] = "LIGADA (Resfriando)"
                    elif self.dados["coolant"] >= 100:
                        self.dados["ventoinha"] = "CRÍTICA (Esperada)"
                    else:
                        self.dados["ventoinha"] = "Desligada"
                else:
                    self.dados["ventoinha"] = "Fluxo de Ar Natural" if variacao < 0 else "Desligada"
                
                self.temperatura_anterior = self.dados["coolant"]

                # --- SIMULAÇÃO DE CONSUMO INSTANTÂNEO BÁSICO ---
                if self.dados["velocidade"] > 0 and self.dados["rpm"] > 0:
                    # Fórmula matemática fictícia baseada em RPM/Velocidade para preencher o painel
                    self.dados["consumo"] = (self.dados["velocidade"] * 150) / self.dados["rpm"]
                else:
                    self.dados["consumo"] = 0.0

                time.sleep(0.1) # Taxa de amostragem (100ms)

            except Exception as e:
                print(f"[OBD] Erro no loop: {e}")
                self.dados["conectado"] = False
                self.is_running = False

    def ler_erros_dtc(self):
        """Busca erros na memória da injeção (DTCs)"""
        if self.connection and self.connection.is_connected():
            erros = self.connection.get_current_dtc()
            # Retorna uma lista de tuplas (Código, Descrição)
            return erros if erros else []
        return None

    def apagar_erros_dtc(self):
        """Envia o comando de reset para apagar a luz da injeção"""
        if self.connection and self.connection.is_connected():
            return self.connection.clear_dtc()
        return False