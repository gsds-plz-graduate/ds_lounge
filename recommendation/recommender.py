import joblib
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class Recommender():
    def __init__(self, 
               file_dir = os.path.join(os.path.abspath(__file__), 'data'), 
               tfidf_fname = 'tfidf_tdm.pkl', 
               cid_fname = 'cid_list.pkl'):
        self.tfidf = joblib.load(os.path.join(file_dir, tfidf_fname))
        self.cid_list = joblib.load(os.path.join(file_dir, cid_fname))

    def get_content_based_candidates(self, 
                                   grade_df,
                                   corpus = None,
                                   k = 10):
      
        # generate user representations
        tfidf_list = []
        indices = []
        for cid in grade_df['cid']:
            if cid == 'M3239.002000':  # 데이터사이언스 대학원논문연구
                continue
            idx = np.where(self.cid_list==cid)[0]
            if len(idx) == 0:
                print(f"{cid} not in list")
                continue 
            else: 
                indices.append(idx)
                tfidf_list.append(self.tfidf[idx,:].toarray())
        user_embed = np.mean(np.stack(tfidf_list), axis=0)

        # define item representations
        if corpus is None: # you can use entire corpus
            item_embed = self.tfidf
        else: # you can provide a subset of corpus as an argument
            item_embed = corpus
            
        # calculate cosine similarity
        cosine_sim = cosine_similarity(user_embed, item_embed)

        sim_scores = list(enumerate(cosine_sim[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = [x for x in sim_scores if x[0] not in indices] # drop indices of already taken courses
        sim_scores = sim_scores[1:k+1]
        rec_indices = [i[0] for i in sim_scores]

        return self.cid_list[np.array(rec_indices)]

if __name__ == "__main__":

    import pandas as pd
    grade_df = pd.DataFrame({'cid': ['M3239.000200',
                                    'M3239.000900',
                                    'M3239.000300',
                                    'M3224.000100',
                                    'M3239.002000',
                                    'M3239.001100',
                                    'M3239.000100',
                                    'M3239.001000',
                                    'M3239.004100']})
    rec = Recommender()
    candidates_content = rec.get_content_based_candidates(grade_df)