from django.shortcuts import render
from django.db import connection


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
    return render(request, 'query_results.html', {'sql_res_1': sql_res1})

def rankings(request):
    return render(request, 'rankings.html')

def records_management(request):
    return render(request, 'records_management.html')

