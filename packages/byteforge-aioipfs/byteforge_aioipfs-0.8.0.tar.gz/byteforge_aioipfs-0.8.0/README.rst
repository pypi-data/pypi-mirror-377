=======
aioipfs
=======

:info: Asynchronous IPFS_ client library

**aioipfs** is a python3 library providing an asynchronous API for IPFS_.
Supported python versions: *3.6*, *3.7*, *3.8*, *3.9*, *3.10*, *3.11*, *3.12*.

This library supports the
`RPC API specifications <https://docs.ipfs.tech/reference/kubo/rpc>`_
for kubo_ version *0.28.0*. Unit tests are run against
most major go-ipfs releases and all kubo_
releases, see the *CI* section below.

See the documentation `here <https://aioipfs.readthedocs.io/en/latest>`_.

.. image:: https://gitlab.com/cipres/aioipfs/badges/master/coverage.svg

Installation
============

.. code-block:: shell

    pip install aioipfs

To install the requirements for `bohort <https://aioipfs.readthedocs.io/en/latest/bohort.html>`_, a REPL tool for making RPC calls on kubo nodes:

.. code-block:: shell

    pip install 'aioipfs[bohort]'

Support for CAR (Content-Addressable Archives) decoding (with the
`ipfs-car-decoder package <https://github.com/kralverde/py-ipfs-car-decoder/>`_)
can be enabled with the *car* extra:

.. code-block:: shell

    pip install 'aioipfs[car]'

By default the *json* module from the standard Python library is used
to decode JSON messages, but orjson_ will be used if it is installed:

.. code-block:: shell

    pip install 'aioipfs[orjson]'

Usage
=====

Client instantiation
--------------------

The recommended way to specify the kubo node's RPC API address is
to pass a multiaddr_.

.. code-block:: python

    client = aioipfs.AsyncIPFS(maddr='/ip4/127.0.0.1/tcp/5001')

    client = aioipfs.AsyncIPFS(maddr='/dns4/localhost/tcp/5001')

You can also pass a *multiaddr.Multiaddr* instance.

.. code-block:: python

    from multiaddr import Multiaddr

    client = aioipfs.AsyncIPFS(maddr=Multiaddr('/ip4/127.0.0.1/tcp/5001'))

Otherwise just pass *host* and *port* separately:

.. code-block:: python

    client = aioipfs.AsyncIPFS(host='localhost', port=5001)

    client = aioipfs.AsyncIPFS(host='::1', port=5201)

If the kubo server requires authentication, you can pass the RPC authentication
credentials via the constructor's *auth* keyword argument:

.. code-block:: python

    client = aioipfs.AsyncIPFS(auth=aioipfs.BasicAuth('john', 'password123'))

    client = aioipfs.AsyncIPFS(auth=aioipfs.BearerAuth('my-secret-token'))

Get an IPFS resource
--------------------

.. code-block:: python

    import sys
    import asyncio

    import aioipfs

    async def get(cid: str):
        client = aioipfs.AsyncIPFS()

        await client.get(cid, dstdir='.')
        await client.close()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get(sys.argv[1]))

Add some files
--------------

This example will import all files and directories specified on the command
line. Note that the **add** API function is an asynchronous generator and
therefore should be used with the *async for* syntax.

.. code-block:: python

    import sys
    import asyncio

    import aioipfs

    async def add_files(files: list):
        client = aioipfs.AsyncIPFS()

        async for added_file in client.add(*files, recursive=True):
            print('Imported file {0}, CID: {1}'.format(
                added_file['Name'], added_file['Hash']))

        await client.close()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(add_files(sys.argv[1:]))

You can also use the async list generator syntax:

.. code-block:: python

    cids = [entry['Hash'] async for entry in client.add(dir_path)]

Pubsub service
--------------

.. code-block:: python

    async def pubsub_serve(topic: str):
        async with aioipfs.AsyncIPFS() as cli:
            async for message in cli.pubsub.sub(topic):
                print('Received message from', message['from'])

                await cli.pubsub.pub(topic, message['data'])


Dialing a P2P service
---------------------

.. code-block:: python

    async with aioipfs.AsyncIPFS() as client:
        async with client.p2p.dial_service(peer_id, '/x/echo') as dial:
            print(f'Dial host: {dial.maddr_host}, port: {dial.maddr_port}')

            # Connect to the service now
            ....

CI
==

The Gitlab CI workflow runs unit tests against the following
go-ipfs/kubo releases (`go here <https://gitlab.com/cipres/aioipfs/-/jobs>`_
for the CI jobs overview).

- go-ipfs >=0.11.0,<=0.13.0
- kubo >=0.14.0,<=0.28.0

.. image:: https://github.com/pinnaculum/aioipfs/workflows/aioipfs-build/badge.svg
    :target: https://github.com/pinnaculum/aioipfs/actions

.. image:: https://gitlab.com/cipres/aioipfs/badges/master/pipeline.svg
    :target: https://gitlab.com/cipres/aioipfs/-/jobs

Features
========

Async file writing on get operations
------------------------------------

The **aiofiles** library is used to asynchronously write data retrieved from
the IPFS daemon when using the */api/v0/get* API call, to avoid blocking the
event loop. TAR extraction is done in asyncio's threadpool.

Requirements
============

- Python >= 3.6, <= 3.12
- aiohttp_
- aiofiles_
- py-multibase_
- yarl_

.. _aiohttp: https://pypi.python.org/pypi/aiohttp
.. _aiofiles: https://pypi.python.org/pypi/aiofiles
.. _multiaddr: https://multiformats.io/multiaddr/
.. _py-multibase: https://pypi.python.org/pypi/py-multibase
.. _yarl: https://pypi.python.org/pypi/yarl
.. _IPFS: https://ipfs.io
.. _kubo: https://github.com/ipfs/kubo
.. _orjson: https://github.com/ijl/orjson

License
=======

**aioipfs** is offered under the GNU Lesser GPL3 (LGPL3) license.
