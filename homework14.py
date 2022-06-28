import json
import sqlite3
import flask

app = flask.Flask(__name__)


def get_value_from_db(sql):
    """Открытие базы данных netflix"""
    with sqlite3.connect('netflix.db') as connection:
        connection.row_factory = sqlite3.Row
        result = connection.execute(sql).fetchall()
    return result


def search_by_title(title):
    """Поиск ао названию"""
    sql = f"""
            SELECT * FROM netflix
            WHERE title = {title}
            ORDER BY release_year desc 
            limit 1
            """
    result = get_value_from_db(sql)
    for item in result:
        return item


@app.get('/movie/<title>/')
def search_by_title_view(title):
    """Поиск ао названию"""
    result = search_by_title(title=title)
    return app.response_class(response=json.dumps(result, ensure_ascii=False, indent=4),
                              status=200,
                              mimetype='application.json'
                              )


@app.get('/movie/<year_1>/to/<year_2>/')
def search_data_view(year_1, year_2):
    """Поиск в определенном промежутке годов"""
    sql = f"""
            SELECT title, release_year FROM netflix
            WHERE release_year BETWEEN {year_1} and {year_2}
            limit 100
    """

    result = []

    for item in get_value_from_db(sql=sql):
        result.append(dict(item))

    return app.response_class(response=json.dumps(result, ensure_ascii=False, indent=4),
                              status=200,
                              mimetype='application.json'
                              )


@app.get('/rating/<rating>/')
def search_rating_view(rating):
    """Поиск по рейтингу"""
    my_dict = {"children": ("G", "G"), "family": ("G", "PG", "PG-13"), "adult": ("R", "NC-17")}
    sql = f"""
            SELECT title, rating, description FROM netflix
            WHERE rating in {my_dict.get(rating, ("R"))}

    """

    result = []

    for item in get_value_from_db(sql=sql):
        result.append(dict(item))
    return app.response_class(response=json.dumps(result, ensure_ascii=False, indent=4),
                              status=200,
                              mimetype='application.json'
                              )


@app.get('/genre/<genre>/')
def search_genre_view(genre):
    """Поиск по жанру и вывод 10 фильмов по дате релиза"""

    sql = f"""
            SELECT title, description FROM netflix
            WHERE listed_in LIKE '%{genre}'
            ORDER BY release_year DESC 
            LIMIT 10

    """
    result = []

    for item in get_value_from_db(sql=sql):
        result.append(dict(item))
    return app.response_class(response=json.dumps(result, ensure_ascii=False, indent=4),
                              status=200,
                              mimetype='application.json'
                              )


def search_double_name(name_1, name_2):
    """ Поиск по именам """
    sql = f"""
            SELECT "cast" FROM netflix
            WHERE "cast" LIKE '%{name_1}' AND "cast" LIKE '%{name_2}'
            GROUP BY "cast"
            HAVING COUNT(*) > 2

    """
    result = []

    name_dict = {}
    for item in get_value_from_db(sql=sql):
        names = set(dict(item).get("cast").split(", ")) - set([name_1, name_2])

        for name in names:
            name_dict[str(name.strip())] = name_dict.get(str(name).strip(), 0) + 1

    for key, value in name_dict.items():
        if value >= 2:
            result.append(key)

    return result


def search(typ, year, genre):
    """Поиск по типу, году и жанру """
    sql = f"""
            SELECT title, description, listed_in FROM netflix
            WHERE type = {typ} AND release_year = {year} AND listed_in = '%{genre}%'
    """
    result = []

    for item in get_value_from_db(sql):
        result.append(dict(item))

    return result


if __name__ == '__main__':
    print(search_double_name('Rose McIven', 'Ben Lamb'))
    print(search('Movie', '2021', 'Documentaries'))
    app.run(host='0.0.0.0',
            port=8080,
            debug=True
            )
