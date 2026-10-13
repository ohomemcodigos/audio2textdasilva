# audio2textdasilva
**Aplicativo desktop para transcrição de áudio e vídeo desenvolvido em Python.**

## Baixe Aqui!
Se você procura apenas o o executável pronto para uso no Windows sem precisar configurar código; 
Clique na aba de releases e faça download da versão mais recente:
- [Releases do audio2text da Silva](https://github.com/ohomemcodigos/audio2textdasilva/releases)

## Tecnologias usadas para o desenvolvimento
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
- **Python 3.11:** linguagem principal para orquestração da lógica e backend local.

![CustomTkinter](https://img.shields.io/badge/CustomTkinter-Dark%2FLight-1F538D?style=for-the-badge&logo=python&logoColor=white)
- **CustomTkinter & TkinterDnD2:** para a construção de uma interface gráfica moderna (com suporte a temas e arrastar e soltar arquivos).

![Faster-Whisper](https://img.shields.io/badge/Faster_Whisper-CTranslate2-FF6F00?style=for-the-badge&logo=openai&logoColor=white)
- **Faster-Whisper:** motor local de reconhecimento de fala de alta performance e precisão.

![Google Colab](https://img.shields.io/badge/Google_Colab-Nuves_GPU-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white)
- **Google Colab & Deep Translator:** suporte a exportação para notebooks na nuvem e tradução automática de idiomas.


## Principais Funcionalidades
- **Suporte Multimídia Completo:** Arraste arquivos de áudio (`.mp3`, `.wav`, `.m4a`) ou vídeo (`.mp4`, `.mkv`, `.avi`, `.mov`) diretamente para a fila.
- **Janela de Revisão Integrada:** Edite e corrija o texto transcrito gerado pela IA antes de exportar o arquivo definitivo.
- **Múltiplos Formatos de Saída:** Exporte para legendas cronometradas (`.srt`), documentos editáveis (`.docx`) ou blocos de texto (`.txt`).
- **Otimização de Hardware:** Análise automática de threads da CPU para configurar a performance de acordo com a máquina do usuário.


## Extra
O projeto conta com diversas funcionalidades avançadas focadas em usabilidade e experiência do usuário (UX):
- **Janela de Revisão Integrada:** Permite ler, corrigir e editar o texto completo pós-processamento antes de exportar o arquivo definitivo.

- **Suporte Nativo a Vídeos:** Arraste ficheiros `.mp4`, `.mkv`, `.avi` ou `.mov` diretamente para a fila sem precisar de conversões manuais.

- **Modo Google Colab:** Exporta um pacote compactado e um notebook dedicado para processamento gratuito na nuvem utilizando GPUs do Google para modelos pesados (*large-v3*).

- **Otimização Dinâmica de Hardware:** Analisa as threads da CPU no arranque para recomendar o modelo de IA ideal para o seu computador, exibindo um indicador visual de desempenho.

- **Hub de Ajuda e Tutoriais:** Manuais detalhados integrados na aplicação, tour guiado e instruções passo a passo para o uso do Google Colab.


## Como Rodar o Projeto
### 1. Clone o repositório
Clone este repositório no seu computador:
```
git clone https://github.com/ohomemcodigos/audio2textdasilva.git
```

### 2. Instale as dependências
Abra o terminal na pasta do projeto e instale os pacotes necessários:
```
pip install -r requirements.txt
```

### 3. Inicie a aplicação
Execute o script principal via terminal:
```
python main.py
```

### 4. Compilação Opcional (.exe)
Caso deseje gerar o seu próprio arquivo executável com o ícone personalizado:
```
python -m PyInstaller --name "audio2text_da_Silva" --noconsole --icon=audio2textdaSilva.ico --add-data "audio2textdaSilva.ico;." --collect-all customtkinter --collect-all tkinterdnd2 --collect-all faster_whisper --collect-all ctranslate2 main.py
```

>A aplicação estará pronta para transcrições locais e na nuvem!


## Sobre o Desenvolvimento e Licenciamento
Este projeto foi integralmente desenvolvido com o **suporte de Inteligência Artificial (IA)**. 

Este é um projeto de código aberto e livre. Qualquer pessoa pode pegar este código, clonar, usar, estudar, adaptar ou modificar da maneira que bem entender. Sinta-se totalmente livre para construir em cima do que foi feito aqui.