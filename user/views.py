from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .models import User, Branch
from .forms import UserForm, UserRegistrationForm
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .utils import get_redirect_url
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.db.models import Q


@csrf_exempt
def sayt(request):
    return render(request, 'users/user3.html')


@login_required
@csrf_exempt
def user1(request):
    return render(request, 'users/user1.html')


@login_required
@csrf_exempt
def user2(reqest):
    return render(reqest, 'users/user2.html')


@csrf_exempt
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'bosh sahifa/Bosh_sahifa.html', {'user': request.user})


def register(request):
    # Agar foydalanuvchi allaqachon login qilgan bo‘lsa, bosh sahifaga yo‘naltirish
    if request.user.is_authenticated:
        messages.info(request, 'Siz allaqachon tizimga kirdingiz!')
        return redirect('login')  # 'home' nomli URL bo‘lishi kerak

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ro‘yxatdan o‘tdingiz! Admin tasdiqlashini kuting.')
            return redirect('login')
        else:
            # Xatolarni templatega qoldiramiz, lekin umumiy xabar qo‘shamiz
            messages.error(request, 'Ro‘yxatdan o‘tishda xatolik yuz berdi.')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


# Login funksiyasi
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        passport_number = request.POST.get('passport_number')
        password = request.POST.get('password')

        # Foydalanuvchini autentifikatsiya qilish
        user = authenticate(request, passport_number=passport_number, password=password)

        if user is not None:
            # Foydalanuvchi holatini tekshirish
            if user.user_status == 'active':
                login(request, user)  # Foydalanuvchi tizimga kiradi
                # Yangi redirect funksiyasidan foydalanish
                redirect_url = get_redirect_url(user)
                return redirect(redirect_url)
            elif user.user_status == 'block':
                messages.error(request, 'Sizga tizimga kirish taqiqlangan!')
            elif user.user_status == 'waiting':
                messages.warning(request, 'Hisobingiz hali tasdiqlanmagan. Admin tasdiqlashini kuting.')
        else:
            messages.error(request, 'Noto‘g‘ri passport raqami yoki parol!')
        return redirect('login')
    return render(request, 'login.html')


# Logout funksiyasi
def user_logout(request):
    logout(request)  # Foydalanuvchini tizimdan chiqarish
    messages.success(request, 'Siz tizimdan muvaffaqiyatli chiqdingiz!')
    return redirect('login')


@csrf_exempt
def user_list(request):
    users = User.objects.all()
    return render(request, 'admin/user_list.html', {'users': users})


@login_required
@csrf_exempt
def m_user_list(request):
    current_user = request.user

    # Admin barcha userlarni ko‘radi, moderator faqat o‘z filialidagilarni
    users = User.objects.filter(branch=current_user.branch) if current_user.role == 'moderator' else User.objects.all()

    form = UserForm(user=current_user)

    context = {
        'users': users,
        'form': form
    }
    return render(request, 'moderator/m_user_list.html', context)


@login_required
def admin_list(request):
    """Administratorlar ro‘yxatini ko‘rsatish uchun View"""
    if not request.user.is_superuser:
        return render(request, 'xatolik/403.html', status=403)

    limit = request.GET.get('limit', 10)
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '').strip()

    # Limit va page ni xavfsiz tarzda int ga aylantirish
    limit = min(max(int(limit), 1), 50) if str(limit).isdigit() else 10
    page = max(int(page), 1) if str(page).isdigit() else 1

    # Administratorlarni olish va qidiruv filtri
    users = User.objects.filter(role='administrator').order_by('-created_at')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(passport_number__icontains=search) |
            Q(role__icontains=search) |
            Q(user_status__icontains=search) |
            Q(branch__name__icontains=search)  # Filial nomi bo‘yicha qidiruv
        )

    # Sahifalash
    paginator = Paginator(users, limit)
    paginated_users = paginator.get_page(page)

    # Forma
    form = UserForm(user=request.user)

    # Filiallarni keshdan olish
    cache_key = 'all_branches'
    branches = cache.get(cache_key)
    if not branches:
        branches = Branch.objects.all()
        cache.set(cache_key, branches, 60 * 60)  # 1 soat kesh

    return render(request, 'admin/admin_list.html', {
        'users': paginated_users,
        'branches': branches,
        'form': form,
        'search_query': search,
        'total_pages': paginator.num_pages
    })


