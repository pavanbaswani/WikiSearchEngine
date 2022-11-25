import bz2
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from time import time
from textMining import *
import pickle
import sys
import os
from collections import defaultdict

inverted_index = defaultdict()
token_size = 0
docs = {}
docs_freq = {}
class WikiParse(ContentHandler):

  def __init__(self):
    self.index = 0
    self.revision_bool = False
    self.offset = 20000
    self.title = ""
    self.text = ""
    self.start_t = ""
    self.end_t = ""
    self.prev_files = 0
    self.file_index = self.prev_files + 0
    global token_size

  def startElement(self, tag_name, attrs):
    global inverted_index
    global docs
    global docs_freq

    if tag_name=="page":
      self.revision_bool = False
      self.index += 1
      if(self.index%1000==0):
        print(self.index)

      if(self.index>(self.offset*self.prev_files)):
        if(self.index%self.offset==0):
          path_to_index = sys.argv[2]
          sorted_dict = {}
          for key in sorted(inverted_index.keys()):
            sorted_dict[key] = inverted_index[key]
          inverted_index = defaultdict()
          with open(path_to_index+'/index/index_'+str(self.file_index)+'.pkl', 'wb') as out_file:
            pickle.dump(sorted_dict, out_file, protocol=pickle.HIGHEST_PROTOCOL)

          # with open(path_to_index+"/title/title_"+str(self.file_index)+'.pkl', 'wb') as out_file:
          #   pickle.dump(docs, out_file, protocol=pickle.HIGHEST_PROTOCOL)
          #   docs = {}

          # with open(path_to_index+"/title/docfreq_"+str(self.file_index)+'.pkl', 'wb') as out_file:
          #   pickle.dump(docs_freq, out_file, protocol=pickle.HIGHEST_PROTOCOL)
          #   docs_freq = {}

          with open(path_to_index+"/title.txt", 'a') as out_file:
            for doc in docs:
              out_file.write(str(doc)+'\t'+str(docs[doc])+'\n')
            docs = {}

          with open(path_to_index+"/docfreq.txt", 'a') as out_file:
            for doc in docs_freq:
              out_file.write(str(doc)+'\t'+str(docs_freq[doc])+'\n')
            docs_freq = {}
          
          self.file_index += 1
          self.end_t = time()
          print("Time taken: ")
          print(self.end_t-self.start_t)
          
        if(self.index%self.offset==1):
          self.start_t = time()

    elif tag_name=="title":
      self.title = ""
    elif tag_name=="text":
      self.text = ""
    elif tag_name == "revision":
      self.revision_bool = True

    self.raw_tag = tag_name

  def endElement(self, tag_name):
    global token_size
    global docs
    global docs_freq

    if(self.index>(self.offset*self.prev_files) and tag_name=="text"):
      title_tokens, infobox_tokens, category_tokens, external_links_tokens, references_tokens, body_tokens = set(), set(), set(), set(), set(), set()
      title_tokens, token_len = processTitle(self.title)
      
      token_size += token_len
      infobox_tokens, category_tokens, external_links_tokens, references_tokens, body_tokens, token_len = parse_text(self.text)
      token_size += token_len

      vocab = list(title_tokens.keys()) + list(infobox_tokens.keys()) + list(category_tokens.keys()) + list(external_links_tokens.keys()) + list(references_tokens.keys()) + list(body_tokens.keys())
      docs[self.index] = self.title
      docs_freq[self.index] = len(vocab)
      vocab = set()
      for token in vocab:
        posting = "d"+str(self.index)
        if token not in inverted_index:
          inverted_index[token] = []

        if token in title_tokens:
          posting += "t"+str(title_tokens[token])

        if token in body_tokens:
          posting += "b"+str(body_tokens[token])

        if token in infobox_tokens:
          posting += "i"+str(infobox_tokens[token])

        if token in category_tokens:
          posting += "c"+str(category_tokens[token])

        if token in references_tokens:
          posting += "r"+str(references_tokens[token])

        if token in external_links_tokens:
          posting += "l"+str(external_links_tokens[token])

        inverted_index[token].append(posting)
      del vocab
      del title_tokens
      del infobox_tokens
      del category_tokens
      del external_links_tokens
      del references_tokens
      del body_tokens
    self.raw_tag = ""

  def characters(self, content):
    if self.raw_tag=="title":
      self.title += content
    elif self.raw_tag=="id" and not self.revision_bool:
      self.Id = content
    elif self.raw_tag=="text":
      self.text += content

  def get_length(self):
    return len(inverted_index)


