
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
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
            text='Тестовое содержание поста',
            group=cls.group
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_cant_create_post_anonymous(self):
        '''Тестируем запрет записи поста неавторизованным пользователем'''
        tasks_count = Post.objects.count()
        form_data = {
            'group': PostCreateFormTests.group.id,
            'text': 'Тестовый текст',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_authorized(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'group': PostCreateFormTests.group.id,
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
                             'username': PostCreateFormTests.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostCreateFormTests.group,
                text='Тестовый текст',
                author=PostCreateFormTests.user
            ).exists()
        )


class PostEditFormTests(TestCase):

    class Meta:
        model = Post
        fields = '__all__'

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
            text='Тестовое содержание поста',
            group=cls.group
        )
        cls.form = PostForm(instance=cls.post)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostEditFormTests.user)

    def test_cant_edit_post_authorized(self):
        '''Тестируем редактирования поста авторизованным пользователем'''
        tasks_count = Post.objects.count()
        form_data = {
            'group': PostCreateFormTests.group.id,
            'text': 'test',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostEditFormTests.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        modified_post = Post.objects.get(id=PostEditFormTests.post.id)
        self.assertEquals(modified_post.text, 'test')
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id':
                                             PostEditFormTests.post.id}))
