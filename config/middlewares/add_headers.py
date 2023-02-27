class AddHeaders:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Host"] = "localhost"
        response["Link"] = 'https://bistime.app/api/swagger/; rel="profile"'
        return response
