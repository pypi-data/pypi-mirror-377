# AppApiRestV1AnnSchemaANNFunction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**result_per_function** | **int** |  | [optional] 
**distance** | **float** |  | [optional] 
**function_id_list** | **List[Optional[int]]** | List of function ids to compare | 
**speculative_function_ids** | **List[object]** |  | [optional] 
**collection** | **List[Optional[str]]** | Perform a search on functions within a list of collections | [optional] [default to []]
**collection_search_list** | **List[Optional[int]]** | Perform a search on functions within a list of collections | [optional] [default to []]
**debug_mode** | **bool** |  | [optional] 
**debug_types** | **List[str]** | If limiting results to functions with debug names, which type of debug names to include? | [optional] [default to [SYSTEM]]
**binaries_search_list** | **List[Optional[int]]** | Perform a search on functions within a list of analyses | [optional] [default to []]

## Example

```python
from revengai.models.app_api_rest_v1_ann_schema_ann_function import AppApiRestV1AnnSchemaANNFunction

# TODO update the JSON string below
json = "{}"
# create an instance of AppApiRestV1AnnSchemaANNFunction from a JSON string
app_api_rest_v1_ann_schema_ann_function_instance = AppApiRestV1AnnSchemaANNFunction.from_json(json)
# print the JSON string representation of the object
print(AppApiRestV1AnnSchemaANNFunction.to_json())

# convert the object into a dict
app_api_rest_v1_ann_schema_ann_function_dict = app_api_rest_v1_ann_schema_ann_function_instance.to_dict()
# create an instance of AppApiRestV1AnnSchemaANNFunction from a dict
app_api_rest_v1_ann_schema_ann_function_from_dict = AppApiRestV1AnnSchemaANNFunction.from_dict(app_api_rest_v1_ann_schema_ann_function_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


