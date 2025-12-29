import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import math

# --- CONFIGURAÇÕES GLOBAIS ---
class Config:
    # Tela
    SCREEN_W, SCREEN_H = pyautogui.size()
    
    # Movimento e Rastreamento
    SENSITIVITY = 1.6        # Sensibilidade (Maior = Menos movimento de cabeça necessário)
    
    # SUAVIZAÇÃO DINÂMICA (Ajuste Fino)
    # Se mover devagar -> Usa MIN (Alta precisão/Lento)
    # Se mover rápido -> Usa MAX (Alta resposta/Rápido)
    MIN_SMOOTHING = 0.04     # Muito suave (para clicar em botões pequenos)
    MAX_SMOOTHING = 0.5      # Rápido (para atravessar a tela)
    SMOOTHING_THRESHOLD = 80 # Distância em pixels para ativar a velocidade máxima
    
    DEAD_ZONE = 0.002        # Zona morta para ignorar micro-tremores (respiração)
    
    # Clique (Piscada)
    BLINK_RATIO_THRESHOLD = 0.022 
    LONG_BLINK_DURATION = 0.30     # Aumentei levemente para evitar falsos positivos com a nova suavização

    # Rolagem (Scroll)
    SCROLL_SPEED = 25             
    
    # SCROLL DOWN: Boca Aberta (Vertical)
    MOUTH_OPEN_THRESHOLD = 0.35    
    
    # SCROLL UP: Biquinho (Horizontal)
    MOUTH_PUCKER_THRESHOLD = 0.30   
    
    # Cores (BGR)
    COLOR_HUD = (255, 200, 0)
    COLOR_BOX = (0, 255, 255)
    COLOR_TEXT = (255, 255, 255)
    COLOR_SCROLL = (255, 0, 255)

