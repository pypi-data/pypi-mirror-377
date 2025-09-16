from seven_jd.jd.api.base import RestApi

class EclpGoodsTransportGoodsSerialNumberRuleRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.goodsNo = None
			self.serialNumberLength = None
			self.serialNumberLeftvalue = None
			self.serialNumberLeftLength = None
			self.serialNumberSuffixLength = None
			self.suffixValue = None
			self.type = None
			self.ruleIndex = None
			self.ruleIndexEnd = None
			self.ruleIndexValue = None
			self.manageType = None
			self.sellerSnRuleNo = None
			self.serialRuleType = None

		def getapiname(self):
			return 'jingdong.eclp.goods.transportGoodsSerialNumberRule'

			





