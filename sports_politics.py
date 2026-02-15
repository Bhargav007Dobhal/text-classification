import os, re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import kagglehub

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# -------------------------
# SIMPLE CLASSIFIER PIPE
# -------------------------
class DocClf:
    def __init__(self, path=None):
        self.path = path
        self.df = None
        self.vec = None
        self.models = {}
        self.preds = {}

    def load(self):
        if self.path is None:
            print("Downloading dataset...")
            p = kagglehub.dataset_download("sunilthite/text-document-classification-dataset")
            csv = os.path.join(p, "df_file.csv")
        else:
            csv = self.path

        self.df = pd.read_csv(csv)
        print("Rows:", len(self.df))

    def clean_txt(self, s):
        s = s.lower()
        s = re.sub(r"[^a-z0-9\s]", " ", s)
        return re.sub(r"\s+", " ", s).strip()

    def prep(self):
        self.df = self.df[self.df["Label"].isin([0,1])]
        self.df["Label"] = self.df["Label"].map({0:"Politics",1:"Sports"})
        self.df.dropna(subset=["Text"], inplace=True)
        self.df["clean"] = self.df["Text"].apply(self.clean_txt)

        X = self.df["clean"]
        y = self.df["Label"]

        Xtr, Xte, ytr, yte = train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)

        self.vec = TfidfVectorizer(max_features=5000,stop_words="english",ngram_range=(1,2))
        self.Xtr = self.vec.fit_transform(Xtr)
        self.Xte = self.vec.transform(Xte)
        self.ytr, self.yte = ytr, yte

    def train(self):
        self.models["NB"] = MultinomialNB().fit(self.Xtr,self.ytr)
        self.models["RF"] = RandomForestClassifier(n_estimators=200,n_jobs=-1,random_state=42).fit(self.Xtr,self.ytr)
        self.models["SVM"] = LinearSVC(random_state=42,max_iter=2000).fit(self.Xtr,self.ytr)

        for k,m in self.models.items():
            self.preds[k] = m.predict(self.Xte)

    def eval(self):
        print("\nRESULTS")
        for k,p in self.preds.items():
            acc = accuracy_score(self.yte,p)
            print(f"{k} -> {acc:.4f}")
            print(classification_report(self.yte,p))

    def plots(self):
        os.makedirs("plots",exist_ok=True)
        fig,ax = plt.subplots(1,3,figsize=(14,4))

        for i,(k,p) in enumerate(self.preds.items()):
            cm = confusion_matrix(self.yte,p)
            sns.heatmap(cm,annot=True,fmt="d",ax=ax[i],cmap="Blues")
            ax[i].set_title(k)

        plt.tight_layout()
        plt.savefig("plots/confusion.png",dpi=300)
        plt.show()

    def predict(self, text, model="SVM"):
        s = self.clean_txt(text)
        v = self.vec.transform([s])
        return self.models[model].predict(v)[0]

    def run(self):
        self.load()
        self.prep()
        self.train()
        self.eval()
        self.plots()


def main():
    clf = DocClf()
    clf.run()

    tests = [
        "The striker scored a hat trick",
        "Government passed new tax bill",
        "Team lifted the trophy"
    ]

    for t in tests:
        print(t,"->",clf.predict(t))

if __name__ == "__main__":
    main()
