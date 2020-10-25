import os

import ety
from flask import Flask, render_template, request
from mediawiki import DisambiguationError, MediaWiki
from textblob import TextBlob
from PyDictionary import PyDictionary
from pyunsplash import PyUnsplash


def first_one(img_search):
    for photo in img_search.entries:
        return(photo.link_download)


def polari_check(search):
    search = TextBlob(search)
    try:
        return search.sentiment.polarity
    except ValueError:
        return "cant find polarity"


img_yes = PyUnsplash(api_key=os.getenv('PU'))


def find_ety(search):
    search = ety.origins(search)
    word_origin_list = ""
    for word in search:
        word_origin_list += str(word)
    return word_origin_list


def syn_find(search):
    dictionary = PyDictionary()
    return dictionary.synonym(search)


def find_alter_meaning(search):
    dictionary = PyDictionary()
    stringit = ""
    if dictionary.meaning(search):
        for key in dictionary.meaning(search).values():
            for value in key:
                stringit += value
        return stringit
    return None


def find_short_meaning(search):
    try:
        wikipedia = MediaWiki()
        meaning = wikipedia.page(search.title())
    except DisambiguationError:
        return find_alter_meaning(search)
    else:
        if search.lower() != meaning.title.lower():
            return find_alter_meaning(search)
        def_meaning = meaning.summarize()
        return str(def_meaning + "link for further read: " + wikipedia.
                   opensearch(f'{meaning.title}', results=1)[0][2])


def find_img(search):
    img_search = img_yes.search(type_='photos', query=search)
    image = first_one(img_search)
    return image


def palindrome(search):
    return search[:] == search[::-1]


app = Flask(__name__)
app.static_folder = 'static'
@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search = request.form.get('search')
        if not search or len(search) < 3:
            return render_template('main.html')
        img_search = find_img(search)
        searchby = request.form.get('searchby')
        if searchby == "Semantic Field":
            search_check = polari_check(search)
        elif searchby == "Palindrome":
            search_check = palindrome(search)
        elif searchby == "Synonyms":
            search_check = syn_find(search)
        elif searchby == "Etymology":
            search_check = find_ety(search)
        else:
            search_check = "cant find the desired parameter!"
        short_def = find_short_meaning(search)
        return single_option(search, searchby, search_check,
                             img_search, short_def)
    else:
        return render_template('main.html')


@app.route("/", methods=['GET', 'POST'])
def single_option(search, searchby,
                  search_check=None, img_search=None, short_def=None):
    if not img_search:
        img_search = "https://unsplash.com/a/img/empty-states/photos.png"
    return render_template('onechoice.html',
                           searchby=searchby, search=search,
                           search_check=search_check,
                           img_search=img_search, short_def=short_def)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run()
