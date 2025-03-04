from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .models import Branch
from .forms import BranchForm
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.core.cache import cache


@cache_page(60 * 10)
def branch_list(request):
    """ Filiallar ro‘yxatini ko‘rsatish uchun View """
    limit = request.GET.get('limit', 10)  # Default 10
    page_number = request.GET.get('page', 1)  # Default 1

    # Limit va page_number ni xavfsiz tarzda int ga aylantirish
    limit = min(max(int(limit), 1), 100) if str(limit).isdigit() else 10  # 1-100 oralig‘ida cheklash
    page_number = max(int(page_number), 1) if str(page_number).isdigit() else 1

    # Filiallarni olish va sahifalash
    branches = Branch.objects.all()
    paginator = Paginator(branches, limit)
    page_obj = paginator.get_page(page_number)

    # Sessiyadan xabarni olish
    success_message = request.session.pop('success', None)
    form = BranchForm()

    return render(request, 'branch_list.html', {
        'branches': page_obj,
        'form': form,
        'success_message': success_message
    })


@csrf_protect
def branch_create(request):
    if request.method == "POST":
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            cache.clear()  # Butun keshni tozalash (oddiy yechim)
            request.session['success'] = "Filial muvaffaqiyatli qo‘shildi!"
            return redirect('branch_list')
    return redirect('branch_list')


@csrf_exempt
def branch_edit(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == "POST":
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            request.session['success'] = "Filial muvaffaqiyatli tahrirlandi!"
            return redirect('branch_list')
    return redirect('branch_list')


@csrf_exempt
def branch_delete(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == "POST":
        branch.delete()
        request.session['success'] = "Filial muvaffaqiyatli o‘chirildi!"
        return redirect('branch_list')
    return redirect('branch_list')
