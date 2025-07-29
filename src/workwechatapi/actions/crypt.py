from Crypto.Cipher import AES
import hashlib
import base64
import struct
import socket


class WechatEDCryption:
    block_size = 32

    class Status:
        OK = 0
        ValidateSignature_Error = -40001
        ParseXml_Error = -40002
        ComputeSignature_Error = -40003
        IllegalAesKey = -40004
        ValidateCorpid_Error = -40005
        EncryptAES_Error = -40006
        DecryptAES_Error = -40007
        IllegalBuffer = -40008
        EncodeBase64_Error = -40009
        DecodeBase64_Error = -40010
        GenReturnXml_Error = -40011

    def __init__(self, token, AESKey, CorpID):
        self.token = token
        self.AESKey = base64.b64decode(AESKey + "=" * (-len(AESKey) % 4))
        self.CorpID = CorpID
        assert len(self.AESKey) == 32, "AESKey unvailable!"

    @staticmethod
    def getRandomStr(length=16):
        """生成随机字符串
        @param length: 随机字符串长度
        @return: 随机字符串
        """
        import random
        import string

        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def xml_extract(self, xmltext):
        """提取出xml数据包中的加密消息
        @param xmltext: 待提取的xml字符串
        @return: 提取出的加密消息字符串
        """
        try:
            import xml.etree.ElementTree as ET

            xml_tree = ET.fromstring(xmltext)
            encrypt = xml_tree.find("Encrypt")
            if encrypt is None or encrypt.text is None:
                return (
                    self.Status.ParseXml_Error,
                    "Error in WechatEDCryption.xml_extract: No Encrypt element found",
                )
            return self.Status.OK, encrypt.text
        except Exception as e:
            return (
                self.Status.ParseXml_Error,
                "Error in WechatEDCryption.xml_extract: " + str(e),
            )

    def xml_generate(self, encrypt, signature, timestamp, nonce):
        """生成xml消息
        @param encrypt: 加密后的消息密文
        @param signature: 安全签名
        @param timestamp: 时间戳
        @param nonce: 随机字符串
        @return: 生成的xml字符串
        """
        xml = f"""<xml>
        <Encrypt><![CDATA[{encrypt}]]></Encrypt>
        <MsgSignature><![CDATA[{signature}]]></MsgSignature>
        <TimeStamp><![CDATA[{timestamp}]]></TimeStamp>
        <Nonce><![CDATA[{nonce}]]></Nonce>
        </xml>"""
        return xml

    def getSHA1(self, timestamp, nonce, encrypt_text):
        """用SHA1算法计算安全签名
        @param timestamp: 时间戳
        @param nonce: 随机字符串
        @param encrypt: 加密后的消息密文
        @return: 安全签名
        """
        try:
            sha1 = hashlib.sha1()
            sha1.update(
                "".join(sorted([self.token, timestamp, nonce, encrypt_text])).encode(
                    "utf-8"
                )
            )
            return self.Status.OK, sha1.hexdigest()
        except Exception as e:
            return (
                self.Status.ComputeSignature_Error,
                "Error in MsgCrypt.getSHA1: " + str(e),
            )

    def pkcs7_encode(self, data: bytes) -> bytes:
        """对数据进行PKCS7填充"""
        padding = self.block_size - len(data) % self.block_size
        if padding == 0:
            padding = self.block_size
        return data + bytes([padding] * padding)

    def pkcs7_decode(self, data: str) -> str:
        """对数据进行PKCS7去填充"""
        padding = ord(data[-1])
        if padding < 1 or padding > self.block_size:
            padding = 0
        return data[:-padding]

    def ase_encrypt(self, text: str, receiver_id: str):
        """使用AES算法对文本进行加密
        @param text: 待加密的文本
        @param receiver_id: 接收者ID
        @return: 加密后的文本
        """
        try:
            encode_text = (
                self.getRandomStr().encode()
                + struct.pack("I", socket.htonl(len(text)))
                + text.encode()
                + receiver_id.encode()
            )
            encode_text = self.pkcs7_encode(encode_text)
            cipher = AES.new(self.AESKey, AES.MODE_CBC, self.AESKey[:16])
            encrypted_text = cipher.encrypt(encode_text)
            return self.Status.OK, base64.b64encode(encrypted_text).decode("utf-8")
        except Exception as e:
            return (
                self.Status.EncryptAES_Error,
                "Error in WechatEDCryption.ase_encrypt:" + str(e),
            )

    def ase_decrypt(self, text: str, receiver_id: str):
        try:
            cipher = AES.new(self.AESKey, AES.MODE_CBC, self.AESKey[:16])
            plain_text = cipher.decrypt(base64.b64decode(text))
        except Exception as e:
            return (
                self.Status.DecryptAES_Error,
                "Error in WechatEDCryption.ase_decrypt:" + str(e),
            )
        try:
            pad = plain_text[-1]
            content = plain_text[16:-pad]
            xml_len = socket.ntohl(struct.unpack("I", content[:4])[0])
            xml_content = content[4 : xml_len + 4].decode()
            from_receiveid = content[xml_len + 4 :].decode()
        except Exception as e:
            return (
                self.Status.IllegalBuffer,
                "Error in WechatEDCryption.ase_decrypt:" + str(e),
            )
        if from_receiveid != receiver_id:
            return (
                self.Status.ValidateCorpid_Error,
                "Error in WechatEDCryption.ase_decrypt: Unvaild receiveid!",
            )
        return self.Status.OK, xml_content

    def VerifyURL(self, msg_signature: str, timestamp: str, nonce: str, echostr: str):
        """验证URL的合法性
        @param msg_signature: 消息签名
        @param timestamp: 时间戳
        @param nonce: 随机字符串
        @param echostr: 随机字符串
        @return: 验证结果和原始echostr
        """
        try:
            ret, signature = self.getSHA1(timestamp, nonce, echostr)
            if ret != self.Status.OK:
                return (
                    self.Status.ComputeSignature_Error,
                    "Error in WechatEDCryption.VerifyURL: " + str(signature),
                )

            if signature != msg_signature:
                return (
                    self.Status.ValidateSignature_Error,
                    "Error in WechatEDCryption.VerifyURL: Signature mismatch!",
                )

            ret, decrypted_echostr = self.ase_decrypt(echostr, self.CorpID)
            if ret != self.Status.OK:
                return (
                    self.Status.ValidateSignature_Error,
                    "Error in WechatEDCryption.VerifyURL: " + str(decrypted_echostr),
                )

            return self.Status.OK, decrypted_echostr
        except Exception as e:
            return (
                self.Status.ValidateSignature_Error,
                "Error in WechatEDCryption.VerifyURL: " + str(e),
            )

    def encrypt_msg(self, text: str, nonce: str, timestamp: str = ""):
        """加密消息
        @param text: 待加密的文本
        @param timestamp: 时间戳
        @param nonce: 随机字符串
        @return: 加密后的消息和签名
        """
        ret, encrypted_text = self.ase_encrypt(text, self.CorpID)
        if ret != self.Status.OK:
            return ret, encrypted_text

        ret, signature = self.getSHA1(timestamp, nonce, encrypted_text)
        if ret != self.Status.OK:
            return ret, encrypted_text

        return self.Status.OK, self.xml_generate(
            encrypted_text, signature, timestamp, nonce
        )

    def decrypt_msg(self, text: bytes, signature: str, timestamp: str, nonce: str):
        """解密消息
        @param text: 待解密的文本
        @param signature: 消息签名
        @param timestamp: 时间戳
        @param nonce: 随机字符串
        @return: 解密后的消息内容
        """
        ret, encrypted_text = self.xml_extract(text)
        if ret != self.Status.OK or not encrypted_text:
            return ret, "Error in WechatEDCryption.decrypt_msg: " + str(encrypted_text)

        ret, decrypted_text = self.getSHA1(timestamp, nonce, encrypted_text)
        if ret != self.Status.OK:
            return ret, "Error in WechatEDCryption.decrypt_msg: " + str(decrypted_text)
        if signature != decrypted_text:
            return (
                self.Status.ValidateSignature_Error,
                "Error in WechatEDCryption.decrypt_msg: Signature mismatch!",
            )
        ret, decrypted_text = self.ase_decrypt(encrypted_text, self.CorpID)
        if ret != self.Status.OK:
            return ret, "Error in WechatEDCryption.decrypt_msg: " + str(decrypted_text)
        return self.Status.OK, decrypted_text
