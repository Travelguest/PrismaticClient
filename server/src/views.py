from src import app
from src.models import Model
from flask import request
import simplejson
import math

# initialize the model
CORR = Model()
print("================================================================")


def json_dumps(data):
    return simplejson.dumps(data, ensure_ascii=False, ignore_nan=True)


@app.route('/get_stock_list', methods=['GET'])
def get_stock_list():
    return json_dumps(CORR.get_stock_list())


@app.route('/get_corr_dist', methods=['POST'])
def get_corr_dist():
    post_data = request.data.decode()
    if post_data != "":
        post_data = simplejson.loads(post_data)
    # with open('../client/src/components/index_corr_dist.json', 'w+') as file:
    #     simplejson.dump(CORR.get_corr_dist(post_data), file)
    return json_dumps(CORR.get_corr_dist(post_data))


@app.route('/get_corr_clusters_all_years', methods=['POST'])
def get_corr_clusters_all_years():
    post_data = request.data.decode()
    response = []
    if post_data != "":
        post_data = simplejson.loads(post_data)
        response = CORR.get_corr_clusters_all_years(left_threshold=post_data[0], right_threshold=post_data[1])
        # with open('../client/src/components/corr_clusters_all_years.json', 'w+') as file:
        #     simplejson.dump(response, file)
    return json_dumps(response)


@app.route('/get_business_tag_table', methods=['POST'])
def get_business_tag_table():
    post_data = request.data.decode()
    response = []
    if post_data != "":
        post_data = simplejson.loads(post_data)
        response = CORR.get_business_tag_table(left_threshold=post_data[0], right_threshold=post_data[1])
        # with open('../client/src/components/business_tag_table.json', 'w+') as file:
        #     simplejson.dump(response, file)
    return json_dumps(response)


@app.route('/get_correlation_matrix', methods=['GET'])
def get_correlation_matrix():
    corr_matrix = CORR.list_to_corr_matrix()
    corr_matrix = CORR.two_phase_hierarchical_clustering(corr_matrix)
    if corr_matrix is not False:
        corr_matrix = {
            'columns': corr_matrix[0],
            'corr': corr_matrix[1],
        }
        # with open('../client/src/components/matrix.json', 'w+') as file:
        #     simplejson.dump(corr_matrix, file)
    return json_dumps(corr_matrix)


@app.route('/set_period', methods=['POST'])
def set_period():
    post_data = request.data.decode()
    if post_data != "":
        post_data = simplejson.loads(post_data)
        CORR.corr_community_detection(
            start_date=post_data[0][:10],
            end_date=post_data[1][:10],
            # method='spearman'
        )
    return json_dumps(post_data != "")


@app.route('/get_corr_tri_market', methods=['POST'])
def get_corr_tri_market():
    post_data = request.data.decode()
    response = {}
    if post_data != "":
        post_data = simplejson.loads(post_data)
        pinus = CORR.rolling_corr_market(
            query_code=post_data[0],
            start_date=post_data[1][:10],
            end_date=post_data[2][:10]
        )
        response = {
            'name': 'SSE Composite Index',
            'date': pinus.columns.to_list(),
            'window': pinus.index.to_list(),
            'corr': [
                i
                for num, row in pinus.iterrows()
                for i in row.fillna(2).to_list()[-(len(pinus)+2-num):]
            ]
        }
        # with open(f'../client/src/components/pinus_market_{post_data[0]}.json', 'w+') as file:
        #     simplejson.dump(response, file)
    return json_dumps(response)


@app.route('/get_corr_tri_sector', methods=['POST'])
def get_corr_tri_sector():
    post_data = request.data.decode()
    response = {}
    if post_data != "":
        post_data = simplejson.loads(post_data)

        sector_info = CORR.find_index_code(post_data[0])
        pinus = CORR.rolling_corr_market(
            query_code=post_data[0],
            index_code=sector_info.in_code,
            start_date=post_data[1][:10],
            end_date=post_data[2][:10]
        )
        response = {
            'name': sector_info['name'],
            'date': pinus.columns.to_list(),
            'window': pinus.index.to_list(),
            'corr': [
                i
                for num, row in pinus.iterrows()
                for i in row.fillna(2).to_list()[-(len(pinus)+2-num):]
            ]
        }
        # with open(f'../client/src/components/pinus_sector_{post_data[0]}.json', 'w+') as file:
        #     simplejson.dump(response, file)
    return json_dumps(response)


@app.route('/get_corr_tri_stock', methods=['POST'])
def get_corr_tri_stock():
    post_data = request.data.decode()
    response = {}
    if post_data != "":
        post_data = simplejson.loads(post_data)

        pinus = CORR.rolling_corr_stock(
            query_code_left=post_data[0],
            query_code_right=post_data[1],
            start_date=post_data[2][:10],
            end_date=post_data[3][:10]
        )
        response = {
            'name': f'{post_data[0]} against {post_data[1]}',
            'date': pinus.columns.to_list(),
            'window': pinus.index.to_list(),
            'corr': [
                i
                for num, row in pinus.iterrows()
                for i in row.fillna(2).to_list()[-(len(pinus)+2-num):]
            ]
        }
        # with open(f'../client/src/components/pinus_stock_{post_data[0]}.json', 'w+') as file:
        #     simplejson.dump(response, file)
    return json_dumps(response)
