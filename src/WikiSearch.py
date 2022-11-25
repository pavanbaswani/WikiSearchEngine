from time import time
from textMining import *
import pickle
import sys
import os
from re import split, search, sub, findall
import math
from collections import defaultdict

class WikiSearch():
  def __init__(self, path):
    self.index_path = path
    self.alpha = [chr(i) for i in range(ord('a'),ord('z')+1)]
    self.nums = [chr(i) for i in range(ord('0'),ord('9')+1)]
    self.total_docs = 7359999

  def retrieve_posting(low, high, offset, word, file_ptr):
    posting = []
    position = -1
    counter=0

    while low < high:
      mid = int((low + high) / 2)
      counter+=1
      file_ptr.seek(offset[mid])
      index_word = file_ptr.readline().strip().split()
      if word == wordPtr[0]:
        posting=wordPtr[1:]
        position=mid
        break
      elif word < wordPtr[0]:
        high = mid
      else:
        low = mid + 1
    return posting, position
  
  def rank_results(self, postings, q_type):
    IDF = {}
    docs = defaultdict(float)
    factors = {'t':0.32, 'i':0.28, 'b':0.2, 'c':0.1}
    for key in postings:
      IDF[key] = math.log(float(self.total_docs)/float(len(postings[key])))
    
    for word in postings:
      key = ''
      if(q_type==1):
        key = word.split(":",1)[0]

      for doc in postings[word]:
        docId = search(r'd\d+',doc).group()
        docId = docId.strip()
        docId = int(docId[1:])
        doc = sub(r'd\d+', '',doc)
        if(q_type==1):
          for field in findall(r'\s*[tbiclr]\s*\d+', doc):
            temp = field.strip()
            field = temp[0]
            if(field==key):
              freq = int(temp[1:])
              factor = factors.get(field, 0.05)
              docs[docId] += float(factor * float(1+math.log(float(freq))) * IDF[word])
        else:
          for field in findall(r'\s*[tbiclr]\s*\d+', doc):
            temp = field.strip()
            field = temp[0]
            freq = int(temp[1:])
            factor = factors.get(field, 0.05)
            docs[docId] += float(factor * float(1+math.log(float(freq))) * IDF[word])
    
    return docs


  def plain_query(self, query):
    query_tokens = list(word_tokenize(query))
    stemmed_tokens = list(stem_tokens(query_tokens))
    index_files = {}
    for token in stemmed_tokens:
      if token[0] in self.alpha:
        if token[0] not in index_files:
          index_files[token[0]] = [token]
        else:
          index_files[token[0]].append(token)
      elif token[0] in self.nums:
        if "num" not in index_files:
          index_files["num"] = [token]
        else:
          index_files["num"].append(token)
      else:
        if "oth" not in index_files:
          index_files["oth"] = [token]
        else:
          index_files["oth"].append(token)
    
    self.postings_list = {}
    for file_, tokens in index_files.items():
      print("processing ",file_+"_index.pkl")
      file_name = self.index_path+file_+"_index.pkl"
      temp = {}
      with open(file_name, "rb") as in_file:
        temp = pickle.load(in_file)
      for tok in tokens:
        self.postings_list[tok] = temp.get(tok, [])

    return self.postings_list

  def field_query(self, query):
    self.postings_list = {}
    fields = [i.replace(':','').strip() for i in findall(r'[tbiclr]\s*:\s*',query)]
    field_tokens = [i for i in split(r'[tbiclr]\s*:\s*',query) if len(i.strip())>0]
    assert len(fields)==len(field_tokens)

    index_files = {}
    for ind in range(len(field_tokens)):
      field = fields[ind]
      query_tokens = list(word_tokenize(field_tokens[ind]))
      stemmed_tokens = list(stem_tokens(query_tokens))
      for token in stemmed_tokens:
        if token[0] in self.alpha:
          if token[0] not in index_files:
            index_files[token[0]] = [field+":"+token]
          else:
            index_files[token[0]].append(field+":"+token)
        elif token[0] in self.nums:
          if "num" not in index_files:
            index_files["num"] = [field+":"+token]
          else:
            index_files["num"].append(field+":"+token)
        else:
          if "oth" not in index_files:
            index_files["oth"] = [field+":"+token]
          else:
            index_files["oth"].append(field+":"+token)
    
    self.postings_list = {}
    for file_, tokens in index_files.items():
      print("processing ",file_+"_index.pkl")
      file_name = self.index_path+file_+"_index.pkl"
      temp = {}
      with open(file_name, "rb") as in_file:
        temp = pickle.load(in_file)
      for tok in tokens:
        key = tok.split(":",1)[1]
        self.postings_list[tok] = temp.get(key, [])

    return self.postings_list



def main():
  offset = 20000
  if len(sys.argv)>=2:
    start_time = time()
    path_to_index = sys.argv[1]+"/inverted_index/"
    if os.path.exists(path_to_index):
      search_obj = WikiSearch(path_to_index)
      results = []

      # query_path = sys.argv[2]
      # queries = []
      # with open(query_path, 'r') as fp:
      #   queries = fp.readlines()
      # for query in queries[1:2]:
      while True:
        query = input("Query: ")
        query = query.strip()
        if(query=="exit"):
          break

        if(len(query)>0):
          query = query.strip().lower()
          postings_list = {}
          if search(r'[tbiclr]\s*:\s*',query):
            print("Field Query: ",query)
            postings_list = search_obj.field_query(query)
            results = search_obj.rank_results(postings_list,1)
          else:
            print("Plain Query: ",query)
            postings_list = search_obj.plain_query(query)
            results = search_obj.rank_results(postings_list,0)

        print('Results:')
        if(len(results)>0):
          results = sorted(results, key=results.get, reverse=True)
          for docId in results[:10]:
            file_no = int(docId/offset)
            if docId%offset>0:
              file_no += 1
            file_path = sys.argv[1]+"/title/title_"+str(file_no)+".pkl"
            temp = {}
            with open(file_path, "rb") as in_file:
              temp = pickle.load(in_file)
            print(temp.get(docId,''))
        else:
          print("No results found...!")
        
        end_time = time()
        print("Time taken: {} seconds".format(end_time-start_time))
      
    else:
      print("Index path doesn't exists")
  else:
    print("Insufficient Arguments\n")
    print("Usage: python3 search.py <inverted_index_folder_path> <query_file_path>")


if __name__ == "__main__":
	start_time = time()
	main()
	end_time = time()
	time_taken = end_time - start_time
	# print("Time Spent: %.2f seconds" %(time_taken))