with open("顺控生成.csv","r",encoding='utf-8') as f:
    ls=f.read().splitlines()

with open("顺控模板.txt","r") as f:
    readed=f.read()

with open("顺控模板9.txt","r") as f:
    readed9=f.read()

TITLE = """selected,Action,Record,PntName,PntType,DataType,Domain,Drop,Control,Description,Character,Unit,Set,Reset,FC,Location,Channel,ChType,RefNum,Security,BD,EvHigh,EvLow,InitAS,InitAS2,InitValue,DpuSave,History,MathDeal,ValueLimit,Filter,SOE,Reverse,HSRDB,SendAlarm,SHighAlarm,SLowAlarm,HighSetAlarm,LowResetAlarm,AlarmDB,HighLimit,LowLimit,HAlarmAddr,LAlarmAddr,SensorType,SensorParam,C0,C1,C2,C3,C4,C5,SensorHigh,SensorLow,FilterFactor,HighAlarmPriority,LowAlarmPriority
选中,动作,记录类型,点名,类型,数据类型,域,站,控制区,描述,特征字,工程单位,1描述,0描述,功能分类,卡位,通道,通道类型,引用计数,安全字,周期,量程上限,量程下限,初始状态字1,初始状态字2,初始值,定时保存,保存历史,信号处理方式,限值检查,滤波处理,SOE,反相,历史死区,发送报警,传感器高限报警,传感器低限报警,高限/1报警,低限/0报警,报警死区,报警上限,报警下限,变上限报警,变下限报警,传感器类型,传感器参数,C0,C1,C2,C3,C4,C5,传感器上限,传感器下限,滤波因子,高限/1报警优先级,低限/0报警优先级
"""
GP = """Y,addUpdate,Point,GP点,GP,Gp,域号,站号,1,,,,,,0,,,,0,0x01,1,,,0x00,0x00,0x00,0,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
"""
GPL = {}

be_change = ls[0].strip().split(",")
for line in ls[1:]:
    changed=line.strip().split(",")
    if(int(changed[3])>9):
        read=readed[:]
    else:
        read=readed9[:]

    for x in range(0,len(be_change)):
        if(be_change[x] and be_change[x] not in ("域","站","页","步数","GP")):
            read=read.replace(be_change[x],changed[x])
            if("GP" in be_change[x] and changed[x]):
                TMP = changed[0]+"."+changed[1]
                if(TMP not in GPL):
                    GPL[TMP] = TITLE[:]
                GP0 = GP[:]
                GP0 = GP0.replace("GP点",changed[x])
                GP0 = GP0.replace("域号",changed[0])
                GP0 = GP0.replace("站号",changed[1])
                GPL[TMP] = GPL[TMP]+GP0

    print(changed[4])
    print(read)

for each in GPL:
    with open("./导入点/"+each+".csv","w") as f:
        f.write(GPL[each])
