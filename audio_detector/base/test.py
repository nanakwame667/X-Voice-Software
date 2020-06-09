from audio_detector.base.detector import AudioClassifier
classifier = AudioClassifier()

# you can also load previously built model
classifier.load('models/model.pkl')
classifier.predict('audiofile')

# how to pass args
# classifier.predict('path_to_audio_file')  # path to the audio file
# result format : [class_number]

# classifier.predict(['path_to_file_1', 'path_to_file_2', ...])  # or pass in a list of audio path
# result format : [class_number_for_file_1, class_number_for_file_2, ...]


# build the model from the xml file with the features
# confusion_matrix, accuracy_score = classifier.build_model_train_test('../data/voice-data.xls')
# print('accuracy: ', accuracy_score)