@csrf_protect
@login_required
def admin_create(request):
    if not request.user.is_superuser:
        return render(request, 'xatolik/403.html', status=403)

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.role = 'administrator'
            user.save()
            messages.success(request, "Admin muvaffaqiyatli qo‘shildi!")
            return redirect('admin_list')
        else:
            messages.error(request, "Admin qo'shishda xatolik yuz berdi.")
    return redirect('admin_list')


@csrf_protect
@login_required
def admin_edit(request, user_id):
    if not request.user.is_superuser:
        return render(request, 'xatolik/403.html', status=403)

    user = get_object_or_404(User, id=user_id, role='administrator')
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            if 'password' in form.cleaned_data and form.cleaned_data['password']:
                updated_user.password = make_password(form.cleaned_data['password'])
            updated_user.role = 'administrator'  # Rol o‘zgarmasligini ta'minlash
            updated_user.save()
            messages.success(request, "Admin muvaffaqiyatli tahrirlandi!")
            return redirect('admin_list')
        else:
            messages.error(request, "Admin tahrirlashda xatolik yuz berdi.")
    return redirect('admin_list')


@csrf_protect
@login_required
def admin_delete(request, user_id):
    if not request.user.is_superuser:
        return render(request, 'xatolik/403.html', status=403)

    user = get_object_or_404(User, id=user_id, role='administrator')
    if request.method == "POST":
        user.delete()
        messages.success(request, "Admin muvaffaqiyatli o‘chirildi!")
        return redirect('admin_list')
    return redirect('admin_list')


@login_required
def moderator_list(request):
    """Moderatorlar ro‘yxatini ko‘rsatish uchun View"""
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    limit = request.GET.get('limit', 10)
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '').strip()

    # Limit va page ni xavfsiz tarzda int ga aylantirish
    limit = min(max(int(limit), 1), 50) if str(limit).isdigit() else 10
    page = max(int(page), 1) if str(page).isdigit() else 1

    # Moderatorlarni olish
    users = User.objects.filter(role='moderator').order_by('-created_at')

    # Agar joriy foydalanuvchi moderator bo‘lsa, faqat o‘z filialidagi moderatorlarni ko‘rsin
    if request.user.role == 'moderator' and request.user.branch:
        users = users.filter(branch=request.user.branch)

    # Qidiruv filtri hamma ustunlar bo‘yicha
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(passport_number__icontains=search) |
            Q(role__icontains=search) |
            Q(user_status__icontains=search) |
            Q(branch__name__icontains=search)  # Filial nomi bo‘yicha qidiruv
        )

    # Sahifalash
    paginator = Paginator(users, limit)
    paginated_users = paginator.get_page(page)

    # Forma
    form = UserForm(user=request.user)

    # Filiallarni keshdan olish
    cache_key = 'all_branches'
    branches = cache.get(cache_key)
    if not branches:
        branches = Branch.objects.all()
        cache.set(cache_key, branches, 60 * 60)  # 1 soat kesh

    return render(request, 'admin/moderator_list.html', {
        'users': paginated_users,
        'branches': branches,
        'form': form,
        'search_query': search,
        'total_pages': paginator.num_pages
    })


@csrf_protect
@login_required
def moderator_create(request):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'moderator'
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Moderator muvaffaqiyatli qo‘shildi!")
            return redirect('moderator_list')
        else:
            messages.error(request, "Moderator qo'shishda xatolik yuz berdi.")
    return redirect('moderator_list')


