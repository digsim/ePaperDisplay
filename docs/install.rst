Installation
====================

From Download
--------------
The simplest way to use *displayCalendar* is to download the packaged *pex* file from `displayCalendar`_ and put it somewhere on the path like ``/usr/local/bin/``or ``/usr/local/share/bin``or ``~/.local/bin/`` and make it executable,

From this point on, the binary can be executed by calling the *pex* file directly. There exist 3 variants of the *pex* file, depending on the availalbe python version. Choose either *displayCalendar27.pex* or *displayCalendar35.pex* depending on what is availalbe on your system.

.. only:: builder_html
Download files directly from here:

* :download:`displayCalendar27.pex <../dist/displayCalendar27.pex>`
* :download:`displayCalendar35.pex <../dist/displayCalendar35.pex>`

From pip
---------

Simply run::

    sudo -H pip install displayCalendar


From Sources
-------------

Final installation
^^^^^^^^^^^^^^^^^^

From a terminal launch::

    python setup.py install --record files.txt

This will compile and install the project to the pyhton libraries (eg. ``/usr/local/lib/python3.5/site-packages/displayCalendar-0.9-py3.5.egg``). Furthermore it will install a script in ``/usr/local/bin/``:
* displayCalendar

Upon the first start a copy of a pristine application and logging configuration are created in the user's home directory ``~/.epaper_display/``. From this point on configuration files are read from this location. It is however possible to overwrite them either by placing a file with the same name (but prefixed with a dot eg. ``.logging.conf``) in the current working directory.

Development installation
^^^^^^^^^^^^^^^^^^^^^^^^

from a terminal launch::

    python setup.py develop --record files.txt

does the same as before but, uses links instead of copying files.

Clean Working directory
^^^^^^^^^^^^^^^^^^^^^^^^

To clean the working directory::

    python setup.py clean --all
    rm -rf build/ dist/displayCalendar.egg-info/ files.txt




Known Problems
--------------

SSL Problems
^^^^^^^^^^^^^

Upon running the displayCalendar binary you might get the following exception::

    ITC Password:
    DEBUG - Using Python 2
    DEBUG - Saving calendar to file /var/folders/j4/8bm7_nb54kl2m_9kl6k5gk880000gn/T/tmp6krkW7
    INFO - Starting new HTTPS connection (1): example.com
    INFO - Starting new HTTPS connection (1): example.com
    Traceback (most recent call last):
      File "/usr/local/bin/displayCalendar", line 9, in <module>
        load_entry_point('displayCalendar==1.0.0', 'console_scripts', 'displayCalendar')()
      File "/Volumes/Data/ruppena/Documents/Programming/Python/ePaperCalendar/main/__init__.py", line 8, in main
        main.getArguments(sys.argv[1:])
      File "/Volumes/Data/ruppena/Documents/Programming/Python/ePaperCalendar/main/mainImpl.py", line 58, in getArguments
        self.main()
      File "/Volumes/Data/ruppena/Documents/Programming/Python/ePaperCalendar/main/main.py", line 48, in main
        self.doWork()
      File "/Volumes/Data/ruppena/Documents/Programming/Python/ePaperCalendar/main/mainImpl.py", line 76, in doWork
        events = c.fetchCalendarEvents()
      File "/Volumes/Data/ruppena/Documents/Programming/Python/ePaperCalendar/ITC/calendar2itc.py", line 33, in fetchCalendarEvents
        response = requests.get(self.__calendarurl, auth=(self.__username, self.__password), stream=True, verify=False, proxies=self.__proxies)
      File "/Library/Python/2.7/site-packages/requests/api.py", line 70, in get
        return request('get', url, params=params, **kwargs)
      File "/Library/Python/2.7/site-packages/requests/api.py", line 56, in request
        return session.request(method=method, url=url, **kwargs)
      File "/Library/Python/2.7/site-packages/requests/sessions.py", line 475, in request
        resp = self.send(prep, **send_kwargs)
      File "/Library/Python/2.7/site-packages/requests/sessions.py", line 596, in send
        r = adapter.send(request, **kwargs)
      File "/Library/Python/2.7/site-packages/requests/adapters.py", line 497, in send
        raise SSLError(e, request=request)
    requests.exceptions.SSLError: [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:590)


This simply means that some OpenSSL libraries are too old. Start by upgrading::

    sudo -H pip install --upgrade pyOpenSSL
    sudo -H pip install --upgrade ndg-httpsclient

if that is not enough also update the following::

    sudo -H pip install --upgrade pyasn1

Proxy Problems
^^^^^^^^^^^^^^^

