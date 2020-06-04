Debug
================================================================================


Enable logging
--------------------------------------------------------------------------------
hpestorapi uses Python’s Standard Library `logging module
<https://docs.python.org/3/library/logging.html>`_. Simple python script
with enabled debug logging:

.. code:: python

    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-

        import logging
        import hpestorapi

        if __name__ == '__main__':
            # Setup logging format, level, logfile
            logfmt = ('[%(asctime)s] '
                      '%(levelname)-8s '
                      '%(filename)-12s:%(lineno)-3d '
                      '%(message)s')

            logging.basicConfig(format=logfmt,
                                level=logging.WARNING,
                                filename='messages.log')

            # Set XP, 3PAR, StoreOnce loglevel
            logging.getLogger("hpestorapi.xp").setLevel(logging.DEBUG)
            logging.getLogger("hpestorapi.storeserv").setLevel(logging.DEBUG)
            logging.getLogger("hpestorapi.storeonce").setLevel(logging.DEBUG)

            """
            Your code starts here
            """

Five logging levels are used:

* DEBUG
* INFO
* WARNING
* ERROR
* FATAL

Bug reports
--------------------------------------------------------------------------------
If you have found a bug, please create an `GitHub issue <https://github
.com/HewlettPackard/python-storage-clients/issues>`_. Your questions are
welcomed in `gitter chat <https://gitter
.im/python-storage-clients>`_. And do not hesitate to contact me: Ivan
Smirnov <ivan.smirnov@hpe.com>
