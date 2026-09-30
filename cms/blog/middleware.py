from .models import Visitor


class VisitorTrackingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        if request.method == "GET":
            ip_address = self.get_client_ip(request)

            Visitor.objects.create(
                ip_address=ip_address,
                page=request.path
            )

        return response

    def get_client_ip(self, request):

        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")

        if forwarded:
            return forwarded.split(",")[0]

        return request.META.get("REMOTE_ADDR")