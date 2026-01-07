import sys
import os
import subprocess 
import webbrowser
import time
import math
import traceback
import ctypes # Adicionado para suporte a multi-monitor

# --- FUNÇÃO DE AUTO-REPARO ---
def repair_environment():
    print("\n⚠️ INICIANDO PROTOCOLO DE AUTO-REPARO ⚠️")
    print("O script detectou que sua instalação do MediaPipe está corrompida.")
    print("Vamos limpar tudo e reinstalar as versões corretas automaticamente.\n")
    
    confirm = input("Digite 'S' para confirmar e iniciar o reparo (ou qualquer outra tecla para sair): ")
    if confirm.upper() != 'S':
        print("Reparo cancelado. Saindo...")
        sys.exit(1)

    print("\n[1/3] Desinstalando versões conflitantes...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "mediapipe", "protobuf"])
    except subprocess.CalledProcessError:
        print("Aviso: Falha parcial na desinstalação. Tentando continuar...")
    
    print("\n[2/3] Instalando versões estáveis (MediaPipe 0.10.9 + Protobuf 3.20.3)...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "--user", "--upgrade", "--force-reinstall",
            "mediapipe==0.10.9", "protobuf==3.20.3"
        ])
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERRO FATAL NO PIP: {e}")
        print("Tente rodar o terminal como Administrador ou use o comando manualmente:")
        print("pip install mediapipe==0.10.9 protobuf==3.20.3 --user")
        sys.exit(1)
    
    print("\n[3/3] Verificando instalação...")
    try:
        import mediapipe
        print("✅ Instalação concluída!")
        print("\n========================================================")
        print("REPARO FINALIZADO. POR FAVOR, RODE ESTE SCRIPT NOVAMENTE.")
        print("========================================================\n")
    except ImportError:
        print("❌ O reparo falhou. Tente instalar o Visual C++ Redistributable manualmente.")
    
    input("Pressione ENTER para fechar...")
    sys.exit(0)

# --- DEBUG DE IMPORTAÇÃO (Diagnóstico Real) ---
print("--- Iniciando Diagnóstico de Importação ---")
mp_face_mesh = None
mp_drawing = None
mp_drawing_styles = None
mp = None

try:
    import mediapipe as mp
    print(f"MediaPipe base importado: {mp.__file__}")
except ImportError as e:
    print(f"ERRO FATAL: Não foi possível importar 'mediapipe'. Causa: {e}")
    repair_environment() 

errors = []

try:
    if hasattr(mp, 'solutions'):
        mp_face_mesh = mp.solutions.face_mesh
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        print("SUCESSO: mp.solutions carregado via atributo padrão.")
    else:
        errors.append("mp.solutions não existe no objeto mediapipe.")
except Exception as e:
    errors.append(f"Erro ao acessar mp.solutions: {e}")

if mp_face_mesh is None:
    try:
        from mediapipe.solutions import face_mesh
        from mediapipe.solutions import drawing_utils
        from mediapipe.solutions import drawing_styles
        
        mp_face_mesh = face_mesh
        mp_drawing = drawing_utils
        mp_drawing_styles = drawing_styles
        print("SUCESSO: Carregado via 'from mediapipe.solutions import ...'")
    except Exception as e:
        errors.append(f"Erro na importação direta (Tentativa 2): {e}")

if mp_face_mesh is None:
    try:
        import mediapipe.python.solutions.face_mesh as mp_face_mesh
        import mediapipe.python.solutions.drawing_utils as mp_drawing
        import mediapipe.python.solutions.drawing_styles as mp_drawing_styles
        print("SUCESSO: Carregado via caminho legado (mediapipe.python.solutions).")
    except Exception as e:
        errors.append(f"Erro no caminho legado (Tentativa 3): {e}")

if mp_face_mesh is None:
    print("\n================================================================")
    print("❌ FALHA TOTAL DE CARREGAMENTO ❌")
    print("DETALHES DOS ERROS:")
    for i, err in enumerate(errors):
        print(f"  [{i+1}] {err}")
    print("================================================================\n")
    repair_environment()

if not hasattr(mp, 'solutions') or mp.solutions is None:
    class Solutions: pass
    mp.solutions = Solutions()
    mp.solutions.face_mesh = mp_face_mesh
    mp.solutions.drawing_utils = mp_drawing
    mp.solutions.drawing_styles = mp_drawing_styles

print("--- Importação Concluída com Sucesso ---\n")

print("Carregando bibliotecas de visão e automação...")
try:
    import cv2
    import pyautogui
    import numpy as np
except ImportError as e:
    print(f"\nERRO: Falta uma biblioteca essencial ({e}).")
    print("Rode: pip install opencv-python pyautogui numpy")
    sys.exit(1)

# ---------------------------------------

