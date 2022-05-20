
class InterpolationLM(NGramLM):
  def __init__(self,texts,n,vocabulary):
    self.unigram_counts = get_counts(texts,1)
    self.bigram_counts = get_counts(texts,2)
    self.trigram_counts = get_counts(texts,3)
    self.n = n

    #get total counts:
    self.total_counts = 0

    for word in self.unigram_counts:
      self.total_counts+= self.unigram_counts[word] 
    self.unigram_pr = {word: self.unigram_counts[word]/self.total_counts for word in self.unigram_counts}
   
    self.bigram_pr = {}
    for bigram in self.bigram_counts:
      context = bigram[0]
      prediction = bigram[1]
      probability = self.bigram_counts[bigram] / self.unigram_counts[context]
      if context not in self.bigram_pr:
        self.bigram_pr[context]={}
      self.bigram_pr[context][prediction] = probability
   
    self.trigram_pr = {}
    for trigram in self.trigram_counts:
      context = trigram[:-1]
      prediction = trigram[-1]
      probability = self.trigram_counts[trigram] / self.bigram_counts[context]
      if context not in self.trigram_pr:
        self.trigram_pr[context] = {}
      self.trigram_pr[context][prediction] = probability
    # raise NotImplementedError("STEP 5: Initialize the Interpolation LM")
 
  def generate_text(self, length,interpolants,prompt=[]):
    self.length = length
    return_prompt = prompt
    self.interp_pr = {}
    for word1, word2 in self.trigram_pr:
      self.interp_pr[(word1, word2)] = {}
      for word in self.trigram_pr[(word1, word2)]:
        self.interp_pr[(word1, word2)][word] = interpolants[0] * self.trigram_pr[(word1, word2)][word] 
        + interpolants[1]*self.bigram_pr[word2][word] + self.unigram_pr[word]
    if(return_prompt==[]):
      word1, word2 = random.choice(list(self.interp_pr))
      return_prompt.append(word1)
      return_prompt.append(word2)
      self.length = self.length -2
    for i in range(0, self.length):
      # print((return_prompt[i], return_prompt[i+1]))
      if((return_prompt[i], return_prompt[i+1]) in self.interp_pr):
        return_prompt.append(random.choices(population=list(self.interp_pr[(return_prompt[i], return_prompt[i+1])]), 
                                            weights= list(self.interp_pr[(return_prompt[i], return_prompt[i+1])].values()))[0])
      else:
        word1, word2 = random.choice(list(self.interp_pr))
        return_prompt.append(word1)
        return_prompt.append(word2)
        i=i+1
    return return_prompt
    # print(self.interp_pr)
    # raise NotImplementedError("STEP 5: Given a prompt (a list of strings) generate length number of strings -- return a list containing all of the text (prompt + generated) ")

  def score_text(self,text,interpolants):
    for word1, word2 in self.trigram_pr:
      self.interp_pr[(word1, word2)] = {}
      for word in self.trigram_pr[(word1, word2)]:
        self.interp_pr[(word1, word2)][word] = interpolants[0] * self.trigram_pr[(word1, word2)][word] 
        + interpolants[1]*self.bigram_pr[word2][word] + self.unigram_pr[word]
    log_prob = 0
    for i in range(0, len(text) - 3):
      if((text[i], text[i+1]) not in self.interp_pr):
        return float('inf')
      else:
        if text[i+2] not in self.interp_pr[(text[i], text[i+1])]:
          return float('inf')
        else:
          log_prob += np.log(self.interp_pr[(text[i], text[i+1])][text[i+2]])
    log_prob /= (len(text)-1)
    return 2**(-log_prob)
    # raise NotImplementedError("STEP 5: Given a text, return the perplexity of that text ")

# lm = InterpolationLM(texts, 3, vocab)
# lm.generate_text(20, interpolants=[1/3, 1/3, 1/3])
# lm.return_prompt
# lm.interp_pr
for interpolants in [[1/3, 1/3, 1/3],[0.1,0.2,0.7],[0.7,0.2,0.1]]:
  print(f'Interpolants = {interpolants}')
  lm = InterpolationLM(texts,3,vocab)

  print(' '.join(lm.generate_text(20,interpolants, [])))
  print(' '.join(lm.generate_text(20,interpolants,['palm', 'to'])))

  print(lm.score_text(['IBM','announced','today','that','they','will','be','buying','Google'],interpolants))
  print(lm.score_text(['palm', 'to', 'palm', 'is', 'holy', 'palmers'],interpolants))
  print(lm.score_text(['what','do','you','say','to','that','Hamlet'],interpolants))