import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


# 1. Количество новостей на главной странице — не более 10.
@pytest.mark.django_db
def test_news_count(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


# 2. Новости отсортированы от самой свежей к самой старой. Свежие
# новости в начале списка.
@pytest.mark.django_db
def test_news_order(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


# 3. Комментарии на странице отдельной новости отсортированы в хронологическом
# порядке: старые в начале списка, новые — в конце.
@pytest.mark.django_db
def test_comments_order(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


# 4.1. Анонимному пользователю недоступна форма для отправки комментария
# на странице отдельной новости.
@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


# 4.2. Авторизованному пользователю доступна форма для отправки комментария
# на странице отдельной новости.
@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
