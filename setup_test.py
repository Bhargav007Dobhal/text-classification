#!/usr/bin/env python3
import sys, os, re

# ------------------------
# basic import check
# ------------------------
def chk_imports():
    print("Checking packages...\n")

    pkgs = [
        ("pandas","pandas"),
        ("numpy","numpy"),
        ("matplotlib","matplotlib.pyplot"),
        ("seaborn","seaborn"),
        ("sklearn","sklearn"),
        ("kagglehub","kagglehub"),
        ("wordcloud","wordcloud")
    ]

    bad = []

    for name, imp in pkgs:
        try:
            __import__(imp)
            print("OK:", name)
        except Exception as e:
            print("FAIL:", name, "-", e)
            bad.append(name)

    if bad:
        print("\nMissing:", ", ".join(bad))
        print("Run -> pip install -r requirements.txt")
        return False

    print("\nAll imports good.")
    return True


# ------------------------
# sklearn models
# ------------------------
def chk_models():
    print("\nTesting ML models...\n")
    try:
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.svm import LinearSVC

        MultinomialNB()
        RandomForestClassifier(n_estimators=10)
        LinearSVC()

        print("NB OK")
        print("RF OK")
        print("SVM OK")
        return True
    except Exception as e:
        print("Model error:", e)
        return False


# ------------------------
# text + tfidf
# ------------------------
def chk_text():
    print("\nTesting text pipeline...\n")
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer

        s = "This is a TEST! With 123 numbers."
        c = re.sub(r"[^a-z0-9\s]"," ",s.lower())
        c = re.sub(r"\s+"," ",c).strip()

        print("Original:", s)
        print("Cleaned :", c)

        tf = TfidfVectorizer(max_features=50,stop_words="english")
        X = tf.fit_transform([
            "The match was exciting",
            "Government passed bill",
            "Team won championship"
        ])

        print("TFIDF shape:", X.shape)
        return True
    except Exception as e:
        print("Text error:", e)
        return False


# ------------------------
# kaggle check
# ------------------------
def chk_kaggle():
    print("\nChecking Kaggle config...\n")
    p = os.path.expanduser("~/.kaggle/kaggle.json")

    if os.path.exists(p):
        print("Found:", p)
        return True
    else:
        print("Not found:", p)
        print("Create token -> Kaggle Account > API")
        print("Move kaggle.json to ~/.kaggle/")
        return False


# ------------------------
# main
# ------------------------
def main():
    print("="*45)
    print("SETUP TEST : SPORTS vs POLITICS")
    print("="*45)

    res = []
    res.append(chk_imports())
    res.append(chk_models())
    res.append(chk_text())
    kag = chk_kaggle()

    print("\nSUMMARY")
    if all(res):
        print("All good. Ready to run classifier.")
        if kag:
            print("Run -> python text_classifier.py")
        else:
            print("Or load local csv in classifier.")
    else:
        print("Fix errors above first.")
        sys.exit(1)


if __name__ == "__main__":
    main()
