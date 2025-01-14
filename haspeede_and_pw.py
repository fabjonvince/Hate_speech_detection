# -*- coding: utf-8 -*-
"""
NLP Project + Project work  - The HaSpeeDe2

Authors:

*   Fabian Vincenzi fabian.vincenzi@studio.unibo.it
*   Davide Perozzi davide.perozzi@studio.unibo.it
*   Martina Ianaro martina.ianaro@studio.unibo.it

# Functions
"""

import os
import random
import numpy as np
import torch
import pandas as pd
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO

def set_reproducibility(seed):
  random.seed(seed)
  np.random.seed(seed)
  rng = np.random.default_rng(seed)
  torch.manual_seed(seed)
  os.environ['TF_DETERMINISTIC_OPS'] = '1'

class EarlyStopping(object):
    def __init__(self, mode='min', min_delta=0, patience=2, percentage=False):
        self.mode = mode
        self.min_delta = min_delta
        self.patience = patience
        self.best = None
        self.num_bad_epochs = 0
        self.is_better = None
        self._init_is_better(mode, min_delta, percentage)

        if patience == 0:
            self.is_better = lambda a, b: True
            self.step = lambda a: False

    def step(self, metrics):
        if self.best is None:
            self.best = metrics
            return False

        if np.isnan(metrics):
            return True

        if self.is_better(metrics, self.best):
            self.num_bad_epochs = 0
            self.best = metrics
        else:
            self.num_bad_epochs += 1

        if self.num_bad_epochs >= self.patience:
            print('terminating because of early stopping!')
            return True
        return False

    def _init_is_better(self, mode, min_delta, percentage):
        if mode not in {'min', 'max'}:
            raise ValueError('mode ' + mode + ' is unknown!')
        if not percentage:
            if mode == 'min':
                self.is_better = lambda a, best: a < best - min_delta
            if mode == 'max':
                self.is_better = lambda a, best: a > best + min_delta
        else:
            if mode == 'min':
                self.is_better = lambda a, best: a < best - (
                            best * min_delta / 100)
            if mode == 'max':
                self.is_better = lambda a, best: a > best + (
                            best * min_delta / 100)

!pip install transformers

"""# Download"""

url1 = 'https://github.com/msang/haspeede/blob/master/2020/haspeede2_dev.zip?raw=true'
url2 = 'https://github.com/msang/haspeede/blob/master/2020/haspeede2_reference.zip?raw=true'
pwd = b"zNw3tCszKWcpDahq"

resp = urlopen(url1)
zipfile = ZipFile(BytesIO(resp.read()))
zipfile.extractall('/content/haspeede2_dev', pwd=pwd)

resp = urlopen(url2)
zipfile = ZipFile(BytesIO(resp.read()))
zipfile.extractall('/content/haspeede2_reference', pwd=pwd)

dev_df = pd.read_csv('/content/haspeede2_dev/haspeede2_dev_taskAB.tsv', sep='\t',
                     names=['id', 'text', 'hs', 'stereotype'], usecols=[0, 1, 2, 3], header=0)

test_df = pd.read_csv('/content/haspeede2_reference/haspeede2_reference/haspeede2_reference_taskAB-tweets.tsv', sep='\t', names=['id', 'text', 'hs', 'stereotype'], usecols=[0, 1, 2, 3], header=0)

test_df_news = pd.read_csv('/content/haspeede2_reference/haspeede2_reference/haspeede2_reference_taskAB-news.tsv', sep='\t', names=['id', 'text', 'hs', 'stereotype'], usecols=[0, 1, 2, 3], header=0)

dev_df.head()

test_df.head()

test_df_news.head()

import pandas as pd
import matplotlib.pyplot as plt

fig, axs = plt.subplots(2, 3, figsize=(12, 8))

dev_df['hs'].value_counts().plot(kind='bar', ax=axs[0, 0])
axs[0, 0].set_ylabel('Frequency')
axs[0, 0].set_title('dev_df hs distribution')

test_df['hs'].value_counts().plot(kind='bar', ax=axs[0, 1])
axs[0, 1].set_ylabel('Frequency')
axs[0, 1].set_title('test_df hs distribution')

test_df_news['hs'].value_counts().plot(kind='bar', ax=axs[0, 2])
axs[0, 2].set_ylabel('Frequency')
axs[0, 2].set_title('test_news_df hs distribution')

#axs[0, 2].remove()
axs[1, 0].remove()
axs[1, 1].remove()
axs[1, 2].remove()

plt.tight_layout()
plt.show()

"""# TASK A - Hate Speech Detection

## Preprocessing
"""

from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import nltk
nltk.download('stopwords')
import re

def preprocessing(subset_len=None):
  if subset_len:
    subset_len = min(len(dev_df), subset_len)
    # Randomly subset
    temp_dev_df = dev_df.sample(n=subset_len)
  else:
    temp_dev_df = dev_df

  # Split dev_df into train and val
  X_train, X_val, y_train, y_val = train_test_split(temp_dev_df['text'], temp_dev_df['hs'], test_size=0.2)

  X_test = test_df['text']
  y_test = test_df['hs']

  X_test_news = test_df_news['text']
  y_test_news = test_df_news['hs']

  sw = stopwords.words('italian')
  stemmer = SnowballStemmer("italian")

  def preprocess_tweet(tweet):
    # convert to lowercase
    tweet = tweet.lower()
    # remove URLs
    tweet = tweet.replace('url', '')
    # remove mentions
    tweet = re.sub(r'@\w+', '', tweet)
    # remove non-alphanumeric characters
    tweet = re.sub(r'[^\w\s]', ' ', tweet)
    # remove duplicate whitespace and stopwords
    tweet = ' '.join([word for word in tweet.split() if not word in sw])

    return tweet

  X_train = X_train.apply(preprocess_tweet)

  X_val = X_val.apply(preprocess_tweet)

  X_test = X_test.apply(preprocess_tweet)

  X_test_news = X_test_news.apply(preprocess_tweet)

  return X_train, X_val, y_train, y_val, X_test, X_test_news, y_test, y_test_news,

from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt

X_dev = dev_df['text']
y_dev = dev_df['hs']

# split dev_df into 80% training and 20% validation
X_train, X_val, y_train, y_val = train_test_split(X_dev, y_dev, test_size=0.2)

X_test = test_df['text']
y_test = test_df['hs']

X_test_news = test_df_news['text']
y_test_news = test_df_news['hs']

fig, axs = plt.subplots(1, 4, figsize=(24, 8))

y_train.value_counts().plot(kind='bar', ax=axs[0])
axs[0].set_ylabel('Frequency')
axs[0].set_title('Train hs distribution')

y_val.value_counts().plot(kind='bar', ax=axs[1])
axs[1].set_ylabel('Frequency')
axs[1].set_title('Validation hs distribution')

y_test.value_counts().plot(kind='bar', ax=axs[2])
axs[2].set_ylabel('Frequency')
axs[2].set_title('Test tweets hs distribution')

y_test_news.value_counts().plot(kind='bar', ax=axs[3])
axs[3].set_ylabel('Frequency')
axs[3].set_title('Test news hs distribution')

plt.tight_layout()
plt.show()

num_positives = sum(y_train)
num_negatives = len(y_train) - num_positives

positive_ratio_train = (num_positives / len(y_train)) * 100
negative_ratio_train = (num_negatives / len(y_train)) * 100

print(f"Ratio positive/negative in train set")
print(f"Positive: {positive_ratio_train:.2f}%")
print(f"Negative: {negative_ratio_train:.2f}%")

num_positives = sum(y_val)
num_negatives = len(y_val) - num_positives

positive_ratio_val = (num_positives / len(y_val)) * 100
negative_ratio_val = (num_negatives / len(y_val)) * 100

print(f"Ratio positive/negative in val set")
print(f"Positive: {positive_ratio_val:.2f}%")
print(f"Negative: {negative_ratio_val:.2f}%")

num_positives = sum(y_test)
num_negatives = len(y_test) - num_positives

positive_ratio_test = (num_positives / len(y_test)) * 100
negative_ratio_test = (num_negatives / len(y_test)) * 100

print(f"Ratio positive/negative in test set")
print(f"Positive: {positive_ratio_test:.2f}%")
print(f"Negative: {negative_ratio_test:.2f}%")

num_positives = sum(y_test_news)
num_negatives = len(y_test_news) - num_positives

positive_ratio_test = (num_positives / len(y_test_news)) * 100
negative_ratio_test = (num_negatives / len(y_test_news)) * 100

print(f"Ratio positive/negative in news test set")
print(f"Positive: {positive_ratio_test:.2f}%")
print(f"Negative: {negative_ratio_test:.2f}%")

