Usage
=================

Launch the application with  ``displayCalendar -h`` to get a list of supported operations and parameters

.. _configuration:

Configuration
--------------
Upon the first launch, the script creates the ``~/.epaper_display/`` directory containing:
* logging.conf where the logger is configured
* epaper.conf where the general configuration is stored. Adapt at least the ``<calendars>``, ``<calendarurl>`` of the specified calendar properties to get started. The script will interactively ask for passwords when the ``<user>`` tag is set for a *Calendar* section.

The example below shows what such a file could look like::

    [Config]
    # Comma-separated list of calendars to parse for ITC events
    calendars: cal1
    # Verify SSL certificates
    verifyssl: true

    [cal1]
    # Replace XXX with your username
    url: http://example.com/Calendar

    [cal2]
    # If a resource requires authentication (basic auth) you can specify
    # the crendentials with user and pass.
    # if you omit the password, then displayCalendar will ask for it interactively.
    url: https://example.com/my_hard_work.ics
    user: XXX
    pass: ZZZ


The config file has 2 sections *Config* where general options sit and *cal1* contains url and credentials for the first calendar.

.. _debugging_and_logging:

Debugging and Logging
---------------------
As the script is run, this folder will also host a ``epaper.log`` file, containing the log of the *last* run.
