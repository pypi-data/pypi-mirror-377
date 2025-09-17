import sys,os



sys.path.append("/Users/garry/PycharmProjects/data-service-sdk")
data_serice_sdk = os.path.abspath(".")
sys.path.append(data_serice_sdk)
os.environ.setdefault("HOME",data_serice_sdk)
from machkit.services.base_request import check_IP
from machkit.machkit import Datapp


if __name__ == '__main__':
    os.environ["DATAPP_KIT_DEBUG"] = 'on'
    datapp = Datapp()
    # test account
    # res, data = datapp.login("13333330003", "test123")
    # res, data = datapp.login("17600206307", "test7890")
    # print(res)
    # res, data = datapp.login("18610928883", "21151091321197")
    # res, data = datapp.login("15185055472", "megviiHEXIN02000000")
    # print(res, data)
    print("**********")
    check_IP()