temp, _, _, _, _, _, _, _ = preprocessing()
lengths = [len(s) for s in temp]

plt.hist(lengths, bins=range(min(lengths), max(lengths) + 2, 1), edgecolor='black')
plt.xlabel('Length of sample')
plt.ylabel('Frequency')
plt.title('Distribution of tweets lengths')
plt.show()

_, _, _, _, _, temp, _, _ = preprocessing()
lengths = [len(s) for s in temp]

plt.hist(lengths, bins=range(min(lengths), max(lengths) + 2, 1), edgecolor='black')
plt.xlabel('Length of sample')
plt.ylabel('Frequency')
plt.title('Distribution of news lengths')
plt.show()

"""## Tokenization"""

import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertTokenizer

def tokenization(X, y, batch_size, tokenizer=None):
  if tokenizer is None:
      tokenizer = BertTokenizer.from_pretrained("dbmdz/bert-base-italian-uncased")

  max_length = 256

  encoding = tokenizer.batch_encode_plus(list(X), max_length=max_length, padding=True, truncation=True)

  input_ids = torch.tensor(encoding['input_ids'])
  attention_mask = torch.tensor(encoding['attention_mask'])

  inputs = torch.tensor(input_ids)
  mask = torch.tensor(attention_mask)
  labels = torch.tensor(list(y))

  data = TensorDataset(inputs, mask, labels)
  sampler = RandomSampler(data)
  dataloader = DataLoader(data, sampler=sampler, batch_size=batch_size)

  return dataloader

"""## Model & functions"""

from transformers import AutoModel
import torch

class Model(torch.nn.Module):
  def __init__(self, dropout):
    super(Model, self).__init__()
    self.bert = AutoModel.from_pretrained("dbmdz/bert-base-italian-uncased")
    for param in self.bert.parameters():
        param.requires_grad = True
    self.dropout = torch.nn.Dropout(dropout)
    self.linear = torch.nn.Linear(768, 1)

  def forward(self, input_ids, attention_mask):
    outputs = self.bert(input_ids=input_ids.to(device), attention_mask=attention_mask.to(device))
    pooled_output = outputs.pooler_output
    pooled_output = self.dropout(pooled_output)
    logits = self.linear(pooled_output)
    return logits

from tqdm import tqdm

def train_model(model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs):
  early_stopping = EarlyStopping(patience=int(num_epochs * 0.1))
  train_losses = []
  val_losses = []
  reports = []
  for epoch in range(num_epochs):
    print(f"Epoch {epoch+1}")

    # Train on training set
    train_loss = train_fn(train_dataloader, model, criterion, optimizer)

    # Evaluate on validation set
    val_loss, report = val_fn(val_dataloader, model, criterion)

    train_losses.append(train_loss)
    val_losses.append(val_loss)
    reports.append(report)

    # Check early stopping
    if early_stopping.step(val_losses[-1]):
      break

  return train_losses, val_losses, reports

def train_fn(data_loader, model, criterion, optimizer):
  # Train on training set
  model.train()
  train_loss = 0

  for batch in tqdm(data_loader):
    ids, mask, labels = batch
    optimizer.zero_grad()

    # Forward pass
    outputs = model(ids.to(device), mask.to(device))
    outputs = outputs.squeeze()
    loss = criterion(outputs.cpu(), labels.type_as(outputs).cpu())
    train_loss += loss.item()

    # Backward pass
    loss.backward()
    optimizer.step()

  return train_loss / len(data_loader)

from sklearn.metrics import classification_report

def val_fn(data_loader, model, criterion):
  model.eval()
  val_loss, predictions, true_labels = 0, [], []

  with torch.no_grad():
    for batch in tqdm(data_loader):
      ids, mask, labels = batch
      labels = labels.unsqueeze(1)

      # Forward pass
      outputs = model(ids.to(device), mask.to(device))
      loss = criterion(outputs.cpu(), labels.float().cpu())
      val_loss += loss.item()

      preds = (torch.sigmoid(outputs) > 0.5).float()
      predictions.append(preds)
      true_labels.append(labels)

  predictions = torch.cat(predictions, dim=0)
  true_labels = torch.cat(true_labels, dim=0)
  val_loss /= len(data_loader)
  report = classification_report(true_labels.cpu(), predictions.cpu(), labels=[0, 1], zero_division=0, output_dict=True)

  return val_loss, report

"""## GridSearch"""

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Hyperparameter grid
seeds = [42, 12321]
num_epochs = 20
lr = 1e-5
batch_sizes = [32, 64]
pos_weight = torch.tensor([1.5])
dropout_rate = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

results_df = pd.DataFrame(columns=["learning_rate", "pos_weight", "seed", "batch_size", "dropout_rate", "val_loss", "f1_score"])

# Loop over the hyperparameter grid
for seed in seeds:
  set_reproducibility(seed)
  # preprocessing
  X_train, X_val, y_train, y_val, _, _, _, _ = preprocessing(2500)

  for batch_size in batch_sizes:
    # tokenization
    train_dataloader = tokenization(X_train, y_train, batch_size)
    val_dataloader = tokenization(X_val, y_val, batch_size)

    for dropout in dropout_rate:
      # model, criterion, optimizer
      model = Model(dropout).to(device)
      criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
      optimizer = torch.optim.Adam(model.parameters(), lr=lr)

      _, losses, reports = train_model(model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs=num_epochs)

      results_df = results_df.append({"learning_rate": lr, "pos_weight": pos_weight, "seed": seed, "batch_size": batch_size,"dropout_rate": dropout, "val_loss": losses[-1], "f1_score": reports[-1]["macro avg"]["f1-score"]}, ignore_index=True)

# Get row with max f1_score
max_f1_row = results_df.loc[results_df['f1_score'].idxmax()]

# Get row with lowest val_loss
min_val_loss_row = results_df.loc[results_df['val_loss'].idxmin()]

print(f"Model with the higher f1_score ({max_f1_row['f1_score']:.3f}): seed: {max_f1_row['seed']}, batch_size: {max_f1_row['batch_size']}, dropout rate: {max_f1_row['dropout_rate']:.3f} and loss: {max_f1_row['val_loss']:.3f}\nModel with the lowest loss ({min_val_loss_row['val_loss']:.3f}): seed: {min_val_loss_row['seed']}, batch_size: {min_val_loss_row['batch_size']}, dropout rate: {min_val_loss_row['dropout_rate']:.3f} and f1_score: {min_val_loss_row['f1_score']:.3f}")

results_df

"""## Train and Test with best hyperparameters"""

# hyperparameters
seed = 42
lr = 1e-5
pos_weight = torch.tensor([1.5])
batch_size = 32
dropout = 0.3

"""#### Train"""

set_reproducibility(seed)
# preprocessing
X_train, X_val, y_train, y_val, _, _, _, _ = preprocessing()
# tokenization
train_dataloader = tokenization(X_train, y_train, batch_size=batch_size)
val_dataloader = tokenization(X_val, y_val, batch_size=batch_size)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define your model, criterion, optimizer
best_model = Model(dropout).to(device)

# Define your criterion, optimizer
criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = torch.optim.Adam(best_model.parameters(), lr=lr)

# Train the model and validate loss, F1 score, and precision
train_loss, val_loss, report = train_model(best_model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs=2)

import matplotlib.pyplot as plt

plt.plot(train_loss, label='train_loss')
plt.plot(val_loss, label='val_loss')
plt.plot([report[i]["macro avg"]["f1-score"] for i in range(len(report))], label='F1 score')

plt.title('Training Progress')
plt.xlabel('Epoch')
plt.ylabel('Value')

plt.legend()
plt.show()

# to access drive
from google.colab import drive
drive.mount('/content/drive')

# Save the fine-tuned model
torch.save(best_model.state_dict(), "/content/drive/MyDrive/Colab Notebooks/model_hs")

"""#### Evaluation over tweets and news"""

# to access drive
from google.colab import drive
drive.mount('/content/drive')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
best_model_hs = Model(dropout)
best_model_hs.load_state_dict(torch.load("/content/drive/MyDrive/Colab Notebooks/model_hs"))
best_model_hs = best_model_hs.to(device)

set_reproducibility(seed)

# preprocessing
_, _, _, _, X_test, X_test_news, y_test, y_test_news = preprocessing()
# tokenization
test_dataloader = tokenization(X_test, y_test, batch_size=batch_size)
test_news_dataloader = tokenization(X_test_news, y_test_news, batch_size=batch_size)

criterion = torch.nn.BCEWithLogitsLoss()

loss_tweets, report_tweets = val_fn(test_dataloader, best_model_hs, criterion)

print(f"\nTWEETS")
print(f"\nLoss: {loss_tweets}")

loss_news, report_news = val_fn(test_news_dataloader, best_model_hs, criterion)

