# layer-builder
Simple library that supports building AWS Lambda layers as part of your AWS CDK build process.
Cross-platform (supports both Win and Mac), targeting both x86 and ARM chips, and 
based on you existing `requirements.txt`.

## Build from requirements
Using this library, you can 


```Python
from layer_builder import build_from_requirements
from constructs import Construct
from aws_cdk import Stack, aws_lambda as aws_lambda

class LayerStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        build_from_requirements(
            "../../requirements.txt",
            "./build/layer",
            max_mb=20, # Check if the size of the layer is larger than expected
            clean=True, # Delete previous install
            graviton=True, # Specify targeting ARM architecture
        )
        self.my_layer = aws_lambda.LayerVersion(
            self,
            "my-layer",
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_13],
            compatible_architectures=[aws_lambda.Architecture.ARM_64],
            code=aws_lambda.Code.from_asset("./build/layer"),
        )
```
