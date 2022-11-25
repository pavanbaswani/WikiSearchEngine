from re import split, compile, search, sub, finditer
import string
from nltk.stem.snowball import SnowballStemmer
Stemmer = SnowballStemmer("english", ignore_stopwords=True)


punkts = compile(r'['+string.punctuation+' ]')
stop_words = set(['our', 'why', 'he', 'are', 'if', 'been', 'about', 'her', 'his', 'you', 'had', 'didn', 'am', 'wasn', 'herself', 'o', 'm', 'we', 're', 'an', 'own', 'yourselves', 'should', 'is', 'did', 'ourselves', 'doing', 'their', 'does', 'as', "hadn't", "won't", 'the', 'has', 'those', 'having', 'they', 'i', 'll', 'shouldn', 'themselves', 'what', 'being', 'will', 'be', 'was', 'out', 'himself', 'ours', 'him', 'haven', 'me', 'hers', 'have', 'them', 'do', 'itself', 'my', "you'd", "you're", 'yours', 'these', 'so', 'can', 'other', 'doesn', 'because', 'yourself', 'this', "aren't", 'won', 'theirs', "she's", 'were', 'with', 'aren', 'nor', "shan't", 'hadn', 'she', 'couldn', "couldn't", 'but', 'between', "mustn't", "it's", 'some', "haven't", 'myself', 'down', 'that'])

token_len = 0
def word_tokenize(raw_text):
  tokens = split(punkts, raw_text)
  global token_len
  token_len = len(tokens)
  return [token for token in tokens if token!=""]

def remove_stop_words(tokens):
  return [token for token in tokens if token not in stop_words]

def stem_tokens(tokens):
  dic = {}
  for token in tokens:
    stem = Stemmer.stem(token)
    if(stem not in dic):
      dic[stem] = 1
    else:
      dic[stem] += 1
  return dic

def get_tokens(raw_text):
  tokens = list(filter(None,split(punkts, raw_text)))
  global token_len
  token_len = len(tokens)
  return [token for token in tokens if token not in stop_words]

def parse_text(raw_text):
  global token_len
  token_len = 0
  external_links_pattern = compile(r'[=]{2,}[ ]*external links[ ]*[=]{2,}')
  reference_pattern = compile(r'[=]{2,}references[=]{2,}|[=]{2,}notes[=]{2,}|[=]{2,}bibliography[=]{2,}')
  category_pattern = compile(r'\[{2,}category.*\]{2,}')
  tags_pattern = compile(r'(&lt;(!--)?)|((--)?&gt;)|(&quot;)')
  infobox_patter = compile(r'\{\{infobox')

  infobox = []
  body = []
  category = []
  external_links = []
  references = []

  raw_text = raw_text.lower()
  raw_text = sub(tags_pattern, "",raw_text)

  lines = raw_text.split('\n')
  ind = 0
  while ind<len(lines):

    if ind<len(lines) and search(infobox_patter,lines[ind]):
      braces_stack = 1
      temp = []
      while ind<len(lines) and braces_stack>0:
        if search(infobox_patter,lines[ind]):
          if len(temp)>0:
            infobox.append(" ".join(temp))
          temp = []
          lines[ind] = " ".join(split(infobox_patter, lines[ind])[1:])
          braces_stack = 1
        braces_stack += lines[ind].count('{{')
        braces_stack -= lines[ind].count('}}')
        lines[ind] = sub(r'\|[a-zA-Z\s]*='," ",lines[ind])
        temp.append(lines[ind])
        ind += 1
      if len(temp)>0:
        infobox.append(" ".join(temp))

    elif ind<len(lines) and search(category_pattern,lines[ind]):
      lines[ind] = lines[ind]
      lines[ind] = sub(r'\[{2,}category[:]?', "", lines[ind])
      lines[ind] = sub(r'\]{2,}', "", lines[ind])
      category.append(lines[ind])

    elif ind<len(lines) and search(external_links_pattern, lines[ind]):
      while(ind<len(lines) and lines[ind].strip()!=""):
        lines[ind] = sub(external_links_pattern,"",lines[ind]).strip()
        if(lines[ind]!=""):
          external_links.append(" ".join([line for line in lines[ind].split(" ") if "http" not in line]))
        ind += 1

    elif ind<len(lines) and search(reference_pattern, lines[ind]):
      while(ind<len(lines) and lines[ind].strip()!=""):
        lines[ind] = sub(reference_pattern, "", lines[ind].strip())
        if(lines[ind]!=""):
          lines[ind] = sub(r'\|[a-zA-Z\s]*='," ",lines[ind])
          references.append(" ".join([line for line in lines[ind].split(" ") if "http" not in line]))
        ind += 1

    elif ind<len(lines):
      lines[ind] = sub(r'\|[a-zA-Z\s]*='," ",lines[ind])
      body.append(lines[ind])

    ind += 1
  
  token_length = 0
  category = stem_tokens(get_tokens(' '.join(category)))
  token_length += token_len
  infobox = stem_tokens(get_tokens(' '.join(infobox)))
  token_length += token_len
  external_links = stem_tokens(get_tokens(' '.join(external_links)))
  token_length += token_len
  references = stem_tokens(get_tokens(' '.join(references)))
  token_length += token_len
  body = ' '.join(body)
  body = body.replace("\n","").replace("\r","").replace(r'[ ]{2,}'," ")
  body = stem_tokens(get_tokens(body))
  token_length += token_len
  return infobox, category, external_links, references, body, token_length
  
    
def processTitle(raw_text):
  return stem_tokens(get_tokens(raw_text.lower())), token_len