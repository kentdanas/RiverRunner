class Prediction:
    def __init__(self, run_id, timestamp, fr_lb, fr, fr_ub):
        self.run_id = run_id
        self.timestamp = timestamp
        self.fr_lb = fr_lb
        self.fr = fr
        self.fr_ub = fr_ub

    def __str__(self):
        return 'run: %s, %s, lb: %s, fr: %s, ub: %s' % \
               (self.run_id, self.timestamp, self.fr_lb, self.fr, self.fr_ub)

    def __repr__(self):
        return '<Prediction> %s-%s' % (self.run_id, self.timestamp)

    def as_gvalue(self):
        return [
            str(self.run_id),
            str(self.timestamp),
            str(self.fr_lb),
            str(self.fr),
            str(self.fr_ub)
        ]