print(f"\nNEWS")
print(f"\nLoss: {loss_news}")

"""#### Error Analysis - Classification report"""

pd.DataFrame(report_tweets).transpose()

pd.DataFrame(report_news).transpose()

"""# TASK B - Stereotype detection

## Preprocessing
"""

from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import nltk
nltk.download('stopwords')
import re

def preprocessing(subset_len=None):
  if subset_len:
    subset_len = min(len(dev_df), subset_len)
    # Randomly subset
    temp_dev_df = dev_df.sample(n=subset_len)
  else:
    temp_dev_df = dev_df

  # Split dev_df into train and val
  X_train, X_val, y_train, y_val = train_test_split(temp_dev_df['text'], temp_dev_df['stereotype'], test_size=0.2)

  X_test = test_df['text']
  y_test = test_df['stereotype']

  X_test_news = test_df_news['text']
  y_test_news = test_df_news['stereotype']

  sw = stopwords.words('italian')
  stemmer = SnowballStemmer("italian")

  def preprocess_tweet(tweet):
    # convert to lowercase
    tweet = tweet.lower()
    # remove URLs
    tweet = tweet.replace('url', '')
    # remove mentions
    tweet = re.sub(r'@\w+', '', tweet)
    # remove non-alphanumeric characters
    tweet = re.sub(r'[^\w\s]', ' ', tweet)
    # remove duplicate whitespace and stopwords
    tweet = ' '.join([word for word in tweet.split() if not word in sw])

    return tweet

  X_train = X_train.apply(preprocess_tweet)

  X_val = X_val.apply(preprocess_tweet)

  X_test = X_test.apply(preprocess_tweet)

  X_test_news = X_test_news.apply(preprocess_tweet)

  return X_train, X_val, y_train, y_val, X_test, X_test_news, y_test, y_test_news,

from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt

X_dev = dev_df['text']
y_dev = dev_df['stereotype']

# split dev_df into 80% training and 20% validation
X_train, X_val, y_train, y_val = train_test_split(X_dev, y_dev, test_size=0.2)

X_test = test_df['text']
y_test = test_df['stereotype']

X_test_news = test_df_news['text']
y_test_news = test_df_news['stereotype']

fig, axs = plt.subplots(1, 4, figsize=(24, 8))

y_train.value_counts().plot(kind='bar', ax=axs[0])
axs[0].set_ylabel('Frequency')
axs[0].set_title('Train stereotype distribution')

y_val.value_counts().plot(kind='bar', ax=axs[1])
axs[1].set_ylabel('Frequency')
axs[1].set_title('Validation stereotype distribution')

y_test.value_counts().plot(kind='bar', ax=axs[2])
axs[2].set_ylabel('Frequency')
axs[2].set_title('Test tweets stereotype distribution')

y_test_news.value_counts().plot(kind='bar', ax=axs[3])
axs[3].set_ylabel('Frequency')
axs[3].set_title('Test news stereotype distribution')

plt.tight_layout()
plt.show()

num_positives = sum(y_train)
num_negatives = len(y_train) - num_positives

positive_ratio_train = (num_positives / len(y_train)) * 100
negative_ratio_train = (num_negatives / len(y_train)) * 100

print(f"Ratio positive/negative in train set")
print(f"Positive: {positive_ratio_train:.2f}%")
print(f"Negative: {negative_ratio_train:.2f}%")

num_positives = sum(y_val)
num_negatives = len(y_val) - num_positives

positive_ratio_val = (num_positives / len(y_val)) * 100
negative_ratio_val = (num_negatives / len(y_val)) * 100

print(f"Ratio positive/negative in val set")
print(f"Positive: {positive_ratio_val:.2f}%")
print(f"Negative: {negative_ratio_val:.2f}%")

num_positives = sum(y_test)
num_negatives = len(y_test) - num_positives

positive_ratio_test = (num_positives / len(y_test)) * 100
negative_ratio_test = (num_negatives / len(y_test)) * 100

print(f"Ratio positive/negative in test set")
print(f"Positive: {positive_ratio_test:.2f}%")
print(f"Negative: {negative_ratio_test:.2f}%")

num_positives = sum(y_test_news)
num_negatives = len(y_test_news) - num_positives

positive_ratio_test = (num_positives / len(y_test_news)) * 100
negative_ratio_test = (num_negatives / len(y_test_news)) * 100

print(f"Ratio positive/negative in news test set")
print(f"Positive: {positive_ratio_test:.2f}%")
print(f"Negative: {negative_ratio_test:.2f}%")

temp, _, _, _, _, _, _, _ = preprocessing()
lengths = [len(s) for s in temp]

plt.hist(lengths, bins=range(min(lengths), max(lengths) + 2, 1), edgecolor='black')
plt.xlabel('Length of sample')
plt.ylabel('Frequency')
plt.title('Distribution of tweets lengths')
plt.show()

_, _, _, _, _, temp, _, _ = preprocessing()
lengths = [len(s) for s in temp]

plt.hist(lengths, bins=range(min(lengths), max(lengths) + 2, 1), edgecolor='black')
plt.xlabel('Length of sample')
plt.ylabel('Frequency')
plt.title('Distribution of news lengths')
plt.show()

"""## Tokenization"""

import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertTokenizer

def tokenization(X, y, batch_size, tokenizer=None):
  if tokenizer is None:
      tokenizer = BertTokenizer.from_pretrained("dbmdz/bert-base-italian-uncased")

  max_length = 256

  encoding = tokenizer.batch_encode_plus(list(X), max_length=max_length, padding=True, truncation=True)

  input_ids = torch.tensor(encoding['input_ids'])
  attention_mask = torch.tensor(encoding['attention_mask'])

  inputs = torch.tensor(input_ids)
  mask = torch.tensor(attention_mask)
  labels = torch.tensor(list(y))

  data = TensorDataset(inputs, mask, labels)
  sampler = RandomSampler(data)
  dataloader = DataLoader(data, sampler=sampler, batch_size=batch_size)

  return dataloader

"""## Model & functions"""

from transformers import AutoModel
import torch

class Model(torch.nn.Module):
  def __init__(self, dropout):
    super(Model, self).__init__()
    self.bert = AutoModel.from_pretrained("dbmdz/bert-base-italian-uncased")
    for param in self.bert.parameters():
        param.requires_grad = True
    self.dropout = torch.nn.Dropout(dropout)
    self.linear = torch.nn.Linear(768, 1)

  def forward(self, input_ids, attention_mask):
    outputs = self.bert(input_ids=input_ids.to(device), attention_mask=attention_mask.to(device))
    pooled_output = outputs.pooler_output
    pooled_output = self.dropout(pooled_output)
    logits = self.linear(pooled_output)
    return logits

def train_fn(data_loader, model, criterion, optimizer):
  # Train on training set
  model.train()
  train_loss = 0

  for batch in tqdm(data_loader):
    ids, mask, labels = batch
    optimizer.zero_grad()

    # Forward pass
    outputs = model(ids.to(device), mask.to(device))
    outputs = outputs.squeeze()
    loss = criterion(outputs.cpu(), labels.type_as(outputs).cpu())
    train_loss += loss.item()

    # Backward pass
    loss.backward()
    optimizer.step()

  return train_loss / len(data_loader)

def train_fn(data_loader, model, criterion, optimizer):
  # Train on training set
  model.train()
  train_loss = 0

  for batch in tqdm(data_loader):
    ids, mask, labels = batch
    optimizer.zero_grad()

    # Forward pass
    outputs = model(ids.to(device), mask.to(device))
    outputs = outputs.squeeze()
    loss = criterion(outputs.cpu(), labels.type_as(outputs).cpu())
    train_loss = loss.item()

    # Backward pass
    loss.backward()
    optimizer.step()

  return train_loss

from sklearn.metrics import classification_report

def val_fn(data_loader, model, criterion):
  model.eval()
  val_loss, predictions, true_labels = 0, [], []

  with torch.no_grad():
    for batch in tqdm(data_loader):
      ids, mask, labels = batch
      labels = labels.unsqueeze(1)

      # Forward pass
      outputs = model(ids.to(device), mask.to(device))
      loss = criterion(outputs.cpu(), labels.float().cpu())
      val_loss += loss.item()

      preds = (torch.sigmoid(outputs) > 0.5).float()
      predictions.append(preds)
      true_labels.append(labels)

  predictions = torch.cat(predictions, dim=0)
  true_labels = torch.cat(true_labels, dim=0)
  val_loss /= len(data_loader)
  report = classification_report(true_labels.cpu(), predictions.cpu(), labels=[0, 1], zero_division=0, output_dict=True)

  return val_loss, report

