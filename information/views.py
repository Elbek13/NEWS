from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Dissertatsiya, Monografiya, Risola, Darslik, Qollanma, Loyiha, Jurnal, Maqola, Other, \
    Xorijiy_Tajriba, Branch
from .forms import DissertatsiyaForm, MonografiyaForm, RisolaForm, DarslikForm, QollanmaForm, LoyihaForm, JurnalForm, \
    MaqolaForm, OtherForm, XorijiyTajribaForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def role_required(*roles):
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            user = request.user
            if user.role not in roles:
                return HttpResponseForbidden("Sizga bu sahifaga kirishga ruxsat yo‘q.")

            # View funktsiyasini chaqirish
            result = view_func(request, *args, **kwargs)

            # Agar natija kontekst bo‘lsa, filtr qo‘llash
            if isinstance(result, dict) and 'items' in result:
                items = result['items']
                if hasattr(items, 'queryset'):
                    queryset_to_filter = items.queryset

                    # Rolga qarab filtr qo‘llash
                    if user.role == 'user1':
                        pass  # Hamma ma'lumotni ko‘radi
                    elif user.role == 'user2':
                        queryset_to_filter = queryset_to_filter.exclude(degree='LEVEL1')
                    elif user.role == 'user3':
                        queryset_to_filter = queryset_to_filter.filter(degree='LEVEL3')

                    # Yangi querysetni Paginatorga qayta yuklash
                    limit = request.GET.get("limit", items.per_page)
                    page = request.GET.get("page", items.number)
                    paginator = Paginator(queryset_to_filter, limit)
                    result['items'] = paginator.get_page(page)
                    result['total_pages'] = paginator.num_pages

            return result  # Kontekstni qaytarish (render view’da bajariladi)

        return wrapper

    return decorator


@login_required
@role_required('user1', 'user2', 'user3')
def global_search(request):
    search = request.GET.get("search", "").strip()

    results = {
        'dissertatsiyalar': Dissertatsiya.objects.none(),
        'monografiyalar': Monografiya.objects.none(),
        'risolalar': Risola.objects.none(),
        'darsliklar': Darslik.objects.none(),
        'qollanmalar': Qollanma.objects.none(),
        'loyihalar': Loyiha.objects.none(),
        'jurnallar': Jurnal.objects.none(),
        'maqolalar': Maqola.objects.none(),
        'otherlar': Other.objects.none(),
        'tajribalar': Xorijiy_Tajriba.objects.none(),
    }

    if search:
        # Qidiruv bo‘yicha asosiy so‘rovlar
        results['dissertatsiyalar'] = Dissertatsiya.objects.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(institution_name__icontains=search)
        ).order_by("-created_at")  # Vergul olib tashlandi

        results['monografiyalar'] = Monografiya.objects.filter(  # Dissertatsiya → Monografiya ga tuzatildi
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(institution_name__icontains=search)
        ).order_by("-created_at")  # Vergul olib tashlandi

        results['risolalar'] = Risola.objects.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(institution_name__icontains=search)
        ).order_by("-created_at")  # Vergul olib tashlandi

        results['darsliklar'] = Darslik.objects.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(institution_name__icontains=search)
        ).order_by("-created_at")  # Vergul olib tashlandi

        results['qollanmalar'] = Qollanma.objects.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(institution_name__icontains=search)
        ).order_by("-created_at")  # Vergul olib tashlandi

        results['loyihalar'] = Loyiha.objects.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(institution_name__icontains=search)
        ).order_by("-created_at")  # Vergul olib tashlandi

        results['jurnallar'] = Jurnal.objects.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(institution_name__icontains=search)
        ).order_by("-created_at")  # Vergul olib tashlandi

        results['maqolalar'] = Maqola.objects.filter(  # 'not' olib tashlandi, bu xato edi
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(institution_name__icontains=search)
        ).order_by("-created_at")  # Vergul olib tashlandi

        results['otherlar'] = Other.objects.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(institution_name__icontains=search)
        ).order_by("-created_at")  # Vergul olib tashlandi

        results['tajribalar'] = Xorijiy_Tajriba.objects.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(Military_organization__icontains=search)
        ).order_by("-Military_organization")  # Vergul olib tashlandi

        # Foydalanuvchining roli user2 bo‘lsa, barcha query-setlarda LEVEL1 ma'lumotni chiqarib tashlash:
        user = request.user
        if user.role == 'user2':
            for key, qs in results.items():
                # Agar querysetda 'degree' maydoni mavjud bo‘lsa filtr qo‘llash:
                if hasattr(qs.model, 'degree'):
                    results[key] = qs.exclude(degree='LEVEL1')

    context = {
        'search_query': search,
        'results': results,
    }

    return render(request, "global_search.html", context)


class U3DissertatsiyaListView(LoginRequiredMixin, ListView):
    model = Dissertatsiya
    template_name = 'kategoriya/users/dissertatsiyalar/u3_dissertatsiyalar.html'
    context_object_name = 'dissertatsiyalar'
    paginate_by = 8  # Sahifalash soni

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        # User3 uchun faqat LEVEL3 darajali dissertatsiyalarni filtrlaymiz
        if user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dissertatsiyalar Roʻyxati (User3)'
        context['search_query'] = self.request.GET.get('search', '')

        # Qo‘lda sahifalashni tekshirish
        dissertatsiyalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(dissertatsiyalar, self.paginate_by)

        try:
            dissertatsiyalar = paginator.page(page)
        except PageNotAnInteger:
            dissertatsiyalar = paginator.page(1)
        except EmptyPage:
            dissertatsiyalar = paginator.page(paginator.num_pages)

        context['dissertatsiyalar'] = dissertatsiyalar
        return context


