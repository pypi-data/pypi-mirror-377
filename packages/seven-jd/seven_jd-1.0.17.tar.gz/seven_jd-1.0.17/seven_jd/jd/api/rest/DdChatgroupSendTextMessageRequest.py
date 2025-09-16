from seven_jd.jd.api.base import RestApi

class DdChatgroupSendTextMessageRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.id = None
			self.sender = None
			self.content = None
			self.groupId = None
			self.sendTime = None
			self.gid = None

		def getapiname(self):
			return 'jingdong.dd.chatgroup.sendTextMessage'

			





