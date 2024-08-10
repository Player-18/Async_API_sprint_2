def generate_filmwork_query(last_modified, size_of_batch):
    """
    Function generate filmwork query.
    :param last_modified: Last modified datetime for query.
    :param size_of_batch: Size of batch.
    :return: Query
    """
    query = f"""
                SELECT
                    fw.id, 
                    fw.title, 
                    fw.description, 
                    fw.rating, 
                    fw.type,  
                    fw.modified, 
                    JSON_AGG(DISTINCT JSONB_BUILD_OBJECT(
                        'id', g.id, 
                        'name', g.name
                        )) as genres,
                    JSON_AGG(DISTINCT JSONB_BUILD_OBJECT(
                        'id', p.id, 
                        'name', p.full_name
                        ))
                        FILTER (WHERE pfw.role = 'actor') AS actors,
                    JSON_AGG(DISTINCT JSONB_BUILD_OBJECT(
                        'id', p.id, 
                        'name', p.full_name
                        ))
                        FILTER (WHERE pfw.role = 'director') AS directors,
                    JSON_AGG(DISTINCT JSONB_BUILD_OBJECT(
                        'id', p.id, 
                        'name', p.full_name
                        ))
                        FILTER (WHERE pfw.role = 'writer') AS writers
                FROM film_work as fw
                LEFT JOIN genre_film_work as gfw ON gfw.film_work_id = fw.id
                LEFT JOIN person_film_work as pfw ON pfw.film_work_id = fw.id
                LEFT JOIN genre as g ON g.id = gfw.genre_id
                LEFT JOIN person as p ON p.id = pfw.person_id
                WHERE fw.modified > '{last_modified}'
                GROUP BY fw.id
                ORDER BY fw.modified
                LIMIT {size_of_batch};
            """
    return query


def generate_person_query(last_modified, size_of_batch):
    query = f"""SELECT person.id, person.full_name as name, person.modified
                                            FROM person
                                            WHERE person.modified > '{last_modified}'
                                            ORDER BY person.modified
                                            LIMIT {size_of_batch};
                                            """
    return query


def generate_genre_query(last_modified, size_of_batch):
    query = f"""SELECT genre.id, genre.name, genre.description, genre.modified
                                                            FROM genre
                                                            WHERE genre.modified > '{last_modified}'
                                                            ORDER BY genre.modified
                                                            LIMIT {size_of_batch};
                                                            """
    return query
