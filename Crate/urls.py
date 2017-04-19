from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views

urlpatterns = [
    # Page that displays the list of categories
    url(r'^$', views.category_list, name='category_list'),
    # Page that displays the list of subcategories for a category
    url(r'^(?P<category_name>((([\w]+)\s?)+))/$', views.category, name='category'),
    # Page that displays the list of interest groups pertaining to the subcategory
    url(r'^(?P<category_name>((([\w]+)\s?)+))/(?P<subcategory_name>(([\w]+)\s?)+)/$',
        views.subcategory, name='subcategory'),
    # Page that displays the discussion for the given interest group
    url(r'^(?P<category_name>((([\w]+)\s?)+))/(?P<subcategory_name>(([\w]+)\s?)+)/(?P<interest_group_name>([\w]+)\s?)+/$',
        views.DiscussionFormView.as_view(), name='box_discussion'),
    # Page that allows users to vote on a box
    url(r'^(?P<box_id>[\d]+)/vote$', views.BoxVoteFormView.as_view(), name='box_item_vote'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
