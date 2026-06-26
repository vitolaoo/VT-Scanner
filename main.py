# main.py
from obd_manager import OBDManager
from interface import InterfaceGrafica

if __name__ == "__main__":
    # 1. Inicializa o motor de dados OBD em segundo plano
    gerenciador_obd = OBDManager()
    
    # 2. Defina a porta COM do seu scanner (Ex: Windows "COM3", Linux "/dev/rfcomm0")
    # Para o seu teste prático inicial no carro, mude para a porta real pareada
    PORTA_SCANNER = "COM3"
    gerenciador_obd.conectar(PORTA_SCANNER)
    
    # 3. Inicializa e abre a interface gráfica CustomTkinter
    app = InterfaceGrafica(gerenciador_obd)
    app.mainloop()