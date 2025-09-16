from seven_jd.jd.api.base import RestApi

class MarketSmscardFileQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.mediaFileId = None

		def getapiname(self):
			return 'jingdong.market.smscard.file.query'

			





