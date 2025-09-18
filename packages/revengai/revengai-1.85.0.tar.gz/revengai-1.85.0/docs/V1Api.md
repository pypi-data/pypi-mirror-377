# revengai.V1Api

All URIs are relative to *https://api.reveng.ai*

Method | HTTP request | Description
------------- | ------------- | -------------
[**batch_symbol_ann**](V1Api.md#batch_symbol_ann) | **POST** /v1/ann/symbol/batch | Batch Symbol ANN using function IDs


# **batch_symbol_ann**
> FunctionBatchAnn batch_symbol_ann(app_api_rest_v1_ann_schema_ann_function, authorization=authorization)

Batch Symbol ANN using function IDs

Takes in an input of functions ID's and settings and finds the nearest functions for each function that's within the database

### Example

* Api Key Authentication (APIKey):

```python
import revengai
from revengai.models.app_api_rest_v1_ann_schema_ann_function import AppApiRestV1AnnSchemaANNFunction
from revengai.models.function_batch_ann import FunctionBatchAnn
from revengai.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.reveng.ai
# See configuration.py for a list of all supported configuration parameters.
configuration = revengai.Configuration(
    host = "https://api.reveng.ai"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKey
configuration.api_key['APIKey'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKey'] = 'Bearer'

# Enter a context with an instance of the API client
with revengai.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = revengai.V1Api(api_client)
    app_api_rest_v1_ann_schema_ann_function = revengai.AppApiRestV1AnnSchemaANNFunction() # AppApiRestV1AnnSchemaANNFunction | 
    authorization = 'authorization_example' # str | API Key bearer token (optional)

    try:
        # Batch Symbol ANN using function IDs
        api_response = api_instance.batch_symbol_ann(app_api_rest_v1_ann_schema_ann_function, authorization=authorization)
        print("The response of V1Api->batch_symbol_ann:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling V1Api->batch_symbol_ann: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_api_rest_v1_ann_schema_ann_function** | [**AppApiRestV1AnnSchemaANNFunction**](AppApiRestV1AnnSchemaANNFunction.md)|  | 
 **authorization** | **str**| API Key bearer token | [optional] 

### Return type

[**FunctionBatchAnn**](FunctionBatchAnn.md)

### Authorization

[APIKey](../README.md#APIKey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Invalid request parameters |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

