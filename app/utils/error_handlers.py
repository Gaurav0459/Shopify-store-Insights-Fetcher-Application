from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

# Custom error messages that reflect my personality
FRIENDLY_ERROR_MESSAGES = {
    400: "Hmm, that doesn't look right. Could you check your request and try again?",
    401: "You need to be authenticated to access this resource.",
    403: "Sorry, you don't have permission to access this resource.",
    404: "Oops! I couldn't find what you're looking for. Are you sure that URL exists?",
    405: "That method isn't allowed here. Try a different approach.",
    408: "The request timed out. Shopify stores can be slow sometimes, maybe try again?",
    429: "Whoa there! Too many requests at once. Please slow down a bit.",
    500: "Something went wrong on our end. I've logged the error and will look into it.",
    503: "Our service is temporarily unavailable. Please try again in a few minutes."
}

# This was a pain point I encountered during development
SHOPIFY_SPECIFIC_ERRORS = {
    "products_not_found": "Couldn't find any products. This might not be a Shopify store, or it could be using a custom storefront API.",
    "access_denied": "The store seems to be blocking our requests. Some Shopify stores have stricter security settings.",
    "rate_limited": "We've been rate limited by the store. This happens when we make too many requests too quickly.",
    "invalid_store": "This doesn't appear to be a valid Shopify store. Double-check the URL and try again."
}


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with friendly messages"""
    # I found that most validation errors were related to the URL format
    error_msg = "There's an issue with your request data. "
    
    # Extract specific error details
    for error in exc.errors():
        if error["loc"][0] == "body" and len(error["loc"]) > 2 and error["loc"][1] == "website_url":
            error_msg += "The website URL doesn't seem to be valid. Make sure it's a complete URL (e.g., https://example.com)."
            break
    else:
        error_msg += "Please check your input and try again."
    
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": error_msg}
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with friendly messages"""
    status_code = exc.status_code
    error_msg = FRIENDLY_ERROR_MESSAGES.get(status_code, str(exc.detail))
    
    # Add more context for specific errors
    if status_code == 404 and "shopify" in str(request.url).lower():
        error_msg += " If you're looking for a Shopify store, make sure the URL is correct."
    
    logger.error(f"HTTP error {status_code}: {str(exc.detail)}")
    return JSONResponse(
        status_code=status_code,
        content={"detail": error_msg}
    )


def setup_error_handlers(app):
    """Set up custom error handlers for the application"""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)