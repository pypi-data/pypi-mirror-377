from seven_jd.jd.api.base import RestApi

class VopInvoiceQueryElectronicInvoiceDetailRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.jdOrderId = None
			self.ivcType = None

		def getapiname(self):
			return 'jingdong.vop.invoice.queryElectronicInvoiceDetail'

			





