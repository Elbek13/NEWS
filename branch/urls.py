from django.urls import path
from branch.views import branch_list, branch_create,branch_delete,branch_edit

urlpatterns = [
    path('branches/', branch_list, name='branch_list'),  # Filiallar ro‘yxati
    path('branches/create/', branch_create, name='branch_create'),  # Yangi filial qo‘shish
    path('branches/edit/<int:branch_id>/', branch_edit, name='branch_edit'),
    path('branches/delete/<int:branch_id>/', branch_delete, name='branch_delete'),
]
