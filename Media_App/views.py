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
    return render(request, 'records_management.html')

