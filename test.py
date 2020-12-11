# Import packages
from elasticsearch import Elasticsearch
import json

# Connect to the elastic cluster
es = Elasticsearch([{'host':'localhost','port':9200}],timeout=30)

# Query the index
res = es.search(index='articles_20190225_20201025',body={
 "size":0,
  "query": {
    "range": {
      "@timestamp": {
        "gte": "2020-05-01T00:00:00",
        "lt": "2020-09-30T00:00:00"
      }
    }
  },

  "aggs": {
    "top_feeds": {
      "terms": {
         "field" : "Feed.keyword",
         "size":291
      },
      "aggs": {
        "latest_articles_per_feed": {
          "top_hits": {
            "_source": ["published","title"],
            "sort": [
              {
                "published": {
                  "order": "desc"
                }
              }
            ],
            "size": 1
          }
        }
      }
    }
  }

})

with open('latest_article_per_feed_20200501_20200930.json', 'w') as f:
    json.dump(res, f)
