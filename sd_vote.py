import webapp2
import jinja2
import os
import json
import re
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_VOTE_NAME = 'personal_vote'
DEFAULT_GROUPVOTE_NAME = 'group_vote'

# context={'defaultvalues': []}
# context['defaultvalues'].append({'provider'})
# context['defaultvalues'].append({'provider'})
# list1 = [{"username": "abhi", "pass": 2087}]
# odds = [1, 3, 5, 7]

# defaultvalues = {'one':'Curie', 'two':'Darwing','three':'Turing'}



# class listofvalues(webapp2.RequestHandler):
#     def get(self):
#         self.response.headers['Content-Type'] = 'text/plain'
#         self.response.write(defaultvalues[0])
        # self.response.write(context['idp'][5])

class Account(ndb.Model):
    username = ndb.StringProperty()
    userid = ndb.IntegerProperty()
    email = ndb.StringProperty()

def votebook_key(votebook_name=DEFAULT_VOTE_NAME):
    # use votebook_name as key for Guestbook entities
    return ndb.Key('Votebook', votebook_name)

# [START votes]
class Client(ndb.Model):
    """Sub model for representing an client."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)

class Vote(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    client = ndb.StructuredProperty(Client)
    values = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END votes]

def groupvote_key(groupvote_name=DEFAULT_GROUPVOTE_NAME):
    # use votebook_name as key for Guestbook entities
    return ndb.Key('Groupvote', groupvote_name)

# [START groupvote]

class Groupvalue(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    value = ndb.StringProperty()
    rank = ndb.IntegerProperty(default=1)
    username = ndb.StringProperty()
    @classmethod
    def make_key(cls, isbn):
        return ndb.Key(cls, isbn)

class LoxonValues(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    value = ndb.StringProperty()
    score = ndb.StringProperty()
    rank = ndb.IntegerProperty(default=1)
    username = ndb.StringProperty()
    group = ndb.StringProperty(default='notingroup')
    date = ndb.DateTimeProperty(auto_now_add=True)
    @classmethod
    def make_key(cls, isbn):
        return ndb.Key(cls, isbn)

class LoxonValueshistory(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    value = ndb.StringProperty()
    score = ndb.StringProperty()
    username = ndb.StringProperty()
    group = ndb.StringProperty(default='notingroup')
    date = ndb.DateTimeProperty(auto_now_add=True)


class LoxonGroup(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    user = ndb.StringProperty()
    group = ndb.StringProperty(default='notingroup')

class Groupvote(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    groupvalue = ndb.StructuredProperty(Groupvalue)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END groupvote]


class Votebook(webapp2.RequestHandler):
# [START guestbook entity fill in]

    def post(self):
        # We set the same parent key on the 'Vote' to ensure each
        # Vote is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        votebook_name = self.request.get('votebook_name',
                                          DEFAULT_VOTE_NAME)
        votes = Vote(parent=votebook_key(votebook_name))

        if users.get_current_user():
            votes.client = Client(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        votes.values = self.request.get('values')
        votes.put()

        query_params = {'votebook_name': votebook_name}
        self.redirect('/?' + urllib.urlencode(query_params))
# [END guestbook entity fill in]



class MainPage(webapp2.RequestHandler):
# [STATRT main page servie that includes handling POST requests]

    def get(self):

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'LOGOUT'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'LOGIN'

        # groupvalue_keycheck = ndb.Key(Groupvalue.username=='group').get()


                # if groupvalue_keycheck:

        groupvalue = Groupvalue.query(Groupvalue.username == 'group')

        if groupvalue.count(1):

            q2 = Groupvalue.query(Groupvalue.username == 'group')
            q3 = q2.order(- Groupvalue.rank)
            qlist_group = q3.fetch(6)

            kpi = 0

            for item in qlist_group:
                kpi += item.rank

            kpimax = qlist_group[0].rank
            kpilength = len(qlist_group)

            kpi = 100 * kpi / kpimax / kpilength
        else:
            kpi = 0

        kpi = [10,20]

        groupassigned = 0
        groupname = 'notingroup'

        if url_linktext == 'LOGOUT':

            qgroup = LoxonGroup.query(LoxonGroup.user == user.email())
            usergroup = qgroup.fetch(1)
            if qgroup.count(1):
            	groupname = usergroup[0].group
                if groupname == 'notingroup':
                    groupassigned = 0
                else:
                    groupassigned = 1

        q5 = LoxonValues.query(LoxonValues.value == 'Delivering value')
        qlist_one = q5.fetch(20)

        q6 = LoxonValues.query(LoxonValues.value == 'Easy to release')
        qlist_two = q6.fetch(20)

        q7 = LoxonValues.query(LoxonValues.value == 'Fun')
        qlist_three = q7.fetch(20)

        q8 = LoxonValues.query(LoxonValues.value == 'Health of codebase')
        qlist_four = q8.fetch(20)

        q9 = LoxonValues.query(LoxonValues.value == 'Teamwork')
        qlist_five = q9.fetch(20)

        numscore_disaster = 0
        numscore_meh = 0
        numscore_helpful = 0

        for one in qlist_one:
            if one.group == groupname:
                if one.score == 'disaster':
                    numscore_disaster = numscore_disaster +1
                if one.score == 'meh':
                    numscore_meh = numscore_meh +1
                if one.score == 'helpful':
                    numscore_helpful = numscore_helpful +1
        kpi_one = [numscore_disaster,numscore_meh, numscore_helpful]

        numscore_disaster = 0
        numscore_meh = 0
        numscore_helpful = 0

        for one in qlist_two:
            if one.group == groupname:
                if one.score == 'disaster':
                    numscore_disaster = numscore_disaster +1
                if one.score == 'meh':
                    numscore_meh = numscore_meh +1
                if one.score == 'helpful':
                    numscore_helpful = numscore_helpful +1

        kpi_two = [numscore_disaster,numscore_meh, numscore_helpful]

        numscore_disaster = 0
        numscore_meh = 0
        numscore_helpful = 0

        for one in qlist_three:
            if one.group == groupname:
                if one.score == 'disaster':
                    numscore_disaster = numscore_disaster +1
                if one.score == 'meh':
                    numscore_meh = numscore_meh +1
                if one.score == 'helpful':
                    numscore_helpful = numscore_helpful +1

        kpi_three = [numscore_disaster,numscore_meh, numscore_helpful]

        numscore_disaster = 0
        numscore_meh = 0
        numscore_helpful = 0

        for one in qlist_four:
            if one.group == groupname:
                if one.score == 'disaster':
                    numscore_disaster = numscore_disaster +1
                if one.score == 'meh':
                    numscore_meh = numscore_meh +1
                if one.score == 'helpful':
                    numscore_helpful = numscore_helpful +1

        kpi_four = [numscore_disaster,numscore_meh, numscore_helpful]

        numscore_disaster = 0
        numscore_meh = 0
        numscore_helpful = 0

        for one in qlist_five:
            if one.group == groupname:
                if one.score == 'disaster':
                    numscore_disaster = numscore_disaster +1
                if one.score == 'meh':
                    numscore_meh = numscore_meh +1
                if one.score == 'helpful':
                    numscore_helpful = numscore_helpful +1

        kpi_five = [numscore_disaster,numscore_meh, numscore_helpful]

        template_values = {
            'user': user,
            'url': url,
            'groupassigned' : groupassigned,
            'groupname' : groupname,
            'url_linktext': url_linktext,
            'motivation_one': kpi_one,
            'motivation_two': kpi_two,
            'motivation_three': kpi_three,
            'motivation_four': kpi_four,
            'motivation_five': kpi_five,

        }


        template = JINJA_ENVIRONMENT.get_template('sd.html')
        self.response.write(template.render(template_values))


    def post(self):

        # entries = Groupvalues.query(Groupvalues.rank==0).fetch(1000,keys_only=True)
        # ndb.delete(entries)


        user = users.get_current_user().email()
        data = json.loads(self.request.body)
        select = data["name"]
        selectmeasure = data["measure"]
        measure = data["type"]
        vote_list = select.split(';')
        measure_list = selectmeasure.split(';')
        # value = select.split(';')

        i = 0

        qgroup = LoxonGroup.query(LoxonGroup.user == user)
        usergroup = qgroup.get()

        for value in vote_list:


            # groupvalue_key = Groupvalue.query(Groupvalue.value == vote_list[0]).fetch(1,keys_only=True)
            # if groupvalue_key[0]:
            #     groupvalue = groupvalue_key[0].get()
            #     groupvalue.rank = groupvalue.rank + 1
            # groupvalue.put()
            id_actual = value + user

            groupvalue = LoxonValues(id=id_actual)
            groupvalue.username = user
            groupvalue.score = measure_list[i]
            groupvalue.value = value
            groupvalue.group = usergroup.group
            groupvalue.rank = len(vote_list)
            groupvalue.put()

            groupvaluehist = LoxonValueshistory(
            username = user,
            score = measure_list[i],
            value = value,
            group = usergroup.group)
            groupvaluehist.put()


            i = i + 1





                #     groupvalue_key = Groupvalue.make_key(value)
                #     groupvalue = groupvalue_key.get()
                #     groupvalue.username = 'group'
                #     groupvalue.value = value
                #     groupvalue.put()



        # for value_selected in x:
        #     if value_selected:
        #         p = Groupvalues(value = value_selected, rank = 0)
        #         p.put()


        self.response.write(json.dumps({"message": 'your vote is stored'}))
 # [END main page servie that includes handling POST requests]

class Trend(webapp2.RequestHandler):
# [STATRT main page servie that includes handling POST requests]

    def get(self):

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'LOGOUT'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'LOGIN'

        # groupvalue_keycheck = ndb.Key(Groupvalue.username=='group').get()


                # if groupvalue_keycheck:

        groupvalue = Groupvalue.query(Groupvalue.username == 'group')

        if groupvalue.count(1):

            q2 = Groupvalue.query(Groupvalue.username == 'group')
            q3 = q2.order(- Groupvalue.rank)
            qlist_group = q3.fetch(6)

            kpi = 0

            for item in qlist_group:
                kpi += item.rank

            kpimax = qlist_group[0].rank
            kpilength = len(qlist_group)

            kpi = 100 * kpi / kpimax / kpilength
        else:
            kpi = 0

        kpi = [10,20]

        groupassigned = 0
        groupname = 'notingroup'

        if url_linktext == 'LOGOUT':

            qgroup = LoxonGroup.query(LoxonGroup.user == user.email())
            usergroup = qgroup.fetch(1)
            if qgroup.count(1):
                groupname = usergroup[0].group
                if groupname == 'notingroup':
                    groupassigned = 0
                else:
                    groupassigned = 1

        q5 = LoxonValues.query(LoxonValues.value == 'Delivering value')
        qlist_one = q5.fetch(20)

        q6 = LoxonValues.query(LoxonValues.value == 'Easy to release')
        qlist_two = q6.fetch(20)

        q7 = LoxonValues.query(LoxonValues.value == 'Fun')
        qlist_three = q7.fetch(20)

        q8 = LoxonValues.query(LoxonValues.value == 'Health of codebase')
        qlist_four = q8.fetch(20)

        q9 = LoxonValues.query(LoxonValues.value == 'Teamwork')
        qlist_five = q9.fetch(20)

        numscore_disaster = 0
        numscore_meh = 0
        numscore_helpful = 0

        for one in qlist_one:
            if one.group == groupname:
                if one.score == 'disaster':
                    numscore_disaster = numscore_disaster +1
                if one.score == 'meh':
                    numscore_meh = numscore_meh +1
                if one.score == 'helpful':
                    numscore_helpful = numscore_helpful +1
        kpi_one = [numscore_disaster,numscore_meh, numscore_helpful]

        numscore_disaster = 0
        numscore_meh = 0
        numscore_helpful = 0

        for one in qlist_two:
            if one.group == groupname:
                if one.score == 'disaster':
                    numscore_disaster = numscore_disaster +1
                if one.score == 'meh':
                    numscore_meh = numscore_meh +1
                if one.score == 'helpful':
                    numscore_helpful = numscore_helpful +1

        kpi_two = [numscore_disaster,numscore_meh, numscore_helpful]

        numscore_disaster = 0
        numscore_meh = 0
        numscore_helpful = 0

        for one in qlist_three:
            if one.group == groupname:
                if one.score == 'disaster':
                    numscore_disaster = numscore_disaster +1
                if one.score == 'meh':
                    numscore_meh = numscore_meh +1
                if one.score == 'helpful':
                    numscore_helpful = numscore_helpful +1

        kpi_three = [numscore_disaster,numscore_meh, numscore_helpful]

        numscore_disaster = 0
        numscore_meh = 0
        numscore_helpful = 0

        for one in qlist_four:
            if one.group == groupname:
                if one.score == 'disaster':
                    numscore_disaster = numscore_disaster +1
                if one.score == 'meh':
                    numscore_meh = numscore_meh +1
                if one.score == 'helpful':
                    numscore_helpful = numscore_helpful +1

        kpi_four = [numscore_disaster,numscore_meh, numscore_helpful]

        numscore_disaster = 0
        numscore_meh = 0
        numscore_helpful = 0

        for one in qlist_five:
            if one.group == groupname:
                if one.score == 'disaster':
                    numscore_disaster = numscore_disaster +1
                if one.score == 'meh':
                    numscore_meh = numscore_meh +1
                if one.score == 'helpful':
                    numscore_helpful = numscore_helpful +1

        kpi_five = [numscore_disaster,numscore_meh, numscore_helpful]

        template_values = {
            'user': user,
            'url': url,
            'groupassigned' : groupassigned,
            'groupname' : groupname,
            'url_linktext': url_linktext,
            'motivation_one': kpi_one,
            'motivation_two': kpi_two,
            'motivation_three': kpi_three,
            'motivation_four': kpi_four,
            'motivation_five': kpi_five,

        }


        template = JINJA_ENVIRONMENT.get_template('trend.html')
        self.response.write(template.render(template_values))


    def post(self):

        # entries = Groupvalues.query(Groupvalues.rank==0).fetch(1000,keys_only=True)
        # ndb.delete(entries)


        user = users.get_current_user().email()
        data = json.loads(self.request.body)
        select = data["name"]
        selectmeasure = data["measure"]
        measure = data["type"]
        vote_list = select.split(';')
        measure_list = selectmeasure.split(';')
        # value = select.split(';')

        i = 0

        qgroup = LoxonGroup.query(LoxonGroup.user == user)
        usergroup = qgroup.get()

        for value in vote_list:


            # groupvalue_key = Groupvalue.query(Groupvalue.value == vote_list[0]).fetch(1,keys_only=True)
            # if groupvalue_key[0]:
            #     groupvalue = groupvalue_key[0].get()
            #     groupvalue.rank = groupvalue.rank + 1
            # groupvalue.put()
            id_actual = value + user

            groupvalue = LoxonValues(id=id_actual)
            groupvalue.username = user
            groupvalue.score = measure_list[i]
            groupvalue.value = value
            groupvalue.group = usergroup.group
            groupvalue.rank = len(vote_list)
            groupvalue.put()

            groupvaluehist = LoxonValueshistory(
            username = user,
            score = measure_list[i],
            value = value,
            group = usergroup.group)
            groupvaluehist.put()


            i = i + 1





                #     groupvalue_key = Groupvalue.make_key(value)
                #     groupvalue = groupvalue_key.get()
                #     groupvalue.username = 'group'
                #     groupvalue.value = value
                #     groupvalue.put()



        # for value_selected in x:
        #     if value_selected:
        #         p = Groupvalues(value = value_selected, rank = 0)
        #         p.put()


        self.response.write(json.dumps({"message": 'your vote is stored'}))
 # [END main page servie that includes handling POST requests]



class AllSubPages(webapp2.RequestHandler):
  def get(self, html_page):
 # [STATRT sub page servies, take over path from originating URI (re group which is put in brackets)]

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'LOGOUT'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'LOGIN'


        q1 = Groupvalue.query(Groupvalue.username == user.email())
        qlist = q1.fetch()


        q2 = Groupvalue.query(Groupvalue.username == 'group')

        q3 = q2.order(- Groupvalue.rank)
        qlist_group = q3.fetch(6)
        qlist_group2 = q3.fetch(10)

        if not qlist:
            qlist = qlist_group2

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'defaultvalue_list': qlist,
            'defaultvalue_list_group': qlist_group,
        }


        template = JINJA_ENVIRONMENT.get_template('%s' % html_page)
        self.response.write(template.render(template_values))
# [STATRT sub page servies]


class Groupname(webapp2.RequestHandler):
# [STATRT main page servie that includes handling POST requests]
    def get(self):




        # i = 0

        # for value in vote_list:

        #     id_actual = value + user

        #     groupvalue = LoxonValues(id=id_actual)
        #     groupvalue.username = user
        #     groupvalue.score = measure_list[i]
        #     groupvalue.value = value
        #     groupvalue.rank = len(vote_list)
        #     groupvalue.put()
        #     i = i + 1

        self.response.write("hello")


    def post(self):


        data = json.loads(self.request.body)
        user = users.get_current_user().email()
        groupname = data["groupname"]


        useringroup = LoxonGroup(id=user)
        useringroup.group = groupname
        useringroup.user = user


        useringroup.put()


        qgroup = LoxonValues.query(LoxonValues.username == user)
        usergroup = qgroup.fetch(10)



        for i in range(0,len(usergroup)):

            usergroup[i].group = groupname
            usergroup[i].put()





        # i = 0

        # for value in vote_list:

        #     id_actual = value + user

        #     groupvalue = LoxonValues(id=id_actual)
        #     groupvalue.username = user
        #     groupvalue.score = measure_list[i]
        #     groupvalue.value = value
        #     groupvalue.rank = len(vote_list)
        #     groupvalue.put()
        #     i = i + 1

        self.response.write(json.dumps({"message": "Sikeres! Group Name = " + groupname}))

 # [END main page


app = webapp2.WSGIApplication(
    [('/', MainPage),
    ('/groupname', Groupname),
    ('/trend.html', Trend),
    ('/(\w+\.html)', AllSubPages),
    ],
    debug=True)
