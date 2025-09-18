import copy
import os
import yaml
import json
import urllib.request
from gentccode.produce_case_code import ProduceCaseCode
from gentccode.filter_cp_result import produce_cp_param_by_node
from gentccode.read_swagger_rule import NoneRule
from http_content_parser.req_data import ReqData
from http_content_parser.api_parser import ApiModelParser


SOURCE_CURL = "curl"
SOURCE_POSTMAN = "postman"
SOURCE_SWAGGER = "swagger"
SOURCE_OPENAPI = "openapi"


class ProduceUseCase(object):
    def __init__(self) -> None:
        self.pcc = ProduceCaseCode()
        self.api_parser = ApiModelParser()

    def produce_case_for_postman(
        self,
        postman_file_path: str,
        yaml_file_path: str,
        use_case_file_path: str,
        append_assert_info: str,
    ):
        with open(postman_file_path, "r") as f:
            postman_dict = json.load(f)
        self.init_file(file=use_case_file_path)
        self.init_file(file=yaml_file_path)
        req_model_list = self.api_parser.get_api_model_for_postman(postman_dict)
        assert_str = self.pcc.append_custome_assert_info(append_assert_info)
        code_str = self.pcc.produce_code_for_api_model(
            req_data=req_model_list,
            append_assert_str=assert_str,
        )
        # write api info to yaml
        self.write_api_info_to_yaml_file(
            req_list=req_model_list, yaml_file=yaml_file_path
        )
        # write use case to py
        self.write_use_case_to_py_file(code_str=code_str, py_file=use_case_file_path)

    def produce_case_for_swagger2(self, swagger_json_path, yaml_file, use_case_file):
        # 读取 doc.json 文件
        with open(swagger_json_path, "r") as f:
            swagger2_dict = json.load(f)
        self.init_file(file=use_case_file)
        self.init_file(file=yaml_file)
        payload_list = self.api_parser.get_api_model_for_swagger(
            swagger2_dict, yaml_file
        )
        none_rule = NoneRule()
        code_str = self.pcc.produce_code_for_api_dict(
            append_assert_str="",
            api_info=swagger2_dict,
            sql_rule=none_rule,
        )
        # write api info to yaml
        self.write_api_info_to_yaml_file(req_list=payload_list, yaml_file=yaml_file)
        # write use case to py
        self.write_use_case_to_py_file(code_str=code_str, py_file=use_case_file)

    def produce_case_for_curl(
        self,
        curl_file: str,
        yaml_file: str,
        use_case_file: str,
        append_assert_info: str,
        curl_filter=None,
    ):
        self.init_file(file=use_case_file)
        self.init_file(file=yaml_file)
        req_model_list = self.api_parser.get_api_model_for_curl(
            curl_file=curl_file, curl_filter=curl_filter
        )
        assert_str = self.pcc.append_custome_assert_info(append_assert_info)
        code_str = self.pcc.produce_code_for_api_model(
            req_data=req_model_list,
            append_assert_str=assert_str,
        )
        # write api info to yaml
        self.write_api_info_to_yaml_file(req_list=req_model_list, yaml_file=yaml_file)
        # write use case to py
        self.write_use_case_to_py_file(code_str=code_str, py_file=use_case_file)

    def produce_case_by_param_type_for_curl(
        self,
        payload_list,
        curl_file,
        use_case_file,
        param_type,
        add_after_assert_response_str,
        add_method_name_suffix_str=False,
    ):
        self.init_file(file=use_case_file)
        # read from curl
        http_payload_list = self.api_parser.get_api_model_for_curl(curl_file=curl_file)
        # modify api's param
        new_payloads = []
        for p in payload_list:
            for payload in http_payload_list:
                temp = copy.deepcopy(payload)
                if param_type == "body":
                    temp.body = p
                elif param_type == "query":
                    temp.query_param = p
                new_payloads.append(temp)
        # generate code
        code_str = self.pcc.produce_code_for_api_model(
            req_data=new_payloads,
            add_method_name_suffix_str=add_method_name_suffix_str,
            append_assert_str=add_after_assert_response_str,
        )
        # write api info to yaml
        # self.write_api_content_to_yaml(req_list=http_payload_list, yaml_file=)
        # write use case to py
        self.write_use_case_to_py_file(code_str=code_str, py_file=use_case_file)

    def get_payload_body(self, curl_file):
        # read from curl
        http_payloads = self.api_parser.convert_curl_data_to_model(
            curl_file_path=curl_file
        )
        return [payload.body for payload in http_payloads]

    def get_query_param_from_curl(self, curl_file):
        # read from curl file
        http_payloads = self.api_parser.convert_curl_data_to_model(
            curl_file_path=curl_file
        )
        return [payload.query_param for payload in http_payloads]

    def __download_swagger_json(url):
        d = {}
        try:
            response = urllib.request.urlopen(url)
            data = response.read().decode("utf-8")
            d = json.loads(data)
        except Exception as ex:
            print(ex)
        return d

    def produce_cp_case(
        self,
        param_type: str,
        source_type: str,
        node: str,
        curl_file_path: str,
        use_case_file_path: str,
        add_after_assert_response_str: str,
    ):
        PARAM_TYPE_QUERY = "query"
        PARAM_TYPE_BODY = "body"
        if param_type == PARAM_TYPE_BODY:
            payload_params = self.get_payload_body(curl_file=curl_file_path)
            cp_param_list = produce_cp_param_by_node(node, payload_params)
        elif param_type == PARAM_TYPE_QUERY:
            payload_params = self.get_query_param_from_curl(curl_file=curl_file_path)
            cp_param_list = produce_cp_param_by_node(node, payload_params)
        else:
            print("param type is not exist")
        if source_type == SOURCE_CURL:
            node_assert_res_str = self.pcc.append_custome_assert_info(
                add_after_assert_response_str
            )
            self.produce_case_by_param_type_for_curl(
                payload_list=cp_param_list,
                param_type=param_type,
                curl_file=curl_file_path,
                use_case_file=use_case_file_path,
                add_method_name_suffix_str=True,
                add_after_assert_response_str=node_assert_res_str,
            )
        elif source_type == SOURCE_POSTMAN:
            pass
        elif source_type == SOURCE_SWAGGER:
            pass
        elif source_type == SOURCE_OPENAPI:
            pass
        else:
            print("source type is not exsit")

    def write_api_info_to_yaml_file(self, yaml_file: str, req_list: list[ReqData]):
        yaml_obj = {}
        for req_model in req_list:
            api_obj = {
                "original_url": req_model.original_url,
                "path": req_model.path,
                "query_param": req_model.query_param,
                "path_param": req_model.path_param,
                "header": req_model.header,
                "body": req_model.body,
                "method": req_model.method,
                "response": req_model.response,
            }
            yaml_obj[req_model.temp_api_label] = api_obj
        with open(yaml_file, "wt", encoding="utf-8") as f:
            yaml.dump(yaml_obj, f)

    def write_use_case_to_py_file(self, py_file: str, code_str: str):
        with open(py_file, "wt", encoding="utf-8") as f:
            f.write(code_str)

    def init_file(self, file: str):
        if os.path.exists(file):
            with open(file, "w") as f:
                f.write("")
