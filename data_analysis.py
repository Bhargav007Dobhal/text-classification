import re
from datetime import date

# ----------------------------
# small helpers
# ----------------------------
def lev(a, b):
    # keep a as longer string (tiny speed win)
    if len(a) < len(b):
        return lev(b, a)
    if not b:
        return len(a)

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        cur = [i + 1]
        for j, cb in enumerate(b):
            ins = prev[j + 1] + 1
            dele = cur[j] + 1
            rep = prev[j] + (ca != cb)
            cur.append(min(ins, dele, rep))
        prev = cur
    return prev[-1]


def save_log(lines, fn="m25mac001_prob1.log"):
    bar = "=" * 40
    with open(fn, "a", encoding="utf-8") as f:
        f.write("\n" + bar + "\n")
        f.write(f"RUN START : {date.today()}\n")
        f.write(bar + "\n")
        for x in lines:
            f.write(x + "\n")
        f.write(bar + "\nRUN END\n" + bar + "\n")


def parse_dob(s):
    # month name -> number
    mon = {
        "january": 1, "jan": 1,
        "february": 2, "feb": 2,
        "march": 3, "mar": 3,
        "april": 4, "apr": 4,
        "may": 5,
        "june": 6, "jun": 6,
        "july": 7, "jul": 7,
        "august": 8, "aug": 8,
        "september": 9, "sep": 9, "sept": 9,
        "october": 10, "oct": 10,
        "november": 11, "nov": 11,
        "december": 12, "dec": 12,
    }

    # 12 Mar 2001
    m = re.search(r"\b(\d{1,2})\s+([A-Za-z]+)\s+(\d{2,4})\b", s, re.I)
    if m:
        d = int(m.group(1))
        mm = mon.get(m.group(2).lower())
        y = int(m.group(3))
        if mm is None:
            return None
        if y < 100:
            y += 1900 if y > 50 else 2000
        return d, mm, y

    # 03-12-2001 or 3/12/01
    m = re.search(r"\b(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})\b", s)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        y = int(m.group(3))
        if y < 100:
            y += 1900 if y > 50 else 2000

        # decide day/month
        if a > 12:
            d, mm = a, b
        elif b > 12:
            mm, d = a, b
        else:
            # both possible -> assume mm-dd (common)
            mm, d = a, b
        return d, mm, y

    # 2001-03-12
    m = re.search(r"\b(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})\b", s)
    if m:
        y, mm, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return d, mm, y

    return None


def calc_age(d, m, y):
    t = date.today()
    bd = date(y, m, d)
    a = t.year - bd.year
    if (t.month, t.day) < (bd.month, bd.day):
        a -= 1
    return a


def mood(s):
    pos = ["good", "great", "happy", "excellent", "wonderful", "amazing", "fantastic", "fine"]
    neg = ["bad", "sad", "angry", "terrible", "awful", "horrible", "down", "annoyed"]
    wds = s.lower().split()

    # exact
    for w in wds:
        if w in pos:
            return "pos", w
        if w in neg:
            return "neg", w

    # fuzzy for typos
    for w in wds:
        if len(w) < 3:
            continue
        for p in pos:
            if lev(w, p) <= 2:
                return "pos", p
        for n in neg:
            if lev(w, n) <= 2:
                return "neg", n

    return None, None


def surname(full):
    s = re.sub(r"\b(mr|mrs)\.?\s+", "", full, flags=re.I).strip()
    parts = re.findall(r"[A-Za-z]+", s)
    return parts[-1] if len(parts) >= 2 else None


# ----------------------------
# chatbot
# ----------------------------
def chat():
    log = []
    state = "name"
    user = {"name": None, "ln": None, "age": None}

    def say(x):
        print(x)
        log.append(x)

    say("Reggy++: Hi! I'm Reggy++. What's your name?")

    while True:
        txt = input("You: ").strip()
        log.append("You: " + txt)

        if not txt:
            say("Reggy++: Please type something.")
            continue

        if re.search(r"\b(exit|quit|bye|goodbye)\b", txt.lower()):
            say(f"Reggy++: Goodbye, {user['name']}!" if user["name"] else "Reggy++: Goodbye!")
            save_log(log)
            break

        if state == "name":
            user["name"] = re.sub(r"[.,!?]+$", "", txt)
            user["ln"] = surname(user["name"])
            msg = f"Reggy++: Nice to meet you, {user['name']}!"
            if user["ln"]:
                msg += f" Surname: {user['ln']}."
            say(msg)
            say("Reggy++: When's your birthday?")
            state = "dob"
            continue

        if state == "dob":
            dob = parse_dob(txt)
            if not dob:
                say("Reggy++: Can't read that date. Try '12 Mar 2001' or '03-12-2001'.")
                continue

            d, m, y = dob
            a = calc_age(d, m, y)
            if not (0 <= a <= 150):
                say("Reggy++: That age looks wrong. Try again.")
                continue

            user["age"] = a
            say(f"Reggy++: Cool. You're {a} years old.")
            first = user["name"].split()[0] if user["name"] else "there"
            say(f"Reggy++: How you feeling today, {first}?")
            state = "mood"
            continue

        if state == "mood":
            tag, w = mood(txt)
            if tag == "pos":
                say(f"Reggy++: Nice. Feeling {w}.")
                state = "chat"
            elif tag == "neg":
                say(f"Reggy++: Sorry. Feeling {w}. Wanna talk?")
                state = "chat"
            else:
                say("Reggy++: More like good or bad?")
            continue

        # normal convo
        tag, w = mood(txt)
        if tag == "pos":
            say(f"Reggy++: Love that you're {w}.")
            continue
        if tag == "neg":
            say(f"Reggy++: Yeah, {w} days happen.")
            continue

        if txt.endswith("?"):
            say("Reggy++: Interesting. What do you think?")
        else:
            say("Reggy++: Tell me more.")


if __name__ == "__main__":
    chat()
