
class ScoringMetrics():
    @staticmethod
    def jaccard_similarity(a:list,b:list):
        intersection = len(set(a).intersection(set(b)))
        union = len(a) + len(b) - intersection
        return intersection / union
