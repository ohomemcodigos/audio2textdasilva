import os
from interface import Audio2TextApp

#ponto de entrada da aplicacao
def main():
    app = Audio2TextApp()
    caminho_icone = "audio2textdaSilva.ico"
    if os.path.exists(caminho_icone):
        app.iconbitmap(caminho_icone)
    app.mainloop()

if __name__ == "__main__":
    main()