"""## GridSearch"""

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Hyperparameter grid
seeds = [42, 12321]
num_epochs = 20
lr = 1e-5
batch_sizes = [32, 64]
pos_weight = torch.tensor([1.25])
dropout_rate = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

results_df = pd.DataFrame(columns=["learning_rate", "pos_weight", "seed", "batch_size", "dropout_rate", "val_loss", "f1_score"])

# Loop over the hyperparameter grid
for seed in seeds:
  set_reproducibility(seed)
  # preprocessing
  X_train, X_val, y_train, y_val, _, _, _, _ = preprocessing(2500)

  for batch_size in batch_sizes:
    # tokenization
    train_dataloader = tokenization(X_train, y_train, batch_size)
    val_dataloader = tokenization(X_val, y_val, batch_size)

    for dropout in dropout_rate:
      # model, criterion, optimizer
      model = Model(dropout).to(device)
      criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
      optimizer = torch.optim.Adam(model.parameters(), lr=lr)

      _, losses, reports = train_model(model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs=num_epochs)

      results_df = results_df.append({"learning_rate": lr, "pos_weight": pos_weight, "seed": seed, "batch_size": batch_size,"dropout_rate": dropout, "val_loss": losses[-1], "f1_score": reports[-1]["macro avg"]["f1-score"]}, ignore_index=True)

# Get row with max f1_score
max_f1_row = results_df.loc[results_df['f1_score'].idxmax()]

# Get row with lowest val_loss
min_val_loss_row = results_df.loc[results_df['val_loss'].idxmin()]

print(f"Model with the higher f1_score ({max_f1_row['f1_score']:.3f}): seed: {max_f1_row['seed']}, batch_size: {max_f1_row['batch_size']}, dropout rate: {max_f1_row['dropout_rate']:.3f} and loss: {max_f1_row['val_loss']:.3f}\nModel with the lowest loss ({min_val_loss_row['val_loss']:.3f}): seed: {min_val_loss_row['seed']}, batch_size: {min_val_loss_row['batch_size']}, dropout rate: {min_val_loss_row['dropout_rate']:.3f} and f1_score: {min_val_loss_row['f1_score']:.3f}")

results_df

"""## Train and Test with best hyperparameters"""

# hyperparameters
seed = 42
lr = 1e-5
batch_size = 32
pos_weight = torch.tensor([1.25])
dropout = 0.8

"""### Train"""

set_reproducibility(seed)
# preprocessing
X_train, X_val, y_train, y_val, _, _, _, _ = preprocessing()
# tokenization
train_dataloader = tokenization(X_train, y_train, batch_size=batch_size)
val_dataloader = tokenization(X_val, y_val, batch_size=batch_size)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define your model, criterion, optimizer
best_model = Model(dropout).to(device)

# Define your criterion, optimizer
criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = torch.optim.Adam(best_model.parameters(), lr=lr)

# Train the model and validate loss, F1 score, and precision
train_loss, val_loss, report = train_model(best_model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs=2)

import matplotlib.pyplot as plt

plt.plot(train_loss, label='train_loss')
plt.plot(val_loss, label='val_loss')
plt.plot([report[i]["macro avg"]["f1-score"] for i in range(len(report))], label='F1 score')

plt.title('Training Progress')
plt.xlabel('Epoch')
plt.ylabel('Value')

plt.legend()
plt.show()

# to access drive
from google.colab import drive
drive.mount('/content/drive')

# Save the fine-tuned model
torch.save(best_model.state_dict(), "/content/drive/MyDrive/Colab Notebooks/model_stereotype")

"""### Evaluation over tweets and news"""

# to access drive
from google.colab import drive
drive.mount('/content/drive')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
best_model_stereotype = Model(dropout)
best_model_stereotype.load_state_dict(torch.load("/content/drive/MyDrive/Colab Notebooks/model_stereotype"))
best_model_stereotype = best_model_stereotype.to(device)

set_reproducibility(seed)
# preprocessing
_, _, _, _, X_test, X_test_news, y_test, y_test_news = preprocessing()
# tokenization
test_dataloader = tokenization(X_test, y_test, batch_size=batch_size)
test_news_dataloader = tokenization(X_test_news, y_test_news, batch_size=batch_size)

loss_tweets, report_tweets = val_fn(test_dataloader, best_model_stereotype, criterion)

print(f"\nTWEETS")
print(f"\nLoss: {loss_tweets}")

loss_news, report_news = val_fn(test_news_dataloader, best_model_stereotype, criterion)

print(f"\nNEWS")
print(f"\nLoss: {loss_news}")

"""### Error Analysis - Classification report"""

pd.DataFrame(report_tweets).transpose()

pd.DataFrame(report_news).transpose()

"""# TASK C - Identification of Nominal Utterances

## Download
"""

import pandas as pd
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import requests

dev_df = pd.read_csv('/content/haspeede2_dev/haspeede2_dev_taskC.txt', sep='\t',
                     names=['TweetID-TokenNumber', 'token', 'IOB_annotation'], usecols=[0, 1, 2], header=0)

test_df = pd.read_csv('/content/haspeede2_reference/haspeede2_reference/haspeede2_reference_taskC-tweets.txt', sep='\t', names=['TweetID-TokenNumber', 'token', 'IOB_annotation'], usecols=[0, 1, 2], header=0)

test_df_news = pd.read_csv('/content/haspeede2_reference/haspeede2_reference/haspeede2_reference_taskC-news.txt', sep='\t', names=['TweetID-TokenNumber', 'token', 'IOB_annotation'], usecols=[0, 1, 2], header=0)

row = []

with open('/content/haspeede2_dev/haspeede2_dev_taskC.txt') as txt:
  lines = filter(None, (line.rstrip() for line in txt)) #remove blank lines
  for line in lines:
    if not line.startswith('#') and not line.startswith(' '):
        row.append([word for word in line.strip().split('\t')])

dev_df = pd.DataFrame(row, columns=['id', 'token', 'IOB'])

row= []
with open('/content/haspeede2_reference/haspeede2_reference/haspeede2_reference_taskC-tweets.txt') as txt:
  lines = filter(None, (line.rstrip() for line in txt)) #remove blank lines
  for line in lines:
    if not line.startswith('#') and not line.startswith(' '):
        row.append([word for word in line.strip().split('\t')])

test_df = pd.DataFrame(row, columns=['id', 'token', 'IOB'])

dev_df.drop_duplicates(subset=['id'], inplace=True)
test_df.drop_duplicates(subset=['id'], inplace=True)

# separate tweet ID from token number
dev_df[['id', 'numb']] = dev_df.id.str.split('-', expand=True)
test_df[['id', 'numb']] = test_df.id.str.split('-', expand=True)

#reorder column
cols = ['id', 'numb', 'token', 'IOB']
dev_df = dev_df[cols]
test_df = test_df[cols]

dev_df.loc[dev_df.IOB == 'B-NU-CGA', 'IOB'] = 'B'
dev_df.loc[dev_df.IOB == 'I-NU-CGA', 'IOB'] = 'I'

test_df.loc[test_df.IOB == 'B-NU-CGA', 'IOB'] = 'B'
test_df.loc[test_df.IOB == 'I-NU-CGA', 'IOB'] = 'I'

test_df.head()

import pandas as pd
import matplotlib.pyplot as plt

fig, axs = plt.subplots(1, 2, figsize=(12, 6))

dev_df['IOB'].value_counts().plot(kind='bar', ax=axs[0])
axs[0].set_ylabel('Frequency')
axs[0].set_title('dev_df NU distribution')

test_df['IOB'].value_counts().plot(kind='bar', ax=axs[1])
axs[1].set_ylabel('Frequency')
axs[1].set_title('test_df hs distribution')

plt.tight_layout()
plt.show()

"""## Preprocessing"""

from sklearn.model_selection import train_test_split

def preprocessing(max_len, subset_len=None):

  def create_dataframe(df):
      groups = df.groupby('id')
      rows = []
      for name, group in groups:
          sentences = group['token'].tolist()
          iob = group['IOB'].tolist()
          rows.append([name, sentences, iob])
      return pd.DataFrame(rows, columns=['id', 'sentences', 'IOB'])

  new_df = create_dataframe(dev_df)[:subset_len] if subset_len else create_dataframe(dev_df)
  new_df_test = create_dataframe(test_df)[:subset_len] if subset_len else create_dataframe(test_df)

  # preprocessing: lower case
  new_df["sentences"] = new_df["sentences"].apply(lambda x: [word.lower() for word in x])
  new_df_test["sentences"] = new_df_test["sentences"].apply(lambda x: [word.lower() for word in x])

  # truncate the head of > max_len sentences
  new_df["sentences"] = new_df["sentences"].apply(lambda x: x[-max_len:] if len(x) > max_len else x)
  new_df_test["sentences"] = new_df_test["sentences"].apply(lambda x: x[-max_len:] if len(x) > max_len else x)

  # split
  training_samp, val_samp = train_test_split(new_df["id"].unique(), test_size=0.2, shuffle=True)
  X_train, y_train = new_df[new_df['id'].isin(training_samp)]['sentences'], new_df[new_df['id'].isin(training_samp)]['IOB']
  X_val, y_val = new_df[new_df['id'].isin(val_samp)]['sentences'], new_df[new_df['id'].isin(val_samp)]['IOB']
  X_test, y_test = new_df_test['sentences'], new_df_test['IOB']

  return X_train, y_train, X_val, y_val, X_test, y_test

