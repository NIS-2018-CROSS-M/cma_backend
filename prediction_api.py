import os
from flask import Flask, Response, request, json, jsonify, send_file, make_response
import datetime

from predict_for_file import predict_runner

app = Flask(__name__)

@app.route('/upload_translit_table', methods=['POST'])
def upload_translit_table():
    # check if the post request has the file part
    extension = "translit"
    response_dict = receive_file(request.files, extension)

    response_json = json.dumps(response_dict)
    content_type = "application/json; charset=utf-8"

    response = Response(response=response_json, content_type=content_type, status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    return response


@app.route('/upload_data_to_process', methods=['POST'])
def upload_data_to_process():
    # check if the post request has the file part
    extension = "data"
    response_dict = receive_file(request.files, extension)
    dataset_path = response_dict["saved"]
    trans_fn = request.args.get("saved_trans_fn")
    lang = request.args.get("lang")
    if lang == "tur":
        model_path = "trk_model.pcl"
    elif lang == "roa":
        model_path = "roa_model.pcl"
    else:
        model_path = None
    print(trans_fn, dataset_path, model_path)
    result_path = predict_runner(trans_table_path=f"{trans_fn}",
                                 dataset_path=f"{dataset_path}",
                                 model_path=model_path)

    app.logger.info(trans_fn, dataset_path, model_path, result_path)
    response_dict["result"] = result_path

    response_json = json.dumps(response_dict)
    content_type = "application/json; charset=utf-8"

    response = Response(response=response_json, content_type=content_type, status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    return response


@app.route('/download', methods=['GET'])
def download():
    # check if the post request has the file part
    extension = "data"
    result_fn = request.args.get("result_fn")

    response = make_response(send_file(result_fn+".done", as_attachment=True))
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    return response


@app.route('/is_done', methods=['GET'])
def is_done():
    # check if the post request has the file part
    extension = "data"
    result_fn = request.args.get("result_fn")
    response_dict = {}
    print(f"checking if {result_fn}.done exists")

    response_dict["done"] = os.path.exists(result_fn+".done")
    response_json = json.dumps(response_dict)
    content_type = "application/json; charset=utf-8"

    response = Response(response=response_json, content_type=content_type, status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    return response


def receive_file(request_files, extension):
    if 'file' not in request_files:
        print('No file part')
        app.logger.info('No file part')
        response_dict = {"result": "bad"}
    else:
        response_dict = {"result": "initial_bad"}

        file = request_files['file']
        # if user does not select file, browser also
        # submit an empty part without filename

        if file.filename == '':
            print("i got a file with empty filename")
            app.logger.info("i got a file with empty filename")

        if file:  # если с файлом все ок
            saved_filename = int(datetime.datetime.now().timestamp())
            file_to_save_fn = f"{saved_filename}.{extension}"
            err = ''
            try:
                app.logger.info("before writing to file")
                file.save(file_to_save_fn)
                app.logger.info("after writing to file")
            except:
                err_msg2 = "ERR: smth wrong when saving file 1"
                err += err_msg2
                print(err_msg2)
                app.logger.info(err_msg2)

            if not err:
                response_dict = {"saved": saved_filename}
            else:
                response_dict = {"result": err}
    return response_dict

