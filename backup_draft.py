class BackOffLM(NGramLM):
  def __init__(self,texts,n,vocabulary):
    self.unigram_counts = get_counts(texts,1)
    self.bigram_counts = get_counts(texts,2)
    self.trigram_counts = get_counts(texts,3)
    self.n = n

    #get total counts:
    self.total_counts = 0
    for word in self.unigram_counts:
      self.total_counts+= self.unigram_counts[word] 
    if (n==1):
      self.unigram_pr = {word: self.unigram_counts[word]/self.total_counts for word in self.unigram_counts}
    elif(n==2):
      self.bigram_pr = {}
      for bigram in self.bigram_counts:
        context = bigram[0]
        prediction = bigram[1]
        probability = self.bigram_counts[bigram] / self.unigram_counts[context]
        if context not in self.bigram_pr:
          self.bigram_pr[context]={}
        self.bigram_pr[context][prediction] = probability
    elif(n==3):
      self.trigram_pr = {}
      for trigram in self.trigram_counts:
        context = trigram[:-1]
        prediction = trigram[-1]
        probability = self.trigram_counts[trigram] / self.bigram_counts[context]
        if context not in self.trigram_pr:
          self.trigram_pr[context] = {}
        self.trigram_pr[context][prediction] = probability
    # raise NotImplementedError("STEP 5b: Initialize the Backoff LM")
 
  def generate_text(self, length,prompt=[]):
    return_prompt = prompt
    self.length = length
    if(self.n == 1):
      for i in range(length - len(return_prompt)):
        return_prompt.append(random.choice(list(self.unigram_counts)))
      return return_prompt
    elif(self.n == 2):
      if return_prompt == []:
         return_prompt.append(random.choice(list(self.unigram_counts)))
         self.length = self.length - 1
      for i in range(self.length - len(return_prompt)):
        if(return_prompt[-1] in self.bigram_pr):
          return_prompt.append(random.choices(population=list(self.bigram_pr[return_prompt[-1].lower()]), 
                                              weights=list(self.bigram_pr[return_prompt[-1].lower()].values()))[0])
        else:
          return_prompt.append(random.choices(population=list(self.unigram_pr), weights=list(self.unigram_pr).values())[0])
      return return_prompt
    elif(self.n == 3):
      if (return_prompt == []):
        word1, word2 = random.choice(list(self.trigram_pr))
        return_prompt.append(word1)
        return_prompt.append(word2)

      while(len(return_prompt)<(self.length)):


        if((return_prompt[-2], return_prompt[-1]) in self.trigram_pr):
          return_prompt.append(random.choices(population=list(self.trigram_pr[(return_prompt[-2], return_prompt[-1])]), 
                                              weights=list(self.trigram_pr[(return_prompt[-2], return_prompt[-1])].values()))[0])

        elif(return_prompt[-1] in self.bigram_pr):
          return_prompt.append(random.choices(population=list(self.bigram_pr[return_prompt[-1].lower()]), 
                                              weights=list(self.bigram_pr[return_prompt[-1].lower()].values()))[0])

        else:
          return_prompt.append(random.choices(population=list(self.unigram_pr), weights=list(self.unigram_pr.values()))[0])

      return return_prompt
    raise NotImplementedError("STEP 5b: Given a prompt (a list of strings) generate length number of strings -- return a list containing all of the text (prompt + generated) ")

  def score_text(self,text):
    raise NotImplementedError("STEP 5b: Given a text, return the perplexity of that text ")

lm = BackOffLM(texts,3,vocab)

print(' '.join(lm.generate_text(20, [])))
print(' '.join(lm.generate_text(20,['palm', 'to'])))

# print(lm.score_text(['IBM','announced','today','that','they','will','be','buying','Google']))
# print(lm.score_text(['palm', 'to', 'palm', 'is', 'holy', 'palmers']))
# print(lm.score_text(['what','do','you','say','to','that','Hamlet']))