temp, _, _, _, _, _, = preprocessing(256)
lengths = [len(s) for s in temp]

plt.hist(lengths, bins=range(min(lengths), max(lengths) + 2, 1), edgecolor='black')
plt.xlabel('Length of sample')
plt.ylabel('Frequency')
plt.title('Distribution of tweets lengths')
plt.show()

"""## Tokenization"""

import torch
from torch.utils.data import DataLoader, TensorDataset, RandomSampler
from transformers import BertTokenizer

label_map = {'O': 0, 'B': 1, 'I': 2, 'PAD': 3}

def tokenization(X, y, max_len, batch_size, tokenizer=None):
  if tokenizer is None:
      tokenizer = BertTokenizer.from_pretrained('dbmdz/bert-base-italian-uncased')

  input_ids = []
  attention_masks = []
  label_ids = []
  for text, label in zip(X, y):
    encoded_dict = tokenizer.encode_plus(
        text,
        max_length=max_len,
        pad_to_max_length=True,
        return_attention_mask=True,
        truncation=True,
        padding='max_length'
    )
    input_ids.append(encoded_dict['input_ids'])
    attention_masks.append(encoded_dict['attention_mask'])

    # Add the PAD label at the beginning and end of the label list
    label_ids_list = [label_map['PAD']] + [label_map[l] for l in label] + [label_map['PAD']]
    # Pad the label list to the maximum length
    label_ids_list = label_ids_list[:max_len] + [label_map['PAD']] * (max_len - len(label_ids_list))


    label_ids.append(torch.tensor(label_ids_list))

  input_ids = torch.tensor(input_ids)
  attention_masks = torch.tensor(attention_masks)
  label_ids = torch.stack(label_ids)

  dataset = TensorDataset(input_ids, attention_masks, label_ids)
  sampler = RandomSampler(dataset)
  dataloader = DataLoader(dataset, sampler=sampler, batch_size=batch_size)

  return dataloader

"""## Model & functions"""

from transformers import AutoModel

class Model(torch.nn.Module):
  def __init__(self, dropout, num_labels):
    super(Model, self).__init__()
    self.bert = AutoModel.from_pretrained("dbmdz/bert-base-italian-uncased")
    for param in self.bert.parameters():
        param.requires_grad = True
    self.dropout = torch.nn.Dropout(dropout)
    self.classifier = torch.nn.Linear(self.bert.config.hidden_size, num_labels)

  def forward(self, input_ids, attention_mask):
    outputs = self.bert(input_ids=input_ids.to(device), attention_mask=attention_mask.to(device))
    sequence_output = outputs.last_hidden_state
    sequence_output = self.dropout(sequence_output)
    logits = self.classifier(sequence_output)
    return logits

from tqdm import tqdm

def train_model(model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs, num_labels=None):
  early_stopping = EarlyStopping(patience=int(num_epochs * 0.1))
  train_losses = []
  val_losses = []
  reports = []
  for epoch in range(num_epochs):
    print(f"Epoch {epoch+1}")

    # Train on training set
    train_loss = train_fn(train_dataloader, model, criterion, num_labels, optimizer)

    # Evaluate on validation set
    val_loss, report = val_fn(val_dataloader, model, criterion, num_labels)

    train_losses.append(train_loss)
    val_losses.append(val_loss)
    reports.append(report)

    # Check early stopping
    if early_stopping.step(val_losses[-1]):
      break

  return train_losses, val_losses, reports

def train_fn(data_loader, model, criterion, num_labels, optimizer):
  model.train()
  train_loss = 0

  for batch in tqdm(data_loader):
    ids, mask, labels = batch
    optimizer.zero_grad()

    logits = model(ids.to(device), mask.to(device))

    loss = criterion(logits.cpu().view(-1, num_labels), labels.cpu().view(-1))
    loss.backward()
    optimizer.step()

    train_loss += loss.item()

  return train_loss/len(data_loader)

from sklearn.metrics import classification_report

def val_fn(data_loader, model, criterion, num_labels):
  model.eval()

  val_loss, predictions, true_labels = 0, [], []

  with torch.no_grad():
    for batch in tqdm(data_loader):
      ids, mask, labels = batch

      # Forward pass
      logits = model(ids.to(device), mask.to(device))

      loss = criterion(logits.cpu().view(-1, num_labels), labels.cpu().view(-1))
      val_loss += loss.item()
      val_prediction = torch.argmax(logits.cpu(), axis=2).cpu().numpy()
      actual = labels.cpu().numpy()

      predictions.append(val_prediction)
      true_labels.append(actual)

  predictions = np.concatenate(predictions, axis=0)
  true_labels = np.concatenate(true_labels, axis=0)
  val_loss /= len(data_loader)
  report = classification_report(true_labels.flatten(), predictions.flatten(), labels=[1, 2], zero_division=0, output_dict=True)

  return val_loss, report

"""## GridSearch"""

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Hyperparameter grid
max_len = 140
num_labels = len(label_map)
num_epochs = 20
lr = 1e-5
seeds = [42, 12321]
batch_sizes = [32, 64]
dropout_rate = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

results_df = pd.DataFrame(columns=["learning_rate", "seed", "batch_size", "dropout_rate", "val_loss", "precision", "recall", "f1_score"])

for seed in seeds:
  set_reproducibility(seed)
  # preprocessing
  X_train, y_train, X_val, y_val, _, _ = preprocessing(max_len,subset_len=2500)

  for batch_size in batch_sizes:
    # tokenization
    train_dataloader = tokenization(X_train, y_train, max_len, batch_size )
    val_dataloader = tokenization(X_val, y_val, max_len, batch_size)

    for dropout in dropout_rate:
      # model, criterion, optimizer
      model = Model(dropout, num_labels).to(device)
      criterion = torch.nn.CrossEntropyLoss()
      optimizer = torch.optim.Adam(model.parameters(), lr=lr)

      print(f"Running: seed: {seed}, batch_size: {batch_size}, dropout: {dropout}")
      _, losses, reports = train_model(model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs, num_labels)

      results_df = results_df.append({"learning_rate": lr, "seed": seed, "batch_size": batch_size,"dropout_rate": dropout, "val_loss": losses[-1], "precision": reports[-1]["macro avg"]["precision"], "recall": reports[-1]["macro avg"]["recall"], "f1_score": reports[-1]["macro avg"]["f1-score"]}, ignore_index=True)

# Get row with max f1_score
max_f1_row = results_df.loc[results_df['f1_score'].idxmax()]

# Get row with lowest val_loss
min_val_loss_row = results_df.loc[results_df['val_loss'].idxmin()]

print(f"Model with the higher f1_score ({max_f1_row['f1_score']:.3f}): seed: {max_f1_row['seed']}, batch_size: {max_f1_row['batch_size']}, dropout rate: {max_f1_row['dropout_rate']:.3f} and loss: {max_f1_row['val_loss']:.3f}\nModel with the lowest loss ({min_val_loss_row['val_loss']:.3f}): seed: {min_val_loss_row['seed']}, batch_size: {min_val_loss_row['batch_size']}, dropout rate: {min_val_loss_row['dropout_rate']:.3f} and f1_score: {min_val_loss_row['f1_score']:.3f}")

results_df

"""## Train and Test with best hyperparameters"""

# Hyperparameters
max_len = 140
num_labels = len(label_map)
lr = 1e-5
seed = 12321
batch_size = 64
dropout = 0.2

"""### Train"""

set_reproducibility(seed)
# preprocessing
X_train, y_train, X_val, y_val, _, _ = preprocessing(max_len)
# tokenization
train_dataloader = tokenization(X_train, y_train, max_len, batch_size)
val_dataloader = tokenization(X_val, y_val, max_len, batch_size)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# model, criterion, optimizer
best_model = Model(dropout, num_labels).to(device)
criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(best_model.parameters(), lr=lr)

train_loss, val_loss, reports = train_model(best_model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs=40, num_labels=num_labels)

import matplotlib.pyplot as plt

