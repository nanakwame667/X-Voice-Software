import os
import time
import librosa
import numpy as np
import pandas as pd

from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib


class AudioClassifier:
    def __init__(self):
        self.model = None

    def load(self, path):
        if os.path.isfile(path):
            self.model = joblib.load(path)
            return self.model

    def save(self, path):
        save_path = path
        if os.path.isdir(path):
            save_path = os.path.join(path, f'model{time.time()}.pkl')
        model = joblib.dump(self.model, save_path)
        return model

    def train(self, features, values):
        scale = StandardScaler()
        features = scale.fit_transform(features)
        classifier = LogisticRegression()
        self.model = classifier.fit(features, values)
        return self.model

    def predict(self, audio):

        if self.model is None:
            return EnvironmentError('attempting to call predict on an empty model')

        predictions: list = []

        if isinstance(audio, list):
            for item in audio:
                if os.path.isfile(item):
                    prediction = self.model.predict([self.extract_features(item)])
                    predictions.append(prediction)
                else:
                    predictions.append(None)
        else:
            if os.path.isfile(audio):
                prediction = self.model.predict([self.extract_features(audio)])
                predictions.append(prediction)
            else:
                predictions.append(None)

        return predictions

    def build_model_train_test(self, xml_audio_feats_path):
        df = pd.read_csv('../data/voice-data.xls')
        df = df.dropna()
        df = df.drop_duplicates()
        df = df.sample(frac=1)

        def get_class(row):
            if str(row).lower() == 'youth':
                return 1
            if str(row).lower() == 'adult':
                return 2
            if str(row).lower() == 'senior':
                return 3
            else:
                return 0

        Y = df['age']
        X = df.iloc[:, 1:-3].values
        Y = Y.apply(lambda row: get_class(row))

        # spliting sample to training and testing set
        X_train, x_test, Y_train, y_test = train_test_split(X, Y, test_size=0.3)

        # training
        self.train(X_train, Y_train)

        # testing
        y_predicted = self.predict(x_test)
        cm = confusion_matrix(y_test, y_predicted)
        asc = accuracy_score(y_test, y_predicted)
        return cm, asc

    def extract_features(self, media):

        # uses default sample rate of 22050
        y, sr = librosa.load(media, sr=22050)
        spectrogram = np.abs(librosa.stft(y))
        melspec = librosa.feature.melspectrogram(y=y, sr=sr)
        stft = np.abs(librosa.stft(y))
        mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
        mel = np.mean(librosa.feature.melspectrogram(y, sr=sr).T, axis=0)
        contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sr).T, axis=0)
        tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr).T, axis=0)
        chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sr).T, axis=0)

        features = []

        for i in range(mfccs.shape[0]):
            features.append(mfccs[i])
        for i in range(chroma.shape[0]):
            features.append(chroma[i])
        for i in range(mel.shape[0]):
            features.append(mel[i])
        for i in range(contrast.shape[0]):
            features.append(contrast[i])
        for i in range(tonnetz.shape[0]):
            features.append(tonnetz[i])

        return features
