from src import app
from src.models import Model
from flask import request
import simplejson

# initialize the model
CORR = Model()
print("================================================================")


def json_dumps(data):
    return simplejson.dumps(data, ensure_ascii=False, ignore_nan=True)


@app.route('/get')
def get():
    return json_dumps("Get")


@app.route('/get_corr_community', methods=['POST'])
def get_corr_community():
    """
    Get stock codes from post request
    :return: Boolean
    True if successfully set, i.e. stock codes are right
    False if unsuccessful
    """
    post_data = request.data.decode()
    if post_data != "":
        post_data = simplejson.loads(post_data)
    return json_dumps(CORR.set_query_codes(post_data))
