from machkit.services.base_request import BaseRequest, GET_BATCHES, POST_BATCHES_PUBLISH, GET_BATCHES_CONFIG, \
    GET_BATCH, POST_BATCHES_CONFIGS, GET_BATCHES_SIMPLE


class BatchesService:

    def get_batch(self, batch_id):
        uri = GET_BATCH.format(batchId=batch_id)
        res, data = BaseRequest('GET', uri, {}).request()
        re_data = {}
        if res['code'] == 10000:
            re_data = {
                'id': data['id'],
                'name': data['name'],
                'state': data['state'],
                'state_desc': data['state_desc'],
                'label_type_id': data['task_type_id'],
            }
        return res, re_data

    def get_batches(self, requirement_id, state, search, page, per_page):
        params = {
            "page": page,
            "per_page": per_page
        }
        if requirement_id:
            params['requirement_id'] = requirement_id
        if state > 0:
            params['state'] = state
        if search:
            params['search'] = search
        res, data = BaseRequest('GET', GET_BATCHES, params).request()
        re_list = []
        pagination = {}
        if res['code'] == 10000:
            pagination = data['pagination']
            for item in data['items']:
                re_list.append({
                    'id': item['id'],
                    'name': item['name'],
                    'state': item['state'],
                    'state_desc': item['state_desc'],
                    'label_type_id': item['task_type_id'],
                })
        return res, {'pagination': pagination, 'items': re_list}

    def get_batches_simple(self, requirement_id, page, per_page):
        params = {
            "requirement_id": requirement_id,
            "page": page,
            "per_page": per_page
        }
        res, data = BaseRequest('GET', GET_BATCHES_SIMPLE, params).request()
        re_list = []
        if res['code'] == 10000:
            item_list = data['data']
            for item in item_list:
                re_list.append({
                    'id': item['id'],
                    'name': item['name'],
                    'state_desc': item['state_desc']                })
        return res, {'items': re_list}

    def get_batches_config(self, batch_id):
        uri = GET_BATCHES_CONFIG.format(batchId=batch_id)
        return BaseRequest('GET', uri, {}).request()

    def publish_batches(self, batch_ids):
        body = {
            "batch_ids": batch_ids
        }
        return BaseRequest('POST', POST_BATCHES_PUBLISH, {}, body=body).request()

    def configs_batches(self, config):
        return BaseRequest('POST', POST_BATCHES_CONFIGS, {}, body=config).request()
