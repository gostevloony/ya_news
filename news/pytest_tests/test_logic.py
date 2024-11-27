from http import HTTPStatus
from pytest_django.asserts import assertFormError, assertRedirects

from django.urls import reverse
import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import News, Comment


# 1. Анонимный пользователь не может отправить комментарий.
@pytest.mark.django_db
def test_anonymous_user_cant_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


# 2. Авторизованный пользователь может отправить комментарий.
def test_user_can_create_comment(author_client, news, author, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']


# 3. Если комментарий содержит запрещённые слова, он не будет опубликован,
# а форма вернёт ошибку.
def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


# 4.1 Авторизованный пользователь может редактировать свои комментарии.
def test_author_can_edit_comment(author_client, form_data, news, comment):
    url_detail = reverse('news:detail', args=(news.id,))
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    assertRedirects(response, f'{url_detail}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


# 4.2 Авторизованный пользователь может удалять свои комментарии.
def test_author_can_delete_comment(author_client, news, comment):
    url_detail = reverse('news:detail', args=(news.id,))
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    assertRedirects(response, f'{url_detail}#comments')
    assert Comment.objects.count() == 0


# 5.1 Авторизованный пользователь не может редактировать чужие комментарии.
def test_user_cant_edit_comment_of_another_user(
        not_author_client, form_data, comment
):
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    comment.text == form_data['text']


# 5.2 Авторизованный пользователь не может удалять чужие комментарии.
def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
