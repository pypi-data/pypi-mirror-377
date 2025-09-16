from seven_jd.jd.api.base import RestApi

class WareWriteUpdateWareSaleAttrvalueAliasRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.wareId = None
			self.props = None

		def getapiname(self):
			return 'jingdong.ware.write.updateWareSaleAttrvalueAlias'

			
	

class SkuProp(object):
		def __init__(self):
			"""
			"""
			self.attrId = None
			self.attrValues = None
			self.attrValueAlias = None





