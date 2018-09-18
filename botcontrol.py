import argparse
from datetime import datetime
import json
from random import randint
import requests
import sys
from time import sleep
import robobrowser





########Important Global Boogaloo#########
header = {
    'app_version': '3',
    'platform': 'ios',
    'User-agent': 'User-Agent: Tinder/3.0.4 (iPhone; iOS 7.1; Scale/2.00)',
    'content-type': 'application/json'
}

#username and password of our bot
username = ""
password = ""

#Important Robobrowser stuff
MOBILE_USER_AGENT = "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)"
FB_AUTH = "https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F&display=touch&state=%7B%22challenge%22%3A%22IUUkEUqIGud332lfu%252BMJhxL4Wlc%253D%22%2C%220_auth_logger_id%22%3A%2230F06532-A1B9-4B10-BB28-B29956C71AB1%22%2C%22com.facebook.sdk_client_state%22%3Atrue%2C%223_method%22%3A%22sfvc_auth%22%7D&scope=user_birthday%2Cuser_photos%2Cuser_education_history%2Cemail%2Cuser_relationship_details%2Cuser_friends%2Cuser_work_history%2Cuser_likes&response_type=token%2Csigned_request&default_audience=friends&return_scopes=true&auth_type=rerequest&client_id=464891386855067&ret=login&sdk=ios&logger_id=30F06532-A1B9-4B10-BB28-B29956C71AB1&ext=1470840777&hash=AeZqkIcf-NEW6vBd"

#name of the bot's tinder profile
pass_name = ""

#List of users liked by bot
user_list1 = []
user_list2 = []





#########Classes#########
class User(object):
    def __init__(self, data_dict):
        self.d = data_dict

    @property
    def user_id(self):
        return self.d['_id']

    @property
    def ago(self):
        raw = self.d.get('ping_time')
        if raw:
            d = datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S.%fZ')
            secs_ago = int(datetime.now().strftime("%s")) - int(d.strftime("%s"))
            if secs_ago > 86400:
                return u'{days} days ago'.format(days=secs_ago / 86400)
            elif secs_ago < 3600:
                return u'{mins} mins ago'.format(mins=secs_ago / 60)
            else:
                return u'{hours} hours ago'.format(hours=secs_ago / 3600)

        return '[unknown]'

    @property
    def bio(self):
        try:
            x = self.d['bio'].encode('ascii', 'ignore').replace('\n', '')[:50].strip()
        except (UnicodeError, UnicodeEncodeError, UnicodeDecodeError):
            return '[garbled]'
        else:
            return x

    @property
    def age(self):
        raw = self.d.get('birth_date')
        if raw:
            d = datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S.%fZ')
            return datetime.now().year - int(d.strftime('%Y'))

        return 0

    def __unicode__(self):
        return u'{name} ({age}), {distance}km, {ago}'.format(
            name=self.d['name'],
            age=self.age,
            distance=self.d['distance_mi'],
            ago=self.ago
			)

			
class Match(object):
	def __init__(self, data_dict):
		self.d = data_dict
	
	def user_id(self):
		return_str = self.d['_id']
		return return_str
	
	def __eq__(self, other):
		if self.d['_id'] == other.d['_id']:
			return True
		else:
			return False
			
	def messages(self):
		message_dict = self.d['messages']
		for m in message_dict:
			if m['_id'] == self.user_id():
				return_dict.append(m)
		return return_dict
	
	def last_sent_message(self):
		return self.messages[-1]['message']
		



