import json
from pandas import read_sql
from lib.sql_linker import connect_sys_db, mysql


class Book:
    def __init__(self, id):
        self._id = id

    # Get book's all detail by book_id
    def get_info(self):
        # SQL
        conn = connect_sys_db()
        query = "SELECT id, title, authors, publisher, published_date, description," \
                "ISBN13, categories, google_rating, google_ratings_count, book_cover_url, " \
                "language FROM books WHERE id = \'{id}\' ".format(
            id=self._id
        )
        db_result = read_sql(sql=query, con=conn)
        if db_result.empty:
            # if ID not existed
            return None
        else:
            info = db_result.iloc[0]
            return info

    # Search result of input content
    @staticmethod
    def book_search(input):
        # SQL
        conn = connect_sys_db()
        query = "SELECT id, authors, title ,ISBN13, book_cover_url, description, publisher, published_date, categories FROM books WHERE title like \'%{input}%\' or authors like \'%{input}%\' or ISBN13 like \'%{input}%\'".format(
            input=input
        )
        db_result = read_sql(sql=query, con=conn)
        json_str = db_result.to_json(orient='index')
        ds = json.loads(json_str)
        result = []
        for index in ds:
            ds[index]['average'] = Book.get_book_average_rating(ds[index]['id'])
            result.append(ds[index])
        return result

    # Is book exist by book_id
    @staticmethod
    def is_book_exists_by_id(id):
        # SQL
        conn = connect_sys_db()
        query = 'SELECT id FROM books Where id = \'{id}\''.format(
            id=id
        )
        db_result = read_sql(sql=query, con=conn)
        if db_result.empty:
            return False
        else:
            return True

    # Is book exist in certain collection
    @staticmethod
    def is_book_exists_in_collection(collection_id, book_id):
        # SQL
        conn = connect_sys_db()
        query = 'SELECT * FROM collects Where (book_id = \'{book_id}\' AND collection_id = \'{collection_id}\')'.format(
            book_id=book_id,
            collection_id=collection_id
        )
        db_result = read_sql(sql=query, con=conn)
        if db_result.empty:
            return False
        else:
            return True

    # # Length of search result of input content
    # @staticmethod
    # def book_search_length(input, rating_from, rating_to):
    #     # SQL
    #     conn = connect_sys_db()
    #     query = "SELECT count(*) as num FROM books WHERE title like \'%{input}%\' or authors like \'%{input}%\' or ISBN13 like \'%{input}%\'".format(
    #         input=input
    #     )
    #     db_result = read_sql(sql=query, con=conn)
    #     return db_result.iloc[0].num

    # Length of search result of input content
    @staticmethod
    def book_search_length(input, rating_from, rating_to):
        # SQL
        conn = connect_sys_db()
        query = "SELECT id FROM books WHERE title like \'%{input}%\' or authors like \'%{input}%\' or ISBN13 like \'%{input}%\'".format(
            input=input
        )
        db_result = read_sql(sql=query, con=conn)
        json_str = db_result.to_json(orient='index')
        ds = json.loads(json_str)
        result = []
        for index in ds:
            avg_rating = Book.get_book_average_rating(ds[index]['id'])
            if rating_from <= avg_rating <= rating_to:
                result.append(ds[index])
        return len(result)

    @staticmethod
    def book_search_regex(input):
        ans = ""
        for ch in input:
            if not (ch.isdigit() or ch.isalpha()):
                ch = "%"
            ans += ch
        return ans

    # Get total number of search result page
    @staticmethod
    def get_book_search_page_num(content, rating_from, rating_to, result_each_page):
        num_results = Book.book_search_length(content, rating_from, rating_to)
        # If total number of review < number of review on each page
        if num_results <= result_each_page:
            num_page = 1
            num_last_page = num_results
        else:
            num_last_page = num_results % result_each_page
            if num_last_page != 0:
                num_page = (num_results - num_last_page) / result_each_page + 1
            else:
                num_page = num_results / result_each_page
        return num_page, num_last_page

    # Get book list on certain search page
    @staticmethod
    def get_book_search_page(content, rating_from, rating_to, result_each_page, curr_page):
        page_num, last_page_num = Book.get_book_search_page_num(content, rating_from, rating_to, result_each_page)
        reviews_num = Book.book_search_length(content, rating_from, rating_to)
        if (reviews_num == 0):
            return []
        if page_num == curr_page:
            if last_page_num != 0:
                index_from = reviews_num - last_page_num + 1
                index_to = reviews_num
            else:
                index_from = reviews_num - result_each_page + 1
                index_to = reviews_num
        else:
            index_from = result_each_page * (curr_page - 1) + 1
            index_to = result_each_page * (curr_page)
        return Book.get_book_search_from_to(content, rating_from, rating_to, index_from - 1, index_to - 1)

    # @staticmethod
    # def get_book_search_from_to(content, rating_from, rating_to, index_from, index_to):
    #     print(index_from, index_to)
    #     num = index_to - index_from + 1
    #     conn = connect_sys_db()
    #     query = "SELECT id, authors, title ,ISBN13, book_cover_url, description, publisher, published_date, categories FROM books WHERE title like \'%{input}%\' or authors like \'%{input}%\' or ISBN13 like \'%{input}%\' limit {index_from},{num}".format(
    #         input=content,
    #         index_from=index_from,
    #         num=num
    #     )
    #     # print(query)
    #     db_result = read_sql(sql=query, con=conn)
    #     print(db_result)
    #     json_str = db_result.to_json(orient='index')
    #     ds = json.loads(json_str)
    #     result = []
    #     for index in ds:
    #         ds[index]['average'] = Book.get_book_average_rating(ds[index]['id'])
    #         if rating_from <= ds[index]['average'] <= rating_to:
    #             result.append(ds[index])
    #     return result

    @staticmethod
    def get_book_search_from_to(content, rating_from, rating_to, index_from, index_to):
        # print(index_from, index_to)
        num = index_to - index_from + 1
        conn = connect_sys_db()
        query = "SELECT id, authors, title ,ISBN13, book_cover_url, description, publisher, published_date, categories FROM books WHERE title like \'%{input}%\' or authors like \'%{input}%\' or ISBN13 like \'%{input}%\'".format(
            input=content,
        )
        # print(query)
        db_result = read_sql(sql=query, con=conn)
        # print(db_result)
        json_str = db_result.to_json(orient='index')
        ds = json.loads(json_str)
        result = []
        for index in ds:
            ds[index]['average'] = Book.get_book_average_rating(ds[index]['id'])
            if rating_from <= ds[index]['average'] <= rating_to:
                result.append(ds[index])
        ans = []
        i = 0
        for index in result:
            if (index_from <= i <= index_to):
                ans.append(index)
                i += 1
            else:
                i += 1
        return ans

    # Get average rating of book
    @staticmethod
    def get_book_average_rating(book_id):
        # SQL
        conn = connect_sys_db()
        query = "SELECT rating FROM review_rate WHERE (book_id = \'{book_id}\')".format(
            book_id=book_id
        )
        db_result = read_sql(sql=query, con=conn)
        json_str = db_result.to_json(orient='index')
        ds = json.loads(json_str)
        result = []
        for index in ds:
            result.append(ds[index])
        # If there is no rating
        if len(result) == 0:
            return 0
        sum = 0
        # Get average rating
        for i in result:
            sum = sum + i['rating']
        return float(sum / len(result))

    @staticmethod
    def get_popular_book():
        # SQL
        conn = connect_sys_db()
        query = "SELECT id, title, book_cover_url from books order by rand() limit 10"
        db_result = read_sql(sql=query, con=conn)
        json_str = db_result.to_json(orient='index')
        ds = json.loads(json_str)
        result = []
        for index in ds:
            result.append(ds[index])
        return result
