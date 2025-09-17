
import os,time,hashlib
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, hmac as chmac



class S1:
    def __init__(self) -> None:
        self.__V=b"KeyisB-c-s-m1"
        self.__C={}

    def __derive(self, k:bytes, kh:bool=False):
        d=hashlib.sha3_512(k).digest() if not kh else k
        if d in self.__C:return self.__C[d]
        s=hashlib.sha3_512(self.__V+b"|salt|"+k).digest()
        hk=HKDF(algorithm=hashes.SHA3_512(),length=96,salt=s,info=self.__V+b"|HKDF|")
        o=hk.derive(k);v=(o[:32],o[32:]);self.__C[d]=v;return v

    def sign(self,k:bytes)->bytes:
        ek,mk=self.__derive(k);n=os.urandom(16);t=int(time.time()).to_bytes(8,"big")
        st=hashlib.sha3_512(k[32:]+hashlib.sha3_512(k).digest()).digest()
        m=t+os.urandom(32)+st
        c=Cipher(algorithms.ChaCha20(ek,n),None).encryptor().update(m)
        h=chmac.HMAC(mk,hashes.SHA3_512());h.update(self.__V+b"|HMAC|");h.update(n);h.update(c)
        return n+c+h.finalize()

    def verify(self,k:bytes,s:bytes,ttl:int=15,kh:bool=False)->bool:
        if len(s)<80:return False
        ek,mk=self.__derive(k,kh=kh);n,ct,tg=s[:16],s[16:-64],s[-64:]
        h=chmac.HMAC(mk,hashes.SHA3_512());h.update(self.__V+b"|HMAC|");h.update(n);h.update(ct)
        try:h.verify(tg)
        except: return False
        m=Cipher(algorithms.ChaCha20(ek,n),None).decryptor().update(ct)
        if len(m)<104:return False
        ts=int.from_bytes(m[:8],"big");now=int(time.time())
        if (now-ts if now>=ts else ts-now)>ttl:return False
        st=hashlib.sha3_512(k[32:]+hashlib.sha3_512(k).digest()).digest()
        return m.endswith(st)

s1 = S1()