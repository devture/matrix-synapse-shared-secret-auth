# Version 2

This is a major release, which changes a few things.

It **requires [Synapse v1.46.0+](https://github.com/matrix-org/synapse/releases/tag/v1.46.0)**, which introduced support for password provider modules (Synapse previously had a `password_providers` configuration key for password providers, but switched to its new `module` system). You **need to add this module to the `modules` configuration key in `homeserver.yaml`**.

We now **recommend that you use a custom login type (`com.devture.shared_secret_auth`)** for Synapse's [`POST /_matrix/client/r0/login` API](https://matrix.org/docs/spec/client_server/r0.6.1#post-matrix-client-r0-login), **instead of the `m.login.password` login type used in version 1**. Using a special login type means that regular password requests (which use the `m.login.password` login type) do not go through this module needlessly. By default, we don't enable support for `m.login.password` requests, but we let you turn on backward compatibility with a `m_login_password_support_enabled` setting.

Steps to upgrade:

- ensure you have Synapse v1.46.0+
- install the new module (an updated `shared_secret_authenticator.py` file)
- update your `homeserver.yaml` Synapse configuration to move the module from the `password_providers` configuration key to the new `modules` configuration key. Some configuration keys have also changed. See the [README](./README.md#configuring).
- (optionally) update your other software to newer versions which send `com.devture.shared_secret_auth` login requests, not `m.login.password`. Once everything has been upgraded, you can remove the `m_login_password_support_enabled` backward compatibility configuration option.


# Version 1

Initial release.