plt.plot(train_loss, label='train_loss')
plt.plot(val_loss, label='val_loss')
plt.plot([reports[i]["macro avg"]["f1-score"] for i in range(len(reports))], label='F1 score')

plt.title('Training Progress')
plt.xlabel('Epoch')
plt.ylabel('Value')

plt.legend()
plt.show()

# to access drive
from google.colab import drive
drive.mount('/content/drive')

# Save the fine-tuned model
torch.save(best_model.state_dict(), "/content/drive/MyDrive/Colab Notebooks/model_NU")

"""### Evaluation"""

# to access drive
from google.colab import drive
drive.mount('/content/drive')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
best_model_NU = Model(dropout, num_labels)
best_model_NU.load_state_dict(torch.load("/content/drive/MyDrive/Colab Notebooks/model_NU"))
best_model_NU = best_model_NU.to(device)

set_reproducibility(seed)
# preprocessing
_, _, _, _, X_test, y_test = preprocessing(max_len=max_len)
# tokenization
test_dataloader = tokenization(X_test, y_test, max_len=max_len, batch_size=batch_size)

loss, report = val_fn(test_dataloader, best_model_NU, criterion, num_labels)

print(f"\nLoss: {loss}")

"""### Error Analysis - Classification report"""

pd.DataFrame(report).transpose()

"""# Project work

## Spanish

### Download
"""

url1 = 'https://datacloud.di.unito.it/index.php/s/eMZdFYq6yRP3zeL/download/hateval2019.zip?raw=true'
pwd = b"2019hateval"

resp = urlopen(url1)
zipfile = ZipFile(BytesIO(resp.read()))
zipfile.extractall('/content/haspeede_spanish', pwd=pwd)

train_df = pd.read_csv('/content/haspeede_spanish/hateval2019_es_train.csv', sep=',',
                     names=['id', 'text', 'hs', 'tr', 'ag'], usecols=[0, 1, 2, 3, 4], header=0)

dev_df = pd.read_csv('/content/haspeede_spanish/hateval2019_es_dev.csv', sep=',',
                     names=['id', 'text', 'hs', 'tr', 'ag'], usecols=[0, 1, 2, 3, 4], header=0)

test_df = pd.read_csv('/content/haspeede_spanish/hateval2019_es_test.csv', sep=',',
                     names=['id', 'text', 'hs', 'tr', 'ag'], usecols=[0, 1, 2, 3, 4], header=0)

train_df.head()

print(train_df.shape)
print(dev_df.shape)
print(test_df.shape)

import pandas as pd
import matplotlib.pyplot as plt

fig, axs = plt.subplots(2, 3, figsize=(12, 8))

train_df['hs'].value_counts().plot(kind='bar', ax=axs[0, 0])
axs[0, 0].set_ylabel('Frequency')
axs[0, 0].set_title('train_df hs distribution')

dev_df['hs'].value_counts().plot(kind='bar', ax=axs[0, 1])
axs[0, 1].set_ylabel('Frequency')
axs[0, 1].set_title('val_df hs distribution')

test_df['hs'].value_counts().plot(kind='bar', ax=axs[0, 2])
axs[0, 2].set_ylabel('Frequency')
axs[0, 2].set_title('test_df hs distribution')

axs[1, 0].remove()
axs[1, 1].remove()
axs[1, 2].remove()

plt.tight_layout()
plt.show()



"""### Preprocessing"""

from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt

X_train = train_df['text']
y_train = train_df['hs']

X_val = dev_df['text']
y_val = dev_df['hs']

X_test = test_df['text']
y_test = test_df['hs']

fig, axs = plt.subplots(1, 3, figsize=(24, 8))

y_train.value_counts().plot(kind='bar', ax=axs[0])
axs[0].set_ylabel('Frequency')
axs[0].set_title('Train hs distribution')

y_val.value_counts().plot(kind='bar', ax=axs[1])
axs[1].set_ylabel('Frequency')
axs[1].set_title('Validation hs distribution')

y_test.value_counts().plot(kind='bar', ax=axs[2])
axs[2].set_ylabel('Frequency')
axs[2].set_title('Test hs distribution')

plt.tight_layout()
plt.show()

num_positives = sum(y_train)
num_negatives = len(y_train) - num_positives

positive_ratio_train = (num_positives / len(y_train)) * 100
negative_ratio_train = (num_negatives / len(y_train)) * 100

print(f"Ratio positive/negative in train set")
print(f"Positive: {positive_ratio_train:.2f}%")
print(f"Negative: {negative_ratio_train:.2f}%")

num_positives = sum(y_val)
num_negatives = len(y_val) - num_positives

positive_ratio_val = (num_positives / len(y_val)) * 100
negative_ratio_val = (num_negatives / len(y_val)) * 100

print(f"Ratio positive/negative in val set")
print(f"Positive: {positive_ratio_val:.2f}%")
print(f"Negative: {negative_ratio_val:.2f}%")

num_positives = sum(y_test)
num_negatives = len(y_test) - num_positives

positive_ratio_test = (num_positives / len(y_test)) * 100
negative_ratio_test = (num_negatives / len(y_test)) * 100

print(f"Ratio positive/negative in test set")
print(f"Positive: {positive_ratio_test:.2f}%")
print(f"Negative: {negative_ratio_test:.2f}%")

from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import nltk
nltk.download('stopwords')
import re

sw = stopwords.words('spanish')
stemmer = SnowballStemmer("spanish")

def preprocess_tweet(tweet):
  # convert to lowercase
  tweet = tweet.lower()
  # remove URLs
  tweet = tweet.replace('url', '')
  # remove mentions
  tweet = re.sub(r'@\w+', '', tweet)
  # remove non-alphanumeric characters
  tweet = re.sub(r'[^\w\s]', ' ', tweet)
  # remove duplicate whitespace and stopwords
  tweet = ' '.join([word for word in tweet.split() if not word in sw])

  return tweet

X_train = X_train.apply(preprocess_tweet)

X_val = X_val.apply(preprocess_tweet)

X_test = X_test.apply(preprocess_tweet)

lengths = [len(s) for s in X_train]

plt.hist(lengths, bins=range(min(lengths), max(lengths) + 2, 1), edgecolor='black')
plt.xlabel('Length of sample')
plt.ylabel('Frequency')
plt.title('Distribution of tweets lengths')
plt.show()

"""### Tokenization"""

import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import AutoTokenizer

def tokenization(X, y, batch_size, tokenizer=None):
  if tokenizer is None:
      tokenizer = AutoTokenizer.from_pretrained("dccuchile/distilbert-base-spanish-uncased")

  max_length = 256

  encoding = tokenizer.batch_encode_plus(list(X), max_length=max_length, padding=True, truncation=True)

  input_ids = torch.tensor(encoding['input_ids'])
  attention_mask = torch.tensor(encoding['attention_mask'])

  inputs = torch.tensor(input_ids)
  mask = torch.tensor(attention_mask)
  labels = torch.tensor(list(y))

  data = TensorDataset(inputs, mask, labels)
  sampler = RandomSampler(data)
  dataloader = DataLoader(data, sampler=sampler, batch_size=batch_size)

  return dataloader

"""### Model & functions"""

from transformers import AutoModel
import torch

class Model(torch.nn.Module):
    def __init__(self, dropout):
        super(Model, self).__init__()
        self.bert = AutoModel.from_pretrained("dccuchile/distilbert-base-spanish-uncased")
        for param in self.bert.parameters():
            param.requires_grad = True
        self.dropout = torch.nn.Dropout(dropout)
        self.linear = torch.nn.Linear(768, 1)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids.to(device), attention_mask=attention_mask.to(device))
        last_hidden_state = outputs.last_hidden_state
        pooled_output = torch.mean(last_hidden_state, dim=1)
        pooled_output = self.dropout(pooled_output)
        logits = self.linear(pooled_output)
        return logits

from tqdm import tqdm

def train_model(model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs):
  early_stopping = EarlyStopping(patience=int(num_epochs * 0.1))
  train_losses = []
  val_losses = []
  reports = []
  for epoch in range(num_epochs):
    print(f"Epoch {epoch+1}")

    # Train on training set
    train_loss = train_fn(train_dataloader, model, criterion, optimizer)

    # Evaluate on validation set
    val_loss, report = val_fn(val_dataloader, model, criterion)

    train_losses.append(train_loss)
    val_losses.append(val_loss)
    reports.append(report)

    # Check early stopping
    if early_stopping.step(val_losses[-1]):
      break

  return train_losses, val_losses, reports

