from user.views import admin_list, admin_delete, admin_create, admin_edit, user_list, user1_list, user1_create, \
    user1_edit, \
    user1_delete, moderator_list, moderator_create, moderator_edit, moderator_delete, user2_list, \
    user2_create, user2_edit, user2_delete, user3_list, user3_create, user3_delete, user3_edit, m_user_list, \
    m_user1_list, m_user1_create, m_user1_edit, m_user1_delete, m_user2_list, m_user2_create, m_user2_edit, \
    m_user2_delete, m_user3_edit, m_user3_list, m_user3_create, m_user3_delete,sayt,user1,user2
from django.urls import path

urlpatterns = [
    path('sayt/',sayt,name='sayt'),
    path('user_list/', user_list, name='user_list'),
    path('m_user_list/', m_user_list, name='m_user_list'),
    path('user1/', user1, name='user1'),
    path('user2/', user2, name='user2'),

    path('admin_list/', admin_list, name='admin_list'),
    path('admin_list/create/', admin_create, name='admin_create'),
    path('admin_list/edit/<int:user_id>/', admin_edit, name='admin_edit'),
    path('admin_list/delete/<int:user_id>/', admin_delete, name='admin_delete'),

    path('moderator_list/', moderator_list, name='moderator_list'),
    path('moderator_list/create/', moderator_create, name='moderator_create'),
    path('moderator_list/edit/<int:user_id>/', moderator_edit, name='moderator_edit'),
    path('moderator_list/delete/<int:user_id>/', moderator_delete, name='moderator_delete'),

    path('user1_list/', user1_list, name='user1_list'),
    path('m_user1_list/', m_user1_list, name='m_user1_list'),
    path('m_user2_list/', m_user2_list, name='m_user2_list'),
    path('m_user3_list/', m_user3_list, name='m_user3_list'),

    path('user1/create/', user1_create, name='user1_create'),
    path('m_user1/create/', m_user1_create, name='m_user1_create'),
    path('m_user2/create/', m_user2_create, name='m_user2_create'),
    path('m_user3/create/', m_user3_create, name='m_user3_create'),

    path('user1/edit/<int:user_id>/', user1_edit, name='user1_edit'),
    path('m_user1/edit/<int:user_id>/', m_user1_edit, name='m_user1_edit'),
    path('m_user2/edit/<int:user_id>/', m_user2_edit, name='m_user2_edit'),
    path('m_user3/edit/<int:user_id>/', m_user3_edit, name='m_user3_edit'),

    path('user1/delete/<int:user_id>/', user1_delete, name='user1_delete'),
    path('m_user1/delete/<int:user_id>/', m_user1_delete, name='m_user1_delete'),
    path('m_user2/delete/<int:user_id>/', m_user2_delete, name='m_user2_delete'),
    path('m_user3/delete/<int:user_id>/', m_user3_delete, name='m_user3_delete'),

    path('user2_list/', user2_list, name='user2_list'),
    path('user2/create/', user2_create, name='user2_create'),
    path('user2/edit/<int:user_id>/', user2_edit, name='user2_edit'),
    path('user2/delete/<int:user_id>/', user2_delete, name='user2_delete'),

    path('user3_list/', user3_list, name='user3_list'),
    path('user3/create/', user3_create, name='user3_create'),
    path('user3/edit/<int:user_id>/', user3_edit, name='user3_edit'),
    path('user3/delete/<int:user_id>/', user3_delete, name='user3_delete'),

]
