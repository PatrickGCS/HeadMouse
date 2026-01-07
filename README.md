
# HeadMouse Pro 🖱️👀

Um controlador de mouse "hands-free" de alta precisão que utiliza Visão Computacional (MediaPipe) para rastrear movimentos da cabeça e expressões faciais.

O sistema possui **suavização dinâmica** (rápido para movimentos longos, cirúrgico para cliques pequenos) e suporte a múltiplos monitores.

## ✨ Funcionalidades

* **Rastreamento de Cabeça:** O cursor segue o movimento do seu nariz.
* **Cliques Oculares:** Pisque (segure levemente) para clicar.
  * 👁️ Olho Esquerdo: Clique Esquerdo
  * 👁️ Olho Direito: Clique Direito
* **Rolagem Facial (Scroll):**
  * 😮 **Boca Aberta:** Rola para BAIXO.
  * 😗 **Biquinho:** Rola para CIMA.
* **Modo Pausa:** Tecla `P` para congelar o mouse.

## 🚀 Instalação (Passo a Passo)

Para evitar erros de conflito entre bibliotecas (comum no Windows), siga exatamente estes passos.

### 1. Pré-requisitos

* **Python:** Recomenda-se a versão **3.10** ou **3.11** . (Versões 3.12+ ou muito antigas podem dar erro no MediaPipe).
* **Visual C++ Redistributable:** OBRIGATÓRIO no Windows.
  * Se o programa não abrir ou der erro de DLL, [Baixe e Instale o vc_redist.x64.exe aqui](https://www.google.com/search?q=https://aka.ms/vs/17/release/vc_redist.x64.exe "null").

### 2. Instalando as Bibliotecas (Versões Corretas)

Abra seu terminal/PowerShell na pasta do projeto e execute este comando exato (ele garante que o `protobuf` e `numpy` não quebrem o `mediapipe`):

```
pip install "numpy<2" "protobuf<3.20.3" mediapipe==0.10.9 opencv-python pyautogui

```

*Nota: As aspas são importantes no PowerShell para interpretar os sinais de `<`.*

### 3. Executando

Execute o script principal:

```
python rastreador.py

```

## 🎮 Guia de Uso

1. **A Calibração:** Ao iniciar, você verá sua webcam com um **retângulo ciano** . Mantenha a cabeça dentro dele.
2. **Mover o Mouse:** Aponte seu nariz para as bordas desse retângulo para alcançar os cantos da sua tela.
3. **Clicar:** Feche um olho e segure por **0.3 segundos** . Uma barra de progresso aparecerá. Quando encher, o clique ocorre.
4. **Rolagem (Scroll):**
   * **Descer:** Abra a boca (verticalmente).
   * **Subir:** Faça um biquinho (junte os lábios horizontalmente).
   * *Dica:* Olhe os números `V:` (Vertical) e `H:` (Horizontal) na parte inferior da tela para entender seus limites.

## ⚙️ Ajustes Finos (Configuração)

Para personalizar a sensibilidade para o seu rosto e ambiente, abra o arquivo `rastreador.py` (ou `head_mouse_pro.py`) em um editor de texto e altere os valores dentro da classe `Config` (logo no início do arquivo).

### 🕹️ Movimento do Mouse

* `SENSITIVITY` (Padrão: 1.6):
  * **Aumente** (ex: 2.0) se quiser mover *menos* a cabeça para atravessar a tela.
  * **Diminua** (ex: 1.2) se quiser mais precisão e uma área de movimento maior.
* `DEAD_ZONE` (Padrão: 0.002):
  * Define o quanto você pode tremer ou respirar sem que o mouse se mexa. Aumente se o mouse estiver tremendo muito quando parado.

### 🖱️ Cliques (Piscada)

* `LONG_BLINK_DURATION` (Padrão: 0.30):
  * Tempo em segundos que o olho deve ficar fechado.
  * Diminua para cliques mais rápidos (cuidado com piscadas naturais).
  * Aumente para evitar cliques acidentais.
* `BLINK_RATIO_THRESHOLD` (Padrão: 0.022):
  * Define o quão fechado o olho deve estar. Se você tem olhos naturalmente mais fechados, aumente levemente este valor.

### 📜 Rolagem (Scroll)

Use os números de debug (`V` e `H`) que aparecem na janela da câmera como referência.

* `MOUTH_OPEN_THRESHOLD` (Para descer):
  * Se a página desce sozinha quando você fala, **aumente** este valor.
* `MOUTH_PUCKER_THRESHOLD` (Para subir):
  * Se a página sobe sozinha, **diminua** este valor.
  * Se for difícil subir, **aumente** este valor.

## 🛠️ Solução de Problemas Comuns

* **Erro `AttributeError: module 'mediapipe' has no attribute 'solutions'`:**
  * Isso significa conflito de versão. Rode o comando de instalação do passo 2 novamente com `--force-reinstall`.
* **Erro `ImportError: DLL load failed`:**
  * Falta o Visual C++. Instale o link mencionado nos pré-requisitos e reinicie o PC.
* **Câmera não abre:**
  * Verifique se o Teams/Zoom não está usando a câmera.
  * Verifique as permissões de privacidade do Windows

Um controlador de mouse "hands-free" de alta precisão que utiliza Visão Computacional (MediaPipe) para rastrear movimentos da cabeça e expressões faciais. Desenvolvido para acessibilidade, produtividade ou apenas para se sentir em um filme de ficção científica.

✨ Funcionalidades

Rastreamento de Cabeça: O cursor segue o movimento do seu nariz com suavização dinâmica (rápido quando você precisa, preciso quando você para).

Cliques Oculares: Pisque (segure levemente) para clicar.

- 👁️ Olho Esquerdo: Clique Esquerdo
- 👁️ Olho Direito: Clique Direito

Rolagem Facial (Scroll):

- 😮 Boca Aberta: Rola para BAIXO.
- 😗 Biquinho: Rola para CIMA.

Modo Pausa: Desative o controle temporariamente para relaxar.

🚀 Como Rodar

1. Instalar Dependências

Certifique-se de ter o Python instalado. Copie e cole o comando abaixo no seu terminal para instalar as bibliotecas necessárias:

pip install opencv-python mediapipe pyautogui numpy

2. Executar o Projeto

No terminal, navegue até a pasta onde salvou o arquivo e execute:

python rastreador.py

🎮 Guia de Uso

A Calibração: Ao iniciar, você verá uma janela com a sua webcam e um retângulo ciano no centro.

Mova o Mouse: Mantenha seu rosto dentro do quadro. Mova o nariz para as bordas do retângulo ciano para alcançar as bordas da tela.

Clicar: Feche um olho e segure por 0.3 segundos. Você verá uma barra de progresso no topo da tela. Quando ela encher, o clique acontece.

- Rolagem (Scroll):

Abra a boca para descer a página.

Faça um "biquinho" (junte os lábios) para subir a página.

Observe os indicadores numéricos (V: e H:) na parte inferior para entender o que a câmera está detectando.

- Pausar: Pressione a tecla P no teclado para congelar o mouse se precisar olhar para o lado ou conversar.
- Sair: Pressione ESC na janela da câmera para fechar o programa.

⚙️ Ajustes Finos (Configuração)

Abra o arquivo head_mouse_pro.py em um editor de texto. No início do arquivo, você encontrará a classe Config onde pode personalizar tudo:

- SENSITIVITY: Aumente para mover menos a cabeça. Diminua para mais precisão.
- SCROLL_SPEED: Aumente para rolar a página mais rápido.

MOUTH_OPEN_THRESHOLD e MOUTH_PUCKER_THRESHOLD: Ajuste esses valores se o scroll estiver muito sensível ou difícil de ativar (use os números de debug na tela como guia).

Projeto desenvolvido com Python e MediaPipe.
