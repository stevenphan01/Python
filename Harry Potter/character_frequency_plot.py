import os
import urllib
import urllib.parse
import urllib.request
import re
import collections
import numpy as np
import matplotlib.pyplot as plt

def build_google_drive_url(doc_id):
  DRIVE1  = "https://docs.google.com/uc" 
  DRIVE2  = "https://drive.google.com/uc"  
  baseurl = DRIVE1 # DRIVE2 works as well 
  params = {"export" : "download",
            "id"     : doc_id}
  url = baseurl + "?" + urllib.parse.urlencode(params) 

  return url

def read_google_doc(doc_id): 
  url = build_google_drive_url(doc_id)
  filename = doc_id + ".txt"
  if not os.path.exists(filename):
    with urllib.request.urlopen(url) as text:
      with open(doc_id + ".txt", "w") as new_file:
        decoded_text = text.read().decode("utf-8")
        for line in decoded_text:
          new_file.write(line)
  return (open(doc_id + ".txt", "r").read())

def get_harry_potter():
  return read_google_doc("1jOCDUhsMY3uAoLqV3NoZogyrr-FVqEoo")

def clean_hp(text):
  splt_text = text.split("Harry Potter and the Sorcerer's Stone")
  return ("Harry Potter and the Sorcerer's Stone" + splt_text[2]).strip()

def split_text_into_tokens(text):
  token_list = []
  token_list_2 = []
  pattern = "['A-Za-z0-9]+-?['A-Za-z0-9]+"
  regex = re.compile(pattern)
  token_list_1 = regex.findall(text)
  for token in token_list_1:
    token_list.append(token.strip("'"))
  for token in token_list:
    if "'s" not in token:
      token_list_2.append(token)
    elif "'s" in token:
      token_list_2.append(token.strip("'s"))
  return token_list_2

def load_stop_words(add_pronouns = False):
  pronouns = ['they', 'your', "who", "she'd", "he'd", 'madam', 'he', "she", 'i', 'it', "i'm", "i've", "oh", "you", "mr", "mrs", "i'll", "i'd"]
  stop_words = stopwords.words('english')
  if add_pronouns:
    for pronoun in pronouns:
      stop_words.append(pronoun)
    return stop_words
  else:
    return stop_words

def bi_grams(tokens):
  return ngrams(tokens, 2)

def build_table(words):
  counter = collections.Counter()
  for word in words:
    counter[word] += 1
  return counter

def top_n(tokens, n):
  token_list = build_table(tokens)
  return [(key, val) for key, val in token_list.most_common(n)]

def remove_stop_words(tokens, stoplist):
  l = []
  for t in tokens:
    if t not in stoplist:
      l.append(t)
  return l

def find_characters_v2(text, stoplist = [], top = 15):
  token_text = split_text_into_tokens(text)
  bigram = bi_grams(token_text)
  cap_tokens = []
  for token in bigram:
    if token[1][0].isupper() and token[0][0].isupper():
      cap_tokens.append(token)
  stoplist_tokens = []
  for token in cap_tokens:
    if token[1].lower() not in stoplist and token[0].lower() not in stoplist:
      stoplist_tokens.append(token)
  temp = top_n(stoplist_tokens, top)
  new_list = []
  for item in temp:
    new_string = item[0][0] + " " + item[0][1]
    new_list.append((new_string, item[1]))
  return new_list

def split_into_chapters(text):
  pattern = r'CHAPTER\s[a-zA-Z]+'
  regex = re.compile(pattern, re.M)
  chapters = regex.split(text)[1:]
  return chapters

def get_character_counts_v2(chapters, names):
  py_data = [np.char.count(chapters[chapter], n) for n in names for chapter in range(0,17)]
  counts = np.array(py_data)
  return np.cumsum(counts.reshape(len(names), 17), axis = 1).T

def simple_graph_hp(counts, names):
  plt.style.use("seaborn")
  fig, axes = plt.subplots(nrows = 1, ncols = 1)
  plots = axes.plot(counts)
  axes.grid(True)
  axes.legend(handles=plots, loc='upper left', labels=names)
  axes.set_xlabel("chapters")
  axes.set_ylabel("mentions")
  dim_x = np.arange(1, counts.shape[0],1)
  axes.set_xlim(1,dim_x[-1])
  fig.suptitle("HP Characters Mentions")
  axes.set_xticks(dim_x)

  return fig

def pipeline_v2(names):
  hp = clean_hp(get_harry_potter())
  chapters = split_into_chapters(hp) 
  np_hp = get_character_counts_v2(chapters, names)
  fig = simple_graph_hp(np_hp, names)
  return fig

who = ["Harry", "Ron", "Hagrid", "Hermione"] 
fig = pipeline_v2(who)