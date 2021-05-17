from confluent_kafka import Consumer, KafkaError, Producer
import Match
import configparser

def Kafka_Consumer_UserRecords(CONFIG):

    # 基本設定
    settings = {
        'bootstrap.servers': f'{CONFIG["KAFKA"]["HOST"]}',
        'group.id': CONFIG["KAFKA"]['TOPIC_1'],
        'client.id': 'client-1',
        'enable.auto.commit': True,
        'session.timeout.ms': 6000,
        'default.topic.config': {'auto.offset.reset': 'smallest'}
    }

    # 設定Consumer物件
    c = Consumer(settings)

    # 設定要Consum的topic
    c.subscribe([CONFIG["KAFKA"]['TOPIC_1']])

    try:
        while True:
            # 將kafka 上的資訊拉下來
            msg = c.poll(1)
            if msg is None:
                continue
            if not msg.error():
                # Test
                print('({0}, {1})'.format(msg.key(), msg.value()))

                # 將bytes轉換成string
                msg_key = msg.key().decode()
                msg_value = msg.value().decode()
                result = Match.Recipe_Match(CONFIG, msg_key, msg_value)

                return result

            elif msg.error().code() == KafkaError._PARTITION_EOF:
                print('End of partition reached {0}/{1}'.format(msg.topic(), msg.partition()))
            else:
                print('Error occured: {0}'.format(msg.error().str()))

    except KeyboardInterrupt:
        pass

    finally:
        c.close()

if __name__=="__main__":

    # 讀取Linebot、mysql、kafka連線資訊
    CONFIG = configparser.ConfigParser()
    CONFIG.read('config.ini')
    Kafka_Consumer_UserRecords(CONFIG)

