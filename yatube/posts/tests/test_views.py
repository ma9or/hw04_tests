from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug':
                            PostPagesTests.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            PostPagesTests.user.username}):
            'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            PostPagesTests.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            PostPagesTests.post.id}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_author_0 = first_object.author
        posts_group_0 = first_object.group
        self.assertEqual(posts_text_0, PostPagesTests.post.text)
        self.assertEqual(posts_author_0, PostPagesTests.post.author)
        self.assertEqual(posts_group_0, PostPagesTests.post.group)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:group_posts',
                                              kwargs={'slug':
                                                      PostPagesTests.
                                                      group.slug}))
        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_author_0 = first_object.author
        posts_group_0 = first_object.group
        self.assertEqual(posts_text_0, PostPagesTests.post.text)
        self.assertEqual(posts_author_0, PostPagesTests.post.author)
        self.assertEqual(posts_group_0, PostPagesTests.post.group)
        group_context = response.context['group']
        self.assertEqual(group_context, PostPagesTests.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:profile',
                                                      kwargs={'username':
                                                              PostPagesTests.
                                                              user.username}))
        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_author_0 = first_object.author
        posts_group_0 = first_object.group
        self.assertEqual(posts_text_0, PostPagesTests.post.text)
        self.assertEqual(posts_author_0, PostPagesTests.post.author)
        self.assertEqual(posts_group_0, PostPagesTests.post.group)
        author_context = response.context['author']
        self.assertEqual(author_context, PostPagesTests.post.author)

    def test_posts_detail_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                                      kwargs={'post_id':
                                                              PostPagesTests.
                                                              post.id}))
        post_context = response.context['post']
        self.assertEqual(post_context, PostPagesTests.post)

    def test_create_post__page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        username_context = response.context['username']
        self.assertEqual(username_context, PostPagesTests.user)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id':
                                                              PostPagesTests.
                                                              post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        username_context = response.context['username']
        self.assertEqual(username_context, PostPagesTests.user)
        is_edit_context = response.context.get('is_edit')
        self.assertTrue(is_edit_context)

    def test_page_list_is_1(self):
        """Пост с группой попал на необходимые страницы."""
        field_urls_templates = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={
                'slug': PostPagesTests.group.slug}),
            reverse('posts:profile', kwargs={
                'username': PostPagesTests.user.username})
        ]
        for url in field_urls_templates:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context['page_obj']), 1)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        list_objs = list()
        for i in range(13):
            list_objs.append(Post.objects.create(
                author=cls.user,
                text=f'Тестовое содержание поста #{i}',
                group=cls.group)
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_paginator_pages(self):
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_posts',
                    kwargs={'slug': PaginatorViewsTest.
                            group.slug}),
            reverse('posts:profile', kwargs={'username':
                                             PaginatorViewsTest.
                                             user.username})
        ]
        get_first_page_contains_ten_records(self,
                                            self.authorized_client,
                                            pages_names)
        get_second_page_contains_three_records(self,
                                               self.authorized_client,
                                               pages_names)


def get_first_page_contains_ten_records(self, client, page_names):
    for url in page_names:
        with self.subTest(url=url):
            response = client.get(url)
            self.assertEqual(len(response.context['page_obj']), 10)


def get_second_page_contains_three_records(self, client, page_names):
    for url in page_names:
        with self.subTest(url=url):
            response = client.get(url + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)
