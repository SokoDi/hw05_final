from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Давай что-нибудь напишем!')
        self.fields['group'].empty_label = (
            'Выберите группу, если желаете 🙂')

    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': 'Введите текст',
            'group': 'Выберите группу'
        }
        help_texts = {
            'text': 'Ваш текст поста',
            'group': 'Из уже существующих'
        }

class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Критику!')
        
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Введите текст',
        }
        help_texts = {
            'text': 'Текст вашего коментария',
        }
