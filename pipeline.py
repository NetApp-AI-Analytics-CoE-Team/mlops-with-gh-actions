import kfp
import kfp.dsl as dsl
from kfp.components import create_component_from_func


def step_func():
    print('test pipline')

step_func_op = create_component_from_func(step_func)

@dsl.pipeline(
  name="test pipeline",
  description="uploaded via kfp client",
)
def test():
  # STEP1: Taking snapshot before data preprocessing 
  step1 = step_func_op()

kfp.compiler.Compiler().compile(
    pipeline_func=test,
    package_path='pipeline.yaml')