# AppApiRestV2SimilaritySchemaANNFunction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**limit** | **int** | The amount of neighbours per function ID | [optional] [default to 5]
**distance** | **float** | The distance between two neighbours | [optional] [default to 0.1]
**analysis_search_ids** | **List[Optional[int]]** | Perform a search on functions within a list of analyses | [optional] [default to []]
**collection_search_ids** | **List[Optional[int]]** | Search only within these collections | [optional] [default to []]
**search_binary_ids** | [**SearchBinaryIds**](SearchBinaryIds.md) |  | [optional] 
**search_function_ids** | [**SearchFunctionIds**](SearchFunctionIds.md) |  | [optional] 
**debug_only** | **bool** | Searches for only functions which are debug | [optional] [default to False]

## Example

```python
from revengai.models.app_api_rest_v2_similarity_schema_ann_function import AppApiRestV2SimilaritySchemaANNFunction

# TODO update the JSON string below
json = "{}"
# create an instance of AppApiRestV2SimilaritySchemaANNFunction from a JSON string
app_api_rest_v2_similarity_schema_ann_function_instance = AppApiRestV2SimilaritySchemaANNFunction.from_json(json)
# print the JSON string representation of the object
print(AppApiRestV2SimilaritySchemaANNFunction.to_json())

# convert the object into a dict
app_api_rest_v2_similarity_schema_ann_function_dict = app_api_rest_v2_similarity_schema_ann_function_instance.to_dict()
# create an instance of AppApiRestV2SimilaritySchemaANNFunction from a dict
app_api_rest_v2_similarity_schema_ann_function_from_dict = AppApiRestV2SimilaritySchemaANNFunction.from_dict(app_api_rest_v2_similarity_schema_ann_function_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


