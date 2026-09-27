import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class Audio2TextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio2Text Da Silva")
        self.root.geometry("650x550")
        
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

        #para traduzir
        self.var_traduzir = tk.BooleanVar()
        ttk.Checkbutton(frame_config, text="Traduzir para Português (Deep Translator)", variable=self.var_traduzir).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # --- modo de processamento ---
        frame_modo = ttk.LabelFrame(self.root, text="Modo de Processamento")
        frame_modo.pack(padx=10, pady=10, fill="x")

        self.var_modo = tk.StringVar(value="local")
        ttk.Radiobutton(frame_modo, text="Hardware Local (CPU/GPU)", variable=self.var_modo, value="local").pack(anchor="w", padx=10, pady=2)
        ttk.Radiobutton(frame_modo, text="Exportar para Google Colab (.zip + script)", variable=self.var_modo, value="colab").pack(anchor="w", padx=10, pady=2)

        # --- progresso e Ação ---
        frame_acao = ttk.Frame(self.root)
        frame_acao.pack(padx=10, pady=10, fill="x")

        self.lbl_status = ttk.Label(frame_acao, text="Estado: A aguardar ficheiros...")
        self.lbl_status.pack(pady=5)

        self.progress_bar = ttk.Progressbar(frame_acao, orient="horizontal", mode="determinate", length=400)
        self.progress_bar.pack(pady=5)

        self.btn_iniciar = ttk.Button(frame_acao, text="Iniciar Processamento", command=self.iniciar_processamento)
        self.btn_iniciar.pack(pady=10)

    # --- interface ---
    def show_guide(self):
        guia_win = tk.Toplevel(self.root)
        guia_win.title("Guia de Uso")
        guia_win.geometry("400x250")
        texto = (
            "Guia Rápido do Audio2Text Da Silva\n\n"
            "1. Fila de Áudio: Adicione até 5 ficheiros (mp3, wav, m4a).\n"
            "2. Idioma: Se souber o idioma original, selecione-o (acelera o processo). Caso contrário, deixe em 'Automático'.\n"
            "3. Tradução: Marque a caixa se o áudio estiver noutro idioma e quiser o texto final em Português.\n"
            "4. Modo Local: Transcreve usando o seu computador.\n"
            "5. Modo Colab: Prepara os seus ficheiros para processamento gratuito e rápido na nuvem do Google."
        )
        ttk.Label(guia_win, text=texto, justify="left", wraplength=360).pack(padx=20, pady=20)

    def add_audio(self):
        if len(self.audio_files) >= 5:
            messagebox.showwarning("Limite Atingido", "Só pode adicionar até 5 ficheiros de cada vez na fila.")
            return
        
        ficheiros = filedialog.askopenfilenames(
            title="Selecione os ficheiros de áudio",
            filetypes=[("Ficheiros de Áudio", "*.mp3 *.wav *.m4a")]
        )
        
        for f in ficheiros:
            if len(self.audio_files) < 5 and f not in self.audio_files:
                self.audio_files.append(f)
                #extrai apenas o nome do arquivo para exibir na interface de forma limpa
                nome_arquivo = f.split('/')[-1]
                self.listbox_audios.insert(tk.END, nome_arquivo)
            elif len(self.audio_files) >= 5:
                messagebox.showinfo("Aviso", "O limite de 5 ficheiros foi atingido. Alguns ficheiros não foram adicionados.")
                break

    def clear_queue(self):
        self.audio_files.clear()
        self.listbox_audios.delete(0, tk.END)

    def iniciar_processamento(self):
        if not self.audio_files:
            messagebox.showerror("Erro", "A fila está vazia! Adicione pelo menos um ficheiro.")
            return
        
        #teste visual da barra de progresso
        self.lbl_status.config(text="A iniciar testes de interface... (Pronto para a Fase 3)")
        self.progress_bar["value"] = 10

def main():
    root = tk.Tk()
    app = Audio2TextApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()