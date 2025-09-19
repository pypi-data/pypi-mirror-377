from sklearn_crfsuite.utils import flatten
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
from balinese_nlp.postag.HMM import HiddenMarkovModelPOSTag
import pandas as pd
import numpy as np
import pickle
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


class BaseModel:
    def __init__(
        self,
        model_clf=None,
        feature_encoding={
            'w[i]': True,
            'w[i].lower()': True,
            'w[i].cluster()': True,
            'w[i].embedding()': True,
            'surr:w[i]': True,
            'surr:w[i].lower()': True,
            'surr:w[i].cluster()': True,
            'surr:w[i].embedding()': True,
            'pref:w[i]': True,
            'suff:w[i]': True,
            'surrPreff:w[i]': True,
            'surrSuff:w[i]': True,
            'w[i].isLessThres': True,
            'w[i].isdigit()': True,
            'surr:w[i].isdigit()': True,
            'w[i].isupper()': True,
            'surr:w[i].isupper()': True,
            'w[i].istitle()': True,
            'surr:w[i].istitle()': True,
            'w[i].isStartWord()': True,
            'w[i].isEndWord()': True,
            'pos:w[i]': True,
            'surrPos:w[i]': True,
        },
        pretrained_cluster_model=None,
        pretrained_embedding_model=None,
        embedding_component_decomposition=None

    ):
        # supervised ML from scikit-learn
        self.MODEL_CLF = model_clf
        self.FEATURE_ENCODING = feature_encoding
        self.TYPE_OF_BOOLEAN_FEATURES = [
            'isLessThres()',
            'isdigit()',
            'isupper()',
            'istitle()',
            'isStartWord()',
            'isEndWord()',
        ]
        self.PRETRAINED_CLUSTER_MODEL = None
        self.IS_USING_WORDCLUSTER = False
        if pretrained_cluster_model is not None:
            self.PRETRAINED_CLUSTER_MODEL = pretrained_cluster_model
            self.IS_USING_WORDCLUSTER = True

        self.PRETRAINED_EMBEDDING_MODEL = None
        self.IS_USING_WORDEMBEDDING = False
        self.VECTOR_SIZE = None
        if pretrained_embedding_model is not None:
            self.PRETRAINED_EMBEDDING_MODEL = pretrained_embedding_model
            self.IS_USING_WORDEMBEDDING = True
            self.VECTOR_SIZE = self.PRETRAINED_EMBEDDING_MODEL.vector_size
            self.EMBEDDING_DF_COLUMNS = [
                f'wv-{idx+1}' for idx in range(self.VECTOR_SIZE)]

        self.DECOMPOSITION_MODEL = None
        if embedding_component_decomposition is not None and embedding_component_decomposition > 0:
            self.DECOMPOSITION_MODEL = PCA(
                n_components=embedding_component_decomposition)

    def extract_word_embedding_features(self, data_df):
        """
        Function untuk ekstraksi fitur word embedding dengan dimensi vector size dari pretrained word embedding

        <Inputs>
        - data_df: formatted input data in dataframe

        <Outputs>
        - df_embedding_vectors: embedding vector dataframe with n x vector size. Each column was labelled with 'wv-idx'
        - df_reducted_embedding_vectors: embedding vector that has been reducted using decomposition model
        """
        word_embedding_vectors = list()
        for idx_data, data in data_df.iterrows():
            wv = self.PRETRAINED_EMBEDDING_MODEL.wv[data['Word']
                                                    ] if data['Word'] in self.PRETRAINED_EMBEDDING_MODEL.wv else np.zeros(self.VECTOR_SIZE)
            word_embedding_vectors.append(wv)

        # convert to df
        df_embedding_vectors = pd.DataFrame(
            word_embedding_vectors)
        df_embedding_vectors.columns = self.EMBEDDING_DF_COLUMNS

        # check if decomposition step is needed?
        df_reducted_embedding_vectors = None
        if self.DECOMPOSITION_MODEL is not None:
            df_reducted_embedding_vectors = self.__embedding_decomposition(
                df_embedding_vectors)
            self.VECTOR_SIZE = self.DECOMPOSITION_MODEL.n_components_

        return df_embedding_vectors, df_reducted_embedding_vectors

    def __embedding_decomposition(self, data_df):
        """
        Function untuk melakukan reduksi dimensi pada data_df hasil ekstraksi terutama hasil ekstraksi word embedding yang memiliki dimensi vektor tinggi

        <Inputs>
        - data_df: DataFrame hasil ekstraksi fitur berupa word_embedding atau fitur lainnya yang telah diconcat seperti word cluster

        <Outputs>
        - df: DataFrame yang berisi hasil reduksi fitur
        """
        # standarize the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data_df)

        # fit to decomposition model
        principal_components = self.DECOMPOSITION_MODEL.fit_transform(
            scaled_data)

        # convert results to dataframe
        column_names = self.EMBEDDING_DF_COLUMNS[0:
                                                 self.DECOMPOSITION_MODEL.n_components_]
        df = pd.DataFrame(data=principal_components,
                          columns=column_names)

        return df

    def extract_word_cluster_features(self, df_embedding_vectors):
        """
        Function untuk ekstraksi fitur word cluster dari data_df menggunakan pretrained word cluster model. 
        Pastikan model cluster Anda dilatih dengan dimensi yang sama dengan model word embedding yang Anda gunakan!

        <Inputs>
        - df_embedding_vectors: embedding vectors n x vector_size in dataframe format

        <Outputs>
        - df: word cluster dataframe with n x 1 ('Word Cluster Label')
        """
        # convert df_embedding_vectors to numpy array format since our predict_cluster_labels is required X_test in numpy array format
        X_test = None
        if isinstance(df_embedding_vectors, pd.DataFrame):
            X_test = df_embedding_vectors.to_numpy()

        # predict word cluster label using pretrained cluster model
        df = pd.DataFrame({
            'Word Cluster Label': self.PRETRAINED_CLUSTER_MODEL._predict_cluster_labels(X_test)
        })
        return df

    def concat_cluster_embedding_features(self, data_df):
        """
        Function untuk concatenate data_df dengan dataframe word cluster dan dataframe word embedding
        <Inputs>
        - data_df: formatted input data in dataframe

        <Outputs>
        - df: dataframe yang sudah di concat yang berisi data_df, data_word_cluster, data_word_embedding
        """
        if self.PRETRAINED_EMBEDDING_MODEL is None and self.PRETRAINED_CLUSTER_MODEL is None:
            raise ValueError(
                'Please insert your pretrained word embedding and cluster model first!')

        df_merged = pd.DataFrame()
        if self.PRETRAINED_EMBEDDING_MODEL is not None:
            df_embedding_vectors, _ = self.extract_word_embedding_features(
                data_df)
            df_merged = pd.concat((df_merged, df_embedding_vectors), axis=1)
        if self.PRETRAINED_CLUSTER_MODEL is not None:
            df_word_cluster = self.extract_word_cluster_features(
                df_embedding_vectors)
            df_merged = pd.concat((df_merged, df_word_cluster), axis=1)

        df = pd.concat((data_df, df_merged), axis=1)
        return df

    @staticmethod
    def dataframe2sequential(data_df, wv_vector_size=100, is_using_wordcluster=True, is_using_wordembedding=True):
        # convert dataframe to sequential data
        Seqdata = list()

        satua_titles = set(list(data_df['StoryTitle'].values))
        for title in satua_titles:
            stories = data_df[
                data_df['StoryTitle'] == title
            ]
            # get the sentences ID in the stories
            stories_sentences_ids = set(list(stories['SentenceID'].values))
            for sentence_id in stories_sentences_ids:
                stories_group_by_sentence = stories[
                    stories['SentenceID'] == sentence_id
                ]
                sentence_list = list()
                for idx, row in stories_group_by_sentence.iterrows():
                    word = row['Word']
                    pos_tag = row['POS Tag']
                    ner_tag = row['Character Named Entity Tagset']

                    word_cluster = row['Word Cluster Label'] if is_using_wordcluster else None
                    word_vectors = None
                    if is_using_wordembedding:
                        word_vectors = dict()
                        for idx in range(wv_vector_size):
                            word_vectors.update({
                                f'wv-{idx+1}': row[f'wv-{idx+1}']
                            })
                    sentence_list.append(
                        (word, pos_tag, ner_tag, word_cluster, word_vectors))
                Seqdata.append(sentence_list)
        return Seqdata

    @staticmethod
    def sentence2features(sent, bit_encoding, is_using_wordcluster, is_using_wordembedding):
        """
        Function to extract features from a sentence based on activated bit_encoding

        Args:
            - sent: input sentence will be extracted
            - bit_encoding: encoding of any activated feature extraction

        Returns:
            list of dictionary of extracted features of each words in sent
        """
        sentence_length = len(sent)
        w2features = list()
        for index_word, values in enumerate(sent):
            word = values[0]
            postag = values[1]

            # mapping procedure
            mapping = {
                'w[i]': {
                    'w[i]': word
                },
                'pref:w[i]': {
                    'pref:w[i][0:1]': word[0:1],
                    'pref:w[i][0:2]': word[0:2],
                    'pref:w[i][0:3]': word[0:3],
                },
                'suff:w[i]': {
                    'suff:w[i][-1:]': word[-1:],
                    'suff:w[i][-2:]': word[-2:],
                    'suff:w[i][-3:]': word[-3:],
                },
                'pos:w[i]': {
                    'pos:w[i]': postag
                },
                'w[i].lower()': {
                    'w[i].lower()': word.lower()
                },
                'w[i].isdigit()': {
                    'w[i].isdigit()': word.isdigit()
                },
                'w[i].isupper()': {
                    'w[i].isupper()': word.isupper()
                },
                'w[i].istitle()': {
                    'w[i].istitle()': word.istitle()
                },
                'w[i].isLessThres': {
                    'w[i].istitle()': True if len(word) < 5 else False
                },
                'surr:w[i]': dict(),
                'surr:w[i].lower()': dict(),
                'surr:w[i].cluster()': dict(),
                'surr:w[i].embedding()': dict(),
                'surrPreff:w[i]': dict(),
                'surrSuff:w[i]': dict(),
                'surr:w[i].isdigit()': dict(),
                'surr:w[i].isupper()': dict(),
                'surr:w[i].istitle()': dict(),
                'w[i].isStartWord()': dict(),
                'w[i].isEndWord()': dict(),
                'surrPos:w[i]': dict(),
            }
            # check if cluster or word embedding features are activated
            if is_using_wordcluster:
                word_cluster = values[3]
                map_word_cluster = {
                    'w[i].cluster()': {
                        'w[i].cluster()': word_cluster
                    }
                }
                mapping.update(map_word_cluster)

            if is_using_wordembedding:
                word_vectors = values[4]
                map_word_embedding = {
                    'w[i].embedding()': dict([(f"w[i].embedding()|[{k}]", v) for k, v in word_vectors.items()])
                }
                mapping.update(map_word_embedding)

            if index_word > 0:
                # ambil informasi 1 kata sebelumnya
                wordPrev1 = sent[index_word-1][0]
                posPrev1 = sent[index_word-1][1]

                mapping['surr:w[i]'].update({
                    'surr:w[i-1]': wordPrev1
                })
                mapping['surr:w[i].lower()'].update({
                    'surr:w[i-1].lower()': wordPrev1.lower()
                })

                if is_using_wordcluster:
                    wordclusterPrev1 = sent[index_word-1][3]
                    mapping['surr:w[i].cluster()'].update({
                        'surr:w[i-1].cluster()': wordclusterPrev1
                    })
                if is_using_wordembedding:
                    wordvectorPrev1 = sent[index_word-1][4]
                    mapping['surr:w[i].embedding()'].update(
                        dict([(f"surr:w[i-1].embedding()[{k}]", v) for k, v in wordvectorPrev1.items()]))

                mapping['surrPreff:w[i]'].update({
                    'surrPreff:w[i-1][0:1]': wordPrev1[0:1],
                    'surrPreff:w[i-1][0:2]': wordPrev1[0:2],
                    'surrPreff:w[i-1][0:3]': wordPrev1[0:3],
                })
                mapping['surrSuff:w[i]'].update({
                    'surrSuff:w[i-1][-1:]': wordPrev1[-1:],
                    'surrSuff:w[i-1][-2:]': wordPrev1[-2:],
                    'surrSuff:w[i-1][-3:]': wordPrev1[-3:],
                })
                mapping['surr:w[i].isdigit()'].update({
                    'surr:w[i-1].isdigit()': wordPrev1.isdigit()
                })
                mapping['surr:w[i].isupper()'].update({
                    'surr:w[i-1].isupper()': wordPrev1.isupper()
                })
                mapping['surr:w[i].istitle()'].update({
                    'surr:w[i-1].istitle()': wordPrev1.istitle()
                })
                mapping['w[i].isStartWord()'].update({
                    'w[i].isStartWord()': False
                })
                mapping['w[i].isEndWord()'].update({
                    'w[i].isEndWord()': False
                })
                mapping['surrPos:w[i]'].update({
                    'surrPos:w[i-1]': posPrev1
                })

            if index_word < sentence_length-1:
                # ambil informasi 1 kata setelahnya
                wordNext1 = sent[index_word+1][0]
                posNext1 = sent[index_word+1][1]
                wordclusterNext1 = sent[index_word+1][3]
                wordvectorNext1 = sent[index_word+1][4]

                mapping['surr:w[i]'].update({
                    'surr:w[i+1]': wordNext1
                })
                mapping['surr:w[i].lower()'].update({
                    'surr:w[i+1].lower()': wordNext1.lower()
                })
                if is_using_wordcluster:
                    wordclusterNext1 = sent[index_word+1][3]
                    mapping['surr:w[i].cluster()'].update({
                        'surr:w[i+1].cluster()': wordclusterNext1
                    })
                if is_using_wordembedding:
                    wordvectorNext1 = sent[index_word+1][4]
                    mapping['surr:w[i].embedding()'].update(
                        dict([(f"surr:w[i+1].embedding()[{k}]", v) for k, v in wordvectorNext1.items()]))

                mapping['surrPreff:w[i]'].update({
                    'surrPreff:w[i+1][0:1]': wordNext1[0:1],
                    'surrPreff:w[i+1][0:2]': wordNext1[0:2],
                    'surrPreff:w[i+1][0:3]': wordNext1[0:3],
                })
                mapping['surrSuff:w[i]'].update({
                    'surrSuff:w[i+1][-1:]': wordNext1[-1:],
                    'surrSuff:w[i+1][-2:]': wordNext1[-2:],
                    'surrSuff:w[i+1][-3:]': wordNext1[-3:],
                })
                mapping['surr:w[i].isdigit()'].update({
                    'surr:w[i+1].isdigit()': wordNext1.isdigit()
                })
                mapping['surr:w[i].isupper()'].update({
                    'surr:w[i+1].isupper()': wordNext1.isupper()
                })
                mapping['surr:w[i].istitle()'].update({
                    'surr:w[i+1].istitle()': wordNext1.istitle()
                })
                mapping['w[i].isStartWord()'].update({
                    'w[i].isStartWord()': False
                })
                mapping['w[i].isEndWord()'].update({
                    'w[i].isEndWord()': False
                })
                mapping['surrPos:w[i]'].update({
                    'surrPos:w[i+1]': posNext1
                })

            if index_word == 0 or index_word == sentence_length:
                mapping['w[i].isStartWord()'].update({
                    'w[i].isStartWord()': True
                })
                mapping['w[i].isEndWord()'].update({
                    'w[i].isEndWord()': False
                })
                if index_word == sentence_length:
                    mapping['w[i].isStartWord()'].update({
                        'w[i].isStartWord()': False
                    })
                    mapping['w[i].isEndWord()'].update({
                        'w[i].isEndWord()': True
                    })

            # features untuk setiap w[i] pada sent
            features = dict()
            for key, isActive in bit_encoding.items():
                if isActive is True:
                    features.update(mapping[key])
            w2features.append(features)

        return w2features

    @staticmethod
    def sentence2labels(sent):
        return [label for token, postag, label, word_cluster, word_vectors in sent]

    @staticmethod
    def sentence2tokens(sent):
        return [token for token, postag, label, word_cluster, word_vectors in sent]

    @staticmethod
    def token_with_predicted_tags(token_sentence, y_pred):
        token_with_predicted_tag = list()
        for idx_token, token in enumerate(token_sentence):
            token_with_predicted_tag.append(
                str(token) + "/" + str(y_pred[idx_token]))
        return token_with_predicted_tag

    @staticmethod
    def extract_predicted_characters_from_sentence(sentence, y_pred):
        """
        <Description>
        Module untuk mengekstrak daftar karakter dari kalimat yang sudah diprediksi model
        """
        token_sentence = sentence.split(' ')
        list_of_characters_from_example_kalimat = list()
        counter_list_of_characters = -1
        for idx_word, word in enumerate(token_sentence):
            split_ner_tags = y_pred[idx_word].split('-')
            if split_ner_tags[0] == 'B':
                list_of_characters_from_example_kalimat.append(word)
                counter_list_of_characters += 1
            elif split_ner_tags[0] == 'I':
                if counter_list_of_characters == -1:
                    list_of_characters_from_example_kalimat.append(word)
                    counter_list_of_characters += 1
                else:
                    list_of_characters_from_example_kalimat[counter_list_of_characters] = list_of_characters_from_example_kalimat[
                        counter_list_of_characters] + " " + word
            elif split_ner_tags[0] == 'O':
                continue

        # return value
        n_predicted_chars = len(list_of_characters_from_example_kalimat)
        context = {
            'n_predicted_chars': n_predicted_chars,
            'predicted_chars': '; '.join(list_of_characters_from_example_kalimat) if n_predicted_chars != 0 else np.nan
        }
        return context

    @staticmethod
    def identify_characters(preprocessed_story, pretrained_model):
        """
        Function to identify all character named entities present in a given story
        <Parameters>:
        - preprocessed_story: <string>
            --> a string of Balinese story text. You can pass a preprocessed text here.
        - pretrained_model: <pickle object>
            --> pass our one of our loaded pretrained model here.
        <Output>:
        - List of identified characters by the provided pretrained models 
        """
        # Split the story into list of sentences
        preprocessed_story = preprocessed_story.split("\\n")
        preprocessed_story.pop()  # pop empty string

        # identify the character entities from each sentence
        predicted_characters = set()
        for sentence in preprocessed_story:
            sentence = sentence.strip()
            y_pred, token_with_predicted_chars = pretrained_model.predict_sentence(
                sentence)
            results = pretrained_model.extract_predicted_characters_from_sentence(
                sentence, y_pred)
            results_predicted_chars = results['predicted_chars']
            if results_predicted_chars is not np.nan and results_predicted_chars != "":
                for pred_char in results_predicted_chars.split(';'):
                    predicted_characters.add(pred_char.strip())

        return list(predicted_characters)

    def _prepare_input_sentence(self, sentence):
        """
        Function untuk mempersiapkan ekstraksi fitur dari sebuah kalimat
        """
        # tokenize sentence
        token_sentence = sentence.strip().split(' ')

        # buat sequential data
        seq_data = list()
        for token in token_sentence:
            # ekstrak pos tag
            pos = HiddenMarkovModelPOSTag().predict(
                token).replace('\n', '').split('/')[1]
            ner_label = ''

            # ekstrak word vector
            word_vectors = None
            if self.IS_USING_WORDEMBEDDING:
                wv = self.PRETRAINED_EMBEDDING_MODEL.wv[token] if token in self.PRETRAINED_EMBEDDING_MODEL.wv else np.zeros(
                    self.VECTOR_SIZE, dtype=np.float32)
                df_wv = pd.DataFrame([wv])
                df_wv.columns = self.EMBEDDING_DF_COLUMNS
                word_vectors = dict()
                for idx in range(self.VECTOR_SIZE):
                    word_vectors[self.EMBEDDING_DF_COLUMNS[idx]] = wv[idx]

            # ekstrak word cluster
            # Menggunakan `float32` untuk mencegah error ini:
            # ValueError: Buffer dtype mismatch, expected 'float' but got 'double'
            word_cluster = None
            if self.IS_USING_WORDCLUSTER:
                X_array = df_wv.to_numpy()
                if isinstance(X_array, pd.DataFrame):
                    X_array = X_array.values.astype(np.float32)
                else:
                    X_array = np.asarray(X_array, dtype=np.float32)
                X_array = X_array.reshape(1, -1)
                word_cluster = self.PRETRAINED_CLUSTER_MODEL._predict_cluster_labels(X_array)[
                    0]

            # convert all information to sequential data
            seq_data.append(
                (token, pos, ner_label, word_cluster, word_vectors))

        # ekstraksi fitur
        X_features = [
            self.sentence2features(seq_data, self.FEATURE_ENCODING,
                                   self.IS_USING_WORDCLUSTER, self.IS_USING_WORDEMBEDDING)
        ]
        return token_sentence, X_features

    def evaluate(self, y_train, y_pred_train, y_test, y_pred_test, average_metric='macro'):
        # flatten process
        if isinstance(y_train, np.ndarray):
            y_train = y_train.flatten()
        else:  # assuming it's a list if not np.ndarray
            y_train = flatten(y_train)

        if isinstance(y_pred_train, np.ndarray):
            y_pred_train = y_pred_train.flatten()
        else:
            y_pred_train = flatten(y_pred_train)

        if isinstance(y_test, np.ndarray):
            y_test = y_test.flatten()
        else:
            y_test = flatten(y_test)

        if isinstance(y_pred_test, np.ndarray):
            y_pred_test = y_pred_test.flatten()
        else:
            y_pred_test = flatten(y_pred_test)

        self.test_evaluation = {
            'accuracy': accuracy_score(y_test, y_pred_test),
            'recall': recall_score(y_test, y_pred_test, average=average_metric, zero_division=0),
            'precision': precision_score(y_test, y_pred_test, average=average_metric, zero_division=0),
            'f1_score': f1_score(y_test, y_pred_test, average=average_metric, zero_division=0)
        }
        self.train_evaluation = {
            'accuracy': accuracy_score(y_train, y_pred_train),
            'recall': recall_score(y_train, y_pred_train, average=average_metric, zero_division=0),
            'precision': precision_score(y_train, y_pred_train, average=average_metric, zero_division=0),
            'f1_score': f1_score(y_train, y_pred_train, average=average_metric, zero_division=0)
        }
        return self.train_evaluation, self.test_evaluation

    def classification_report(self, y_train, y_pred_train, y_test, y_pred_test, print_train=True, relax_match=False, target_names=None):
        # Ensure all inputs are flattened lists
        # Use sklearn_crfsuite.utils.flatten for lists
        # Or convert to numpy array and then flatten for numpy arrays

        if isinstance(y_train, np.ndarray):
            y_train = y_train.flatten()
        else:  # assuming it's a list if not np.ndarray
            y_train = flatten(y_train)

        if isinstance(y_pred_train, np.ndarray):
            y_pred_train = y_pred_train.flatten()
        else:
            y_pred_train = flatten(y_pred_train)

        if isinstance(y_test, np.ndarray):
            y_test = y_test.flatten()
        else:
            y_test = flatten(y_test)

        if isinstance(y_pred_test, np.ndarray):
            y_pred_test = y_pred_test.flatten()
        else:
            y_pred_test = flatten(y_pred_test)

        if relax_match:
            y_train = np.array(pd.Series(y_train).apply(lambda x: x.split(
                '-')[0] if len(x.split('-')) == 1 else x.split('-')[1]))
            y_pred_train = np.array(pd.Series(y_pred_train).apply(
                lambda x: x.split('-')[0] if len(x.split('-')) == 1 else x.split('-')[1]))
            y_test = np.array(pd.Series(y_test).apply(lambda x: x.split(
                '-')[0] if len(x.split('-')) == 1 else x.split('-')[1]))
            y_pred_test = np.array(pd.Series(y_pred_test).apply(
                lambda x: x.split('-')[0] if len(x.split('-')) == 1 else x.split('-')[1]))

        if print_train:
            print('='*50)
            print('CLASSIFICATION REPORT FOR TRAINING DATA\n')
            print(classification_report(y_train, y_pred_train,
                  digits=4, target_names=target_names))
            print('='*50)
        print('='*50)
        print('CLASSIFICATION REPORT FOR TESTING DATA\n')
        print(classification_report(y_test, y_pred_test,
              digits=4, target_names=target_names))
        print('='*50)

    def save(self, saved_model, path_to_save, filename):
        """
        Function to save the pretrained model and others data in pickle format (.pkl)

        Args:
            - saved_model: dictionary contain data that will be saved, including 'model' key that
            - path_to_save: path directory for saving the model
            - filename: filename with .pkl suffix

        Returns: None
        """
        pickle.dump(saved_model, open(path_to_save+filename, 'wb'))
