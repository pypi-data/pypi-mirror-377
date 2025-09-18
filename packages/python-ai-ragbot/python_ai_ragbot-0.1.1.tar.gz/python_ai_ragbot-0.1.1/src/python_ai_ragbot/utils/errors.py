class AppError(Exception):
    def __init__(self, code, message, status=400, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details

def error_to_http_payload(err):
    if isinstance(err, AppError):
        return {
            "status": err.status,
            "body": {
                "success": False,
                "error": {
                    "code": err.code,
                    "message": err.message,
                    "details": err.details,
                },
            },
            "headers": {"Content-Type": "application/json"},
        }
    return {
        "status": 500,
        "body": {
            "success": False,
            "error": {"code": "UNEXPECTED_ERROR", "message": "An unexpected error occurred."},
        },
        "headers": {"Content-Type": "application/json"},
    }
