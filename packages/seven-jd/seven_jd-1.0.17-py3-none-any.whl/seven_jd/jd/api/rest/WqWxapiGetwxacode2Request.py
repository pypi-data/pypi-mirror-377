from seven_jd.jd.api.base import RestApi

class WqWxapiGetwxacode2Request(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.scene = None
			self.page = None
			self.width = None
			self.auto_color = None
			self.is_hyaline = None
			self.apptype = None

		def getapiname(self):
			return 'jingdong.wq.wxapi.getwxacode2'

			





