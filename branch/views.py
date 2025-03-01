from django.shortcuts import render, get_object_or_404,redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Branch
from .forms import BranchForm
from django.core.paginator import Paginator


def branch_list(request):
    """ Filiallar ro‘yxatini ko‘rsatish uchun View """

    # GET parametrlardan limitni olish
    limit = request.GET.get('limit', '10')  # Default limit = '10' (string sifatida keladi)
    page_number = request.GET.get('page', '1')  # Default sahifa = '1'

    # limitni aniq butun son shaklga o'tkazish (agar noto‘g‘ri qiymat bo‘lsa, default = 10)
    try:
        limit = int(limit) if limit.isdigit() and int(limit) > 0 else 10
    except ValueError:
        limit = 10

    try:
        page_number = int(page_number) if page_number.isdigit() and int(page_number) > 0 else 1
    except ValueError:
        page_number = 1

    # Barcha filiallarni olish va sahifalash
    branches = Branch.objects.all()
    paginator = Paginator(branches, limit)
    page_obj = paginator.get_page(page_number)

    # Muvaffaqiyatli xabarni olish
    success_message = request.session.pop('success', None)

    # Forma yaratish
    form = BranchForm()

    return render(request, 'branch_list.html', {
        'branches': page_obj,
        'form': form,
        'success_message': success_message
    })



@csrf_exempt
def branch_create(request):
    if request.method == "POST":
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
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

