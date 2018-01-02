from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
import logging

from coursemanaging.models import NewsBulletin, NewsItem

logger = logging.getLogger(__name__)


class NewsBulletinTest(TestCase):
    def test_news_item_no_image(self):
        with self.assertRaises(ValidationError) as error:
            news_item = NewsItem.objects.create(text="longtext", short_text="short_text", title="title")
            NewsBulletin.objects.create(bulletin_level=1, news_item=news_item)
        self.assertEqual(error.exception.messages[0],
                         "news item : title needs to have an image in order to become a bulletin")

    def test_news_item_no_short_text(self):
        image = SimpleUploadedFile(name='test_image.jpg',
                                   content=open('coursemanaging/test/models/test_image.jpg', 'rb').read(),
                                   content_type='image/jpeg')
        with self.assertRaises(ValidationError) as error:
            news_item = NewsItem.objects.create(text="longtext", title="title", image=image)
            NewsBulletin.objects.create(bulletin_level=1, news_item=news_item)
        self.assertEqual(error.exception.messages[0],
                         "news item : title needs to have a short_text in order to become a bulletin")
