from seven_jd.jd.api.base import RestApi

class DataVenderSmsNotifyRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.approver_phone = None
			self.sign = None
			self.text_content = None
			self.task_inst_id = None
			self.url = None
			self.send_time = None
			self.full_content = None
			self.mkt_activity_id = None
			self.send_num = None
			self.mkt_activity_inst_id = None
			self.task_id = None
			self.strategy_inst_id = None
			self.sms_abTest_bRatio = None

		def getapiname(self):
			return 'jingdong.data.vender.sms.notify'

			





