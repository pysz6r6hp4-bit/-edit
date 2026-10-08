# Transcript -> word timings. Segment times come from the supplied transcript;
# words inside a segment are spread by spoken length (letters, ellipsis = pause).
import re
SEGMENTS = [
    (0.30, 2.32, "cam", "هاني إيش عندك يا هاني؟"),
    (2.32, 3.82, "hani", "عثمان صلّي على النبي"),
    (3.82, 6.18, "hani", "اليوم الخميس … أحسن عروض على اللحمة يا معلم!"),
    (6.18, 8.34, "hani", "كمان في عروض على الكولا يا بابا"),
    (8.34, 11.92, "hani", "إي واحدة … إي اثنين … إي ثلاثة … إي أربعة يا عثمان!"),
    (11.92, 13.42, "hani", "لسّه ما خلّصتش"),
    (13.42, 15.64, "hani", "إي خمسة … إي ستة يا بابا!"),
    (15.64, 17.38, "cam", "ست علب هدول بكم يا معلم؟"),
    (18.25, 19.98, "cam", "هدول بخمستعش عندك؟"),
    (19.98, 21.48, "hani", "مش خمستعش يا عثمان!"),
    (21.48, 24.48, "hani", "هدول الستة بعشرة شيكل يا حج!"),
    (24.48, 28.44, "hani", "طقم الستة بعشرة شيكل … كوكاكولا 300 مل"),
    (29.66, 31.56, "hani", "حاجة ألف يا بابا!"),
    (31.56, 32.96, "hani", "عند فروج الحلو يا معلم"),
    (32.96, 35.84, "hani", "عنواننا معروف … شارع النصر مقابل برج الشفاء"),
    (35.84, 38.18, "hani", "أهلاً وسهلاً بكم … تشرّفونا وبتنوّرونا"),
    (38.18, 39.20, "cam", "حط إيدك على الكاميرا"),
]
DIAC = re.compile(r"[ً-ْـ]")

def _weight(tok):
    return 2.2 if tok == "…" else len(DIAC.sub("", tok).strip("؟!")) + 1.2

def words():
    out = []
    for si, (s, e, spk, text) in enumerate(SEGMENTS):
        toks = text.split()
        tot = sum(_weight(t) for t in toks)
        t = s
        for tok in toks:
            d = (e - s) * _weight(tok) / tot
            if tok != "…":
                out.append(dict(w=tok, s=round(t, 3), e=round(t + d, 3), seg=si, spk=spk))
            t += d
    return out

def chunks(max_words=4):
    """Caption pages: break at ellipses, then split each run into balanced pages."""
    import math
    pages = []
    for si, (s, e, spk, text) in enumerate(SEGMENTS):
        ws = iter([w for w in WORDS if w["seg"] == si])
        runs, cur = [], []
        for tok in text.split():
            if tok == "…":
                runs.append(cur); cur = []
            else:
                cur.append(next(ws))
        runs.append(cur)
        for run in filter(None, runs):
            k = math.ceil(len(run) / max_words)
            size = math.ceil(len(run) / k)
            for i in range(0, len(run), size):
                g = run[i:i + size]
                pages.append(dict(words=g, s=g[0]["s"], e=g[-1]["e"], spk=spk))
    return pages

WORDS = words()
PAGES = chunks()

def word_time(word, nth=0):
    hits = [w for w in WORDS if w["w"].strip("؟!") == word]
    return hits[nth]["s"]

if __name__ == "__main__":
    for p in PAGES:
        print(f'{p["s"]:6.2f}-{p["e"]:6.2f} {p["spk"]:4s} ' + " | ".join(f'{w["w"]}@{w["s"]:.2f}' for w in p["words"]))
