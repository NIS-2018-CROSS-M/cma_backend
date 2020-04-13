from CrossMorphAnalyzer import CrossMorphAnalyzer
from Transliterator import Transliterator
import pickle
import os
import datetime
import threading


# нужен метод который принимает путь к файлу с транслитерацией, путь к файлу с корпусом, путь к пиклу с моделью, путь к файлу для результата.
# Он создаёт пустой файл "путь к файлу для результата.working" и запускает обработку корпуса моделью.
# Когда обработка закончилась, файл .working удаляется, а обработанный корпус записан в "путь к файлу для результата.done"

def predict_for_file(trans_table_path, dataset_path, model_path, result_path_no_f_extension):
    print(trans_table_path, dataset_path, model_path, result_path_no_f_extension)
    open(f"{result_path_no_f_extension}.working", 'w').close()  # aka touch

    transliterator = Transliterator(trans_table_path)

    model: CrossMorphAnalyzer
    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)

    list_for_predict = transliterator.transliterate(dataset_path).split('\n')

    output = model.predict(list_for_predict)
    output_one_line = '\n'.join(['\t'.join(line) for line in output])

    with open('{}.done'.format(result_path_no_f_extension), 'w') as output_file:
        output_file.write(output_one_line)

    os.remove(f"{result_path_no_f_extension}.working")

def predict_runner(trans_table_path, dataset_path, model_path=None, result_path=None):
    if result_path is None:
        result_path = f"{dataset_path}_{int(datetime.datetime.now().timestamp())+1}"

    args = (trans_table_path+".translit", dataset_path+".data", model_path, result_path)
    try:
        threading.Thread(target=predict_for_file, args=args).start()
    except:
        pass
    return result_path
