import tkinter as tk
import random
import threading

# Conjunto de frases de exemplo
EXAMPLES = [
    "Eu te amo muito.",
    "A beleza do mundo é incrível.",
    "Sinto que nunca vou parar de amar você.",
    "Cada dia é uma nova oportunidade.",
    "Você faz parte da minha vida.",
    "A amizade é um tesouro precioso.",
    "Estou sempre aqui para você.",
    "Meu coração pertence a você."
]

# Dicionário de palavras em português (simplificado)
PALAVRAS = [
    "eu", "te", "amo", "gosto", "de", "muito", "você", "a", "sua", "beleza",
    "é", "maravilhosa", "sempre", "minha", "vida", "com", "isso", "me",
    "faz", "feliz", "sinto", "que", "nunca", "vou", "parar", "mais", "hoje",
    "amanhã", "todo", "dia", "amizade", "tesouro", "precioso", "parte", "coração"
]

class BabelLibrary:
    def __init__(self):
        self.target_text = ""
        self.running = False
        self.result = None
        self.generated_texts = set()  # Armazena textos já gerados
        self.contextual_words = self.create_contextual_words()

    def create_contextual_words(self):
        """ Cria um dicionário de palavras com base em exemplos. """
        contextual = {}
        for phrase in EXAMPLES:
            words = phrase.lower().split()
            for i in range(len(words)):
                if words[i] not in contextual:
                    contextual[words[i]] = []
                if i > 0:
                    contextual[words[i]].append(words[i - 1])  # Palavra anterior
                if i < len(words) - 1:
                    contextual[words[i]].append(words[i + 1])  # Palavra seguinte
        return contextual

    def generate_contextual_text(self, target_length):
        """ Gera um texto considerando a contextualização das palavras. """
        generated = []
        first_word = random.choice(PALAVRAS)
        generated.append(first_word)

        for _ in range(target_length - 1):
            last_word = generated[-1]
            next_words = self.contextual_words.get(last_word, PALAVRAS)  # Escolhe palavras relacionadas ou aleatórias
            next_word = random.choice(next_words)
            generated.append(next_word)

        return ' '.join(generated)

    def directed_search(self, target_text):
        """ Realiza uma busca inteligente para encontrar a frase desejada. """
        self.target_text = target_text
        self.running = True
        room, shelf, book = 0, 0, 0
        target_length = len(target_text.split())

        while self.running:
            # Gera textos com comprimento baseado em contexto
            generated_text = self.generate_contextual_text(random.randint(5, 20))

            # Atualizar localização
            book += 1
            if book > 1000:
                book = 0
                shelf += 1
            if shelf > 100:
                shelf = 0
                room += 1

            # Verificar se o texto gerado contém o texto-alvo
            if target_text in generated_text:
                self.result = {
                    "room": room,
                    "shelf": shelf,
                    "book": book,
                    "generated_text": generated_text
                }
                self.running = False
                return

            # Adiciona o texto à coleção de textos gerados
            self.generated_texts.add(generated_text)

            # Otimização: se a coleção de textos gerados for muito grande, reinicia
            if len(self.generated_texts) > 10000:
                self.generated_texts.clear()

class BabelGUI:
    def __init__(self, master):
        self.master = master
        master.title("Biblioteca de Babel")

        self.library = BabelLibrary()

        self.label = tk.Label(master, text="Informe o texto que deseja buscar:")
        self.label.pack()

        self.entry = tk.Entry(master)
        self.entry.pack()

        self.search_button = tk.Button(master, text="Buscar", command=self.start_search)
        self.search_button.pack()

        self.result_label = tk.Label(master, text="", wraplength=300)
        self.result_label.pack()

        self.progress_label = tk.Label(master, text="")
        self.progress_label.pack()

    def start_search(self):
        self.result_label.config(text="")
        self.progress_label.config(text="Procurando...")
        target_text = self.entry.get().strip().lower()

        # Iniciar a busca em uma thread separada
        search_thread = threading.Thread(target=self.search_text, args=(target_text,))
        search_thread.start()

    def search_text(self, target_text):
        self.library.directed_search(target_text)
        self.display_result()

    def display_result(self):
        if self.library.result:
            result = self.library.result
            self.result_label.config(text=f"Texto encontrado!\n"
                                           f"Sala: {result['room']}, Estante: {result['shelf']}, Livro: {result['book']}")
            self.show_full_page(result['generated_text'])  # Mostrar a página completa
        else:
            self.result_label.config(text="Texto não encontrado.")
        self.progress_label.config(text="")

    def show_full_page(self, full_text):
        """ Cria uma nova janela para exibir o texto completo encontrado. """
        full_text_window = tk.Toplevel(self.master)
        full_text_window.title("Texto Completo Encontrado")

        text_box = tk.Text(full_text_window, wrap=tk.WORD)
        text_box.pack(expand=True, fill=tk.BOTH)

        text_box.insert(tk.END, full_text)
        text_box.config(state=tk.DISABLED)  # Torna o texto não editável

if __name__ == "__main__":
    root = tk.Tk()
    gui = BabelGUI(root)
    root.mainloop()
#asodkaowkdoakdokdijwiojw