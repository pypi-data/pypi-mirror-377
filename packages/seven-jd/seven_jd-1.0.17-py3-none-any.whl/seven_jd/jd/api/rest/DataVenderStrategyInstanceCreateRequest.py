from seven_jd.jd.api.base import RestApi

class DataVenderStrategyInstanceCreateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.mkt_activity_id = None
			self.strategy_id = None
			self.task_inst_id = None
			self.mkt_activity_inst_id = None
			self.task_id = None
			self.strategy_param = None
			self.instance_pack_type = None

		def getapiname(self):
			return 'jingdong.data.vender.strategy.instance.create'

			





