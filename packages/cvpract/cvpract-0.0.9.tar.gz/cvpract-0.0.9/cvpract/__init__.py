def show():
    print(r"""

pract 1a(implement advance deep learning algo cnn)

import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import numpy as np


(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

# Normalize pixel values to [0,1]
x_train, x_test = x_train / 255.0, x_test / 255.0


class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']


plt.figure(figsize=(10, 10))
for i in range(25):
    plt.subplot(5, 5, i + 1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(x_train[i])
    plt.xlabel(class_names[y_train[i][0]])
plt.show()
model = models.Sequential([
    layers.Conv2D(64, (3, 3), activation='relu', input_shape=(32, 32, 3)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(10, activation='softmax')
])
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
history = model.fit(x_train, y_train, epochs=10, batch_size=64, validation_split=0.2)
test_loss, test_acc = model.evaluate(x_test, y_test)
print(f"Test accuracy: {test_acc:.4f}")
img = x_test[1]
img_batch = np.expand_dims(img, axis=0)
pred_probs = model.predict(img_batch)
predicted_class = np.argmax(pred_probs)
plt.imshow(img)
plt.title(f"Predicted: {class_names[predicted_class]}")
plt.axis('off')
plt.show()
model.summary()


prac 1b(RNN)




reviews = [
    "I loved the movie, it was fantastic!",       # positive
    "Absolutely terrible, worst film ever.",      # negative
    "Great acting and wonderful story.",          # positive
    "The movie was boring and too long.",         # negative
    "An excellent and emotional performance.",    # positive
    "I hated it, very disappointing."             # negative
]
labels = [1, 0, 1, 0, 1, 0] 
import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, TensorDataset
from collections import Counter
import torch.nn as nn
import re

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.split()

tokenized_reviews = [preprocess(review) for review in reviews]

all_words = [word for review in tokenized_reviews for word in review]
word_counts = Counter(all_words)

vocab = {word: i+1 for i, (word, _) in enumerate(word_counts.most_common())}  
vocab['<PAD>'] = 0  
vocab['<UNK>'] = len(vocab)  


encoded_reviews = [[vocab.get(word, vocab['<UNK>']) for word in review] for review in tokenized_reviews]

padded_reviews = pad_sequence([torch.tensor(seq) for seq in encoded_reviews], batch_first=True)

labels_tensor = torch.tensor(labels)
dataset = TensorDataset(padded_reviews, labels_tensor)
dataloader = DataLoader(dataset, batch_size=2, shuffle=True)


class ReviewRNN(nn.Module):
    def _init_(self, vocab_size, embed_size, hidden_size, num_classes):
        super(ReviewRNN, self)._init_()
        self.embedding = nn.Embedding(vocab_size, embed_size, padding_idx=0)
        self.rnn = nn.RNN(embed_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = self.embedding(x)
        output, _ = self.rnn(x)
        out = self.fc(output[:, -1, :])  
        return out


vocab_size = len(vocab)
embed_size = 32
hidden_size = 64
num_classes = 2

model = ReviewRNN(vocab_size, embed_size, hidden_size, num_classes)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

num_epochs = 10
for epoch in range(num_epochs):
    for batch_x, batch_y in dataloader:
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

def predict_sentiment(text):
    model.eval()
    with torch.no_grad():
        tokens = preprocess(text)
        encoded = [vocab.get(word, vocab['<UNK>']) for word in tokens]
        tensor = torch.tensor(encoded).unsqueeze(0)
        output = model(tensor)
        pred = torch.argmax(output, dim=1).item()
        return "Positive" if pred == 1 else "Negative"


print(predict_sentiment("I really enjoyed the movie"))
print(predict_sentiment("It was the worst movie ever"))
print(predict_sentiment("An excellent and emotional performance."))
print(predict_sentiment("Amazing movie!"))


prac 1 c(CNN using pytorch)



import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np

batch_size = 64
num_classes = 10
learning_rate = 0.001
num_epochs = 20


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")


transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.4914, 0.4822, 0.4465],
                         std=[0.2023, 0.1994, 0.2010])
])


train_dataset = torchvision.datasets.CIFAR10(root='./data', train=True, transform=transform, download=True)
test_dataset = torchvision.datasets.CIFAR10(root='./data', train=False, transform=transform, download=True)

train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
test_loader = torch.utils.data.DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False)


class ConvNeuralNet(nn.Module):
    def _init_(self, num_classes):
        super(ConvNeuralNet, self)._init_()
        self.conv_layer1 = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3)
        self.conv_layer2 = nn.Conv2d(in_channels=32, out_channels=32, kernel_size=3)
        self.max_pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv_layer3 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3)
        self.conv_layer4 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3)
        self.max_pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(1600, 128)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        out = self.conv_layer1(x)
        out = self.conv_layer2(out)
        out = self.max_pool1(out)
        out = self.conv_layer3(out)
        out = self.conv_layer4(out)
        out = self.max_pool2(out)
        out = out.reshape(out.size(0), -1)
        out = self.fc1(out)
        out = self.relu1(out)
        out = self.fc2(out)
        return out

model = ConvNeuralNet(num_classes).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, weight_decay=0.005, momentum=0.9)


print("\nStarting Training...\n")
for epoch in range(num_epochs):
    for i, (images, labels) in enumerate(train_loader):
        images = images.to(device)
        labels = labels.to(device)

        # Forward pass
        outputs = model(images)
        loss = criterion(outputs, labels)

        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Print progress
        if (i + 1) % 100 == 0 or (i + 1) == len(train_loader):
            print(f'Epoch [{epoch+1}/{num_epochs}], Step [{i+1}/{len(train_loader)}], Loss: {loss.item():.4f}')

# --- CIFAR-10 Class Names ---
classes = ['plane', 'car', 'bird', 'cat', 'deer',
           'dog', 'frog', 'horse', 'ship', 'truck']

# --- Helper Function to Show Images ---
def imshow(img):
    img = img * torch.tensor([0.2023, 0.1994, 0.2010]).view(3, 1, 1) + \
          torch.tensor([0.4914, 0.4822, 0.4465]).view(3, 1, 1)
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.axis('off')
    plt.show()

# --- Evaluate Model ---
model.eval()
with torch.no_grad():
    correct = 0
    total = 0

    # Show predictions on a few test images
    dataiter = iter(test_loader)
    images, labels = next(dataiter)
    images_display = images[:8]
    labels_display = labels[:8]

    images_display = images_display.to(device)
    outputs = model(images_display)
    _, predicted = torch.max(outputs, 1)

    images_display = images_display.cpu()
    predicted = predicted.cpu()
    labels_display = labels_display.cpu()

    print("\nPredictions on Sample Test Images:")
    imshow(torchvision.utils.make_grid(images_display, nrow=4))
    print('Predicted:', ' '.join(f'{classes[predicted[j]]}' for j in range(8)))
    print('Actual:   ', ' '.join(f'{classes[labels_display[j]]}' for j in range(8)))

    # Calculate total accuracy
    for images, labels in test_loader:
        images = images.to(device)
        labels = labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    print(f'\nAccuracy of the network on 10000 test images: {100 * correct / total:.2f}%')



prac 2a(build nlp model using sentiment analysis)


import tensorflow as tf
from tensorflow.keras.datasets import imdb
from tensorflow.keras.preprocessing.sequence import pad_sequences from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout


# Load IMDB Dataset num_words = 10000
(x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=num_words)


# Set parameters max_len = 200
x_train = pad_sequences(x_train, maxlen=max_len) x_test = pad_sequences(x_test, maxlen=max_len)

# Build the model model = Sequential([
Embedding(input_dim=num_words, output_dim=128, input_length=max_len), LSTM(64, dropout=0.2, recurrent_dropout=0.2),
Dense(1, activation='sigmoid')
])


# Compile the model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


# Train the model
model.fit(x_train, y_train, batch_size=64, epochs=3, validation_split=0.2)
 
# Evaluate the model
loss, accuracy = model.evaluate(x_test, y_test) print(f"Test Accuracy: {accuracy:.4f}")

# Decode a review example word_index = imdb.get_word_index() index_offset = 3
word_index = {word: (index + index_offset) for word, index in word_index.items()} word_index["<PAD>"] = 0
word_index["<START>"] = 1
word_index["<UNK>"] = 2


reverse_word_index = {index: word for word, index in word_index.items()} decoded_review = " ".join([reverse_word_index.get(i, "?") for i in x_train[0]])

# Print decoded review and label
print("Decoded Review Example:\n", decoded_review) print("Label:", y_train[0])


prac 2b(nlp model for text classification)


import pandas as pd
data = pd.read_csv('https://raw.githubusercontent.com/mohitgupta-omg/Kaggle-SMS-Spam-Collection-Dataset-/master/spam.csv', encoding='latin-1')
data.drop(['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'], axis=1, inplace=True)
data.columns = ['label', 'text']

import nltk
nltk.download('all')

import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
corpus = []
for i in range(len(data['text'])):
    r = re.sub('[^a-zA-Z]', ' ', data['text'][i])
    r = r.lower()
    r = r.split()
    r = [word for word in r if word not in stopwords.words('english')]
    r = [lemmatizer.lemmatize(word) for word in r]
    r = ' '.join(r)
    corpus.append(r)
data['text'] = corpus

X = data['text']
y = data['label']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

from sklearn.feature_extraction.text import CountVectorizer
cv = CountVectorizer()
X_train_cv = cv.fit_transform(X_train)

from sklearn.linear_model import LogisticRegression
lr = LogisticRegression()
lr.fit(X_train_cv, y_train)

X_test_cv = cv.transform(X_test)
predictions = lr.predict(X_test_cv)

from sklearn import metrics
df = pd.DataFrame(metrics.confusion_matrix(y_test, predictions), index=['ham', 'spam'], columns=['ham', 'spam'])
print(df)
print("Accuracy:", metrics.accuracy_score(y_test, predictions))


prac 3(chatbot for transformer model)

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load the pre-trained GPT-2 model and tokenizer
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Set the model to evaluation mode
model.eval()

# Function to generate a response
def generate_response(prompt, max_length=50):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_length=max_length,
            num_return_sequences=1,
            pad_token_id=50256
        )
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response

# Chat loop
print("Chatbot: Hi there! How can I help you?")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Chatbot: Goodbye!!!")
        break
    response = generate_response(user_input)
    print("Chatbot:", response)

prac 4 (recommendation sys using collabrotative filtering)

import numpy as np
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

ratings = pd.read_csv("ratings.csv")
print(ratings.head())

movies = pd.read_csv("movies.csv")
print(movies.head())

n_ratings = len(ratings)
n_movies = len(ratings['movie_id'].unique())
n_users = len(ratings['user_id'].unique())
print(f"Number of ratings: {n_ratings}")
print(f"Number of unique movie_id's: {n_movies}")
print(f"Number of unique users: {n_users}")
print(f"Average ratings per user: {round(n_ratings / n_users, 2)}")
print(f"Average ratings per movie: {round(n_ratings / n_movies, 2)}")

user_freq = ratings[['user_id', 'movie_id']].groupby('user_id').count().reset_index()
user_freq.columns = ['user_id', 'n_ratings']
print(user_freq.head())

mean_rating = ratings.groupby('movie_id')[['rating']].mean()
lowest_rated = mean_rating['rating'].idxmin()
print("Lowest rated movie:")
print(movies.loc[movies['movie_id'] == lowest_rated])

highest_rated = mean_rating['rating'].idxmax()
print("Highest rated movie:")
print(movies.loc[movies['movie_id'] == highest_rated])

print(ratings[ratings['movie_id'] == highest_rated])
print(ratings[ratings['movie_id'] == lowest_rated])

movie_stats = ratings.groupby('movie_id')[['rating']].agg(['count', 'mean'])
movie_stats.columns = movie_stats.columns.droplevel()

from scipy.sparse import csr_matrix

def create_matrix(df):
    N = len(df['user_id'].unique())
    M = len(df['movie_id'].unique())
    user_mapper = dict(zip(np.unique(df["user_id"]), list(range(N))))
    movie_mapper = dict(zip(np.unique(df["movie_id"]), list(range(M))))
    user_inv_mapper = dict(zip(list(range(N)), np.unique(df["user_id"])))
    movie_inv_mapper = dict(zip(list(range(M)), np.unique(df["movie_id"])))
    user_index = [user_mapper[i] for i in df['user_id']]
    movie_index = [movie_mapper[i] for i in df['movie_id']]
    X = csr_matrix((df["rating"], (movie_index, user_index)), shape=(M, N))
    return X


prac 6 (Train a GAN for generalistic realistic images.)


import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

latent_dim = 100
lr = 0.0002
beta1 = 0.5
beta2 = 0.999
num_epochs = 10
batch_size = 32

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

train_dataset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)


class Generator(nn.Module):
    def _init_(self, latent_dim):
        super(Generator, self)._init_()
        self.model = nn.Sequential(
            nn.Linear(latent_dim, 256 * 4 * 4),
            nn.LeakyReLU(0.2),
            nn.Unflatten(1, (256, 4, 4)),
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2),
            nn.ConvTranspose2d(64, 3, kernel_size=4, stride=2, padding=1),
            nn.Tanh()
        )

    def forward(self, z):
        return self.model(z)


class Discriminator(nn.Module):
    def _init_(self):
        super(Discriminator, self)._init_()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.25),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64, momentum=0.8),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.25),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128, momentum=0.8),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.25),
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(256, momentum=0.8),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.25),
            nn.Flatten()
        )
        self.output_layer = nn.Sequential(
            nn.Linear(256 * 2 * 2, 1),
            nn.Sigmoid()
        )

    def forward(self, img):
        x = self.conv_layers(img)
        return self.output_layer(x)


generator = Generator(latent_dim).to(device)
discriminator = Discriminator().to(device)

adversarial_loss = nn.BCELoss()
optimizer_G = optim.Adam(generator.parameters(), lr=lr, betas=(beta1, beta2))
optimizer_D = optim.Adam(discriminator.parameters(), lr=lr, betas=(beta1, beta2))

for epoch in range(num_epochs):
    for i, (real_images, _) in enumerate(dataloader):
        real_images = real_images.to(device)
        batch_size = real_images.size(0)

        valid = torch.ones(batch_size, 1, device=device)
        fake = torch.zeros(batch_size, 1, device=device)

        optimizer_D.zero_grad()
        z = torch.randn(batch_size, latent_dim, device=device)
        fake_images = generator(z)

        real_loss = adversarial_loss(discriminator(real_images), valid)
        fake_loss = adversarial_loss(discriminator(fake_images.detach()), fake)
        d_loss = (real_loss + fake_loss) / 2
        d_loss.backward()
        optimizer_D.step()

        optimizer_G.zero_grad()
        gen_images = generator(z)
        g_loss = adversarial_loss(discriminator(gen_imag_



""")

