from seven_jd.jd.api.base import RestApi

class EclpGoodsQueryGoodsByPageAndTimeRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.isvGoodsNos = None
			self.goodsNos = None
			self.pageNo = None
			self.pageSize = None
			self.updateTimeStart = None
			self.updateTimeEnd = None

		def getapiname(self):
			return 'jingdong.eclp.goods.queryGoodsByPageAndTime'

			





