_Below are high-level instructions. The links below should provide you with info to forge ahead. Some of this setup is platform-specific, so google around and if you still are stuck email neil AT awaaz DOT de. If you are setting up on Ubuntu 10.04 LTS (recommended), then you may benefit from these ill-formatted by quite detailed install guides: [IVR](https://www.dropbox.com/s/dyr5piwhyoy2dq8/AD_IVR_install_guide.pdf) and [Web App](https://www.dropbox.com/s/iu4qj9u364rzigu/AD_web_app_install_guide.pdf) (thanks to Jigar for creating these)_

## Web Components ##
  1. Install Python, Java SDK, MySQL
  1. Install Django
  1. Install wadofstuff Django serializers
  1. Install mysqldb python module
  1. Create a mysql database called 'otalo', and a user 'otalo' and password 'otalo' with all privileges to it.

## Dev Environment ##
  1. Setup web components above
  1. Install Eclipse
  1. Install [Subclipse eclipse plugin](http://subclipse.tigris.org/servlets/ProjectProcess?pageID=p4wYuA)
  1. Install [GWT eclipse plugin](http://code.google.com/eclipse/docs/getting_started.html)
  1. Checkout gwt folder from the repository (trunk/web/). You can follow the instructions [here](http://blog.msbbc.co.uk/2007/06/using-googles-free-svn-repository-with.html). Be sure to check out the code as a GWT project and name it 'ao' with package name 'org.otalo.ao'.
  1. Checkout trunk/web/django into a new project ao\_server. Optionally use [python project plugin](http://pydev.org/download.html)
  1. Checkout trunk/IVR into a new project ao\_IVR. Optionally use [lua plugin](http://luaeclipse.luaforge.net/manual.html#installation), v.1.1 works on Helios

## IVR ##
  1. Download and install FreeSWITCH, with mod\_shout enabled
  1. Download and install lua and luasql
  1. Open ports 5060, 5080 tcp and udp in server firewall (for centOS, use /sbin/iptables command)
  1. Checkout trunk/IVR and drop the directory into /usr/local/freeswitch/scripts/AO (i.e. call the downloaded directory 'AO')
  1. In FreeSWITCH's conf/dialplan/default directory, create a new dialplan for AO. Call it something like 001\_otalo.xml, and make it look like this:

```
<extension name="incoming">
        <condition field="destination_number" expression="^30142000$">
            <action application="lua" data="AO/otalo.lua" />
        </condition>
 </extension>
```

The 'expression' attribute should correspond to your inbound PRI number or SIP extension (i.e. '5000', but make sure no other app is taking that extension (including in /dialplan/default.xml)). Default user ids are 1000, 1001, 1002, all with password 1234

## Web Server ##
  1. Setup web components above
  1. Checkout trunk/web and place the code in a place you are comfortable with web server accessing it (a good place is /home/

&lt;userid&gt;

/otalo). You can place the gwt and django\_templates folders in /var/www/html.
  1. In the django (or 'otalo') directory, run 'python manage.py syncdb' to setup the mysql tables. Run 'python manage.py loaddata production.json' and 'python manage.py loaddata tags.json' to seed the tables.
  1. Install and configure mod\_wsgi for your apache server
  1. setup django project to interface with wsgi using [these instructions](http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango)
  1. Be sure that the paths in django.wsgi, settings.py, and the paths in your apache config file are all matched up