def createFinalIndex():
  alpha = [chr(i) for i in range(ord('a'),ord('z')+1)]
  nums = [chr(i) for i in range(ord('0'),ord('9')+1)]
  alpha_numeric = alpha + nums
  file_names = []
  file_names.extend(alpha+["num","oth"])

  vocab_c = 0
  files = 0
  file_size = 0

  path_to_index = sys.argv[2]+"/index/"
  path_to_title = sys.argv[2]+"/title/"
  path_to_finalindex = sys.argv[2]+"/inverted_index/"

  if(os.path.exists(path_to_index) and os.path.exists(path_to_title)):
    for char in file_names:
      print("Looking for index startwith: "+char)
      inverted_index = {}
      
      for file_name in os.listdir(path_to_index):
        print("Processing: ",file_name)
        file_ind = file_name.split("_")[1]
        file_ind = int(file_ind.replace(".pkl",""))
        temp = {}
        with open(path_to_index + file_name, "rb") as in_file:
          temp = pickle.load(in_file)
      
        for word, postings in temp.items():
          word = word.lower()
          if(len(word)>0):
            if word[0]==char or (char=="num" and word[0] in nums):
              if(word not in inverted_index):
                inverted_index[word.strip()] = postings
              else:
                inverted_index[word.strip()].extend(postings)

            elif (char=="oth" and word[0] not in alpha_numeric):
              if(word not in inverted_index):
                inverted_index[word.strip()] = postings
              else:
                inverted_index[word.strip()].extend(postings)
      
      if(len(inverted_index)>0):
        with open(path_to_finalindex+char+"_index.pkl", "wb") as out_file:
          pickle.dump(inverted_index, out_file, protocol = pickle.HIGHEST_PROTOCOL)
        files += 1
        vocab_c += len(inverted_index)
        file_size += os.path.getsize(path_to_finalindex+char+"_index.pkl")
        print("Pickle write to file: "+char+"_index.pkl is done")

  else:
    print("Path issue for intermediate files")

  return vocab_c, files, file_size


def main():	
  if len(sys.argv)>=4:
    filename = sys.argv[1]
    if os.path.exists(filename):

      ### make nested directories in the inverted index path
      path_to_index = sys.argv[2]
      if not os.path.exists(path_to_index):
        temp = path_to_index.split("/")
        if(len(temp)>1):
          parent_folder = temp[0]
          for folder in temp[1:]:
            if not os.path.exists(parent_folder+"/"+folder):
              os.mkdir(parent_folder+"/"+folder)
            parent_folder += "/"+folder
      
      if not os.path.exists(path_to_index+"/index"):
        os.mkdir(path_to_index+"/index")
      if not os.path.exists(path_to_index+"/inverted_index"):
        os.mkdir(path_to_index+"/inverted_index")
      if not os.path.exists(path_to_index+"/title"):
        os.mkdir(path_to_index+"/title")

      ### Parsing the wikidump contents for creation of inverted index
      parser = make_parser()
      handler = WikiParse()
      parser.setContentHandler(handler)

      fp = bz2.BZ2File(filename)
      parser.parse(fp)
      fp.close()
      
      with open(path_to_index+'/index/index_final.pkl', 'wb') as out_file:
        pickle.dump(inverted_index, out_file, protocol=pickle.HIGHEST_PROTOCOL)
      
      # vocab_size, fileCount, fileSize = createFinalIndex()

      # ## Saving the vocabsize, files count and files size for inverted index stats
      # index_stat_path = sys.argv[3]
      # try:
      #   with open(index_stat_path, "w") as fp:
      #     fp.write(str(vocab_size)+"\n")
      #     fp.write(str(fileCount)+"\n")
      #     fp.write(str(fileSize/(1024**3)))
      # except Exception as e:
      #   print(e)
    else:
      print("Wikidump file doesn't exists")
  else:
    print("Insufficient Arguments\n")
    print("Usage: python3 index.py <wikidump_path> <inverted_index_folder_path> <inverted_index_stats>")


if __name__ == "__main__":
	start_time = time()
	main()
	end_time = time()
	time_taken = end_time - start_time
	print("Time Spent: %.2f seconds" %(time_taken))