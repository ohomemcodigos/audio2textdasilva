import os
import zipfile
import json

def exportar_colab(audio_files, pasta_destino):
    try:
        #cria o ficheiro zip com os audios na pasta escolhida pelo utilizador
        nome_zip = os.path.join(pasta_destino, "audios_para_colab.zip")
        with zipfile.ZipFile(nome_zip, 'w') as zipf:
            for f in audio_files:
                zipf.write(f, os.path.basename(f))
        
        #gera o codigo em python para o colab
        codigo_colab = [
            "!pip install faster-whisper deep-translator\n",
            "import os\n",
            "import time\n",
            "from faster_whisper import WhisperModel\n",
            "from deep_translator import GoogleTranslator\n\n",
            "# descompacta os audios\n",
            "!unzip -o audios_para_colab.zip -d meus_audios/\n\n",
            "print('carregando modelo large-v3 na gpu gratuita do google...')\n",
            "model = WhisperModel('large-v3', device='cuda', compute_type='float16')\n\n",
            "arquivos = [os.path.join('meus_audios', f) for f in os.listdir('meus_audios') if f.endswith(('.mp3', '.wav', '.m4a'))]\n",
            "for f in arquivos:\n",
            "    print(f'\\ntranscrevendo: {f}')\n",
            "    segments, info = model.transcribe(f, beam_size=5)\n",
            "    texto = []\n",
            "    for segment in segments:\n",
            "        start = time.strftime('%H:%M:%S', time.gmtime(segment.start))\n",
            "        texto.append(f'[{start}] {segment.text}')\n",
            "    with open(f + '_transcrito.txt', 'w', encoding='utf-8') as out:\n",
            "        out.write('\\n'.join(texto))\n",
            "print('\\npronto! verifique os arquivos .txt gerados na pasta meus_audios.')\n"
        ]

        #estrutura do notebook jupyter
        notebook = {
            "cells": [{"cell_type": "code", "metadata": {}, "source": codigo_colab, "outputs": [], "execution_count": None}],
            "metadata": {"accelerator": "GPU"},
            "nbformat": 4,
            "nbformat_minor": 4
        }

        caminho_notebook = os.path.join(pasta_destino, "audio2text_Colab.ipynb")
        with open(caminho_notebook, "w", encoding="utf-8") as f:
            json.dump(notebook, f, indent=1)

        return True, caminho_notebook
    except Exception as e:
        return False, str(e)