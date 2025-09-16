from seven_jd.jd.api.base import RestApi

class DataVenderLableDefineInfoQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.application_scenario = None
			self.begroup = None
			self.lversion = None

		def getapiname(self):
			return 'jingdong.data.vender.lable.define.info.query'

			





