import tkinter as tk
from tkinter import ttk
import random
import threading
import time
import re
from collections import defaultdict, Counter

class MarkovModel:
    """Modelo de Cadeia de Markov para geração de texto a partir de frases."""

    def __init__(self, frases_file):
        self.frases_file = frases_file
        self.chain = defaultdict(list)
        self.is_loaded = False
        self.rewards = []  # Armazenar recompensas

    def load_phrases(self):
        """Carrega frases do arquivo e constrói a cadeia de Markov."""
        print("Iniciando o carregamento das frases...")
        try:
            with open(self.frases_file, 'r', encoding='utf-8') as f:
                content = f.read()
                phrases = [line.strip().lower() for line in re.split(r'[,\n]', content) if line.strip()]

            print(f"Total de frases carregadas: {len(phrases)}")

            for phrase in phrases:
                words = self.preprocess_phrase(phrase)
                self.build_chain(words)

            self.is_loaded = True
            print("Modelo de Cadeias de Markov carregado com sucesso!")
        except FileNotFoundError:
            print("Erro: O arquivo de frases não foi encontrado.")
        except Exception as e:
            print(f"Erro ao carregar frases: {e}")

    def preprocess_phrase(self, phrase):
        """Limpa e separa as palavras da frase, normalizando-as."""
        words = re.findall(r'\b\w+\b', phrase)
        return [word for word in words if word]

    def build_chain(self, words):
        """Constrói a cadeia de Markov a partir de uma lista de palavras."""
        for i in range(len(words) - 1):
            context = ' '.join(words[max(0, i - 3):i + 1])  # Aumenta o contexto para 3 palavras
            self.chain[context].append(words[i + 1])

    def suggest_words(self, context):
        """Sugere palavras com base no contexto."""
        return Counter(self.chain.get(context, [])).most_common(5)  # Sugere as 5 palavras mais comuns

    def calculate_reward(self, generated_word, correct_word):
        """Calcula a recompensa com base na comparação da palavra gerada e a palavra correta."""
        if generated_word == correct_word:
            return 1  # Recompensa positiva
        else:
            return -1  # Penalização

    def generate_text(self, input_text, max_words=100, callback=None):  # Aumenta max_words
        """Gera texto com base no texto de entrada."""
        input_words = self.preprocess_phrase(input_text)
        generated_words = []
        total_reward = 0  # Inicializa a recompensa total

        if not input_words:
            return "Nenhum texto de entrada fornecido."

        current_word = random.choice(input_words)
        generated_words.append(current_word)
        current_context = current_word

        for _ in range(max_words - 1):
            next_words = self.chain.get(current_context, None)
            if not next_words:
                break
            current_word = random.choice(next_words)
            generated_words.append(current_word)
            current_context = ' '.join(generated_words[-3:])  # Atualiza o contexto com 3 palavras
            
            # Calcular recompensa
            if generated_words[-1] in next_words:
                correct_word = next_words[0]  # Exemplo: a primeira palavra na lista de sugestões
                reward = self.calculate_reward(current_word, correct_word)
                total_reward += reward
            
            if callback:
                callback(current_word, ' '.join(generated_words))

        # Armazena a recompensa total
        self.rewards.append(total_reward)
        return self.format_generated_text(generated_words)

    def format_generated_text(self, words):
        """Formata o texto gerado para apresentação."""
        if words:
            return ' '.join(words).capitalize() + '.'  # Garante que o texto comece com letra maiúscula
        return ''


class BabelGUI:
    """Interface gráfica para o gerador de histórias."""

    def __init__(self, master):
        self.master = master
        master.title("Gerador de Histórias")
        master.geometry('500x400')

        self.library = MarkovModel('frases198k.txt')
        self.loading_thread = threading.Thread(target=self.library.load_phrases)
        self.loading_thread.start()

        self.create_widgets()

    def create_widgets(self):
        """Cria todos os widgets da interface gráfica."""
        self.label = ttk.Label(self.master, text="Informe o texto que deseja usar como base:")
        self.label.pack(pady=10)

        self.entry = ttk.Entry(self.master, width=40)
        self.entry.pack(pady=5)

        self.generate_button = ttk.Button(self.master, text="Gerar Texto", command=self.start_generation)
        self.generate_button.pack(pady=20)

        self.result_label = ttk.Label(self.master, text="", wraplength=400)
        self.result_label.pack(pady=10)

        self.suggestions_label = ttk.Label(self.master, text="", wraplength=400)
        self.suggestions_label.pack(pady=10)

        self.logs = tk.Text(self.master, height=6, state=tk.DISABLED)
        self.logs.pack(pady=10)

        self.loading_bar = ttk.Progressbar(self.master, mode='indeterminate')
        self.loading_bar.pack(pady=10)
        self.loading_bar.start()

        self.master.after(100, self.check_loading)

    def check_loading(self):
        """Verifica se o carregamento da biblioteca foi concluído."""
        if not self.loading_thread.is_alive():
            self.loading_bar.stop()
            self.loading_bar.pack_forget()
            self.update_logs("Biblioteca carregada com sucesso.")
        else:
            self.master.after(100, self.check_loading)

    def start_generation(self):
        """Inicia o processo de geração de texto."""
        if not self.library.is_loaded:
            self.result_label.config(text="A biblioteca ainda está carregando. Tente novamente mais tarde.")
            return

        self.result_label.config(text="")
        self.suggestions_label.config(text="")
        self.logs.config(state=tk.NORMAL)
        self.logs.delete(1.0, tk.END)
        self.logs.insert(tk.END, "Gerando texto...\n")
        self.logs.config(state=tk.DISABLED)

        input_text = self.entry.get().strip().lower()
        if not input_text:
            self.result_label.config(text="Por favor, insira um texto válido.")
            return

        # Sugerir palavras com base no último contexto
        context = ' '.join(self.library.preprocess_phrase(input_text)[-3:])  # Ajustado para 3 palavras
        suggestions = self.library.suggest_words(context)
        self.display_suggestions(suggestions)

        generation_thread = threading.Thread(target=self.generate_text, args=(input_text,))
        generation_thread.start()

    def generate_text(self, input_text):
        """Gera texto e atualiza a interface gráfica."""
        time.sleep(1)  # Simula tempo de carregamento
        generated_text = self.library.generate_text(input_text, callback=self.display_progress)
        self.display_result(generated_text)

    def display_suggestions(self, suggestions):
        """Exibe sugestões de palavras na interface gráfica."""
        if suggestions:
            formatted_suggestions = ', '.join([f"{word[0]} (usado {word[1]} vezes)" for word in suggestions])
            self.suggestions_label.config(text=f"Sugestões: {formatted_suggestions}")
        else:
            self.suggestions_label.config(text="Nenhuma sugestão disponível.")

    def display_progress(self, word, generated_text):
        """Atualiza o progresso da geração de texto na interface gráfica."""
        self.result_label.config(text=f"Texto gerado:\n{generated_text}...")
        self.update_logs(f"Palavra escolhida: {word}")

    def display_result(self, generated_text):
        """Exibe o resultado final da geração de texto."""
        self.result_label.config(text=f"Texto gerado:\n{generated_text}")
        self.update_logs("Texto gerado com sucesso.")

    def update_logs(self, message):
        """Atualiza a área de logs na interface gráfica."""
        self.logs.config(state=tk.NORMAL)
        self.logs.insert(tk.END, f"{message}\n")
        self.logs.see(tk.END)
        self.logs.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    gui = BabelGUI(root)
    root.mainloop()
