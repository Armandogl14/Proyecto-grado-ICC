from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset, DatasetDict
import pandas as pd

# Cargar el tokenizador y modelo base de Llama
model_name = "(Ruta del modelo, windows de porqueria)"  
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

df = pd.read_csv('Contracts/contratos.csv')
df = df.dropna()
df = df.drop_duplicates()

data = {
    "text": df["objeto"].tolist(),
    "label": df["tipo"].tolist()
}

dataset = DatasetDict.from_dict({"train": data})
tokenized_dataset = dataset.map(lambda x: tokenizer(x["text"], truncation=True, padding="max_length"), batched=True)

training_args = TrainingArguments(
    output_dir="./results",       # Directorio de salida
    evaluation_strategy="epoch", # Evaluar al final de cada época
    save_strategy="epoch",       # Guardar al final de cada época
    logging_dir="./logs",        # Directorio de logs
    per_device_train_batch_size=8,
    num_train_epochs=3,
    learning_rate=5e-5,
    weight_decay=0.01,
    fp16=True                     
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"]
)

trainer.train()
