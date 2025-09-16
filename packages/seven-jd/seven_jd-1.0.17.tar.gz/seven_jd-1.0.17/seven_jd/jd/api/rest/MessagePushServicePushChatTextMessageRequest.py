from seven_jd.jd.api.base import RestApi

class MessagePushServicePushChatTextMessageRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.accessToken = None
			self.aspid = None
			self.accessid = None
			self.fromPin = None
			self.fromApp = None
			self.fromClientType = None
			self.open_id_seller = None
			self.xid_seller = None
			self.toPin = None
			self.toApp = None
			self.toClientType = None
			self.open_id_buyer = None
			self.xid_buyer = None
			self.content = None
			self.chatinfo = None
			self.upid = None
			self.ver = None

		def getapiname(self):
			return 'jingdong.MessagePushService.pushChatTextMessage'

			





