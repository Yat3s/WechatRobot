#!/usr/bin/env python
# coding: utf-8

from wxbot import *
import ConfigParser
import json

class TulingWXBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = ""
        self.robot_switch = True
        self.adminName = u'Yat3s'
        self.robotName = u'Aran'
        self.DEBUG = True

        try:
            cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')
            self.tuling_key = cf.get('main', 'key')
        except Exception:
            pass
        print 'tuling_key:', self.tuling_key

    def tuling_auto_reply(self, uid, msg):
        if self.tuling_key:
            url = "http://www.tuling123.com/openapi/api"
            user_id = uid.replace('@', '')[:30]
            body = {'key': self.tuling_key, 'info': msg.encode('utf8'), 'userid': user_id}
            r = requests.post(url, data=body)
            respond = json.loads(r.text)
            result = ''
            if respond['code'] == 100000:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')
            elif respond['code'] == 200000:
                result = respond['url']
            elif respond['code'] == 302000:
                for k in respond['list']:
                    result = result + u"【" + k['source'] + u"】 " +\
                        k['article'] + "\t" + k['detailurl'] + "\n"
            else:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')

            print '    ROBOT:', result
            return result
        else:
            return u"知道啦"


    def hand_admin_msg(self, msgContent, userId):
        replyMsg = u"欢迎主人，请吩咐!"
        stop_cmd = [u'stop', u'退下', u'走开', u'关闭', u'关掉', u'休息', u'滚开']
        start_cmd = [u'start', u'出来', u'启动', u'工作']
        findCmd = False;
        if self.robot_switch:
            for idx in stop_cmd:
                if idx == msgContent:
                    self.robot_switch = False
                    self.send_msg_by_uid(u'叶爸爸我滚去睡觉了', userId)
                    findCmd = True;
        else:
            for idx in start_cmd:
                if idx == msgContent:
                    self.robot_switch = True
                    self.send_msg_by_uid(u'叶爸爸我起来了', userId)
        if not findCmd:
            self.send_msg_by_uid(u'叶爸爸，' + self.tuling_auto_reply(userId, msgContent), userId)


    def handle_msg_all(self, msg):
        messgae_content = msg['content']['data']
        messgae_type_id = msg['msg_type_id']
        content_type_id = msg['content']['type']
        username = msg['user']['name']
        user_id = msg['user']['id']
        if self.DEBUG:
            print 'Content--> ', messgae_content
            print 'MessageTypeId--> ', messgae_type_id # 整个消息的类型
            print 'ContentTypeId--> ', content_type_id # 文本 图片类型等
            print 'UserName--> ', username
            print 'UserId--> ', user_id

        if not self.robot_switch and username != self.adminName:
            return
        if username == self.adminName: # Process admin command
            self.hand_admin_msg(messgae_content, user_id)
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 0:  # text message from contact
            self.send_msg_by_uid(self.tuling_auto_reply(msg['user']['id'], msg['content']['data']), msg['user']['id'])
        elif msg['msg_type_id'] == 3 and msg['content']['type'] == 0:  # group text message
            my_nickname = self.my_account['NickName']
            if self.DEBUG:
                print '------------ GROUP DEBUG --------------'
                print 'MyNickname', self.my_account['NickName']
                print 'Content', msg['content']
                print 'ContentDetail', msg['content']['detail']
                for detail in msg['content']['detail']:
                    print 'ContentDetailType',detail['type']
                    print 'ContentDetailValue', detail['value']
                print 'username', msg['content']['user']['name']
                print '------------ GROUP DEBUG --------------'

            if 'detail' in msg['content']:
                my_names = self.get_group_member_name(msg['user']['id'], self.my_account['UserName'])
                if my_names is None:
                    my_names = {}
                if 'NickName' in self.my_account and self.my_account['NickName']:
                    my_names['nickname2'] = self.my_account['NickName']
                if 'RemarkName' in self.my_account and self.my_account['RemarkName']:
                    my_names['remark_name2'] = self.my_account['RemarkName']

                is_at_me = False
                for detail in msg['content']['detail']:
                    # if detail['type'] == 'at':
                    for k in my_names:
                        if my_names[k] and my_names[k] in detail['value'] or self.robotName in detail['value']:
                            is_at_me = True
                            break
                if is_at_me:
                    src_name = msg['content']['user']['name']
                    if src_name == self.adminName:
                        self.hand_admin_msg(msg['content']['desc'], msg['user']['id'])
                    else :
                        reply = '@' + src_name + ' '
                        if msg['content']['type'] == 0:  # text message
                            reply += self.tuling_auto_reply(msg['content']['user']['id'], msg['content']['desc'])
                        else:
                            reply += u"对不起，我刚上二年级，只看得懂字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"
                        self.send_msg_by_uid(reply, msg['user']['id'])


def main():
    bot = TulingWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'

    bot.run()


if __name__ == '__main__':
    main()
