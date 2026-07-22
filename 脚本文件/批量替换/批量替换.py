with open("批量替换.csv","r",encoding="utf-8") as f:
    ls=f.read()[1:].splitlines()
    
with open("模板.txt","r",encoding="utf-8") as f:
    readed=f.read()

str0=""
be_change = ls[0].strip().split(",")
for line in ls[1:]:
    changed=line.strip().split(",")
    read=readed[:]

    for x in range(0,len(be_change)):
        if(be_change[x]):
            read=read.replace(be_change[x],changed[x])

    print(changed[0])
    str0=str0+read

print(str0)

