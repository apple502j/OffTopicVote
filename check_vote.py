from time import sleep
from datetime import datetime as dt
from bs4 import BeautifulSoup
import requests
import github3

def isABC(v):
    if v in ["a","A","ａ","Ａ"]:
        return "A"
    elif v in ["b","B","ｂ","Ｂ"]:
        return "B"
    elif v in ["c","C","ｃ","Ｃ"]:
        return "C"
    else:
        return None

comment = "https://scratch.mit.edu/site-api/comments/gallery/5130077/?page="
votes = {
    "A":[],
    "B":[],
    "C":[]
    }
voted_names = []
error_msgs=[]
unknowns=[]
cnt=0

while True:
    cnt=cnt+1
    try:
        x=requests.get("https://scratch.mit.edu/site-api/comments/gallery/5130077/?page="+str(cnt))
        if x.status_code == 404:
            break
        soup=BeautifulSoup(x.text, "html.parser")
        names=list(map(lambda x:x.string.strip(),soup.select("div.name a")))
        contents=list(map(lambda x:x.string,soup.find_all(class_="content")))
        # 2018-07-02T12:48:44Z
        times=list(map(lambda x:dt.strptime(x.get("title"),"%Y-%m-%dT%H:%M:%SZ"), soup.find_all(class_="time")))
        for i in range(len(names)):
            name = names[i]
            content = str(contents[i]).strip()
            time = times[i]
            res = isABC(content)
            if res:
                if name in voted_names:
                    error_msgs.append("二重投票 {0} {1} 票:{2}".format(name,time,res))
                    continue
                else:
                    voted_names.append(name)
                    votes[res].append((name, time))
                    continue
            else:
                unknowns.append((name, content, time))
                continue
        sleep(1)
    except KeyboardInterrupt:
        raise SystemExit
print(votes)
print(unknowns)
print(error_msgs)

detail_msgs = []

all_num = len(votes["A"]) + len(votes["B"]) + len(votes["C"])
A_per = round(len(votes["A"]) / all_num * 100)
B_per = round(len(votes["B"]) / all_num * 100)
C_per = round(len(votes["C"]) / all_num * 100)

detail_msgs.append("A {0}% ({1})".format(A_per, len(votes["A"])))
detail_msgs.append("B {0}% ({1})".format(B_per, len(votes["B"])))
detail_msgs.append("C {0}% ({1})".format(C_per, len(votes["C"])))
detail_msgs.append("合計 {0}".format(all_num))

for A in votes["A"]:
    detail_msgs.append("A: {0} 時刻 {1}".format(A[0],A[1]))
for B in votes["B"]:
    detail_msgs.append("B: {0} 時刻 {1}".format(B[0],B[1]))
for C in votes["C"]:
    detail_msgs.append("C: {0} 時刻 {1}".format(C[0],C[1]))
for D in unknowns:
    detail_msgs.append("不明: {0} 時刻 {1} 内容 {2}".format(D[0],D[1],D[2]))
for E in error_msgs:
    detail_msgs.append(E)

detail_text = "\n".join(detail_msgs)

GRAPH = 10

with open("index.html", "r", encoding="utf-8") as html:
    html_content = html.read()
    html_content = html_content.format(Aw=A_per*GRAPH, Ac=A_per, Bw=B_per*GRAPH, Bc=B_per, Cw=C_per*GRAPH, Cc=C_per, detail=detail_text)
    with open("vote_result.html","w", encoding="utf-8") as html_result:
        html_result.write(html_content)

with open('settings.txt') as f:
    gh_user = f.readline().strip()
    gh_pass = f.readline().strip()
    gh_repo = f.readline().strip()
g=github3.login(gh_user,gh_pass)
repo=g.repository(gh_user,gh_repo)
vr=repo.file_contents("vote_result.html")
vr.update("update", html_content.encode("utf-8"))