@csrf_protect
@login_required
def moderator_edit(request, user_id):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    user = get_object_or_404(User, id=user_id, role='moderator')
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            if 'password' in form.cleaned_data and form.cleaned_data['password']:
                updated_user.password = make_password(form.cleaned_data['password'])
            updated_user.role = 'moderator'  # Rol o‘zgarmasligini ta'minlash
            updated_user.save()
            messages.success(request, "Moderator muvaffaqiyatli tahrirlandi!")
            return redirect('moderator_list')
        else:
            messages.error(request, "Moderator tahrirlashda xatolik yuz berdi.")
    return redirect('moderator_list')


@csrf_protect
@login_required
def moderator_delete(request, user_id):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    user = get_object_or_404(User, id=user_id, role='moderator')
    if request.method == "POST":
        user.delete()
        messages.success(request, "Moderator muvaffaqiyatli o‘chirildi!")
        return redirect('moderator_list')
    return redirect('moderator_list')


@login_required
def user1_list(request):
    """User1 ro‘yxatini ko‘rsatish uchun View"""
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    limit = request.GET.get('limit', 10)
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '').strip()

    # Limit va page ni xavfsiz tarzda int ga aylantirish
    limit = min(max(int(limit), 1), 50) if str(limit).isdigit() else 10
    page = max(int(page), 1) if str(page).isdigit() else 1

    # User1 rolidagi foydalanuvchilarni olish
    users = User.objects.filter(role='user1').order_by('-created_at')

    # Agar joriy foydalanuvchi moderator bo‘lsa, faqat o‘z filialidagi user1’larni ko‘rsin
    if request.user.role == 'moderator' and request.user.branch:
        users = users.filter(branch=request.user.branch)

    # Qidiruv filtri hamma ustunlar bo‘yicha
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(passport_number__icontains=search) |
            Q(role__icontains=search) |
            Q(user_status__icontains=search) |
            Q(branch__name__icontains=search)  # Filial nomi bo‘yicha qidiruv
        )

    # Sahifalash
    paginator = Paginator(users, limit)
    paginated_users = paginator.get_page(page)

    # Forma
    form = UserForm(user=request.user)

    # Filiallarni keshdan olish
    cache_key = 'all_branches'
    branches = cache.get(cache_key)
    if not branches:
        branches = Branch.objects.all()
        cache.set(cache_key, branches, 60 * 60)  # 1 soat kesh

    return render(request, 'admin/user1_list.html', {
        'users': paginated_users,
        'branches': branches,
        'form': form,
        'search_query': search,
        'total_pages': paginator.num_pages
    })


@login_required
def m_user1_list(request):
    """Moderator uchun User1 ro‘yxatini ko‘rsatish uchun View"""
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu sahifaga kirishga ruxsat yo‘q.")

    limit = request.GET.get('limit', 10)
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '').strip()

    # Limit va page ni xavfsiz tarzda int ga aylantirish
    limit = min(max(int(limit), 1), 50) if str(limit).isdigit() else 10
    page = max(int(page), 1) if str(page).isdigit() else 1

    # Moderatorning o‘z filialidagi user1 foydalanuvchilarni olish
    users = User.objects.filter(
        role='user1',
        branch=request.user.branch
    ).order_by('-created_at')

    # Qidiruv filtri hamma ustunlar bo‘yicha
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(passport_number__icontains=search) |
            Q(role__icontains=search) |
            Q(user_status__icontains=search) |
            Q(branch__name__icontains=search)  # Filial nomi bo‘yicha qidiruv
        )

    # Sahifalash
    paginator = Paginator(users, limit)
    paginated_users = paginator.get_page(page)

    # Forma
    form = UserForm(user=request.user)

    # Faqat moderatorning filialini keshdan olish
    cache_key = f'branch_{request.user.branch.id}'
    branches = cache.get(cache_key)
    if not branches:
        branches = Branch.objects.filter(id=request.user.branch.id)
        cache.set(cache_key, branches, 60 * 60)  # 1 soat kesh

    return render(request, 'moderator/m_user1_list.html', {
        'users': paginated_users,
        'branches': branches,
        'form': form,
        'search_query': search,
        'total_pages': paginator.num_pages
    })


