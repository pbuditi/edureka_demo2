strSMTPServer = Wscript.Arguments.Item(0) 
strEmailFrom = Wscript.Arguments.Item(1) 
strEmailTo = Wscript.Arguments.Item(2)
strEmailCc = Wscript.Arguments.Item(3)
strSubject = Wscript.Arguments.Item(4)
strAttachments = Wscript.Arguments.Item(5)

Set objMail = CreateObject("CDO.Message")
Set objConf = CreateObject("CDO.Configuration")
Set objFlds = objConf.Fields
Set objFSO = CreateObject("Scripting.FileSystemObject") 
Set objFile = objFSO.OpenTextFile(strAttachments) 
strData = objFile.ReadAll 

objFlds.Item("http://schemas.microsoft.com/cdo/configuration/sendusing") = 2 'cdoSendUsingPort
objFlds.Item("http://schemas.microsoft.com/cdo/configuration/smtpserver") = strSMTPServer '"10.129.102.46"
objFlds.Item("http://schemas.microsoft.com/cdo/configuration/smtpserverport") = 25 'default port for email
objFlds.Item("http://schemas.microsoft.com/cdo/configuration/sendusername") = "bamboo"
objFlds.Item("http://schemas.microsoft.com/cdo/configuration/sendpassword") = "bamboo"
objFlds.Item("http://schemas.microsoft.com/cdo/configuration/smtpauthenticate") = 1 'cdoBasic
objFlds.Update

objMail.Configuration = objConf
objMail.From = strEmailFrom
objMail.To = strEmailTo
objMail.Cc = strEmailCc
objMail.Subject = strSubject
objMail.HTMLBody = "<html>" + strData + "</html>"
objMail.AddAttachment strAttachments

'Option Explicit
Dim i
i = 0
Do While i < 10
  On Error Resume Next
  WScript.Echo "Sending e-mail"
  objMail.Send
  If Err.Number <> 0 Then
    WScript.Echo "Error during e-mail send: " & Err.Description
	i = i + 1
  Else i = 10
  End If
Loop

Set objFile = Nothing
Set objFSO = Nothing
Set objFlds = Nothing
Set objConf = Nothing
Set objMail = Nothing
