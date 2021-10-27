import json
import sys
import uuid

from elasticsearch import Elasticsearch

def main(file_name):
    es = Elasticsearch()

    with open(file_name) as f:
        for i, line in enumerate(f):
            paper = json.loads(line)
            es.index(
                index='papers',
                doc_type='paper',
                id=uuid.uuid4(),
                body=paper
            )
            if not i%1000:
                print(
                    f'{i} docs indexed.',
                    end='\r'
                )

if __name__ == "__main__":
    main(sys.argv[1])
