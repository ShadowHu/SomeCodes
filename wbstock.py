

import requests
import pymysql.cursors
import time

URL = 'https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&containerid=230677sz002405'
SQL = '''INSERT INTO weibotemp180110 (ir_sid, ir_authors, ir_urltime, ir_urldate, ir_content, ir_urlname, ir_nresrved1, ir_nresrved2, ir_nresrved3, ir_istrash, ir_mediatype, ir_mediasource, ir_url, ir_title, ir_des, ir_comment, ir_readnum, ir_md5) VALUE("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'''
headers = {
	"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.8",
    "Connection":"keep-alive",
    "Host":"m.weibo.cn",
    # "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
    "Cookie": r"_T_WM=9595e39b4b48c791dbab490fad8f560b; H5_wentry=H5; backURL=https%3A%2F%2Flogin.sina.com.cn%2Fsso%2Flogin.php%3Furl%3Dhttps%3A%2F%2Fm.weibo.cn%2F%3F%26jumpfrom%3Dweibocom%26_rand%3D1515518129.4732%26gateway%3D1%26service%3Dsinawap%26entry%3Dsinawap%26useticket%3D1%26returntype%3DMETA%26sudaref%3D%26_client_version%3D0.6.26; ALF=1518110806; SCF=AvxhgwjbHCH9_EwysmlyQAnVljnzMQ49NFd-9mYsHlI1ygrqhGgkDWbO9rZOngQfIzpRbFZF3FrMMzstnHMix0E.; SUB=_2A253UIsyDeRhGeBN7lAU9yjKyDyIHXVUuhV6rDV6PUJbktANLW7RkW1NRHZkh2JizVXgZ_FT4iR-oxYSp0i6wWr5; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhfSWzUpOELveW-froZ.UJa5JpX5K-hUgL.Foq0SKzfS0qce052dJLoIpMLxKML1hqL1K.LxKML1hqL1KLkSc8uS7tt; SUHB=0FQrk72iRm-0cH; SSOLoginState=1515518818; WEIBOCN_FROM=1110006030; M_WEIBOCN_PARAMS=fid%3D1005056352576630%252Fhome%26uicode%3D10000011"
}
connect = pymysql.Connect(
	host='140.210.4.68',
	port=3306,
	user='fulua',
	passwd='fuluabc!@#',
	db='abroadsystem',
	charset='utf8mb4'
)
cursor = connect.cursor()



for p in range(1, 101):
	url = URL + '&page=' + str(p)
	req = requests.get(url, headers=headers)
	js = req.json()
	index = 3 if p == 1 else 0
	print(url)
	for w in js['data']['cards'][index]['card_group']:
		ir_sid = w['itemid']
		ir_md5 = w['mblog']['bid']
		ir_nresrved2 = w['mblog']['comments_count']
		ir_nresrved3 = w['mblog']['attitudes_count'] # up num
		ir_nresrved1 = w['mblog']['reposts_count']
		ir_readnum = w['mblog']['reads_count']
		urltime = w['mblog']['created_at']
		print(urltime[-3:])
		if urltime[-3:] == '分钟前':
			ir_urltime = int(time.time()) - int(urltime[:-3])*60
		elif urltime[-3:] == '小时前':
			ir_urltime = int(time.time()) - int(urltime[:-3])*3600
		elif urltime[:2] == '20':
			ir_urltime = time.mktime(time.strptime(urltime, '%Y-%m-%d'))
		else:
			urltime = '01-09' if urltime[:2] == '昨天' else urltime
			ir_urltime = time.mktime(time.strptime('2018-'+urltime, '%Y-%m-%d'))
		try:
			ir_content = w['mblog']['raw_text']
		except KeyError:
			ir_content = w['mblog']['text']
		print(ir_content)
		ir_url = w['scheme']
		ir_authors = w['mblog']['user']['screen_name']
		ir_istrash = w['mblog']['user']['followers_count']
		ir_des = w['mblog']['user']['description']
		ir_urlname = w['mblog']['user']['profile_url']
		rawcomments = ''
		try:
			for x in w['mblog']['comment_summary']['comment_list']:
				rawcomments = rawcomments + '$$$' + x['user']['screen_name'] + '-_-!'  + \
				 x['text'] + '' + x['created_at']
		except KeyError:
			pass
		ir_comment = rawcomments
		sql = SQL.format(ir_sid, ir_authors, ir_urltime, int(time.time()), connect.escape(ir_content), ir_urlname, ir_nresrved1, ir_nresrved2, ir_nresrved3, ir_istrash, 5, 'weibo.com', ir_url, connect.escape(ir_content[:100]), connect.escape(ir_des), connect.escape(ir_comment), ir_readnum, ir_md5)
		try:
			cursor.execute(sql)
		except pymysql.err.IntegrityError:
			pass
		except Exception as e:
			print(sql)
			raise e
	connect.commit()

cursor.close()
connect.close()