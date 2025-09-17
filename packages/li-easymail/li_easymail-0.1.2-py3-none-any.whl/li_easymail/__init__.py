from .easymail import _Easymail as Easymail

easymail = Easymail()
easymail.sendmail = Easymail.SendMail(easymail)
