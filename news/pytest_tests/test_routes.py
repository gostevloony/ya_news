from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


# 1. Главная страница доступна анонимному пользователю.
# 6. Страницы регистрации пользователей, входа в учётную
# запись и выхода из неё доступны анонимным пользователям.
@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# 2. Страница отдельной новости доступна анонимному пользователю.
@pytest.mark.django_db
def test_detail_availability_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# 3. Страницы удаления и редактирования комментария доступны автору
# комментария.
# 5. Авторизованный пользователь не может зайти на страницы редактирования
# или удаления чужих комментариев (возвращается ошибка 404).
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


# 4. При попытке перейти на страницу редактирования или удаления комментария
# анонимный пользователь перенаправляется на страницу авторизации.
@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_args')),
        ('news:delete', pytest.lazy_fixture('id_for_args')),
    ),
)
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
