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


if __name__ == "__main__":
    unittest.main()
