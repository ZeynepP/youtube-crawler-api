import json
from datetime import datetime

def dump_bloom_filter(video_filter, bloom_file):
    dumps = video_filter.dumps()
    with open(bloom_file, "wb") as f:
        f.write(dumps)


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

