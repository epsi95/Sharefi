from pymongo import MongoClient
import datetime


class MongoDB(object):
    def __init__(self, connection_string):
        self.MONGO_CONNECTION_STRING = connection_string
        self.db = MongoClient(self.MONGO_CONNECTION_STRING)['ShareFiDB']

    def get_user_info(self, user_mobile_number):
        # user schema
        # user = {
        #   mobile: <mobile_number>,
        #   name: <name of the user>,
        #   mac: <mac address of the user>,
        #   created_at: <time of the user creation>,
        #   session_state: <ACTIVE/SUSPENDED>,
        #   session_start_dt: <session start datetime>,
        #   session_end_dt: <session end datetime>
        # }
        user_collection = self.db['users']
        return user_collection.find_one({"mobile": {"$eq": user_mobile_number}})

    def create_user(self, user_mobile_number, user_name, user_mac):
        user_collection = self.db['users']
        if user_collection.find_one({"mobile": {"$eq": user_mobile_number}}):
            return -1
        user = {
            "mobile": str(user_mobile_number),
            "name": user_name,
            "mac": user_mac,
            "created_at": datetime.datetime.now(),
            "session_state": "SUSPENDED",
            "session_start_dt": datetime.datetime.now(),
            "session_end_dt": datetime.datetime.now()
        }
        user_collection = self.db['users']
        return user_collection.insert_one(user).inserted_id

    def insert_order(self, order):
        order_collection = self.db['orders']
        return order_collection.insert_one(order).inserted_id

    def insert_captured_payment(self, captured_payment_details):
        payments_collection = self.db['captured_payments']
        return payments_collection.insert_one(captured_payment_details).inserted_id

    def get_order_details(self, order_id):
        order_collection = self.db['orders']
        return order_collection.find_one({"id": {"$eq": order_id}})

    def update_user_subscription(self, user_mobile_number):
        user_collection = self.db['users']
        session_end_dt = datetime.datetime.now() + datetime.timedelta(hours=24)
        user_collection.update_one({"mobile": {"$eq": user_mobile_number}},
                                          {"$set": {
                                              "session_state": "ACTIVE",
                                              "session_start_dt": datetime.datetime.now(),
                                              "session_end_dt": session_end_dt
                                          }
                                          })
        return session_end_dt
