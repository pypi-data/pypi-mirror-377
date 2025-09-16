from seven_jd.jd.api.base import RestApi

class DataVenderSendDongdongChatMsgRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.task_id = None
			self.mkt_activity_inst_id = None
			self.strategy_inst_id = None
			self.mkt_activity_id = None
			self.approver_phone = None
			self.send_mesage = None
			self.send_time = None
			self.send_num = None
			self.task_inst_id = None
			self.activity_name = None

		def getapiname(self):
			return 'jingdong.data.vender.send.dongdong.chat.msg'

			