@csrf_protect
@login_required
def user1_create(request):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'user1'  # Rolni majburan 'user1' qilib belgilash
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli qo‘shildi!")
            return redirect('user1_list')
        else:
            messages.error(request, "Foydalanuvchi qo'shishda xatolik yuz berdi.")
    return redirect('user1_list')


@csrf_protect
@login_required
def m_user1_create(request):
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu amalni bajarishga ruxsat yo‘q.")

    if request.method == "POST":
        form = UserForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'user1'  # Rolni majburan 'user1' qilib belgilash
            user.branch = request.user.branch  # Moderatorning filialini avtomatik qo‘shish
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli qo‘shildi!")
            return redirect('m_user1_list')
        else:
            messages.error(request, "Foydalanuvchi qo'shishda xatolik yuz berdi.")
    return redirect('m_user1_list')


@csrf_protect
@login_required
def user1_edit(request, user_id):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    user = get_object_or_404(User, id=user_id, role='user1')
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            if 'password' in form.cleaned_data and form.cleaned_data['password']:
                updated_user.password = make_password(form.cleaned_data['password'])
            updated_user.role = 'user1'  # Rol o‘zgarmasligini ta'minlash
            updated_user.save()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli tahrirlandi!")
            return redirect('user1_list')
        else:
            messages.error(request, "Foydalanuvchi tahrirlashda xatolik yuz berdi.")
    return redirect('user1_list')


@csrf_protect
@login_required
def m_user1_edit(request, user_id):
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu amalni bajarishga ruxsat yo‘q.")

    user = get_object_or_404(User, id=user_id, role='user1', branch=request.user.branch)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            if 'password' in form.cleaned_data and form.cleaned_data['password']:
                updated_user.password = make_password(form.cleaned_data['password'])
            updated_user.role = 'user1'  # Rol o‘zgarmasligini ta'minlash
            updated_user.branch = request.user.branch  # Filial o‘zgarmasligini ta'minlash
            updated_user.save()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli tahrirlandi!")
            return redirect('m_user1_list')
        else:
            messages.error(request, "Foydalanuvchi tahrirlashda xatolik yuz berdi.")
    return redirect('m_user1_list')


@csrf_protect
@login_required
def m_user2_edit(request, user_id):
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu amalni bajarishga ruxsat yo‘q.")

    user = get_object_or_404(User, id=user_id, role='user2', branch=request.user.branch)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            if 'password' in form.cleaned_data and form.cleaned_data['password']:
                updated_user.password = make_password(form.cleaned_data['password'])
            updated_user.role = 'user2'  # Rol o‘zgarmasligini ta'minlash
            updated_user.branch = request.user.branch  # Filial o‘zgarmasligini ta'minlash
            updated_user.save()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli tahrirlandi!")
            return redirect('m_user2_list')
        else:
            messages.error(request, "Foydalanuvchi tahrirlashda xatolik yuz berdi.")
    return redirect('m_user2_list')


@csrf_protect
@login_required
def m_user3_edit(request, user_id):
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu amalni bajarishga ruxsat yo‘q.")

    user = get_object_or_404(User, id=user_id, role='user3', branch=request.user.branch)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            if 'password' in form.cleaned_data and form.cleaned_data['password']:
                updated_user.password = make_password(form.cleaned_data['password'])
            updated_user.role = 'user3'  # Rol o‘zgarmasligini ta'minlash
            updated_user.branch = request.user.branch  # Filial o‘zgarmasligini ta'minlash
            updated_user.save()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli tahrirlandi!")
            return redirect('m_user3_list')
        else:
            messages.error(request, "Foydalanuvchi tahrirlashda xatolik yuz berdi.")
    return redirect('m_user3_list')


