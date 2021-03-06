import jdCookie
import json
import requests
import time

"""
1、从jdCookie.py处填写 cookie
2、shareCode 为自己的助力码，但是需要别人为自己助力
3、欢迎留下shareCode互助
4、waterTimesLimit 自定义的每天浇水最大次数，防止浪费

"""
waterTimesLimit = 30
shareCodes = ["c081c648576e4e61a9697c3981705826",
              "f1d0d5ebda7c48c6b3d262d5574315c7",
              "13d13188218a4e3aae0c4db803c81985"]


def postTemplate(cookies, functionId, body):
    headers = {
        'User-Agent': 'JD4iPhone/167249 (iPhone; iOS 13.5.1; Scale/3.00)',
        'Host': 'api.m.jd.com',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    params = (
        ('functionId', functionId),
    )
    data = {
        'body': json.dumps(body),
        "appid": "wh5",
        "clientVersion": "9.0.4"
    }
    response = requests.post(
        'https://api.m.jd.com/client.action', headers=headers, cookies=cookies, data=data, params=params)
    return response.json()


def getTemplate(cookie, functionId, body):
    headers = {
        'User-Agent': 'JD4iPhone/167249 (iPhone; iOS 13.5.1; Scale/3.00)',
        'Host': 'api.m.jd.com',
        # 'Content-Type': 'application/x-www-form-urlencoded',
    }
    body["version"] = 4
    body["channel"] = 1
    params = (
        ('functionId', functionId),  # initForTurntableFarm
        ('body', json.dumps(body)),
        ('appid', 'wh5'),
    )

    response = requests.get('https://api.m.jd.com/client.action',
                            headers=headers, params=params, cookies=cookies)
    return response.json()


def luck(cookies):
    print("\n【随机水滴】")
    result = postTemplate(cookies, "gotWaterGoalTaskForFarm", {"type": 3})
    if result["code"] == "0":
        print("addEnergy ", result["addEnergy"])
    if result["code"] == "7":
        print("暂无")


def initFarm(cookies):
    result = postTemplate(cookies, 'initForFarm', {"version": 4})
    nickName = result["farmUserPro"]["nickName"]
    myshareCode = result["farmUserPro"]["shareCode"]
    treeEnergy = result["farmUserPro"]["treeEnergy"]
    lastTimes = int((result["farmUserPro"]["treeTotalEnergy"]-treeEnergy)/10)
    print(f"""\n\n[ {nickName} ]\n{result["farmUserPro"]["name"]}""")
    print(f"""我的助力码: {myshareCode}""")
    print(
        f"""treeEnergy: {treeEnergy}/{result["farmUserPro"]["treeTotalEnergy"]}""")
    print(
        f"""预计浇水次数: {lastTimes}""")


def water(cookies, totalWaterTaskTimes):
    print("\n【Water】")
    totalEnergy = postTemplate(cookies, "initForFarm", {"version": 2})[
        "farmUserPro"]["totalEnergy"]
    print(f"当前水滴: {totalEnergy}")
    if totalWaterTaskTimes >= waterTimesLimit:
        print("跳过浇水")
        print("已达今日最大浇水次数 ", waterTimesLimit)
        print("\n请自行修改 waterTimesLimit")
        return
    n = waterTimesLimit-totalWaterTaskTimes
    for i in range(int(totalEnergy/10)):
        if n == 0:
            print("浇水次数限制,结束浇水")
            return
        print(f"自动浇水...[{i}]")
        time.sleep(0.2)
        waterInfo = postTemplate(cookies, "waterGoodForFarm", {})
        print(waterInfo)
        if waterInfo["finished"]:
            print("\n水果成熟,退出浇水")
            return
        if waterInfo["waterStatus"] == 1:
            print(postTemplate(cookies, "gotStageAwardForFarm", {"type": 1}))  # 奖励30水
        if waterInfo["waterStatus"] == 2:
            print(postTemplate(cookies, "gotStageAwardForFarm", {"type": 2}))  # 奖励40水
        n -= 1


def takeTask(cookies):
    print("\n【任务列表】")

    taskList = postTemplate(cookies, "taskInitForFarm", {})
    # print(taskList["taskOrder"])
    if "signInit" in taskList:
        _signInit = taskList["signInit"]  # 连续签到
        print(f"""todaySigned: {_signInit["todaySigned"]}""")
        if not _signInit["todaySigned"]:
            print("连续签到")
            postTemplate(cookies, "signForFarm", {"type": 2})

    _gotBrowseTaskAdInit = taskList["gotBrowseTaskAdInit"]  # 浏览
    print(f"""BrowseTaskAd: {_gotBrowseTaskAdInit["f"]}""")
    if not _gotBrowseTaskAdInit["f"]:
        for i in _gotBrowseTaskAdInit["userBrowseTaskAds"]:
            print("浏览广告")
            postTemplate(cookies, "browseAdTaskForFarm", {
                         "type": 0, "advertId": i["advertId"]})
            time.sleep(0.4)
            postTemplate(cookies, "browseAdTaskForFarm", {
                         "type": 1, "advertId": i["advertId"]})

    _gotThreeMealInit = taskList["gotThreeMealInit"]  # 定时领水 6-9，11-14，17-21
    print(f"""ThreeMeal: {_gotThreeMealInit["f"]}""")
    if not _gotThreeMealInit["f"]:
        print("三餐定时领取")
        postTemplate(cookies, "gotThreeMealForFarm", {})

    _firstWaterInit = taskList["firstWaterInit"]  # 每日首次浇水
    print(f"""firstWater: {_firstWaterInit["f"]}""")
    if not _firstWaterInit["f"]:
        print("首次浇水奖励")
        postTemplate(cookies, "firstWaterTaskForFarm", {})

    _totalWaterTaskInit = taskList["totalWaterTaskInit"]  # 每日累计浇水
    print(
        f"""totalWaterTask: {_totalWaterTaskInit["f"]}  ({_totalWaterTaskInit["totalWaterTaskTimes"]}/10)""")
    if not _totalWaterTaskInit["f"]:
        print("浇水10次奖励")
        postTemplate(cookies, "totalWaterTaskForFarm", {})

    _waterRainInit = taskList["waterRainInit"]  # 收集水滴雨
    print(f"""waterRain: {_waterRainInit["winTimes"]}/2""")
    if not _waterRainInit["f"]:
        print(">>>>水滴雨")
        postTemplate(cookies, "waterRainForFarm", {
            "type": 1, "hongBaoTimes": 100, "version": 3})
    return _totalWaterTaskInit["totalWaterTaskTimes"]


def _help(cookies, shareCodes):
    for i in shareCodes:
        postTemplate(cookies, "initForFarm", {"shareCode": i})


def masterHelp(cookies):
    print("\n【助力得水】")
    help_me_list = postTemplate(cookies, "masterHelpTaskInitForFarm", {})
    masterHelpPeoples = len(help_me_list["masterHelpPeoples"])
    print(
        f"""完成进度 {masterHelpPeoples}/5   {help_me_list["f"]}""")
    if not help_me_list["f"] and masterHelpPeoples >= 5:
        print("领取奖励")
        help_me_list1 = postTemplate(
            cookies, "masterGotFinishedTaskForFarm", {})
        print(help_me_list1)


def clockIn(cookies):
    print("\n【打卡领水】")
    clockInInit = postTemplate(
        cookies, "clockInInitForFarm", {})
    if clockInInit["totalSigned"] == 7 and not clockInInit["gotClockInGift"]:  # 惊喜礼包
        print('[领取惊喜礼包]', postTemplate(cookies, "clockInForFarm", {"type": 2}))

    print(f"""todaySigned: {clockInInit["todaySigned"]}""")
    if not clockInInit["todaySigned"]:
        print("今日签到")
        print(postTemplate(cookies, "clockInForFarm", {"type": 1}))

    if "themes" in clockInInit:
        if clockInInit["themes"]:
            print(
                f""">>> 限时关注得水滴 {clockInInit["myFollowThemeConfigTimes"]}/3""")
            for i in [i["id"] for i in clockInInit["themes"] if not i["hadGot"]]:
                print(f"""关注id [{i}]""")
                postTemplate(cookies, "clockInFollowForFarm", {
                    "id": i, "type": "theme", "step": 1})
                time.sleep(0.5)
                postTemplate(cookies, "clockInFollowForFarm", {
                    "id": i, "type": "theme", "step": 2})
                time.sleep(0.5)

    if "venderCoupons" in clockInInit:
        if clockInInit["venderCoupons"]:
            print(
                f""">>> 限时领券得水滴 {clockInInit["myFollowVenderCouponTimes"]}/3""")
            for i in [i["id"] for i in clockInInit["venderCoupons"] if not i["hadGot"] and i["hadStock"]]:
                print(f"""领券id [{i}]""")
                print(i)
                time.sleep(0.5)
                postTemplate(cookies, "clockInFollowForFarm",
                             {"id": i, "type": "venderCoupon", "step": 1})
                time.sleep(0.5)
                postTemplate(cookies, "clockInFollowForFarm",
                             {"id": i, "type": "venderCoupon", "step": 2})


def turnTable(cookies):
    print("\n【天天抽奖】")
    result = getTemplate(cookies, "initForTurntableFarm", {})
    if not result["timingGotStatus"] and result["sysTime"]-result["timingLastSysTime"] > 14400000:  # 领取定时奖励
        print('[定时奖励] ', getTemplate(
            cookies, "timingAwardForTurntableFarm", {}))
    print(
        f"""为我助力: {result["masterHelpTimes"]}/{result["helpedTimesByOther"]}""")

    for i in shareCodes:
        getTemplate(cookies, "initForFarm", {"shareCode": f"{i}-3"})  # 助力

    result = getTemplate(cookies, "initForTurntableFarm", {})
    for i in range(result["remainLotteryTimes"]):  # 抽奖次数
        print(f'[抽奖 {i}] ', getTemplate(
            cookies, "lotteryForTurntableFarm", {"type": 1}))  # 抽奖
        time.sleep(0.4)


for cookies in jdCookie.get_cookies():
    initFarm(cookies)
    turnTable(cookies)
    clockIn(cookies)
    _help(cookies, shareCodes)
    totalWaterTaskTimes = takeTask(cookies)
    masterHelp(cookies)
    luck(cookies)
    water(cookies, totalWaterTaskTimes)
    print("\n")
    print("##"*30)
