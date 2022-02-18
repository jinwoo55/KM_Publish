import time
import pyupbit
import datetime
import requests

access = "userAccessKey"         
secret = "userSecert" 
myToken = "xoxb-3070117775266-3093895970272-7rceqOSe0zpRMlRiTVPgQCHr"

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(response)


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_current_price(ticker=ticker)

# 로그인
upbit = pyupbit.Upbit(access, secret)
# 시작 메세지 슬랙 전송
post_message(myToken,"#crypto", "autotrade start")

#돌릴 코인 명
coin = ["KRW-BTC", "KRW-XRP", "KRW-ETH", "KRW-MATIC"]

#현재 보유 현금 (코인 개수만큼 나눠서 투자)
krw = get_balance("KRW")/len(coin)

print("자동매매 시작")

# 자동매매 시작
while True:
    try:

        print()
        print("-----------------------")
        oriKrw = get_balance("KRW")
        print("잔여 현금가 : " + str(oriKrw))
        print("구매 설정가 : " + str(krw))
        

        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        k = 0.3

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            for selCoin in coin:
                getCoinBal = get_balance(selCoin.replace('KRW-', ''))
                if getCoinBal * get_current_price(selCoin) < 5000:
                    print("진입 코인 " + selCoin)
                    target_price = get_target_price(selCoin, k)
                    ma15 = get_ma15(selCoin)
                    current_price = get_current_price(selCoin)
                    # print("목표가" + str(target_price))
                    # print("현재가" + str(current_price))
                    # print("이평선 " + str(ma15))
                    if target_price < current_price and ma15 < current_price:
                        if krw > 5000:
                            buy_result = upbit.buy_market_order(selCoin, krw*0.9995)
                            print(selCoin + " 코인 " + str(krw*0.9995) + " KRW 매수")
                            post_message(myToken,"#crypto",  selCoin + " buy : " +str(buy_result))
                    time.sleep(1)
        else:
            for selCoin in coin:
                getCoinBal = get_balance(selCoin.replace('KRW-', ''))
                if getCoinBal * get_current_price(selCoin) > 5000:
                    sell_result = upbit.sell_market_order(selCoin, getCoinBal*0.9995)
                    post_message(myToken,"#crypto", selCoin + "sell : " +str(sell_result))
                    krw = get_balance("KRW")/len(coin)
                    
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#crypto", e)
        time.sleep(1)
