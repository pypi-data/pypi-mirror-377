from machkit.services.batches_service import BatchesService


class BatchesController:

    def __init__(self):
        self.service = BatchesService()

    def get_batch(self, batch_id):
        return self.service.get_batch(batch_id)

    def get_batches(self, requirement_id, state, search, page, per_page):
        return self.service.get_batches(requirement_id, state, search, page, per_page)

    def get_batches_simple(self, requirement_id, page, per_page):
        return self.service.get_batches_simple(requirement_id, page, per_page)

    def get_batches_config(self, batch_id):
        return self.service.get_batches_config(batch_id)

    def publish_batches(self, batch_ids):
        return self.service.publish_batches(batch_ids)

    def configs_batches(self, config):
        return self.service.configs_batches(config)
