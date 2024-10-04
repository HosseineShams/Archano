from django.utils.deprecation import MiddlewareMixin
import threading

_thread_local = threading.local()

class CurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _thread_local.current_user = request.user

    @classmethod
    def get_current_user(cls):
        return getattr(_thread_local, 'current_user', None)
