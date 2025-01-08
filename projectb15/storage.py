from storages.backends.s3boto3 import S3Boto3Storage
import io
from django.core.files.storage import Storage

class FileStorage(S3Boto3Storage):
    location = 'media'      
    file_overwrite = False  

    def listall(self):
        try:
           
            objects = self.bucket.objects.filter(Prefix=self.location)
            return [obj.key for obj in objects]
        except Exception as e:
            return []

    def _open(self, name, mode='rb'):
        try:
            
            file_obj = super()._open(name, mode)
            file_bytes = file_obj.read()
            return io.BytesIO(file_bytes)
        except Exception as e:
            raise IOError(f"Unable to open file {name}: {str(e)}")

    def _save(self, name, content):

        try:
            
            return super()._save(name, content)
        except Exception as e:
            raise IOError(f"Unable to save file {name}: {str(e)}")

    def delete(self, name):

        try:
            super().delete(name)
        except Exception as e:
            raise IOError(f"Unable to delete file {name}: {str(e)}")

    def url(self, name):

        try:
            return super().url(name)
        except Exception as e:
            raise IOError(f"Unable to generate URL for file {name}: {str(e)}")

    def exists(self, name):

        try:
            return super().exists(name)
        except Exception as e:
            return False
