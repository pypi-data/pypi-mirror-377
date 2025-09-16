from seven_jd.jd.api.base import RestApi

class LiveIsvOperationAnchorMessageSendRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.liveId = None
			self.message = None

		def getapiname(self):
			return 'jingdong.live.isvOperation.anchor.message.send'

			





