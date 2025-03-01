from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    """Butun saytga kirish uchun login talab qiluvchi middleware"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Login bo'lishi shart bo'lmagan sahifalar (faqat login sahifasi, ro‘yxatdan o‘tish sahifasi va static fayllar)
        allowed_paths = [settings.LOGIN_URL, '/login/']

        # Agar foydalanuvchi login qilmagan bo‘lsa va ruxsat berilmagan sahifaga kirmoqchi bo‘lsa
        if not request.user.is_authenticated and not any(request.path.startswith(path) for path in allowed_paths):
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)
