import copy
from graphql_relay import from_global_id
from django.conf import settings
from graphql import GraphQLResolveInfo
import json
from django.utils.deprecation import MiddlewareMixin

import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('general')

# this is a decorator function to provide a generic try-except error handling mechanism
# & it logs the full path to failed function in the case of a failure
# the default return value in any failure case is 'None', this value can be changed easily
# via the decorator argument
# credit: https://stackoverflow.com/questions/15572288/general-decorator-to-wrap-try-except-in-python
def handle_error(return_if_error=None, log_error=True, *args, **kwargs):
    def decorate(func):
        def applicator(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # log where the exception is coming from
                if log_error:
                    print(f"Error in {func.__qualname__}:", e)
                return return_if_error

        return applicator

    return decorate

def handle_graphql_error(*args, **kwargs):
    def decorate(func):
        def applicator(*args, **kwargs):
            graphql_resolve_info = [arg for arg in args if isinstance(arg, GraphQLResolveInfo)][0]
            field_name = graphql_resolve_info.field_name
            try:
                logger.info(f"Ran {graphql_resolve_info.parent_type}: {field_name}")
                return func(*args, **kwargs)
            except Exception as e:
                # log where the exception is coming from
                logger.error(f"Error in {func.__qualname__} at {graphql_resolve_info.parent_type} {field_name}: {e}")
                raise e

        return applicator

    return decorate

# helper function to decode a Relay global id back to django model object id
# with error handling
@handle_error(log_error=False)
def decode_global_id(id=None):
    return from_global_id(id)[1]


# for accessing deep nested json data in a safer way
def safe_get(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except (KeyError, IndexError):
            return None
        except:
            return None
    return dct

# a function that helps to remove all key-value pairs in the given dict using the given
# key names
def remove_from_dict(_dict, *keys):
    new_dict = copy.deepcopy(_dict)
    for key in keys:
        if key in new_dict:
            del new_dict[key]
    return new_dict


def remove_new_lines(text):
    return text.replace('\n', '').replace('\r', '')

def find_key(obj, key_value):
    if isinstance(obj, dict):
        if key_value in obj:
            return obj[key_value]
        for key, value in obj.items():
            result = find_key(value, key_value)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_key(item, key_value)
            if result is not None:
                return result
    return None

class GraphQLLoggingMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if hasattr(request, 'body') and request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                
                logger.info(f"Request Body: {remove_new_lines(safe_get(body, 'query'))}")
            except (ValueError, KeyError) as exception:
                logger.error(f"Error processing GraphQL request: {exception}")
        return None

    def process_response(self, request, response):
        if hasattr(response, 'content'):
            byte_result = response.content
            decoded_result = byte_result.decode('utf-8')
            data = json.loads(decoded_result)

            logger.info(f"GraphQL Data: {data}")
            errors_data = find_key(data, "errors")
            errors = {'errors': errors_data}
    
            if errors_data:
                logger.error(f"GraphQL Error: {errors}")
        return response