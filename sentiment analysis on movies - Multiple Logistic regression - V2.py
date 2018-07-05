#0 = bad
#1 = somewhat bad
#2 = neutral
#3 = somewhat good
#4 = good


import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error as msq
from nltk import word_tokenize, pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from tqdm import tqdm
from textpreprocess import cleanText
import pickle
# %%
review_text = []
review_rating = []
authors = ['Dennis+Schwartz','James+Berardinelli','Scott+Renshaw','Steve+Rhodes']
for author in authors:

    array1 = open('MovieReview/scaledata/'+author+'/subj.'+author).read().split('\n')
    array2 = open('MovieReview/scaledata/'+author+'/label.4class.'+author).read().split('\n')
    review_text = review_text+array1
    review_rating = review_rating+array2
    #index_array = range(5010,5010+156060)

df_one = pd.DataFrame(data={'Phrase':review_text, 'Sentiment':review_rating})
for i in tqdm(range(0, df_one['Sentiment'].shape[0])):
    if df_one['Sentiment'][i] != '':
        if (df_one['Sentiment'][i] == '0') | (df_one['Sentiment'][i] == '1'):
            df_one['Sentiment'][i] = int(df_one['Sentiment'][i])
        else:
            df_one['Sentiment'][i] = int(df_one['Sentiment'][i]) + 1
df_one = df_one[(df_one['Phrase'].str.len() > 10) | (df_one['Sentiment'] != '')]
df_one['Sentiment'] = df_one['Sentiment'].astype(int)
df_two = pd.read_csv('train.tsv', delimiter='\t')[['Phrase','Sentiment']]
df_two = df_two.shift(5009).dropna()
frames = [df_one,df_two]
df = pd.concat(frames)

# %%

wordnet_tags = ['n', 'v']
def lemmatize(token, tag):
    if tag[0].lower() in ['n', 'v']:
        return lemmatizer.lemmatize(token, tag[0].lower())
    return token
lemmatizer = WordNetLemmatizer()


# %%

df_copy = df.copy()
X = df_copy['Phrase']#[df['Phrase'].str.split(' ').apply(len)<400]
Y = df_copy['Sentiment']#[df['Phrase'].str.split(' ').apply(len)<400]

X_clean = [cleanText(train_text) for train_text in X]
#tagged_X = [pos_tag(word_tokenize(document)) for document in X_clean]
#tagged_X_lemm = [[lemmatize(token, tag) for token, tag in document] for document in tagged_X]
#joined_lemm_X = [' '.join(text) for text in tagged_X_lemm]
#split into train and test data
X_train_clean , X_test_clean, Y_train, Y_test = train_test_split(X_clean,Y)


# %%
plt.plot(range(0,len(X_train_clean)),[len(string.split(' ')) for string in X_train_clean])

# %%
### WITHOUT USING GRID SEARCH ###
vectorizer = TfidfVectorizer(stop_words = 'english', max_df=0.25, ngram_range=(1,2),use_idf = False)
X_train = vectorizer.fit_transform(X_train_clean)
X_test = vectorizer.transform(X_test_clean)
X_vec = vectorizer.transform(X)

#regressor = LogisticRegression(C=10)
regressor = LogisticRegression(C=10, warm_start=True)
regressor.fit(X_train, Y_train)

##create confusion matrix
# confusion_matrix = confusion_matrix(Y_test, regressor.predict(X_test))
# print(confusion_matrix)
#
# # %%
# #plot and show the confusion matrix with color bar
# plt.matshow(confusion_matrix)
# plt.title('Sentiment Analysis from reviews')
# plt.ylabel('True Values')
# plt.xlabel('Predicted Values')
# plt.colorbar()
# plt.show()
#
# # %%
# #recall precision accuracy and f1 scores
# print('Accuracy: %s'%accuracy_score(Y_test, regressor.predict(X_test)))
# #print('Recall: %s'%recall_score(Y_test, regressor.predict(X_test), average='macro'))
# #print('Precision: %s'%precision_score(Y_test, regressor.predict(X_test), average='macro'))
# #print('F1: %s'%f1_score(Y_test, regressor.predict(X_test), average='macro'))
# print('CR: %s'%classification_report(Y_test, regressor.predict(X_test)))
# print('R Square: %s'%regressor.score(X_test, Y_test))
# print('Mean sqared error: %s'%msq(Y_test, regressor.predict(X_test)))

### USING GRID SEARCH ### (called only when the funtion main is called)
# %%
#CROSS VAL SCORE
#print('Cross Val Score: %s'%cross_val_score(regressor, X_vec, Y, cv=5))

# %%
def gs():
    pipeline = Pipeline([
        ('vect', TfidfVectorizer(stop_words = 'english')),
        ('reg', LogisticRegression())
    ])
    parameters = {
        'vect__max_df': (0.25, 0.5, 0.75),
        'vect__ngram_range': ((1, 1), (1, 2), (1,3)),
        'vect__use_idf': (True, False),
        'reg__C':(1, 10, 100)
    }
    grid_search = GridSearchCV(pipeline, parameters, n_jobs=-1, scoring='accuracy')
    grid_search.fit(X_train_clean, Y_train)
    print('Best score: %0.3f' % grid_search.best_score_)
    print ('Best parameters set:')
    best_parameters = grid_search.best_estimator_.get_params()
    for param_name in sorted(parameters.keys()):
        print ('\t%s: %r' % (param_name, best_parameters[param_name]))
    print('CR: %s'%classification_report(Y_test, grid_search.predict(X_test_clean)))
    print('R Square: %s'%grid_search.score(X_test_clean, Y_test))
    print('Mean sqared error: %s'%msq(Y_test, grid_search.predict(X_test_clean)))

# if __name__ == '__main__':
#    gs()
# %%
with open('rating-model.pkl','w') as file:
    print 'Writing model to a file'
    pickle.dump([regressor, vectorizer], file)
    print 'Write complete'
