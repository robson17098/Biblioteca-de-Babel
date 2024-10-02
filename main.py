import sys
import random
import string
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal

def gerar_palavras(num_palavras: int):
    """
    Gera uma lista de palavras aleatórias utilizando um modelo de Markov.
    """
    palavras = []
    for _ in range(num_palavras):
        tamanho = random.randint(3, 8)  # Palavras com comprimento entre 3 e 8
        palavra = ''.join(random.choices(string.ascii_lowercase, k=tamanho))
        palavras.append(palavra)
    return palavras

class Livro:
    def __init__(self, id: int, num_paginas: int):
        self.id = id
        self.paginas = self.gerar_paginas(num_paginas)

    def gerar_paginas(self, num_paginas: int):
        palavras = gerar_palavras(num_paginas * 500)  # Gera todas as palavras de uma vez
        return [self.gerar_pagina(i + 1, palavras) for i in range(num_paginas)]

    def gerar_pagina(self, numero: int, palavras):
        start_index = (numero - 1) * 500
        end_index = numero * 500
        return f"Página {numero}:\n" + ' '.join(palavras[start_index:end_index])

class Biblioteca:
    def __init__(self, num_paginas_por_livro: int):
        self.num_paginas_por_livro = num_paginas_por_livro
        self.livros = []

    def gerar_livro(self, id: int):
        livro = Livro(id, self.num_paginas_por_livro)
        self.livros.append(livro)
        return livro

    def pesquisar_palavra(self, palavra: str):
        resultados = []
        for livro in self.livros:
            for pagina in livro.paginas:
                if palavra in pagina:
                    resultados.append((livro.id, pagina))
        return resultados

class Worker(QThread):
    progress_changed = pyqtSignal(int)
    text_updated = pyqtSignal(str)

    def __init__(self, biblioteca, palavra):
        super().__init__()
        self.biblioteca = biblioteca
        self.palavra = palavra

    def run(self):
        for i in range(60):
            livro = self.biblioteca.gerar_livro(i)
            self.progress_changed.emit(int((i + 1) * 100 / 60))

            if i % 5 == 0:
                self.text_updated.emit(f'\nCriando livro {livro.id}...\n')
                random_palavras = gerar_palavras(10)  # Gera 10 palavras aleatórias
                self.text_updated.emit("Palavras geradas: " + ', '.join(random_palavras) + "\n")

            resultados = self.biblioteca.pesquisar_palavra(self.palavra)
            if resultados:
                for id_livro, pagina in resultados:
                    self.text_updated.emit(f"Palavra '{self.palavra}' encontrada no Livro {id_livro}:\n{pagina}\n\n")
                return

        self.text_updated.emit(f"A palavra '{self.palavra}' não foi encontrada em nenhum livro.\n")

class BibliotecaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.biblioteca = Biblioteca(num_paginas_por_livro=5000)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Biblioteca de Babel Infinita')

        self.layout = QVBoxLayout()

        self.label = QLabel('Pesquise por uma palavra:')
        self.layout.addWidget(self.label)

        self.entry = QLineEdit(self)
        self.layout.addWidget(self.entry)

        self.search_button = QPushButton('Pesquisar', self)
        self.search_button.clicked.connect(self.pesquisar)
        self.layout.addWidget(self.search_button)

        self.progress = QProgressBar(self)
        self.progress.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.progress)

        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.layout.addWidget(self.text_area)

        self.setLayout(self.layout)

    def pesquisar(self):
        palavra = self.entry.text().strip()
        if not palavra:
            QMessageBox.warning(self, 'Aviso', 'Por favor, insira uma palavra para pesquisar.')
            return

        self.text_area.clear()
        self.progress.setValue(0)

        self.worker = Worker(self.biblioteca, palavra)
        self.worker.progress_changed.connect(self.progress.setValue)
        self.worker.text_updated.connect(self.text_area.append)
        self.worker.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BibliotecaApp()
    window.show()
    sys.exit(app.exec_())
