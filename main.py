# Chatbot básico em Python

# Dicionário com algumas respostas
respostas = {
    "olá": "Olá! Como posso ajudá-lo hoje?",
    "como você está?": "Estou apenas um programa de computador, mas estou aqui para ajudar!",
    "qual é o seu nome?": "Eu sou um chatbot simples criado em Python.",
    "o que você pode fazer?": "Posso responder a perguntas básicas e ajudar com informações.",
    "tchau": "Até logo! Tenha um bom dia!"
}

# Função principal do chatbot
def chatbot():
    print("Bem-vindo ao Chatbot! (Digite 'tchau' para encerrar)")
    
    while True:
        usuario_input = input("Você: ").lower()  # Lê a entrada do usuário
        if usuario_input in respostas:
            print("Chatbot:", respostas[usuario_input])  # Responde de acordo com o dicionário
        elif usuario_input == 'tchau':
            print("Chatbot: Até logo! Tenha um bom dia!")
            break  # Encerra o loop se o usuário digitar 'tchau'
        else:
            print("Chatbot: Desculpe, não entendi. Você pode reformular a pergunta.")

# Chama a função do chatbot
chatbot()
