

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
    "Cookie": r""
}
connect = pymysql.Connect(
	host='',
	port=3306,
	user='',
	passwd='',
	db='',
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
