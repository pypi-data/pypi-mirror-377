# FunctionBatchAnn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **object** |  | [optional] 
**settings** | **object** |  | 
**function_matches** | **object** |  | 

## Example

```python
from revengai.models.function_batch_ann import FunctionBatchAnn

# TODO update the JSON string below
json = "{}"
# create an instance of FunctionBatchAnn from a JSON string
function_batch_ann_instance = FunctionBatchAnn.from_json(json)
# print the JSON string representation of the object
print(FunctionBatchAnn.to_json())

# convert the object into a dict
function_batch_ann_dict = function_batch_ann_instance.to_dict()
# create an instance of FunctionBatchAnn from a dict
function_batch_ann_from_dict = FunctionBatchAnn.from_dict(function_batch_ann_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


