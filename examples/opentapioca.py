import requests
import sys

OPEN_TAPIOCA_URL = "https://opentapioca.org/api/annotate"
AFFILIATION = 'University of Chile' # Default

def request(affiliation=AFFILIATION):
    query = {'query': affiliation}
    res = requests.get(OPEN_TAPIOCA_URL, query)
    response = res.json()
    if response['annotations'][0]['best_qid'] is not None:
        return response['annotations'][0]['best_qid']

    else:
        return response['annotations'][0]['tags'][0]['id']

if __name__ == "__main__":
    try:
        affiliation = ' '.join(sys.argv[1:])
        print(f'wd:{request(affiliation)}')

    except:
        print(f'wd:{request()}')