import kfp
import os
import argparse
from importlib import import_module

def compile_pipeline(pipeline_file:str, pipeline_func_name:str, package_path:str):
    # load pipeline definition
    pipeline_module = import_module(pipeline_file)

    # compile pipeline func to pipeline package
    kfp.compiler.Compiler().compile(
        pipeline_func=pipeline_module.pipeline_func_name,
        package_path=package_path
        )
    
    abs_package_path = os.path.abspath(package_path)
    return abs_package_path

if __name__ == "__main__":
    # define command line arguments 
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pipeline-file', help="pipeline file where pipeline func is declared", required=True)
    parser.add_argument('-f', '--pipeline-func', help="pipeline function name", required=True)
    parser.add_argument('-o', '--output-path', help="pipeline package path", required=True)
    args = parser.parse_args()

    ret = compile_pipeline(
        pipeline_file=args.pipeline_file, 
        pipeline_func_name=args.pipeline_func,
        package_path=args.output_path,
        )
    print(ret)