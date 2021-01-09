from site_location import SiteLocationPlayer, Store, attractiveness_allocation


class AodSemiGreedyPlayer(SiteLocationPlayer):
    """
    Custom semi-greedy player.

    Author: Juho Kim
    """

    SEPARATION_COUNT = 10
    ACTIVE_ROUND_COUNT = 5
    ATTRACTIVENESS_WEIGHT = 3
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
        densities = {}

        for x in range(slmap.size[0] // self.SEPARATION_COUNT // 2, slmap.size[0],
                       slmap.size[0] // self.SEPARATION_COUNT):
            for y in range(slmap.size[1] // self.SEPARATION_COUNT // 2, slmap.size[1],
                           slmap.size[1] // self.SEPARATION_COUNT):
                poss.append((x, y))
                attractivenesses[x, y] = self.get_attractiveness_allocation(slmap, store_locations, store_config,
                                                                            Store((x, y), 'small'))
                densities[x, y] = slmap.population_distribution[x, y]

        min_attractiveness = min(attractivenesses.values())
        max_attractiveness = max(attractivenesses.values())
        min_density = min(densities.values())
        max_density = max(densities.values())

        for x, y in poss:
            attractivenesses[x, y] = (attractivenesses[x, y] - min_attractiveness) / (
                        max_attractiveness - min_attractiveness)
            densities[x, y] = (densities[x, y] - min_density) / (max_density - min_density)

        weights = {(x, y): self.ATTRACTIVENESS_WEIGHT * attractivenesses[x, y] + densities[x, y] for x, y in poss}

        poss.sort(key=lambda key: weights[key])

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
