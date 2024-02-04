

class BaseServerHttpException(Exception):
    """Base Exception raised for HTTP errors.

    Reference: https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers

    Attributes:
        message     : Message of the error.

    """

    pass


class BadRequestHttpException(BaseServerHttpException):
    # 400: General bad request exception on unable to handle the request.
    # Message: Bad Request: Please make modifications to the request before pinging the server again.

    def __init__(self):
        self.status_code = 400
        self.message = 'Bad Request: Please make modifications to the request before pinging the server again.'


class UnauthorizedHttpException(BaseServerHttpException):
    # 403: Unauthorized request
    # Message: Invalid or expired authorization token.

    def __init__(self):
        self.status_code = 403
        self.message = 'Invalid or expired authorization token.'


class ServerLimitHttpException(BaseServerHttpException):
    # 434: Server has reached its limit to serve requests.
    # Message: We are unable to serve your request at the moment. Please try again later.

    def __init__(self):
        self.status_code = 433
        self.message = 'We are unable to serve your request at the moment. Please try again later.'
