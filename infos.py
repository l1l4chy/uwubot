from pyobigram.utils import sizeof_fmt,nice_time
import datetime
import time
import os

def text_progres(index,max):
	try:
		if max<1:
			max += 1
		porcent = index / max
		porcent *= 100
		porcent = round(porcent)
		make_text = ''
		index_make = 1
		make_text += '├'
		while(index_make<21):
			if porcent >= index_make * 5: make_text+= '▣'
			else: make_text+= '▢'
			index_make+=1
		make_text += ''
		return make_text
	except Exception as ex:
			return ''

def porcent(index,max):
    porcent = index / max
    porcent *= 100
    porcent = round(porcent)
    return porcent

def createDownloading(filename,totalBits,currentBits,speed,time,tid=''):
    msg = '╭───ⓘ Downloading: '+str(porcent(currentBits,totalBits))+'%\n'
    msg += '├File name: '+filename+'\n'
    msg += text_progres(currentBits,totalBits)+'\n'
    msg += '├Done: '+sizeof_fmt(currentBits)+' of '+sizeof_fmt(totalBits)+'\n'
    msg += '├Speed: '+sizeof_fmt(speed)+'/s\n'
    msg += '├ETA: '+str(datetime.timedelta(seconds=int(time)))+'s\n'
    msg += '╰─ⓘ UwU XD 〄\n'

    if tid!='':
        msg+= '/cancel_' + tid
    return msg
def createUploading(filename,totalBits,currentBits,speed,time,originalname=''):
    msg = '╭───ⓘ Uploading: '+str(porcent(currentBits,totalBits))+'%\n'
    msg += '├File name: '+filename+'\n'
    msg += text_progres(currentBits,totalBits)+'\n'
    msg += '├Done: '+sizeof_fmt(currentBits)+' of '+sizeof_fmt(totalBits)+'\n'
    msg += '├Speed: '+sizeof_fmt(speed)+'/s\n'
    msg += '├ETA: '+str(datetime.timedelta(seconds=int(time)))+'s\n'
    msg += '╰─ⓘ UwU XD 〄'

    return msg
def createCompresing(filename,filesize,splitsize):
    msg = "╭───ⓘ Compressing: " + str(sizeof_fmt(filesize))+'\n│\n'
    msg += "╰─⎔ Dividing in "+ str(round(int(filesize/splitsize)+1,1))+" parts of "+str(sizeof_fmt(splitsize))+'\n'

    return msg
def createFinishUploading(filename,filesize,split_size,current,count,findex):
    msg = "<b>╭───ⓘ Finished!</b> " + str(sizeof_fmt(filesize))+'\n'
    msg += "<b>│</b>"
    return msg

def createFileMsg(filename,files):
    import urllib
    if len(files)>0:
        msg= "<b>╰─⎔ Link(s) ⤋</b>\n"
        for f in files:
            url = urllib.parse.unquote(f['directurl'],encoding='utf-8', errors='replace')
            #msg+= '<a href="'+f['url']+'">' + f['name'] + '</a>'
            msg+= "<a href='"+url+"'>"+f['name']+'</a>\n'
        return msg
    return ''

def createFilesMsg(evfiles):
    msg = 'File(s) ('+str(len(evfiles))+')\n\n'
    i = 0
    for f in evfiles:
            try:
                fextarray = str(f['files'][0]['name']).split('.')
                fext = ''
                if len(fextarray)>=3:
                    fext = '.'+fextarray[-2]
                else:
                    fext = '.'+fextarray[-1]
                fname = f['name'] + fext
                msg+= '/txt_'+ str(i) + ' /del_'+ str(i) + '\n' + fname +'\n\n'
                i+=1
            except:pass
    return msg
def createStat(username,userdata,isadmin):
    from pyobigram.utils import sizeof_fmt
    msg = '╭───ⓘ User Settings\n'+'│'+'\n'
    msg+= '├User: ' + str(userdata['moodle_user'])+'\n'
    msg+= '├Password: ' + '********\n'
    msg+= '├Cloud URL: '+ str(userdata['moodle_host'])+'\n'
    msg+= '├Cloud ID: ' + str(userdata['moodle_repo_id'])+'\n'
    msg+= '├Upload type: ' + str(userdata['uploadtype'])+'\n'
    msg+= '├Zips size: ' + sizeof_fmt(userdata['zips']*1024*1024) + '\n│\n'
    proxy = 'Off'
    if userdata['proxy'] !='':
       proxy = '✓'
    msg+= '├Proxy setted: ' + proxy + '\n'
    msg+= '╰─ⓘ UwU XD 〄'
    return msg
