from seven_jd.jd.api.base import RestApi

class EclpSerialQuerySerialBySkuAndSerialRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.goodsNo = None
			self.goodsSID = None
			self.queryType = None

		def getapiname(self):
			return 'jingdong.eclp.serial.querySerialBySkuAndSerial'

			





