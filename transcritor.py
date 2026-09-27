import os
import time
import threading
import sys
import re
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator

#classe espia para ler a percentagem de download do terminal e mandar para a interface
class InterceptadorDownload:
    def __init__(self, on_status):
        self.on_status = on_status
        self.original_stderr = sys.stderr

    def write(self, msg):
        #procura por percentagens no log do terminal (ex: 45%)
        match = re.search(r'(\d+)%', msg)
        if match:
            self.on_status(f"A descarregar o modelo de IA... {match.group(1)}%")
        
        #garante que o terminal continua a receber o log original para nao quebrar nada
        self.original_stderr.write(msg)

    def flush(self):
        self.original_stderr.flush()

def processar_audios_local(lista_destinos, modelo, idioma, traduzir, on_status, on_progress, on_finish, on_error):
    #roda numa thread separada para nao congelar a interface
    def tarefa():
        #ativa o nosso espiao de terminal
        interceptador = InterceptadorDownload(on_status)
        
        try:
            on_status(f"A preparar para carregar o modelo {modelo}...")
            
            #desvia o log de erro padrao para o nosso espiao
            sys.stderr = interceptador
            
            #se o modelo nao existir no pc, aqui vai comecar o download
            model = WhisperModel(modelo, device="cpu", compute_type="int8", cpu_threads=4)
            
            #devolve o terminal ao normal apos o download/carregamento
            sys.stderr = interceptador.original_stderr
            
            mapa_idiomas = {"Inglês": "en", "Português": "pt", "Espanhol": "es"}
            lang_code = mapa_idiomas.get(idioma, None) 
            
            total = len(lista_destinos)
            
            #lista_destinos e uma lista de tuplos: (caminho_audio_original, caminho_onde_salvar_texto)
            for index, (caminho_audio, caminho_destino) in enumerate(lista_destinos):
                nome_base = os.path.basename(caminho_audio)
                on_status(f"Transcrevendo {index+1}/{total}: {nome_base}")
                
                segments, info = model.transcribe(caminho_audio, language=lang_code, beam_size=5)
                
                texto_final = []
                for segment in segments:
                    start_time = time.strftime('%H:%M:%S', time.gmtime(segment.start))
                    linha = f"[{start_time}] {segment.text}"
                    
                    if traduzir:
                        linha = GoogleTranslator(source='auto', target='pt').translate(linha)
                    
                    texto_final.append(linha)
                
                with open(caminho_destino, "w", encoding="utf-8") as f:
                    f.write("\n".join(texto_final))
                
                #customtkinter progressbar vai de 0.0 a 1.0
                progresso = (index + 1) / total
                on_progress(progresso)
                
            on_finish()
            
        except Exception as e:
            #em caso de erro fatal, devolve o terminal e avisa a interface
            sys.stderr = interceptador.original_stderr
            on_error(str(e))

    threading.Thread(target=tarefa, daemon=True).start()