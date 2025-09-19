import requests


def fun1():
    url = "https://www.kujiale.com/yuntai/api/niches?ids=3FO4K4W0CB3C%2C3FO4K4W0CEFD%2C3FO4K4W0DMVQ&param1=ignored;&param2=insert&param3=delete&param4=where"
    headers = {
        "User-Agent": "test_zhang",
        "Cookie": "qunhe-jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzM1OTkxNDEyNjMsInNfaWQiOiJjMjM5ZTJkNzdiOGExMWVkYWI2NDc1YjA1ZDJkYzcyMiIsImtfaWQiOiIzRk80TTVPNllRU0IiLCJ1dCI6NSwiYyI6MTY3MTAwNzE0MTI2MywiZSI6MTY3MzU5OTE0MTI2MywidXYiOjQsImlhZSI6ZmFsc2UsImFfaWQiOjE4Mjk3ODksInJfaWQiOjE4MDg4NDksImxvIjoiemhfQ04iLCJ1bCI6IkZBU1QiLCJyIjoiQ04ifQ.YR3DSD6MYZccMkTELyqixGzOgFyxBRlVhm4xIgx2ZzI"
    }

    ""
    response = requests.get(url, headers=headers)
    print(response.text)
    pass

def fun2():
    print("fun2-1")
    pass

def fun3():
    print("fun3")
    pass


if __name__ == '__main__':
    fun1()
