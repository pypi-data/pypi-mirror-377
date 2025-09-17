import logging
import traceback

from re_common.baselibrary.utils.basepika import BasePika
from retry import retry

logging_logger = logging.getLogger(__name__)


class UseMq(object):

    def __init__(self, queue, qos=1):
        self.queue = queue
        self.qos = qos
        self.basepika = BasePika()
        self.basepika.set_default()
        self.basepika.connect()
        self.basepika.create_channel()
        self.basepika.queue_declare(queue=queue, durable=True)
        self.basepika.basic_qos(qos)
        self.properties = self.basepika.get_properties()

    def re_conn(self):
        """
        重新连接
        :return:
        """
        self.basepika.connect()
        self.basepika.create_channel()
        self.basepika.queue_declare(queue=self.queue, durable=True)
        self.basepika.basic_qos(self.qos)

    @retry(delay=5, backoff=2, max_delay=60 * 3, logger=logging_logger)
    def get_mq(self):
        try:
            if self.basepika.channel.is_closed:
                logging_logger.info("重连中......")
                self.re_conn()
                logging_logger.info("重连完成......")
            self.basepika.set_get_msg_callback(routing_key=self.queue, callback=self.callback, auto_ack=False)
            self.basepika.start_get_msg()
        except:
            traceback.print_exc()
            logging_logger.info("重连中......")
            self.re_conn()

    def callback(self, ch, method, properties, body):
        # print(type(body))
        # print(" [x] Received %r" % body)
        # body = body.decode()
        self.callback2(ch, method, properties, body)
        if self.basepika.auto_ack is False:
            self.basepika.basic_ack(ch, method)

    def callback2(self, ch, method, properties, body):
        pass

    @retry(delay=5, backoff=2, max_delay=60 * 3, logger=logging_logger)
    def send_mq(self, body, num=100):
        try:
            if self.basepika.get_queue_size(self.queue) < num:
                self.basepika.easy_send_msg(routing_key=self.queue,
                                            body=body,
                                            properties=self.properties)
                return True
            else:
                return False
        except:
            traceback.print_exc()
            logging_logger.info("重连中......")
            self.re_conn()
            return False

    def get_server_mq_num(self, num=100):
        if self.basepika.get_queue_size(self.queue) < num:
            return True
        else:
            return False

    def easy_send_mq(self, body):
        self.basepika.easy_send_msg(routing_key=self.queue,
                                    body=body,
                                    properties=self.properties)
