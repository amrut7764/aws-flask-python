from lib import *
import unittest
import os
import sys
sys.path.append(os.path.abspath("../"))


class TestAWSUnittest(unittest.TestCase):

    def test_ec2InstaneList(self):
        ec2 = awsEC2()
        # self.assertRaises(AttributeError, ec2.allInstances)
        self.assertNotEqual(ec2.allInstances(), False)

    def test_rdsInstances(self):
        rds = awsRDS(region="us-east-1")
        ret = rds.RDSInstances()
        self.assertIsNot(ret, False)


if __name__ == "__main__":
    unittest.main()
