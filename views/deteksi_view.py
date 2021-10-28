import os
import uuid
import base64

from flask import render_template, Blueprint, request, redirect, Response, flash, url_for, send_file, make_response, jsonify
from werkzeug.utils import secure_filename
from config.path import Path

import core.heuristic as heuristic
import core.learning as learning
import core.utils.file_util as file_util

from config import *
from views import deteksi

net = learning.Net()

@deteksi.route('/v1', methods=["GET","POST"])
def index1():
    if request.method == 'GET':
        return render_template('index1.html')
    else:
        file_util.empty_dir(Path.temp)
        file = request.files['input_img']
        index_person = request.form['index_person']
        filename = secure_filename(file.filename)
        file.save(os.path.join(Path.temp, filename))
        img = os.path.join(Path.temp, filename)
        final_comp_path = ''
        pred_score = 0
        for i in range(0,6):
            for j in range(1,91):
                final_comp_path = f'{Path.v1_base_comp_path}/{index_person}_{i}_{j}.bmp'
                pred = net.calculateMatching(img, final_comp_path, True)
                if pred[0][0]*100 > 95:
                    pred_score = pred[0][0]*100
                    break
            else:
                continue
            break

        pred_result = ''
        if pred_score <= 95:
            pred_result = 'Not Match'
        else:
            pred_result = 'Match'

        response = make_response(
            jsonify(
                    {
                        "score" : pred_score,
                        "result" : pred_result,
                        "final_comp_path" : final_comp_path
                    }
                ),
                200,
            )
        response.headers["Content-Type"] = "application/json"
        return response

@deteksi.route('/v2', methods=["GET","POST"])
def index2():
    if request.method == 'GET':
        return render_template('index2.html')
    else:
        file_util.empty_dir(Path.temp)
        file = request.files['input_img']
        index_person = request.form['index_person']
        filename = secure_filename(file.filename)
        file.save(os.path.join(Path.temp, filename))
        img = os.path.join(Path.temp, filename)
        pred_result = "Not Match"
        for i in range(1,9):
            final_comp_path = Path.v2_base_comp_path + str(index_person) + str('_') + str(i) + str('.tif')
            flag, array_data = heuristic.calculateMatching(img, final_comp_path,1, 0)
            if flag == 0:
                pred_result = "Match"
                break
            
        response = make_response(
            jsonify(
                    {
                        "result": pred_result
                    }
                ),
                200,
            )
        response.headers["Content-Type"] = "application/json"
        return response

@deteksi.route('/about', methods=['GET'])
def about():
    if request.method == 'GET':
        return render_template('about.html')