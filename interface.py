import customtkinter as ctk
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import json

#lista de idiomas suportados pelo whisper para a aba de pesquisa
IDIOMAS_WHISPER = [
    "Alemão", "Árabe", "Coreano", "Chinês", "Dinamarquês", "Francês", 
    "Grego", "Hebraico", "Holandês", "Hindi", "Indonésio", "Italiano", 
    "Japonês", "Polonês", "Russo", "Sueco", "Turco", "Ucraniano", "Vietnamita"
]

#classe base para juntar customtkinter com drag and drop
class AppRoot(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

class Audio2TextApp(AppRoot):
    def __init__(self):
        super().__init__()
        self.title("audio2text da Silva")
        self.geometry("750x750")
        
        #define o tema escuro
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        #carrega configuracoes (verifica se e a primeira vez)
        self.config_file = "config.json"
        self.config = self.carregar_config()
        
        #lista de ficheiros sem limite
        self.audio_files = []
        
        self.setup_ui()
        
        #inicia o tour automaticamente se for a primeira vez
        if self.config.get("primeira_vez", True):
            #delay de 500ms para a janela principal carregar antes de abrir o modal
            self.after(500, self.iniciar_tour)

    def carregar_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"primeira_vez": True}

    def salvar_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f)

    #funcao utilitaria para prender as modais exatamente no meio da janela principal
    def centralizar_janela(self, janela, largura, altura):
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (largura // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (altura // 2)
        janela.geometry(f"{largura}x{altura}+{x}+{y}")

    def setup_ui(self):
        # --- barra superior elegante ---
        self.frame_topo = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.frame_topo.pack(fill="x", padx=20, pady=(10, 0))
        
        #o botao agora chama a funcao que abre o menu dropdown
        self.btn_ajuda = ctk.CTkButton(self.frame_topo, text="❓ Ajuda", width=100, fg_color="gray30", hover_color="gray40", command=self.mostrar_menu_ajuda)
        self.btn_ajuda.pack(side="right")

        # --- area de drag and drop e fila ---
        self.frame_fila = ctk.CTkFrame(self)
        self.frame_fila.pack(padx=20, pady=10, fill="x")
        
        self.lbl_fila = ctk.CTkLabel(self.frame_fila, text="Arraste os áudios aqui ou clique no botão", font=("Arial", 16))
        self.lbl_fila.pack(pady=10)
        
        self.btn_add = ctk.CTkButton(self.frame_fila, text="Adicionar Áudios", command=self.add_audio)
        self.btn_add.pack(pady=5)
        
        #scroll sem limites
        self.scroll_arquivos = ctk.CTkScrollableFrame(self.frame_fila, height=150)
        self.scroll_arquivos.pack(padx=10, pady=10, fill="x")
        
        #registar areas de drop
        self.frame_fila.drop_target_register(DND_FILES)
        self.frame_fila.dnd_bind('<<Drop>>', self.on_drop)
        self.scroll_arquivos.drop_target_register(DND_FILES)
        self.scroll_arquivos.dnd_bind('<<Drop>>', self.on_drop)
        
        # --- configuracoes ---
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.pack(padx=20, pady=10, fill="x")
        
        #idioma com gatilho para o modal
        self.lbl_idioma = ctk.CTkLabel(self.frame_config, text="Idioma Original:")
        self.lbl_idioma.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.combo_idioma = ctk.CTkComboBox(self.frame_config, values=["Automático", "Português", "Inglês", "Espanhol", "Outros..."], command=self.verificar_idioma)
        self.combo_idioma.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        #modelo e icone elegante ajustado (letra 'i' nativa em vez de caractere especial borrado)
        self.lbl_modelo = ctk.CTkLabel(self.frame_config, text="Modelo de IA:")
        self.lbl_modelo.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        
        frame_mod = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        frame_mod.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        self.combo_modelo = ctk.CTkComboBox(frame_mod, values=["tiny", "base", "small", "medium", "large-v3"])
        self.combo_modelo.set("medium")
        self.combo_modelo.pack(side="left", padx=(0, 5))
        
        self.btn_info = ctk.CTkButton(frame_mod, text=" i ", width=28, corner_radius=14, font=("Arial", 14, "bold"), fg_color="gray30", text_color="cyan", hover_color="gray40", command=self.mostrar_info_modelos)
        self.btn_info.pack(side="left")
        
        #traducao
        self.var_traduzir = ctk.BooleanVar()
        self.chk_traduzir = ctk.CTkCheckBox(self.frame_config, text="Traduzir texto final para Português", variable=self.var_traduzir)
        self.chk_traduzir.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        # --- modo de processamento ---
        self.frame_modo = ctk.CTkFrame(self)
        self.frame_modo.pack(padx=20, pady=10, fill="x")
        
        self.lbl_modo = ctk.CTkLabel(self.frame_modo, text="Onde deseja processar os ficheiros?", font=("Arial", 14, "bold"))
        self.lbl_modo.pack(pady=10)
        
        self.var_modo = ctk.StringVar(value="local")
        self.rad_local = ctk.CTkRadioButton(self.frame_modo, text="🖥️ PC Local", variable=self.var_modo, value="local")
        self.rad_local.pack(side="left", padx=50, pady=10)
        
        self.rad_colab = ctk.CTkRadioButton(self.frame_modo, text="☁️ Google Colab", variable=self.var_modo, value="colab")
        self.rad_colab.pack(side="left", padx=20, pady=10)
        
        # --- botao iniciar ---
        self.btn_iniciar = ctk.CTkButton(self, text="Iniciar Processamento", height=40, font=("Arial", 14, "bold"), fg_color="green", hover_color="darkgreen", command=self.iniciar_processamento)
        self.btn_iniciar.pack(pady=20)

    # --- logica dos menus e modais customizadas ---

    def mostrar_menu_ajuda(self):
        #cria um menu dropdown nativo do tkinter
        menu = tk.Menu(self, tearoff=0, bg="#2b2b2b", fg="white", font=("Arial", 10))
        menu.add_command(label="Fazer Tour Guiado", command=self.iniciar_tour)
        menu.add_command(label="Ajuda Específica", command=self.mostrar_ajuda_especifica)
        
        #calcula a posicao exata debaixo do botao
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
            "1. Limites: Não há limite de quantidade de ficheiros na fila.\n"
            "2. Tradução: O aplicativo usa a internet para traduzir textos. Se estiver offline, desmarque a opção.\n"
            "3. Exportação Colab: Útil quando tem ficheiros enormes e o seu PC está lento. Gera um script para rodar no Google."
        )
        ctk.CTkLabel(ajuda_win, text=texto, font=("Arial", 14), justify="left", wraplength=450).pack(padx=20, pady=10)
        ctk.CTkButton(ajuda_win, text="Fechar", width=120, command=ajuda_win.destroy).pack(pady=20)

    def iniciar_tour(self):
        self.tour_steps = [
            {"titulo": "Bem-vindo!", "texto": "Este é o audio2text da Silva. Vamos fazer um tour rápido de 4 passos para aprender a usá-lo."},
            {"titulo": "1. Fila de Áudios", "texto": "Você pode clicar no botão para adicionar ficheiros ou simplesmente arrastar os seus áudios (.mp3, .wav) diretamente para dentro da janela!"},
            {"titulo": "2. Idiomas e Modelos", "texto": "Selecione o idioma para acelerar a IA. Se precisar de outro idioma, clique em 'Outros...'. Use o botão 'i' para escolher o melhor modelo para o seu PC."},
            {"titulo": "3. Exportação Inteligente", "texto": "Ao clicar em Iniciar, o app vai perguntar onde deseja salvar. Se o seu PC for lento, escolha o Modo Colab para gerar um ficheiro e rodar na nuvem grátis!"}
        ]
        self.tour_index = 0
        
        #atualiza config para nao mostrar mais na inicializacao
        if self.config.get("primeira_vez", True):
            self.config["primeira_vez"] = False
            self.salvar_config()

        self.tour_win = ctk.CTkToplevel(self)
        self.tour_win.title("Tour Guiado")
        
        #aumentamos a altura de 250 para 300 e centralizamos
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
                                        command=lambda i=idioma: [self.combo_idioma.set(i), modal.destroy()])
                    btn.pack(fill="x", pady=2)
                    
        entry_busca.bind("<KeyRelease>", lambda e: preencher_lista(entry_busca.get()))
        preencher_lista()

    def mostrar_info_modelos(self):
        info_win = ctk.CTkToplevel(self)
        info_win.title("Sobre os Modelos")
        #aumentamos a altura para 380 para evitar cortes
        self.centralizar_janela(info_win, 450, 380)
        info_win.grab_set()
        info_win.attributes("-topmost", True)
        
        ctk.CTkLabel(info_win, text="Como escolher o Modelo certo?", font=("Arial", 18, "bold"), text_color="cyan").pack(pady=15)
        
        texto = (
            "• tiny/base: Rápido, mas pode errar pontuações.\n\n"
            "• small: Bom equilíbrio para áudios limpos.\n\n"
            "• medium: Ideal para PCs como o seu (Ryzen 5). Excelente precisão.\n\n"
            "• large-v3: A melhor do mercado. Use quando for exportar para o Google Colab."
        )
        #adicionado wraplength para forcar quebra de linha
        ctk.CTkLabel(info_win, text=texto, font=("Arial", 14), justify="left", wraplength=400).pack(padx=20, pady=10, anchor="w")
        
        ctk.CTkButton(info_win, text="Entendi", width=120, command=info_win.destroy).pack(pady=20)

    # --- funcoes de lista e arquivos ---

    def on_drop(self, event):
        arquivos = self.tk.splitlist(event.data)
        for f in arquivos:
            if f.lower().endswith(('.mp3', '.wav', '.m4a')):
                self.adicionar_na_lista(f)

    def add_audio(self):
        from tkinter import filedialog
        arquivos = filedialog.askopenfilenames(filetypes=[("Arquivos de Áudio", "*.mp3 *.wav *.m4a")])
        for f in arquivos:
            self.adicionar_na_lista(f)

    def adicionar_na_lista(self, caminho):
        if caminho not in self.audio_files:
            self.audio_files.append(caminho)
            self.atualizar_ui_lista()

    def atualizar_ui_lista(self):
        for widget in self.scroll_arquivos.winfo_children():
            widget.destroy()
            
        for caminho in self.audio_files:
            nome = os.path.basename(caminho)
            ext = nome.split('.')[-1].upper()
            
            cartao = ctk.CTkFrame(self.scroll_arquivos, fg_color="gray25", corner_radius=8)
            cartao.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(cartao, text=f"🎵 {ext}", text_color="cyan", font=("Arial", 12, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(cartao, text=nome).pack(side="left", padx=10)
            
            ctk.CTkButton(cartao, text="X", width=30, fg_color="#c9302c", hover_color="#ac2925", command=lambda c=caminho: self.remover_da_lista(c)).pack(side="right", padx=10, pady=5)

    def remover_da_lista(self, caminho):
        self.audio_files.remove(caminho)
        self.atualizar_ui_lista()

    def iniciar_processamento(self):
        print("Lógica de salvar e IA pendentes para a próxima fase.")