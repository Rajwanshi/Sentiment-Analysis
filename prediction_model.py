import pickle
from textpreprocess import cleanText

def loadModel():
    with open('rating-model.pkl','r') as file:
        model, vectorizer = pickle.load(file)
    return model, vectorizer

def predictor(reviewText):
    weights = (model.predict_proba(vectorizer.transform([reviewText])))[0]
    score = 0
    for i in enumerate(weights):
        score += (i[0]+1)*i[1]
    return "{:.2f}".format(score)

# %%
if __name__ == '__main__':
    model, vectorizer = loadModel()
    review = cleanText(open('./Samples/ittefaq','r').read())
    print(predictor(review))
