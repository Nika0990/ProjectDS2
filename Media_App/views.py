from django.shortcuts import render
from django.db import connection
from .models import Programranks, Households, Programs, Recordorders,Recordreturns


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
    if request.method == 'POST' and request.POST:
        id = request.POST["ID"]
        title = request.POST["title"]
        rank = request.POST["rank"]
        with connection.cursor() as cursor:
            cursor.execute("""SELECT *
                                FROM ProgramRanks""")
            ranked = dictfetchall(cursor)
        for line in ranked:
            if (line['hID'] == id) and (line['title'] == title) :
                with connection.cursor() as cursor:
                    cursor.execute("""DELETE 
                                      FROM ProgramRanks
                                      WHERE hID = %s and title = %s""",[id], [title])
        with connection.cursor() as cursor:
            cursor.execute("""SELECT *
                                FROM Households
                                WHERE hID = %s""",[id])
            new_id = dictfetchall(cursor)
        with connection.cursor() as cursor:
            cursor.execute("""SELECT *
                                FROM Programs
                                WHERE title = %s""", [title])
            new_title = dictfetchall(cursor)
        new_Rank = Programranks(title =Programs(new_title)[0]['title'] ,hid=Households(new_id)[0]['hID'], rank = rank)
        new_Rank.save()
    return render(request, 'rankings.html', {'res_1': res1, 'res_2': res2})

def records_management(request):
    return render(request, 'records_management.html')

