from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import User, Branch
from .forms import UserForm, UserRegistrationForm
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .utils import get_redirect_url
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden



@csrf_exempt
def sayt(request):
    return render(request, 'users/user3.html')

@login_required
@csrf_exempt
def user1(reqest):
    return render(reqest, 'users/user1.html')

@login_required
@csrf_exempt
def user2(reqest):
    return render(reqest, 'users/user2.html')
@csrf_exempt
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'bosh sahifa/Bosh_sahifa.html', {'user': request.user})


@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ro‘yxatdan o‘tdingiz! Admin tasdiqlashini kuting.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    branches = Branch.objects.all()
    return render(request, 'register.html', {'form': form, 'branches': branches})


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


@csrf_exempt
def admin_list(request):
    limit = request.GET.get("limit", 10)  # Default limit = 10
    page = request.GET.get("page", 1)  # Default sahifa = 1

    # Limit integer bo‘lishi kerak, noto‘g‘ri kiritilsa 10 qilib qo‘yamiz
    try:
        limit = int(limit)
        if limit <= 0:
            limit = 10
    except ValueError:
        limit = 10

    # Faqat administrator rolidagi foydalanuvchilarni tanlaymiz
    users = User.objects.filter(role='administrator').order_by(
        "-created_at")  # Eng oxirgi foydalanuvchilar birinchi bo‘lsin

    paginator = Paginator(users, limit)  # Paginator obyektini yaratish
    paginated_users = paginator.get_page(page)  # Hozirgi sahifani olish

    success_message = request.session.pop('success', None)
    form = UserForm()

    return render(request, 'admin/admin_list.html', {
        'users': paginated_users,
        'branches': Branch.objects.all(),
        'success_message': success_message,
        'form': form,
        'total_pages': paginator.num_pages  # Umumiy sahifalar sonini ham jo‘natamiz
    })


