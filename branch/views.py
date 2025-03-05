from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.cache import cache
from .models import Branch
from .forms import BranchForm


@login_required
def branch_list(request):
    """Filiallar ro‘yxatini ko‘rsatish uchun View"""
    limit = request.GET.get('limit', 10)  # Default 10
    page_number = request.GET.get('page', 1)  # Default 1
    search = request.GET.get('search', '').strip()

    # Limit va page_number ni xavfsiz tarzda int ga aylantirish
    limit = min(max(int(limit), 1), 100) if str(limit).isdigit() else 10  # 1-100 oralig‘ida
    page_number = max(int(page_number), 1) if str(page_number).isdigit() else 1

    # Filiallarni olish va qidiruv filtri
    branches = Branch.objects.all().order_by('-created_at')
    if search:
        branches = branches.filter(name__icontains=search)

    # Sahifalash
    paginator = Paginator(branches, limit)
    page_obj = paginator.get_page(page_number)

    # Forma
    form = BranchForm()

    return render(request, 'branch_list.html', {
        'branches': page_obj,
        'form': form,
        'search_query': search,
    })


@csrf_protect
@login_required
def branch_create(request):
    if request.method == "POST":
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            cache.clear()  # Keshni tozalash
            messages.success(request, "Filial muvaffaqiyatli qo‘shildi!")
            return redirect('branch_list')
        else:
            messages.error(request, "Filial qo'shishda xatolik yuz berdi.")
    return redirect('branch_list')


@csrf_protect
@login_required
def branch_edit(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == "POST":
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            cache.clear()  # Keshni tozalash
            messages.success(request, "Filial muvaffaqiyatli tahrirlandi!")
            return redirect('branch_list')
        else:
            messages.error(request, "Filial tahrirlashda xatolik yuz berdi.")
    return redirect('branch_list')


@csrf_protect
@login_required
def branch_delete(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == "POST":
        branch.delete()
        cache.clear()  # Keshni tozalash
        messages.success(request, "Filial muvaffaqiyatli o‘chirildi!")
        return redirect('branch_list')
    return redirect('branch_list')
