from .models import Post

from django.forms import ModelForm


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': 'Введите текст',
            'group': 'Выберите нужную группу'
        }
        help_text = {
            'text': 'Придумайте текст для поста. '
                    'Поле обязательно для заполнения',
            'group': 'Группа поста',
        }
