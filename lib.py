__author__ = 'Ammirat'


import gzip
import pprint
import logging
import json
import StringIO
import datetime
import boto3
from boto.s3.connection import S3Connection
import os
import sys
sys.path.append(os.path.abspath("../"))
logger = logging.getLogger()
# FORMAT = "[%(asctime)s - %(filename)s:%(lineno)s - %(funcName) 2s()] %(levelname)-2s:%(message)s", "%Y-%m-%d %H:%M:%S"
# FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
# logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)


class awsEC2(object):

    def __init__(self, region="us-east-1"):
        """
        Class object for S3 operations.
        Args:
            region : Name of the region for EC2 instances. Default is "us-east-1"
        Returns:
            Returns Client/Resource object for EC2 for specified region.
        Raises:
            Throws Error and raise exeception: if failed to create client.
        """
        self.region = region
        self.ec2Client = boto3.client("ec2",  region_name=self.region)

    def allInstances(self, instanceId=None):
        """
        Args:
            instanceId : InstanceId of an EC2 instance (optional)
            default: All EC2 instances information will be displayed
        """
        try:
            dict = {}
            logger.debug("Listing all EC2 instances in region %s" %
                         (self.region))
            if instanceId:
                ret = self.ec2Client.describe_instances(
                    InstanceIds=[instanceId])
                for i in ret["Reservations"]:
                    for j in i["Instances"]:
                        for k in j["Tags"]:
                            if k["Key"] == "Name":
                                dict[j["InstanceId"]] = k["Value"]
                return dict
            else:
                ret = self.ec2Client.describe_instances()
                return ret

        except Exception as e:
            raise(e)


class awsRDS(object):

    def __init__(self, region="us-east-1"):
        self.region = region
        self.rdsClient = boto3.client("rds", region_name=self.region)

    def RDSInstances(self, dbInstanceId=None):
        """
        Args:
            dbInstanceId : DBInstanceIdentifier to get details (optional)
            default: All RDS instances information will be displayed
        """
        try:
            logger.debug("Listing all RDS instances in region %s" %
                         self.region)
            if dbInstanceId:
                ret = self.rdsClient.describe_db_instances(
                    DBInstanceIdentifier=dbInstanceId)
                return ret
            else:
                ret = self.rdsClient.describe_db_instances()
                return ret
        except Exception as e:
            raise (e)