class U3DissertatsiyaDetailView(LoginRequiredMixin, DetailView):
    model = Dissertatsiya
    template_name = 'kategoriya/users/dissertatsiyalar/u3_dissertatsiya_detail.html'
    context_object_name = 'dissertatsiya'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user3 va dissertatsiya LEVEL3 bo‘lmasa, kirishni taqiqlash
        if user.role == 'user3' and obj.degree != 'LEVEL3':
            messages.error(self.request, "Sizda ushbu dissertatsiyani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Dissertatsiya: {self.object.title}"
        return context


class U3MonografiyaListView(LoginRequiredMixin, ListView):
    model = Monografiya
    template_name = 'kategoriya/users/monografiyalar/u3_monografiyalar.html'
    context_object_name = 'monografiyalar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        # User3 uchun faqat LEVEL3 darajali monografiyalarni filtrlaymiz
        if user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Monografiyalar Roʻyxati (User3)'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda tekshirish
        monografiyalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(monografiyalar, self.paginate_by)

        try:
            monografiyalar = paginator.page(page)
        except PageNotAnInteger:
            monografiyalar = paginator.page(1)
        except EmptyPage:
            monografiyalar = paginator.page(paginator.num_pages)

        context['monografiyalar'] = monografiyalar
        return context


class U3MonografiyaDetailView(LoginRequiredMixin, DetailView):
    model = Monografiya
    template_name = 'kategoriya/users/monografiyalar/u3_monografiyalar_detail.html'
    context_object_name = 'monografiya'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user3 va monografiya LEVEL3 bo‘lmasa, kirishni taqiqlash
        if user.role == 'user3' and obj.degree != 'LEVEL3':
            messages.error(self.request, "Sizda ushbu monografiyani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Monografiya: {self.object.title}"
        return context


class U3RisolaListView(LoginRequiredMixin, ListView):
    model = Risola
    template_name = 'kategoriya/users/Kitob va Risola/u3_risolalar.html'
    context_object_name = 'risolalar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        # User3 uchun faqat LEVEL3 darajali risolalarni filtrlaymiz
        if user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Risolalar Roʻyxati (User3)'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda tekshirish
        risolalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(risolalar, self.paginate_by)

        try:
            risolalar = paginator.page(page)
        except PageNotAnInteger:
            risolalar = paginator.page(1)
        except EmptyPage:
            risolalar = paginator.page(paginator.num_pages)

        context['risolalar'] = risolalar
        return context


class U3RisolaDetailView(LoginRequiredMixin, DetailView):
    model = Risola
    template_name = 'kategoriya/users/Kitob va Risola/u3_risolalar_detail.html'
    context_object_name = 'risola'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user3 va risola LEVEL3 bo‘lmasa, kirishni taqiqlash
        if user.role == 'user3' and obj.degree != 'LEVEL3':
            messages.error(self.request, "Sizda ushbu risolani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Risola: {self.object.title}"
        return context


class U3DarslikListView(LoginRequiredMixin, ListView):
    model = Darslik
    template_name = 'kategoriya/users/Darsliklar/u3_darsliklar.html'
    context_object_name = 'darsliklar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        # User3 uchun faqat LEVEL3 darajali darsliklarni filtrlaymiz
        if user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Darsliklar Roʻyxati (User3)'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        darsliklar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(darsliklar, self.paginate_by)

        try:
            darsliklar = paginator.page(page)
        except PageNotAnInteger:
            darsliklar = paginator.page(1)
        except EmptyPage:
            darsliklar = paginator.page(paginator.num_pages)

        context['darsliklar'] = darsliklar
        return context


class U3DarslikDetailView(LoginRequiredMixin, DetailView):
    model = Darslik
    template_name = 'kategoriya/users/Darsliklar/u3_darsliklar_detail.html'
    context_object_name = 'darslik'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user3 va darslik LEVEL3 bo‘lmasa, kirishni taqiqlash
        if user.role == 'user3' and obj.degree != 'LEVEL3':
            messages.error(self.request, "Sizda ushbu darslikni ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Darslik: {self.object.title}"
        return context


class U3QollanmaListView(LoginRequiredMixin, ListView):
    model = Qollanma
    template_name = 'kategoriya/users/Qollanmalar/u3_qollanmalar.html'
    context_object_name = 'qollanmalar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        # User3 uchun faqat LEVEL3 darajali qo‘llanmalarni filtrlaymiz
        if user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Qo‘llanmalar Roʻyxati (User3)'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        qollanmalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(qollanmalar, self.paginate_by)

        try:
            qollanmalar = paginator.page(page)
        except PageNotAnInteger:
            qollanmalar = paginator.page(1)
        except EmptyPage:
            qollanmalar = paginator.page(paginator.num_pages)

        context['qollanmalar'] = qollanmalar
        return context


class U3QollanmaDetailView(LoginRequiredMixin, DetailView):
    model = Qollanma
    template_name = 'kategoriya/users/Qollanmalar/u3_qollanmalar_detail.html'
    context_object_name = 'qollanma'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user3 va qollanma LEVEL3 bo‘lmasa, kirishni taqiqlash
        if user.role == 'user3' and obj.degree != 'LEVEL3':
            messages.error(self.request, "Sizda ushbu qo‘llanmani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Qo‘llanma: {self.object.title}"
        return context


class U3LoyihaListView(LoginRequiredMixin, ListView):
    model = Loyiha
    template_name = 'kategoriya/users/Loyihalar/u3_loyihalar.html'
    context_object_name = 'loyihalar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        # User3 uchun faqat LEVEL3 darajali loyihalarni filtrlaymiz
        if user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Loyihalar Roʻyxati (User3)'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        loyihalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(loyihalar, self.paginate_by)

        try:
            loyihalar = paginator.page(page)
        except PageNotAnInteger:
            loyihalar = paginator.page(1)
        except EmptyPage:
            loyihalar = paginator.page(paginator.num_pages)

        context['loyihalar'] = loyihalar
        return context


class U3LoyihaDetailView(LoginRequiredMixin, DetailView):
    model = Loyiha
    template_name = 'kategoriya/users/Loyihalar/u3_loyihalar_detail.html'
    context_object_name = 'loyiha'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user3 va loyiha LEVEL3 bo‘lmasa, kirishni taqiqlash
        if user.role == 'user3' and obj.degree != 'LEVEL3':
            messages.error(self.request, "Sizda ushbu loyihani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Loyiha: {self.object.title}"
        return context


class U3JurnalListView(LoginRequiredMixin, ListView):
    model = Jurnal
    template_name = 'kategoriya/users/Jurnallar/u3_jurnallar.html'
    context_object_name = 'jurnallar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        # User3 uchun faqat LEVEL3 darajali jurnallarni filtrlaymiz
        if user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Jurnallar Roʻyxati (User3)'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        jurnallar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(jurnallar, self.paginate_by)

        try:
            jurnallar = paginator.page(page)
        except PageNotAnInteger:
            jurnallar = paginator.page(1)
        except EmptyPage:
            jurnallar = paginator.page(paginator.num_pages)

        context['jurnallar'] = jurnallar
        return context


class U3JurnalDetailView(LoginRequiredMixin, DetailView):
    model = Jurnal
    template_name = 'kategoriya/users/Jurnallar/u3_jurnallar_detail.html'
    context_object_name = 'jurnal'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user3 va jurnal LEVEL3 bo‘lmasa, kirishni taqiqlash
        if user.role == 'user3' and obj.degree != 'LEVEL3':
            messages.error(self.request, "Sizda ushbu jurnalni ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Jurnal: {self.object.title}"
        return context


class U3MaqolaListView(LoginRequiredMixin, ListView):
    model = Maqola
    template_name = 'kategoriya/users/Maqolalar/u3_maqolalar.html'
    context_object_name = 'maqolalar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        # User3 uchun faqat LEVEL3 darajali maqolalarni filtrlaymiz
        if user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Maqolalar Roʻyxati (User3)'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        maqolalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(maqolalar, self.paginate_by)

        try:
            maqolalar = paginator.page(page)
        except PageNotAnInteger:
            maqolalar = paginator.page(1)
        except EmptyPage:
            maqolalar = paginator.page(paginator.num_pages)

        context['maqolalar'] = maqolalar
        return context


class U3MaqolaDetailView(LoginRequiredMixin, DetailView):
    model = Maqola
    template_name = 'kategoriya/users/Maqolalar/u3_maqolalar_detail.html'
    context_object_name = 'maqola'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user3 va maqola LEVEL3 bo‘lmasa, kirishni taqiqlash
        if user.role == 'user3' and obj.degree != 'LEVEL3':
            messages.error(self.request, "Sizda ushbu maqolani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Maqola: {self.object.title}"
        return context


class U3TajribaListView(LoginRequiredMixin, ListView):
    model = Xorijiy_Tajriba
    template_name = 'kategoriya/users/Xorijiy_Tajribalar/u3_tajribalar.html'
    context_object_name = 'tajribalar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        # User3 uchun faqat LEVEL3 darajali tajribalarni filtrlaymiz
        if user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Xorijiy Tajribalar Roʻyxati (User3)'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        tajribalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(tajribalar, self.paginate_by)

        try:
            tajribalar = paginator.page(page)
        except PageNotAnInteger:
            tajribalar = paginator.page(1)
        except EmptyPage:
            tajribalar = paginator.page(paginator.num_pages)

        context['tajribalar'] = tajribalar
        return context


class U3TajribaDetailView(LoginRequiredMixin, DetailView):
    model = Xorijiy_Tajriba
    template_name = 'kategoriya/users/Xorijiy_Tajribalar/u3_tajriba_detail.html'
    context_object_name = 'tajriba'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user3 va tajriba LEVEL3 bo‘lmasa, kirishni taqiqlash
        if user.role == 'user3' and obj.degree != 'LEVEL3':
            messages.error(self.request, "Sizda ushbu tajribani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Xorijiy Tajriba: {self.object.title}"
        return context


class U3OtherListView(LoginRequiredMixin, ListView):
    model = Other
    template_name = 'kategoriya/users/Boshqalar/u3_otherlar.html'
    context_object_name = 'otherlar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        # User3 uchun faqat LEVEL3 darajali "Other" ma'lumotlarni filtrlaymiz
        if user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Boshqa Ma\'lumotlar Roʻyxati (User3)'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        otherlar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(otherlar, self.paginate_by)

        try:
            otherlar = paginator.page(page)
        except PageNotAnInteger:
            otherlar = paginator.page(1)
        except EmptyPage:
            otherlar = paginator.page(paginator.num_pages)

        context['otherlar'] = otherlar
        return context


class U3OtherDetailView(LoginRequiredMixin, DetailView):
    model = Other
    template_name = 'kategoriya/users/Boshqalar/u3_other_detail.html'
    context_object_name = 'other'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user3 va "Other" ma'lumot LEVEL3 bo‘lmasa, kirishni taqiqlash
        if user.role == 'user3' and obj.degree != 'LEVEL3':
            messages.error(self.request, "Sizda ushbu ma'lumotni ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Boshqa Ma'lumot: {self.object.title}"
        return context


class U2DissertatsiyaListView(LoginRequiredMixin, ListView):
    model = Dissertatsiya
    template_name = 'kategoriya/users/dissertatsiyalar/u2_dissertatsiyalar.html'
    context_object_name = 'dissertatsiyalar'
    paginate_by = 8  # Sahifalash soni

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        if user.role == 'user2':
            queryset = queryset.exclude(degree='LEVEL1')
        elif user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dissertatsiyalar Roʻyxati'
        context['search_query'] = self.request.GET.get('search', '')

        # Qo‘lda sahifalashni tekshirish
        dissertatsiyalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(dissertatsiyalar, self.paginate_by)

        try:
            dissertatsiyalar = paginator.page(page)
        except PageNotAnInteger:
            dissertatsiyalar = paginator.page(1)
        except EmptyPage:
            dissertatsiyalar = paginator.page(paginator.num_pages)

        context['dissertatsiyalar'] = dissertatsiyalar
        return context


class U2DissertatsiyaDetailView(LoginRequiredMixin, DetailView):
    model = Dissertatsiya
    template_name = 'kategoriya/users/dissertatsiyalar/u2_dissertatsiya_detail.html'
    context_object_name = 'dissertatsiya'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user2 va dissertatsiya LEVEL1 bo‘lsa, kirishni taqiqlash
        if user.role == 'user2' and obj.degree == 'LEVEL1':
            messages.error(self.request, "Sizda ushbu dissertatsiyani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Dissertatsiya: {self.object.title}"
        return context


class U2MonografiyaListView(LoginRequiredMixin, ListView):
    model = Monografiya
    template_name = 'kategoriya/users/monografiyalar/u2_monografiyalar.html'
    context_object_name = 'monografiyalar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        if user.role == 'user2':
            queryset = queryset.exclude(degree='LEVEL1')
        elif user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Monografiyalar Roʻyxati'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda tekshirish
        monografiyalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(monografiyalar, self.paginate_by)

        try:
            monografiyalar = paginator.page(page)
        except PageNotAnInteger:
            monografiyalar = paginator.page(1)
        except EmptyPage:
            monografiyalar = paginator.page(paginator.num_pages)

        context['monografiyalar'] = monografiyalar
        return context


class U2MonografiyaDetailView(LoginRequiredMixin, DetailView):
    model = Monografiya  # Dissertatsiya o‘rniga Monografiya
    template_name = 'kategoriya/users/monografiyalar/u2_monografiyalar_detail.html'  # Template yo‘li o‘zgartirildi
    context_object_name = 'monografiya'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user2 va monografiya LEVEL1 bo‘lsa, kirishni taqiqlash
        if user.role == 'user2' and obj.degree == 'LEVEL1':
            messages.error(self.request, "Sizda ushbu monografiyani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Monografiya: {self.object.title}"  # Sahifa sarlavhasi moslashtirildi
        return context


class U2RisolaListView(LoginRequiredMixin, ListView):
    model = Risola
    template_name = 'kategoriya/users/Kitob va Risola/u2_risolalar.html'
    context_object_name = 'risolalar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        if user.role == 'user2':
            queryset = queryset.exclude(degree='LEVEL1')
        elif user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Risolalar Roʻyxati'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda tekshirish
        risolalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(risolalar, self.paginate_by)

        try:
            risolalar = paginator.page(page)
        except PageNotAnInteger:
            risolalar = paginator.page(1)
        except EmptyPage:
            risolalar = paginator.page(paginator.num_pages)

        context['risolalar'] = risolalar
        return context


class U2RisolaDetailView(LoginRequiredMixin, DetailView):
    model = Risola  # Monografiya o‘rniga Risola
    template_name = 'kategoriya/users/Kitob va Risola/u2_risolalar_detail.html'  # Template yo‘li o‘zgartirildi
    context_object_name = 'risola'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user2 va risola LEVEL1 bo‘lsa, kirishni taqiqlash
        if user.role == 'user2' and obj.degree == 'LEVEL1':
            messages.error(self.request, "Sizda ushbu risolani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Risola: {self.object.title}"  # Sahifa sarlavhasi moslashtirildi
        return context


class U2DarslikListView(LoginRequiredMixin, ListView):
    model = Darslik
    template_name = 'kategoriya/users/Darsliklar/u2_darsliklar.html'
    context_object_name = 'darsliklar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        if user.role == 'user2':
            queryset = queryset.exclude(degree='LEVEL1')
        elif user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Darsliklar Roʻyxati'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        darsliklar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(darsliklar, self.paginate_by)

        try:
            darsliklar = paginator.page(page)
        except PageNotAnInteger:
            darsliklar = paginator.page(1)
        except EmptyPage:
            darsliklar = paginator.page(paginator.num_pages)

        context['darsliklar'] = darsliklar
        return context


class U2DarslikDetailView(LoginRequiredMixin, DetailView):
    model = Darslik  # Risola o‘rniga Darslik modeli
    template_name = 'kategoriya/users/Darsliklar/u2_darsliklar_detail.html'  # Template yo‘li o‘zgartirildi
    context_object_name = 'darslik'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user2 va darslik LEVEL1 bo‘lsa, kirishni taqiqlash
        if user.role == 'user2' and obj.degree == 'LEVEL1':
            messages.error(self.request, "Sizda ushbu darslikni ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Darslik: {self.object.title}"  # Sahifa sarlavhasi moslashtirildi
        return context


class U2QollanmaListView(LoginRequiredMixin, ListView):
    model = Qollanma  # Model o'zgartirildi
    template_name = 'kategoriya/users/Qollanmalar/u2_qollanmalar.html'  # Template yo‘li moslashtirildi
    context_object_name = 'qollanmalar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        if user.role == 'user2':
            queryset = queryset.exclude(degree='LEVEL1')
        elif user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Qo‘llanmalar Roʻyxati'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        qollanmalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(qollanmalar, self.paginate_by)

        try:
            qollanmalar = paginator.page(page)
        except PageNotAnInteger:
            qollanmalar = paginator.page(1)
        except EmptyPage:
            qollanmalar = paginator.page(paginator.num_pages)

        context['qollanmalar'] = qollanmalar
        return context


class U2QollanmaDetailView(LoginRequiredMixin, DetailView):
    model = Qollanma  # Darslik o‘rniga Qollanma modeli
    template_name = 'kategoriya/users/Qollanmalar/u2_qollanmalar_detail.html'  # Template yo‘li moslashtirildi
    context_object_name = 'qollanma'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user2 va qollanma LEVEL1 bo‘lsa, kirishni taqiqlash
        if user.role == 'user2' and obj.degree == 'LEVEL1':
            messages.error(self.request, "Sizda ushbu qo‘llanmani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Qo‘llanma: {self.object.title}"  # Sahifa sarlavhasi moslashtirildi
        return context


class U2LoyihaListView(LoginRequiredMixin, ListView):
    model = Loyiha  # Qollanma o‘rniga Loyiha modeli
    template_name = 'kategoriya/users/Loyihalar/u2_loyihalar.html'  # Template yo‘li moslashtirildi
    context_object_name = 'loyihalar'
    paginate_by = 8  # Sahifalash uchun

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        if user.role == 'user2':
            queryset = queryset.exclude(degree='LEVEL1')
        elif user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Loyihalar Roʻyxati'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        loyihalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(loyihalar, self.paginate_by)

        try:
            loyihalar = paginator.page(page)
        except PageNotAnInteger:
            loyihalar = paginator.page(1)
        except EmptyPage:
            loyihalar = paginator.page(paginator.num_pages)

        context['loyihalar'] = loyihalar
        return context


class U2LoyihaDetailView(LoginRequiredMixin, DetailView):
    model = Loyiha  # Qollanma o‘rniga Loyiha modeli
    template_name = 'kategoriya/users/Loyihalar/u2_loyihalar_detail.html'  # Template yo‘li o‘zgartirildi
    context_object_name = 'loyiha'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user2 va loyiha LEVEL1 bo‘lsa, kirishni taqiqlash
        if user.role == 'user2' and obj.degree == 'LEVEL1':
            messages.error(self.request, "Sizda ushbu loyihani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Loyiha: {self.object.title}"  # Sahifa sarlavhasi moslashtirildi
        return context


class U2JurnalListView(LoginRequiredMixin, ListView):
    model = Jurnal  # Loyiha o‘rniga Jurnal modeli
    template_name = 'kategoriya/users/Jurnallar/u2_jurnallar.html'  # Template yo‘li moslashtirildi
    context_object_name = 'jurnallar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        if user.role == 'user2':
            queryset = queryset.exclude(degree='LEVEL1')
        elif user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Jurnallar Roʻyxati'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        jurnallar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(jurnallar, self.paginate_by)

        try:
            jurnallar = paginator.page(page)
        except PageNotAnInteger:
            jurnallar = paginator.page(1)
        except EmptyPage:
            jurnallar = paginator.page(paginator.num_pages)

        context['jurnallar'] = jurnallar
        return context


class U2JurnalDetailView(LoginRequiredMixin, DetailView):
    model = Jurnal  # Loyiha o‘rniga Jurnal modeli
    template_name = 'kategoriya/users/Jurnallar/u2_jurnallar_detail.html'  # Template yo‘li moslashtirildi
    context_object_name = 'jurnal'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user2 va jurnal LEVEL1 bo‘lsa, kirishni taqiqlash
        if user.role == 'user2' and obj.degree == 'LEVEL1':
            messages.error(self.request, "Sizda ushbu jurnalni ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Jurnal: {self.object.title}"  # Sahifa sarlavhasi moslashtirildi
        return context


class U2MaqolaListView(LoginRequiredMixin, ListView):
    model = Maqola  # Jurnal o‘rniga Maqola modeli
    template_name = 'kategoriya/users/Maqolalar/u2_maqolalar.html'  # Template yo‘li moslashtirildi
    context_object_name = 'maqolalar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        if user.role == 'user2':
            queryset = queryset.exclude(degree='LEVEL1')
        elif user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Maqolalar Roʻyxati'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        maqolalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(maqolalar, self.paginate_by)

        try:
            maqolalar = paginator.page(page)
        except PageNotAnInteger:
            maqolalar = paginator.page(1)
        except EmptyPage:
            maqolalar = paginator.page(paginator.num_pages)

        context['maqolalar'] = maqolalar
        return context


class U2MaqolaDetailView(LoginRequiredMixin, DetailView):
    model = Maqola  # Jurnal o‘rniga Maqola modeli
    template_name = 'kategoriya/users/Maqolalar/u2_maqolalar_detail.html'  # Template yo‘li moslashtirildi
    context_object_name = 'maqola'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user2 va maqola LEVEL1 bo‘lsa, kirishni taqiqlash
        if user.role == 'user2' and obj.degree == 'LEVEL1':
            messages.error(self.request, "Sizda ushbu maqolani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Maqola: {self.object.title}"  # Sahifa sarlavhasi moslashtirildi
        return context


class U2TajribaListView(LoginRequiredMixin, ListView):
    model = Xorijiy_Tajriba  # Maqola o‘rniga Tajriba modeli
    template_name = 'kategoriya/users/Xorijiy_Tajribalar/u2_tajribalar.html'  # Template yo‘li moslashtirildi
    context_object_name = 'tajribalar'
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        if user.role == 'user2':
            queryset = queryset.exclude(degree='LEVEL1')
        elif user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tajribalar Roʻyxati'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        tajribalar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(tajribalar, self.paginate_by)

        try:
            tajribalar = paginator.page(page)
        except PageNotAnInteger:
            tajribalar = paginator.page(1)
        except EmptyPage:
            tajribalar = paginator.page(paginator.num_pages)

        context['tajribalar'] = tajribalar
        return context


class U2TajribaDetailView(LoginRequiredMixin, DetailView):
    model = Xorijiy_Tajriba  # Maqola o‘rniga Tajriba modeli
    template_name = 'kategoriya/users/Xorijiy_Tajribalar/u2_tajriba_detail.html'  # Template yo‘li moslashtirildi
    context_object_name = 'tajriba'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user2 va tajriba LEVEL1 bo‘lsa, kirishni taqiqlash
        if user.role == 'user2' and obj.degree == 'LEVEL1':
            messages.error(self.request, "Sizda ushbu tajribani ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Tajriba: {self.object.title}"  # Sahifa sarlavhasi moslashtirildi
        return context


class U2OtherListView(LoginRequiredMixin, ListView):
    model = Other  # Other modeli
    template_name = 'kategoriya/users/Boshqalar/u2_otherlar.html'  # Template yo‘li moslashtirildi
    context_object_name = 'otherlar'  # TO'G'RILANDI
    paginate_by = 8

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '').strip()

        if user.role == 'user2':
            queryset = queryset.exclude(degree='LEVEL1')
        elif user.role == 'user3':
            queryset = queryset.filter(degree='LEVEL3')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(institution_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Other Roʻyxati'
        context['search_query'] = self.request.GET.get('search', '')

        # Sahifalashni qo‘lda qo‘shish
        otherlar = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(otherlar, self.paginate_by)

        try:
            otherlar = paginator.page(page)
        except PageNotAnInteger:
            otherlar = paginator.page(1)
        except EmptyPage:
            otherlar = paginator.page(paginator.num_pages)

        context['otherlar'] = otherlar  # TO'G'RILANDI
        return context


class U2OtherDetailView(LoginRequiredMixin, DetailView):
    model = Other  # Maqola o‘rniga Other modeli
    template_name = 'kategoriya/users/Boshqalar/u2_other_detail.html'  # Template yo‘li moslashtirildi
    context_object_name = 'other'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        # Agar user2 va other LEVEL1 bo‘lsa, kirishni taqiqlash
        if user.role == 'user2' and obj.degree == 'LEVEL1':
            messages.error(self.request, "Sizda ushbu ma'lumotni ko‘rish huquqi yo‘q.")
            return redirect(reverse('allow'))  # 'allow' sahifasiga yo‘naltirish

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Other: {self.object.title}"  # Sahifa sarlavhasi moslashtirildi
        return context


# Pagination va qidiruv uchun umumiy funksiya
def paginate_and_filter(request, queryset, limit_default=10, search_fields=None):
    limit = request.GET.get("limit", limit_default)
    page = request.GET.get("page", 1)
    search = request.GET.get("search", "").strip()

    try:
        limit = int(limit)
        if limit <= 0:
            limit = limit_default
    except ValueError:
        limit = limit_default

    if search and search_fields:
        q_objects = Q()
        for field in search_fields:
            q_objects |= Q(**{f"{field}__icontains": search})
        queryset = queryset.filter(q_objects)

    queryset = queryset.order_by("-created_at")
    paginator = Paginator(queryset, limit)
    paginated_items = paginator.get_page(page)

    return {
        "items": paginated_items,
        "total_pages": paginator.num_pages,
        "search_query": search,
    }


# Umumiy CRUD operatsiyalari uchun yordamchi funksiyalar
@csrf_exempt
def handle_create(request, form_class, redirect_name, publication_type=None, user=None):
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, user=user)
        if form.is_valid():
            instance = form.save(commit=False)
            if user:
                instance.user = user
            if publication_type:
                instance.publication_type = publication_type
            instance.save()
            request.session['success'] = f"{publication_type or 'Obyekt'} muvaffaqiyatli qo‘shildi!"
            return redirect(redirect_name)
    return redirect(redirect_name)


@csrf_exempt
def handle_edit(request, model_class, instance_id, form_class, redirect_name, user=None):
    instance = get_object_or_404(model_class, id=instance_id)
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance, user=user)
        if form.is_valid():
            updated_instance = form.save(commit=False)
            if not request.FILES.get('file'):
                updated_instance.file = instance.file
            if not request.FILES.get('image'):
                updated_instance.image = instance.image
            updated_instance.save()
            request.session['success'] = f"{model_class._meta.model_name.capitalize()} muvaffaqiyatli yangilandi!"
            return redirect(redirect_name)
    return redirect(redirect_name)


@require_POST
def handle_delete(request, model_class, instance_id, redirect_name):
    instance = get_object_or_404(model_class, id=instance_id)
    instance.delete()
    request.session['success'] = f"{model_class._meta.model_name.capitalize()} muvaffaqiyatli o‘chirildi!"
    return redirect(redirect_name)


# Umumiy list va detail funksiyasi
def resource_list(request, model_class, form_class, template, limit_default=10, search_fields=None, user=None,
                  moderator_filter=False):
    queryset = model_class.objects.all()
    if moderator_filter and request.user.role == 'moderator' and request.user.branch:
        queryset = queryset.filter(branch=request.user.branch)

    pagination_data = paginate_and_filter(request, queryset, limit_default, search_fields)
    form = form_class(user=user) if user else form_class()

    if request.method == "POST" and user:
        form = form_class(request.POST, request.FILES, user=user)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            request.session['success'] = f"{model_class._meta.model_name.capitalize()} muvaffaqiyatli qo'shildi!"
            return redirect(request.path_info)

    context = {
        model_class._meta.model_name + "lar": pagination_data["items"],
        "branches": Branch.objects.filter(
            id=request.user.branch.id) if moderator_filter and request.user.role == 'moderator' and request.user.branch else Branch.objects.all(),
        "success_message": request.session.pop('success', None),
        "form": form,
        "total_pages": pagination_data["total_pages"],
        "search_query": pagination_data["search_query"],
    }
    return render(request, template, context)


def resource_detail(request, model_class, instance_id, form_class, template, user=None):
    instance = get_object_or_404(model_class, id=instance_id)
    form = form_class(instance=instance, user=user) if user else form_class(instance=instance)
    return render(request, template, {
        model_class._meta.model_name: instance,
        "form": form,
    })


# Kategoriya
@csrf_exempt
def category_list(request):
    return render(request, 'kategoriya/admin/category.html')


@role_required('moderator')
@csrf_exempt
def m_category_list(request):
    return render(request, 'kategoriya/moderator/m_category.html')


# Dissertatsiya
@csrf_exempt
def dissertatsiya_list(request):
    return resource_list(
        request, Dissertatsiya, DissertatsiyaForm, 'kategoriya/admin/dissertatsiya.html',
        search_fields=['title', 'author', 'institution_name']
    )


@role_required('moderator')
@csrf_exempt
def m_dissertatsiya_list(request):
    if not request.user.branch:
        return HttpResponseForbidden("Moderator uchun branch belgilanmagan.")
    return resource_list(
        request, Dissertatsiya, DissertatsiyaForm, 'kategoriya/moderator/m_dissertatsiya.html',
        search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


@role_required('moderator', 'administrator', 'user1', 'user2', 'user3')
@csrf_exempt
def u1_dissertatsiya_list(request):
    return resource_list(
        request, Dissertatsiya, DissertatsiyaForm, 'kategoriya/users/dissertatsiyalar/u_dissertatsiyalar.html',
        limit_default=8, search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


def u1_dissertatsiya_detail(request, dissertatsiya_id):
    return resource_detail(
        request, Dissertatsiya, dissertatsiya_id, DissertatsiyaForm,
        'kategoriya/users/dissertatsiyalar/u_dissertatsiyalar_detail.html', user=request.user
    )


@csrf_exempt
def dissertatsiya_create(request):
    return handle_create(request, DissertatsiyaForm, 'dissertatsiya_list', 'Dissertatsiya')


@csrf_exempt
def m_dissertatsiya_create(request):
    return handle_create(request, DissertatsiyaForm, 'm_dissertatsiya_list', 'Dissertatsiya', user=request.user)


@csrf_exempt
def dissertatsiya_edit(request, dissertatsiya_id):
    return handle_edit(request, Dissertatsiya, dissertatsiya_id, DissertatsiyaForm, 'dissertatsiya_list')


@csrf_exempt
def m_dissertatsiya_edit(request, dissertatsiya_id):
    return handle_edit(request, Dissertatsiya, dissertatsiya_id, DissertatsiyaForm, 'm_dissertatsiya_list',
                       user=request.user)


def dissertatsiya_delete(request, dissertatsiya_id):
    return handle_delete(request, Dissertatsiya, dissertatsiya_id, 'dissertatsiya_list')


def m_dissertatsiya_delete(request, dissertatsiya_id):
    return handle_delete(request, Dissertatsiya, dissertatsiya_id, 'm_dissertatsiya_list')


# Monografiya
@csrf_exempt
def monografiya_list(request):
    return resource_list(
        request, Monografiya, MonografiyaForm, 'kategoriya/admin/monografiya.html',
        search_fields=['title', 'author', 'institution_name']
    )


@role_required('moderator')
@csrf_exempt
def m_monografiya_list(request):
    if not request.user.branch:
        return HttpResponseForbidden("Moderator uchun branch belgilanmagan.")
    return resource_list(
        request, Monografiya, MonografiyaForm, 'kategoriya/moderator/m_monografiya.html',
        search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


@role_required('moderator', 'administrator', 'user1', 'user2', 'user3')
@csrf_exempt
def u1_monografiya_list(request):
    return resource_list(
        request, Monografiya, MonografiyaForm, 'kategoriya/users/monografiyalar/u_monografiyalar.html',
        limit_default=8, search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


def u1_monografiya_detail(request, monografiya_id):
    return resource_detail(
        request, Monografiya, monografiya_id, MonografiyaForm,
        'kategoriya/users/monografiyalar/u1_monografiyalar_detail.html', user=request.user
    )


@csrf_exempt
def monografiya_create(request):
    return handle_create(request, MonografiyaForm, 'monografiya_list', 'Monografiya')


@csrf_exempt
def m_monografiya_create(request):
    return handle_create(request, MonografiyaForm, 'm_monografiya_list', 'Monografiya', user=request.user)


@csrf_exempt
def monografiya_edit(request, monografiya_id):
    return handle_edit(request, Monografiya, monografiya_id, MonografiyaForm, 'monografiya_list')


@csrf_exempt
def m_monografiya_edit(request, monografiya_id):
    return handle_edit(request, Monografiya, monografiya_id, MonografiyaForm, 'm_monografiya_list', user=request.user)


def monografiya_delete(request, monografiya_id):
    return handle_delete(request, Monografiya, monografiya_id, 'monografiya_list')


def m_monografiya_delete(request, monografiya_id):
    return handle_delete(request, Monografiya, monografiya_id, 'm_monografiya_list')


# Risola
@csrf_exempt
def risola_list(request):
    return resource_list(
        request, Risola, RisolaForm, 'kategoriya/admin/Kitob_Risola.html',
        search_fields=['title', 'author', 'institution_name']
    )


@role_required('moderator')
@csrf_exempt
def m_risola_list(request):
    if not request.user.branch:
        return HttpResponseForbidden("Moderator uchun branch belgilanmagan.")
    return resource_list(
        request, Risola, RisolaForm, 'kategoriya/moderator/m_Kitob_Risola.html',
        search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


@role_required('moderator', 'administrator', 'user1', 'user2', 'user3')
@csrf_exempt
def u1_risola_list(request):
    return resource_list(
        request, Risola, RisolaForm, 'kategoriya/users/Kitob va Risola/u1_risolalar.html',
        limit_default=8, search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


def u1_risola_detail(request, risola_id):
    return resource_detail(
        request, Risola, risola_id, RisolaForm,
        'kategoriya/users/Kitob va Risola/u1_risolalar_detail.html', user=request.user
    )


@csrf_exempt
def risola_create(request):
    return handle_create(request, RisolaForm, 'risola_list', 'risola')


@csrf_exempt
def m_risola_create(request):
    return handle_create(request, RisolaForm, 'm_risola_list', 'risola', user=request.user)


@csrf_exempt
def risola_edit(request, risola_id):
    return handle_edit(request, Risola, risola_id, RisolaForm, 'risola_list')


@csrf_exempt
def m_risola_edit(request, risola_id):
    return handle_edit(request, Risola, risola_id, RisolaForm, 'm_risola_list', user=request.user)


def risola_delete(request, risola_id):
    return handle_delete(request, Risola, risola_id, 'risola_list')


def m_risola_delete(request, risola_id):
    return handle_delete(request, Risola, risola_id, 'm_risola_list')


# Darslik
@csrf_exempt
def darslik_list(request):
    return resource_list(
        request, Darslik, DarslikForm, 'kategoriya/admin/Darslik.html',
        search_fields=['title', 'author', 'institution_name']
    )


@role_required('moderator')
@csrf_exempt
def m_darslik_list(request):
    if not request.user.branch:
        return HttpResponseForbidden("Moderator uchun branch belgilanmagan.")
    return resource_list(
        request, Darslik, DarslikForm, 'kategoriya/moderator/m_Darslik.html',
        search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


@role_required('moderator', 'administrator', 'user1', 'user2', 'user3')
@csrf_exempt
def u1_darslik_list(request):
    return resource_list(
        request, Darslik, DarslikForm, 'kategoriya/users/Darsliklar/u1_darsliklar.html',
        limit_default=8, search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


def u1_darslik_detail(request, darslik_id):
    return resource_detail(
        request, Darslik, darslik_id, DarslikForm,
        'kategoriya/users/Darsliklar/u1_darsliklar_detail.html', user=request.user
    )


@csrf_exempt
def darslik_create(request):
    return handle_create(request, DarslikForm, 'darslik_list', 'darslik')


@csrf_exempt
def m_darslik_create(request):
    return handle_create(request, DarslikForm, 'm_darslik_list', 'darslik', user=request.user)


@csrf_exempt
def darslik_edit(request, darslik_id):
    return handle_edit(request, Darslik, darslik_id, DarslikForm, 'darslik_list')


@csrf_exempt
def m_darslik_edit(request, darslik_id):
    return handle_edit(request, Darslik, darslik_id, DarslikForm, 'm_darslik_list', user=request.user)


def darslik_delete(request, darslik_id):
    return handle_delete(request, Darslik, darslik_id, 'darslik_list')


def m_darslik_delete(request, darslik_id):
    return handle_delete(request, Darslik, darslik_id, 'm_darslik_list')


# Qollanma
@csrf_exempt
def qollanma_list(request):
    return resource_list(
        request, Qollanma, QollanmaForm, 'kategoriya/admin/Qollanma.html',
        search_fields=['title', 'author', 'institution_name']
    )


@role_required('moderator', 'administrator')
@csrf_exempt
def m_qollanma_list(request):
    if request.user.role == 'moderator' and not request.user.branch:
        return HttpResponseForbidden("Moderator uchun branch belgilanmagan.")
    return resource_list(
        request, Qollanma, QollanmaForm, 'kategoriya/moderator/m_Qollanma.html',
        search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


@role_required('moderator', 'administrator', 'user1', 'user2', 'user3')
@csrf_exempt
def u1_qollanma_list(request):
    return resource_list(
        request, Qollanma, QollanmaForm, 'kategoriya/users/Qollanmalar/u1_qollanmalar.html',
        limit_default=8, search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


def u1_qollanma_detail(request, qollanma_id):
    return resource_detail(
        request, Qollanma, qollanma_id, QollanmaForm,
        'kategoriya/users/Qollanmalar/u1_qollanmalar_detail.html', user=request.user
    )


@csrf_exempt
def qollanma_create(request):
    return handle_create(request, QollanmaForm, 'qollanma_list', 'qollanma')


@csrf_exempt
def m_qollanma_create(request):
    return handle_create(request, QollanmaForm, 'm_qollanma_list', 'qollanma', user=request.user)


@csrf_exempt
def qollanma_edit(request, qollanma_id):
    return handle_edit(request, Qollanma, qollanma_id, QollanmaForm, 'qollanma_list')


@csrf_exempt
def m_qollanma_edit(request, qollanma_id):
    return handle_edit(request, Qollanma, qollanma_id, QollanmaForm, 'm_qollanma_list', user=request.user)


def qollanma_delete(request, qollanma_id):
    return handle_delete(request, Qollanma, qollanma_id, 'qollanma_list')


def m_qollanma_delete(request, qollanma_id):
    return handle_delete(request, Qollanma, qollanma_id, 'm_qollanma_list')


# Loyiha
@csrf_exempt
def loyiha_list(request):
    return resource_list(
        request, Loyiha, LoyihaForm, 'kategoriya/admin/Ilmiy Loyiha.html',
        search_fields=['title', 'description']
    )


@role_required('moderator', 'administrator')
@csrf_exempt
def m_loyiha_list(request):
    if request.user.role == 'moderator' and not request.user.branch:
        return HttpResponseForbidden("Moderator uchun branch belgilanmagan.")
    return resource_list(
        request, Loyiha, LoyihaForm, 'kategoriya/moderator/m_Ilmiy Loyiha.html',
        search_fields=['title', 'description'], user=request.user, moderator_filter=True
    )


@role_required('moderator', 'administrator', 'user1', 'user2', 'user3')
@csrf_exempt
def u1_loyiha_list(request):
    return resource_list(
        request, Loyiha, LoyihaForm, 'kategoriya/users/Loyihalar/u1_loyihalar.html',
        limit_default=8, search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


def u1_loyiha_detail(request, loyiha_id):
    return resource_detail(
        request, Loyiha, loyiha_id, LoyihaForm,
        'kategoriya/users/Loyihalar/u1_loyihalar_detail.html', user=request.user
    )


@csrf_exempt
def loyiha_create(request):
    return handle_create(request, LoyihaForm, 'loyiha_list', 'loyiha')


@csrf_exempt
def m_loyiha_create(request):
    return handle_create(request, LoyihaForm, 'm_loyiha_list', 'loyiha', user=request.user)


@csrf_exempt
def loyiha_edit(request, loyiha_id):
    return handle_edit(request, Loyiha, loyiha_id, LoyihaForm, 'loyiha_list')


@csrf_exempt
def m_loyiha_edit(request, loyiha_id):
    return handle_edit(request, Loyiha, loyiha_id, LoyihaForm, 'm_loyiha_list', user=request.user)


def loyiha_delete(request, loyiha_id):
    return handle_delete(request, Loyiha, loyiha_id, 'loyiha_list')


def m_loyiha_delete(request, loyiha_id):
    return handle_delete(request, Loyiha, loyiha_id, 'm_loyiha_list')


# Jurnal
@csrf_exempt
def jurnal_list(request):
    return resource_list(
        request, Jurnal, JurnalForm, 'kategoriya/admin/ilmiy Jurnallar.html',
        search_fields=['title', 'author', 'institution_name']
    )


@role_required('moderator', 'administrator')
@csrf_exempt
def m_jurnal_list(request):
    if request.user.role == 'moderator' and not request.user.branch:
        return HttpResponseForbidden("Moderator uchun branch belgilanmagan.")
    return resource_list(
        request, Jurnal, JurnalForm, 'kategoriya/moderator/m_ilmiy Jurnallar.html',
        search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


@role_required('moderator', 'administrator', 'user1', 'user2', 'user3')
@csrf_exempt
def u1_jurnal_list(request):
    return resource_list(
        request, Jurnal, JurnalForm, 'kategoriya/users/Jurnallar/u1_jurnallar.html',
        limit_default=8, search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


def u1_jurnal_detail(request, jurnal_id):
    return resource_detail(
        request, Jurnal, jurnal_id, JurnalForm,
        'kategoriya/users/Jurnallar/u1_jurnallar_detail.html', user=request.user
    )


@csrf_exempt
def jurnal_create(request):
    return handle_create(request, JurnalForm, 'jurnal_list', 'jurnal')


@csrf_exempt
def m_jurnal_create(request):
    return handle_create(request, JurnalForm, 'm_jurnal_list', 'jurnal', user=request.user)


@csrf_exempt
def jurnal_edit(request, jurnal_id):
    return handle_edit(request, Jurnal, jurnal_id, JurnalForm, 'jurnal_list')


@csrf_exempt
def m_jurnal_edit(request, jurnal_id):
    return handle_edit(request, Jurnal, jurnal_id, JurnalForm, 'm_jurnal_list', user=request.user)


def jurnal_delete(request, jurnal_id):
    return handle_delete(request, Jurnal, jurnal_id, 'jurnal_list')


def m_jurnal_delete(request, jurnal_id):
    return handle_delete(request, Jurnal, jurnal_id, 'm_jurnal_list')


# Maqola
@csrf_exempt
def maqola_list(request):
    return resource_list(
        request, Maqola, MaqolaForm, 'kategoriya/admin/Ilmiy Maqola.html',
        search_fields=['title', 'author', 'institution_name']
    )


@role_required('moderator', 'administrator')
@csrf_exempt
def m_maqola_list(request):
    if request.user.role == 'moderator' and not request.user.branch:
        return HttpResponseForbidden("Moderator uchun branch belgilanmagan.")
    return resource_list(
        request, Maqola, MaqolaForm, 'kategoriya/moderator/m_Ilmiy Maqola.html',
        search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


@role_required('moderator', 'administrator', 'user1', 'user2', 'user3')
@csrf_exempt
def u1_maqola_list(request):
    return resource_list(
        request, Maqola, MaqolaForm, 'kategoriya/users/Maqolalar/u1_maqolalar.html',
        limit_default=8, search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


def u1_maqola_detail(request, maqola_id):
    return resource_detail(
        request, Maqola, maqola_id, MaqolaForm,
        'kategoriya/users/Maqolalar/u1_maqolalar_detail.html', user=request.user
    )


@csrf_exempt
def maqola_create(request):
    return handle_create(request, MaqolaForm, 'maqola_list', 'maqola')


@csrf_exempt
def m_maqola_create(request):
    return handle_create(request, MaqolaForm, 'm_maqola_list', 'maqola', user=request.user)


@csrf_exempt
def maqola_edit(request, maqola_id):
    return handle_edit(request, Maqola, maqola_id, MaqolaForm, 'maqola_list')


@csrf_exempt
def m_maqola_edit(request, maqola_id):
    return handle_edit(request, Maqola, maqola_id, MaqolaForm, 'm_maqola_list', user=request.user)


def maqola_delete(request, maqola_id):
    return handle_delete(request, Maqola, maqola_id, 'maqola_list')


def m_maqola_delete(request, maqola_id):
    return handle_delete(request, Maqola, maqola_id, 'm_maqola_list')


# Other
@csrf_exempt
def other_list(request):
    return resource_list(
        request, Other, OtherForm, 'kategoriya/admin/Boshqalar.html',
        search_fields=['title', 'author', 'institution_name']
    )


@role_required('moderator', 'administrator')
@csrf_exempt
def m_other_list(request):
    if request.user.role == 'moderator' and not request.user.branch:
        return HttpResponseForbidden("Moderator uchun branch belgilanmagan.")
    return resource_list(
        request, Other, OtherForm, 'kategoriya/moderator/m_Boshqalar.html',
        search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


@role_required('moderator', 'administrator', 'user1', 'user2', 'user3')
@csrf_exempt
def u1_other_list(request):
    return resource_list(
        request, Other, OtherForm, 'kategoriya/users/Boshqalar/u1_otherlar.html',
        limit_default=8, search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


def u1_other_detail(request, other_id):
    return resource_detail(
        request, Other, other_id, OtherForm,
        'kategoriya/users/Boshqalar/u1_other_detail.html', user=request.user
    )


@csrf_exempt
def other_create(request):
    return handle_create(request, OtherForm, 'other_list', 'otherlar')


@csrf_exempt
def m_other_create(request):
    return handle_create(request, OtherForm, 'm_other_list', 'otherlar', user=request.user)


@csrf_exempt
def other_edit(request, other_id):
    return handle_edit(request, Other, other_id, OtherForm, 'other_list')


@csrf_exempt
def m_other_edit(request, other_id):
    return handle_edit(request, Other, other_id, OtherForm, 'm_other_list', user=request.user)


def other_delete(request, other_id):
    return handle_delete(request, Other, other_id, 'other_list')


def m_other_delete(request, other_id):
    return handle_delete(request, Other, other_id, 'm_other_list')


# Xorijiy Tajriba
@csrf_exempt
def tajriba_list(request):
    pagination_data = paginate_and_filter(
        request, Xorijiy_Tajriba.objects.all().order_by('-Military_organization'),
        search_fields=['title', 'author', 'Military_organization']
    )
    return render(request, 'kategoriya/admin/Xorijiy tajribalar.html', {
        'tajribalar': pagination_data["items"],
        'branches': Branch.objects.all(),
        'success_message': request.session.pop('success', None),
        'form': XorijiyTajribaForm(),
        'total_pages': pagination_data["total_pages"],
        'search_query': pagination_data["search_query"],
    })


@role_required('moderator', 'administrator')
@csrf_exempt
def m_tajriba_list(request):
    if request.user.role == 'moderator' and not request.user.branch:
        return HttpResponseForbidden("Moderator uchun branch belgilanmagan.")
    queryset = Xorijiy_Tajriba.objects.filter(
        branch=request.user.branch) if request.user.role == 'moderator' else Xorijiy_Tajriba.objects.all()
    pagination_data = paginate_and_filter(
        request, queryset.order_by('-Military_organization'),
        search_fields=['title', 'author', 'Military_organization']
    )
    return render(request, 'kategoriya/moderator/m_Xorijiy tajribalar.html', {
        'tajribalar': pagination_data["items"],
        'branches': Branch.objects.filter(
            id=request.user.branch.id) if request.user.role == 'moderator' and request.user.branch else Branch.objects.all(),
        'success_message': request.session.pop('success', None),
        'form': XorijiyTajribaForm(user=request.user),
        'total_pages': pagination_data["total_pages"],
        'search_query': pagination_data["search_query"],
    })


@role_required('moderator', 'administrator', 'user1', 'user2', 'user3')
@csrf_exempt
def u1_tajriba_list(request):
    return resource_list(
        request, Xorijiy_Tajriba, XorijiyTajribaForm, 'kategoriya/users/Xorijiy_Tajribalar/u1_tajribalar.html',
        limit_default=8, search_fields=['title', 'author', 'institution_name'], user=request.user, moderator_filter=True
    )


def u1_tajriba_detail(request, tajriba_id):
    return resource_detail(
        request, Xorijiy_Tajriba, tajriba_id, XorijiyTajribaForm,
        'kategoriya/users/Xorijiy_Tajribalar/u1_tajriba_detail.html', user=request.user
    )


@csrf_exempt
def tajriba_create(request):
    return handle_create(request, XorijiyTajribaForm, 'tajriba_list', 'tajriba')


@csrf_exempt
def m_tajriba_create(request):
    return handle_create(request, XorijiyTajribaForm, 'm_tajriba_list', 'tajriba', user=request.user)


@csrf_exempt
def tajriba_edit(request, tajriba_id):
    return handle_edit(request, Xorijiy_Tajriba, tajriba_id, XorijiyTajribaForm, 'tajriba_list')


@csrf_exempt
def m_tajriba_edit(request, tajriba_id):
    return handle_edit(request, Xorijiy_Tajriba, tajriba_id, XorijiyTajribaForm, 'm_tajriba_list', user=request.user)


def tajriba_delete(request, tajriba_id):
    return handle_delete(request, Xorijiy_Tajriba, tajriba_id, 'tajriba_list')


def m_tajriba_delete(request, tajriba_id):
    return handle_delete(request, Xorijiy_Tajriba, tajriba_id, 'm_tajriba_list')
