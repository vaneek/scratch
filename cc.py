#!/usr/bin/env python

###
### TO DO Add ETag checking
### TO DO Add better error checking
###

"""
Simple command line tool to conditionally copy to S3 based on ETag hash.
"""

# import sys
# import os
# import re
import argparse
import boto3
import botocore

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='A simple command line utility.')
    parser.add_argument('keyname', metavar='FileName', help='Filename to copy to S3')
    parser.add_argument('bucket', metavar='BucketName', help='Destination bucket')
    parser.add_argument('-P', '--profile', help='AWS config profile name')

    args = parser.parse_args()
    print args

    if args.profile:
        print args.profile
        session = boto3.Session(profile_name=args.profile)
        s3 = session.resource('s3')
    else:
        s3 = boto3.resource('s3')

    bucket = s3.Bucket(args.bucket)
    exists = True
    try:
        s3.meta.client.head_bucket(Bucket=args.bucket)
    except botocore.exceptions.ClientError as error:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(error.response['Error']['Code'])
        if error_code == 404:
            exists = False
    print exists

    if exists:
        with open(args.keyname, 'rb') as data:
            bucket.Object(args.keyname).put(Body=data)