def train_fn(data_loader, model, criterion, optimizer):
  # Train on training set
  model.train()
  train_loss = 0

  for batch in tqdm(data_loader):
    ids, mask, labels = batch
    optimizer.zero_grad()

    # Forward pass
    outputs = model(ids.to(device), mask.to(device))
    outputs = outputs.squeeze()
    loss = criterion(outputs.cpu(), labels.type_as(outputs).cpu())
    train_loss += loss.item()

    # Backward pass
    loss.backward()
    optimizer.step()

  return train_loss / len(data_loader)

from sklearn.metrics import classification_report

def val_fn(data_loader, model, criterion):
  model.eval()
  val_loss, predictions, true_labels = 0, [], []

  with torch.no_grad():
    for batch in tqdm(data_loader):
      ids, mask, labels = batch
      labels = labels.unsqueeze(1)

      # Forward pass
      outputs = model(ids.to(device), mask.to(device))
      loss = criterion(outputs.cpu(), labels.float().cpu())
      val_loss += loss.item()

      preds = (torch.sigmoid(outputs) > 0.5).float()
      predictions.append(preds)
      true_labels.append(labels)

  predictions = torch.cat(predictions, dim=0)
  true_labels = torch.cat(true_labels, dim=0)
  val_loss /= len(data_loader)
  report = classification_report(true_labels.cpu(), predictions.cpu(), labels=[0, 1], zero_division=0, output_dict=True)

  return val_loss, report

"""### GridSearch"""

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Hyperparameter grid
seeds = [42, 12321]
num_epochs = 20
lr = 1e-5
batch_sizes = [32, 64]
pos_weight = torch.tensor([1.4])
dropout_rate = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

results_df = pd.DataFrame(columns=["learning_rate", "pos_weight", "seed", "batch_size", "dropout_rate", "val_loss", "f1_score"])

# Loop over the hyperparameter grid
for seed in seeds:
  set_reproducibility(seed)

  for batch_size in batch_sizes:
    # tokenization
    train_dataloader = tokenization(X_train, y_train, batch_size)
    val_dataloader = tokenization(X_val, y_val, batch_size)

    for dropout in dropout_rate:
      # model, criterion, optimizer
      model = Model(dropout).to(device)
      criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
      optimizer = torch.optim.Adam(model.parameters(), lr=lr)

      _, losses, reports = train_model(model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs=num_epochs)

      results_df = results_df.append({"learning_rate": lr, "pos_weight": pos_weight, "seed": seed, "batch_size": batch_size,"dropout_rate": dropout, "val_loss": losses[-1], "f1_score": reports[-1]["macro avg"]["f1-score"]}, ignore_index=True)

# Get row with max f1_score
max_f1_row = results_df.loc[results_df['f1_score'].idxmax()]

# Get row with lowest val_loss
min_val_loss_row = results_df.loc[results_df['val_loss'].idxmin()]

print(f"Model with the higher f1_score ({max_f1_row['f1_score']:.3f}): seed: {max_f1_row['seed']}, batch_size: {max_f1_row['batch_size']}, dropout rate: {max_f1_row['dropout_rate']:.3f} and loss: {max_f1_row['val_loss']:.3f}\nModel with the lowest loss ({min_val_loss_row['val_loss']:.3f}): seed: {min_val_loss_row['seed']}, batch_size: {min_val_loss_row['batch_size']}, dropout rate: {min_val_loss_row['dropout_rate']:.3f} and f1_score: {min_val_loss_row['f1_score']:.3f}")

results_df

"""### Traing and Test with best hyperparameters"""

# hyperparameters
seed = 12321
lr = 1e-5
pos_weight = torch.tensor([1.4])
batch_size = 32
dropout = 0.5

"""#### Train"""

set_reproducibility(seed)

# tokenization
train_dataloader = tokenization(X_train, y_train, batch_size=batch_size)
val_dataloader = tokenization(X_val, y_val, batch_size=batch_size)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define your model, criterion, optimizer
best_model = Model(dropout).to(device)

# Define your criterion, optimizer
criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = torch.optim.Adam(best_model.parameters(), lr=lr)

# Train the model and validate loss, F1 score, and precision
train_loss, val_loss, report = train_model(best_model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs=10)

import matplotlib.pyplot as plt

plt.plot(train_loss, label='train_loss')
plt.plot(val_loss, label='val_loss')
plt.plot([report[i]["macro avg"]["f1-score"] for i in range(len(report))], label='F1 score')

plt.title('Training Progress')
plt.xlabel('Epoch')
plt.ylabel('Value')

plt.legend()
plt.show()

# to access drive
from google.colab import drive
drive.mount('/content/drive')

# Save the fine-tuned model
torch.save(best_model.state_dict(), "/content/drive/MyDrive/Colab Notebooks/model_spanish_hs")

"""#### Evaluation"""

# to access drive
from google.colab import drive
drive.mount('/content/drive')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
best_model_hs = Model(dropout)
best_model_hs.load_state_dict(torch.load("/content/drive/MyDrive/Colab Notebooks/model_spanish_hs"))
best_model_hs = best_model_hs.to(device)

set_reproducibility(seed)

# tokenization
test_dataloader = tokenization(X_test, y_test, batch_size=batch_size)

criterion = torch.nn.BCEWithLogitsLoss()

loss, report = val_fn(test_dataloader, best_model_hs, criterion)

print(f"\nLoss: {loss}")

"""#### Error Analysis - Classification report"""

pd.DataFrame(report).transpose()

"""## German

### Download
"""

!git clone https://github.com/UCSM-DUE/IWG_hatespeech_public

df = pd.read_csv('/content/IWG_hatespeech_public/german hatespeech refugees.csv', sep=',',
                     names=['text', 'hs'], usecols=[0, 1], header=0)

df.head()

df['hs'] = df['hs'].apply(lambda x: 1 if x=='YES' else 0)

print(df.shape)

import pandas as pd
import matplotlib.pyplot as plt


df['hs'].value_counts().plot(kind='bar', xlabel='hs distribution', ylabel='Frequency')

"""### Preprocessing"""

from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import nltk
nltk.download('stopwords')
import re

def preprocessing(subset_len=None):
  if subset_len:
    subset_len = min(len(df), subset_len)
    # Randomly subset
    temp_df = df.sample(n=subset_len)
  else:
    temp_df = df

  # Split dev_df into train and val
  X_train, X_val, y_train, y_val = train_test_split(temp_df['text'], temp_df['hs'], test_size=0.4)

  X_val, X_test, y_val, y_test = train_test_split(X_val, y_val, test_size=0.5)

  sw = stopwords.words('german')
  stemmer = SnowballStemmer("german")

  def preprocess_tweet(tweet):
    # convert to lowercase
    tweet = tweet.lower()
    # remove URLs
    tweet = tweet.replace('url', '')
    # remove mentions
    tweet = re.sub(r'@\w+', '', tweet)
    # remove non-alphanumeric characters
    tweet = re.sub(r'[^\w\s]', ' ', tweet)
    # remove duplicate whitespace and stopwords
    tweet = ' '.join([word for word in tweet.split() if not word in sw])

    return tweet

  X_train = X_train.apply(preprocess_tweet)

  X_val = X_val.apply(preprocess_tweet)

  X_test = X_test.apply(preprocess_tweet)

  return X_train, X_val, y_train, y_val, X_test, y_test

from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt

X_df = df['text']
y_df = df['hs']

# split dev_df into 80% training and 20% validation
X_train, X_val, y_train, y_val = train_test_split(X_df, y_df, test_size=0.6)

X_val, X_test, y_val, y_test = train_test_split(X_val, y_val, test_size=0.5)

fig, axs = plt.subplots(1, 3, figsize=(24, 8))

y_train.value_counts().plot(kind='bar', ax=axs[0])
axs[0].set_ylabel('Frequency')
axs[0].set_title('Train hs distribution')

y_val.value_counts().plot(kind='bar', ax=axs[1])
axs[1].set_ylabel('Frequency')
axs[1].set_title('Validation hs distribution')

y_test.value_counts().plot(kind='bar', ax=axs[2])
axs[2].set_ylabel('Frequency')
axs[2].set_title('Test hs distribution')

plt.tight_layout()
plt.show()

num_positives = sum(y_train)
num_negatives = len(y_train) - num_positives

positive_ratio_train = (num_positives / len(y_train)) * 100
negative_ratio_train = (num_negatives / len(y_train)) * 100

print(f"Ratio positive/negative in train set")
print(f"Positive: {positive_ratio_train:.2f}%")
print(f"Negative: {negative_ratio_train:.2f}%")

num_positives = sum(y_val)
num_negatives = len(y_val) - num_positives

positive_ratio_val = (num_positives / len(y_val)) * 100
negative_ratio_val = (num_negatives / len(y_val)) * 100

print(f"Ratio positive/negative in val set")
print(f"Positive: {positive_ratio_val:.2f}%")
print(f"Negative: {negative_ratio_val:.2f}%")

