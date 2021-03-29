from src import app
from src.models import Model
from flask import request
import simplejson

# initialize the model
CORR = Model()
print("================================================================")


def json_dumps(data):
    return simplejson.dumps(data, ensure_ascii=False, ignore_nan=True)


'''
Initialization
'''


@app.route('/get_stock_list', methods=['GET'])
def get_stock_list():
    # with open(f'../client/src/components/stock_list.json', 'w+') as file:
    #     json_dumps(CORR.get_stock_list())
    return json_dumps(CORR.get_stock_list())


'''
Control Panel
'''


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


@app.route('/get_corr_clusters_one_year', methods=['POST'])
def get_corr_clusters_one_year():
    post_data = request.data.decode()
    response = []
    if post_data != "":
        post_data = simplejson.loads(post_data)
        response = CORR.get_corr_clusters_one_year(year=post_data[0], left_threshold=post_data[1], right_threshold=post_data[2])
    return json_dumps(response)


@app.route('/get_business_tag_table', methods=['POST'])
def get_business_tag_table():
    post_data = request.data.decode()
    response = []
    if post_data != "":
        post_data = simplejson.loads(post_data)
        response = CORR.get_business_tag_table(left_threshold=post_data[0], right_threshold=post_data[1])
        # with open('../client/src/components/busineƒss_tag_table.json', 'w+') as file:
        #     simplejson.dump(response, file)
    return json_dumps(response)


'''
Correlation Matrix
'''


@app.route('/get_correlation_matrix', methods=['POST'])
def get_correlation_matrix():
    post_data = request.data.decode()
    corr_matrix = []
    if post_data != "":
        post_data = simplejson.loads(post_data)
        corr_matrix = CORR.list_to_corr_matrix(stock_list=post_data[0], start_time=post_data[1], end_time=post_data[2])
        corr_matrix = CORR.two_phase_hierarchical_clustering(corr_matrix)
        if corr_matrix is not False:
            corr_matrix = {
                'columns': corr_matrix[0],
                'corr': corr_matrix[1],
            }
            # with open('../client/src/components/matrix.json', 'w+') as file:
            #     simplejson.dump(corr_matrix, file)
    return json_dumps(corr_matrix)


@app.route('/get_stock_return', methods=['POST'])
def get_stock_return():
    post_data = request.data.decode()
    response = {}
    if post_data != "":
        post_data = simplejson.loads(post_data)
        response = CORR.get_stock_return(stock_list=post_data[0], start_time=post_data[1], end_time=post_data[2])
        # with open(f'../client/src/components/stock_return.json', 'w+') as file:
        #     simplejson.dump(response, file)
    return json_dumps(response)


'''
Prism View
'''


@app.route('/get_corr_tri_market', methods=['POST'])
def get_corr_tri_market():
    post_data = request.data.decode()
    response = {}
    if post_data != "":
        post_data = simplejson.loads(post_data)
        pinus = CORR.rolling_corr_market(
            query_code=post_data[0],
            start_date=post_data[1],
            end_date=post_data[2]
        )
        response = {
            'name': 'SSE Composite Index',
            'date': pinus.columns.to_list(),
            'window': pinus.index.to_list(),
            'corr': [
                i
                for num, row in pinus.iterrows()
                for i in row.fillna(2).to_list()[-(len(pinus) + 2 - num):]
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
            start_date=post_data[1],
            end_date=post_data[2]
        )
        response = {
            'name': sector_info['name'],
            'date': pinus.columns.to_list(),
            'window': pinus.index.to_list(),
            'corr': [
                i
                for num, row in pinus.iterrows()
                for i in row.fillna(2).to_list()[-(len(pinus) + 2 - num):]
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
            start_date=post_data[2],
            end_date=post_data[3]
        )
        response = {
            'name': f'{post_data[0]} against {post_data[1]}',
            'date': pinus.columns.to_list(),
            'window': pinus.index.to_list(),
            'corr': [
                i
                for num, row in pinus.iterrows()
                for i in row.fillna(2).to_list()[-(len(pinus) + 2 - num):]
            ]
        }
        # with open(f'../client/src/components/pinus_stock_{post_data[0]}.json', 'w+') as file:
        #     simplejson.dump(response, file)
    return json_dumps(response)


@app.route('/get_stock_daily', methods=['POST'])
def get_stock_daily():
    post_data = request.data.decode()
    response = {}
    if post_data != "":
        post_data = simplejson.loads(post_data)
        response = CORR.query_stock_daily(post_data[0], post_data[1], post_data[2])
        # with open(f'../client/src/components/pinus_stock_{post_data[0]}.json', 'w+') as file:
        #     simplejson.dump(response, file)
    return json_dumps(response)


@app.route('/get_stock_index_daily', methods=['POST'])
def get_stock_index_daily():
    post_data = request.data.decode()
    response = {}
    if post_data != "":
        post_data = simplejson.loads(post_data)
        response = CORR.query_stock_index_daily(post_data[0], post_data[1], post_data[2], post_data[3])
        # with open(f'../client/src/components/pinus_stock_{post_data[0]}.json', 'w+') as file:
        #     simplejson.dump(response, file)
    return json_dumps(response)


'''
Control Panel
'''


@app.route('/get_knowledge_graph_count', methods=['POST'])
def get_knowledge_graph_count():
    post_data = request.data.decode()
    response = {}
    if post_data != "":
        post_data = simplejson.loads(post_data)
        response = CORR.query_stock_knowledge_graph_count(*post_data)
    return json_dumps(response)


@app.route('/get_knowledge_graph_links', methods=['POST'])
def get_knowledge_graph_links():
    post_data = request.data.decode()
    response = {}
    if post_data != "":
        post_data = simplejson.loads(post_data)
        response = CORR.query_stock_knowledge_graph_links(*post_data)
    return json_dumps(response)


@app.route('/get_knowledge_graph_members', methods=['POST'])
def get_knowledge_graph_members():
    post_data = request.data.decode()
    response = {}
    if post_data != "":
        post_data = simplejson.loads(post_data)
        response = CORR.query_stock_knowledge_graph_members(*post_data)
    return json_dumps(response)

