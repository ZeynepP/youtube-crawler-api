import json
from datetime import datetime

from bloomfilter import BloomFilter


def dump_bloom_filter(video_filter, bloom_file):
    dumps = video_filter.dumps()
    with open(bloom_file, "wb") as f:
        f.write(dumps)


def get_bloom_filter(bloom_path):
    try:
        with open(bloom_path, "rb") as f:
            video_filter = BloomFilter.loads(f.read())
    except:
        video_filter = BloomFilter(expected_insertions=500, err_rate=0.01)

    return video_filter

def generate_file_name(platform, seed_id=None, seed_name=None, start_date=None, end_date=None):
    """
    Generete a file name seed_id_seedname_retrieved_date
    :return: string : file name
    """
    date = "_"
    if start_date and end_date:
        date = f"_from_{start_date}_to_{end_date}_"
    if seed_name:
        return f'{platform}_{seed_id}_{seed_name.replace(" ", "_")}{date}retrieved_{datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")}.jsonl'

    elif seed_id:
        return f'{platform}_{seed_id}_from_{start_date}{date}retrieved_{datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")}.jsonl'

    else:
        return f'{platform}{date}retrieved_{datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")}.jsonl'



def write_raw_list(output_path, results):
    # try:
    #     with jsonlines.open(output_path, 'a+') as writer:
    #         writer.write_all(results)
    # except Exception as e:
    #     raise e
    try:
        with open(output_path, 'a+', encoding="utf-8") as outfile:
            for res in results:
                json.dump(res, outfile, ensure_ascii=False)
                outfile.write('\n')

    except Exception as e:
        raise e


def write_raw_data(output_path, phh_id, seed_id, results, collection, crawled_date=None):
    """
    :param output_path: path to output file
    :param seed_id: seed_id for the results
    :param results: list of results as json
    :return: None
    """
    if crawled_date is None:
        crawled_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),

    try:
        with open(output_path, 'a+', encoding="utf-8") as outfile:

            for res in results:
                temp = {
                    "phh_id": str(phh_id),
                    "seed_id": str(seed_id),
                    "crawled_date": crawled_date,  # strftime("%Y-%m-%dT%H:%M:%SZ")
                    "collection": collection,
                    "data": res

                }
                json.dump(temp, outfile, ensure_ascii=False)
                outfile.write('\n')

    except Exception as e:
        raise e
