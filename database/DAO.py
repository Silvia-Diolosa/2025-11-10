from database.DB_connect import DBConnect
from model import store
from model.order import Order

from model.store import Store


class DAO():
    @staticmethod
    def getAllStores():
        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM `stores` as s ORDER by s.store_name"
        """SELECT DISTINCT o.*
FROM stores s, orders o
WHERE s.store_id = o.store_id
AND s.store_name = "Santa Cruz Bikes" """

        cursor.execute(query)

        for row in cursor:
            results.append(Store(**row))

        cursor.close()
        conn.close()
        return results


    @staticmethod
    def getAllNodes(store):
        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """SELECT DISTINCT o.*
                    FROM stores s, orders o
                    WHERE s.store_id = o.store_id
                    AND s.store_name = %s """


        cursor.execute(query, (store.store_name,))

        for row in cursor:
            results.append(Order(**row))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getAllEdges(store, n):
        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """SELECT t1.id as id1, t2.id as id2, (t1.quantity + t2.quantity) / (TIMESTAMPDIFF(DAY, t1.data, t2.data)) as peso
FROM
(SELECT o.order_id as id, o.order_date as data, SUM(oi.quantity) as quantity
FROM stores s, orders o, order_items oi
WHERE s.store_id = o.store_id
AND s.store_name = %s
AND o.order_id = oi.order_id
GROUP BY o.order_id ) t1,
(SELECT o.order_id as id, o.order_date as data, SUM(oi.quantity) as quantity
FROM stores s, orders o, order_items oi
WHERE s.store_id = o.store_id
AND s.store_name = %s
AND o.order_id = oi.order_id
GROUP BY o.order_id  ) t2
WHERE TIMESTAMPDIFF(DAY, t1.data, t2.data) <= %s
AND t1.id<>t2.id  
AND t1.data < t2.data 
 GROUP BY t1.id, t2.id"""

        cursor.execute(query, (store.store_name, store.store_name, n))

        for row in cursor:
            results.append((row["id1"], row["id2"], row["peso"]))

        cursor.close()
        conn.close()
        return results


# SELECT o1.order_id AS id1, o2.order_id AS id2,
#                    ((SUM(oi.quantity) + SUM(oi2.quantity)) / DATEDIFF(o2.order_date, o1.order_date)) AS weight
#                     FROM
#                         orders o1, orders o2, order_items oi, order_items oi2
#                     WHERE
#                         o1.store_id = %s
#                         AND o1.store_id = o2.store_id
#                         AND oi.order_id = o1.order_id
#                         AND oi2.order_id = o2.order_id
#                         AND o1.order_date < o2.order_date
#                         AND DATEDIFF(o2.order_date, o1.order_date) <= %s
#                     GROUP BY
#                         o1.order_id, o2.order_id