Installation from sources may fail behind a proxy. Thus install the requirements by hand and specify the proxy::

    sudo -H pip install --proxy=http://my.proxy.com:1234 -r requirements.txt


Uninstall
----------

Method 1 (pip)
^^^^^^^^^^^^^^

If the package was installed with ``pip`` simply run::

    pip uninstall displayCalendar

Method 2 (from sources)
^^^^^^^^^^^^^^^^^^^^^^^

If the packages was installed from sources::

    cat files.txt |sudo xargs rm -rf

Method 3  (from sources)
^^^^^^^^^^^^^^^^^^^^^^^^^

First find the installed package with pip and the uninstall it::

    ✔ ~/Documents/Programming/Python/ePaperCalendar [master|✚ 1]
    19:02 $ pip3 freeze |grep displayCalendar
    displayCalendar==1.1

    ✔ ~/Documents/Programming/Python/ePaperCalendar [master|✚ 1]
    19:02 $  pip3 uninstall displayCalendar
    Uninstalling displayCalendar-1.1:
      /usr/local/bin/displayCalendar
      /usr/local/lib/python3.5/site-packages/displayCalendar-1.1.dist-info/DESCRIPTION.rst
      /usr/local/lib/python3.5/site-packages/displayCalendar-1.1.dist-info/INSTALLER
      /usr/local/lib/python3.5/site-packages/displayCalendar-1.1.dist-info/METADATA
      /usr/local/lib/python3.5/site-packages/displayCalendar-1.1.dist-info/RECORD
      /usr/local/lib/python3.5/site-packages/displayCalendar-1.1.dist-info/WHEEL
      /usr/local/lib/python3.5/site-packages/displayCalendar-1.1.dist-info/entry_points.txt
      /usr/local/lib/python3.5/site-packages/displayCalendar-1.1.dist-info/metadata.json
      /usr/local/lib/python3.5/site-packages/displayCalendar-1.1.dist-info/top_level.txt
      /usr/local/lib/python3.5/site-packages/displayCalendar/__init__.py
      /usr/local/lib/python3.5/site-packages/displayCalendar/__pycache__/__init__.cpython-35.pyc
      /usr/local/lib/python3.5/site-packages/displayCalendar/etc/displayCalendar-completion.bash
      /usr/local/lib/python3.5/site-packages/displayCalendar/etc/displayCalendar.conf
      /usr/local/lib/python3.5/site-packages/displayCalendar/etc/logging.conf
      /usr/local/lib/python3.5/site-packages/displayCalendar/calendar/__init__.py
      /usr/local/lib/python3.5/site-packages/displayCalendar/calendar/__pycache__/__init__.cpython-35.pyc
      /usr/local/lib/python3.5/site-packages/displayCalendar/calendar/__pycache__/calendar2events.cpython-35.pyc
      /usr/local/lib/python3.5/site-packages/displayCalendar/calendar/__pycache__/calendarEvent.cpython-35.pyc
      /usr/local/lib/python3.5/site-packages/displayCalendar/calendar/calendar2events.py
      /usr/local/lib/python3.5/site-packages/displayCalendar/calendar/calendarEvent.py
      /usr/local/lib/python3.5/site-packages/displayCalendar/main/__init__.py
      /usr/local/lib/python3.5/site-packages/displayCalendar/main/__pycache__/__init__.cpython-35.pyc
      /usr/local/lib/python3.5/site-packages/displayCalendar/main/__pycache__/main.cpython-35.pyc
      /usr/local/lib/python3.5/site-packages/displayCalendar/main/__pycache__/mainImpl.cpython-35.pyc
      /usr/local/lib/python3.5/site-packages/displayCalendar/main/main.py
      /usr/local/lib/python3.5/site-packages/displayCalendar/main/mainImpl.py
    Proceed (y/n)? y
      Successfully uninstalled displayCalendar-1.1



To install the displayCalendar package, use::

  python setup.py install

If installation is successful, you will be able to import the iCalendar
package, like this::

  >>> import icalendar


Building the documentation locally
----------------------------------

To build the documentation follow these steps:

.. code-block:: bash

    $ git clone http://digsim.is-a-geek.com/rhode/ePaperCalendar
    $ cd displayCalendar
    $ virtualenv-2.7 .
    $ source bin/activate
    $ pip install -r requirements_docs.txt --extra-index-url http://pypi.is-a-geek.com/simple --trusted-host pypi.is-a-geek.com
    $ cd docs
    $ make html

You can now open the output from ``_build/html/index.html``. To build the
presentation-version use ``make presentation`` instead of ``make html``. You
can open the presentation at ``presentation/index.html``.


.. _`displayCalendar`: https://displayCalendar.gotdns.org/