class APIResponse:

    @staticmethod
    def success(data=None, message="Success"):
        return {
            "success": True,
            "message": message,
            "data": data
        }

    @staticmethod
    def error(message="Error", data=None):
        return {
            "success": False,
            "message": message,
            "data": data
        }