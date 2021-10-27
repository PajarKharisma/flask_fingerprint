import os
import uuid
import base64

from flask import render_template, Blueprint, request, redirect, Response, flash, url_for, send_file, make_response, jsonify
from werkzeug.utils import secure_filename
from config.path import Path

import core.heuristic as heuristic
import core.utils.file_util as file_util

from config import *
from views import deteksi

@deteksi.route('/', methods=["GET","POST"])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        file_util.empty_dir(Path.temp)
        content = request.json
        index_person = content['index_person']
        imgdata = base64.b64decode(content['img'])
        filename = os.path.join(Path.temp, '{}.tif'.format(str(uuid.uuid4().hex)))
        with open(filename, 'wb') as f:
            f.write(imgdata)
        pred_result = "Not Match"
        for i in range(1,9):
            final_comp_path = Path.base_comp_path + str(index_person) + str('_') + str(i) + str('.tif')
            flag, array_data = heuristic.calculateMatching(filename, final_comp_path,1, 0)
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