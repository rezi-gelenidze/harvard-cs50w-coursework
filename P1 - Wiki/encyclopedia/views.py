import re
import markdown2
from django.shortcuts import render, redirect
from . import util
from random import choice


def editpage(request, title=''):
    # if title is empty redirect to indexpage
    if not title:
        return redirect('wiki-index')

    if request.method == "GET":
        content = util.get_entry(title)
        return render(request, 'encyclopedia/edit.html', {'content':content, 'title':title})
    
    # if form is submitted with POST
    newContent = request.POST.get('content')
    
    util.save_entry(title, newContent)
    return redirect('wiki-entry', title=title)


def entrypage(request, title=''):
    # if title is empty, return random entry
    if not title:
        all_entries = util.list_entries()
        title = choice(all_entries)

    # match similar title
    title = util.match_title(title)
    # if match exists
    if title:
        content = util.get_entry(title)
        # if content is found
        if content:
            html = markdown2.markdown(content)
            return render(request, 'encyclopedia/entry.html', {"content":html, "title":title})
    # else return error
    return render(request, 'encyclopedia/error.html', {
        'error': 'Invalid entry name.'
        })


def newentry(request):
    # if get request, return empty page for creating new entry
    if request.method == "GET":
        return render(request, 'encyclopedia/new.html')
    # get parameters
    title = request.POST.get('entryTitle')
    content = request.POST.get('entryContent')

    # if any of the parameters are not specified return error
    if not title or not content:
        error = 'Title or content can not be empty'
        return render(request, 'encyclopedia/error.html', {'error':error})

    # validate that title of the new entry is not taken
    all_entries = [entry.lower() for entry in util.list_entries()]
    if title.lower() in all_entries:
        return render(request, 'encyclopedia/new.html', {'content':content, 'error':True})

    # save new entry and redirect to it
    util.save_entry(title, content)
    return redirect('wiki-entry', title=title)


def index(request):
    # get list of entries and render index page
    all_entries = util.list_entries()
    return render(request, 'encyclopedia/index.html', {'heading':'All entries', 'entries':all_entries})   


def search(request):
    # get entries list and search query parameter 'q'
    query = request.GET.get('q', '')
    if not query:
        return redirect('wiki-index')

    matched = util.match_title(query)
    if matched:
        return redirect('wiki-entry', title=matched)

    # else return similar results
    results = []
    all_entries = util.list_entries()
    param_lower = query.lower()
    for entry in all_entries:
        srch_res = re.search(param_lower, entry.lower())
        if srch_res:
            results.append(entry)

    if results:
        return render(request, 'encyclopedia/index.html', {
            'heading':f"All results of - '{query}'",
            'entries':results
            })

    #if no search query, return error
    return render(request, 'encyclopedia/error.html', {'error':'Nothing found'})
