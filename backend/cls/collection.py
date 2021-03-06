import datetime
import json
import time

from pandas import read_sql

from cls.book import Book
from cls.user import User
from lib.sql_linker import connect_sys_db, mysql


class Collection:
    def __init__(self, id):
        self._id = id

    # Update existed collection's name
    def update_collection_name(self, user_id, new_name):
        # SQL
        conn = connect_sys_db()
        query = "SELECT * FROM collections WHERE (user_id = \'{user_id}\' AND name = \'{name}\')".format(
            user_id=user_id,
            name=new_name
        )
        db_result = read_sql(sql=query, con=conn)
        # Is new collection name already exist
        if not db_result.empty:
            return False, 'This collection already existed'
        # SQL
        query = "UPDATE collections SET name = \'{name}\' WHERE (user_id = \'{user_id}\' AND id = \'{id}\')".format(
            name=new_name,
            user_id=user_id,
            id=self._id
        )
        with mysql(conn) as cursor:
            cursor.execute(query)
        return True, 'Collection update successfully'

    # Get list of books in collection
    def get_book_in_collection(self):
        # SQL
        conn = connect_sys_db()
        query = "SELECT user_id FROM collections WHERE id = \'{collection_id}\'".format(
            collection_id=self._id
        )
        db_result = read_sql(sql=query, con=conn)
        user_id = db_result.iloc[0].user_id

        # SQL
        query = "SELECT * FROM collects WHERE collection_id = \'{collection_id}\'".format(
            collection_id=self._id
        )
        db_result = read_sql(sql=query, con=conn)
        json_str = db_result.to_json(orient='index')
        ds = json.loads(json_str)
        result = []

        for index in ds:
            finish_date = Collection.get_book_read_date(user_id, ds[index]['book_id'])
            # post finish_time if finish
            if finish_date != 0:
                ds[index]['finish_time'] = finish_date
            result.append(ds[index])
        return result

    # Add book to existed collection
    def add_book_to_collection(self, book_id):
        # SQL
        conn = connect_sys_db()
        query = "SELECT * FROM collects WHERE (collection_id = \'{collection_id}\' and book_id = \'{book_id}\')".format(
            collection_id=self._id,
            book_id=book_id,
        )
        db_result = read_sql(sql=query, con=conn)
        # Is book already existed in collection
        if not db_result.empty:
            return 201, "This book already existed in this collection"
        # SQL
        query = "INSERT INTO collects VALUES(\'{book_id}\', \'{collection_id}\', \'{collect_time}\')".format(
            book_id=book_id,
            collection_id=self._id,
            collect_time=datetime.datetime.utcnow()
        )
        with mysql(conn) as cursor:
            cursor.execute(query)
        return 200, "Add book to collection successfully"

    # Delete existed book in collection
    def delete_book_in_collection(self, book_id):
        # SQL
        conn = connect_sys_db()
        query = "SELECT * FROM collects WHERE (collection_id = \'{collection_id}\' and book_id = \'{book_id}\')".format(
            collection_id=self._id,
            book_id=book_id,
        )
        db_result = read_sql(sql=query, con=conn)
        # Is book exist in this collection
        if db_result.empty:
            return False
        # SQL
        query = "DELETE FROM collects WHERE (collection_id = \'{collection_id}\' AND book_id = \'{book_id}\')".format(
            book_id=book_id,
            collection_id=self._id
        )
        with mysql(conn) as cursor:
            cursor.execute(query)
        return True

    # Move book to another collection
    def move_book_to_another_collection(self, new_collection_id, book_id):
        # SQL
        conn = connect_sys_db()
        query = "UPDATE collects SET collection_id = \'{new_collection_id}\' WHERE (book_id = \'{book_id}\' AND collection_id = \'{old_collection_id}\')".format(
            new_collection_id=new_collection_id,
            old_collection_id=self._id,
            book_id=book_id
        )
        with mysql(conn) as cursor:
            cursor.execute(query)

    # Get collection's name
    def get_collection_name(self):
        # SQL
        conn = connect_sys_db()
        query = "SELECT name as collection_name FROM collections WHERE id = \'{id}\'".format(
            id=self._id
        )
        db_result = read_sql(sql=query, con=conn)
        return db_result.iloc[0].collection_name

    # -------------------------------------- Help Func -------------------------------------
    # Is collection existed by user_id and collection_id
    @staticmethod
    def is_collection_exists_by_both_id(user_id, collection_id):
        # SQL
        conn = connect_sys_db()
        query = "SELECT * FROM collections WHERE (user_id = \'{user_id}\' AND id = \'{id}\')".format(
            user_id=user_id,
            id=collection_id
        )
        db_result = read_sql(sql=query, con=conn)
        if db_result.empty:
            return False
        else:
            return True

    # Is collection exist by collection_id
    @staticmethod
    def is_collection_exists_by_id(collection_id):
        # SQL
        conn = connect_sys_db()
        query = "SELECT * FROM collections WHERE id = \'{id}\'".format(
            id=collection_id
        )
        db_result = read_sql(sql=query, con=conn)
        if db_result.empty:
            return False
        else:
            return True

    # Is collection existed by user_id and collection_name
    @staticmethod
    def is_collection_exists_by_name(user_id, collection_name):
        # SQL
        conn = connect_sys_db()
        query = "SELECT * FROM collections WHERE (user_id = \'{user_id}\' AND name = \'{collection_name}\')".format(
            user_id=user_id,
            collection_name=collection_name
        )
        db_result = read_sql(sql=query, con=conn)
        if db_result.empty:
            return False
        else:
            return True
    # -----------------------------------------------------------------------------------

    @staticmethod
    def get_collection_id_by_name(user_id, collection_name):
        conn = connect_sys_db()
        query = "SELECT id FROM collections WHERE (user_id = \'{user_id}\' AND name = \'{collection_name}\')".format(
            user_id=user_id,
            collection_name=collection_name
        )
        db_result = read_sql(sql=query, con=conn)
        return db_result.iloc[0].id

    # Get all collection of user
    @staticmethod
    def get_user_collection(user_id):
        # Is user exist
        if not User.is_user_exists_by_id(user_id):
            return None
        # SQL
        conn = connect_sys_db()
        query = "SELECT id, user_id, name, creation_time FROM collections WHERE user_id = \'{user_id}\'".format(
            user_id=user_id
        )
        db_result = read_sql(sql=query, con=conn)
        json_str = db_result.to_json(orient='index')
        ds = json.loads(json_str)
        result = []
        for index in ds:
            if ds[index]['name'] == "Read":
                continue
            # Add book's number and number of read book in collection to result
            ds[index]['book_num'] = Collection.get_num_book_collection(int(ds[index]['id']))
            ds[index]['finished_num'] = Collection.get_num_read_collection(user_id, int(ds[index]['id']))
            result.append(ds[index])
        return result

    # Create new collection
    @staticmethod
    def post_new_collection(user_id, name):
        # SQL
        conn = connect_sys_db()
        query = "SELECT * FROM collections WHERE (user_id = \'{user_id}\' AND name = \'{name}\')".format(
            user_id=user_id,
            name=name
        )
        db_result = read_sql(sql=query, con=conn)
        # If collection's name already existed
        if db_result.empty:
            query = "INSERT INTO collections VALUES(0,\'{user_id}\',\'{name}\',\'{time}\')".format(
                user_id=user_id,
                name=name,
                time=datetime.datetime.utcnow()
            )
            with mysql(conn) as cursor:
                cursor.execute(query)
            return True
        else:
            return False

    # Get readcollection's id of user
    @staticmethod
    def get_readcollection_id(user_id):
        # SQL
        conn = connect_sys_db()
        query = "SELECT id FROM collections WHERE (user_id = \'{user_id}\' and name = 'read')".format(
            user_id=user_id
        )
        db_result = read_sql(sql=query, con=conn)
        if db_result.empty:
            return None
        else:
            return db_result.iloc[0].id

    # Mark certain book as read
    @staticmethod
    def mark_as_read(user_id, book_id, date):
        read_collection_id = Collection.get_readcollection_id(user_id)
        date = date + "-10 10:00:00"
        print(date)
        # SQL
        conn = connect_sys_db()
        query = "INSERT INTO collects VALUES(\'{book_id}\', \'{collection_id}\', \'{collect_time}\')".format(
            book_id=book_id,
            collection_id=read_collection_id,
            # collect_time="2020-06-29 06:06:18.423409"
            collect_time=date
        )
        with mysql(conn) as cursor:
            cursor.execute(query)

    @staticmethod
    def is_book_read(user_id, book_id):
        collection_id = Collection.get_readcollection_id(user_id)
        # SQL
        conn = connect_sys_db()
        query = "SELECT book_id FROM collects WHERE (book_id = \'{book_id}\' AND collection_id = \'{collection_id}\')".format(
            book_id=book_id,
            collection_id=collection_id
        )
        db_result = read_sql(sql=query, con=conn)
        if db_result.empty:
            return False
        else:
            return True

    @staticmethod
    def mark_as_unread(user_id, book_id):
        read_collection_id = Collection.get_readcollection_id(user_id)
        # SQL
        conn = connect_sys_db()
        query = "DELETE FROM collects WHERE (collection_id = \'{collection_id}\' AND book_id = \'{book_id}\')".format(
            book_id=book_id,
            collection_id=read_collection_id,
        )
        with mysql(conn) as cursor:
            cursor.execute(query)

    # Get number of books which have been read in collection
    @staticmethod
    def get_num_read_collection(user_id, collection_id):
        read_collection_id = Collection.get_readcollection_id(user_id)
        # SQL
        conn = connect_sys_db()
        query = "select book_id from(select book_id from collects where collection_id = \'{collection_id}\' UNION all select book_id from collects where collection_id = \'{read_collection_id}\')a group by book_id having count(*) > 1".format(
            collection_id=collection_id,
            read_collection_id=read_collection_id
        )
        db_result = read_sql(sql=query, con=conn)
        return int(db_result.size)

    # Get number of books in certain collection
    @staticmethod
    def get_num_book_collection(collection_id):
        # SQL
        conn = connect_sys_db()
        query = "SELECT count(*) as num FROM collects WHERE collection_id = \'{collection_id}\'".format(
            collection_id=collection_id
        )
        db_result = read_sql(sql=query, con=conn)
        return int(db_result.iloc[0].num)

    # Get read_date of certain book
    @staticmethod
    def get_book_read_date(user_id, book_id):
        read_collection_id = Collection.get_readcollection_id(user_id)
        # SQL
        conn = connect_sys_db()
        query = "SELECT * FROM collects WHERE (collection_id = \'{collection_id}\' AND book_id = \'{book_id}\')".format(
            collection_id=read_collection_id,
            book_id=book_id
        )
        db_result = read_sql(sql=query, con=conn)
        # This book is existed in this collection
        if db_result.empty:
            return 0
        json_str = db_result.to_json(orient='index')
        ds = json.loads(json_str)
        result = []
        for index in ds:
            return ds[index]['collect_time']
        return 0

    # Get number of collections of user
    @staticmethod
    def get_num_collection(user_id):
        # SQL
        conn = connect_sys_db()
        query = "SELECT count(*) as num FROM collections WHERE (user_id = \'{user_id}\')".format(
            user_id=user_id
        )
        db_result = read_sql(sql=query, con=conn)
        return int(db_result.iloc[0].num) - 1

    # Get book added history
    @staticmethod
    def get_recent_added_books(user_id):
        conn = connect_sys_db()
        query = "SELECT book_id, max(collect_time) as latest FROM collections \
        JOIN collects ON collections.id = collects.collection_id WHERE user_id = \'{user_id}\' \
        AND name != 'read' GROUP BY book_id ORDER BY latest DESC".format(
            user_id=user_id
        )
        db_result = read_sql(sql=query, con=conn)
        json_str = db_result.to_json(orient='index')
        ds = json.loads(json_str)
        result = []
        for index in ds:
            book = Book(ds[index]['book_id'])
            book_info = book.get_info()
            # Add book's title and cover_url to result
            ds[index]['title'] = book_info.title
            ds[index]['book_cover_url'] = book_info.book_cover_url
            result.append(ds[index])
        return result

    # Delete existed collection
    @staticmethod
    def delete_collection(collection_id):
        # SQL
        conn = connect_sys_db()
        query = "DELETE FROM collections WHERE (id = \'{id}\')".format(
            id=collection_id
        )
        with mysql(conn) as cursor:
            cursor.execute(query)

    # Get list of books in collection
    @staticmethod
    def get_read_history(user_id):
        collection_id = Collection.get_readcollection_id(user_id)
        # SQL
        conn = connect_sys_db()
        query = "SELECT book_id FROM collects WHERE collection_id = \'{collection_id}\'".format(
            collection_id=collection_id
        )
        db_result = read_sql(sql=query, con=conn)
        json_str = db_result.to_json(orient='index')
        ds = json.loads(json_str)
        result = []
        for index in ds:
            finish_date = Collection.get_book_read_date(user_id, ds[index]['book_id'])
            # Add book's finish_time and title and cover_url to result
            ds[index]['finish_time'] = finish_date
            book = Book(ds[index]['book_id'])
            ds[index]['book_title'] = book.get_info().title
            ds[index]['book_cover_url'] = book.get_info().book_cover_url

            # Reformat result need for front-end
            # timeArray = time.strptime(finish_date, "%Y-%m-%d %H:%M:%S")
            date = datetime.datetime.fromtimestamp(int(finish_date) / 1000)
            target, finish_num, finish_flag = Collection.get_tag(user_id, date.year, date.month)
            ds[index]['tag'] = {'target': target, 'finish_num': finish_num, 'finish_flag': finish_flag}
            result.append(ds[index])
        return result

    @staticmethod
    # Get list of books read in certain month
    def get_read_history_by_date(user_id, year, month):
        # set default start date
        start_date = str(year) + "-" + str(month) + "-01 00:00:00"
        # set default finish date
        if month is 12:
            finish_date = str(year) + "-" + str(1) + "-01 00:00:00"
        else:
            finish_date = str(year) + "-" + str(month + 1) + "-01 00:00:00"
        # date -> timestamp
        start_timestamp = int(time.mktime(time.strptime(start_date, "%Y-%m-%d %H:%M:%S"))) * 1000
        finish_timestamp = int(time.mktime(time.strptime(finish_date, "%Y-%m-%d %H:%M:%S"))) * 1000
        collection_id = Collection.get_readcollection_id(user_id)
        # SQL
        conn = connect_sys_db()
        query = "SELECT book_id FROM collects WHERE collection_id = \'{collection_id}\'".format(
            collection_id=collection_id
        )
        db_result = read_sql(sql=query, con=conn)
        json_str = db_result.to_json(orient='index')
        ds = json.loads(json_str)
        result = []
        for index in ds:
            finish_date = Collection.get_book_read_date(user_id, ds[index]['book_id'])
            # Compare finish time to make sure whether this book is finished in this month
            if start_timestamp <= finish_date < finish_timestamp:
                ds[index]['finish_time'] = finish_date
                book = Book(ds[index]['book_id'])
                ds[index]['book_title'] = book.get_info().title
                ds[index]['book_cover_url'] = book.get_info().book_cover_url
                result.append(ds[index])
        return result

    # Copy certain collection as my own collection
    @staticmethod
    def copy_collection(source_id, target_id):
        # Get collection object
        source_collection = Collection(source_id)
        target_collection = Collection(target_id)
        source_book = source_collection.get_book_in_collection()
        for book in source_book:
            target_collection.add_book_to_collection(book['book_id'])

    # Get the tag need for front-end
    @staticmethod
    def get_tag(user_id, year, month):
        conn = connect_sys_db()
        query = "SELECT goal FROM monthly_goal WHERE (user_id = \'{user_id}\' AND year = \'{year}\' AND month = \'{month}\')".format(
            user_id=user_id,
            year=year,
            month=month,
        )
        db_result = read_sql(sql=query, con=conn)
        if db_result.empty:
            target = 0
        else:
            target = int(db_result.iloc[0].goal)
        finish_book = Collection.get_read_history_by_date(user_id, year, month)
        finish_num = len(finish_book)
        if finish_num >= target:
            finish_flag = True
        else:
            finish_flag = False
        return target, finish_num, finish_flag
