from seven_jd.jd.api.base import RestApi

class EclpGoodsQueryGoodsInfoRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.isvGoodsNos = None
			self.goodsNos = None
			self.queryType = None
			self.barcodes = None
			self.pageNo = None
			self.pageSize = None

		def getapiname(self):
			return 'jingdong.eclp.goods.queryGoodsInfo'

			





