from django.urls import path

from . import views

app_name = 'demands'

urlpatterns = [
    path("", views.index, name="index"),
    # Demands
    path("demands/create", views.createDemand, name="create"),
    path('demands/view/<int:id>/', views.view, name="view"),
    path('demands/edit/<int:id>/', views.edit, name="edit"),
    path('demands/search/', views.search, name="search"),
    # Acvities
    path('demands/activity/create', views.createActivity, name="createActivity"),
    path('demands/activity/delete/<int:id>/', views.deleteActivity, name="deleteActivity"),
    # user
    path('demands/user/edit/<int:id>/', views.editUser, name="editUser"),
]