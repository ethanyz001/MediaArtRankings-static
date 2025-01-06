from django.db import models

# Create your models here.
from django.db import models


# Authors Model
class Author(models.Model):
    name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.name


# Universities Model
class University(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    is_institution = models.BooleanField(default=False)
    formal_version = models.CharField(max_length=255, null=True, blank=True)
    chinese_name = models.CharField(max_length=255, null=True, blank=True)
    related_university = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


# Conferences Model
class Conference(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    rank = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B')], null=True)

    def __str__(self):
        return self.name


# Papers Model
class Paper(models.Model):
    title = models.CharField(max_length=255, primary_key=True)
    conference_name = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title


# PaperAuthors Model (Mapping papers and authors with 'is_first_author' flag)
class PaperAuthor(models.Model):
    paper_title = models.ForeignKey(Paper, on_delete=models.CASCADE)
    author_name = models.ForeignKey(Author, on_delete=models.CASCADE)
    is_first_author = models.BooleanField(default=False)

    class Meta:
        unique_together = ('paper_title', 'author_name')

    def __str__(self):
        return f'{self.author_name.name} - {self.paper_title.title}'


# AuthorsUniversities Model (Mapping authors to universities)
class AuthorUniversity(models.Model):
    author_name = models.ForeignKey(Author, on_delete=models.CASCADE)
    university_name = models.ForeignKey(University, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('author_name', 'university_name')

    def __str__(self):
        return f'{self.author_name.name} - {self.university_name.name}'
