import os


def init_bucket():
    bucket_location = os.getenv("BUCKET")


class Bucket:
    bucket_location = None

    @staticmethod
    def get_file(file_path):
        bucket_location = Bucket.bucket_location
        if bucket_location is not None:
            file_path = f'{bucket_location}/{file_path}'
