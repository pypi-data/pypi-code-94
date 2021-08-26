# Created by Q-ays.
# whosqays@gmail.com


from elasticsearch_dsl import Document, InnerDoc, Text, Keyword, Integer, Float, Boolean, Ip, Object, Nested, Date, \
    GeoPoint

from datetime import datetime
import requests

class EnumType(InnerDoc):
    name = Text(fields={'keyword': Keyword()})  # 枚举名称
    code = Text(fields={'keyword': Keyword()})  # 枚举code
    order = Integer()  # 序号


class Phone(Text):
    pass


class Email(Text):
    pass


class EnumObj(Object):
    pass


def enumObj():
    return EnumObj(EnumType)


def text_keyword():
    return Text(fields={'keyword': Keyword()})


def doc_spawn(AM_HOST, **kwargs):
    class BaseDocument(Document):
        user_ = Nested()
        org_ = Nested()
        addTime_ = Date()
        updTime_ = Date()
        status_ = Text()

        @classmethod
        def field2index_set(cls):
            try:
                cls.init()
            except Exception as e:
                print('es 模型初始化失败，模型字段类型可能冲突')
                print(e)

            try:
                index = cls.Index.name
                # todo 存表结构 return 表id
                obj_in = {'index': index,
                          'status': kwargs.get('status', 'init'),
                          'types': kwargs.get('types')
                          }
                res = requests.post(
                    "{}/api/v1/index/index_add".format(AM_HOST), json=obj_in)
                if res.status_code == 200:
                    print(res.json(),"waht is res")
                    index_id = res.json().get('id')
                else:
                    print(res)
                    raise Exception('添加index表出错')

                datas = list()

                fields = cls._doc_type.mapping.properties._params.get(
                    'properties')

                i = 5
                for k in fields:
                    if k in ['user_', 'org_', 'status_', 'addTime_', 'updTime_']:
                        continue
                    fields_name = cls.filedName()
                    data = dict()
                    data['index'] = index
                    data['index_id'] = index_id
                    data['field'] = k
                    data['sort'] = i
                    data['name'] = fields_name.get(k,None)
                    if isinstance(fields[k], EnumObj):
                        data['types'] = 'enum'
                        data['properties'] = [
                            'code', 'value', 'name', 'label', 'order']
                    elif isinstance(fields[k], Phone):
                        data['name'] = '电话'
                        data['types'] = 'phone'
                    elif isinstance(fields[k], Email):
                        data['name'] = '邮箱'
                        data['types'] = 'email'
                    elif isinstance(fields[k], Date):
                        data['name'] = '日期'
                        data['types'] = 'date'
                    elif isinstance(fields[k], Integer):
                        data['types'] = 'int'
                    elif isinstance(fields[k], Ip):
                        data['types'] = 'ip'
                    elif isinstance(fields[k], Nested):
                        data['types'] = 'nested'
                    elif isinstance(fields[k], Boolean):
                        data['types'] = 'boolean'
                    # 这行代码需要放到最后的 else if
                    elif isinstance(fields[k], Text):
                        data['types'] = 'str'
                    else:
                        pass

                    datas.append(data)
                    i = i + 2

                res = requests.post(
                    "{}/api/v1/index/index_add".format(AM_HOST), json=datas)
                print(res.json())
            except Exception as e:
                print('字段和表存入pg 失败')
                print(e)

        def save(self, *args, **kwargs):
            if not self.addTime_:
                self.addTime_ = datetime.now()

            return super().save(*args, **kwargs)

    return BaseDocument
