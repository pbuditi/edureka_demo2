::This is an example of using mailer.vbs

set mailerPath=${bamboo.working.directory}\Scripts\mailer\mailer.vbs
set smtpServer=10.129.102.46
set from=bamboo@network.ae
set to=Sergei_Miasnikov@epam.com
set cc=Sergei_Miasnikov@epam.com
set subj="Test Subject"
set htmlPath="D:\Atlassian\Bamboo-Home\artifacts\ET-TEC\PIRR\build-00123\Log\SummaryTestRun_Report.html"

cscript //nologo %mailerpath% %smtpServer% %from% %to% %cc% %subj% %htmlPath%
