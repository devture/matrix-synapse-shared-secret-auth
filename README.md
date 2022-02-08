# Shared Secret Authenticator password provider module for Matrix Synapse

Shared Secret Authenticator is a password provider module that plugs into your [Matrix Synapse](https://github.com/matrix-org/synapse) homeserver.

The goal is to allow an external system to send a specially-crafted login request to Matrix Synapse and be able to obtain login credentials for any user on the homeserver.

This is useful when you want to:

- use a bridge to another chat network which does double-puppeting and may need to impersonate your users from time to time
- manage the state of your Matrix server (and its users) from an external system (your own custom code or via a tool like [matrix-corporal](https://github.com/devture/matrix-corporal))

Example: you want your external system to auto-join a given user (`@user:example.com`) to some room. To do this, you need `@system:example.com` to invite `@user:example.com` to `!room:example.com` and then for the user to accept the invitation.

To do these, your external system needs to be able to log in with both `@system:example.com` and `@user:example.com` and perform actions on their behalf. You can have pre-generated access tokens (or keep a plain-text password) lying around for each user, but that's prone to breakage:

- a pre-generated access token is annoying to create and can get revoked by the user at any time, leaving your external system unable to do anything.

- keeping a plain-text password for all your users is cumbersome and not a good way to do things. Passwords can also get changed by the user at any time, leaving your external system unable to do anything.

This is where the Shared Secret Authenticator module comes to the rescue.


## Installing

If you're using the [matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy) Ansible playbook to install your homeserver and related services, you can also make it install this module too. See the [Setting up the Shared Secret Auth password provider module](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/configuring-playbook-shared-secret-auth.md) documentation.

On [Archlinux](https://www.archlinux.org/), you can install one of these [AUR](https://wiki.archlinux.org/index.php/Arch_User_Repository) packages: [python-matrix-synapse-shared-secret-auth](https://aur.archlinux.org/packages/python-matrix-synapse-shared-secret-auth/) (latest tagged release) or [python-matrix-synapse-shared-secret-auth-git](https://aur.archlinux.org/packages/python-matrix-synapse-shared-secret-auth-git/).

To install and configure this manually, make sure `shared_secret_authenticator.py` is on the Python path, somewhere where the Matrix Synapse server can find it.

The easiest way is `pip install git+https://github.com/devture/matrix-synapse-shared-secret-auth` but you can also manually download `shared_secret_authenticator.py` from this repo to a path like `/usr/local/lib/python3.8/site-packages/shared_secret_authenticator.py`.

Some distribution packages (such as the Debian packages from `matrix.org`) may use an isolated virtual environment, so you will need to install the library there. Any environments should be referenced in your init system - for example, the `matrix.org` Debian package creates a systemd init file at `/lib/systemd/system/matrix-synapse.service` that executes python from `/opt/venvs/matrix-synapse`.

Once installed, you can proceed to [Configuring](#configuring).


### Using with Synapse running in a container

To use it with [Synapse](https://github.com/matrix-org/synapse) running in a container (for example, using the [matrixdotorg/synapse container image](https://hub.docker.com/r/matrixdotorg/synapse)), download the `shared_secret_authenticator.py` script from this repository and mount it into the container at a path like `/usr/local/lib/python3.8/site-packages/shared_secret_authenticator.py`.

If you're using `docker run` (`podman run`, etc.) to start your container, simply add `--mount type=bind,src=/HOST/PATH/TO/shared_secret_authenticator.py,dst=/usr/local/lib/python3.8/site-packages/shared_secret_authenticator.py` (or `-v /HOST/PATH/TO/shared_secret_authenticator.py:/usr/local/lib/python3.8/site-packages/shared_secret_authenticator.py`).

Once installed, you can proceed to [Configuring](#configuring).


### Using with Synapse running under docker-compose

If you're using [docker-compose](https://docs.docker.com/compose/) to start the [Synapse](https://github.com/matrix-org/synapse) container, download the `shared_secret_authenticator.py` script from this repository and mount it into the container using a `volume` definition like this:

```yaml
  matrix:
    image: matrixdotorg/synapse:latest
    volumes:
     - ./shared_secret_authenticator.py:/usr/local/lib/python3.8/site-packages/shared_secret_authenticator.py
     ...
```

Once installed, you can proceed to [Configuring](#configuring).


## Configuring

As the name suggests, you need a "shared secret" (between this Matrix Synapse module and your external system).

You can generate a secure one with a command like this: `pwgen -s 128 1`.

You then need to edit Matrix Synapse's configuration (`homeserver.yaml` file) and enable the module:

```yaml
modules:
    - module: shared_secret_authenticator.SharedSecretAuthProvider
      config:
          shared_secret: "YOUR_SHARED_SECRET_GOES_HERE"
          # By default, only login requests of type `com.devture.shared_secret_auth` are supported.
          # Below, we explicitly enable support for the old `m.login.password` login type,
          # which was used in v1 of matrix-synapse-shared-secret-auth and still widely supported by external software.
          # If you don't need such legacy support, consider setting this to `false` or omitting it entirely.
          m_login_password_support_enabled: true
```

This uses the new **module** API (and `module` configuration key in `homeserver.yaml`), which added support for "password providers" in [Synapse v1.46.0](https://github.com/matrix-org/synapse/releases/tag/v1.46.0) (released on 2021-11-02). If you're running an older version of Synapse or need to use the old `password_providers` API, install an older version of matrix-synapse-sshared-secret-auth (`1.*` or the `v1-stable` branch).

The `m_login_password_support_enabled` configuration key enables support for the [`m.login.password`](https://matrix.org/docs/spec/client_server/r0.6.1#password-based) authentication type (the default that we used in **v1** of matrix-synapse-sshared-secret-auth).
In **v2** we don't

For additional logging information, you might want to edit Matrix Synapse's `.log.config` file as well, adding a new logger:

```
loggers:
    # other stuff here

    shared_secret_authenticator:
        level: INFO
```

You need to restart Matrix Synapse for the module to start working.


## Usage

Once installed and configured, you can obtain an access token for any user on your homeserver.

Example code (in Python):

```python
import json
import hmac
import hashlib
import requests


def obtain_access_token(full_user_id, homeserver_api_url, shared_secret):
    login_api_url = homeserver_api_url + '/_matrix/client/r0/login'

    token = hmac.new(shared_secret.encode('utf-8'), full_user_id.encode('utf-8'), hashlib.sha512).hexdigest()

    payload = {
        'type': 'com.devture.shared_secret_auth',
        'identifier': {
          'type': 'm.id.user',
          'user': full_user_id,
        },
        'token': token,
    }

    # If `m_login_password_support_enabled`, you can use `m.login.password`.
    # The token goes into the `password` field for this login type, not the `token` field.
    #
    # payload = {
    #     'type': 'm.login.password',
    #     'identifier': {
    #       'type': 'm.id.user',
    #       'user': full_user_id,
    #     },
    #     'password': token,
    # }

    response = requests.post(login_api_url, data=json.dumps(payload))

    return response.json()['access_token']


user_id = "@a:example.com"
homeserver_api_url = "https://matrix.example.com"
shared_secret = "SECRET"

access_token = obtain_access_token(user_id, homeserver_api_url, shared_secret)
print(access_token)
```

Once your external system does its work with that accces token, it's best to clean up and revoke it (by hitting the appropriate `/logout` Matrix API routes).


## FAQ

### Can users still log in normally?

Yes.

This doesn't change the way normal log in happens.
Users would normally be authenticated by Matrix Synapse's database and the password stored in there.

This module merely provides an alternate way (a new `com.devture.shared_secret_auth` login type) that a user (or rather, some system on behalf of the user) could use to log in. It's completely separate from the other login flows (like `m.login.password`).

If you've enabled the old `m.login.password` login type via the `m_login_password_support_enabled` configuration setting (defaults to `false`, disabled) then this login type also gets handled. All regular password logins pass through this authentication module, and should they fail to complete, continue on their way to Synapse.


### Can this be used in conjunction with other password providers?

Yes.

Matrix Synapse will go through the list of password provider modules and try each matching one in turn.
It will stop only when it finds a password provider that successfully authenticates the user.

Because this password provider only does things locally and upon a direct "password" hit and other password providers (like the [HTTP JSON REST Authenticator](https://github.com/kamax-io/matrix-synapse-rest-auth)) may perform additional (and slower) tasks, for performance reasons it's better to put this one first in the `modules` list.

If you don't require backward compatibility (`m.login.password` support), we also suggest not enabling support for this login type (set `m_login_password_support_enabled` to `false` or skip this configuration option), which will improve performance.


### This feels like an evil backdoor. Why would you do it?

This is meant to be used by server admins for administrating their server - data that they already host and own.

The easiest (and least intrusive) way to allow for such administration access is through such a special password provider.


## How secure is this?

It uses a shared secret and [HMAC](https://en.wikipedia.org/wiki/HMAC), so it should be secure.

It doesn't use a nonce, so requests are replayable. The same request payload (user id + HMAC "password" combo) will always and forever authenticate you. That said, Matrix's `/login` endpoint suffers from the same deficiency by design (the same user id + password combo) will always and forever authenticate you.

A future iteration of this module may put some timestamp information into the password value and reject requests from the past, thus making this even more secure.

With all that said, to the best of our knowledge, using this module (even as it is now), doesn't introduce any realistic security concern. If you know better, we'd be happy to hear from you.


## Support

Matrix room: [#matrix-synapse-shared-secret-auth:devture.com](https://matrix.to/#/#matrix-synapse-shared-secret-auth:devture.com)

Github issues: [devture/matrix-synapse-shared-secret-auth/issues](https://github.com/devture/matrix-synapse-shared-secret-auth/issues)
