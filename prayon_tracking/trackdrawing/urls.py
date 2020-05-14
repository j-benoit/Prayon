"""prayon_tracking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    url(r'^connexion$', auth_views.LoginView.as_view(), name='login'),
    url(r'^deconnexion$', auth_views.LogoutView.as_view(next_page='accueil'), name='deconnexion'),
    url(r'^$', RedirectView.as_view(pattern_name='login')),
    url(r'^accueil', views.ListeSAP.as_view(), name='accueil'),
    url(r'^ExtractSAP/(?P<pk>\d+)$', views.UpdatedInfoCreate.as_view(), name='edit_data'),
    url(r'show/(?P<num_cadastre>\d+)$', views.DisplayDrawing, name='show_image'),
    # url(r'^backlog/(?P<pk>\d+)$', views.Send_To_Backlog, name='backlog'),
    url(r'^dashboard', views.Dashboard, name='dash'),
    url(r'^Backlog', views.ListBacklog.as_view(), name='Backlog'),
    url(r'^work', views.Dispatch_Work, name='work'),
    url(r'^test', views.Test, name='test'),
    url(r'^Export', views.Export_Database, name='Export'),
    url(r'^checker', views.nbChecker, name='checker'),
    url(r'^Admin', views.Admin, name='Admin'),
    url(r'^ModDB', views.FilterDatabase.as_view(), name='viewdb'),
    url(r'^ViewDB/Filter', views.FilterModDatabase.as_view(), name='Filterdb'),
    url(r'^ViewDB/CSV', views.CsvModDatabase.as_view(), name='CSVdb'),
    url(r'^Stamp$', views.StampView.as_view(), name='StampView'),
    url(r'^Stamp/Download/(?P<num_cadastre>\d+)$', views.DownloadDrawing, name='DownloadDrawing'),
    url(r'^Stamp/Upload/(?P<num_cadastre>\d+)$', views.UploadDrawing, name='UploadDrawing'),
    # url(r'^GroupUser', views.GroupUser, name='GroupUser'),
    url(r'^UpdateData$', views.UpdatedInfoCreate.as_view(), name='update_data'),

    url(r'^xed_post$', views.xed_post, name='xed_post'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
