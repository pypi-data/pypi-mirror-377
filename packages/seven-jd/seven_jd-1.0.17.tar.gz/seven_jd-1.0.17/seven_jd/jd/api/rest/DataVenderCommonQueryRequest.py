from seven_jd.jd.api.base import RestApi

class DataVenderCommonQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.method = None
			self.input_para = None

		def getapiname(self):
			return 'jingdong.data.vender.common.query'

			





