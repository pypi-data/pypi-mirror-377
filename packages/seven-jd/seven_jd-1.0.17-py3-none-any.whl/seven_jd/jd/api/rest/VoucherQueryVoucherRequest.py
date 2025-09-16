from seven_jd.jd.api.base import RestApi

class VoucherQueryVoucherRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.orderType = None
			self.businessNo = None
			self.sellerNo = None
			self.systemSource = None

		def getapiname(self):
			return 'jingdong.voucher.queryVoucher'

			





