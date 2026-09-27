import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading #evita travamentos do app
import os
import time
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator

class Audio2TextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio2Text Da Silva")
        self.root.geometry("650x600") #aumentei um pouquinho a altura
        
        #lista interna; até 5 arquivos de áudio
        self.audio_files = [] 
        
        self.create_menu()
        self.create_widgets()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        #menu de ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Guia de Uso", command=self.show_guide)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        
        self.root.config(menu=menubar)

    def create_widgets(self):
        # --- fila de áudios ---
        frame_fila = ttk.LabelFrame(self.root, text="Fila de Áudios (Máx: 5)")
        frame_fila.pack(padx=10, pady=10, fill="x")

        self.listbox_audios = tk.Listbox(frame_fila, height=5)
        self.listbox_audios.pack(padx=10, pady=10, fill="x")

        btn_frame = ttk.Frame(frame_fila)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Adicionar Áudio", command=self.add_audio).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpar Fila", command=self.clear_queue).pack(side="left", padx=5)

        # --- configurações ---
        frame_config = ttk.LabelFrame(self.root, text="Configurações de Transcrição")
        frame_config.pack(padx=10, pady=10, fill="x")

        #idioma original
        ttk.Label(frame_config, text="Idioma Original:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_idioma = ttk.Combobox(frame_config, values=["Automático", "Inglês", "Português", "Espanhol"], state="readonly")
        self.combo_idioma.current(0)
        self.combo_idioma.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        #escolha do modelo
        ttk.Label(frame_config, text="Modelo de IA:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_modelo = ttk.Combobox(frame_config, values=["tiny", "base", "small", "medium", "large-v3"], state="readonly")
        self.combo_modelo.current(3) #medium como padrão
        self.combo_modelo.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        #para traduzir
        self.var_traduzir = tk.BooleanVar()
        ttk.Checkbutton(frame_config, text="Traduzir para Português (Deep Translator)", variable=self.var_traduzir).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # --- modo de processamento ---
        frame_modo = ttk.LabelFrame(self.root, text="Modo de Processamento")
        frame_modo.pack(padx=10, pady=10, fill="x")

        self.var_modo = tk.StringVar(value="local")
        ttk.Radiobutton(frame_modo, text="Hardware Local (CPU/GPU)", variable=self.var_modo, value="local").pack(anchor="w", padx=10, pady=2)
        ttk.Radiobutton(frame_modo, text="Exportar para Google Colab (.zip + script)", variable=self.var_modo, value="colab").pack(anchor="w", padx=10, pady=2)

        # --- progresso e Ação ---
        frame_acao = ttk.Frame(self.root)
        frame_acao.pack(padx=10, pady=10, fill="x")

        self.lbl_status = ttk.Label(frame_acao, text="Estado: Aguardando arquivos...")
        self.lbl_status.pack(pady=5)

        self.progress_bar = ttk.Progressbar(frame_acao, orient="horizontal", mode="determinate", length=400)
        self.progress_bar.pack(pady=5)

        self.btn_iniciar = ttk.Button(frame_acao, text="Iniciar Processamento", command=self.iniciar_processamento)
        self.btn_iniciar.pack(pady=10)

    # --- interface ---
    def show_guide(self):
        guia_win = tk.Toplevel(self.root)
        guia_win.title("Guia de Uso")
        guia_win.geometry("450x300")
        texto = (
            "Guia Rápido do audio2text Da Silva\n\n"
            "1. Fila: Adicione até 5 arquivos.\n"
            "2. Idioma: Selecionar acelera o processo.\n"
            "3. Modelo:\n"
            "   - tiny/base: Muito rápido, mas comete erros.\n"
            "   - small: Bom equilíbrio para áudios limpos.\n"
            "   - medium: Recomendado. Alta precisão.\n"
            "   - large-v3: Máxima precisão, mas muito lento na CPU.\n"
            "4. Tradução: Traduz o texto final para Português.\n"
            "5. Modos: Local (usa seu PC) ou Colab (nuvem Google)."
        )
        ttk.Label(guia_win, text=texto, justify="left", wraplength=400).pack(padx=20, pady=20)

    def add_audio(self):
        if len(self.audio_files) >= 5:
            messagebox.showwarning("Limite Atingido", "Só pode adicionar até 5 arquivos de cada vez na fila.")
            return
        
        arquivos = filedialog.askopenfilenames(
            title="Selecione os arquivos de áudio",
            filetypes=[("Arquivos de Áudio", "*.mp3 *.wav *.m4a")]
        )
        
        for f in arquivos:
            if len(self.audio_files) < 5 and f not in self.audio_files:
                self.audio_files.append(f)
                #extrai apenas o nome do arquivo para exibir na interface de forma limpa
                nome_arquivo = f.split('/')[-1]
                self.listbox_audios.insert(tk.END, nome_arquivo)
            elif len(self.audio_files) >= 5:
                messagebox.showinfo("Aviso", "O limite de 5 arquivos foi atingido. Alguns arquivos não foram adicionados.")
                break

    def clear_queue(self):
        self.audio_files.clear()
        self.listbox_audios.delete(0, tk.END)

    def iniciar_processamento(self):
        if not self.audio_files:
            messagebox.showerror("Erro", "A fila está vazia! Adicione pelo menos um arquivo.")
            return
        
        modo = self.var_modo.get()
        
        if modo == "local":
            #desativa o botão para evitar cliques duplos durante o processo
            self.btn_iniciar.config(state="disabled")
            self.progress_bar["value"] = 0
            
            #inicia a thread para rodar a ia em segundo plano e não travar o app
            thread = threading.Thread(target=self.processar_local)
            thread.start()
        else:
            self.lbl_status.config(text="O Modo Colab será implementado na próxima fase.")

    def processar_local(self):
        modelo_selecionado = self.combo_modelo.get()
        self.lbl_status.config(text=f"Carregando modelo {modelo_selecionado} (pode demorar se for o 1º download)...")
        
        try:
            #configuração específica para rodar na cpu
            model = WhisperModel(modelo_selecionado, device="cpu", compute_type="int8", cpu_threads=4)
            
            #mapeia o idioma selecionado
            idioma_selecionado = self.combo_idioma.get()
            mapa_idiomas = {"Inglês": "en", "Português": "pt", "Espanhol": "es"}
            lang_code = mapa_idiomas.get(idioma_selecionado, None) 
            
            total_arquivos = len(self.audio_files)
            
            for index, caminho_audio in enumerate(self.audio_files):
                nome_base = os.path.basename(caminho_audio)
                self.lbl_status.config(text=f"Transcrevendo {index+1}/{total_arquivos}: {nome_base}")
                
                #inicia a transcrição
                segments, info = model.transcribe(caminho_audio, language=lang_code, beam_size=5)
                
                texto_final = []
                
                for segment in segments:
                    #formata o tempo no estilo de rélogio [00:00:00]
                    start_time = time.strftime('%H:%M:%S', time.gmtime(segment.start))
                    linha = f"[{start_time}] {segment.text}"
                    
                    #traduz a linha se o checkbox estiver marcado
                    if self.var_traduzir.get():
                        linha = GoogleTranslator(source='auto', target='pt').translate(linha)
                    
                    texto_final.append(linha)
                
                #salva o arquivo de texto
                caminho_txt = f"{os.path.splitext(caminho_audio)[0]}_transcrito.txt"
                with open(caminho_txt, "w", encoding="utf-8") as f:
                    f.write("\n".join(texto_final))
                
                #atualiza a barra de progresso
                progresso = ((index + 1) / total_arquivos) * 100
                self.progress_bar["value"] = progresso
                
            self.lbl_status.config(text="Processamento concluído com sucesso!")
            messagebox.showinfo("Pronto", "Todos os arquivos foram transcritos!")
            
        except Exception as e:
            self.lbl_status.config(text="Erro no processamento.")
            messagebox.showerror("Erro Crítico", f"Ocorreu um erro: {str(e)}")
            
        finally:
            #reativa o botão ao final
            self.btn_iniciar.config(state="normal")

def main():
    root = tk.Tk()
    app = Audio2TextApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()