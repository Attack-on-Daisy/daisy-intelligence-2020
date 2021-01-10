from site_location import SiteLocationPlayer, Store, attractiveness_allocation
from random import randrange


class AodSemiGreedyPlayer(SiteLocationPlayer):
    """
    Custom semi-greedy player.

    Author: Juho Kim
    """

    SAMPLE_COUNT = 400
    FILTER_COUNT = 100
    ACTIVE_ROUND_COUNT = 4
    FIRST_TARGET = 0.8

    def __init__(self, player_id, config):
        super().__init__(player_id, config)

        self.round = 0

    def place_stores(self, slmap, store_locations, current_funds):
        self.round += 1

        if self.round > self.ACTIVE_ROUND_COUNT:
            return

        store_config = self.config['store_config']

        store_types = []

        while True:
            for store_type, store in sorted(store_config.items(), key=lambda item: -item[1]['capital_cost']):
                if current_funds >= store['capital_cost']:
                    store_types.append(store_type)
                    current_funds -= store['capital_cost']
                    break
            else:
                break

            if len(store_types) == self.config['max_stores_per_round']:
                break

        poss = []
        attractivenesses = {}

        for _ in range(self.SAMPLE_COUNT):
            x, y = randrange(0, slmap.size[0]), randrange(0, slmap.size[1])
            poss.append((x, y))

        poss = sorted(poss, key=lambda key: -slmap.population_distribution[key])[:self.FILTER_COUNT]

        for x, y in poss:
            attractivenesses[x, y] = self.get_attractiveness_allocation(slmap, store_locations, store_config,
                                                                        Store((x, y), 'small'))

        min_attractiveness = min(attractivenesses.values())
        max_attractiveness = max(attractivenesses.values())

        for x, y in poss:
            attractivenesses[x, y] = (attractivenesses[x, y] - min_attractiveness) / (
                        max_attractiveness - min_attractiveness)

        poss.sort(key=lambda key: attractivenesses[key])

        stores = []

        for store_type in store_types:
            if self.round > 1:
                pos = poss.pop()
            else:
                pos = poss.pop(int(len(poss) * self.FIRST_TARGET))

            store = Store(pos, store_type)
            stores.append(store)

        self.stores_to_place = stores

    def get_attractiveness_allocation(self, slmap, store_locations, store_conf, store):
        store_locations[self.player_id].append(store)
        alloc = attractiveness_allocation(slmap, store_locations, store_conf)
        score = (alloc[self.player_id] * slmap.population_distribution).sum()
        store_locations[self.player_id].pop()

        return score
