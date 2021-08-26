from libcatapult.storage.s3_tools import S3Utils


class NotConnectedException(Exception):
    pass


class S3Api(object):
    def __init__(self, access: str, secret: str, bucket_name: str, endpoint_url: str, s3_region: str):
        self.s3_conn = None
        self.access = access
        self.secret = secret
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.s3_region = s3_region

    def get_s3_connection(self):
        if not self.s3_conn:
            self.s3_conn = S3Utils(self.access, self.secret, self.bucket_name, self.endpoint_url, self.s3_region)
        return self.s3_conn

    def list_s3_files(self, prefix: str):
        if not self.s3_conn:
            raise NotConnectedException("must call S3API.get_s3_connection() before using S3API.list_s3_files")

        path_sizes = self.s3_conn.list_files_with_sizes(prefix)
        return path_sizes

    def get_object_body(self, path: str):
        if not self.s3_conn:
            raise NotConnectedException("must call S3API.get_s3_connection() before using S3API.get_object_body")

        return self.s3_conn.get_object_body(path)

    def fetch_file(self, source: str, dest: str):
        if not self.s3_conn:
            raise NotConnectedException("must call S3API.get_s3_connection() before using S3API.fetch_file")

        return self.s3_conn.fetch_file(source, dest)