#########Functions#########
def get_fb_access_token(email, password):
    s = robobrowser.RoboBrowser(user_agent=MOBILE_USER_AGENT, parser="lxml")
    s.open(FB_AUTH)
    f = s.get_form()
    f["pass"] = password
    f["email"] = email
    s.submit_form(f)
    f = s.get_form()
    try:
        s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])
        access_token = re.search(
            r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
        return access_token
    except Exception as ex:
        print("access token could not be retrieved. Check your username and password.")
        print("Official error: %s" % ex)
        return {"error": "access token could not be retrieved. Check your username and password."}


def get_fb_id(access_token):
    if "error" in access_token:
        return {"error": "access token could not be retrieved"}
    """Gets facebook ID from access token"""
    req = requests.get(
        'https://graph.facebook.com/me?access_token=' + access_token)
    return req.json()["id"]

	
#Authenticates because we have to
def auth_please(fb_token, fb_user_id):
	h = header
	h.update({'content-type': 'application/json'})
	req = requests.post('https://api.gotinder.com/auth', headers=h, data=json.dumps({'facebook_token': fb_token, 'facebook_id': fb_user_id}))
	
	#try:
	return req.json()
	#except:
	#	return None
	

#Main function, calls everything and gets people talking. 
#Function that checks messages and forwards from one user to another
def main():
	fb_token1 = get_fb_access_token(username, password)
	fb_user_id1 = get_fb_id(fb_token1)
	token = auth_please(fb_token1, fb_user_id1)
	
	print(token)

	#s = float(randint(200, 3000) / 1000)
	
	#userlike(token)
	#sleep(s)
	#user_lists_update(token)

	#save_everything()
	

#Adds new matches to user_lists, if a user is already in, checks for changes
#if any new messages pop up then sends message
#returns something
def user_lists_update(fb_token):
	h = header
	h.update({'X-Auth-Token': fb_token})
	
	m = requests.get('https://api.gotinder.com/updates', headers = h)
	
	return_list = []
	ind = 0
	
	if not 'matches' in m.json():
		return []
	
	for i in m.json()['matches']:
		mat = Match(i)
		
		if not ((mat in user_list1) or (mat in user_list2)):
			if len(user_list1) > len(user_list2):
				user_list2.append(mat)
			else:
				user_list1.append(mat)
		elif len(user_list1) == len(user_list2):
		
			if mat in user_list1:
				ind = user_list1.index(mat)
				
				if user_list1[ind].last_sent_message() != mat.last_sent_message():
					message_send(user_list2[ind].user_id, mat.last_sent_message(), fb_token)
					
				user_list1[ind] = mat
				
			else:
				ind = user_list2.index(mat)
				
				if user_list2[ind].last_sent_message() != mat.last_sent_message():
					message_send(user_list1[ind].user_id, mat.last_sent_message(), fb_token)
					
				user_list2[ind] = mat
	
	return return_list
	

#Function that actually sends a message from one user to another
def message_send(userid, message, fb_token):
	h = header
	h.update({'X-Auth-Token': fb_token})
	
	sent = requests.post('https://api.gotinder.com/user/matches/%s' % userid, headers = h, data=json.dumps({'message': message}))


#Function that likes users in recommended if they have the correct name
#and adds that user to the list of users on that bot
def userlike(fb_token):
	seconds = float(randint(250, 2500) / 1000)
	sleep(seconds)
	
	h = headers
	h.update({'X-Auth-Token': fb_token})
	
	reccy = get_recommendeds(fb_token)
	
	for rec in reccy:
		if rec.d['name'] == pass_name:
			requests.get('https://api.gotinder.com/like/%s' % user_id(rec), headers = h)
		else:
			requests.get('https://api.gotinder.com/pass/%s' % user_id(rec), headers = h)
	
	
#Returns a list of recommended users, needs the token you got from tinder	
def get_recommendeds(fb_token):
	h = headers
	h.update({'X-Auth-Token': fb_token})
	temp = requests.get('https://api.gotinder.com/user/recs', headers=h)
	
	return_list = []
	
	if temp.status_code == 401 or r.status_code == 504:
		raise Exception('Your auth token didnt work')
		print(temp.content)
	
	if not 'results' in temp.json():
		print(temp.json())
	
	for u in temp.json()['results']:
		return_list.append(User(u))
	
	return return_list

	
#Saves user_lists 1 and 2 to a bunch of files
def save_everything():
	file_name = ""
	for j in user_list1:
		file_name = j.user_id
		with open(file_name, 'w') as f:
			json.dump(j, f)
	
	for j in user_list2:
		file_name = j.user_id
		with open(file_name, 'w') as f:
			json.dump(j, f)


def print_recommendeds(fb_token):
	h = headers
	h.update({'': fb_token})

print("Hello")

main()