class awsS3(object):

    def __init__(self,  objType="client", ver="3", profile_name="default", region_name=None):
        """
        Class object for S3 operations.
        Args:
            objType : Object type can be either client or resource
            profile_name : Different profiles saved in ~/.aws/credentials file can be used
            vers = Boto library version to use
            profile_name : Name of the aws profile to use
            region_name : Name of the region to carry operatiosn on. Default is as per aws profile if set otherwise "us-east-1"
        Returns:
            Returns Client/Resource object for S3 depending on type.
        Raises:
            Throws Error and raise exeception: if failed to create client.
        """
        try:
            if ver == 2:
                logger.debug("Creating S3 object with boto library")
                accessKeyId = environ["ACCESS_KEY_ID"]
                secreteKey = environ["SECRETE_KEY"]
                try:
                    conn = S3Connection(accessKeyId, secreteKey)
                    self.s3conn = conn
                except Exception as e:
                    logger.error(
                        "Failed to create S3 connection using AWS credentials :: %s" % e)
                    raise e
            logger.debug("Creating S3 boto object %s of type %s using profile %s" % (
                ver, objType, profile_name))
            if region_name:
                self.s3Sess = boto3.session.Session(
                    profile_name=profile_name, region_name=region_name)
            else:
                self.s3Sess = boto3.session.Session(profile_name=profile_name)
            if objType == "client":
                self.s3Obj = self.s3Sess.client("s3")
            elif objType == "resource":
                self.s3Obj = self.s3Sess.resource("s3")

        except Exception as e:
            logger.error("Failed to create S3 object :: %s" % e)
            raise e

    def createBucket(self, **kwargs):
        """
        Create a bucket in specified region.
        Args:
            Bucket : Name for the new bucket (REQUIRED)
            ACL : The canned ACL to apply to the bucket. e.g. 'private'|'public-read'|'public-read-write'|'authenticated-read'
            Region: LocationConstraint in which the new bucket will be created. e.g. 'EU'|'eu-west-1'|'us-west-1'|'us-west-2'|'ap-south-1'|'ap-southeast-1'|'ap-southeast-2'|'ap-northeast-1'|'sa-east-1'|'cn-north-1'|'eu-central-1'
            GrantFullControl (string) -- Allows grantee the read, write, read ACP, and write ACP permissions on the bucket.
            GrantRead (string) -- Allows grantee to list the objects in the bucket.
            GrantReadACP (string) -- Allows grantee to read the bucket ACL.
            GrantWrite (string) -- Allows grantee to create, overwrite, and delete any object in the bucket.
            GrantWriteACP (string) -- Allows grantee to write the ACL for the applicable bucket.
            ObjectLockEnabledForBucket (boolean) -- Specifies whether you want S3 Object Lock to be enabled for the new bucket.
        Returns:
            Returns Client/Resource object for S3 depending on type.
        Raises:
            Exception: if failed to create Bucket.
        """
        # if region is not specified by user while calling this method then use default region from aws profile
        logger.debug("User submitted keyword arguments are: %s" % kwargs)

        # If user has not specified an argment
        if not 'Region' in kwargs.keys():
            kwargs["Region"] = self.s3Sess.region_name

        # For region "us-east-1" we should not pass CreateBucketConfiguration
        if kwargs["Region"] == "us-east-1":
            del kwargs["Region"]
        # For other regions CreateBucketConfiguration need to be passed as an argument
        else:
            CreateBucketConfiguration = {
                'LocationConstraint': kwargs['Region']}
            kwargs['CreateBucketConfiguration'] = CreateBucketConfiguration
            # Delete the user specified argument
            del kwargs["Region"]

        try:
            logger.debug(
                "Keyword Arguments for createBucket: [ %s ] " % kwargs)
            ret = self.s3Obj.create_bucket(**kwargs)
            return ret
        except Exception as e:
            logger.error("Failed to create a bucket [%s] with arguremts [%s]" % (
                kwargs["Bucket"], kwargs))
            raise e

    def listAllBuckets(self):
        """
        Get list of all buckets in the account
        Args:
            This operation does not use request parameters
        Returns: list
            Buckets: The return value. True for success, False otherwise.
        Raises:
            Exception
        """
        try:
            ret = self.s3Obj.list_buckets()
            return ret
        except Exception as e:
            logger.error("Failed to get list of all buckets :: %s" % e)
            raise e

    def downloadFile(self, bucket, key, localFile, extraArgs=None):
        """
        Gets detailed information about a specified number of requests
        Args:
            bucket : Name of the bucket for downloading the file from
            key : Name of the S3 file name to download
            localFile : Location for downloading file on local server
            extraArgs : Extra arguments that may be passed to the client operation.
        Returns:
            bool: The return value. True for success, False otherwise.
        Raises:
            Error
        """
        try:
            logger.debug("Downloading file [%s/%s]" % (bucket, key))
            self.s3Obj.meta.client.download_file(
                bucket, key, localFile, ExtraArgs=extraArgs)
            return True

        except Exception as e:
            logger.error("Failed to download S3 file with ERROR : %s" % e)
            raise e

    def uploadFile(self, bucket, key, localFile, extraArgs=None):
        """
        Upload local file to specified bucket with name specified as key
        Args:
            bucket : Name of the bucket on S3 to upload a file
            key : Name of the file on S3 to upload
            localFile : Name of the local file to upload to S3
            extraArgs : Extra arguments that may be passed to the client operation.
        Returns:
            bool: The return value. True for success, False otherwise.
        Raises:
            Error

        """
        try:
            logger.debug("Uploading file to [%s/%s]" % (bucket, key))
            self.s3Obj.meta.client.upload_file(
                localFile, bucket, key, ExtraArgs=extraArgs)
            return True

        except Exception as e:
            doError("Failed to upload file to S3 with ERROR: %s" % e)
            return False

    def writeLocalFile(self, fileName, contents):
        """
        Write contents to local file
        Args:
            fileName : Name of the file to write contents to.
            contents : Contents to write to file.
        Returns:
            bool: The return value. True for success, False otherwise.
        Raises:
            Error
        """
        try:
            logger.debug("Writing file contents to local file %s" % fileName)
            with open(fileName, mode="a+") as fh:
                for i in contents:
                    fh.writelines("%s\n" % i)
                fh.close()
            return True

        except Exception as e:
            doError("Failed to write contents to file with ERROR: %s" % e)
            return False

    def readLogsFromS3(self, prefix, match):
        """
        prefix - the prefix of files to match, useful for limiting date ranges
        match - the string present in relevant log entries
        """
        logs = ["No log file found with prefix"]
        bucketName = environ["log_bucket"]
        count = 0
        longPrefix = "AWSLogs/527486489180/elasticloadbalancing/us-east-1/" + prefix
        try:
            conn = S3Connection()
            bucket = conn.get_bucket(bucketName)

            keys = bucket.get_all_keys(prefix=longPrefix)
            logger.debug("Searching {} log files".format(len(keys)))
            for key in keys:
                fileobj = StringIO.StringIO(key.get_contents_as_string())
                gzip_file_handle = gzip.GzipFile(fileobj=fileobj)
                log = gzip_file_handle.read()
                logs = log.split('\n')
                logs = [l for l in logs if match in l]
                logger.debug(
                    "Fetched logs from S3 with matching prefix and matching string are: %s" % logs)
                for l in logs:
                    count += 1

            return logs
        except Exception as e:
            doException("Failed to fetch logs from S3 with log prefix: %s and match: %s" % (prefix, match), e,
                        RuntimeError, logger)

    def deleteObject(self, **kwargs):
        """
        Delete the specified Object 
        Args:
            Bucket: Name of the bucket where object key is [REQUIRED]
            Key : Name of the object key in the bucket [REQUIRED]
            VersionId: Spcific version of the key object 
            MFA :  The concatenation of the authentication device's serial number, a space, and the value that is displayed on your authentication device
        Returns: 
            DeleteMarker: True|False
            VersionId: Returns the version ID of the delete marker created as a result of the DELETE operation.
            RequestCharged: If present, indicates that the requester was successfully charged for the request.
        Raises:
            Exception
        """
        try:
            logger.info("KWARGS: %s" % kwargs)
            logger.debug("Deleting object key [ %s ] from bucket [ %s ]" % (
                kwargs['Key'], kwargs['Bucket']))
            ret = self.s3Obj.delete_object(**kwargs)
            return ret
        except Exception as e:
            logger.error("Failed to delete object key [ %s ] from bucket [ %s ]" % (
                kwargs['Key'], kwargs['Bucket']))

    def deleteBucket(self, Bucket):
        """
        Delete the specified bucket
        Args:
            Bucket: Name of the bucket to be deleted
        Returns: 
            None
        Raises:
            Exception
        Note: The object of S3 needs to be created for the same region. Otherwise will throw "errorMessage": "'awsS3' object has no attribute 'deleteBucket'"
        <bound method S3RegionRedirector.redirect_from_error of <botocore.utils.S3RegionRedirector object at >>
        """
        try:
            logger.debug("Deleting bucket [ %s ]" % Bucket)
            ret = self.s3Obj.delete_bucket(Bucket=Bucket)
            return ret
        except Exception as e:
            logger.error("Failed to delete bucket [ %s ]" % Bucket)
            raise (e)


