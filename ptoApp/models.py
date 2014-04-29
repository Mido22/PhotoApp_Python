import shlex, subprocess
from pyDj.settings import STATIC_ROOT,MEDIA_ROOT
import random
import os
import zipfile

class Album(object):
    def __init__(self,path='/Camera Uploads',name='Unorganized',count=0):
        self.path=path
        self.name=name
        self.count=count
        self.disp_with_count=self.fun_disp_with_count

    @property
    def fun_disp_with_count(self):
        return str(self.name+'('+str(self.count)+')')

    def __str__(self):
        return self.path+','+str(self.count)+','+self.name

class DropboxObj(object):

    def __init__(self, sess,cli):
        self.cli=cli
        self.sess=sess
        self.path=self.sess.current_path

    def ls(self):
        flist=[]
        if 'contents' in self.cli.metadata(self.path):
            for f in self.cli.metadata(self.path)['contents']:
                flist.append(os.path.basename(f['path']))
        return flist

    def ls_folders(self):
        flist=[]
        if 'contents' in self.cli.metadata(self.path):
            for f in self.cli.metadata(self.path)['contents']:
                if f['is_dir']:
                    flist.append(os.path.basename(f['path']))
        return flist

    def ls_files(self):
        flist=[]
        if 'contents' in self.cli.metadata(self.path):
            for f in self.cli.metadata(self.path)['contents']:
                if not f['is_dir']:
                    flist.append(os.path.basename(f['path']))
        return flist

    def fileCount(self):
        count=0
        if 'contents' in self.cli.metadata(self.path):
            for f in self.cli.metadata(self.path)['contents']:
                if not f['is_dir']:
                    count+=1
        return count

    def cd(self, path):
        if path == "..":
            self.path = "/".join(self.path.split("/")[0:-1])
        else:
            self.path += "/" + path

    def rm(self, path):
        self.cli.file_delete(self.path + "/" + path)

    def mkdir(self, path):
        self.cli.file_create_folder(self.path + "/" + path)

    def create_album(self, path):
        alb_path='/Photos/' + path
        for f in self.cli.metadata('/Photos/')['contents']:
            if f['path']==alb_path:
                alb_path+='_'+str(random.randint(1,999))
        self.cli.file_create_folder(alb_path)

    def mv(self, from_path, to_path):
        """move/rename a file or directory"""
        self.cli.file_move(self.path + "/" + from_path, self.path + "/" + to_path)

    def mv_abs(self, from_path, to_path):
        self.cli.file_move( from_path, to_path)

    def move_Album(self, from_path, to_path):
        self.cli.file_move( '/Photos/'+from_path, '/Photos/'+to_path)

    def download(self, from_path, to_path):
        """        Dropbox> get file.txt ~/dropbox-file.txt        """
        to_file = open(os.path.expanduser(to_path), "wb")
        f,metadata = self.cli.get_file_and_metadata(self.path + "/" + from_path)
        to_file.write(f.read())

    def download_abs(self, from_path, to_path):
        to_file = open(to_path, "wb")
        f,metadata = self.cli.get_file_and_metadata(from_path)
        to_file.write(f.read())

    def loadImage(self, from_path, to_path):
        to_file = open(os.path.expanduser(to_path), "wb")

        f,metadata = self.cli.get_file_and_metadata(from_path)
        to_file.write(f.read())

    def thumbnails(self, from_path, to_path, size='large', format='PNG'):
        """        Dropbox> thumbnail file.txt ~/dropbox-file.txt medium PNG        """
        to_path+='.png'
        to_file = open(os.path.expanduser(to_path), "wb")
        f,metadata = self.cli.thumbnail_and_metadata(self.path + "/" + from_path, size, format)
        to_file.write(f.read())

    def upload(self, from_path, to_path):
        """        Dropbox> put ~/test.txt dropbox-copy-test.txt        """
        from_file = open(os.path.expanduser(from_path), "rb")
        self.cli.put_file(self.path + "/" + to_path, from_file)

    def delete_album(self,album):
        self.path='/Photos/'+album
        for i in self.ls():
            self.mv_abs(self.path+"/"+i,"/Camera Uploads/"+i)
        path=self.path.split("/")[-1]
        self.path = "/".join(self.path.split("/")[0:-1])
        self.rm(path)

    def deletePhotos(self,data):
        for photo in data.split('||'):
            self.cli.file_delete(photo)

    def movePhotos(self,data,album):
        if album=='Unorganized':
            to_path='/Camera Uploads/'
        else:
            to_path='/Photos/'+album+'/'
        for photo in data.split('||'):
            self.cli.file_move(photo,to_path+os.path.split(photo)[1])

class User(object):
    def __init__(self,name):
        self.name=name
        self.path= MEDIA_ROOT+'/users/'+name
        self.url_path='users/'+name
        self.thumb_path =self.path+'/thumbs'
        self.ops_path =self.path+'/ops'
        self.zip_location=self.path+'/'+'download.zip'
        self.zip_url_path=self.url_path+'/download.zip'
        self.collage_path=self.url_path+'/ops/collage.jpg'
        if not os.path.exists(self.thumb_path): os.makedirs(self.thumb_path)
        if not os.path.exists(self.ops_path): os.makedirs(self.ops_path)

    def make_thumbs(self,path,sessionObj):
        for the_file in os.listdir(self.thumb_path): os.unlink(os.path.join(self.thumb_path, the_file)) #for deleting all files in the folder
        sessionObj.path=path
        thumbs=[]
        for pic in sessionObj.ls_files():
            sessionObj.thumbnails(pic,self.thumb_path+'/'+pic)
            thumbs.append(thumb(path+'/'+pic,self.thumb_path+'/'+pic))
        return thumbs

    def downloadPhotos(self,data,sess):
        for the_file in os.listdir(self.ops_path): os.unlink(os.path.join(self.ops_path, the_file))
        zip=zipfile.ZipFile(self.zip_location,'w')
        for photo in data.split('||'):
            sess.download_abs(photo,self.ops_path+'/'+os.path.split(photo)[1])
            zip.write(self.ops_path+'/'+os.path.split(photo)[1],os.path.split(photo)[1])
        zip.close()

    def makeCollage(self,data,sess):
        for the_file in os.listdir(self.ops_path): os.unlink(os.path.join(self.ops_path, the_file))
        for photo in data.split('||'):
            sess.download_abs(photo,self.ops_path+'/'+os.path.split(photo)[1])
        #os.system('cd "'+self.ops_path+'"')
        #os.curdir=self.ops_path
        #subprocess.Popen('cd',self.ops_path,shell=True)
        os.chdir(self.ops_path)
        #print os.getcwd()
        command_line = ['montage', "*.jpg", '-border', '2x2', '-resize', '50%', '+polaroid', '-background', 'LightGray', '-geometry', '+5+5', "collage.jpg"]
        argos = " ".join(command_line)
        args = shlex.split(argos)
        subprocess.Popen(args)
        #os.system('mv collage.jpg ../showImage.jpg')
        #if not 'Collages' in sess.ls_folders() :
        #    sess.cli.file_create_folder('/Photos/Collages')
        #from_file = open(self.ops_path+'/collage.jpg', 'rb')
        #sess.path='/Photos/Collages'
        #self.cli.put_file(sess.path+'/Collage'+ sess.fileCount+'.jpg', from_file)


class thumb(object):
    def __init__(self,name,path):
        self.name=name
        self.path=path
        self.rel_path=self.path.strip(STATIC_ROOT)+'.png'

    def __str__(self):
        return self.path+','+self.name









