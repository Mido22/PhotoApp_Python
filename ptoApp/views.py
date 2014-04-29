import random
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.template.loader import render_to_string
from dropbox import client, rest, session
import os
from models import Album,DropboxObj,User
from pyDj.settings import APP_KEY,APP_SECRET,ACCESS_TYPE,MEDIA_URL,STATIC_URL
import json

def leftSideBar(request):
    sessObj = request.session['sessObj']
    sess=sessObj.sess
    cli=sessObj.cli
    #cli=request.session['client']
    sess.current_path='/Photos'
    albums=[Album(count=getCount(sess,cli))]
    album_dict={'Unorganized':Album(count=getCount(sess,cli))}
    if 'contents' in cli.metadata(sess.current_path):
        for f in cli.metadata(sess.current_path)['contents']:
            if f['is_dir']:
                albums.append(Album(name=os.path.basename(f['path']),path=f['path'],count=getCount(sess,cli,f['path'])))
                album_dict[os.path.basename(f['path'])]=Album(name=os.path.basename(f['path']),path=f['path'],count=getCount(sess,cli,f['path']))
    request.session['albums']=album_dict
    out = render_to_string('leftSideBar.html', {'items': albums})
    respond={'innerHTML':out}
    return HttpResponse(json.dumps(respond), content_type="application/json")

def goToHomePage(request):
    if 'LoggedIn' in request.session:
        if request.session['LoggedIn']==True:
            response=homepg(request)
        else:
            response=goToLogin(request)
    else:
        response=goToLogin(request)
    return response

def goToLogin(request):
    sess=session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
    request_token = sess.obtain_request_token()
    request.session['token']=request_token
    request.session['sess']=sess
    request.session['LoggedIn']=False
    url = sess.build_authorize_url(request_token,oauth_callback='http://127.0.0.1:8000/homepage/')
    t=get_template('goToLogin.html')
    html=t.render(Context({'url':url,'MEDIA_URL':MEDIA_URL}))
    return HttpResponse(html)

def homepg(request):
    request_token = request.session['token']
    sess = request.session['sess']
    sess.current_path='/Photos'
    request.session['current_album']='Unorganized'
    cli = client.DropboxClient(sess)
    request.session['client']=cli
    if request.session['LoggedIn']==False:
        sess.obtain_access_token(request_token)
        request.session['LoggedIn']=True
    request.session['user']=User(cli.account_info()['display_name'])
    request.session['sessObj']=DropboxObj(sess,cli)
    t=get_template('homePage.html')
    html=t.render(Context({'MEDIA_URL':MEDIA_URL,'user':cli.account_info()['display_name']}))
    return HttpResponse(html)

def loadAlbum(request):
    if 'data' not in request.GET:
        request.session['current_album']=request.GET['album']
    album=request.session['albums'][request.session['current_album']]
    user=request.session['user']
    thumbs=user.make_thumbs(album.path,request.session['sessObj'])
    thumbs2=[]
    t_temp=[]
    count=0
    for t in thumbs:
        if count<4:
            t_temp.append(t)
            count+=1
        else:
            thumbs2.append(t_temp)
            t_temp=[t]
            count=1
    thumbs2.append(t_temp)
    out = render_to_string('mainPage.html', {'album': album,'thumbs':thumbs2,'MEDIA_URL':MEDIA_URL})
    ckBoxes=[]
    for t in thumbs: ckBoxes.append(t.name)
    respond={'innerHTML':out,'ckBoxes':ckBoxes}
    return HttpResponse(json.dumps(respond), content_type="application/json")

def createAlbum(request):
    album_name=request.GET['album']
    request.session['sessObj'].create_album(album_name)
    respond={'innerHTML':album_name}
    return HttpResponse(json.dumps(respond), content_type="application/json")

def renameAlbum(request):
    oldName=request.GET['album']
    newName=request.GET['newName']
    request.session['sessObj'].move_Album(oldName,newName)
    respond={'innerHTML':newName}
    return HttpResponse(json.dumps(respond), content_type="application/json")

def deleteAlbum(request):
    album_name=request.GET['album']
    request.session['sessObj'].delete_album(album_name)
    respond={'innerHTML':"The Album Has been deleted. All it's photos have been moved to Unorganized"}
    return HttpResponse(json.dumps(respond), content_type="application/json")

def loadImage(request):
    user=request.session['user']
    if 'image' in request.session:
        if os.path.exists(user.path+request.session['image']): os.unlink(user.path+request.session['image'])
        request.session['image']='/showImage'+'_'+str(random.randint(1,999))+os.path.splitext(request.GET['image'])[1]
    else:
        request.session['image']='/showImage.jpg'

    request.session['sessObj'].loadImage(request.GET['image'],user.path+request.session['image'])
    out = render_to_string('image.html', {'user': user,'MEDIA_URL':MEDIA_URL,'image':request.session['image']})
    respond={'innerHTML':out}
    return HttpResponse(json.dumps(respond), content_type="application/json")

def deletePhotos(request):
    request.session['sessObj'].deletePhotos(request.GET['data'])
    return loadAlbum(request)

def movePhotos(request):
    request.session['sessObj'].movePhotos(request.GET['data'],request.GET['album'])
    return loadAlbum(request)

def downloadPhotos(request):
    user=request.session['user']
    user.downloadPhotos(request.GET['data'],request.session['sessObj'])
    respond={'path':MEDIA_URL+user.zip_url_path}
    return HttpResponse(json.dumps(respond), content_type="application/json")

def logout(request):
    request.session.clear()
    out = "<h1><a href=\"http://127.0.0.1:8000/loginPage/\">Click here</a> to go to Login Page </h1>"
    respond={'innerHTML':out}
    return HttpResponse(json.dumps(respond), content_type="application/json")

def makeCollage(request):
    user=request.session['user']
    user.makeCollage(request.GET['data'],request.session['sessObj'])
    out = render_to_string('image.html', {'user': user,'MEDIA_URL':MEDIA_URL,'image':'/ops/collage.jpg'})
    respond={'innerHTML':out,'path':MEDIA_URL+user.collage_path}
    return HttpResponse(json.dumps(respond), content_type="application/json")

def getCount(sess,cli,path='/Camera Uploads'):
    path,sess.current_path=sess.current_path,path
    resp = cli.metadata(sess.current_path)
    count=0
    if 'contents' in resp:
        for f in resp['contents']:
            if not f['is_dir']:
                count+=1
    path,sess.current_path=sess.current_path,path
    return count

