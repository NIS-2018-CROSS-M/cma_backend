from CrossMorphAnalyzer import CrossMorphAnalyzer
import pandas as pd
import pickle

if __name__ == '__main__':
    train = pd.read_csv('trk-uncovered-transliterated', sep='\t', header=None)
    train.rename({0: 'language',
                  1: 'word',
                  2: 'wordform',
                  3: 'POS',
                  4: 'tags'}, inplace=True, axis=1)
    analyzer = CrossMorphAnalyzer()
    analyzer.fit(train)

    with open('trk_model.pcl', 'wb') as model_file:
        pickle.dump(analyzer, model_file)
