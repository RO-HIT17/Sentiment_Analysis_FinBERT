# -*- coding: utf-8 -*-
"""training_using_bert.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/10LR0Ym6C8xZj3NtWwtd3LDOuzidVHL0U
"""



import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer
import torch

DATASET_COLUMNS = ['target', 'ids', 'date', 'flag', 'user', 'text']
DATASET_ENCODING = "ISO-8859-1"
df = pd.read_csv('./Project_Data.csv', encoding=DATASET_ENCODING, names=DATASET_COLUMNS)

df = df[['target', 'text']]

df['target'] = df['target'].map({0: 0, 2: 1, 4: 2})

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['target'], test_size=0.2, random_state=42)

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

def encode_data(texts, labels, max_length=128):
    encodings = tokenizer(
        texts.tolist(),
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors='pt'
    )
    return encodings, torch.tensor(labels.values)

train_encodings, train_labels = encode_data(X_train, y_train)
test_encodings, test_labels = encode_data(X_test, y_test)

from torch.utils.data import Dataset, DataLoader

class TwitterDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item['labels'] = self.labels[idx]
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = TwitterDataset(train_encodings, train_labels)
test_dataset = TwitterDataset(test_encodings, test_labels)

from transformers import BertForSequenceClassification, AdamW, Trainer, TrainingArguments

model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset
)

trainer.train()

from torch.utils.data import DataLoader, RandomSampler, SequentialSampler
from accelerate import Accelerator

train_dataloader = DataLoader(
    train_dataset,
    sampler=RandomSampler(train_dataset),
    batch_size=8
)


test_dataloader = DataLoader(
    test_dataset,
    sampler=SequentialSampler(test_dataset),
    batch_size=8
)

accelerator = Accelerator()

model, train_dataloader, test_dataloader = accelerator.prepare(
    model, train_dataloader, test_dataloader
)

from transformers import AdamW, get_linear_schedule_with_warmup
import torch
from tqdm.auto import tqdm


optimizer = AdamW(model.parameters(), lr=2e-5)

total_steps = len(train_dataloader) * 3


scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=0,
    num_training_steps=total_steps
)


optimizer, scheduler = accelerator.prepare(optimizer, scheduler)


epochs = 3
for epoch in range(epochs):
    model.train()
    total_loss = 0

    progress_bar = tqdm(train_dataloader, desc=f"Epoch {epoch + 1}")

    for batch in progress_bar:

        batch = {k: v.to(accelerator.device) for k, v in batch.items()}


        optimizer.zero_grad()

        outputs = model(**batch)
        loss = outputs.loss


        total_loss += loss.item()


        accelerator.backward(loss)


        optimizer.step()
        scheduler.step()


        progress_bar.set_postfix({"loss": loss.item()})


    avg_loss = total_loss / len(train_dataloader)
    print(f"Epoch {epoch + 1} finished with average loss: {avg_loss:.4f}")

model.save_pretrained('./saved_model')
tokenizer.save_pretrained('./saved_model')

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset
)

trainer.train()