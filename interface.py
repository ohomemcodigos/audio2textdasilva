import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import json

from gestor_arquivos import exportar_colab, salvar_documento
from transcritor import processar_audios_local

IDIOMAS_WHISPER = [
    "Alemão", "Árabe", "Coreano", "Chinês", "Dinamarquês", "Francês", 
    "Grego", "Hebraico", "Holandês", "Hindi", "Indonésio", "Italiano", 
    "Japonês", "Polonês", "Russo", "Sueco", "Turco", "Ucraniano", "Vietnamita"
]

EXTENSOES_SUPORTADAS = ('.mp3', '.wav', '.m4a', '.mp4', '.mkv', '.avi', '.mov')

class AppRoot(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

class Audio2TextApp(AppRoot):
    def __init__(self):
        super().__init__()
        self.title("audio2text da Silva")
        self.geometry("750x850")
        
        self.config_file = "config.json"
        self.config = self.carregar_config()
        
        ctk.set_appearance_mode(self.config.get("tema", "Dark"))
        ctk.set_default_color_theme("blue")
        
        self.audio_files = []
        
        self.setup_ui()
        self.verificar_hardware_silencioso()

    def carregar_config(self):
        default = {
            "primeira_vez": True, 
            "hardware_analisado": False, 
            "tema": "Dark",
            "pasta_padrao": "",
            "threads_cpu": 4
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    dados = json.load(f)
                    for key, val in default.items():
                        if key not in dados:
                            dados[key] = val
                    return dados
            except:
                pass
        return default

    def salvar_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f)

    def centralizar_janela(self, janela, largura, altura):
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (largura // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (altura // 2)
        janela.geometry(f"{largura}x{altura}+{x}+{y}")

    def verificar_hardware_silencioso(self):
        if not self.config.get("hardware_analisado", False):
            self.after(500, self.pedir_permissao_hardware)
        else:
            threads = os.cpu_count() or 4
            if threads >= 8:
                self.combo_modelo.set("medium")
            elif threads >= 4:
                self.combo_modelo.set("small")
            else:
                self.combo_modelo.set("base")
                
            # Atualiza o aviso visual com a recomendação
            self.lbl_otimizacao.configure(text=f"✓ Otimizado para o seu PC ({threads} Threads)")
            
            if self.config.get("primeira_vez", True):
                self.after(500, self.iniciar_tour)

    def pedir_permissao_hardware(self):
        resposta = messagebox.askyesno(
            "Análise de Hardware",
            "Permite que o aplicativo analise rapidamente o seu processador para configurar "
            "automaticamente o melhor modelo e performance da IA?\n\n(Apenas para uso local)."
        )
        if resposta:
            self.config["hardware_analisado"] = True
            self.salvar_config()
            self.verificar_hardware_silencioso()
        else:
            self.config["hardware_analisado"] = True 
            self.salvar_config()
            
        if self.config.get("primeira_vez", True):
            self.iniciar_tour()

    def alternar_tema(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
            self.btn_tema.configure(text="🌙 Escuro")
        else:
            ctk.set_appearance_mode("Dark")
            self.btn_tema.configure(text="☀️ Claro")

    def setup_ui(self):
        self.frame_topo = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.frame_topo.pack(fill="x", padx=20, pady=(10, 0))
        
        self.btn_config = ctk.CTkButton(self.frame_topo, text="⚙️ Configurações", width=120, fg_color="gray30", hover_color="gray40", command=self.abrir_configuracoes)
        self.btn_config.pack(side="left")

        self.btn_ajuda = ctk.CTkButton(self.frame_topo, text="❓ Ajuda", width=100, fg_color="gray30", hover_color="gray40", command=self.mostrar_menu_ajuda)
        self.btn_ajuda.pack(side="right")

        self.frame_fila = ctk.CTkFrame(self)
        self.frame_fila.pack(padx=20, pady=10, fill="x")
        
        self.lbl_fila = ctk.CTkLabel(self.frame_fila, text="Arraste Áudios ou Vídeos (.mp4) aqui", font=("Arial", 16))
        self.lbl_fila.pack(pady=10)
        
        self.btn_add = ctk.CTkButton(self.frame_fila, text="Adicionar Arquivos", command=self.add_audio)
        self.btn_add.pack(pady=5)
        
        self.scroll_arquivos = ctk.CTkScrollableFrame(self.frame_fila, height=150)
        self.scroll_arquivos.pack(padx=10, pady=10, fill="x")
        
        self.frame_fila.drop_target_register(DND_FILES)
        self.frame_fila.dnd_bind('<<Drop>>', self.on_drop)
        self.scroll_arquivos.drop_target_register(DND_FILES)
        self.scroll_arquivos.dnd_bind('<<Drop>>', self.on_drop)
        
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.pack(padx=20, pady=10, fill="x")
        
        self.lbl_idioma = ctk.CTkLabel(self.frame_config, text="Idioma Original:")
        self.lbl_idioma.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.combo_idioma = ctk.CTkComboBox(self.frame_config, values=["Automático", "Português", "Inglês", "Espanhol", "Outros..."], command=self.verificar_idioma)
        self.combo_idioma.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        self.lbl_modelo = ctk.CTkLabel(self.frame_config, text="Modelo de IA:")
        self.lbl_modelo.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        
        frame_mod = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        frame_mod.grid(row=1, column=1, padx=10, pady=5, sticky="w", columnspan=2)
        
        self.combo_modelo = ctk.CTkComboBox(frame_mod, values=["tiny", "base", "small", "medium", "large-v3"])
        self.combo_modelo.set("medium")
        self.combo_modelo.pack(side="left", padx=(0, 5))
        
        self.btn_info = ctk.CTkButton(frame_mod, text=" i ", width=28, corner_radius=14, font=("Arial", 14, "bold"), fg_color="gray30", text_color="cyan", hover_color="gray40", command=self.mostrar_info_modelos)
        self.btn_info.pack(side="left")
        
        # Label de Otimização Visual (Fica invisível até ser preenchida pelo scan)
        self.lbl_otimizacao = ctk.CTkLabel(frame_mod, text="", text_color="#2ecc71", font=("Arial", 11, "italic"))
        self.lbl_otimizacao.pack(side="left", padx=10)
        
        self.lbl_formato = ctk.CTkLabel(self.frame_config, text="Formato de Saída:")
        self.lbl_formato.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.combo_formato = ctk.CTkComboBox(self.frame_config, values=[".txt", ".srt", ".docx"], command=self.verificar_formato)
        self.combo_formato.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        self.lbl_estilo = ctk.CTkLabel(self.frame_config, text="Estilo de Texto:")
        self.lbl_estilo.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        
        self.var_estilo = ctk.StringVar(value="com_tempo")
        frame_estilo = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        frame_estilo.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        self.rad_tempo = ctk.CTkRadioButton(frame_estilo, text="Com Horários", variable=self.var_estilo, value="com_tempo")
        self.rad_tempo.pack(side="left", padx=(0, 10))
        self.rad_corrido = ctk.CTkRadioButton(frame_estilo, text="Texto Corrido", variable=self.var_estilo, value="corrido")
        self.rad_corrido.pack(side="left")

        self.var_traduzir = ctk.BooleanVar()
        self.chk_traduzir = ctk.CTkCheckBox(self.frame_config, text="Traduzir texto final para Português", variable=self.var_traduzir)
        self.chk_traduzir.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        self.frame_modo = ctk.CTkFrame(self)
        self.frame_modo.pack(padx=20, pady=10, fill="x")
        
        self.lbl_modo = ctk.CTkLabel(self.frame_modo, text="Onde deseja processar os arquivos?", font=("Arial", 14, "bold"))
        self.lbl_modo.pack(pady=10)
        
        self.var_modo = ctk.StringVar(value="local")
        self.rad_local = ctk.CTkRadioButton(self.frame_modo, text="🖥️ PC Local", variable=self.var_modo, value="local")
        self.rad_local.pack(side="left", padx=50, pady=10)
        
        self.rad_colab = ctk.CTkRadioButton(self.frame_modo, text="☁️ Google Colab", variable=self.var_modo, value="colab")
        self.rad_colab.pack(side="left", padx=20, pady=10)

        self.lbl_status = ctk.CTkLabel(self, text="Estado: Aguardando arquivos...")
        self.lbl_status.pack(pady=(15, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate", width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(0, 15))
        
        self.btn_iniciar = ctk.CTkButton(self, text="Iniciar Processamento", height=40, font=("Arial", 14, "bold"), fg_color="green", hover_color="darkgreen", command=self.iniciar_processamento)
        self.btn_iniciar.pack(pady=5)
        
        self.lbl_versao = ctk.CTkLabel(self, text="Versão: em testes", font=("Arial", 11, "italic"), text_color="gray50")
        self.lbl_versao.pack(side="bottom", pady=5)

    def verificar_formato(self, escolha):
        if escolha == ".srt":
            self.var_estilo.set("com_tempo")
            self.rad_corrido.configure(state="disabled")
            self.rad_tempo.configure(text="Formato SRT Obrigatório")
        else:
            self.rad_corrido.configure(state="normal")
            self.rad_tempo.configure(text="Com Horários")

    def abrir_configuracoes(self):
        conf_win = ctk.CTkToplevel(self)
        conf_win.title("Configurações Avançadas")
        self.centralizar_janela(conf_win, 500, 450)
        conf_win.grab_set()
        conf_win.attributes("-topmost", True)

        ctk.CTkLabel(conf_win, text="⚙️ Opções do Sistema", font=("Arial", 18, "bold"), text_color="cyan").pack(pady=15)

        frame_tema = ctk.CTkFrame(conf_win, fg_color="transparent")
        frame_tema.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(frame_tema, text="Tema Visual:").pack(side="left")
        
        def mudar_tema(escolha):
            modo = "Dark" if escolha == "Escuro" else "Light"
            ctk.set_appearance_mode(modo)
            self.config["tema"] = modo
            self.salvar_config()
            
        tema_atual = "Escuro" if self.config.get("tema", "Dark") == "Dark" else "Claro"
        seg_tema = ctk.CTkSegmentedButton(frame_tema, values=["Escuro", "Claro"], command=mudar_tema)
        seg_tema.set(tema_atual)
        seg_tema.pack(side="right")

        frame_pasta = ctk.CTkFrame(conf_win, fg_color="transparent")
        frame_pasta.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(frame_pasta, text="Salvar Textos em:").pack(anchor="w")
        
        var_pasta = ctk.StringVar(value=self.config.get("pasta_padrao", "") or "Perguntar na Revisão")
        lbl_pasta_atual = ctk.CTkLabel(frame_pasta, textvariable=var_pasta, text_color="gray60", font=("Arial", 11, "italic"))
        lbl_pasta_atual.pack(side="left")
        
        def escolher_pasta_default():
            conf_win.attributes("-topmost", False) # Desliga para não esconder a janela do Windows
            p = filedialog.askdirectory()
            conf_win.attributes("-topmost", True)  # Religa assim que escolhe
            if p:
                self.config["pasta_padrao"] = p
                self.salvar_config()
                var_pasta.set(p)
        
        def limpar_pasta_default():
            self.config["pasta_padrao"] = ""
            self.salvar_config()
            var_pasta.set("Perguntar na Revisão")

        ctk.CTkButton(frame_pasta, text="Limpar", width=60, fg_color="#c9302c", command=limpar_pasta_default).pack(side="right", padx=(5,0))
        ctk.CTkButton(frame_pasta, text="Mudar", width=60, fg_color="gray30", command=escolher_pasta_default).pack(side="right")

        ctk.CTkLabel(conf_win, text="Desempenho (CPU Threads)", font=("Arial", 14, "bold")).pack(pady=(20, 0))
        ctk.CTkLabel(conf_win, text="Aumente para usar toda a máquina, reduza para não travar o PC", font=("Arial", 10)).pack()
        
        max_threads = os.cpu_count() or 4
        thread_atual = ctk.IntVar(value=self.config.get("threads_cpu", max_threads))
        lbl_thread_val = ctk.CTkLabel(conf_win, text=f"{thread_atual.get()} Threads", text_color="cyan")
        lbl_thread_val.pack()

        def set_thread(valor):
            t = int(float(valor))
            thread_atual.set(t)
            lbl_thread_val.configure(text=f"{t} Threads")
            self.config["threads_cpu"] = t
            self.salvar_config()

        slider = ctk.CTkSlider(conf_win, from_=1, to=max_threads, number_of_steps=max_threads-1, command=set_thread)
        slider.set(thread_atual.get())
        slider.pack(pady=10)

        ctk.CTkButton(conf_win, text="Fechar", command=conf_win.destroy).pack(pady=20)

    def mostrar_menu_ajuda(self):
        menu = tk.Menu(self, tearoff=0, bg="#2b2b2b", fg="white", font=("Arial", 10))
        menu.add_command(label="Fazer Tour Guiado", command=self.iniciar_tour)
        menu.add_command(label="Ajuda Específica", command=self.mostrar_ajuda_especifica)
        x = self.btn_ajuda.winfo_rootx()
        y = self.btn_ajuda.winfo_rooty() + self.btn_ajuda.winfo_height()
        menu.tk_popup(x, y)

    def mostrar_ajuda_especifica(self):
        ajuda_win = ctk.CTkToplevel(self)
        ajuda_win.title("Ajuda Específica")
        self.centralizar_janela(ajuda_win, 500, 350)
        ajuda_win.grab_set()
        ajuda_win.attributes("-topmost", True)
        ctk.CTkLabel(ajuda_win, text="Documentação e Ajuda", font=("Arial", 18, "bold"), text_color="cyan").pack(pady=15)
        texto = (
            "1. Formatos: Use .srt para criar legendas temporizadas ou .docx para relatórios.\n"
            "2. Vídeos: Arraste vídeos (.mp4, .mkv) diretamente. A IA processa sem precisar de extrair o áudio à mão.\n"
            "3. Revisão: Após o processamento, uma janela será aberta para corrigir eventuais erros antes de salvar o arquivo final."
        )
        ctk.CTkLabel(ajuda_win, text=texto, font=("Arial", 14), justify="left", wraplength=450).pack(padx=20, pady=10)
        ctk.CTkButton(ajuda_win, text="Fechar", width=120, command=ajuda_win.destroy).pack(pady=20)

    def iniciar_tour(self):
        self.tour_steps = [
            {"titulo": "Bem-vindo!", "texto": "Este é o audio2text da Silva. Vamos fazer um tour rápido de 4 passos."},
            {"titulo": "1. Fila de Mídia", "texto": "Arraste os seus arquivos de áudio ou VÍDEO (.mp4, .mkv) para dentro da janela!"},
            {"titulo": "2. Idiomas e Modelos", "texto": "Escolha o formato de saída (.srt para vídeos, .docx para texto). Use o botão 'i' para escolher o modelo certo."},
            {"titulo": "3. Revisão Integrada", "texto": "Assim que a IA terminar, abriremos uma janela onde poderá ler e editar o texto inteiro antes de salvar!"}
        ]
        self.tour_index = 0
        if self.config.get("primeira_vez", True):
            self.config["primeira_vez"] = False
            self.salvar_config()

        self.tour_win = ctk.CTkToplevel(self)
        self.tour_win.title("Tour Guiado")
        self.centralizar_janela(self.tour_win, 450, 300)
        self.tour_win.grab_set() 
        self.tour_win.attributes("-topmost", True)
        
        self.lbl_tour_titulo = ctk.CTkLabel(self.tour_win, text="", font=("Arial", 18, "bold"), text_color="cyan")
        self.lbl_tour_titulo.pack(pady=(20, 10))
        self.lbl_tour_texto = ctk.CTkLabel(self.tour_win, text="", font=("Arial", 14), wraplength=400, justify="center")
        self.lbl_tour_texto.pack(pady=10, padx=20)
        
        frame_nav = ctk.CTkFrame(self.tour_win, fg_color="transparent")
        frame_nav.pack(side="bottom", pady=20)
        self.btn_tour_ant = ctk.CTkButton(frame_nav, text="Anterior", width=100, command=self.tour_anterior)
        self.btn_tour_ant.pack(side="left", padx=10)
        self.btn_tour_prox = ctk.CTkButton(frame_nav, text="Próximo", width=100, command=self.tour_proximo)
        self.btn_tour_prox.pack(side="left", padx=10)
        
        self.atualizar_tour()

    def atualizar_tour(self):
        step = self.tour_steps[self.tour_index]
        self.lbl_tour_titulo.configure(text=step["titulo"])
        self.lbl_tour_texto.configure(text=step["texto"])
        self.btn_tour_ant.configure(state="normal" if self.tour_index > 0 else "disabled")
        if self.tour_index == len(self.tour_steps) - 1:
            self.btn_tour_prox.configure(text="Concluir", fg_color="green")
        else:
            self.btn_tour_prox.configure(text="Próximo", fg_color=["#3a7ebf", "#1f538d"])

    def tour_proximo(self):
        if self.tour_index < len(self.tour_steps) - 1:
            self.tour_index += 1
            self.atualizar_tour()
        else:
            self.tour_win.destroy()

    def tour_anterior(self):
        if self.tour_index > 0:
            self.tour_index -= 1
            self.atualizar_tour()

    def verificar_idioma(self, escolha):
        if escolha == "Outros...":
            self.abrir_modal_idiomas()
        self.atualizar_ui_lista()

    def abrir_modal_idiomas(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Pesquisar Idioma")
        self.centralizar_janela(modal, 350, 400)
        modal.grab_set()
        modal.attributes("-topmost", True)
        
        ctk.CTkLabel(modal, text="Escolha um idioma:", font=("Arial", 16, "bold")).pack(pady=10)
        entry_busca = ctk.CTkEntry(modal, placeholder_text="Pesquisar...", width=250)
        entry_busca.pack(pady=10)
        
        scroll_idiomas = ctk.CTkScrollableFrame(modal, width=250, height=250)
        scroll_idiomas.pack(pady=10)
        
        def preencher_lista(termo=""):
            for widget in scroll_idiomas.winfo_children():
                widget.destroy()
            for idioma in IDIOMAS_WHISPER:
                if termo.lower() in idioma.lower():
                    btn = ctk.CTkButton(scroll_idiomas, text=idioma, fg_color="transparent", hover_color="gray30", anchor="w", 
                                        command=lambda i=idioma: [self.combo_idioma.set(i), self.atualizar_ui_lista(), modal.destroy()])
                    btn.pack(fill="x", pady=2)
                    
        entry_busca.bind("<KeyRelease>", lambda e: preencher_lista(entry_busca.get()))
        preencher_lista()

    def mostrar_info_modelos(self):
        info_win = ctk.CTkToplevel(self)
        info_win.title("Sobre os Modelos")
        self.centralizar_janela(info_win, 500, 420)
        info_win.grab_set()
        info_win.attributes("-topmost", True)
        
        ctk.CTkLabel(info_win, text="Como escolher a IA perfeita?", font=("Arial", 18, "bold"), text_color="cyan").pack(pady=15)
        texto = (
            "Atenção: O download ocorre apenas na 1ª vez que usar o modelo.\n\n"
            "• tiny/base (~75MB a 145MB): Download quase instantâneo e uso rápido. Pode errar pontuações.\n\n"
            "• small (~480MB): Bom equilíbrio para áudios limpos.\n\n"
            "• medium (~1.5GB): Ideal para o seu PC. Excelente precisão.\n\n"
            "• large-v3 (~3GB): A melhor do mercado. Use apenas quando for exportar para o Google Colab."
        )
        ctk.CTkLabel(info_win, text=texto, font=("Arial", 14), justify="left", wraplength=450).pack(padx=20, pady=10, anchor="w")
        ctk.CTkButton(info_win, text="Entendi", width=120, command=info_win.destroy).pack(pady=20)

    def on_drop(self, event):
        arquivos = self.tk.splitlist(event.data)
        for f in arquivos:
            if f.lower().endswith(EXTENSOES_SUPORTADAS):
                self.adicionar_na_lista(f)

    def add_audio(self):
        tipos = [("Arquivos Suportados", "*.mp3 *.wav *.m4a *.mp4 *.mkv *.avi *.mov")]
        arquivos = filedialog.askopenfilenames(filetypes=tipos)
        for f in arquivos:
            self.adicionar_na_lista(f)

    def adicionar_na_lista(self, caminho):
        if caminho not in self.audio_files:
            self.audio_files.append(caminho)
            self.atualizar_ui_lista()

    def atualizar_ui_lista(self):
        for widget in self.scroll_arquivos.winfo_children():
            widget.destroy()
            
        idioma = self.combo_idioma.get()
        pasta_global = self.config.get("pasta_padrao", "")
            
        for caminho in self.audio_files:
            nome = os.path.basename(caminho)
            ext = nome.split('.')[-1].upper()
            
            cartao = ctk.CTkFrame(self.scroll_arquivos, fg_color="gray25", corner_radius=8)
            cartao.pack(fill="x", pady=2, padx=5)
            
            icone = "🎬" if ext in ["MP4", "MKV", "AVI", "MOV"] else "🎵"
            
            ctk.CTkLabel(cartao, text=f"{icone} {ext}", text_color="cyan", font=("Arial", 12, "bold")).pack(side="left", padx=(10, 5))
            ctk.CTkLabel(cartao, text=nome, font=("Arial", 12, "bold")).pack(side="left", padx=(0, 5))
            ctk.CTkLabel(cartao, text=f"({idioma})", text_color="gray60", font=("Arial", 11)).pack(side="left", padx=(0, 5))
            
            if pasta_global:
                ctk.CTkLabel(cartao, text=f"-> {pasta_global}", text_color="gray50", font=("Arial", 10, "italic")).pack(side="left", padx=(5, 10), fill="x", expand=True)
            else:
                ctk.CTkLabel(cartao, text=caminho, text_color="gray50", font=("Arial", 10, "italic")).pack(side="left", padx=(5, 10), fill="x", expand=True)
            
            ctk.CTkButton(cartao, text="X", width=30, fg_color="#c9302c", hover_color="#ac2925", command=lambda c=caminho: self.remover_da_lista(c)).pack(side="right", padx=10, pady=5)

    def remover_da_lista(self, caminho):
        self.audio_files.remove(caminho)
        self.atualizar_ui_lista()

    def iniciar_processamento(self):
        if not self.audio_files:
            messagebox.showerror("Erro", "A fila está vazia! Adicione pelo menos um arquivo.")
            return
            
        if self.var_modo.get() == "colab":
            pasta_colab = filedialog.askdirectory(title="Onde deseja salvar os arquivos do Colab?")
            if pasta_colab:
                self.btn_iniciar.configure(state="disabled")
                self.progress_bar.set(0.5)
                self.lbl_status.configure(text="Preparando exportação para o Colab...")
                sucesso, msg = exportar_colab(self.audio_files, pasta_colab)
                if sucesso:
                    self.lbl_status.configure(text="Exportação concluída!")
                    self.progress_bar.set(1.0)
                    messagebox.showinfo("Sucesso", f"Arquivos exportados para:\n{pasta_colab}")
                else:
                    self.lbl_status.configure(text="Erro na exportação.")
                    messagebox.showerror("Erro", msg)
                self.btn_iniciar.configure(state="normal")
        else:
            self.executar_ia_local()

    def executar_ia_local(self):
        self.btn_iniciar.configure(state="disabled")
        self.progress_bar.set(0)
        
        def update_status(msg):
            self.lbl_status.configure(text=msg)
            
        def update_progress(valor):
            self.progress_bar.set(valor)
            
        def finalizado(resultados):
            self.lbl_status.configure(text="Processamento concluído. Abrindo Janela de Revisão...")
            self.btn_iniciar.configure(state="normal")
            self.progress_bar.set(1.0)
            self.abrir_janela_revisao(resultados)
            
        def com_erro(erro):
            self.lbl_status.configure(text="Erro no processamento.")
            self.btn_iniciar.configure(state="normal")
            messagebox.showerror("Erro", erro)
            
        processar_audios_local(
            self.audio_files,
            self.combo_modelo.get(),
            self.combo_idioma.get(),
            self.var_traduzir.get(),
            self.combo_formato.get(),
            self.var_estilo.get(),
            self.config.get("threads_cpu", 4),
            update_status,
            update_progress,
            finalizado,
            com_erro
        )

    def abrir_janela_revisao(self, resultados):
        self.resultados_revisao = resultados
        self.idx_atual = 0
        
        self.rev_win = ctk.CTkToplevel(self)
        self.rev_win.title("Revisão Final e Exportação")
        self.centralizar_janela(self.rev_win, 900, 600)
        self.rev_win.grab_set()
        self.rev_win.attributes("-topmost", True)
        
        frame_esq = ctk.CTkFrame(self.rev_win, width=250)
        frame_esq.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(frame_esq, text="Arquivos", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.scroll_rev = ctk.CTkScrollableFrame(frame_esq, width=230)
        self.scroll_rev.pack(fill="both", expand=True)
        
        self.botoes_rev = []
        
        frame_dir = ctk.CTkFrame(self.rev_win)
        frame_dir.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.lbl_nome_edicao = ctk.CTkLabel(frame_dir, text="", font=("Arial", 16, "bold"), text_color="cyan")
        self.lbl_nome_edicao.pack(pady=10)
        
        self.txt_editor = ctk.CTkTextbox(frame_dir, wrap="word", font=("Arial", 13))
        self.txt_editor.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.btn_salvar_atual = ctk.CTkButton(frame_dir, text="Exportar Este Arquivo", height=40, fg_color="green", hover_color="darkgreen", command=self.exportar_arquivo_atual)
        self.btn_salvar_atual.pack(pady=10)
        
        self.construir_lista_revisao()
        self.carregar_texto_revisao(0)

    def construir_lista_revisao(self):
        for widget in self.scroll_rev.winfo_children():
            widget.destroy()
        self.botoes_rev.clear()
        
        for i, res in enumerate(self.resultados_revisao):
            status = "✔️ Salvo" if res["salvo"] else "✏️ Pendente"
            cor = "green" if res["salvo"] else "gray30"
            
            btn = ctk.CTkButton(
                self.scroll_rev, text=f"{res['nome_base']}\n({status})",
                fg_color=cor, anchor="w",
                command=lambda idx=i: self.trocar_arquivo_revisao(idx)
            )
            btn.pack(fill="x", pady=2)
            self.botoes_rev.append(btn)

    def trocar_arquivo_revisao(self, novo_idx):
        texto_editado = self.txt_editor.get("1.0", "end-1c")
        self.resultados_revisao[self.idx_atual]["texto"] = texto_editado
        self.carregar_texto_revisao(novo_idx)

    def carregar_texto_revisao(self, idx):
        self.idx_atual = idx
        res = self.resultados_revisao[idx]
        
        self.lbl_nome_edicao.configure(text=f"Editando: {res['nome_base']}")
        
        self.txt_editor.delete("1.0", "end")
        self.txt_editor.insert("1.0", res["texto"])
        
        for i, btn in enumerate(self.botoes_rev):
            if i == idx:
                btn.configure(border_width=2, border_color="cyan")
            else:
                btn.configure(border_width=0)

    def exportar_arquivo_atual(self):
        res = self.resultados_revisao[self.idx_atual]
        texto_final = self.txt_editor.get("1.0", "end-1c")
        res["texto"] = texto_final
        
        formato = self.combo_formato.get()
        pasta = self.config.get("pasta_padrao", "")
        
        if not pasta or not os.path.exists(pasta):
            self.rev_win.attributes("-topmost", False) # Desliga para não esconder o explorador
            pasta = filedialog.askdirectory(title=f"Onde salvar {res['nome_base']}?")
            self.rev_win.attributes("-topmost", True)  # Religa logo em seguida
            if not pasta:
                return 
                
        sucesso, msg = salvar_documento(pasta, res["nome_base"], texto_final, formato)
        
        if sucesso:
            res["salvo"] = True
            self.construir_lista_revisao()
            self.carregar_texto_revisao(self.idx_atual)
            
            # Tira o topmost temporariamente para exibir as messageboxes com tranquilidade
            self.rev_win.attributes("-topmost", False)
            messagebox.showinfo("Sucesso", f"Salvo em:\n{msg}")
            
            todos_salvos = all(r["salvo"] for r in self.resultados_revisao)
            if todos_salvos:
                if messagebox.askyesno("Concluído", "Todos os arquivos foram exportados. Deseja fechar o revisor?"):
                    self.rev_win.destroy()
                else:
                    self.rev_win.attributes("-topmost", True)
            else:
                self.rev_win.attributes("-topmost", True)
        else:
            self.rev_win.attributes("-topmost", False)
            messagebox.showerror("Erro ao Salvar", msg)
            self.rev_win.attributes("-topmost", True)