from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor .fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager


# Create your models here.
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(
        max_length=100)  # is a field for post title. this field is CharField, which translates into a VARCHAR column in the SQL database
    slug = models.SlugField(max_length=50,
                            unique_for_date='publish')  # is intended to used in the URL. the unique_for_date parameter is used to build URLs for posts based on the publication date and slug.
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='blog_posts')  # the on_delete parameter specifies the behaviour to adopt when the referenced object is deleted it is an SQL standard. CASCADE specifies that when a referenced user is deleted, the database automatically deletes the related blog. specifying the name of the reverse relationship, from User to Post with the related_name attribute allows you to access the related objects easily.
    body = RichTextUploadingField()  # is the post's body and it translates to a text column in the SQL database
    publish = models.DateTimeField(
        default=timezone.now)  # date time field indicates the time when the post was created and it uses django's timezone now method as a default value returning the current datetime.
    created = models.DateTimeField(
        auto_now_add=True)  # auto_now_add saves the date automatically when an object is created.
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    objects = models.Manager()  # the default manager
    published = PublishedManager()  # custom manager
    tags = TaggableManager()

    class Meta:  # class meta inside the model contains metadata. here the posts are ordered in descending order where recently published posts appear first.
        ordering = ('-publish',)

    def __str__(
            self):  # is a human readable representation of the object. django will use it in many places such as the admin site
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day, self.slug])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
