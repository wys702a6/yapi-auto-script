# -*- coding:utf-8 -*-

from interface.globalconfig import global_config
from utils.util import came_case_to_lower_case, Bunch
import json
import argparse


def _template_method(method, *args, **kwargs):
    if args:
        return """
        def {method}{params}:
            pass
            """.format(method=came_case_to_lower_case(method), params=args)

    if kwargs:
        keys = []
        for k, v in kwargs.items():
            keys.append(came_case_to_lower_case(k) + "='" + str(v) + "'")
        s = ",".join(keys)

        return """
        def {method}({params}):
            pass
            """.format(method=came_case_to_lower_case(method), params=s)


def get_project_id():
    """
    获取项目基本信息，主要拿到project_id
    :return:
    """
    resp = global_config.get_http().get('/api/project/get')

    resp = Bunch(resp)

    return resp.data._id


def get_total_apis(project_id, page=1, limit=1000):
    """
    根据项目id获取该项目的所有接口
    :param project_id: 项目id
    :param page: 分页
    :param limit: 每页条数
    :return:
    """

    apis= []

    header = {
        'Content-Type': 'application/json'
    }

    global_config.get_http().header = header

    resp= global_config.get_http().get('/api/interface/list', project_id=project_id, page=page, limit=limit)

    for _, data in enumerate(resp['data']['list']):
        apis.append(data['_id'])

    return apis


def get_singal_api(func, project_id):
    """
    获取详细接口数据
    :param func:
    :param project_id:
    :return:
    """
    apis = func(project_id)

    for api in apis:
        resp = global_config.get_http().get('/api/interface/get', id=api)

        resp = Bunch(resp)  # 详细接口数据

        path = resp.data.path  # 请求路径
        http_method = resp.data.method  # 请求方法

        if "rpc" not in path:
            method = path.split('/')[-1]

            raw_req_body = {}

            if "GET" == http_method:
                query_strings = {query['name']:query['example'] for query in resp.data.req_query}

                raw_req_body.update(query_strings)

            else:
                if 'req_body_other' in resp.data:   # 请求参数写的是json格式
                    req_body_temp = resp.data.req_body_other.replace('\n', '').replace(' ', '')  # 请求body(过滤掉所有\n,空格)

                    req_body_dict = json.loads(req_body_temp)

                elif 'req_body_form' in resp.data:  # 请求参数写在form里
                    req_body_dict = {req_body['name']:req_body['example'] for req_body in resp.data.req_body_form}

                raw_req_body.update(req_body_dict)

            req_body = _template_method(method, **raw_req_body)

        else:
            if 'req_body_other' in resp.data:
                req_body_temp = resp.data.req_body_other.replace('\n', '').replace(' ', '')  # 请求body(过滤掉所有\n,空格)

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



if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--project_id', '-p', type=int, required=True, help="")
    #
    # args = parser.parse_args()
    #
    # if args.project_id is not None:
    #     project_id = args.project_id

    project_id = get_project_id()

    res = get_singal_api(get_total_apis, project_id=project_id)

    while True:
        try:
            generate_txt_date(res.__next__())
        except StopIteration:
            break
