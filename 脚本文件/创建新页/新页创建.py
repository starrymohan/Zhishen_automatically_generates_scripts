import re
import os

with open("新页数据.csv","r") as f:
    ls=f.read().splitlines()

with open("模板.txt","r") as f:
    readed=f.read()

be_change = ls[0].strip().split(",")
for line in ls[1:]:
    changed=line.strip().split(",")
    read=readed[:]

    for x in range(0,len(be_change)):
        if(be_change[x] in ("域","站","页")):
            read=re.sub(
                be_change[x]+"号@@0@@([\d]*?)@1@0@1",
                be_change[x]+"号@@0@@"+str(changed[x])+"@1@0@1",
                read)

    tmp = "./test/"+changed[0]+"."+changed[1]
    if(not os.path.exists(tmp)):
        os.mkdir(tmp)

    with open(tmp+"/"+changed[x]+".cbp","w") as f:
        f.write(read)

    print(changed[3])