@csrf_protect
@login_required
def user1_delete(request, user_id):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    user = get_object_or_404(User, id=user_id, role='user1')
    if request.method == "POST":
        user.delete()
        messages.success(request, "Foydalanuvchi muvaffaqiyatli o‘chirildi!")
        return redirect('user1_list')
    return redirect('user1_list')


@csrf_protect
@login_required
def m_user1_delete(request, user_id):
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu amalni bajarishga ruxsat yo‘q.")

    user = get_object_or_404(User, id=user_id, role='user1', branch=request.user.branch)
    if request.method == "POST":
        user.delete()
        messages.success(request, "Foydalanuvchi muvaffaqiyatli o‘chirildi!")
        return redirect('m_user1_list')
    return redirect('m_user1_list')


@csrf_protect
@login_required
def m_user2_delete(request, user_id):
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu amalni bajarishga ruxsat yo‘q.")

    user = get_object_or_404(User, id=user_id, role='user2', branch=request.user.branch)
    if request.method == "POST":
        user.delete()
        messages.success(request, "Foydalanuvchi muvaffaqiyatli o‘chirildi!")
        return redirect('m_user2_list')
    return redirect('m_user2_list')


@csrf_protect
@login_required
def m_user3_delete(request, user_id):
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu amalni bajarishga ruxsat yo‘q.")

    user = get_object_or_404(User, id=user_id, role='user3', branch=request.user.branch)
    if request.method == "POST":
        user.delete()
        messages.success(request, "Foydalanuvchi muvaffaqiyatli o‘chirildi!")
        return redirect('m_user3_list')
    return redirect('m_user3_list')


@login_required
def user2_list(request):
    """User2 ro‘yxatini ko‘rsatish uchun View"""
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    limit = request.GET.get('limit', 10)
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '').strip()

    # Limit va page ni xavfsiz tarzda int ga aylantirish
    limit = min(max(int(limit), 1), 50) if str(limit).isdigit() else 10
    page = max(int(page), 1) if str(page).isdigit() else 1

    # User2 rolidagi foydalanuvchilarni olish
    users = User.objects.filter(role='user2').order_by('-created_at')

    # Agar joriy foydalanuvchi moderator bo‘lsa, faqat o‘z filialidagi user2’larni ko‘rsin
    if request.user.role == 'moderator' and request.user.branch:
        users = users.filter(branch=request.user.branch)

    # Qidiruv filtri hamma ustunlar bo‘yicha
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(passport_number__icontains=search) |
            Q(role__icontains=search) |
            Q(user_status__icontains=search) |
            Q(branch__name__icontains=search)  # Filial nomi bo‘yicha qidiruv
        )

    # Sahifalash
    paginator = Paginator(users, limit)
    paginated_users = paginator.get_page(page)

    # Forma
    form = UserForm(user=request.user)

    # Filiallarni keshdan olish
    cache_key = 'all_branches'
    branches = cache.get(cache_key)
    if not branches:
        branches = Branch.objects.all()
        cache.set(cache_key, branches, 60 * 60)  # 1 soat kesh

    return render(request, 'admin/user2_list.html', {
        'users': paginated_users,
        'branches': branches,
        'form': form,
        'search_query': search,
        'total_pages': paginator.num_pages
    })


