from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.dashboard, name="dashboard"),

     # path for activating the registered users
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),

     # path for forgot password
    path("forgotPassword/", views.forgotPassword, name="forgotPassword"),
     # path for validating that the user is the verified user for resetting the password
    path("resetpassword_validate/<uidb64>/<token>/",
         views.resetpassword_validate, name="resetpassword_validate"),
         
     # path for resetting the password after user validation above
    path("resetPassword/", views.resetPassword, name="resetPassword"),

    path("my_orders/", views.my_orders, name="my_orders"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("change_password/", views.change_password, name="change_password"),
    path("order_detail/<int:order_id>/",
         views.order_detail, name="order_detail"),
]