@csrf_exempt
def admin_create(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Foydalanuvchini yaratamiz, lekin hali bazaga saqlamaymiz
            user.password = make_password(form.cleaned_data['password'])  # Parolni hash qilish
            user.role = 'administrator'  # Faqat administrator rolini belgilaymiz
            user.save()  # Endi saqlash
            request.session['success'] = "Admin muvaffaqiyatli qo‘shildi!"
            return redirect('admin_list')
    return redirect('admin_list')


@csrf_exempt
def admin_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            updated_user.role = 'administrator'  # Foydalanuvchi rolini majburan administrator qilib belgilaymiz
            # Agar parol maydoni ham tahrir qilinayotgan bo'lsa, uni hash qilishni ham qo'shishingiz mumkin:
            if 'password' in form.cleaned_data:
                updated_user.password = make_password(form.cleaned_data['password'])
            updated_user.save()
            return redirect('admin_list')
    return redirect('admin_list')


@csrf_exempt
def admin_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Faqat administrator rolidagi foydalanuvchilarni o'chirishga ruxsat beramiz
    if user.role != 'administrator':
        return redirect('admin_list')

    if request.method == "POST":
        user.delete()
        return redirect('admin_list')
    return redirect('admin_list')


@csrf_exempt
def moderator_list(request):
    limit = request.GET.get("limit", 10)  # Default limit = 10
    page = request.GET.get("page", 1)  # Default sahifa = 1

    # Limit integer bo‘lishi kerak, noto‘g‘ri kiritilsa 10 qilib qo‘yamiz
    try:
        limit = int(limit)
        if limit <= 0:
            limit = 10
    except ValueError:
        limit = 10

    # Faqat moderator rolidagi foydalanuvchilarni tanlaymiz
    users = User.objects.filter(role='moderator').order_by("-created_at")

    paginator = Paginator(users, limit)  # Paginator obyektini yaratish
    paginated_users = paginator.get_page(page)  # Hozirgi sahifani olish

    success_message = request.session.pop('success', None)
    form = UserForm()

    return render(request, 'admin/moderator_list.html', {
        'users': paginated_users,
        'branches': Branch.objects.all(),
        'success_message': success_message,
        'form': form,
        'total_pages': paginator.num_pages  # Umumiy sahifalar sonini ham jo‘natamiz
    })


@csrf_exempt
def moderator_create(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # Foydalanuvchini yaratishdan oldin rolni majburan 'moderator' ga o'rnatamiz
            user = form.save(commit=False)
            user.role = 'moderator'
            user.save()
            request.session['success'] = "Moderator muvaffaqiyatli qo‘shildi!"
            return redirect('moderator_list')
    return redirect('moderator_list')


@csrf_exempt
def moderator_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('moderator_list')
    return redirect('moderator_list')


@csrf_exempt
def moderator_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # Faqat moderator rolidagi foydalanuvchilarni o'chirishga ruxsat beramiz
    if user.role != 'moderator':
        return redirect('moderator_list')

    if request.method == "POST":
        user.delete()
        return redirect('moderator_list')
    return redirect('moderator_list')


@csrf_exempt
def user1_list(request):
    limit = request.GET.get("limit", 10)  # Default limit = 10
    page = request.GET.get("page", 1)  # Default sahifa = 1

    # Limit integer bo‘lishi kerak, noto‘g‘ri kiritilsa 10 qilib qo‘yamiz
    try:
        limit = int(limit)
        if limit <= 0:
            limit = 10
    except ValueError:
        limit = 10

    # Faqat moderator rolidagi foydalanuvchilarni tanlaymiz
    users = User.objects.filter(role='user1').order_by("-created_at")

    paginator = Paginator(users, limit)  # Paginator obyektini yaratish
    paginated_users = paginator.get_page(page)  # Hozirgi sahifani olish

    success_message = request.session.pop('success', None)
    form = UserForm()

    return render(request, 'admin/user1_list.html', {
        'users': paginated_users,
        'branches': Branch.objects.all(),
        'success_message': success_message,
        'form': form,
        'total_pages': paginator.num_pages  # Umumiy sahifalar sonini ham jo‘natamiz
    })


@login_required
def m_user1_list(request):
    # Faqat moderatorlar uchun ruxsat
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu sahifaga kirishga ruxsat yo‘q.")

    limit = request.GET.get("limit", 10)  # Default limit = 10
    page = request.GET.get("page", 1)  # Default sahifa = 1

    # Limit integer bo‘lishi kerak, noto‘g‘ri kiritilsa 10 qilib qo‘yamiz
    try:
        limit = int(limit)
        if limit <= 0:
            limit = 10
    except ValueError:
        limit = 10

    # Moderatorning faqat o‘z branchidagi user1, user2, user3 rolli foydalanuvchilarni olish
    users = User.objects.filter(
        role='user1',  # user1, user2, user3 rollari
        branch=request.user.branch  # faqat moderatorning branchi
    ).order_by("-created_at")

    paginator = Paginator(users, limit)  # Paginator obyektini yaratish
    paginated_users = paginator.get_page(page)  # Hozirgi sahifani olish

    success_message = request.session.pop('success', None)
    form = UserForm(user=request.user)  # Forma yaratishda joriy foydalanuvchini uzatamiz

    return render(request, 'moderator/m_user1_list.html', {
        'users': paginated_users,
        'branches': Branch.objects.filter(id=request.user.branch.id),  # Faqat moderatorning branchi
        'success_message': success_message,
        'form': form,
        'total_pages': paginator.num_pages  # Umumiy sahifalar sonini ham jo‘natamiz
    })


@csrf_exempt
def user1_create(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # user.role = 'user1' qatori olib tashlandi
            user.save()
            request.session['success'] = "Foydalanuvchi muvaffaqiyatli qo‘shildi!"
            return redirect('user1_list')
    return redirect('user1_list')


@csrf_exempt
def m_user1_create(request):
    if request.method == "POST":
        form = UserForm(request.POST, user=request.user)  # User uzatish
        if form.is_valid():
            user = form.save(commit=False)

            # Faqat agar request.user haqiqiy foydalanuvchi bo‘lsa va branch mavjud bo‘lsa, branchni o‘rnatish
            if isinstance(request.user, User) and request.user.role == 'moderator' and request.user.branch:
                user.branch = request.user.branch

            user.save()
            request.session['success'] = "Foydalanuvchi muvaffaqiyatli qo‘shildi!"
    return redirect('m_user1_list')


@csrf_exempt
def user1_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            updated_user.save()
            return redirect('user1_list')
    return redirect('user1_list')


@csrf_exempt
def m_user1_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            updated_user.save()
            return redirect('m_user1_list')
    return redirect('m_user1_list')


@csrf_exempt
def m_user2_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            updated_user.save()
            return redirect('m_user2_list')
    return redirect('m_user2_list')


@csrf_exempt
def m_user3_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            updated_user.save()
            return redirect('m_user3_list')
    return redirect('m_user3_list')


@csrf_exempt
def user1_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # Faqat moderator rolidagi foydalanuvchilarni o'chirishga ruxsat beramiz
    if user.role != 'user1':
        return redirect('user1_list')

    if request.method == "POST":
        user.delete()
        return redirect('user1_list')
    return redirect('user1_list')


@csrf_exempt
def m_user1_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # Faqat moderator rolidagi foydalanuvchilarni o'chirishga ruxsat beramiz
    if user.role != 'user1':
        return redirect('m_user1_list')

    if request.method == "POST":
        user.delete()
        return redirect('m_user1_list')
    return redirect('m_user1_list')


@csrf_exempt
def m_user2_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # Faqat moderator rolidagi foydalanuvchilarni o'chirishga ruxsat beramiz
    # if user.role != 'user1':
    #     return redirect('m_user2_list')

    if request.method == "POST":
        user.delete()
        return redirect('m_user2_list')
    return redirect('m_user2_list')


@csrf_exempt
def m_user3_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # Faqat moderator rolidagi foydalanuvchilarni o'chirishga ruxsat beramiz
    # if user.role != 'user1':
    #     return redirect('m_user3_list')

    if request.method == "POST":
        user.delete()
        return redirect('m_user3_list')
    return redirect('m_user3_list')


@csrf_exempt
def user2_list(request):
    limit = request.GET.get("limit", 10)  # Default limit = 10
    page = request.GET.get("page", 1)  # Default sahifa = 1

    # Limit integer bo‘lishi kerak, noto‘g‘ri kiritilsa 10 qilib qo‘yamiz
    try:
        limit = int(limit)
        if limit <= 0:
            limit = 10
    except ValueError:
        limit = 10

    # Faqat moderator rolidagi foydalanuvchilarni tanlaymiz
    users = User.objects.filter(role='user2').order_by("-created_at")

    paginator = Paginator(users, limit)  # Paginator obyektini yaratish
    paginated_users = paginator.get_page(page)  # Hozirgi sahifani olish

    success_message = request.session.pop('success', None)
    form = UserForm()

    return render(request, 'admin/user2_list.html', {
        'users': paginated_users,
        'branches': Branch.objects.all(),
        'success_message': success_message,
        'form': form,
        'total_pages': paginator.num_pages  # Umumiy sahifalar sonini ham jo‘natamiz
    })


@login_required
def m_user2_list(request):
    # Faqat moderatorlar uchun ruxsat
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu sahifaga kirishga ruxsat yo‘q.")

    limit = request.GET.get("limit", 10)  # Default limit = 10
    page = request.GET.get("page", 1)  # Default sahifa = 1

    # Limit integer bo‘lishi kerak, noto‘g‘ri kiritilsa 10 qilib qo‘yamiz
    try:
        limit = int(limit)
        if limit <= 0:
            limit = 10
    except ValueError:
        limit = 10

    # Moderatorning faqat o‘z branchidagi user1, user2, user3 rolli foydalanuvchilarni olish
    users = User.objects.filter(
        role='user2',  # user1, user2, user3 rollari
        branch=request.user.branch  # faqat moderatorning branchi
    ).order_by("-created_at")

    paginator = Paginator(users, limit)  # Paginator obyektini yaratish
    paginated_users = paginator.get_page(page)  # Hozirgi sahifani olish

    success_message = request.session.pop('success', None)
    form = UserForm(user=request.user)  # Forma yaratishda joriy foydalanuvchini uzatamiz

    return render(request, 'moderator/m_user2_list.html', {
        'users': paginated_users,
        'branches': Branch.objects.filter(id=request.user.branch.id),  # Faqat moderatorning branchi
        'success_message': success_message,
        'form': form,
        'total_pages': paginator.num_pages  # Umumiy sahifalar sonini ham jo‘natamiz
    })


@csrf_exempt
def user2_create(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # user.role = 'user2' qatori olib tashlandi
            user.save()
            request.session['success'] = "Foydalanuvchi muvaffaqiyatli qo‘shildi!"
            return redirect('user2_list')
    return redirect('user2_list')


@csrf_exempt
def m_user2_create(request):
    if request.method == "POST":
        form = UserForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            # user.role = 'user1' qatori olib tashlandi
            if isinstance(request.user, User) and request.user.role == 'moderator' and request.user.branch:
                user.branch = request.user.branch
            user.save()
            request.session['success'] = "Foydalanuvchi muvaffaqiyatli qo‘shildi!"
    return redirect('m_user2_list')


@csrf_exempt
def user2_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            # updated_user.role = 'user2' qatori olib tashlandi
            updated_user.save()
            return redirect('user2_list')
    return redirect('user2_list')


@csrf_exempt
def user2_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # if user.role != 'user2' qatori olib tashlandi
    if request.method == "POST":
        user.delete()
        return redirect('user2_list')
    return redirect('user2_list')


@csrf_exempt
def user3_list(request):
    limit = request.GET.get("limit", 10)  # Default limit = 10
    page = request.GET.get("page", 1)  # Default sahifa = 1

    # Limit integer bo‘lishi kerak, noto‘g‘ri kiritilsa 10 qilib qo‘yamiz
    try:
        limit = int(limit)
        if limit <= 0:
            limit = 10
    except ValueError:
        limit = 10

    # Faqat moderator rolidagi foydalanuvchilarni tanlaymiz
    users = User.objects.filter(user_status='waiting', role='user3').order_by("-created_at")

    paginator = Paginator(users, limit)  # Paginator obyektini yaratish
    paginated_users = paginator.get_page(page)  # Hozirgi sahifani olish

    success_message = request.session.pop('success', None)
    form = UserForm()

    return render(request, 'admin/user3_list.html', {
        'users': paginated_users,
        'branches': Branch.objects.all(),
        'success_message': success_message,
        'form': form,
        'total_pages': paginator.num_pages  # Umumiy sahifalar sonini ham jo‘natamiz
    })


@login_required
def m_user3_list(request):
    # Faqat moderatorlar uchun ruxsat
    if request.user.role != 'moderator' or not request.user.branch:
        return HttpResponseForbidden("Sizga bu sahifaga kirishga ruxsat yo‘q.")

    limit = request.GET.get("limit", 10)  # Default limit = 10
    page = request.GET.get("page", 1)  # Default sahifa = 1

    # Limit integer bo‘lishi kerak, noto‘g‘ri kiritilsa 10 qilib qo‘yamiz
    try:
        limit = int(limit)
        if limit <= 0:
            limit = 10
    except ValueError:
        limit = 10

    # Moderatorning faqat o‘z branchidagi user1, user2, user3 rolli foydalanuvchilarni olish
    users = User.objects.filter(
        role='user3',  # user1, user2, user3 rollari
        branch=request.user.branch  # faqat moderatorning branchi
    ).order_by("-created_at")

    paginator = Paginator(users, limit)  # Paginator obyektini yaratish
    paginated_users = paginator.get_page(page)  # Hozirgi sahifani olish

    success_message = request.session.pop('success', None)
    form = UserForm(user=request.user)  # Forma yaratishda joriy foydalanuvchini uzatamiz

    return render(request, 'moderator/m_user3_list.html', {
        'users': paginated_users,
        'branches': Branch.objects.filter(id=request.user.branch.id),  # Faqat moderatorning branchi
        'success_message': success_message,
        'form': form,
        'total_pages': paginator.num_pages  # Umumiy sahifalar sonini ham jo‘natamiz
    })


@csrf_exempt
def user3_create(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # user.role = 'user3'  # Bu qator o‘chirildi, endi forma orqali keladi
            user.save()
            request.session['success'] = "Foydalanuvchi muvaffaqiyatli qo‘shildi!"
            return redirect('user3_list')
    return redirect('user3_list')


@csrf_exempt
def m_user3_create(request):
    if request.method == "POST":
        form = UserForm(request.POST, user=request.user)  # User uzatish
        if form.is_valid():
            user = form.save(commit=False)
            # user.role = 'user1'  # Bu qator o‘chirildi, endi forma orqali keladi

            # Faqat agar request.user haqiqiy foydalanuvchi bo‘lsa va branch mavjud bo‘lsa, branchni o‘rnatish
            if isinstance(request.user, User) and request.user.role == 'moderator' and request.user.branch:
                user.branch = request.user.branch

            user.save()
            request.session['success'] = "Foydalanuvchi muvaffaqiyatli qo‘shildi!"
    return redirect('m_user3_list')


@csrf_exempt
def user3_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user3_list')
    return redirect('user3_list')


@csrf_exempt
def user3_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # Faqat moderator rolidagi foydalanuvchilarni o'chirishga ruxsat beramiz
    if user.role != 'user2':
        return redirect('user3_list')

    if request.method == "POST":
        user.delete()
        return redirect('user3_list')
    return redirect('user3_list')