@login_required
def m_user2_list(request):
    """Moderator uchun User2 ro‘yxatini ko‘rsatish uchun View"""
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu sahifaga kirishga ruxsat yo‘q.")

    limit = request.GET.get('limit', 10)
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '').strip()

    # Limit va page ni xavfsiz tarzda int ga aylantirish
    limit = min(max(int(limit), 1), 50) if str(limit).isdigit() else 10
    page = max(int(page), 1) if str(page).isdigit() else 1

    # Moderatorning o‘z filialidagi user2 foydalanuvchilarni olish
    users = User.objects.filter(
        role='user2',
        branch=request.user.branch
    ).order_by('-created_at')

    # Qidiruv filtri hamma ustunlar bo‘yicha
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(passport_number__icontains=search) |
            Q(role__icontains=search) |
            Q(user_status__icontains=search) |
            Q(branch__name__icontains=search)  # Filial nomi bo‘yicha qidiruv
        )

    # Sahifalash
    paginator = Paginator(users, limit)
    paginated_users = paginator.get_page(page)

    # Forma
    form = UserForm(user=request.user)

    # Faqat moderatorning filialini keshdan olish
    cache_key = f'branch_{request.user.branch.id}'
    branches = cache.get(cache_key)
    if not branches:
        branches = Branch.objects.filter(id=request.user.branch.id)
        cache.set(cache_key, branches, 60 * 60)  # 1 soat kesh

    return render(request, 'moderator/m_user2_list.html', {
        'users': paginated_users,
        'branches': branches,
        'form': form,
        'search_query': search,
        'total_pages': paginator.num_pages
    })


@csrf_protect
@login_required
def user2_create(request):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'user2'  # Rolni majburan 'user2' qilib belgilash
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli qo‘shildi!")
            return redirect('user2_list')
        else:
            messages.error(request, "Foydalanuvchi qo'shishda xatolik yuz berdi.")
    return redirect('user2_list')


@csrf_protect
@login_required
def m_user2_create(request):
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu amalni bajarishga ruxsat yo‘q.")

    if request.method == "POST":
        form = UserForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'user2'  # Rolni majburan 'user2' qilib belgilash
            user.branch = request.user.branch  # Moderatorning filialini avtomatik qo‘shish
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli qo‘shildi!")
            return redirect('m_user2_list')
        else:
            messages.error(request, "Foydalanuvchi qo'shishda xatolik yuz berdi.")
    return redirect('m_user2_list')


@csrf_protect
@login_required
def user2_edit(request, user_id):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    user = get_object_or_404(User, id=user_id, role='user2')
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            if 'password' in form.cleaned_data and form.cleaned_data['password']:
                updated_user.password = make_password(form.cleaned_data['password'])
            updated_user.role = 'user2'  # Rol o‘zgarmasligini ta'minlash
            updated_user.save()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli tahrirlandi!")
            return redirect('user2_list')
        else:
            messages.error(request, "Foydalanuvchi tahrirlashda xatolik yuz berdi.")
    return redirect('user2_list')


@csrf_protect
@login_required
def user2_delete(request, user_id):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    user = get_object_or_404(User, id=user_id, role='user2')
    if request.method == "POST":
        user.delete()
        messages.success(request, "Foydalanuvchi muvaffaqiyatli o‘chirildi!")
        return redirect('user2_list')
    return redirect('user2_list')


def user3_list(request):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    limit = min(max(int(request.GET.get('limit', 10)), 1), 50) if str(request.GET.get('limit', 10)).isdigit() else 10
    page = max(int(request.GET.get('page', 1)), 1) if str(request.GET.get('page', 1)).isdigit() else 1
    search = request.GET.get('search', '').strip()

    users = User.objects.filter(Q(role='user3') | Q(user_status='waiting')).order_by('-created_at')
    print("Initial users count:", users.count())

    if request.user.role == 'moderator' and request.user.branch:
        users = users.filter(branch=request.user.branch)
        print("Filtered by branch count:", users.count())

    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(passport_number__icontains=search) |
            Q(role__icontains=search) |
            Q(user_status__icontains=search) |
            Q(branch__name__icontains=search)
        )
        print("Filtered by search count:", users.count())

    paginator = Paginator(users, limit)
    paginated_users = paginator.get_page(page)
    print("Current page users:", len(paginated_users))

    form = UserForm(user=request.user)
    cache_key = 'all_branches'
    branches = cache.get(cache_key)
    if not branches:
        branches = Branch.objects.all()
        cache.set(cache_key, branches, 60 * 60)

    return render(request, 'admin/user3_list.html', {
        'users': paginated_users,
        'branches': branches,
        'form': form,
        'search_query': search,
        'total_pages': paginator.num_pages
    })


