import traceback


class SiteErrorLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        try:
            from .models import SiteErrorLog

            user = getattr(request, "user", None)
            user_label = ""
            if user and user.is_authenticated:
                user_label = getattr(user, "username", "") or str(user)

            forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
            ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else request.META.get("REMOTE_ADDR", "")

            SiteErrorLog.objects.create(
                path=request.get_full_path()[:500],
                method=request.method,
                status_code=500,
                exception_type=exception.__class__.__name__,
                message=str(exception),
                traceback="".join(traceback.format_exception(type(exception), exception, exception.__traceback__)),
                user_label=user_label,
                ip_address=ip_address,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
        except Exception:
            pass

        return None
