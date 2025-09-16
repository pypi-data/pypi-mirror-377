from seven_jd.jd.api.base import RestApi

class MarketSmscardFileUploadRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.fileName = None
			self.mediaUrl = None
			self.mediaType = None
			self.mediaName = None

		def getapiname(self):
			return 'jingdong.market.smscard.file.upload'

			





