import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

from keras.models import Model
from keras.layers import Input, Dense
from keras import regularizers

df = pd.read_csv('creditcard.csv')
df = df.drop(['Time'], axis=1)

scaler = StandardScaler()
df['Amount'] = scaler.fit_transform(df[['Amount']])

X = df.drop(['Class'], axis=1)
y = df['Class']

X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
X_train = X_train[y[X_train.index] == 0]

input_dim = X_train.shape[1]
input_layer = Input(shape=(input_dim,))
encoded = Dense(14, activation='tanh', activity_regularizer=regularizers.l1(1e-5))(input_layer)
encoded = Dense(7, activation='relu')(encoded)
decoded = Dense(14, activation='tanh')(encoded)
decoded = Dense(input_dim, activation='relu')(decoded)

autoencoder = Model(inputs=input_layer, outputs=decoded)
autoencoder.compile(optimizer='adam', loss='mean_squared_error')

autoencoder.fit(X_train, X_train,
                epochs=20,
                batch_size=64,
                shuffle=True,
                validation_split=0.1,
                verbose=1)

X_test_pred = autoencoder.predict(X_test)
mse = np.mean(np.power(X_test - X_test_pred, 2), axis=1)
threshold = np.percentile(mse, 95)
y_pred = (mse > threshold).astype(int)
y_true = y[X_test.index]
print(confusion_matrix(y_true, y_pred))
print(classification_report(y_true, y_pred))

plt.figure(figsize=(10, 6))

normal_mse = mse[y_true == 0]
fraud_mse = mse[y_true == 1]

plt.hist(normal_mse, bins=100, alpha=0.6, label='Normal', color='blue', density=True)
plt.hist(fraud_mse, bins=100, alpha=0.6, label='Fraud', color='red', density=True)

plt.axvline(threshold, color='black', linestyle='--', label='Threshold')

plt.title("Reconstruction Error (Autoencoder)")
plt.xlabel("Mean Squared Error")
plt.ylabel("Density")
plt.legend()
plt.grid(True)
plt.show()
