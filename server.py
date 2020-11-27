# -*- coding:utf-8 -*-

from interface.globalconfig import global_config
from utils.util import came_case_to_lower_case, Bunch
import json
import argparse
import re
from flask import Flask, request, jsonify


app = Flask(__name__)


# 登录
def do_login(username, password):
    global_config.get_http().login('/api/user/login_by_ldap', user=username, password=password)


# 获取项目组
def get_project_groups():
    resp = global_config.get_http().get('/api/group/list', flag=False)
    resp = Bunch(resp)

    return {d['group_name']: d['_id'] for d in resp.data}


# 根据项目组id获取项目
def get_project_by_signal_group(group_id, page=1, limit=100):
    resp = global_config.get_http().get('/api/project/list', group_id=group_id, page=page, limit=limit)
    resp = Bunch(resp)

    return {d['name']: d['_id'] for d in resp.data.list}


# 根据group_id获取项目token，并获取项目的分类rpc
def get_project_token_and_catalog(project_id):
    resp = global_config.get_http().get('/api/project/token', project_id=project_id)
    resp = Bunch(resp)

    project_token = resp.data

    resp = global_config.get_http().get('/api/interface/getCatMenu', True, False, project_id=project_id, token=project_token)
    resp = Bunch(resp)

    return {d['name']: d['_id'] for d in resp.data}


@app.route('/get_project_token/<project_id>', methods=['GET'])
def get_project_token(project_id):
    result = get_project_token_and_catalog(project_id)

    return jsonify(result), 200


# 登录，获取项目组
@app.route('/login_by_ldap', methods=['POST'])
def login_by_ldap():
    email = request.form['user']
    password = request.form['password']

    do_login(email, password)

    result = get_project_groups()

    return jsonify(result), 200


# 获取项目组下的某个项目
@app.route('/get_groups/<group_id>', methods=['GET'])
def get_groups(group_id):
    result = get_project_by_signal_group(group_id)

    return jsonify(result), 200


@app.route('/encapsulation_by_catalog/<project_id>/<catalog_id>', methods=['GET'])
def generate_rpc_encapsulation_by_catalog(project_id, catalog_id):

    res = get_singal_api(get_total_apis, project_id=project_id, catalog_id=catalog_id)

    while True:
        try:
            generate_txt_date(res.__next__())
        except StopIteration:
            break

    return 'OK', 200


def _template_method(method, *args, **kwargs):
    if args:
        return """
        @rpc_method(low_case_to_camelcase)
        def {method}{params}:
            pass
            """.format(method=came_case_to_lower_case(method), params=args)

    if kwargs:
        keys = []
        for k, v in kwargs.items():
            keys.append(came_case_to_lower_case(k) + "='" + str(v) + "'")
        s = ",".join(keys)

        return """
        @rpc_pack_params(low_case_to_camelcase, low_case_to_camelcase)
        def {method}({params}, **kwargs):
            pass
            """.format(method=came_case_to_lower_case(method), params=s)

# def _temlate_method_api(http_method, method, path=None, query_strings: dict={}, **kwargs):
#
#     if http_method == 'GET':
#         if query_strings:
#             params = query_strings.keys()
#             s = ",".join(params)
#             return """
#             def {method}({params}):
#                 return self._call_api("{path}".format({params})
#             """.format(method=method, params=s, path=path+"?"+"&".join("{}={}".format(*query) for query in query_strings.items()))
#
#         return """
#         def {method}():
#             return
#             """.format(method=method)
#     else:
#         if query_strings:
#             params = query_strings.keys()
#             s = ",".join(params)
#
#             return """
#             def {method}({params}):
#                 {payload}
#                 return self._call_api("{path}".format({params}), req_kwargs=dict(json={payload}))
#             """.format(method=method, params=s, path=path+"?"+"&".join("{}={}".format(*query) for query in query_strings.items()),payload=kwargs)


# def get_project_id():
#     """
#     获取项目基本信息，主要拿到project_id
#     :return:
#     """
#     resp = global_config.get_http().get('/api/project/get')
#
#     resp = Bunch(resp)
#
#     return resp.data._id
#
#
def get_total_apis(project_id, catalog_id, page=1, limit=100):
    """
    根据项目id获取该项目的所有接口
    :param project_id: 项目id
    :param catalog_id: 项目下的某个分组
    :param page: 分页
    :param limit: 每页条数
    :return:
    """
    resp = global_config.get_http().get('/api/project/token', project_id=project_id)
    resp = Bunch(resp)

    project_token = resp.data

    apis = []

    resp = global_config.get_http().get('/api/interface/list_cat', True, False, catid=catalog_id, token=project_token, page=page, limit=limit)

    for _, data in enumerate(resp['data']['list']):
        apis.append(data['_id'])

    return apis, project_token


def get_singal_api(func, project_id, catalog_id):
    """
    获取详细接口数据
    :param func:
    :param project_id:
    :param catalog_id
    :return:
    """
    apis, token = func(project_id, catalog_id)

    for api in apis:
        resp = global_config.get_http().get('/api/interface/get', cookie_need_flag=False, id=api, token=token)

        resp = Bunch(resp)  # 详细接口数据

        path = resp.data.path  # 请求路径
        http_method = resp.data.method  # 请求方法

        if "rpc" not in path:
            method = path.split('/')[-1]

            raw_req_body = {}

            if "GET" == http_method:
                query_strings = {query['name']: query['example'] for query in resp.data.req_query}

                raw_req_body.update(query_strings)

            else:
                if 'req_body_other' in resp.data:   # 请求参数写的是json格式
                    # req_body_other = re.sub(r'//.*', '', resp.data.req_body_other)  # 如果有注释先过滤掉
                    # req_body_temp = req_body_other.replace('\n', '').replace(' ', '')  # 请求body(过滤掉所有\n,空格)
                    req_body_temp = re.sub(r'(//.*)|(\s)', '', resp.data.req_body_other)

                    req_body_dict = json.loads(req_body_temp)

                elif 'req_body_form' in resp.data:  # 请求参数写在form里
                    req_body_dict = {req_body['name']: req_body['example'] for req_body in resp.data.req_body_form}

                raw_req_body.update(req_body_dict)

            req_body = _template_method(method, **raw_req_body)

        else:
            if 'req_body_other' in resp.data:
                # req_body_other = re.sub(r'//.*', '', resp.data.req_body_other)
                # req_body_temp = req_body_other.replace('\n', '').replace(' ', '')
                req_body_temp = re.sub(r'(//.*)|(\s)', '', resp.data.req_body_other)

                try:
                    req_body_dict = json.loads(req_body_temp)
                    method = req_body_dict['method']

                    if isinstance(req_body_dict['params'][0], dict):

                        rpc_params = req_body_dict['params'][0]
                        req_body = _template_method(method, **rpc_params)
                    else:
                        rpc_params = req_body_dict['params']
                        req_body = _template_method(method, *rpc_params)
                except:
                    method, req_body = None, None

        # if resp.data.title.isalpha():
        #     rpc_method = came_case_to_lower_case(resp.data.title)
        # else:
        #     rpc_method = None
        yield req_body


def generate_txt_date(param):
    with open('data.txt', 'a+', encoding='utf-8') as f:
        f.writelines(param)
