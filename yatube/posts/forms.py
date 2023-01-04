from .models import Post

from django.forms import ModelForm, CharField, Textarea


class PostForm(ModelForm):
    text = CharField(
        widget=Textarea,
        label="Введите текст",
        required=True,
        help_text="Текст поста",
    )

    class Meta:
        model = Post
        fields = ("text", "group")
        labels = {"group": "Выберите нужную группу"}
        help_text = {"group": "Группа поста"}
