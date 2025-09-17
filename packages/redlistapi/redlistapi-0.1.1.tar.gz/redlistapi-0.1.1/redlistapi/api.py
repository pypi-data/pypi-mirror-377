import yaml as _yaml
import requests as _requests
import types as _types
import tomllib as _tomllib
import platform as _platform


def _user_agent():
    with open("pyproject.toml", "rb") as f:
        pyproject = _tomllib.load(f)
 
    name    = pyproject["project"]["name"]
    version = pyproject["project"]["version"]
    repo    = pyproject["project"]["urls"]["repository"]
 
    python_version = _platform.python_version()
 
    return f"{name}/{version} (+{repo}) python/{python_version}"

def _parse_openapi_yaml(yaml_url):
    response = _requests.get(yaml_url)
    response.raise_for_status()
    return _yaml.safe_load(response.content)

def _create_api_function_docstring(details):

    summary = details.get('summary', 'No summary available.')

    description = details.get('description', 'No description available.')    

    parameters = "\n".join([
        (f"    {param['name']} : {param['schema']['type']}"
         f"{' (required)' if param.get('required') else ''}"
         ) for param in details.get('parameters', [])
        ])

    response = details.get('responses', {}).get('200', {})
    response = response.get('description', 'No response description available.')

    docstring  = summary + '\n'
    docstring += '\n'
    docstring += description + '\n'
    docstring += '\n'
    docstring += 'Parameters:' + '\n'
    docstring += '    token : str (required)' + '\n'
    docstring += parameters + '\n'
    docstring += '\n'
    docstring += 'Returns:' + '\n'
    docstring += '    dict : API response.' + '\n'
    docstring += '\n'
    docstring += response + '\n'

    return docstring

def _create_api_function(method: str, url: str, details: dict, name: str) -> callable:
    """Create a Python function to call an API endpoint, parametrized."""

    required_params = [
        param['name'] for param in details.get('parameters', [])
        if param['required']
        ]
    required_params.append('token')
    
    def api_function(**kwargs):

        # Ensure required parameters are provided
        missing_params = [par for par in required_params if par not in kwargs]
        if missing_params:
            raise ValueError(
                f"Function '{api_function.__name__}'"
                f"is missing required parameters: {missing_params}"
                )
        
        # Make the appropriate request (GET, POST, etc.)
        if method == "get":
            response = _requests.get(
                url    = f'https://api.iucnredlist.org/{url.format(**kwargs)}',
                params = {par: kwargs[par] for par in kwargs if par not in url and par != 'token'},
                headers= {
                    'accept':'application/json',
                    'Authorization':kwargs['token'],
                    'User-Agent':_user_agent()
                    }
                )
        else:
            raise NotImplementedError(f"Method {method.upper()} is not implemented.")

        return response
    
    api_function.__name__ = name
    api_function.__doc__ = _create_api_function_docstring(details)

    return api_function


def _generate_module_from_openapi_url(openapi_url: str) -> _types.SimpleNamespace:
    """Generate a module-like structure where API paths map to namespaces and functions."""
    
    openapi_spec = _parse_openapi_yaml(openapi_url)

    root_module = _types.SimpleNamespace()
    
    paths = openapi_spec.get('paths', {})

    # Iterate over the paths and methods to create API functions
    for url, methods in paths.items():

        # Edit url to allow simple parsing to namespace.
        # If it is a folder endpoint like "kingdom/", edit as → "kingdom/list"
        # Replace url parameters like "{kingdom_name}" with "by_kingdom_name"
        # then split it in segments
        namespace = url
        namespace += "list" if namespace.endswith("/") else ""
        namespace = namespace.replace("/class/", "/class_/")
        namespace = namespace.replace("{", "by_").replace("}", "")
        segments = namespace.strip('/').split('/')
        
        # Start from the root and build the nested namespaces
        current_namespace = root_module
        for segment in segments[:-1]: # Skip the last segment (function level)
            # Add the namespace if it doesn't exist
            if not hasattr(current_namespace, segment):
                setattr(current_namespace, segment, _types.SimpleNamespace())
            # Move to the next namespace level
            current_namespace = getattr(current_namespace, segment)
        
        # Generate a function for the url method
        # It is assumed that the Red List API only has 'get' methods
        for method, details in methods.items():
            if method != 'get':
                raise NotImplementedError('Only get methods are supported.')
            # Generate the function and attach it to the final namespace
            function_name = segments[-1] # Fallback to the last path segment
            api_function = _create_api_function(method, url, details, function_name)
            setattr(current_namespace, function_name, api_function)
    
    return root_module


v4 = _generate_module_from_openapi_url(
    openapi_url = 'https://api.iucnredlist.org/api-docs/v4/openapi.yaml'
    ).api.v4

# Hic Svnt Dracones!