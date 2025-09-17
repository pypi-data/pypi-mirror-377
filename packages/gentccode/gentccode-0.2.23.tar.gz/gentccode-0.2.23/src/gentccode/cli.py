import os
import click
from gentccode.check_version import (
    check_package_version,
    get_current_version,
    update_package,
)
from gentccode.convert_to_jmx import convert_payloads_of_curl_to_jmx_file
from gentccode.convert_to_locust import product_locust_code
from gentccode.produce_use_case import ProduceUseCase


ptc = ProduceUseCase()
# 生成的接口信息会保存到这个文件中
API_YAML_FILE_PATH = "api.yaml"
# 生成的接口代码会保存到这个文件中
CASE_FILE_PATH = "test_cases.py"

PACKAGE_NAME = "gentccode"


@click.group()
def cli1():
    pass


# cli1的回调函数
@cli1.result_callback()
def check_update(curl):
    check_package_version(PACKAGE_NAME)


@click.command(help="generate test code based on http's payload")
@click.option("-n", "--node", required=True, help="json node, like: '.','a.'")
@click.option("-p", "--paramtype", required=True, help="query,body")
@click.option(
    "-a", "--assertresponse", required=True, help="like: code=0, res.code='0'"
)
@click.argument("filename", type=click.Path(exists=True))
def cp(node, filename, paramtype, assertresponse):
    ptc.produce_cp_case(
        node=node,
        param_type=paramtype,
        source_type="curl",
        curl_file_path=filename,
        add_after_assert_response_str=assertresponse,
        use_case_file_path=CASE_FILE_PATH,
    )


@click.command(help="generate test code based on curl file")
@click.argument("filename", type=click.Path(exists=True))
@click.option(
    "-a", "--assertresponse", required=True, help="like: code=0, res.code='0'"
)
def curl(filename, assertresponse):
    ptc.produce_case_for_curl(
        curl_file=filename,
        yaml_file=API_YAML_FILE_PATH,
        use_case_file=CASE_FILE_PATH,
        append_assert_info=assertresponse,
    )


@click.command(help="generate test code based on swagger json file")
@click.argument("filename", type=click.Path(exists=True))
def swagger2(filename):
    ptc.produce_case_for_swagger2(filename, API_YAML_FILE_PATH, CASE_FILE_PATH)


@click.command(help="generate locust script based on curl file")
@click.argument("filename", type=click.Path(exists=True))
def locust(filename):
    product_locust_code(curl_file_path=filename)


@click.command(help="generate jmeter script based on curl file")
@click.option(
    "-ja",
    "--jsonassert",
    required=True,
    help="json node, like: 'code','data.code','a.b.c'",
)
@click.option(
    "-r",
    "--rate",
    required=True,
    help="qps/s, like: 1, 10",
)
@click.option(
    "-t",
    "--time",
    required=True,
    help="total stress time: 1min, like: 1, 10",
)
@click.argument("filename", type=click.Path(exists=True))
def jmeter(filename, jsonassert, rate, time):  # cli方法中的参数必须为小写
    convert_payloads_of_curl_to_jmx_file(
        curl_file_path=filename, json_path_assert=jsonassert, rate=rate, total_time=time
    )


@click.command()
def version():
    current_version = get_current_version(package_name=PACKAGE_NAME)
    click.echo(f"{PACKAGE_NAME}: v{current_version}")


@click.command(help="upgrade gtc to newest version")
def update():
    update_package(package_name=PACKAGE_NAME)


@click.command(help="generate test code based on postman file")
@click.argument("filename", type=click.Path(exists=True))
@click.option(
    "-a", "--assertresponse", required=True, help="like: code=0, res.code='0'"
)
def postman(filename, assertresponse):
    ptc.produce_case_for_postman(
        postman_file_path=filename,
        yaml_file_path=API_YAML_FILE_PATH,
        use_case_file_path=CASE_FILE_PATH,
        append_assert_info=assertresponse,
    )


def main():
    # clear api yaml content.
    if os.path.exists(API_YAML_FILE_PATH):
        with open(API_YAML_FILE_PATH, "w") as f:
            f.write("")
    cli1.add_command(curl)
    cli1.add_command(postman)
    cli1.add_command(swagger2)
    cli1.add_command(locust)
    cli1.add_command(cp)
    cli1.add_command(jmeter)
    cli1.add_command(version)
    cli1.add_command(update)
    cli1()
