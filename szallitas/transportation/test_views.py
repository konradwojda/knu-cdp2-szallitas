from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.client import RequestFactory

from .models import *
from .views import upload_zip

FIXTURES_DIR = Path(__file__).parent / "gtfs_tools" / "fixtures"


class UploadZIPTestCase(TestCase):
    def setUp(self) -> None:
        get_user_model().objects.create_superuser("test", "", "test1234")  # type: ignore
        self._user = get_user_model().objects.get(username="test")
        self._factory = RequestFactory()
        return super().setUp()

    def test_upload_normal(self):
        with open(FIXTURES_DIR / "lomianki.zip", "rb") as zip:
            file = SimpleUploadedFile("lomianki.zip", content=zip.read())
            request = self._factory.post("/transportation/upload_zip", data={"zip_import": file})
            request.user = self._user
            setattr(request, 'session', 'session')
            messages = FallbackStorage(request)
            setattr(request, '_messages', messages)
            upload_zip(request)

        self.assertEqual(Agency.objects.count(), 1)
        self.assertEqual(Stop.objects.count(), 75)
        self.assertEqual(Line.objects.count(), 3)
        self.assertEqual(Calendar.objects.count(), 2)
        self.assertEqual(CalendarException.objects.count(), 16)
        self.assertEqual(Pattern.objects.count(), 18)
        self.assertEqual(PatternStop.objects.count(), 332)
        self.assertEqual(Trip.objects.count(), 61)

    def test_upload_bad_file(self):
        file = SimpleUploadedFile("lomianki.zip", content=b"abcd")
        request = self._factory.post("/transportation/upload_zip", data={"zip_import": file})
        request.user = self._user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        upload_zip(request)

        self.assertEqual(Agency.objects.count(), 0)
        self.assertEqual(Stop.objects.count(), 0)
        self.assertEqual(Line.objects.count(), 0)
        self.assertEqual(Calendar.objects.count(), 0)
        self.assertEqual(CalendarException.objects.count(), 0)
        self.assertEqual(Pattern.objects.count(), 0)
        self.assertEqual(PatternStop.objects.count(), 0)
        self.assertEqual(Trip.objects.count(), 0)
