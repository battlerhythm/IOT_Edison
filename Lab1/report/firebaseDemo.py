from firebase import firebase
import json as simplejson
firebase = firebase.FirebaseApplication('https://<YOUR_DOMAIN>.firebaseio.com',None)
result  = firebase.get('',None)
print result
 
name = {'Edison':10}
#data = simplejson.dumps(name)
  
post = firebase.post('',name)
   
print post