# --- CONFIGURAÇÕES GLOBAIS ---
class Config:
    # --- SUPORTE MULTI-MONITOR ---
    try:
        # Usa a API do Windows para pegar o tamanho total da "Virtual Screen" (todos monitores)
        user32 = ctypes.windll.user32
        # SM_XVIRTUALSCREEN=76, SM_YVIRTUALSCREEN=77, SM_CXVIRTUALSCREEN=78, SM_CYVIRTUALSCREEN=79
        SCREEN_X = user32.GetSystemMetrics(76) # Posição X inicial (pode ser negativa)
        SCREEN_Y = user32.GetSystemMetrics(77) # Posição Y inicial
        SCREEN_W = user32.GetSystemMetrics(78) # Largura total combinada
        SCREEN_H = user32.GetSystemMetrics(79) # Altura total combinada
        print(f"Multi-Monitor Detectado: Origem({SCREEN_X},{SCREEN_Y}) Tamanho({SCREEN_W}x{SCREEN_H})")
    except Exception as e:
        # Fallback para monitor único se der erro
        print(f"Aviso: Detecção multi-monitor falhou ({e}). Usando padrão.")
        SCREEN_X, SCREEN_Y = 0, 0
        SCREEN_W, SCREEN_H = pyautogui.size()
    
    # Movimento e Rastreamento
    SENSITIVITY = 1.6        
    
    # SUAVIZAÇÃO DINÂMICA
    MIN_SMOOTHING = 0.04     
    MAX_SMOOTHING = 0.5      
    SMOOTHING_THRESHOLD = 80 
    
    DEAD_ZONE = 0.008        

    # Clique (Piscada)
    BLINK_RATIO_THRESHOLD = 0.013 
    LONG_BLINK_DURATION = 0.40     

    # Rolagem (Scroll)
    SCROLL_SPEED = 25             
    
    MOUTH_OPEN_THRESHOLD = 0.35    
    MOUTH_PUCKER_THRESHOLD = 0.30   
    
    # Cores (BGR)
    COLOR_HUD = (255, 200, 0)
    COLOR_BOX = (0, 255, 255)
    COLOR_TEXT = (255, 255, 255)
    COLOR_SCROLL = (255, 0, 255)

