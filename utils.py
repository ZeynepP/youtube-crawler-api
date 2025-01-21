import configparser
import os
import os.path
import urllib.parse
from datetime import timezone, datetime, timedelta
from typing import Dict, Optional, Any

import certifi
import urllib3



def get_dates(published_before, published_after, time_interval, crawl_time_interval):
    if published_before:
        published_before = datetime.fromisoformat(published_before)
    else:
        published_before = datetime.utcnow() - timedelta(hours=time_interval)
        published_before = published_before.replace(hour=00, minute=00, second=00)

    if published_after:
        published_after = datetime.fromisoformat(published_after)
    else:
        published_after = published_before - timedelta(hours=crawl_time_interval)
        published_after = published_after.replace(hour=00, minute=00, second=00)
    return published_before, published_after


def dump_crawled_videos(ids, filename, folder, mode="a+"):
    file = os.path.join(folder, filename)
    out = '\n'.join(ids) + '\n'
    with open(file, mode) as f:
        f.write(out)
    return file


def get_crawled_videos(filename, folder):
    file = os.path.join(folder, filename)
    lines = []
    try:
        with open(file) as f:
            lines = f.readlines()
    except:
        pass
    return lines


def dump_bloom_filter(video_filter, bloom_file):
    dumps = video_filter.dumps()
    with open(bloom_file, "wb") as f:
        f.write(dumps)
def init(config_path):
    current_folder = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(current_folder, config_path)
    config = configparser.ConfigParser()
    config.read(config_file)

    data_dir = config['paths']['data-dir']
    video_dir = config['paths']['video-dir']
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    if not os.path.exists(video_dir):
        os.mkdir(video_dir)

    return config



def date_ranges(published_after, published_before, days: int = 7, is_historical: bool = False):

    # If is_historical is False, return a single range from after to before
    if not is_historical:
        return [(published_after, published_before)]

    # If is_historical is True, split into ranges of `days` duration
    ranges = []
    current = published_after
    while current < published_before:
        next_range = current + timedelta(days=days)
        if next_range > published_before:
            next_range = published_before
        ranges.append((current, next_range))
        current = next_range

    return ranges


def divide_chunks(lst, n):
    chunked_list = list()
    for i in range(0, len(lst), n):
        chunked_list.append(lst[i:i + n])
    return chunked_list


def divide_chunks_dict(data, n):
    chunked_dict_list = []
    temp_dict = {}
    for count, (key, value) in enumerate(data.items(), 1):
        temp_dict[key] = value
        if count % n == 0 or count == len(data):
            chunked_dict_list.append(temp_dict)
            temp_dict = {}
    return chunked_dict_list


def seconds_to_midnight_pacific_time():
    now_utc = datetime.utcnow()
    pacific_time = now_utc.astimezone(timezone("US/Pacific")).replace(tzinfo=None)
    midnight_pacific = datetime.combine(pacific_time, datetime.min.time())

    return (midnight_pacific - pacific_time).seconds


def add_query_argument(url, name, value=None, quote=True):
    if quote:
        name = urllib.parse.quote(name)

    if value == True or value is None:
        arg = name
    else:
        if quote:
            value = urllib.parse.quote(str(value))

        arg = name + "=" + value

    query = None
    fragment = None

    s = url.rsplit("#", 1)

    if len(s) > 1:
        url, fragment = s

    s = url.rsplit("?", 1)

    if len(s) > 1:
        url, query = s

    if query:
        query += "&" + arg
    else:
        query = arg

    url += "?" + query

    if fragment is not None:
        url += "#" + fragment

    return url


def create_pool_manager(
        parallelism: int = 1,
        num_pools: Optional[int] = None,
        insecure: bool = False,
        **kwargs
) -> urllib3.PoolManager:
    """
    Helper function returning a urllib3 pool manager with sane defaults.
    """

    manager_kwargs: Dict[str, Any] = {"timeout": urllib3.Timeout(
        connect=5, read=25
    )}

    if not insecure:
        manager_kwargs["cert_reqs"] = "CERT_REQUIRED"
        manager_kwargs["ca_certs"] = certifi.where()
    else:
        manager_kwargs["cert_reqs"] = "CERT_NONE"
        # manager_kwargs['assert_hostname'] = False

        urllib3.disable_warnings()

    manager_kwargs["maxsize"] = parallelism

    if num_pools is not None:
        manager_kwargs["num_pools"] = num_pools

    manager_kwargs.update(kwargs)

    return urllib3.PoolManager(**manager_kwargs)