class awsWAF(object):

    def __init__(self, region="us-east-1", wafType="cdn"):
        """
        Class object for WAF operations.
        Args:
            region : Name of the region in which ALB waf is created. Default
            "us-east-1".
            waftype : Type of WAF, either "cdn" or "alb". Default is "cdn". For
            "alb", region variable is mandatory.
        Returns:
            Client object for WAF depending on type.
        Raises:
            Throws Error and raise exeception: if failed to create client.
        """
        self.region = region
        try:
            if wafType == "alb":
                session = boto3.session.Session(region_name=self.region)
                self.wafClient = session.client('waf-regional')
            else:
                self.wafClient = boto3.client("waf")
        except Exception as e:
            logger.error("Failed to create WAF client for type %s" % wafType)
            raise (e)

    def getSampleRequests(self, WebAclId, RuleId, StartTime, EndTime, MaxItems):
        """
            Gets detailed information about a specified number of requests
            Args:
                WebAclId    : The WebACLId of the WebACL for which you want
                            GetSampledRequests to return a sample of requests.
                RuleId      : RuleId is one of three values: RuleId of the Rule or the
                            RuleGroupId of the RuleGroup or Default_Action ,
                            which causes GetSampledRequests to return a sample of
                            the requests that didn't match any of the rules in the
                            specified WebACL .
                StartTime   : The beginning of the time range, specify the date add
                            time in the following format:  "2018,06,19,12,00,00" for 2018-06-19 12:00:00. If EndTime
                               is specified as "now" then StartTime will be automatically chosen as 3 hours back
                EndTime     : The end of the time range, you can specify any time
                            range in the previous three hours. "now" for current time, "2018,06,19,12,00,00" for 2018-06-19 12:00:00.
                MaxItems    :The number of requests that you want AWS WAF to return
                            from among the first 5,000 requests that your AWS resource
                            received during the time range.
            Returns:
                Returns list of sample data for particular rule within specified time.
            Raises:
                UserException : if failed to create client.
        """
        try:
            # Check if user has given "Now" for date in environment
            if EndTime == "now":
                doInfo(
                    "User has specify EndTime as now, StartTime will be auto calculated", logger)
                EndTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                StartTime = (datetime.datetime.now(
                ) - datetime.timedelta(hours=2, minutes=59)).strftime("%Y-%m-%d %H:%M:%S")
                logger.debug("%s - %s " % (StartTime, EndTime))
            elif type(environ['StartTime']) and type(environ['EndTime']) == str:
                # If user send defined time as "2018,06,19,12,00,00"
                try:
                    doInfo("User has specified custom date", logger)
                    StartTime = tuple(map(int, StartTime.split(",")))
                    EndTime = tuple(map(int, EndTime.split(",")))

                    # Create a datetime object
                    StartTime = datetime.datetime(
                        *StartTime).strftime("%Y-%m-%d %H:%M:%S")
                    EndTime = datetime.datetime(
                        *EndTime).strftime("%Y-%m-%d %H:%M:%S")
                    logger.debug("%s - %s " % (StartTime, EndTime))
                except Exception as e:
                    doException(
                        "Failed to create a date object from the given input", e, UserException, logger)

            # TODO: To get local time instead of UTC
            # If Testing locally, we need to adjust time as per GMT
            #EndTime = (datetime.datetime.now() - datetime.timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
            # StartTime = ((datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S"))

            TimeWindow = {"StartTime": StartTime, "EndTime": EndTime}
            logger.debug("Args for get_sampled_requests(): (%s %s %s %s)" % (
                WebAclId, RuleId, TimeWindow, MaxItems))
            ret = self.wafClient.get_sampled_requests(WebAclId=WebAclId,
                                                      RuleId=RuleId,
                                                      TimeWindow=TimeWindow,
                                                      MaxItems=MaxItems)
            logger.debug("SampledRequests: %s" % ret)
            return ret['SampledRequests']
        except Exception as e:
            doException("Failed to get sample requests for rule [%s] between"
                        "[%s] and [%s] with ERRROR: %s" % (RuleId, StartTime, EndTime, e), e, UserException)


def doDump(obj):
    ret = []
    for attr in dir(obj):
        if hasattr(obj, attr):
            print("'%s' : '%s'," % (attr, getattr(obj, attr)))
            ret.append("'%s' = '%s'," % (attr, getattr(obj, attr)))


def getError(obj):
    ret = {}
    for attr in dir(obj):
        if attr == None:
            continue
        if attr == "response":
            code = getattr(obj, attr)
            ret["StatusCode"] = code["ResponseMetadata"]["HTTPStatusCode"]
        elif attr == "message":
            Error = getattr(obj, attr)
            ret["Error"] = Error

    return ret


def responseBuilder(app, obj):
    response = app.response_class(
        response=obj.data,
        status=obj.status_code,
        mimetype=app.config['JSONIFY_MIMETYPE']
    )
    return response


def exceptionBuilder(app, obj):
    response = app.response_class(
        response=obj.response['Error']['Code'],
        status=obj.response['ResponseMetadata']['HTTPStatusCode'],
        mimetype=app.config['JSONIFY_MIMETYPE']
    )
    return response
