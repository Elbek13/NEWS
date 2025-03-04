from django import forms
from .models import Monografiya, Risola, Dissertatsiya, Darslik, Loyiha, Jurnal, Maqola, Xorijiy_Tajriba, Qollanma, \
    Other, BaseModel, Branch


class BaseModelForm(forms.ModelForm):
    """Base form for models with file and text fields."""

    class Meta:
        model = BaseModel
        fields = [
            'branch', 'user', 'title', 'author', 'institution_name', 'keywords', 'publication_type', 'publication_year',
            'description', 'content_type', 'degree', 'issn_isbn', 'file', 'image', 'slug'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'institution_name': forms.TextInput(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_type': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'degree': forms.Select(attrs={'class': 'form-select'}),
            'issn_isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file and file.size > 20 * 1024 * 1024:  # Limit to 10 MB
            raise forms.ValidationError("Fayl hajmi 10MB dan oshmasligi kerak.")
        return file

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 10 * 1024 * 1024:  # Limit image size to 5 MB
            raise forms.ValidationError("Rasm hajmi 5MB dan oshmasligi kerak.")
        return image


class RisolaForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = Risola
        fields = BaseModelForm.Meta.fields

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Har bir maydonni majburiy emas qilib qo'yamiz
        for field in self.fields:
            self.fields[field].required = False

        # Faqat moderatorlar uchun o'z filialini ko'rsatamiz
        if user and hasattr(user, 'role') and user.role == 'moderator' and user.branch:
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['branch'].initial = user.branch
            self.fields['branch'].widget.attrs['readonly'] = True  # O‘zgartirib bo‘lmasligi uchun readonly
        else:
            self.fields['branch'].queryset = Branch.objects.all()


class MonografiyaForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = Monografiya
        fields = BaseModelForm.Meta.fields

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Har bir maydonni majburiy emas qilib qo'yamiz
        for field in self.fields:
            self.fields[field].required = False

        # Faqat moderatorlar uchun o'z filialini ko'rsatamiz
        if user and hasattr(user, 'role') and user.role == 'moderator' and user.branch:
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['branch'].initial = user.branch
            self.fields['branch'].widget.attrs['readonly'] = True  # O‘zgartirib bo‘lmasligi uchun readonly
        else:
            self.fields['branch'].queryset = Branch.objects.all()


class DissertatsiyaForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = Dissertatsiya
        fields = BaseModelForm.Meta.fields

    def __init__(self, *args, **kwargs):
        # Foydalanuvchi argument sifatida qabul qilinadi
        user = kwargs.pop('user', None)  # kwargs dan user olamiz va olib tashlaymiz
        super().__init__(*args, **kwargs)

        # Har bir maydonni required=False qilamiz
        for field in self.fields:
            self.fields[field].required = False

        # Agar foydalanuvchi moderator bo‘lsa va branch mavjud bo‘lsa
        if user and hasattr(user, 'role') and user.role == 'moderator' and user.branch:
            # branch maydonini faqat moderatorning o‘z branchi bilan cheklaymiz
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['branch'].initial = user.branch  # Moderatorning branchini standart qiymat qilamiz
            self.fields['branch'].widget.attrs['readonly'] = True  # O‘zgartirib bo‘lmasligi uchun readonly qilamiz
        else:
            # Agar moderator bo‘lmasa, barcha branchlarni ko‘rsatamiz
            self.fields['branch'].queryset = Branch.objects.all()


class DarslikForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = Darslik
        fields = BaseModelForm.Meta.fields

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Har bir maydonni majburiy emas qilib qo'yamiz
        for field in self.fields:
            self.fields[field].required = False

        # Faqat moderatorlar uchun o'z filialini ko'rsatamiz
        if user and hasattr(user, 'role') and user.role == 'moderator' and user.branch:
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['branch'].initial = user.branch
            self.fields['branch'].widget.attrs['readonly'] = True  # O‘zgartirib bo‘lmasligi uchun readonly
        else:
            self.fields['branch'].queryset = Branch.objects.all()


class QollanmaForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = Qollanma
        fields = BaseModelForm.Meta.fields

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Har bir maydonni majburiy emas qilib qo'yamiz
        for field in self.fields:
            self.fields[field].required = False

        # Faqat moderatorlar uchun o'z filialini ko'rsatamiz
        if user and hasattr(user, 'role') and user.role == 'moderator' and user.branch:
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['branch'].initial = user.branch
            self.fields['branch'].widget.attrs['readonly'] = True  # O‘zgartirib bo‘lmasligi uchun readonly
        else:
            self.fields['branch'].queryset = Branch.objects.all()


class LoyihaForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = Loyiha
        fields = BaseModelForm.Meta.fields

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Har bir maydonni majburiy emas qilib qo'yamiz
        for field in self.fields:
            self.fields[field].required = False

        # Faqat moderatorlar uchun o'z filialini ko'rsatamiz
        if user and hasattr(user, 'role') and user.role == 'moderator' and user.branch:
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['branch'].initial = user.branch
            self.fields['branch'].widget.attrs['readonly'] = True  # O‘zgartirib bo‘lmasligi uchun readonly
        else:
            self.fields['branch'].queryset = Branch.objects.all()


class JurnalForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = Jurnal
        fields = BaseModelForm.Meta.fields

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Har bir maydonni majburiy emas qilib qo'yamiz
        for field in self.fields:
            self.fields[field].required = False

        # Faqat moderatorlar uchun o'z filialini ko'rsatamiz
        if user and hasattr(user, 'role') and user.role == 'moderator' and user.branch:
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['branch'].initial = user.branch
            self.fields['branch'].widget.attrs['readonly'] = True  # O‘zgartirib bo‘lmasligi uchun readonly
        else:
            self.fields['branch'].queryset = Branch.objects.all()


class MaqolaForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = Maqola
        fields = BaseModelForm.Meta.fields

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Har bir maydonni majburiy emas qilib qo'yamiz
        for field in self.fields:
            self.fields[field].required = False

        # Faqat moderatorlar uchun o'z filialini ko'rsatamiz
        if user and hasattr(user, 'role') and user.role == 'moderator' and user.branch:
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['branch'].initial = user.branch
            self.fields['branch'].widget.attrs['readonly'] = True  # O‘zgartirib bo‘lmasligi uchun readonly
        else:
            self.fields['branch'].queryset = Branch.objects.all()


class OtherForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = Other
        fields = BaseModelForm.Meta.fields

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Har bir maydonni majburiy emas qilib qo'yamiz
        for field in self.fields:
            self.fields[field].required = False

        # Faqat moderatorlar uchun o'z filialini ko'rsatamiz
        if user and hasattr(user, 'role') and user.role == 'moderator' and user.branch:
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['branch'].initial = user.branch
            self.fields['branch'].widget.attrs['readonly'] = True  # O‘zgartirib bo‘lmasligi uchun readonly
        else:
            self.fields['branch'].queryset = Branch.objects.all()


class XorijiyTajribaForm(forms.ModelForm):
    class Meta:
        model = Xorijiy_Tajriba
        fields = [
            'degree', 'title', 'author', 'country', 'Military_organization', 'material', 'made_in', 'anotation', 'keys',
            'file', 'slug', 'image',
        ]
        widgets = {
            'anotation': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file and file.size > 10 * 1024 * 1024:  # Limit to 10 MB
            raise forms.ValidationError("Fayl hajmi 10MB dan oshmasligi kerak.")
        return file

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # user parametrini xavfsiz olamiz
        super(XorijiyTajribaForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False
        # Agar user moderator bo‘lsa, Military_organization ni cheklash
        if user and user.role == 'moderator' and user.branch:
            self.fields['Military_organization'].queryset = Xorijiy_Tajriba.objects.filter(branch=user.branch)
