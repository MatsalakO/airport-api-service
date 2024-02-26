from django.urls import path

from user.views import CreateUserView, ManageUserView, CreateTokenView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", CreateTokenView.as_view(), name="token"),
    path("me/", ManageUserView.as_view(), name="manage"),
]

app_name = "user"
