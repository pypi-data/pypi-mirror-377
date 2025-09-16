from seven_jd.jd.api.base import RestApi

class DataVenderResultStrategyInstGetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.mkt_activity_id = None
			self.task_inst_id = None
			self.mkt_activity_inst_id = None
			self.task_id = None
			self.strategy_inst_id = None

		def getapiname(self):
			return 'jingdong.data.vender.result.strategy.inst.get'

			





