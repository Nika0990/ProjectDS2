from django.shortcuts import render
from django.db import connection
from .models import Programranks, Households, Programs, Recordorders, Recordreturns


def dictfetchall(cursor):
    # Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def index(request):
    return render(request, 'index.html')


def query_results(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT  g.genre, min(p.title) as movieTitle, g.maxDuration
                            FROM GenresAreA g, Programs p, ReturnedRelevant rr
                            WHERE g.genre = p.genre and g.maxDuration = p.duration and rr.title = p.title
                            GROUP BY g.genre, g.maxDuration
                            ORDER BY g.genre""")
        sql_res1 = dictfetchall(cursor)
    with connection.cursor() as cursor:
        cursor.execute("""SELECT kp.title, Cast(AVG(Cast(pr.rank as FLOAT)) as DECIMAL(10,2)) as avgRank
                            FROM EnoughKosherRanks kp, ProgramRanks pr
                            WHERE kp.title = pr.title
                            GROUP BY kp.title
                            Order by avgRank desc, title""")
        sql_res2 = dictfetchall(cursor)
    with connection.cursor() as cursor:
        cursor.execute("""SELECT title
                            FROM relevantTitles rt
                            WHERE    rt.title NOT IN
                                    (SELECT title
                                    FROM ProgramRanks pr
                                    Where pr.rank < 2)
                            ORDER BY title""")
        sql_res3 = dictfetchall(cursor)
    return render(request, 'query_results.html', {'sql_res_1': sql_res1, 'sql_res_2': sql_res2, 'sql_res_3': sql_res3})


def rankings(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT DISTINCT hID
                            FROM Households""")
        res1 = dictfetchall(cursor)

    with connection.cursor() as cursor:
        cursor.execute("""SELECT DISTINCT title
                            FROM Programs""")
        res2 = dictfetchall(cursor)

    with connection.cursor() as cursor:
        cursor.execute("""SELECT DISTINCT genre
                            FROM(
                                SELECT genre, count(title) as num_movies
                                FROM Programs
                                WHERE genre is not null
                                Group by genre) as NumMovies
                            WHERE num_movies >=5
                            """)
        res3 = dictfetchall(cursor)

    if request.method == 'POST' and 'form1' in request.POST:
        new_id = int(request.POST["ID"])
        title = request.POST["title"]
        rank = request.POST["rank"]
        with connection.cursor() as cursor:
            cursor.execute("""SELECT *
                                FROM ProgramRanks""")
            ranked = dictfetchall(cursor)
        for line in ranked:
            if (line['hID'] == new_id) and (line['title'] == title):
                with connection.cursor() as cursor:
                    cursor.execute("""DELETE 
                                      FROM ProgramRanks
                                      WHERE hID = %s and title = %s""", [new_id, title])
                break
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO ProgramRanks
                               VALUES (%s,%s,%s)""", [title, new_id, rank])

    if request.method == 'POST' and 'form2' in request.POST:
        new_genre = request.POST["genre"]
        min_ranks = request.POST["min_ranks"]
        with connection.cursor() as cursor:
            cursor.execute("""SELECT arr.title, avgRank
                                FROM avgRelevantRanks arr, Programs p, rankingsCount rc
                                Where arr.title = p.title and p.genre = %s and rc.title = p.title and rc.rankings >= %s
                                ORDER BY avgRank desc, title""", [new_genre, min_ranks])
            temp = dictfetchall(cursor)
        with connection.cursor() as cursor:
            cursor.execute("""SELECT rz.title, 0.00 as avgRank
                                FROM rankZeros rz, Programs p
                                WHERE rz.title = p.title and p.genre = %s
                                    union
                                SELECT arr.title,0.00 as avgRank
                                FROM avgRelevantRanks arr, Programs p, rankingsCount rc
                                Where arr.title = p.title and p.genre = %s and rc.title = p.title and rc.rankings < %s
                            ORDER BY title""", [new_genre, new_genre, min_ranks])
            temp.extend(dictfetchall(cursor))
        res4 = temp[0:5]
        return render(request, 'rankings.html', {'res_1': res1, 'res_2': res2, 'res_3': res3, 'res_4': res4})

    return render(request, 'rankings.html', {'res_1': res1, 'res_2': res2, 'res_3': res3})


def records_management(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT c.hID, (c.num + p.num) as amount
                            FROM numOfCurrent c, numOfPast p
                            WHERE c.hID = p.hID
                            ORDER BY amount desc, c.hID""")
        res = dictfetchall(cursor)
    res = res[0:3]

    if request.method == 'POST' and 'form1' in request.POST:
        requested_hid = request.POST["hID"]
        movie_title = request.POST["title"]

        with connection.cursor() as cursor:
            cursor.execute("""SELECT DISTINCT hID
                                FROM Households""")
            families = dictfetchall(cursor)
        flag = False
        for line in families:
            if str(line['hID']) == requested_hid:
                flag = True
                break
        if not flag:
            error = "Error. Not registered client!"
            return render(request, 'records_management.html', {'error': error, 'res': res})
        requested_hid = int(requested_hid)

        flag = False
        with connection.cursor() as cursor:
            cursor.execute("""SELECT DISTINCT title
                                FROM Programs""")
            titles = dictfetchall(cursor)
        for line in titles:
            if line['title'] == movie_title:
                flag = True
                break
        if not flag:
            error = "Request denied. No such film in the library!"
            return render(request, 'records_management.html', {'error': error, 'res': res})

        flag = False
        with connection.cursor() as cursor:
            cursor.execute("""SELECT count(*) as numOfPrograms
                                FROM RecordOrders
                                WHERE hID = %s""", [requested_hid])
            num_orders = dictfetchall(cursor)
        if num_orders[0]['numOfPrograms'] >= 3:
            error = "Request denied. Orders are limited to three items!"
            return render(request, 'records_management.html', {'error': error, 'res': res})

        with connection.cursor() as cursor:
            cursor.execute("""SELECT hID
                                FROM RecordOrders ro
                                WHERE ro.title = %s""", [movie_title])
            ordered = dictfetchall(cursor)
        if len(ordered) != 0:
            if ordered[0]['hID'] != requested_hid:
                error = "Request denied. Record is currently in use!"
                return render(request, 'records_management.html', {'error': error, 'res': res})
            if ordered[0]['hID'] == requested_hid:
                error = "Request denied. You are currently in possession of this record!"
                return render(request, 'records_management.html', {'error': error, 'res': res})

        with connection.cursor() as cursor:
            cursor.execute("""SELECT hID
                                FROM RecordReturns ro
                                WHERE ro.title = %s and ro.hID = %s""", [movie_title, requested_hid])
            ordered = dictfetchall(cursor)
        if len(ordered) != 0:
            error = "Request denied. You already ordered this record in the past!"
            return render(request, 'records_management.html', {'error': error, 'res': res})

        with connection.cursor() as cursor:
            cursor.execute("""SELECT hID
                                FROM Households h, Programs p
                                WHERE (h.hID = %s and h.ChildrenNum > 0 )and p.title = %s 
                                and (p.genre = 'Adults only' or p.genre = 'Reality')""", [requested_hid, movie_title])
            check = dictfetchall(cursor)
        if len(check) != 0:
            error = "Request denied. Film is not suitable for families with children!"
            return render(request, 'records_management.html', {'error': error, 'res': res})

        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO RecordOrders
                               VALUES (%s,%s)""", [movie_title, requested_hid])

    if request.method == 'POST' and 'form2' in request.POST:
        requested_hid = request.POST["hID2"]
        movie_title = request.POST["title2"]

        with connection.cursor() as cursor:
            cursor.execute("""SELECT DISTINCT hID
                                FROM Households""")
            families = dictfetchall(cursor)
        flag = False
        for line in families:
            if str(line['hID']) == requested_hid:
                flag = True
                break
        if not flag:
            error = "Error. Not registered client!"
            return render(request, 'records_management.html', {'error2': error, 'res': res})
        requested_hid = int(requested_hid)

        flag = False
        with connection.cursor() as cursor:
            cursor.execute("""SELECT DISTINCT title
                                FROM Programs""")
            titles = dictfetchall(cursor)
        for line in titles:
            if line['title'] == movie_title:
                flag = True
                break
        if not flag:
            error = "Request denied. No such film in the library!"
            return render(request, 'records_management.html', {'error2': error, 'res': res})

        with connection.cursor() as cursor:
            cursor.execute("""SELECT hID
                                FROM RecordOrders
                                WHERE hID = %s and title = %s""", [requested_hid, movie_title])
            exists = dictfetchall(cursor)
        if len(exists) == 0:
            error = "Request denied. You are not in possession of this film!"
            return render(request, 'records_management.html', {'error2': error, 'res': res})

        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM RecordOrders
                               WHERE title = %s and hID = %s""", [movie_title, requested_hid])

        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO RecordReturns
                               VALUES (%s,%s)""", [movie_title, requested_hid])

    return render(request, 'records_management.html', {'res': res})
