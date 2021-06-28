
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404, handler500
import auctions.views as auction_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("auctions.urls"))
]

handler404 = auction_views.error_404
handler500 = auction_views.error_500