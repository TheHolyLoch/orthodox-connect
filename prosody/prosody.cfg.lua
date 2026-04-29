-- Orthodox Connect - Developed by dgm (dgm@tuta.com)
-- orthodox-connect/prosody/prosody.cfg.lua

local xmpp_domain                = assert(os.getenv('XMPP_DOMAIN'), 'missing XMPP_DOMAIN')
local xmpp_admin_jid             = assert(os.getenv('XMPP_ADMIN_JID'), 'missing XMPP_ADMIN_JID')
local xmpp_muc_domain            = assert(os.getenv('XMPP_MUC_DOMAIN'), 'missing XMPP_MUC_DOMAIN')
local xmpp_provisioning_token_file = assert(os.getenv('XMPP_PROVISIONING_TOKEN_FILE'), 'missing XMPP_PROVISIONING_TOKEN_FILE')
local xmpp_registration_enabled  = os.getenv('XMPP_REGISTRATION_ENABLED') or 'false'

if xmpp_registration_enabled ~= 'false' then
	error('XMPP_REGISTRATION_ENABLED must remain false for the MVP')
end

admins = { xmpp_admin_jid }

daemonize = false
pidfile   = '/var/run/prosody/prosody.pid'

data_path = '/var/lib/prosody'

modules_enabled = {
	'tls';
	'roster';
	'saslauth';
	'disco';
	'carbons';
	'pep';
	'private';
	'blocklist';
	'vcard4';
	'vcard_legacy';
	'version';
	'uptime';
	'time';
	'ping';
	'bosh';
	'websocket';
	'admin_adhoc';
	'orthodox_provisioning';
}

modules_disabled = {
	's2s';
	'register';
}

allow_registration = false

c2s_require_encryption = true
s2s_require_encryption = true
allow_unencrypted_plain_auth = false

authentication = 'internal_hashed'
storage        = 'internal'

c2s_ports = { 5222 }
c2s_interfaces = { "0.0.0.0", "::" }

http_host   = xmpp_domain
http_ports  = { 5280 }
https_ports = { }
http_interfaces = { "0.0.0.0", "::" }

orthodox_provisioning_domain     = xmpp_domain
orthodox_provisioning_muc_domain = xmpp_muc_domain
orthodox_provisioning_token_file = xmpp_provisioning_token_file

log = {
	{ levels = { min = 'info' }, to = 'console' };
}

VirtualHost(xmpp_domain)
	enabled            = true
	allow_registration = false

	ssl = {
		certificate = "/etc/prosody/certs/xmpp.orthodox.zone.crt";
		key = "/etc/prosody/certs/xmpp.orthodox.zone.key";
	}

Component(xmpp_muc_domain, 'muc')
	name                     = 'Orthodox Connect Group Chats'
	restrict_room_creation   = 'admin'
	modules_enabled          = {
		'muc_mam';
	}
	ssl = {
		certificate = "/etc/prosody/certs/rooms.xmpp.orthodox.zone.crt";
		key = "/etc/prosody/certs/rooms.xmpp.orthodox.zone.key";
	}
