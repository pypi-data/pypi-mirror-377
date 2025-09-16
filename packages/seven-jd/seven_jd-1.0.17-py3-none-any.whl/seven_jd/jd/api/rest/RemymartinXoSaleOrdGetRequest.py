from seven_jd.jd.api.base import RestApi

class RemymartinXoSaleOrdGetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.eTime = None
			self.rowNum = None
			self.sTime = None
			self.pageNum = None

		def getapiname(self):
			return 'jingdong.remymartin.xo.sale.ord.get'

			





