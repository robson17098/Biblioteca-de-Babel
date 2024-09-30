import random
import string
import numpy as np
import tkinter as tk
from tkinter import scrolledtext, ttk
from concurrent.futures import ThreadPoolExecutor
import threading

# Definindo a quantidade máxima de livros para busca
MAX_LIVROS = 100000  # Número teórico de livros a serem explorados na busca
NUM_THREADS = 4  # Número de threads para paralelismo

# Funções de geração de textos usando NumPy
def gerar_pagina_numpy(num_caracteres=1000):
    """Gera uma página com caracteres aleatórios usando NumPy"""
    caracteres = np.array(list(string.ascii_letters + string.digits + string.punctuation + " "))
    pagina = ''.join(np.random.choice(caracteres, num_caracteres))
    return pagina

def gerar_livro_numpy(num_paginas=10, num_caracteres_por_pagina=1000):
    """Gera um livro com múltiplas páginas usando NumPy"""
    return [gerar_pagina_numpy(num_caracteres_por_pagina) for _ in range(num_paginas)]

# Classe para a Biblioteca de Babel infinita
class BibliotecaBabel:
    def __init__(self):
        """Inicializa uma biblioteca infinita"""
        self.cache = {}

    def acessar_livro(self, corredor, prateleira):
        """Gera ou acessa um livro específico da biblioteca"""
        chave = (corredor, prateleira)
        if chave not in self.cache:
            # Se o livro ainda não foi gerado, cria e armazena no cache
            self.cache[chave] = gerar_livro_numpy()
        return self.cache[chave]

# Classe para a navegação na Biblioteca
class NavegacaoBiblioteca:
    def __init__(self, biblioteca):
        self.biblioteca = biblioteca
        self.lock = threading.Lock()  # Para garantir que as threads não acessem simultaneamente o cache

    def acessar_livro(self, corredor, prateleira):
        """Acessa um livro por corredor e prateleira"""
        with self.lock:
            livro = self.biblioteca.acessar_livro(corredor, prateleira)
            return livro

    def buscar_palavra_em_subdivisao(self, termo, corredor_start, corredor_end, prateleira_start, prateleira_end, callback_atualizar_progresso, total_livros, resultados):
        """Busca em uma subdivisão específica da biblioteca"""
        total_livros_verificados = 0

        for corredor in range(corredor_start, corredor_end):
            for prateleira in range(prateleira_start, prateleira_end):
                livro = self.acessar_livro(corredor, prateleira)
                for i, pagina in enumerate(livro):
                    if termo in pagina:
                        with self.lock:
                            resultados.append((corredor, prateleira, i, pagina))
                        return
                # Atualiza a barra de progresso a cada livro verificado
                total_livros_verificados += 1
                progresso = (total_livros_verificados / total_livros) * 100
                callback_atualizar_progresso(progresso)

    def buscar_palavra_global(self, termo, callback_atualizar_progresso):
        """Divide a busca global em threads e usa processamento em quadrantes"""
        total_livros = MAX_LIVROS
        num_corredores = total_livros // 10

        # Dividindo a busca em quadrantes lógicos
        subdivisoes = [
            (0, num_corredores // 2, 0, 5),  # Primeiro quadrante
            (0, num_corredores // 2, 5, 10),  # Segundo quadrante
            (num_corredores // 2, num_corredores, 0, 5),  # Terceiro quadrante
            (num_corredores // 2, num_corredores, 5, 10),  # Quarto quadrante
        ]

        resultados = []

        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futuros = []
            for subdivisao in subdivisoes:
                corredor_start, corredor_end, prateleira_start, prateleira_end = subdivisao
                futuros.append(executor.submit(self.buscar_palavra_em_subdivisao, termo, corredor_start, corredor_end, prateleira_start, prateleira_end, callback_atualizar_progresso, total_livros, resultados))

            for futuro in futuros:
                futuro.result()

        if resultados:
            return resultados[0]  # Retorna o primeiro resultado encontrado
        else:
            return None  # Não encontrado

# Interface Gráfica usando Tkinter
class InterfaceBiblioteca:
    def __init__(self, raiz, navegacao):
        self.navegacao = navegacao
        self.raiz = raiz
        self.raiz.title("Biblioteca de Babel")

        # Labels
        self.label_busca = tk.Label(raiz, text="Buscar Termo:")
        self.label_busca.grid(row=0, column=0)

        # Campo de entrada para o termo de busca
        self.busca_input = tk.Entry(raiz)
        self.busca_input.grid(row=0, column=1)

        # Botão de busca global
        self.botao_buscar = tk.Button(raiz, text="Buscar Globalmente", command=self.iniciar_busca_em_thread)
        self.botao_buscar.grid(row=1, column=0, columnspan=2)

        # Barra de progresso
        self.progresso = ttk.Progressbar(raiz, orient="horizontal", length=400, mode="determinate")
        self.progresso.grid(row=2, column=0, columnspan=2)
        
        # Texto para exibir o progresso em porcentagem
        self.label_progresso = tk.Label(raiz, text="Progresso: 0%")
        self.label_progresso.grid(row=3, column=0, columnspan=2)

        # Área de texto para exibir o resultado
        self.resultado_texto = scrolledtext.ScrolledText(raiz, width=60, height=20)
        self.resultado_texto.grid(row=4, column=0, columnspan=2)

    def atualizar_progresso(self, progresso):
        """Atualiza a barra de progresso e a label de porcentagem"""
        self.progresso['value'] = progresso
        self.label_progresso.config(text=f"Progresso: {progresso:.2f}%")
        self.raiz.update_idletasks()

    def buscar_termo_global(self):
        """Realiza a busca global de um termo e mostra os resultados"""
        termo = self.busca_input.get()
        self.resultado_texto.delete(1.0, tk.END)  # Limpa o campo de texto

        resultado = self.navegacao.buscar_palavra_global(termo, self.atualizar_progresso)

        if resultado:
            corredor, prateleira, pagina_num, pagina = resultado
            self.resultado_texto.insert(tk.END, f"Termo '{termo}' encontrado:\n")
            self.resultado_texto.insert(tk.END, f"Corredor: {corredor}, Prateleira: {prateleira}, Página: {pagina_num + 1}\n")
            self.resultado_texto.insert(tk.END, f"Conteúdo da Página:\n{pagina}\n")
        else:
            self.resultado_texto.insert(tk.END, f"Termo '{termo}' não encontrado em {MAX_LIVROS} livros.")

    def iniciar_busca_em_thread(self):
        """Inicia a busca em uma thread separada para não travar a interface"""
        thread_busca = threading.Thread(target=self.buscar_termo_global)
        thread_busca.start()

# Inicializando a biblioteca infinita
biblioteca = BibliotecaBabel()
navegacao = NavegacaoBiblioteca(biblioteca)

# Inicializando a interface gráfica
raiz = tk.Tk()
app = InterfaceBiblioteca(raiz, navegacao)
raiz.mainloop()
