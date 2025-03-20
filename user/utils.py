from django.shortcuts import redirect

def get_redirect_url(user):
    """Foydalanuvchini uning roligiga mos sahifaga yo‘naltiradi"""
    role_redirects = {
        "administrator": "dashboard",
        "moderator": "m_user_list",
        "user1": "user1",
        "user2": "user2",
        "user3": "user3",
    }
    if user.is_superuser:
        return "/dashboard/"  # Django admin panel
    return role_redirects.get(user.role, "/")  # Default sahifa
