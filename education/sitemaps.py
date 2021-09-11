from django.contrib.sitemaps import Sitemap
from .models import Course, Book

class CourseSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Course.objects.all()

    def lastmode(self, obj):
        return obj.date


class BookSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return Book.objects.all()
