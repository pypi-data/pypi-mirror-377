from machkit.controller.batches_controller import BatchesController
from machkit.controller.file_controller import FileController
from machkit.controller.label_controller import LabelController
from machkit.controller.requirement_controller import RequirementController
from machkit.controller.user_controller import UserController


class Datapp:
    """
    datapp工具入口
    """

    def __init__(self):
        self.userController = UserController()
        self.requirement = RequirementController()
        self.label = LabelController()
        self.batch = BatchesController()
        self.fileController = FileController()

    def login(self, account, password):
        """
        登录
        :param account:
        :param password:
        """
        return self.userController.login(account, password)

    def create_requirement(self, data):
        """
        创建需求
        :param data:
        :return:
        """
        return self.requirement.create(data)

    def update_requirement(self, data):
        """
        修改需求
        :param data:
        :return:
        """
        return self.requirement.patch(data)

    def get_requirement(self, requirement_id):
        """
        获取需求详情
        :param requirement_id:
        :return:
        """
        return self.requirement.get_detail(requirement_id)

    def get_requirements(self, page=1, per_page=10):
        """
        获取需求list
        :return:
        """
        return self.requirement.get_list(page, per_page)

    def get_label_type(self):
        """
        获取标注类型
        :return:
        """
        return self.label.get_label_type()

    def search_user(self, search, role=0):
        """
        搜索用户
        :param search:
        :param role: 用户角色，默认搜索全部 （1研究员、2DPM、3费用接口人、4需求方成员、5项目经理、6执行人员）
        """
        return self.userController.search_user(search, role)

    def current_user(self):
        """
        获取当前用户信息
        :return:
        """
        return self.userController.current_user()

    def get_batch(self, batch_id):
        """
        根据批次id获取批次信息
        :param batch_id: 批次ID
        :return:
        """
        return self.batch.get_batch(batch_id)

    def get_batches(self, requirement_id='', state=0, search='', page=1, per_page=10):
        """
        根据需求id或批次id/名称获取批次
        :param requirement_id: 需求id，可选
        :param state: 批次状态，可选（1导入中，2待执行，3执行中，4已完成，5冻结，6待发布）
        :param search: 批次ID/名称，可选
        :param page:
        :param per_page:
        :return:
        """
        return self.batch.get_batches(requirement_id, state, search, page, per_page)

    def get_batches_simple(self, requirement_id, page=1, per_page=10):
        """
        根据需求id获取批次
        :param requirement_id: 需求id，必填
        :param page: 选填，默认 1
        :param per_page: 选填，默认 10
        :return:
        """
        return self.batch.get_batches_simple(requirement_id, page, per_page)

    def get_batches_config(self, batch_id):
        """
        获取批次配置
        :param batch_id: 批次ID
        :return:
        """
        return self.batch.get_batches_config(batch_id)

    def publish_batches(self, batch_ids):
        """
        发布批次
        :param batch_ids: 批次id集合，如：[1187, 1186]
        :return:
        """
        return self.batch.publish_batches(batch_ids)

    def configs_batches(self, config):
        """
        批量配置批次
        :param config: 批次的配置信息，格式可参考test_batch.py中的create_configs_data
        :return:
        """
        return self.batch.configs_batches(config)

    def get_label_task(self, batch_id):
        """
        根据批次id获取任务信息
        :param batch_id: 批次id
        :return:
        """
        return self.label.get_label_task(batch_id)

    def download_cli(self, cli_type, target_path):
        """
        下载cli工具到本地
        :param cli_type: 工具类型（1众智、2越影linux、3越影mac）
        :param target_path: 目标存储路径
        :return:
        """
        return self.fileController.download_cli(cli_type, target_path)
