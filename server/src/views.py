from src import app
from src.models import Model
from flask import request
import simplejson

# initialize the model
CORR = Model()
print("================================================================")


def json_dumps(data):
    return simplejson.dumps(data, ensure_ascii=False, ignore_nan=True)


@app.route('/get_stock_list', methods=['GET'])
def get_stock_list():
    return json_dumps(CORR.get_stock_list())


@app.route('/set_stocks', methods=['POST'])
def set_stocks():
    post_data = request.data.decode()
    if post_data != "":
        post_data = simplejson.loads(post_data)
    return json_dumps(CORR.set_query_codes(post_data))


@app.route('/set_period', methods=['POST'])
def set_period():
    post_data = request.data.decode()
    if post_data != "":
        post_data = simplejson.loads(post_data)
        print(post_data)
        CORR.corr_community_detection(start_date=post_data[0][:10], end_date=post_data[1][:10])
    return json_dumps(post_data != "")


@app.route('/set_correlation', methods=['POST'])
def set_correlation():
    post_data = request.data.decode()
    response = []
    if post_data != "":
        post_data = simplejson.loads(post_data)
        response = CORR.corr_community_filter(left_threshold=post_data[0], right_threshold=post_data[1])
    return json_dumps(response)


@app.route('/get_correlation_matrix', methods=['GET'])
def get_correlation_matrix():
    corr_matrix = CORR.list_to_corr_matrix()
    corr_matrix = CORR.two_phase_hierarchical_clustering(corr_matrix)
    corr_matrix = {
        'columns': corr_matrix.close.columns.to_list(),
        'close': corr_matrix.close,
        'vol': corr_matrix.vol,
        'combined': corr_matrix.combined,
    }
    with open('../client/src/components/matrix.json', 'r+') as file:
        simplejson.dump(corr_matrix, file)
    return json_dumps(corr_matrix)
