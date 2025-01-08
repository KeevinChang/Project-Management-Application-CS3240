# Create your tests here.
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Upload

class FileUploadTest(TestCase):
    def test_file_upload(self):
        # Create a simple uploaded file
        file = SimpleUploadedFile("testfile.txt", b"Test file content")
        
        # Post the file to the upload URL
        response = self.client.post('/upload/', {'file': file})
        
        # Check that the response is a redirect (status code 302)
        self.assertEqual(response.status_code, 302)
        
        # Check that the file was saved in the database
        self.assertTrue(Upload.objects.exists())

class FileListTest(TestCase):
    def test_file_list(self):
        # Create a test file in the database
        Upload.objects.create(file='uploads/testfile.txt')
        
        # Get the file list URL
        response = self.client.get('/files/')
        
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that the file is listed in the response
        self.assertContains(response, 'uploads/testfile.txt')

class HomePageTest(TestCase):
    def test_home_page(self):
        # Get the home page URL
        response = self.client.get('/')
        
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that the home page contains the expected content
        self.assertContains(response, 'Welcome to Project B15')