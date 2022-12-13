from cProfile import run
import pstats
from pyobigram.utils import sizeof_fmt,get_file_size,createID,nice_time
from pyobigram.client import ObigramClient,inlineQueryResultArticle
from MoodleClient import MoodleClient

from JDatabase import JsonDatabase
import zipfile
import os
import infos
import xdlink
import mediafire
import datetime
import time
import youtube
import NexCloudClient
from pydownloader.downloader import Downloader
from ProxyCloud import ProxyCloud
import ProxyCloud
import socket
import tlmedia
import S5Crypto
import asyncio
import aiohttp
import moodlews
import moodle_client
from moodle_client import MoodleClient2
from yarl import URL
import re
from draft_to_calendar import send_calendar

def sign_url(token: str, url: URL):
    query: dict = dict(url.query)
    query["token"] = token
    path = "webservice" + url.path
    return url.with_path(path).with_query(query)

def downloadFile(downloader,filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        thread = args[2]
        if thread.getStore('stop'):
            downloader.stop()
        name = filename
        nam = name[0:15]
        zip = str(name).split('.')[-1]
        name2 = nam+'.'+zip
        if '7z' in name:     
            name2 = nam+'.7z.'+zip
        filename = name2   
        downloadingInfo = infos.createDownloading(filename,totalBits,currentBits,speed,time,tid=thread.id)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def uploadFile(filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        originalfile = args[2]
        thread = args[3]
        name = filename
        nam = name[0:15]
        zip = str(name).split('.')[-1]
        name2 = nam+'.'+zip
        if '7z' in name:     
            name2 = nam+'.7z.'+zip
        filename = name2   
        downloadingInfo = infos.createUploading(filename,totalBits,currentBits,speed,time,originalfile)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def processUploadFiles(filename,filesize,files,update,bot,message,thread=None,jdb=None):
    try:
        bot.editMessageText(message,'📡Connecting to the server...')
        evidence = None
        fileid = None
        user_info = jdb.get_user(update.message.sender.username)
        cloudtype = user_info['cloudtype']
        host = user_info['moodle_host']
        if host != 'https://eva.uci.cu/':
            proxy = ProxyCloud.parse(user_info['proxy'])
            if cloudtype == 'moodle':
                client = MoodleClient(user_info['moodle_user'],
                                  user_info['moodle_password'],
                                  user_info['moodle_host'],
                                  user_info['moodle_repo_id'],
                                  proxy=proxy)
                loged = client.login()
            itererr = 0
            if loged:
                if user_info['uploadtype'] == 'evidence':
                    evidences = client.getEvidences()
                    evidname = str(filename).split('.')[0]
                    for evid in evidences:
                        if evid['name'] == evidname:
                            evidence = evid
                            break
                    if evidence is None:
                        evidence = client.createEvidence(evidname)

                originalfile = ''
                if len(files)>1:
                    originalfile = filename
                draftlist = []
                for f in files:
                    f_size = get_file_size(f)
                    resp = None
                    iter = 0
                    tokenize = False
                    if user_info['tokenize']!=0:
                       tokenize = True
                    while resp is None:
                          if user_info['uploadtype'] == 'evidence':
                             fileid,resp = client.upload_file(f,evidence,fileid,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                          elif user_info['uploadtype'] == 'draft':
                                fileid,resp = client.upload_file_draft(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                                draftlist.append(resp)
                          elif user_info['uploadtype'] == 'profile':
                                fileid,resp = client.upload_file_profile(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                                draftlist.append(resp)
                          elif user_info['uploadtype'] == 'blog':
                                fileid,resp = client.upload_file_blog(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                                draftlist.append(resp)
                          elif user_info['uploadtype'] == 'calendar':
                                fileid,resp = client.upload_file_calendar(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                                draftlist.append(resp)
                          iter += 1
                          if iter>=10:
                              break
                    os.unlink(f)
                if user_info['uploadtype'] == 'evidence':
                    try:
                        client.saveEvidence(evidence)
                    except:pass
                return draftlist
            else:
                if host != 'https://mrrr/' or 'https://rrr/':
                    bot.editMessageText(message,'Retrying')
                    host = user_info['moodle_host']
                    user = user_info['moodle_user']
                    passw = user_info['moodle_password']
                    repoid = user_info['moodle_repo_id']
                    token = moodlews.get_webservice_token(host,user,passw,proxy=proxy)
                    print('ya tomo aki')
                    for f in files:
                        data = asyncio.run(moodlews.webservice_upload_file(host,token,file,progressfunc=uploadFile,proxy=proxy,args=(bot,message,filename,thread)))
                        print(data)
                        while not moodlews.store_exist(file):pass
                        data = moodlews.get_store(file)
                        if data[0]:
                            urls = moodlews.make_draft_urls(data[0])
                            draftlist.append({'file':file,'url':urls[0]})
                            return draftlist
                    else:
                        err = data[1]
                        bot.editMessageText(message,'❗Error.',err)
                else:
                    print('no chilvio el otro v:')
                    cli = MoodleClient2(host,user,passw,repoid,proxy)
                    for file in files:
                        data = asyncio.run(cli.LoginUpload(file, uploadFile, (bot, message, filename, thread)))
                        while cli.status is None: pass
                        data = cli.get_store(file)
                        if data:
                            if 'error' in data:
                                err = data['error']
                                bot.editMessageText(message,'❗Error.',err)
                            else:
                                draftlist.append({'file': file, 'url': data['url']})
                                return draftlist
        elif cloudtype == 'cloud':
            tokenize = False
            if user_info['tokenize']!=0:
               tokenize = True
            bot.editMessageText(message,'🚀Uploading please wait.')
            host = user_info['moodle_host']
            user = user_info['moodle_user']
            passw = user_info['moodle_password']
            remotepath = user_info['dir']
            client = NexCloudClient.NexCloudClient(user,passw,host,proxy=proxy)
            loged = client.login()
            if loged:
               originalfile = ''
               if len(files)>1:
                    originalfile = filename
               filesdata = []
               for f in files:
                   data = client.upload_file(f,path=remotepath,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                   filesdata.append(data)
                   os.unlink(f)
               return filesdata
    except Exception as ex:
        bot.editMessageText(message,f'❗Error {str(ex)}.')


def processFile(update,bot,message,file,thread=None,jdb=None):
    file_size = get_file_size(file)
    getUser = jdb.get_user(update.message.sender.username)
    max_file_size = 1024 * 1024 * getUser['zips']
    file_upload_count = 0
    client = None
    findex = 0
    if file_size > max_file_size:
        compresingInfo = infos.createCompresing(file,file_size,max_file_size)
        bot.editMessageText(message,compresingInfo)
        zipname = str(file).split('.')[0] + createID()
        mult_file = zipfile.MultiFile(zipname,max_file_size)
        zip = zipfile.ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
        zip.write(file)
        zip.close()
        mult_file.close()
        client = processUploadFiles(file,file_size,mult_file.files,update,bot,message,jdb=jdb)
        try:
            os.unlink(file)
        except:pass
        file_upload_count = len(zipfile.files)
    else:
        client = processUploadFiles(file,file_size,[file],update,bot,message,jdb=jdb)
        file_upload_count = 1
    bot.editMessageText(message,'Creating TXT')
    evidname = ''
    files = []
    if client:
        if getUser['cloudtype'] == 'moodle':
            if getUser['uploadtype'] == 'evidence':
                try:
                    evidname = str(file).split('.')[0]
                    txtname = evidname + '.txt'
                    evidences = client.getEvidences()
                    for ev in evidences:
                        if ev['name'] == evidname:
                           files = ev['files']
                           break
                        if len(ev['files'])>0:
                           findex+=1
                    client.logout()
                except:pass
            if getUser['uploadtype'] == 'draft' or getUser['uploadtype'] == 'blog' or getUser['uploadtype'] == 'calendar' or getUser['uploadtype'] == 'profile':
               for draft in client:
                   files.append({'name':draft['file'],'directurl':draft['url']})
        else:
            for data in client:
                files.append({'name':data['name'],'directurl':data['url']})
        bot.deleteMessage(message.chat.id,message.message_id)
        finishInfo = infos.createFinishUploading(file,file_size,max_file_size,file_upload_count,file_upload_count,findex)
        filesInfo = infos.createFileMsg(file,files)
        bot.sendMessage(message.chat.id,finishInfo+'\n'+filesInfo,parse_mode='html')
        if len(files)>0:
            txtname = str(file).split('/')[-1].split('.')[0] + '.txt'
            sendTxt(txtname,files,update,bot)
        try:

            import urllib

            user_info = jdb.get_user(update.message.sender.username)
            cloudtype = user_info['cloudtype']
            proxy = ProxyCloud.parse(user_info['proxy'])
            if cloudtype == 'moodle':
                client = MoodleClient(user_info['moodle_user'],
                                    user_info['moodle_password'],
                                    user_info['moodle_host'],
                                    user_info['moodle_repo_id'],
                                    proxy=proxy)
            host = user_info['moodle_host']
            user = user_info['moodle_user']
            passw = user_info['moodle_password']
            if getUser['uploadtype'] == 'calendario':
                nuevo = []
                #if len(files)>0:
                    #for f in files:
                        #url = urllib.parse.unquote(f['directurl'],encoding='utf-8', errors='replace')
                        #nuevo.append(str(url))
                fi = 0
                for f in files:
                    separator = ''
                    if fi < len(files)-1:
                        separator += '\n'
                    nuevo.append(f['directurl']+separator)
                    fi += 1
                urls = asyncio.run(send_calendar(host,user,passw,nuevo))
                loged = client.login()
                if loged:
                    token = client.userdata
                    modif = token['token']
                    client.logout()
                nuevito = []
                for url in urls:
                    url_signed = (str(sign_url(modif, URL(url))))
                    nuevito.append(url_signed)
                loco = '\n'.join(map(str, nuevito))
                fname = str(txtname)
                with open(fname, "w") as f:
                    f.write(str(loco))
                #fname = str(randint(100000000, 9999999999)) + ".txt"
                bot.sendMessage(message.chat.id,'✔Calendar direct Links!')
                bot.sendFile(update.message.chat.id,fname)
            else:
                return
        except:
            bot.sendMessage(message.chat.id,'❕Could not move to calendar.')
    else:
        bot.editMessageText(message,'❗Cloud error, crash.')


def ddl(update,bot,message,url,file_name='',thread=None,jdb=None):
    downloader = Downloader()
    file = downloader.download_url(url,progressfunc=downloadFile,args=(bot,message,thread))
    if not downloader.stoping:
        if file:
            processFile(update,bot,message,file,jdb=jdb)

def sendTxt(name,files,update,bot):
                txt = open(name,'w')
                fi = 0
                for f in files:
                    separator = ''
                    if fi < len(files)-1:
                        separator += '\n'
                    txt.write(f['directurl']+separator)
                    fi += 1
                txt.close()
                bot.sendFile(update.message.chat.id,name)
                os.unlink(name)

def onmessage(update,bot:ObigramClient):
    try:
        thread = bot.this_thread
        username = update.message.sender.username
        #tl_admin_user = os.environ.get('tl_admin_user')

        #set in debug
        tl_admin_user = 'lil_l4chy'

        jdb = JsonDatabase('database')
        jdb.check_create()
        jdb.load()

        user_info = jdb.get_user(username)

        if username == tl_admin_user or user_info:  # validate user
            if user_info is None:
                if username == tl_admin_user:
                    jdb.create_admin(username)
                else:
                    jdb.create_user(username)
                user_info = jdb.get_user(username)
                jdb.save()
        else:
            mensaje = "❕This bot is for private use.\nUse the public bot: @uwu_dw_bot"
            intento_msg = "❕The user @"+username+ " started the bot!"
            bot.sendMessage(update.message.chat.id,mensaje)
            bot.sendMessage(1234567890,intento_msg)
            return

        msgText = ''
        try: msgText = update.message.text
        except:pass

        # comandos de admin
        if '/useradm' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                message = bot.sendMessage(update.message.chat.id,'🦾')
                message = bot.sendMessage(update.message.chat.id,'✔You are bot administrator, so you have total control over itself.')
            else:
                message = bot.sendMessage(update.message.chat.id,'')
                message = bot.sendMessage(update.message.chat.id,'❗You are just an user, for now you have limitated control.')
            return
        # end

        # comandos de usuario
        if '/help' in msgText:
            message = bot.sendMessage(update.message.chat.id,'𝚄𝚜𝚎𝚛 𝚐𝚞𝚒𝚍𝚎:')
            help = open('help.txt','r')
            bot.sendMessage(update.message.chat.id,help.read())
            help.close()
            return
        if '/version' in msgText:
            message = bot.sendMessage(update.message.chat.id,'〄 Versión 2.10 Release (2022/02/10)')
            version = open('version.txt','r')
            bot.sendMessage(update.message.chat.id,version.read())
            version.close()
            return
        if '/moodles' in msgText:
            message = bot.sendMessage(update.message.chat.id,'𝙿𝚛𝚎𝚌𝚘𝚗𝚏𝚒𝚐𝚞𝚛𝚎𝚍 𝙼𝚘𝚘𝚍𝚕𝚎𝚜:')
            moodles = open('moodles.txt','r')
            bot.sendMessage(update.message.chat.id,moodles.read())
            moodles.close()
            return
        if '/pass' in msgText:
            message = bot.sendMessage(update.message.chat.id,'🔐')
            passwords = open('passwords.txt','r')
            bot.sendMessage(update.message.chat.id,passwords.read())
            passwords.close()
            return
        if '/del' in msgText:
            message = bot.sendMessage(update.message.chat.id,'❗️The correct form is:\n\n/rm https://eva.uo.edu.cu/draftfile.php/249388/user/draft/81374758/Bullet%20TrainSO8dd9O2.7z.001')
            delete = open('delete.txt','r')
            bot.sendMessage(update.message.chat.id,delete.read())
            delete.close()
            return
        if '/cmds' in msgText:
            message = bot.sendMessage(update.message.chat.id,'🙂𝙵𝚘𝚛 𝚊𝚍𝚍 𝚝𝚑𝚒𝚜 𝚌𝚘𝚖𝚖𝚊𝚗𝚍𝚜 𝚝𝚘 𝚝𝚑𝚎 𝚚𝚞𝚒𝚌𝚔 𝚊𝚌𝚌𝚎𝚜𝚜 𝚖𝚎𝚗𝚞 𝚢𝚘𝚞 𝚖𝚞𝚜𝚝 𝚜𝚎𝚗𝚍 𝚝𝚑𝚎 𝚌𝚘𝚖𝚖𝚊𝚗𝚍 /setcommands 𝚝𝚘 @BotFather 𝚊𝚗𝚍 𝚝𝚑𝚎𝚗 𝚜𝚎𝚕𝚎𝚌𝚝 𝚢𝚘𝚞𝚛 𝚋𝚘𝚝, 𝚊𝚏𝚝𝚎𝚛 𝚘𝚗𝚕𝚢 𝚛𝚎𝚖𝚊𝚒𝚗𝚐𝚜 𝚛𝚎𝚜𝚎𝚗𝚍 𝚝𝚑𝚎 𝚖𝚎𝚜𝚜𝚊𝚐𝚎 𝚠𝚒𝚝𝚑 𝚝𝚑𝚎 𝚗𝚎𝚡𝚝 𝚌𝚘𝚖𝚖𝚊𝚗𝚍𝚜 𝚊𝚗𝚍... 𝚍𝚘𝚗𝚎😁.')
            cmds = open('commands.txt','r')
            bot.sendMessage(update.message.chat.id,commands.read())
            commands.close()
            return
        if '/info' in msgText:
            getUser = user_info
            if getUser:
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
                return
        if '/zip' in msgText:
            getUser = user_info
            if getUser:
                try:
                   size = int(str(msgText).split(' ')[1])
                   getUser['zips'] = size
                   jdb.save_data_user(username,getUser)
                   jdb.save()
                   msg = '📚Perfect now the zips will be of '+ sizeof_fmt(size*1024*1024)+' the parts.'
                   bot.sendMessage(update.message.chat.id,msg)
                except:
                   bot.sendMessage(update.message.chat.id,'❗Command error /zip zips_size.')    
                return
        if '/acc' in msgText:
            try:
                account = str(msgText).split(' ',2)[1].split(',')
                user = account[0]
                passw = account[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_user'] = user
                    getUser['moodle_password'] = passw
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'❗Command error /acc user,password.')
            return
        if '/host' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                host = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_host'] = host
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'❗Command error /host cloud_url.')
            return
        if '/repo' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = int(cmd[1])
                getUser = user_info
                if getUser:
                    getUser['moodle_repo_id'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'❗Command error /repo moodle_repo_id.')
            return
        if '/upt' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                type = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['uploadtype'] = type
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)                    
            except:
                bot.sendMessage(update.message.chat.id,'❗Command error /upt (draft, profile, blog, calendar).')
            return
        if '/proxy' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                proxy = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['proxy'] = proxy
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '✔Perfect, proxy equipped successfuly.'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                if user_info:
                    user_info['proxy'] = ''
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'❗Error equipping proxy.')
            return
        if '/crypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy = S5Crypto.encrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'🔒Proxy encrypted:\n{proxy}')
            return
        if '/decrypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy_de = S5Crypto.decrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'🔓Proxy decrypted:\n{proxy_de}')
            return
        if '/off_proxy' in msgText:
            try:
                getUser = user_info
                if getUser:
                    getUser['proxy'] = ''
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '❕Alrigth, proxy unequipped successfuly.'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                if user_info:
                    user_info['proxy'] = ''
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'❗Error encrypting proxy.')
            return                    
        if '/cancel_' in msgText:
            try:
                cmd = str(msgText).split('_',2)
                tid = cmd[1]
                tcancel = bot.threads[tid]
                msg = tcancel.getStore('msg')
                tcancel.store('stop',True)
                time.sleep(3)
                bot.editMessageText(msg,'✔Task cancelled.')
            except Exception as ex:
                print(str(ex))
            return
        #end

        message = bot.sendMessage(update.message.chat.id,'Analizyng⏳...')

        thread.store('msg',message)

        if '/start' in msgText:
            start_msg = '╭───ⓘ Hello! ' + str(username)+'\n│\n'
            start_msg+= '├⎔Bot de descarga gratuita en Cuba.\n│\n'
            start_msg+= '├⎔Enviar /help para más información.\n│\n'
            start_msg+= '╰─ⓘ UwU XD 〄\n'
            bot.editMessageText(message,start_msg)
        elif '/test' in msgText:
            message2 = bot.editMessageText(message,'⏳')

            try:
                proxy = ProxyCloud.parse(user_info['proxy'])
                client = MoodleClient(user_info['moodle_user'],
                                      user_info['moodle_password'],
                                      user_info['moodle_host'],
                                      user_info['moodle_repo_id'],proxy=proxy)
                loged = client.login()
                if loged:
                    token = client.userdata
                    modif = token['token']
                    bot.editMessageText(message2,'✔')
                    client.logout()
                else:
                    bot.editMessageText(message2,'❕')
            except Exception as ex:
                bot.editMessageText(message2,'❗')
        elif '/rm' in msgText:
            enlace = msgText.split('/delete')[-1]
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged= client.login()
            if loged:
                #update.message.chat.id
                deleted = client.delete(enlace)

                bot.sendMessage(update.message.chat.id, "✔LINK successfully removed from Moodle.")

        elif '/jovenclub' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://cursad.jovenclub.cu/"
            getUser['uploadtype'] =  "profile"
            getUser['moodle_user'] = "tehehow"
            getUser['moodle_password'] = "OvKv182Mat*"
            getUser['moodle_repo_id'] = 3
            getUser['zips'] = 99
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"☑Cursad configuration loaded!")
            
        elif '/eva' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://eva.uo.edu.cu/"
            getUser['uploadtype'] =  "profile"
            getUser['moodle_user'] = "srenejr"
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 99
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"☑Eva configuration loaded.")
            
        elif '/uclv' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://moodle.uclv.edu.cu/"
            getUser['uploadtype'] =  "calendar"
            getUser['moodle_user'] = "manuele"
            getUser['moodle_password'] = "manolo*123"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 399
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"☑Uclv configuration loaded!")
            
        elif '/cursos' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://cursos.uo.edu.cu/"
            getUser['uploadtype'] =  "calendar"
            getUser['moodle_user'] = "srenejr"
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 99
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"☑Cursos configuration loaded.")
            
        elif '/eduvirtual' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://eduvirtual.uho.edu.cu/"
            getUser['uploadtype'] =  "profile"
            getUser['moodle_user'] = "karla-gonzalez"
            getUser['moodle_password'] = "kc1515gs"
            getUser['moodle_repo_id'] = 3
            getUser['zips'] = 8
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"☑Eduvirtual configuration loaded!")            
            
        elif '/evea' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://evea.uh.cu/"
            getUser['uploadtype'] =  "calendar"
            getUser['moodle_user'] = "diovi.tirador@estudiantes.fbio.uh.cu"
            getUser['moodle_password'] = "humboldt"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 99
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"☑Evea configuration loaded!")
            
        elif '/hlgsld' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://aulavirtual.hlg.sld.cu/"
            getUser['uploadtype'] =  "calendar"
            getUser['moodle_user'] = "srenejr"
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 5
            getUser['zips'] = 10
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"☑Hlg sld configuration loaded.")
            
        elif '/gtmsld' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://aulauvs.gtm.sld.cu/"
            getUser['uploadtype'] =  "calendar"
            getUser['moodle_user'] = "srenejr"
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 7
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"☑Gtm sld configuration loaded.")
            
        elif 'http' in msgText:
            url = msgText
            ddl(update,bot,message,url,file_name='',thread=thread,jdb=jdb)
        else:
            #if update:
            #    api_id = os.environ.get('api_id')
            #    api_hash = os.environ.get('api_hash')
            #    bot_token = os.environ.get('bot_token')
            #    
                # set in debug
            #    api_id = 7386053
            #    api_hash = '78d1c032f3aa546ff5176d9ff0e7f341'
            #    bot_token = '5124841893:AAH30p6ljtIzi2oPlaZwBmCfWQ1KelC6KUg'

            #    chat_id = int(update.message.chat.id)
            #    message_id = int(update.message.message_id)
            #    import asyncio
            #    asyncio.run(tlmedia.download_media(api_id,api_hash,bot_token,chat_id,message_id))
            #    return
            bot.editMessageText(message,'❗Error analizyng.')
    except Exception as ex:
           print(str(ex))
  
def main():
    bot_token = '5248887155:AAH6UeyVSu0hCJhiKb8ec-bjoTedp1pmAA0'
    
    bot = ObigramClient(bot_token)
    bot.onMessage(onmessage)
    bot.run()
    asyncio.run()

if __name__ == '__main__':
    try:
        main()
    except:
        main()
