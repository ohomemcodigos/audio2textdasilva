import os
import time
import threading
import sys
import re
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator

class InterceptadorDownload:
    def __init__(self, on_status):
        self.on_status = on_status
        self.original_stderr = sys.stderr

    def write(self, msg):
        match = re.search(r'(\d+)%', msg)
        if match:
            self.on_status(f"Baixando o modelo de IA... {match.group(1)}%")
        self.original_stderr.write(msg)

    def flush(self):
        self.original_stderr.flush()

def formatar_tempo_srt(segundos):
    milisegundos = int((segundos - int(segundos)) * 1000)
    s = int(segundos)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{milisegundos:03d}"

def formatar_tempo_txt(segundos):
    return time.strftime('%H:%M:%S', time.gmtime(segundos))

def processar_audios_local(arquivos, modelo, idioma, traduzir, formato, estilo, threads, on_status, on_progress, on_finish, on_error):
    def tarefa():
        interceptador = InterceptadorDownload(on_status)
        try:
            on_status(f"Preparando o carregamento do modelo {modelo}...")
            sys.stderr = interceptador
            model = WhisperModel(modelo, device="cpu", compute_type="int8", cpu_threads=threads)
            sys.stderr = interceptador.original_stderr
            
            mapa_idiomas = {"Inglês": "en", "Português": "pt", "Espanhol": "es"}
            lang_code = mapa_idiomas.get(idioma, None) 
            
            total = len(arquivos)
            resultados = []
            
            for index, caminho_arquivo in enumerate(arquivos):
                nome_base = os.path.basename(caminho_arquivo)
                on_status(f"Transcrevendo {index+1}/{total}: {nome_base} (Iniciando...)")
                
                segments, info = model.transcribe(caminho_arquivo, language=lang_code, beam_size=5)
                duracao_total = info.duration
                
                texto_linhas = []
                inicio_tempo = time.time()
                
                for i, segment in enumerate(segments):
                    texto_traduzido = segment.text.strip()
                    if traduzir:
                        texto_traduzido = GoogleTranslator(source='auto', target='pt').translate(texto_traduzido)
                    
                    if formato == ".srt":
                        tempo_inicio = formatar_tempo_srt(segment.start)
                        tempo_fim = formatar_tempo_srt(segment.end)
                        texto_linhas.append(f"{i + 1}\n{tempo_inicio} --> {tempo_fim}\n{texto_traduzido}\n")
                    else:
                        if estilo == "com_tempo":
                            tempo = formatar_tempo_txt(segment.start)
                            texto_linhas.append(f"[{tempo}] {texto_traduzido}")
                        else:
                            texto_linhas.append(f"{texto_traduzido} ")
                    
                    tempo_decorrido = time.time() - inicio_tempo
                    progresso_arquivo = segment.end / duracao_total if duracao_total > 0 else 0
                    
                    if progresso_arquivo > 0 and progresso_arquivo <= 1.0:
                        tempo_total_estimado = tempo_decorrido / progresso_arquivo
                        tempo_restante = max(0, tempo_total_estimado - tempo_decorrido)
                        
                        eta_str = time.strftime('%H:%M:%S' if tempo_restante > 3600 else '%M:%S', time.gmtime(tempo_restante))
                        percentagem = int(progresso_arquivo * 100)
                        on_status(f"Transcrevendo {index+1}/{total}: {nome_base} | {percentagem}% | ETA: {eta_str}")
                    
                    progresso_global = (index / total) + (progresso_arquivo / total)
                    on_progress(progresso_global)
                
                # junta o texto de acordo com o formato
                if formato == ".srt" or estilo == "com_tempo":
                    texto_completo = "\n".join(texto_linhas)
                else:
                    texto_completo = "".join(texto_linhas)
                
                # guarda na memoria para a janela de revisao
                resultados.append({
                    "caminho_original": caminho_arquivo,
                    "nome_base": os.path.splitext(nome_base)[0],
                    "texto": texto_completo,
                    "salvo": False
                })
                    
            on_finish(resultados)
            
        except Exception as e:
            if hasattr(interceptador, 'original_stderr'):
                sys.stderr = interceptador.original_stderr
            on_error(str(e))

    threading.Thread(target=tarefa, daemon=True).start()