class HeadMouseController:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        
        print("Inicializando câmera (tentando DirectShow)...")
        self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if not self.cam.isOpened():
            print("DirectShow falhou. Tentando backend padrão...")
            self.cam = cv2.VideoCapture(0)
            
        if not self.cam.isOpened():
            print("\n========================================================")
            print("❌ ERRO CRÍTICO: Não foi possível acessar a webcam.")
            print("========================================================")
            print("Possíveis causas:")
            print("1. Outro programa está usando a câmera (Teams, Zoom, Discord, Navegador).")
            print("2. Permissão de câmera negada nas Configurações de Privacidade do Windows.")
            print("3. O índice da câmera está errado (tente mudar VideoCapture(0) para 1).")
            print("========================================================")
            sys.exit(1)
        
        self.prev_x, self.prev_y = 0, 0 
        self.curr_x, self.curr_y = 0, 0 
        
        self.left_blink_start = None
        self.right_blink_start = None
        self.left_clicked = False
        self.right_clicked = False
        
        self.paused = False

        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False

    def get_landmarks(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0].landmark
        return None

    def calculate_blink_ratio(self, landmarks, top_idx, bottom_idx, face_height):
        top = landmarks[top_idx]
        bottom = landmarks[bottom_idx]
        eye_openness = abs(top.y - bottom.y)
        ratio = eye_openness / face_height
        return ratio

    def calculate_mouth_open_ratio(self, landmarks, face_height):
        mouth_openness = abs(landmarks[13].y - landmarks[14].y)
        return mouth_openness / face_height

    def calculate_mouth_width_ratio(self, landmarks):
        mouth_width = math.hypot(landmarks[61].x - landmarks[291].x, landmarks[61].y - landmarks[291].y)
        face_width = math.hypot(landmarks[454].x - landmarks[234].x, landmarks[454].y - landmarks[234].y)
        
        if face_width == 0: return 0
        return mouth_width / face_width

    def process_scroll(self, landmarks, face_height, frame):
        if self.paused: return

        mouth_vertical = self.calculate_mouth_open_ratio(landmarks, face_height)
        mouth_horizontal = self.calculate_mouth_width_ratio(landmarks)
        
        h, w, _ = frame.shape
        center_x = int(w / 2)

        cv2.putText(frame, f"V:{mouth_vertical:.2f} H:{mouth_horizontal:.2f}", 
                   (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        if mouth_vertical > (Config.MOUTH_OPEN_THRESHOLD * 0.2): 
            pyautogui.scroll(-Config.SCROLL_SPEED)
            cv2.putText(frame, "SCROLL DOWN", (center_x - 80, h - 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, Config.COLOR_SCROLL, 2)
            cv2.circle(frame, (int(landmarks[14].x * w), int(landmarks[14].y * h)), 5, Config.COLOR_SCROLL, -1)

        elif mouth_horizontal < Config.MOUTH_PUCKER_THRESHOLD:
            pyautogui.scroll(Config.SCROLL_SPEED)
            cv2.putText(frame, "SCROLL UP", (center_x - 60, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, Config.COLOR_SCROLL, 2)
            cv2.circle(frame, (int(landmarks[13].x * w), int(landmarks[13].y * h)), 5, Config.COLOR_SCROLL, -1)

    def process_clicks(self, landmarks, face_height, frame):
        left_ratio = self.calculate_blink_ratio(landmarks, 159, 145, face_height)
        right_ratio = self.calculate_blink_ratio(landmarks, 386, 374, face_height)
        
        current_time = time.time()
        h, w, _ = frame.shape

        if left_ratio < Config.BLINK_RATIO_THRESHOLD:
            if self.left_blink_start is None:
                self.left_blink_start = current_time
            
            elapsed = current_time - self.left_blink_start
            progress = min(elapsed / Config.LONG_BLINK_DURATION, 1.0)
            
            cv2.rectangle(frame, (50, 50), (50 + int(100 * progress), 65), (0, 255, 0), -1)
            cv2.rectangle(frame, (50, 50), (150, 65), (255, 255, 255), 1)
            
            if elapsed > Config.LONG_BLINK_DURATION and not self.left_clicked:
                if not self.paused:
                    pyautogui.click(button='left')
                self.left_clicked = True
                cv2.putText(frame, "LEFT CLICK", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            self.left_blink_start = None
            self.left_clicked = False

        if right_ratio < Config.BLINK_RATIO_THRESHOLD:
            if self.right_blink_start is None:
                self.right_blink_start = current_time
            
            elapsed = current_time - self.right_blink_start
            progress = min(elapsed / Config.LONG_BLINK_DURATION, 1.0)
            
            start_x = w - 150
            cv2.rectangle(frame, (start_x, 50), (start_x + int(100 * progress), 65), (0, 0, 255), -1)
            cv2.rectangle(frame, (start_x, 50), (start_x + 100, 65), (255, 255, 255), 1)

            if elapsed > Config.LONG_BLINK_DURATION and not self.right_clicked:
                if not self.paused:
                    pyautogui.click(button='right')
                self.right_clicked = True
                cv2.putText(frame, "RIGHT CLICK", (start_x, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            self.right_blink_start = None
            self.right_clicked = False

    def move_mouse(self, landmarks, frame):
        if self.paused: return

        frame_h, frame_w, _ = frame.shape
        nose = landmarks[4] 
        
        offset = 0.25 / Config.SENSITIVITY
        min_x, max_x = 0.5 - offset, 0.5 + offset
        min_y, max_y = 0.5 - offset, 0.5 + offset
        
        cv2.rectangle(frame, 
                      (int(min_x * frame_w), int(min_y * frame_h)), 
                      (int(max_x * frame_w), int(max_y * frame_h)), 
                      Config.COLOR_BOX, 1)
        
        # --- ATUALIZAÇÃO PARA MULTI-MONITOR ---
        # Mapeia a posição do nariz para o espaço TOTAL (todas as telas combinadas)
        # O intervalo de saída agora é [SCREEN_X, SCREEN_X + SCREEN_W] em vez de [0, SCREEN_W]
        target_x = np.interp(nose.x, (min_x, max_x), (Config.SCREEN_X, Config.SCREEN_X + Config.SCREEN_W))
        target_y = np.interp(nose.y, (min_y, max_y), (Config.SCREEN_Y, Config.SCREEN_Y + Config.SCREEN_H))
        
        dist_move = math.hypot(target_x - self.prev_x, target_y - self.prev_y)
        if dist_move < (Config.SCREEN_W * Config.DEAD_ZONE):
            target_x = self.prev_x
            target_y = self.prev_y
            
        smoothing_factor = np.interp(dist_move, 
                                     [0, Config.SMOOTHING_THRESHOLD], 
                                     [Config.MIN_SMOOTHING, Config.MAX_SMOOTHING])
        
        self.curr_x = (target_x * smoothing_factor) + (self.prev_x * (1 - smoothing_factor))
        self.curr_y = (target_y * smoothing_factor) + (self.prev_y * (1 - smoothing_factor))
        
        pyautogui.moveTo(self.curr_x, self.curr_y)
        self.prev_x, self.prev_y = self.curr_x, self.curr_y

    def run(self):
        print("--- HeadMouse Pro Iniciado ---")
        print("Controles: [P] Pausar | [ESC] Sair")
        print("Olho Esq: Clique | Olho Dir: Clique Direito")
        print("Boca Aberta: Scroll Down | Biquinho: Scroll Up")

        while True:
            success, frame = self.cam.read()
            if not success: break
            
            frame = cv2.flip(frame, 1)
            landmarks = self.get_landmarks(frame)
            
            if landmarks:
                face_height = abs(landmarks[152].y - landmarks[10].y)
                
                self.process_clicks(landmarks, face_height, frame)
                self.process_scroll(landmarks, face_height, frame)
                self.move_mouse(landmarks, frame)
            
            if self.paused:
                cv2.putText(frame, "PAUSADO (P)", (int(frame.shape[1]/2)-100, int(frame.shape[0]/2)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

            cv2.imshow("HeadMouse Pro - Dynamic Tracking", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27: # ESC
                break
            elif key == ord('p'):
                self.paused = not self.paused

        self.cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    controller = HeadMouseController()
    controller.run()