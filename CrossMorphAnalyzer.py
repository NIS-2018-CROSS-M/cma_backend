import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
import re


class CrossMorphAnalyzer(object):
    def __init__(self):
        self.Morph2Tags = {}
        self.classifier = None
        self.letters_to_num = None
        self.num_to_pos = None
        self.letters_num = None

    def fit(self, train):
        train.dropna(inplace=True)
        for POS in ['NOUN', 'VERB']:
            self.Morph2Tags[POS] = self._make_dict_for_pos(train, POS)

        all_letters = sorted(list(set(''.join(train['word']))))
        all_pos = list(set(train['POS']))
        letters_num = len(all_letters)
        letters_to_num = {letter: num for num, letter in enumerate(all_letters)}
        pos_to_num = {pos: num for num, pos in enumerate(all_pos)}
        num_to_pos = {num: pos for num, pos in enumerate(all_pos)}

        X_pos = []
        y_pos = [pos_to_num[POS] for POS in train['POS']]
        for word in train['word']:
            tmp_list = [0.0] * (letters_num + 1)
            for letter in word:
                letter_to_num = letters_to_num.get(letter, letters_num)
                tmp_list[letter_to_num] = tmp_list[letter_to_num] + 1
            X_pos.append(tmp_list)

        X_train, X_test, y_train, y_test = train_test_split(np.array(X_pos), np.array(y_pos))
        classifier = OneVsRestClassifier(LogisticRegression())
        classifier.fit(X_train, y_train)

        self.classifier = classifier
        self.letters_to_num = letters_to_num
        self.num_to_pos = num_to_pos
        self.letters_num = letters_num

    def predict(self, list_of_words):
        output = []
        for word in tqdm(list_of_words):
            output.append(self._predict_word(word))
        return output

    def _predict_word(self, word):
        tmp_list = [0.0] * (self.letters_num + 1)
        for letter in word:
            letter_to_num = self.letters_to_num.get(letter, self.letters_num)
            tmp_list[letter_to_num] = tmp_list[letter_to_num] + 1
        pos_tag = self.num_to_pos[self.classifier.predict([tmp_list])[0]]
        if pos_tag in ['NOUN', 'VERB']:
            word_form, word_morph, word_tags = self._predict_tags_for_word(word, pos_tag)
        else:
            word_form, word_morph, word_tags = word, '', ''
        return [word, word_form, pos_tag, word_tags]

    def _predict_tags_for_word(self, word, POS):
        dict_for_pos = self.Morph2Tags[POS]
        len_of_word = len(word)
        for morph, tags in dict_for_pos.items():
            morph_len = len(morph)
            if len_of_word >= morph_len:
                if word[-morph_len:] == morph:
                    word_form = word[:-morph_len]
                    word_morph = morph
                    word_tags = tags
                    break
        if morph == '':
            word_form = word
            word_morph = ''
            word_tags = dict_for_pos.get('', '')
        return word_form, word_morph, word_tags

    def _make_dict_for_pos(self, train, POS):
        POS_train = train[train['POS'] == POS]
        POS_train['diff_between_word_and_wordform'] = POS_train.apply(lambda x: re.sub(x.wordform, '', x.word, count=1)
                                                                      if not len(re.findall('[\(\)]', x.wordform)) > 0 else 'NaN',
                                                                      axis=1)
        POS_train = POS_train[POS_train['diff_between_word_and_wordform'] != 'NaN']
        morph_to_tags = {}
        for line in tqdm(POS_train.values):
            morph_to_tags[line[-1]] = line[-2]
        morph_to_tags = {k: v for k, v in sorted(morph_to_tags.items(), key=lambda item: -len(item[0]))}
        return morph_to_tags
