import kfp
import kfp.dsl as dsl
from kfp.components import create_component_from_func


def step_func(a:int, b:int):
    print('test pipline')
    print(a + b)

step_func_op = create_component_from_func(step_func)

@dsl.pipeline(
  name="test_pipeline_4",
  description="uploaded via kfp client",
)
def test(
  key1: int,
  key2: int
):
  # STEP1: Taking snapshot before data preprocessing 
  step1 = step_func_op(a=key1, b=key2)

kfp.compiler.Compiler().compile(
    pipeline_func=test,
    package_path='pipeline.yaml')