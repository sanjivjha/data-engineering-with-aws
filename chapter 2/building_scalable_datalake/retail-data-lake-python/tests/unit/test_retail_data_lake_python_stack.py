import aws_cdk as core
import aws_cdk.assertions as assertions

from retail_data_lake_python.retail_data_lake_python_stack import RetailDataLakePythonStack

# example tests. To run these tests, uncomment this file along with the example
# resource in retail_data_lake_python/retail_data_lake_python_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RetailDataLakePythonStack(app, "retail-data-lake-python")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
