def SendEmail(fs_smtpsvr, fs_user, fs_pass, fs_emailcontent):
    import smtplib
    import socket

    fs_FromAddr = ''
    fs_ToAddr  = ''
    fs_emailcontent = 'Hello'


# Delta test
    s = socket.socket()
    s.bind(('', 50007))
    s.listen(1)
    s.close()


    # Send Mail
    server = smtplib.SMTP(fs_smtpsvr)
#    server.login(fs_user,fs_pass)
    server.sendmail(fs_FromAddr, fs_ToAddr, fs_emailcontent)
    server.quit()

    return ()