@login_required
def m_user3_list(request):
    """Moderator uchun User3 ro‘yxatini ko‘rsatish uchun View"""
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu sahifaga kirishga ruxsat yo‘q.")

    limit = request.GET.get('limit', 10)
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '').strip()

    # Limit va page ni xavfsiz tarzda int ga aylantirish
    limit = min(max(int(limit), 1), 50) if str(limit).isdigit() else 10
    page = max(int(page), 1) if str(page).isdigit() else 1

    # Moderatorning o‘z filialidagi user3 foydalanuvchilarni olish
    users = User.objects.filter(
        role='user3',
        branch=request.user.branch
    ).order_by('-created_at')

    # Qidiruv filtri hamma ustunlar bo‘yicha
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(passport_number__icontains=search) |
            Q(role__icontains=search) |
            Q(user_status__icontains=search) |
            Q(branch__name__icontains=search)  # Filial nomi bo‘yicha qidiruv
        )

    # Sahifalash
    paginator = Paginator(users, limit)
    paginated_users = paginator.get_page(page)

    # Forma
    form = UserForm(user=request.user)

    # Faqat moderatorning filialini keshdan olish
    cache_key = f'branch_{request.user.branch.id}'
    branches = cache.get(cache_key)
    if not branches:
        branches = Branch.objects.filter(id=request.user.branch.id)
        cache.set(cache_key, branches, 60 * 60)  # 1 soat kesh

    return render(request, 'moderator/m_user3_list.html', {
        'users': paginated_users,
        'branches': branches,
        'form': form,
        'search_query': search,
        'total_pages': paginator.num_pages
    })


@csrf_protect
@login_required
def user3_create(request):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'user3'  # Rolni majburan 'user3' qilib belgilash
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli qo‘shildi!")
            return redirect('user3_list')
        else:
            messages.error(request, "Foydalanuvchi qo'shishda xatolik yuz berdi.")
    return redirect('user3_list')


@csrf_protect
@login_required
def m_user3_create(request):
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu amalni bajarishga ruxsat yo‘q.")

    if request.method == "POST":
        form = UserForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'user3'  # Rolni majburan 'user3' qilib belgilash
            user.branch = request.user.branch  # Moderatorning filialini avtomatik qo‘shish
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli qo‘shildi!")
            return redirect('m_user3_list')
        else:
            messages.error(request, "Foydalanuvchi qo'shishda xatolik yuz berdi.")
    return redirect('m_user3_list')


@csrf_protect
@login_required
def user3_edit(request, user_id):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    user = get_object_or_404(User, id=user_id, role='user3')
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            if 'password' in form.cleaned_data and form.cleaned_data['password']:
                updated_user.password = make_password(form.cleaned_data['password'])
            updated_user.role = 'user3'  # Rol o‘zgarmasligini ta'minlash
            updated_user.save()
            messages.success(request, "Foydalanuvchi muvaffaqiyatli tahrirlandi!")
            return redirect('user3_list')
        else:
            messages.error(request, "Foydalanuvchi tahrirlashda xatolik yuz berdi.")
    return redirect('user3_list')


@csrf_protect
@login_required
def user3_delete(request, user_id):
    if not (request.user.is_superuser or request.user.role == 'moderator'):
        return render(request, 'xatolik/403.html', status=403)

    user = get_object_or_404(User, id=user_id, role='user3')
    if request.method == "POST":
        user.delete()
        messages.success(request, "Foydalanuvchi muvaffaqiyatli o‘chirildi!")
        return redirect('user3_list')
    return redirect('user3_list')


@login_required
def page_403(request):
    return render(request, 'xatolik/403.html')
