import os

import boto3
import pytest
import salt.utils.files
import salt.utils.hashutils
import salt.utils.s3
import yaml

# moto must be imported before boto3
from moto import mock_aws

from saltext.s3fs.fileserver import s3fs


@pytest.fixture
def bucket():
    """Return a test bucket name."""
    return "mybucket"


@pytest.fixture(scope="module")
def aws_creds():
    return {
        "aws_access_key_id": "testing",
        "aws_secret_access_key": "testing",
        "aws_session_token": "testing",
        "region_name": "us-east-1",
    }


@pytest.fixture(scope="function")
def s3(bucket, aws_creds):
    with mock_aws():
        conn = boto3.client("s3", **aws_creds)
        conn.create_bucket(Bucket=bucket)
        yield conn


def make_keys(bucket, conn, keys):
    for key, data in keys.items():
        conn.put_object(
            Bucket=bucket,
            Key=key,
            Body=data["content"],
        )


def verify_cache(bucket, expected):
    for key, data in expected.items():
        correct_content = data["content"]
        cache_file = s3fs._get_cached_file_name(bucket, "base", key)
        assert os.path.exists(cache_file)

        if correct_content is None:
            continue

        with salt.utils.files.fopen(cache_file) as f:
            content = f.read()
            assert correct_content == content


@mock_aws
def test_update(bucket, s3):
    """Tests that files get downloaded from s3 to the local cache."""

    # Set up __opts__ directly on the module
    s3fs.__opts__ = {
        "cachedir": "/tmp/test_cache",
        "s3.buckets": {"base": [bucket]},
        "s3.location": "us-east-1",
        "s3.s3_cache_expire": -1,
    }

    keys = {
        "top.sls": {"content": yaml.dump({"base": {"*": ["foo"]}})},
        "foo.sls": {"content": yaml.dump({"nginx": {"pkg.installed": []}})},
        "files/nginx.conf": {"content": "server {}"},
        "files/conf.d/foo.conf": {"content": "server {}"},
    }

    make_keys(bucket, s3, keys)
    s3fs.update()
    verify_cache(bucket, keys)

    # make a modification and update again - verify the change is retrieved
    keys["top.sls"]["content"] = yaml.dump({"base": {"*": ["foo", "bar"]}})
    make_keys(bucket, s3, keys)
    s3fs.update()
    verify_cache(bucket, keys)

    # verify that when files get deleted from s3, they also get deleted in
    # the local cache
    delete_file = "files/nginx.conf"
    del keys[delete_file]
    s3.delete_object(Bucket=bucket, Key=delete_file)

    s3fs.update()
    verify_cache(bucket, keys)

    cache_file = s3fs._get_cached_file_name(bucket, "base", delete_file)
    assert not os.path.exists(cache_file)

    # we want empty directories to get deleted from the local cache

    # after this one, `files` should still exist
    files_dir = os.path.dirname(cache_file)
    assert os.path.exists(files_dir)

    # but after the last file is deleted, the directory and any parents
    # should be deleted too
    delete_file = "files/conf.d/foo.conf"
    del keys[delete_file]
    s3.delete_object(Bucket=bucket, Key=delete_file)

    s3fs.update()
    verify_cache(bucket, keys)

    cache_file = s3fs._get_cached_file_name(bucket, "base", delete_file)
    assert not os.path.exists(cache_file)

    # after this, `files/conf.d` and `files` should be deleted
    conf_d_dir = os.path.dirname(cache_file)
    assert not os.path.exists(conf_d_dir)
    assert not os.path.exists(files_dir)


@mock_aws
def test_s3_hash(bucket, s3):
    """Verifies that s3fs hashes files correctly."""

    # Set up __opts__ directly on the module
    s3fs.__opts__ = {
        "cachedir": "/tmp/test_cache",
        "s3.buckets": {"base": [bucket]},
        "s3.location": "us-east-1",
        "s3.s3_cache_expire": -1,
    }

    keys = {
        "top.sls": {"content": yaml.dump({"base": {"*": ["foo"]}})},
        "foo.sls": {"content": yaml.dump({"nginx": {"pkg.installed": []}})},
        "files/nginx.conf": {"content": "server {}"},
    }

    make_keys(bucket, s3, keys)
    s3fs.update()

    for key, item in keys.items():
        cached_file_path = s3fs._get_cached_file_name(bucket, "base", key)
        item["hash"] = salt.utils.hashutils.get_hash(cached_file_path, s3fs.S3_HASH_TYPE)
        item["cached_file_path"] = cached_file_path

    load = {"saltenv": "base"}
    fnd = {"bucket": bucket}

    for key, item in keys.items():
        fnd["path"] = item["cached_file_path"]
        actual_hash = s3fs.file_hash(load, fnd)
        assert s3fs.S3_HASH_TYPE == actual_hash["hash_type"]
        assert item["hash"] == actual_hash["hsum"]


def test_cache_round_trip(bucket):
    # Set up __opts__ directly on the module
    s3fs.__opts__ = {
        "cachedir": "/tmp/test_cache",
        "s3.buckets": {"base": [bucket]},
        "s3.location": "us-east-1",
        "s3.s3_cache_expire": -1,
    }

    metadata = {"foo": "bar"}
    cache_file = s3fs._get_buckets_cache_filename()
    s3fs._write_buckets_cache_file(metadata, cache_file)
    assert s3fs._read_buckets_cache_file(cache_file) == metadata


def test_ignore_pickle_load_exceptions():
    #  TODO: parameterized test with patched pickle.load that raises the
    #  various allowable exception from _read_buckets_cache_file
    pass
