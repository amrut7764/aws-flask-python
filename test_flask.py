from botocore.exceptions import NoCredentialsError
from lib import *
import unittest
import os
import sys
sys.path.append(os.path.abspath("../"))


class TestAWSUnittest(unittest.TestCase):

    def test_ec2InstaneList(self):
        ec2 = awsEC2()
        self.assertRaises(NoCredentialsError, ec2.allInstances)

    def test_rdsInstances(self):
        rds = awsRDS(region="us-east-1")
        self.assertRaises(NoCredentialsError, rds.RDSInstances)

    def test_s3CreateBucket(self):
        s3 = awsS3(objType="client", ver=3)
        self.assertRaises(NoCredentialsError, s3.createBucket,
                          Bucket="thisismytestbucket-1231231234234234")


if __name__ == "__main__":
    unittest.main()