num_positives = sum(y_test)
num_negatives = len(y_test) - num_positives

positive_ratio_test = (num_positives / len(y_test)) * 100
negative_ratio_test = (num_negatives / len(y_test)) * 100

print(f"Ratio positive/negative in test set")
print(f"Positive: {positive_ratio_test:.2f}%")
print(f"Negative: {negative_ratio_test:.2f}%")

temp, _, _, _, _, _, = preprocessing(256)
lengths = [len(s) for s in temp]

plt.hist(lengths, bins=range(min(lengths), max(lengths) + 2, 1), edgecolor='black')
plt.xlabel('Length of sample')
plt.ylabel('Frequency')
plt.title('Distribution of tweets lengths')
plt.show()

"""### Tokenization"""

import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertTokenizer

def tokenization(X, y, batch_size, tokenizer=None):
  if tokenizer is None:
      tokenizer = BertTokenizer.from_pretrained("dbmdz/bert-base-german-uncased")

  max_length = 256

  encoding = tokenizer.batch_encode_plus(list(X), max_length=max_length, padding=True, truncation=True)

  input_ids = torch.tensor(encoding['input_ids'])
  attention_mask = torch.tensor(encoding['attention_mask'])

  inputs = torch.tensor(input_ids)
  mask = torch.tensor(attention_mask)
  labels = torch.tensor(list(y))

  data = TensorDataset(inputs, mask, labels)
  sampler = RandomSampler(data)
  dataloader = DataLoader(data, sampler=sampler, batch_size=batch_size)

  return dataloader

"""### Model & functions"""

from transformers import AutoModel
import torch

class Model(torch.nn.Module):
  def __init__(self, dropout):
    super(Model, self).__init__()
    self.bert = AutoModel.from_pretrained("dbmdz/bert-base-german-uncased")
    for param in self.bert.parameters():
        param.requires_grad = True
    self.dropout = torch.nn.Dropout(dropout)
    self.linear = torch.nn.Linear(768, 1)

  def forward(self, input_ids, attention_mask):
    outputs = self.bert(input_ids=input_ids.to(device), attention_mask=attention_mask.to(device))
    pooled_output = outputs.pooler_output
    pooled_output = self.dropout(pooled_output)
    logits = self.linear(pooled_output)
    return logits

from tqdm import tqdm

def train_model(model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs):
  early_stopping = EarlyStopping(patience=int(num_epochs * 0.1))
  train_losses = []
  val_losses = []
  reports = []
  for epoch in range(num_epochs):
    print(f"Epoch {epoch+1}")

    # Train on training set
    train_loss = train_fn(train_dataloader, model, criterion, optimizer)

    # Evaluate on validation set
    val_loss, report = val_fn(val_dataloader, model, criterion)

    train_losses.append(train_loss)
    val_losses.append(val_loss)
    reports.append(report)

    # Check early stopping
    if early_stopping.step(val_losses[-1]):
      break

  return train_losses, val_losses, reports

def train_fn(data_loader, model, criterion, optimizer):
  # Train on training set
  model.train()
  train_loss = 0

  for batch in tqdm(data_loader):
    ids, mask, labels = batch
    optimizer.zero_grad()

    # Forward pass
    outputs = model(ids.to(device), mask.to(device))
    outputs = outputs.squeeze()
    loss = criterion(outputs.cpu(), labels.type_as(outputs).cpu())
    train_loss += loss.item()

    # Backward pass
    loss.backward()
    optimizer.step()

  return train_loss / len(data_loader)

from sklearn.metrics import classification_report

def val_fn(data_loader, model, criterion):
  model.eval()
  val_loss, predictions, true_labels = 0, [], []

  with torch.no_grad():
    for batch in tqdm(data_loader):
      ids, mask, labels = batch
      labels = labels.unsqueeze(1)

      # Forward pass
      outputs = model(ids.to(device), mask.to(device))
      loss = criterion(outputs.cpu(), labels.float().cpu())
      val_loss += loss.item()

      preds = (torch.sigmoid(outputs) > 0.5).float()
      predictions.append(preds)
      true_labels.append(labels)

  predictions = torch.cat(predictions, dim=0)
  true_labels = torch.cat(true_labels, dim=0)
  val_loss /= len(data_loader)
  report = classification_report(true_labels.cpu(), predictions.cpu(), labels=[0, 1], zero_division=0, output_dict=True)

  return val_loss, report

"""### GridSearch"""

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Hyperparameter grid
seeds = [42, 12321]
num_epochs = 20
lr = 1e-5
batch_sizes = [32, 64]
pos_weight = torch.tensor([2.8])
dropout_rate = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

results_df = pd.DataFrame(columns=["learning_rate", "pos_weight", "seed", "batch_size", "dropout_rate", "val_loss", "f1_score"])

# Loop over the hyperparameter grid
for seed in seeds:
  set_reproducibility(seed)
  # preprocessing
  X_train, X_val, y_train, y_val, X_test, y_test = preprocessing(2500)

  for batch_size in batch_sizes:
    # tokenization
    train_dataloader = tokenization(X_train, y_train, batch_size)
    val_dataloader = tokenization(X_val, y_val, batch_size)

    for dropout in dropout_rate:
      # model, criterion, optimizer
      model = Model(dropout).to(device)
      criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
      optimizer = torch.optim.Adam(model.parameters(), lr=lr)

      _, losses, reports = train_model(model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs=num_epochs)

      results_df = results_df.append({"learning_rate": lr, "pos_weight": pos_weight, "seed": seed, "batch_size": batch_size,"dropout_rate": dropout, "val_loss": losses[-1], "f1_score": reports[-1]["macro avg"]["f1-score"]}, ignore_index=True)

# Get row with max f1_score
max_f1_row = results_df.loc[results_df['f1_score'].idxmax()]

# Get row with lowest val_loss
min_val_loss_row = results_df.loc[results_df['val_loss'].idxmin()]

print(f"Model with the higher f1_score ({max_f1_row['f1_score']:.3f}): seed: {max_f1_row['seed']}, batch_size: {max_f1_row['batch_size']}, dropout rate: {max_f1_row['dropout_rate']:.3f} and loss: {max_f1_row['val_loss']:.3f}\nModel with the lowest loss ({min_val_loss_row['val_loss']:.3f}): seed: {min_val_loss_row['seed']}, batch_size: {min_val_loss_row['batch_size']}, dropout rate: {min_val_loss_row['dropout_rate']:.3f} and f1_score: {min_val_loss_row['f1_score']:.3f}")

results_df

"""### Traing and Test with best hyperparameters"""

# hyperparameters
seed = 12321
lr = 1e-5
pos_weight = torch.tensor([2.8])
batch_size = 64
dropout = 0.2

"""#### Train"""

set_reproducibility(seed)
# preprocessing
X_train, X_val, y_train, y_val, _, _ = preprocessing()
# tokenization
train_dataloader = tokenization(X_train, y_train, batch_size=batch_size)
val_dataloader = tokenization(X_val, y_val, batch_size=batch_size)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define your model, criterion, optimizer
best_model = Model(dropout).to(device)

# Define your criterion, optimizer
criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = torch.optim.Adam(best_model.parameters(), lr=lr)

# Train the model and validate loss, F1 score, and precision
train_loss, val_loss, report = train_model(best_model, criterion, optimizer, train_dataloader, val_dataloader, num_epochs=20)

import matplotlib.pyplot as plt

plt.plot(train_loss, label='train_loss')
plt.plot(val_loss, label='val_loss')
plt.plot([report[i]["macro avg"]["f1-score"] for i in range(len(report))], label='F1 score')

plt.title('Training Progress')
plt.xlabel('Epoch')
plt.ylabel('Value')

plt.legend()
plt.show()

# to access drive
from google.colab import drive
drive.mount('/content/drive')

# Save the fine-tuned model
torch.save(best_model.state_dict(), "/content/drive/MyDrive/Colab Notebooks/model_german_hs")

"""#### Evaluation"""

# to access drive
from google.colab import drive
drive.mount('/content/drive')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
best_model_hs = Model(dropout)
best_model_hs.load_state_dict(torch.load("/content/drive/MyDrive/Colab Notebooks/model_german_hs"))
best_model_hs = best_model_hs.to(device)

set_reproducibility(seed)

# preprocessing
_, _, _, _, X_test, y_test = preprocessing()

# tokenization
test_dataloader = tokenization(X_test, y_test, batch_size=batch_size)

criterion = torch.nn.BCEWithLogitsLoss()

loss, report = val_fn(test_dataloader, best_model_hs, criterion)

print(f"\nLoss: {loss}")

"""#### Error Analysis - Classification report"""

pd.DataFrame(report).transpose()
