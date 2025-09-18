class HeroWithItems:
    def __init__(self, base_hero_id: int, left_base_item_ids: list = [], right_base_item_ids: list = []):
        self.base_hero_id = base_hero_id
        self.left_item_ids = left_base_item_ids
        self.right_base_item_ids = right_base_item_ids