# audio2text da Silva ![Versão](https://img.shields.io/badge/versão-v1.0.0-blue.svg)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-Dark%2FLight-1F538D?style=for-the-badge&logo=python&logoColor=white)

> Um aplicativo desktop moderno e inteligente para transcrição de áudio e vídeo alimentado por Inteligência Artificial (Faster-Whisper), com interface intuitiva, suporte a legendas, janela de revisão e opção de processamento na nuvem (Google Colab).

---

## Instalação

Existem duas formas principais de começar a utilizar o **audio2text da Silva**:

### 1. Instalação via Executável (.exe) - Recomendado para usuários
Se você deseja apenas utilizar o aplicativo no seu computador Windows sem precisar configurar ambiente de código, baixe a versão mais recente diretamente da página de releases:

**[Baixar o Executável Compactado (.exe) - GitHub Releases](https://github.com/ohomemcodigos/audio2textdasilva/releases)**

### 2. Instalação via Código-Fonte (Para desenvolvedores)
Se deseja contribuir, estudar ou executar o projeto localmente, siga os passos abaixo:

**Pré-requisitos:**
- [Python 3.11](https://www.python.org/) (ou superior) instalado na sua máquina.

**Passos:**

1. Clone este repositório:
    ```bash
    git clone https://github.com/ohomemcodigos/audio2textdasilva.git
    ```

2. Acesse a pasta do projeto:
    ```bash
    cd audio2textdasilva
    ```

3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4. Inicie a aplicação:
    ```bash
    python main.py
    ```

> **Nota:** Caso deseje gerar o seu próprio arquivo executável com o ícone personalizado, utilize o comando de compilação:
```bash
python -m PyInstaller --name "audio2text_da_Silva" --noconsole --icon=audio2textdaSilva.ico --add-data "audio2textdaSilva.ico;." --collect-all customtkinter --collect-all tkinterdnd2 --collect-all faster_whisper --collect-all ctranslate2 main.py
```

---

## Sobre o Projeto

O **audio2text da Silva** foi desenvolvido pensando nas dificuldades que a minha namorada tinha para realizar transcrições de áudio de aulas que ela teve, já que muito dos softwares e serviços são pagos e caros. Então, para simplificar o fluxo de trabalho dela, mas também de criadores de conteúdo, jornalistas, estudantes e profissionais que necessitam transcrever reuniões, entrevistas ou vídeos inteiros, de forma privada, rápida e local.

O projeto prioriza a experiência e a clareza, oferecendo desde otimizações automáticas de hardware até uma ferramenta de revisão integrada e um modo especial de integração gratuita com o Google Colab para uso de modelos pesados em nuvem.

O projeto não é perfeito, mas pode ser uma mão na roda para quem precisa de extração de texto via áudio e vídeos de maneira gratuita e simples.

---

## Funcionalidades Principais

### Suporte Multimídia Completo
Arraste arquivos de áudio (`.mp3`, `.wav`, `.m4a`) ou vídeo (`.mp4`, `.mkv`, `.avi`, `.mov`) diretamente para a fila de processamento.

### Janela de Revisão Integrada
Interface pós-processamento dedicada que permite ler, corrigir e editar o texto transcrito antes de exportar o arquivo definitivo.

### Múltiplos Formatos de Saída
Exporte os seus resultados de forma flexível para legendas cronometradas (`.srt`), documentos editáveis (`.docx`) ou blocos de texto simples (`.txt`).

### Otimização Dinâmica de Hardware
Analisa as threads da CPU no arranque para recomendar o modelo de IA ideal para o seu computador, exibindo um indicador visual de desempenho.

### Modo Google Colab
Exporta um pacote compactado e um notebook dedicado para processamento gratuito na nuvem utilizando GPUs do Google para modelos avançados (*large-v3*).

---

## Tecnologias e Bibliotecas Utilizadas

O projeto foi construído em **Python**, focando numa arquitetura modular e limpa (`main.py`, `interface.py`, `transcritor.py`, `gestor_arquivos.py`).

- **CustomTkinter & TkinterDnD2** — Construção de uma interface gráfica moderna com suporte a temas (Claro/Escuro) e arrastar e soltar arquivos.
- **Faster-Whisper (CTranslate2)** — Motor local de reconhecimento de fala de altíssima performance e precisão.
- **Deep Translator & python-docx** — Automação de tradução de idiomas e geração nativa de documentos do Word.

---

## Status do Projeto e Licenciamento

Este projeto foi integralmente desenvolvido com o **suporte e colaboração de Inteligência Artificial (IA)**, unindo engenharia de software tradicional e assistência avançada de IA para arquitetura e refinamento.

Este é, portanto, um projeto **Open Source** e livre. Sinta-se totalmente livre para clonar, modificar, adaptar, criar novas funcionalidades ou estudar o código da maneira que bem entender.
