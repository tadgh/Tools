
class Book():
    def __init__(self, name, author, seen, rank, category):
        self.name = name
        self.author = author
        self.last_seen = seen
        self.first_seen = seen
        self.highest_rank = rank
        self.category = category

    def update(self, seen, rank):
        if seen > self.last_seen:
            self.last_seen = seen

        if rank < self.highest_rank:
            self.highest_rank = rank;

    def __repr__(self):
        return self.name
