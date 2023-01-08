from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
STRING_FROM_POST = 'author: {}, date: {:%m%d%Y}, group: {}, text: {}'
LENGTH = 15


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Наименование группы, не более 200 символов'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальный фрагмент URL',
        help_text='Используется как стандарт записи ссылок на объект'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Опишите группу как можно подробнее'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Основной текст поста')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Заполняется автоматически, в момент создания поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return STRING_FROM_POST.format(
            self.author.username,
            self.pub_date,
            self.group,
            self.text[:LENGTH],
        )
