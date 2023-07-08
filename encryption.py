import binascii
from bs4 import BeautifulSoup
import rsa
import time
import urllib3
# 禁用安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 加密类,用于加密密码,发送请求
class Encryption:
    def __init__(self, password, url, key_url, sessions):
        self.password = None  # 加密后的密码
        self.url = url
        self.key_url = key_url
        self.sessions = sessions
        self.time = int(time.time())  # 时间戳
        self.weibo_rsa_e = 65537  # 固定值
        self.modules = None
        self.exponent = None
        self.token = None
        self.temp_password = password  # 未加密的密码
        self.header = None
        self.request = None
        self.cookie = None

    # 获取公钥密码
    def get_public_key(self):
        # result = None
        # 学校的ssl证书有问题,所以verify=False
        result = self.sessions.get(self.key_url + str(self.time), verify=False).json()
        self.modules = result["modulus"]
        # 说实话 这也太那啥了 这居然是没用的 怪不得去年栽在这里
        # self.exponent = result["exponent"]

    # 获取CsrfToken
    def get_csrf_token(self):
        r = self.sessions.get(self.url + str(self.time), verify=False)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        self.token = soup.find('input', attrs={'id': 'csrftoken'}).attrs['value']

    # 加密密码
    def process_public(self):
        message = str(self.temp_password).encode()
        rsa_n = binascii.b2a_hex(binascii.a2b_base64(self.modules))
        key = rsa.PublicKey(int(rsa_n, 16), self.weibo_rsa_e)
        encropy_pwd = rsa.encrypt(message, key)  # 加密
        self.password = binascii.b2a_base64(encropy_pwd)

    # 加密
    def encrypt(self) -> None:
        self.get_public_key()
        self.get_csrf_token()
        self.process_public()
