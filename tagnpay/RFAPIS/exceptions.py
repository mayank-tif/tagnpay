from rest_framework.views import exception_handler
from rest_framework import serializers  # Add this import

def custom_exception_handler(exc, context):
    # Call the default exception handler to get the standard error response
    response = exception_handler(exc, context)

    if response is not None:
        # Check if the exception is of type ValidationError
        if isinstance(exc, serializers.ValidationError):
            # Flatten the list into a single string if the error contains an array
            if isinstance(response.data.get('error'), list):
                response.data['error'] = str(response.data.get('error')[0])  # Get the first error message

    return response
