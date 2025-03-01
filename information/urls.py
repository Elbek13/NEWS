from django.urls import path
from information.views import (
    category_list, m_category_list, global_search,
    dissertatsiya_list, dissertatsiya_create, dissertatsiya_edit, dissertatsiya_delete,
    m_dissertatsiya_list, m_dissertatsiya_create, m_dissertatsiya_edit, m_dissertatsiya_delete,
    u1_dissertatsiya_list, u1_dissertatsiya_detail,
    monografiya_list, monografiya_create, monografiya_edit, monografiya_delete,
    m_monografiya_list, m_monografiya_create, m_monografiya_edit, m_monografiya_delete,
    u1_monografiya_list, u1_monografiya_detail,
    risola_list, risola_create, risola_edit, risola_delete,
    m_risola_list, m_risola_create, m_risola_edit, m_risola_delete,
    u1_risola_list, u1_risola_detail,
    darslik_list, darslik_create, darslik_edit, darslik_delete,
    m_darslik_list, m_darslik_create, m_darslik_edit, m_darslik_delete,
    u1_darslik_list, u1_darslik_detail,
    qollanma_list, qollanma_create, qollanma_edit, qollanma_delete,
    m_qollanma_list, m_qollanma_create, m_qollanma_edit, m_qollanma_delete,
    u1_qollanma_list, u1_qollanma_detail,
    loyiha_list, loyiha_create, loyiha_edit, loyiha_delete,
    m_loyiha_list, m_loyiha_create, m_loyiha_edit, m_loyiha_delete,
    u1_loyiha_list, u1_loyiha_detail,
    jurnal_list, jurnal_create, jurnal_edit, jurnal_delete,
    m_jurnal_list, m_jurnal_create, m_jurnal_edit, m_jurnal_delete,
    u1_jurnal_list, u1_jurnal_detail,
    maqola_list, maqola_create, maqola_edit, maqola_delete,
    m_maqola_list, m_maqola_create, m_maqola_edit, m_maqola_delete,
    u1_maqola_list, u1_maqola_detail,
    other_list, other_create, other_edit, other_delete,
    m_other_list, m_other_create, m_other_edit, m_other_delete,
    u1_other_list, u1_other_detail,
    tajriba_list, tajriba_create, tajriba_edit, tajriba_delete,
    m_tajriba_list, m_tajriba_create, m_tajriba_edit, m_tajriba_delete,
    u1_tajriba_list, u1_tajriba_detail,
)

# Resurslar uchun umumiy patternlarni generatsiya qilish
def generate_resource_patterns(resource_name, has_detail=True):
    view_dict = {
        'dissertatsiya': (dissertatsiya_list, dissertatsiya_create, dissertatsiya_edit, dissertatsiya_delete,
                          m_dissertatsiya_list, m_dissertatsiya_create, m_dissertatsiya_edit, m_dissertatsiya_delete,
                          u1_dissertatsiya_list, u1_dissertatsiya_detail),
        'monografiya': (monografiya_list, monografiya_create, monografiya_edit, monografiya_delete,
                        m_monografiya_list, m_monografiya_create, m_monografiya_edit, m_monografiya_delete,
                        u1_monografiya_list, u1_monografiya_detail),
        'risola': (risola_list, risola_create, risola_edit, risola_delete,
                   m_risola_list, m_risola_create, m_risola_edit, m_risola_delete,
                   u1_risola_list, u1_risola_detail),
        'darslik': (darslik_list, darslik_create, darslik_edit, darslik_delete,
                    m_darslik_list, m_darslik_create, m_darslik_edit, m_darslik_delete,
                    u1_darslik_list, u1_darslik_detail),
        'qollanma': (qollanma_list, qollanma_create, qollanma_edit, qollanma_delete,
                     m_qollanma_list, m_qollanma_create, m_qollanma_edit, m_qollanma_delete,
                     u1_qollanma_list, u1_qollanma_detail),
        'loyiha': (loyiha_list, loyiha_create, loyiha_edit, loyiha_delete,
                   m_loyiha_list, m_loyiha_create, m_loyiha_edit, m_loyiha_delete,
                   u1_loyiha_list, u1_loyiha_detail),
        'jurnal': (jurnal_list, jurnal_create, jurnal_edit, jurnal_delete,
                   m_jurnal_list, m_jurnal_create, m_jurnal_edit, m_jurnal_delete,
                   u1_jurnal_list, u1_jurnal_detail),
        'maqola': (maqola_list, maqola_create, maqola_edit, maqola_delete,
                   m_maqola_list, m_maqola_create, m_maqola_edit, m_maqola_delete,
                   u1_maqola_list, u1_maqola_detail),
        'other': (other_list, other_create, other_edit, other_delete,
                  m_other_list, m_other_create, m_other_edit, m_other_delete,
                  u1_other_list, u1_other_detail),
        'tajriba': (tajriba_list, tajriba_create, tajriba_edit, tajriba_delete,
                    m_tajriba_list, m_tajriba_create, m_tajriba_edit, m_tajriba_delete,
                    u1_tajriba_list, u1_tajriba_detail),
    }

    views = view_dict[resource_name]
    patterns = [
        path(f'{resource_name}_list/', views[0], name=f'{resource_name}_list'),
        path(f'm_{resource_name}_list/', views[4], name=f'm_{resource_name}_list'),
        path(f'u1_{resource_name}_list/', views[8], name=f'u1_{resource_name}_list'),
        path(f'{resource_name}_list/create/', views[1], name=f'{resource_name}_create'),
        path(f'm_{resource_name}_list/create/', views[5], name=f'm_{resource_name}_create'),
        path(f'{resource_name}/edit/<int:{resource_name}_id>/', views[2], name=f'{resource_name}_edit'),
        path(f'm_{resource_name}/edit/<int:{resource_name}_id>/', views[6], name=f'm_{resource_name}_edit'),
        path(f'{resource_name}/delete/<int:{resource_name}_id>/', views[3], name=f'{resource_name}_delete'),
        path(f'm_{resource_name}/delete/<int:{resource_name}_id>/', views[7], name=f'm_{resource_name}_delete'),
    ]
    if has_detail:
        patterns.append(
            path(f'u1_{resource_name}/<int:{resource_name}_id>/', views[9], name=f'u1_{resource_name}_detail')
        )
    return patterns

# Resurslar ro'yxati
resources = [
    'dissertatsiya', 'monografiya', 'risola', 'darslik', 'qollanma',
    'loyiha', 'jurnal', 'maqola', 'other', 'tajriba',
]

# URL patternlarni generatsiya qilish
urlpatterns = [
    path('category/', category_list, name='category_list'),
    path('m_category/', m_category_list, name='m_category_list'),
    path('global-search/', global_search, name='global_search'),
]

for resource in resources:
    urlpatterns.extend(generate_resource_patterns(resource))