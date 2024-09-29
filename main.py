import numpy as np
from transformers import Trainer, TrainingArguments, AutoTokenizer, AutoModelForQuestionAnswering
from datasets import load_dataset

# Carregar o dataset
dataset = load_dataset("squad")

# Carregar o tokenizer e o modelo
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModelForQuestionAnswering.from_pretrained("distilbert-base-uncased")

# Função de pré-processamento
def preprocess_function(examples):
    # Tokeniza as perguntas e os contextos
    tokenized_examples = tokenizer(
        examples["question"], 
        examples["context"], 
        truncation=True,
        padding="max_length",
        max_length=512,  # Ajuste conforme necessário
        return_tensors='pt'
    )
    
    # Adiciona as posições de início e fim
    start_positions = []
    end_positions = []

    for i in range(len(examples['answers'])):
        # Obtemos a resposta correta e sua posição
        answer = examples['answers'][i]
        start = answer['answer_start'][0]  # Primeiro índice do início da resposta
        end = start + len(answer['text'][0])  # Calcula a posição final da resposta
        
        start_positions.append(start)
        end_positions.append(end)
    
    tokenized_examples["start_positions"] = np.array(start_positions)
    tokenized_examples["end_positions"] = np.array(end_positions)

    return tokenized_examples

# Pré-processar os dados
tokenized_dataset = dataset.map(preprocess_function, batched=True)

# Definir os argumentos de treinamento
training_args = TrainingArguments(
    output_dir="./results",             # Onde os resultados serão salvos
    evaluation_strategy="epoch",        # Avaliar a cada época
    learning_rate=2e-5,                 # Taxa de aprendizado
    per_device_train_batch_size=16,     # Tamanho do lote de treinamento
    per_device_eval_batch_size=16,      # Tamanho do lote de avaliação
    num_train_epochs=3,                  # Número de épocas
    weight_decay=0.01,                  # Decaimento de peso
    logging_dir='./logs',                # Diretório para logs
)

# Inicializar o Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
)

# Treinar o modelo
trainer.train()
