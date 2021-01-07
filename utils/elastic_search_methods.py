from elasticsearch import Elasticsearch

class ElasticSearchUtils():

    # Launch the ES significant-text request and get the response
    @staticmethod
    def get_es_significant_texts_by_dates(es_port, es_index, timeout, articles_dates, field, max_nb_words):
        # Connect to the elastic cluster
        es = Elasticsearch([{'host':'localhost','port':es_port}],timeout=timeout)

        # Query the index
        res = es.search(index=es_index,body={
        "size":0,
        "query": {
            "bool": {
              "must": [{
                "terms": {
                  "published":articles_dates
                }
              }]
            }
        },
        "aggs": {
            "Significant texts": {
              "significant_text": {
                  "field": field,
                  "filter_duplicate_text": True,
                  "size": max_nb_words,
                  "exclude":[ "stock","update",
                               "monday","tuesday","wednesday","thursday","friday","saturday","sunday",
                               "today","yesterday","tomorrow","tonight","morning","night","afternoon",
                               "january","february","march","april","may","june","july","august","september", "october", "november","december"
                               ]
              }
            }

        }

        })
        # TODO : les 'exclude" doivent pas être en dur
        return ElasticSearchUtils.format_es_response(res)

    # Launch the ES significant-text request and get the response
    @staticmethod
    def get_es_significant_texts_by_dates_with_sampler(es_port, es_index, timeout, articles_dates, field, max_nb_words, sample_size):
        # Connect to the elastic cluster
        es = Elasticsearch([{'host':'localhost','port':es_port}],timeout=timeout)

        # Query the index
        res = es.search(index=es_index,body={
        "size":0,
        "query": {
            "bool": {
              "must": [{
                "terms": {
                  "published":articles_dates
                }
              }]
            }
        },
        "aggs": {
            "my_sample": {
              "sampler": {
                "shard_size": sample_size
              },
              "aggs": {
                "Significant texts": {
                    "significant_text": {
                        "field": field,
                        "filter_duplicate_text": True,
                        "size":max_nb_words,
                        "exclude":[ "stock","update",
                                   "monday","tuesday","wednesday","thursday","friday","saturday","sunday",
                                   "today","yesterday","tomorrow","tonight","morning","night","afternoon",
                                   "january","february","march","april","may","june","july","august","september", "october", "november","december"
                                   ]
                    }
                }
              }
            }
        }
        })
        # TODO : les 'exclude" doivent pas être en dur
        return ElasticSearchUtils.format_es_response_with_sampler(res)

    # Format the elastic search significant-text query response into the following :
    # [
    #   { 'significant_text': ... , "score": ...},
    #   ....
    #   { 'significant_text': ... , "score": ...}
    # ]
    @staticmethod
    def format_es_response(es_response):
        formatted_response = []
        for item in es_response['aggregations']['Significant texts']['buckets']:
            formatted_response.append(item['key'])
        return formatted_response

    # Format the elastic search significant-text query response into the following :
    # [
    #   { 'significant_text': ... , "score": ...},
    #   ....
    #   { 'significant_text': ... , "score": ...}
    # ]
    @staticmethod
    def format_es_response_with_sampler(es_response):
        formatted_response = []
        # TODO : my_sample doit pas être en dur
        for item in es_response['aggregations']['my_sample']['Significant texts']['buckets']:
            formatted_response.append(item['key'])
        return formatted_response


    # Reindex an existing index into a new index within a smaller date range
    def reindex(self, es_port, es_timeout, reindex_timeout,source_index,dest_index,gte_date,lt_date):
        # Connect to the elastic cluster
        es = Elasticsearch([{'host':'localhost','port':es_port}],timeout=es_timeout)

        # Query the index
        result = es.reindex(body=
                            {
                                "source":{
                                    "index":source_index,
                                    "query": {
                                      "range": {
                                        "@timestamp": {
                                          "gte": gte_date,
                                          "lt": lt_date
                                        }
                                      }
                                    }
                                },
                                "dest": {
                                    "index":dest_index
                                }
                            },wait_for_completion=True, request_timeout=reindex_timeout)

        print("ElasticSearchUtils.reindex : ",result)