class HeadMouseController:
    def __init__(self):
        # Inicializa MediaPipe com configurações otimizadas
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.8, # Aumentei confiança para evitar perda de tracking
            min_tracking_confidence=0.8
        )
        self.cam = cv2.VideoCapture(0)
        
        # Variáveis de Estado
        self.prev_x, self.prev_y = 0, 0 
        self.curr_x, self.curr_y = 0, 0 
        
        # Temporizadores de Clique
        self.left_blink_start = None
        self.right_blink_start = None
        self.left_clicked = False
        self.right_clicked = False
        
        # Estado do Sistema
        self.paused = False

        # Configurações do PyAutoGUI
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False

    def get_landmarks(self, frame):
        """Processa o frame e retorna os landmarks."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0].landmark
        return None

    def calculate_blink_ratio(self, landmarks, top_idx, bottom_idx, face_height):
        """Calcula a abertura do olho relativa ao tamanho do rosto."""
        top = landmarks[top_idx]
        bottom = landmarks[bottom_idx]
        eye_openness = abs(top.y - bottom.y)
        ratio = eye_openness / face_height
        return ratio

    def calculate_mouth_open_ratio(self, landmarks, face_height):
        """Calcula abertura VERTICAL da boca (para Scroll Down)."""
        # 13: Lábio superior, 14: Lábio inferior
        mouth_openness = abs(landmarks[13].y - landmarks[14].y)
        return mouth_openness / face_height

    def calculate_mouth_width_ratio(self, landmarks):
        """Calcula abertura HORIZONTAL da boca (para Scroll Up/Biquinho)."""
        # 61: Canto esquerdo, 291: Canto direito
        # 454: Extrema direita rosto, 234: Extrema esquerda rosto
        mouth_width = math.hypot(landmarks[61].x - landmarks[291].x, landmarks[61].y - landmarks[291].y)
        face_width = math.hypot(landmarks[454].x - landmarks[234].x, landmarks[454].y - landmarks[234].y)
        
        if face_width == 0: return 0
        return mouth_width / face_width

    def process_scroll(self, landmarks, face_height, frame):
        """Gerencia rolagem baseada em Boca Aberta (Descer) e Biquinho (Subir)."""
        if self.paused: return

        # Métricas
        mouth_vertical = self.calculate_mouth_open_ratio(landmarks, face_height)
        mouth_horizontal = self.calculate_mouth_width_ratio(landmarks)
        
        h, w, _ = frame.shape
        center_x = int(w / 2)

        # Debug Visual Discreto
        cv2.putText(frame, f"V:{mouth_vertical:.2f} H:{mouth_horizontal:.2f}", 
                   (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        # Scroll Down (Boca Aberta)
        if mouth_vertical > (Config.MOUTH_OPEN_THRESHOLD * 0.2): 
            pyautogui.scroll(-Config.SCROLL_SPEED)
            cv2.putText(frame, "SCROLL DOWN", (center_x - 80, h - 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, Config.COLOR_SCROLL, 2)
            cv2.circle(frame, (int(landmarks[14].x * w), int(landmarks[14].y * h)), 5, Config.COLOR_SCROLL, -1)

        # Scroll Up (Biquinho)
        elif mouth_horizontal < Config.MOUTH_PUCKER_THRESHOLD:
            pyautogui.scroll(Config.SCROLL_SPEED)
            cv2.putText(frame, "SCROLL UP", (center_x - 60, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, Config.COLOR_SCROLL, 2)
            cv2.circle(frame, (int(landmarks[13].x * w), int(landmarks[13].y * h)), 5, Config.COLOR_SCROLL, -1)

    def process_clicks(self, landmarks, face_height, frame):
        """Gerencia lógica de cliques com timer e feedback visual."""
        
        left_ratio = self.calculate_blink_ratio(landmarks, 159, 145, face_height)
        right_ratio = self.calculate_blink_ratio(landmarks, 386, 374, face_height)
        
        current_time = time.time()
        h, w, _ = frame.shape

        # --- Olho Esquerdo ---
        if left_ratio < Config.BLINK_RATIO_THRESHOLD:
            if self.left_blink_start is None:
                self.left_blink_start = current_time
            
            elapsed = current_time - self.left_blink_start
            progress = min(elapsed / Config.LONG_BLINK_DURATION, 1.0)
            
            # Barra de Progresso
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

        # --- Olho Direito ---
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
        """Calcula posição e move o mouse com suavização dinâmica."""
        if self.paused: return

        frame_h, frame_w, _ = frame.shape
        nose = landmarks[4] 
        
        # 1. Definir Active Zone
        offset = 0.25 / Config.SENSITIVITY
        min_x, max_x = 0.5 - offset, 0.5 + offset
        min_y, max_y = 0.5 - offset, 0.5 + offset
        
        # HUD: Caixa de Controle
        cv2.rectangle(frame, 
                      (int(min_x * frame_w), int(min_y * frame_h)), 
                      (int(max_x * frame_w), int(max_y * frame_h)), 
                      Config.COLOR_BOX, 1)
        
        # 2. Mapeamento Linear
        target_x = np.interp(nose.x, (min_x, max_x), (0, Config.SCREEN_W))
        target_y = np.interp(nose.y, (min_y, max_y), (0, Config.SCREEN_H))
        
        # 3. Dead Zone
        dist_move = math.hypot(target_x - self.prev_x, target_y - self.prev_y)
        if dist_move < (Config.SCREEN_W * Config.DEAD_ZONE):
            target_x = self.prev_x
            target_y = self.prev_y
            
        # 4. Suavização Dinâmica (A GRANDE MELHORIA)
        # Calcula a velocidade do movimento (distância desde o último frame)
        # Se moveu muito (rápido) -> Usa MAX_SMOOTHING (ex: 0.5) para resposta rápida
        # Se moveu pouco (lento)  -> Usa MIN_SMOOTHING (ex: 0.04) para precisão
        
        # Interpolação do fator de suavização baseada na velocidade
        smoothing_factor = np.interp(dist_move, 
                                     [0, Config.SMOOTHING_THRESHOLD], 
                                     [Config.MIN_SMOOTHING, Config.MAX_SMOOTHING])
        
        # Aplica a suavização variável
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
                # Altura do rosto para normalizar cálculos
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